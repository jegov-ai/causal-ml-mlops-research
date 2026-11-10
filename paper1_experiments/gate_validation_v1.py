"""Untouched-seed evaluation of a frozen gate modification; see protocol."""
import argparse,csv,hashlib,importlib.util,io,itertools,json,platform,subprocess,time,zipfile
from datetime import datetime,timezone
from pathlib import Path
import numpy as np
import pandas as pd
import sklearn

ROOT=Path(__file__).resolve().parent
PROTOCOL=ROOT/'GATE_VALIDATION_PROTOCOL_v1.md'

def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def scan_seeds(project,requested):
    checked=0
    def check(handle,label):
        nonlocal checked
        reader=csv.DictReader(handle)
        columns=[c for c in (reader.fieldnames or []) if c in ('seed','stream_seed')]
        if not columns:return
        checked+=1
        for row in reader:
            for c in columns:
                value=row[c]
                if value is None or not value.strip():raise RuntimeError('Missing seed: '+label)
                number=float(value)
                if not np.isfinite(number) or number!=int(number):raise RuntimeError('Malformed seed: '+label)
                if int(number) in requested:raise RuntimeError('Previously recorded evaluation seed: '+label)
    for path in project.rglob('*.csv'):
        if '.venv' in path.parts or '.git' in path.parts:continue
        with path.open(encoding='utf-8-sig',newline='') as f:check(f,str(path))
    for path in (project/'reproducibility/archives').glob('*.zip'):
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if name.lower().endswith('.csv'):
                    with z.open(name) as raw:
                        with io.TextIOWrapper(raw,encoding='utf-8-sig',newline='') as f:check(f,str(path)+'::'+name)
    return checked

def paired_analysis(periods,benchmarks,output,mode):
    keys=['initial_seed','scenario','onset','seed','method','review_budget']
    post=periods[periods.period>=periods.onset]
    totals=post.groupby(keys+['gate_variant']).agg(mean_window_loss=('regret','mean'),cumulative_loss=('regret','sum'),harmful_treatment_rate=('harmful_treatment_rate','mean')).reset_index()
    totals.to_csv(output/'run_outcomes.csv',index=False)
    benchkeys=['initial_seed','scenario','onset','seed']
    bp=benchmarks[benchmarks.period>=benchmarks.onset]
    bt=bp.groupby(benchkeys+['benchmark']).regret.mean().rename('benchmark_mean_window_loss').reset_index()
    comparisons=totals.merge(bt,on=benchkeys,validate='many_to_many')
    comparisons['policy_minus_benchmark']=comparisons.mean_window_loss-comparisons.benchmark_mean_window_loss
    comparisons.to_csv(output/'fixed_policy_comparisons.csv',index=False)
    f=totals[totals.gate_variant=='frozen'].drop(columns='gate_variant')
    u=totals[totals.gate_variant=='refreshed'].drop(columns='gate_variant')
    pairs=u.merge(f,on=keys,suffixes=('_refreshed','_frozen'),validate='one_to_one')
    pairs['loss_difference']=pairs.mean_window_loss_refreshed-pairs.mean_window_loss_frozen
    pairs.to_csv(output/'paired_differences.csv',index=False)
    # One value per independent stream seed; repeated factors remain inside seed blocks.
    primary=pairs[(pairs.method=='M1')&(pairs.scenario!='stable')].groupby('seed').loss_difference.mean()
    primary.rename('equal_grid_mean_difference').to_csv(output/'primary_seed_differences.csv')
    result=dict(scope='Pilot engineering only' if mode=='pilot' else 'Prespecified independent-seed synthetic validation conditional on three fixed initial models and reused calibration',independent_seeds=len(primary),primary_mean_difference=float(primary.mean()),negative_favors='refreshed',claim='No unconditional superiority or deployment-safety claim')
    if mode=='validation':
        rng=np.random.default_rng(20261108)
        samples=rng.choice(primary.to_numpy(),size=(5000,len(primary)),replace=True).mean(axis=1)
        result.update(descriptive_paired_seed_bootstrap_95=np.quantile(samples,[.025,.975]).tolist(),monte_carlo_standard_error=float(primary.std(ddof=1)/np.sqrt(len(primary))))
    (output/'analysis.json').write_text(json.dumps(result,indent=2))

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--reference',required=True,type=Path)
    ap.add_argument('--mode',choices=['pilot','validation'],default='pilot');ap.add_argument('--preflight-only',action='store_true');args=ap.parse_args()
    project=ROOT.parent;ref=args.reference.resolve();manifest=json.loads((ref/'manifest.json').read_text())
    current=dict(numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__)
    if current!=manifest['versions'] or platform.python_version()!=manifest['python'].split()[0]:raise RuntimeError('Reference software environment differs')
    paths=[Path(__file__).resolve(),PROTOCOL,ROOT/'refreshed_gate_development_v1.py',ROOT/'model_onset_sensitivity_v1.py',ROOT/'monitoring_signal_ablation_v1.py',ROOT/'integrated_causal_monitoring_v2_xai.py',ROOT/'monitoring_schedule_comparison_v1.py']
    for path in paths:
        subprocess.run(['git','ls-files','--error-unmatch',str(path.relative_to(project))],cwd=project,check=True,stdout=subprocess.DEVNULL)
    subprocess.run(['git','diff','--exit-code','HEAD','--'],cwd=project,check=True,stdout=subprocess.DEVNULL)
    for name in ['model_onset_sensitivity_v1.py','monitoring_signal_ablation_v1.py','integrated_causal_monitoring_v2_xai.py','monitoring_schedule_comparison_v1.py']:
        snapshot=ref/('script_snapshot.py' if name=='model_onset_sensitivity_v1.py' else name+'.snapshot')
        if digest(ROOT/name)!=digest(snapshot):raise RuntimeError('Source mismatch: '+name)
    # This known comparison implementation is frozen at its already-executed bytes.
    if digest(ROOT/'refreshed_gate_development_v1.py')!='5857c54456aa1217881dc3dc5a7f0f7b791841b991ab71f6dfda319f389af000':raise RuntimeError('Gate comparison source changed')
    seeds=[490000] if args.mode=='pilot' else list(range(500000,500100))
    checked=scan_seeds(project,set(seeds));commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=project,text=True).strip()
    print('PREFLIGHT PASSED:',dict(mode=args.mode,seeds=[seeds[0],seeds[-1]],csvs_checked=checked,commit=commit),flush=True)
    if args.preflight_only:return
    m=load('validation_frozen_sensitivity',ROOT/'model_onset_sensitivity_v1.py');helper=load('validation_gate_helper',ROOT/'refreshed_gate_development_v1.py')
    out=ROOT/('gate_validation_v1_'+args.mode)/('run_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'));out.mkdir(parents=True,exist_ok=False)
    status=dict(status='running',mode=args.mode,git_commit=commit,versions=current,python=platform.python_version(),seed_csv_files_checked=checked,seeds=seeds,reference=str(ref),reference_manifest_sha256=digest(ref/'manifest.json'),source_hashes={p.name:digest(p) for p in paths},configuration_count=39*len(seeds),completed_configurations=0,started_utc=datetime.now(timezone.utc).isoformat())
    for path in paths:(out/(path.name+'.snapshot')).write_bytes(path.read_bytes())
    def checkpoint():(out/'checkpoint.json').write_text(json.dumps(status,indent=2))
    checkpoint();print('OUTPUT:',out,flush=True);started=time.perf_counter();allrows=[];allbench=[];diagnostics=[]
    try:
        for fit in (42,1042,2042):
            train,_=m.train_test_split(m.initial_data(fit),test_size=.2,random_state=42);baseline=m.fit_models(train,fit)
            bg=pd.read_csv(ref/f'background_{fit}.csv');ex=m.base.TwoFeatureShapley(baseline,bg)
            cal=pd.read_csv(ref/f'calibration_{fit}.csv');thresholds=json.loads((ref/f'thresholds_{fit}.json').read_text())
            for scenario in m.SCENARIOS:
                for onset in ((7,) if scenario=='stable' else (4,7,10)):
                    for seed in seeds:
                        frozen=None
                        for variant in ('frozen','refreshed'):
                            cache={}
                            def callback(row,candidate,incumbent,gate,stream,scen,period,n,onset_value):
                                key=(period,id(candidate),id(incumbent))
                                if key not in cache:
                                    benefit=None
                                    if period<12:
                                        future=m.make_window(stream,period+1,scen,n,onset=onset_value)
                                        benefit=helper.loss_difference(future.true_effect,m.policy(candidate,future),m.policy(incumbent,future),m.COST)
                                    cache[key]=benefit
                                diagnostics.append(dict(initial_seed=fit,scenario=scenario,onset=onset,seed=seed,period=period,method=row['method'],review_budget=row['review_budget'],gate_variant=variant,accepted=bool(row['gate_lower']>0),next_window_benefit=cache[key]))
                            rows,_,bench=helper.instrument(m,callback,variant)(seed,scenario,1000,baseline,cal.center.to_numpy(),cal.scale.to_numpy(),thresholds,ex,None,None,None,onset=onset)
                            frame=pd.DataFrame(rows).assign(initial_seed=fit,onset=onset)
                            if not (frame.retrain_accepted==(frame.gate_lower>0)).all():raise RuntimeError('Gate rule mismatch')
                            if frozen is None:frozen=frame
                            else:
                                cols=['seed','scenario','period','method','review_budget','score','threshold','alert_issued','review_performed']
                                pd.testing.assert_frame_equal(frame[cols],frozen[cols])
                            allrows.append(frame.assign(gate_variant=variant))
                            if variant=='frozen':allbench.extend(dict(r,initial_seed=fit,onset=onset) for r in bench)
                        status['completed_configurations']+=1
                        if status['completed_configurations']%10==0 or args.mode=='pilot':
                            pd.concat(allrows,ignore_index=True).to_csv(out/'period_log.csv',index=False)
                            pd.DataFrame(diagnostics).to_csv(out/'review_diagnostics.csv',index=False);checkpoint()
                        print('COMPLETED',status['completed_configurations'],'/',status['configuration_count'],fit,scenario,onset,seed,flush=True)
        periods=pd.concat(allrows,ignore_index=True);benchmarks=pd.DataFrame(allbench)
        periods.to_csv(out/'period_log.csv',index=False);benchmarks.to_csv(out/'benchmarks.csv',index=False);pd.DataFrame(diagnostics).to_csv(out/'review_diagnostics.csv',index=False)
        paired_analysis(periods,benchmarks,out,args.mode)
        status.update(status='complete',elapsed_seconds=time.perf_counter()-started,monitoring_and_reviews_matched=True);checkpoint();print('COMPLETE:',out,flush=True)
    except Exception as e:
        status.update(status='failed',error=str(e));checkpoint();raise

if __name__=='__main__':main()
