"""Run the committed KuaiRand 14-date protocol; --self-test uses artificial data.

Commit this runner before --preflight or --run. Repeats require explicit
--run --reproduce, identical source and versions, and a new output directory.
Uses unchanged pilot model/score helpers; never trains on a gate/evaluation
window before its timestamp. Saved integer timestamps explicitly use ms.
"""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tarfile
import time
import traceback
import uuid

import numpy as np
import pandas as pd
import sklearn
import run_kuairand_pilot as pilot

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PROTOCOL='fourteen_day_protocol_v1.json'
PROTOCOL_HASH='c277dde946e43957f2c8533a86019d8343459c7e33a802e6a5870d3562d657c3'
LOCAL=timezone(timedelta(hours=8))
POLICIES=['frozen_gate_path','refreshed_gate_path','initial_no_update',
          'always_update_current_candidate','uniform_catalogue','always_short','always_long','always_unknown']
PAIRS=[(POLICIES[1],POLICIES[0])]+[(g,b) for g in POLICIES[:2] for b in POLICIES[2:]]
LABELS=[a+'_minus_'+b+'__'+e for a,b in PAIRS for e in ['dr','ips']]


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()


def lf_hash(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()


def save(path,value):
    path=Path(path);temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2,allow_nan=False),encoding='utf-8')
    temp.replace(path)


def plan_and_sources(require_commit=True):
    plan=json.loads((HERE/PROTOCOL).read_text(encoding='utf-8'))
    if canonical_hash(plan)!=PROTOCOL_HASH:
        raise ValueError('Protocol differs from fixed v1; do not silently revise an exposed study')
    for key,value in pilot.SETTINGS['model'].items():
        if plan['model'][key]!=value:
            raise ValueError('Pilot/protocol model mismatch: '+key)
    files=[PROTOCOL,Path(__file__).name,'run_kuairand_pilot.py','pilot_settings.json',
           'feasibility_checkpoint.json','development_outcomes.csv']
    provenance=dict(source_sha256_LF_normalized={n:lf_hash(HERE/n) for n in files},
                    protocol_canonical_sha256=PROTOCOL_HASH,
                    versions=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__))
    if require_commit:
        git=shutil.which('git')
        if not git:
            raise RuntimeError('Git unavailable')
        def call(*args):
            return subprocess.check_output([git,'-C',str(ROOT),*args])
        paths=[(HERE/n).relative_to(ROOT).as_posix() for n in files]
        call('ls-files','--error-unmatch','--',*paths)
        if call('diff','HEAD','--',*paths).strip():
            raise ValueError('Commit the runner and study files before execution')
        expected=call('show',plan['execution']['required_pilot_source_reference']).replace(b'\r\n',b'\n')
        actual=(HERE/'run_kuairand_pilot.py').read_bytes().replace(b'\r\n',b'\n')
        if expected!=actual:
            raise ValueError('Pilot source differs from locked b213e6c implementation')
        provenance['git_commit']=call('rev-parse','HEAD').decode().strip()
        provenance['pilot_source_commit']=call('rev-parse','b213e6c').decode().strip()
    return plan,provenance


def verify_archive(plan):
    archive=ROOT/plan['dataset']['archive']
    if archive.stat().st_size!=plan['dataset']['bytes']:
        raise ValueError('Archive byte count mismatch')
    print('Verifying KuaiRand archive...',flush=True)
    if pilot.digest(archive,'md5')!=plan['dataset']['md5']:
        raise ValueError('Archive MD5 mismatch')
    sha=pilot.digest(archive)
    expected=json.loads((HERE/'feasibility_checkpoint.json').read_text())['archive_sha256']
    if sha!=expected:
        raise ValueError('Archive SHA-256 mismatch')
    return archive,sha


def catalogue(archive):
    with tarfile.open(archive,'r:gz') as tar,tar.extractfile(pilot.ITEMS) as stream:
        v=pd.read_csv(stream,usecols=['video_id','video_duration'],dtype=str)
    if v.video_id.isna().any() or v.video_id.duplicated().any():
        raise ValueError('Invalid catalogue IDs')
    groups=pilot.classify(v.video_duration)
    if len(v)!=7583 or not np.array_equal(np.bincount(groups,minlength=3),pilot.POOL):
        raise ValueError('Catalogue/group counts changed')
    return dict(zip(v.video_id,groups))


def window(archive,mapping,start,end):
    """Convert feedback ONLY AFTER the explicit timestamp/position selection."""
    start,end=pd.Timestamp(start),pd.Timestamp(end)
    pieces=[]
    with tarfile.open(archive,'r:gz') as tar,tar.extractfile(pilot.LOG) as stream:
        for chunk in pd.read_csv(stream,usecols=['time_ms','date','tab','video_id','user_id','is_rand','long_view'],dtype=str,chunksize=50000):
            ms=pd.to_numeric(chunk.time_ms,errors='raise')
            times=pd.to_datetime(ms,unit='ms',utc=True,errors='raise')
            keep=chunk.tab.eq('1') & times.ge(start) & times.lt(end)
            d=chunk.loc[keep].copy()
            if d.empty:
                continue
            if d.isna().any().any() or not d.is_rand.eq('1').all():
                raise ValueError('Invalid selected fields or random flag')
            d['timestamp']=times.loc[keep].dt.tz_convert(LOCAL)
            d['time_ms']=ms.loc[keep].to_numpy(dtype=np.int64)
            d['csv_row_index']=d.index.to_numpy()
            d['group']=d.video_id.map(mapping)
            if d.group.isna().any():
                raise ValueError('Logged video absent from fixed catalogue')
            d['group']=d.group.astype(int)
            d['long_view']=pd.to_numeric(d.long_view,errors='raise')
            if not d.long_view.isin([0,1]).all():
                raise ValueError('Invalid selected outcome')
            d['date_mismatch']=d.timestamp.dt.strftime('%Y%m%d').ne(d.date)
            pieces.append(d)
    if not pieces:
        raise ValueError('Empty required window: '+str(start))
    d=pd.concat(pieces,ignore_index=True).sort_values(['time_ms','csv_row_index'],kind='stable').reset_index(drop=True)
    if len(d)<2 or not d.timestamp.ge(start).all() or not d.timestamp.lt(end).all():
        raise ValueError('Required window validation failed')
    if d.csv_row_index.duplicated().any():
        raise ValueError('Duplicated source-row identity')
    return d


def saved_context(frame):
    return dict(timestamp_ms=frame.time_ms.to_numpy(dtype=np.int64),
                csv_row_index=frame.csv_row_index.to_numpy(dtype=np.int64),
                user_id=frame.user_id.to_numpy(dtype=str),group=frame.group.to_numpy(int),
                long_view=frame.long_view.to_numpy(int),date_mismatch=frame.date_mismatch.to_numpy(bool))


def describe(frame,date,part):
    return dict(date=date,part=part,records=len(frame),long_views=int(frame.long_view.sum()),
                users=int(frame.user_id.nunique()),date_mismatches=int(frame.date_mismatch.sum()),
                first_timestamp=str(frame.timestamp.iloc[0]),last_timestamp=str(frame.timestamp.iloc[-1]))


def aggregates(frame,values):
    codes,users=pd.factorize(frame.user_id.astype(str),sort=True)
    user_counts=np.bincount(codes)
    user_sums=np.column_stack([np.bincount(codes,weights=values[:,j]) for j in range(values.shape[1])])
    block_codes,blocks=pd.factorize(frame.timestamp.dt.floor('30min'),sort=True)
    block_counts=np.bincount(block_codes)
    block_sums=np.column_stack([np.bincount(block_codes,weights=values[:,j]) for j in range(values.shape[1])])
    return dict(users=np.asarray(users,dtype=str),counts=user_counts,sums=user_sums),dict(
        blocks=[str(b) for b in blocks],counts=block_counts.tolist(),sums=block_sums.T.tolist())


def user_bootstrap(days):
    if len(days)!=14:
        raise ValueError('Require all 14 dates')
    users=np.unique(np.concatenate([d['users'] for d in days]));u=len(users)
    k=days[0]['sums'].shape[1]
    counts=np.zeros((u,14));sums=np.zeros((u,14,k))
    means=[]
    for date,day in enumerate(days):
        if np.any(day['counts']<=0) or not np.isfinite(day['sums']).all():
            raise ValueError('Invalid user aggregates')
        index=np.searchsorted(users,day['users'])
        if len(np.unique(index))!=len(index):
            raise ValueError('Duplicate user cluster within date')
        counts[index,date]=day['counts'];sums[index,date,:]=day['sums']
        means.append(day['sums'].sum(axis=0)/day['counts'].sum())
    draws=np.empty((1000,k));rng=np.random.default_rng(42)
    probabilities=np.full(u,1./u)
    flat=sums.reshape(u,-1)
    # Bounded batch size avoids a 1000-by-all-users count allocation.
    for start in range(0,1000,16):
        stop=min(start+16,1000)
        multiplicity=rng.multinomial(u,probabilities,size=stop-start).astype(float)
        denominator=multiplicity@counts
        if np.any(denominator<=0):
            raise ValueError('Bootstrap replicate has an empty date; stopping as specified')
        numerator=(multiplicity@flat).reshape(stop-start,14,k)
        draws[start:stop]=(numerator/denominator[:,:,None]).mean(axis=1)
    return np.mean(means,axis=0),np.quantile(draws,[.025,.975],axis=0).T,u


def temporal_bootstrap(days):
    if len(days)!=14:
        raise ValueError('Require all 14 dates')
    rng=np.random.default_rng(42);draws=None;means=[]
    for day in days:
        sizes=np.asarray(day['counts'],float);totals=np.asarray(day['sums'],float)
        n=len(sizes)
        if n<2 or np.any(sizes<=0) or not np.isfinite(totals).all():
            raise ValueError('Insufficient or invalid time blocks')
        means.append(totals.sum(axis=1)/sizes.sum())
        picked=rng.integers(0,n,size=(1000,n))
        daily=totals[:,picked].sum(axis=2)/sizes[picked].sum(axis=1)[None,:]
        draws=daily/14 if draws is None else draws+daily/14
    return np.mean(means,axis=0),np.quantile(draws,[.025,.975],axis=1).T


def evaluate(frame,q,actions,date,out):
    results={};rows=[];arrays=saved_context(frame);arrays['common_q']=q
    for name in POLICIES:
        dr,ips,w=pilot.scores(frame,q,actions[name]);results[name]=(dr,ips)
        row=dict(date=date,policy=name,records=len(frame),users=int(frame.user_id.nunique()),
                 logged_long_views=int(frame.long_view.sum()),
                 **pilot.support(w,frame.long_view.to_numpy(),frame.user_id.to_numpy()))
        for estimator,values in [('dr',dr),('ips',ips)]:
            row.update({estimator+'_'+key:value for key,value in pilot.summary(values).items()})
            arrays[name+'_'+estimator]=values
        arrays[name+'_weights']=w
        if actions[name] is not None:
            arrays[name+'_actions']=actions[name]
        rows.append(row)
    paired=[];vectors=[]
    for left,right in PAIRS:
        for index,estimator in enumerate(['dr','ips']):
            values=results[left][index]-results[right][index]
            paired.append(dict(date=date,contrast=left+'_minus_'+right+'__'+estimator,**pilot.summary(values)))
            vectors.append(values)
    users,blocks=aggregates(frame,np.column_stack(vectors))
    np.savez_compressed(out/(date+'_evaluation_scores.npz'),**arrays)
    np.savez_compressed(out/(date+'_user_aggregates.npz'),user_id=users['users'],counts=users['counts'],contrast_sums=users['sums'])
    return rows,paired,users,blocks


def run(reproduce=False):
    plan,provenance=plan_and_sources()
    archive,sha=verify_archive(plan)
    base=ROOT/'data/kuairand/fourteen_day_runs';base.mkdir(parents=True,exist_ok=True)
    marker=base/'first_execution.json'
    if marker.exists():
        first=json.loads(marker.read_text())
        if not reproduce:
            raise RuntimeError('First execution exists. Inspect it; repeats require explicit --reproduce.')
        for field in ['source_sha256_LF_normalized','versions']:
            if first[field]!=provenance[field]:
                raise ValueError('Changed '+field+' needs a disclosed deviation, not an automatic retry')
    elif reproduce:
        raise ValueError('No first execution to reproduce')
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8]
    out=base/run_id;out.mkdir(exist_ok=False)
    if not marker.exists():
        with marker.open('x',encoding='utf-8') as handle:
            json.dump(dict(run_id=run_id,**provenance),handle,indent=2)
    manifest=dict(status='running',run_id=run_id,reproduction=reproduce,archive_sha256=sha,
                  timestamp_array_field='timestamp_ms',timestamp_array_unit='ms',**provenance,
                  reserved_outcomes_processing_started=False,windows=[],
                  inference_scope=plan['uncertainty']['limitations'])
    started=time.perf_counter()
    def checkpoint(stage):
        manifest['stage']=stage;manifest['elapsed_seconds']=time.perf_counter()-started
        save(out/'manifest.json',manifest)
    try:
        checkpoint('snapshot')
        snapshots=out/'source_snapshot';snapshots.mkdir()
        for name in provenance['source_sha256_LF_normalized']:
            shutil.copy2(HERE/name,snapshots/name)
        print('Output directory:',out,flush=True)
        mapping=catalogue(archive)
        checkpoint('initial_training')
        initial=window(archive,mapping,*plan['time']['initial_training'])
        if len(initial)!=120645 or int(initial.long_view.sum())!=10128:
            raise ValueError('Initial development counts changed')
        manifest['windows'].append(describe(initial,'development','initial_training'))
        print('Training initial model on all three development dates...',flush=True)
        models={'initial':pilot.fit(initial)};del initial
        paths=dict(frozen='initial',refreshed='initial')
        gates=[];evaluations=[];paired=[];user_days=[];block_days=[]
        manifest['reserved_outcomes_processing_started']=True
        for date in plan['time']['evaluation_dates_local']:
            day=pd.Timestamp(date,tz=LOCAL)
            checkpoint(date+': candidate_training')
            training=window(archive,mapping,day-pd.Timedelta(hours=12),day+pd.Timedelta(hours=12))
            manifest['windows'].append(describe(training,date,'candidate_training'))
            candidate=date+'_candidate'
            print(date+': training rolling-24h candidate...',flush=True)
            models[candidate]=pilot.fit(training);del training
            checkpoint(date+': gate_check')
            frame=window(archive,mapping,day+pd.Timedelta(hours=12),day+pd.Timedelta(hours=18))
            manifest['windows'].append(describe(frame,date,'gate_check'))
            predictions={key:pilot.predict(models[key],frame) for key in sorted({'initial',candidate,*paths.values()})}
            ca=predictions[candidate].argmax(1)
            arrays=saved_context(frame)
            arrays.update(frozen_q=predictions['initial'],refreshed_q=predictions[candidate],candidate_actions=ca)
            for name in ['frozen','refreshed']:
                before=paths[name];ia=predictions[before].argmax(1)
                q=predictions['initial' if name=='frozen' else candidate]
                stats,cs,ins=pilot.decision(frame,q,ca,ia)
                reason='zero_matching_rows' if stats['zero_match_rejection'] else 'positive_lower_bound' if stats['candidate_accepted'] else 'lower_bound_not_positive'
                if stats['candidate_accepted']:
                    paths[name]=candidate
                row=dict(date=date,gate=name,candidate_model=candidate,incumbent_before=before,
                         selected_model=paths[name],reason=reason,**stats)
                for label,result in [('candidate',cs),('incumbent',ins)]:
                    row.update({label+'_'+key:value for key,value in pilot.support(result[2],frame.long_view.to_numpy(),frame.user_id.to_numpy()).items()})
                gates.append(row)
                arrays.update({name+'_incumbent_actions':ia,name+'_candidate_dr':cs[0],name+'_incumbent_dr':ins[0],name+'_candidate_weights':cs[2],name+'_incumbent_weights':ins[2]})
                print(f"  {name}: gain={stats['mean']:.6f}; accepted={stats['candidate_accepted']}",flush=True)
            np.savez_compressed(out/(date+'_gate_scores.npz'),**arrays)
            pd.DataFrame(gates).to_csv(out/'gate_comparison.csv',index=False)
            del frame,predictions,arrays
            checkpoint(date+': subsequent_evaluation')
            frame=window(archive,mapping,day+pd.Timedelta(hours=18),day+pd.Timedelta(days=1))
            manifest['windows'].append(describe(frame,date,'subsequent_evaluation'))
            print(date+': evaluating eight policies...',flush=True)
            predictions={key:pilot.predict(models[key],frame) for key in sorted({'initial',candidate,*paths.values()})}
            actions=dict(frozen_gate_path=predictions[paths['frozen']].argmax(1),
                         refreshed_gate_path=predictions[paths['refreshed']].argmax(1),
                         initial_no_update=predictions['initial'].argmax(1),
                         always_update_current_candidate=predictions[candidate].argmax(1),uniform_catalogue=None,
                         always_short=np.zeros(len(frame),int),always_long=np.ones(len(frame),int),always_unknown=np.full(len(frame),2,int))
            rows,contrasts,users,blocks=evaluate(frame,predictions[candidate],actions,date,out)
            evaluations.extend(rows);paired.extend(contrasts);user_days.append(users);block_days.append(blocks)
            pd.DataFrame(evaluations).to_csv(out/'evaluation.csv',index=False)
            pd.DataFrame(paired).to_csv(out/'daily_paired_contrasts.csv',index=False)
            save(out/'bootstrap_blocks.json',dict(labels=LABELS,dates=plan['time']['evaluation_dates_local'][:len(block_days)],days=block_days))
            models={key:model for key,model in models.items() if key in {'initial',*paths.values()}}
            del frame,predictions,actions
            checkpoint(date+': complete')
        checkpoint('user_cluster_bootstrap')
        print('Computing 1,000 paired user-cluster bootstrap replicates...',flush=True)
        means,user_interval,user_count=user_bootstrap(user_days)
        checkpoint('time_block_bootstrap')
        time_means,time_interval=temporal_bootstrap(block_days)
        np.testing.assert_allclose(means,time_means,atol=1e-12,rtol=1e-10)
        result=dict(date_weighting='equal across all 14 dates',dates=plan['time']['evaluation_dates_local'],
                    bootstrap_resamples=1000,seed=42,user_clusters=user_count,
                    user_interval_label='Exploratory user-cluster percentile interval conditional on selected paths',
                    time_interval_label='Separate exploratory within-date 30-minute block sensitivity interval',
                    limitations=plan['uncertainty']['limitations'],contrasts={})
        for j,label in enumerate(LABELS):
            result['contrasts'][label]=dict(mean=float(means[j]),user_cluster_interval=user_interval[j].tolist(),
                                           time_block_sensitivity_interval=time_interval[j].tolist(),primary=j==0)
        save(out/'aggregate_contrasts.json',result)
        manifest.update(status='complete',final_selected_models=paths,evaluation_user_clusters=user_count)
        checkpoint('complete')
        primary=result['contrasts'][LABELS[0]]
        print('Primary refreshed-minus-frozen DR difference:',primary['mean'],flush=True)
        print('Exploratory user-cluster interval:',primary['user_cluster_interval'],flush=True)
        print('COMPLETE:',out,flush=True)
        print('Exploratory group-policy gate study; no oracle truth, general monitoring superiority or sequential safety established.')
    except BaseException as exc:
        manifest.update(status='failed',error=repr(exc),traceback=traceback.format_exc())
        checkpoint(manifest.get('stage','failed'))
        print('STOPPED. Partial output preserved:',out,flush=True)
        raise


def self_test():
    # No plan, real archive, research outcomes or execution marker is opened.
    q=np.tile([.1,.2,.3],(4,1))
    f=pd.DataFrame(dict(group=[0,1,2,0],long_view=[1,0,1,0],user_id=['a','b','a','b']))
    a=np.zeros(4,int)
    assert not pilot.decision(f,q,a,a)[0]['candidate_accepted']
    days=[dict(users=np.array(['a','b']),counts=np.array([1,9]),sums=np.array([[0.,0.],[18.,0.]])) for _ in range(14)]
    mean,interval,n=user_bootstrap(days)
    np.testing.assert_allclose(mean,[1.8,0]);np.testing.assert_allclose(interval,[[0,2],[0,0]])
    assert n==2 # Same users resampled together across dates, not independently per date.
    days[0]=dict(users=np.array(['a','b']),counts=np.array([100,900]),sums=np.array([[0.,0.],[1800.,0.]]))
    np.testing.assert_allclose(user_bootstrap(days)[0],[1.8,0])
    blocks=[dict(counts=[1,9],sums=[[0.,18.],[0.,0.]]) for _ in range(14)]
    np.testing.assert_allclose(temporal_bootstrap(blocks)[0],[1.8,0])
    try:
        user_bootstrap(days[:13])
    except ValueError:
        pass
    else:
        raise AssertionError('Missing date accepted')
    import tempfile,io
    with tempfile.TemporaryDirectory() as directory:
        archive=Path(directory)/'toy.tar.gz'
        dates=['2022-04-25T11:59:59+08:00','2022-04-25T12:00:00+08:00','2022-04-25T17:59:59+08:00','2022-04-25T18:00:00+08:00','2022-04-26T12:00:00+08:00']
        frame=pd.DataFrame(dict(time_ms=[pd.Timestamp(t).value//1000000 for t in dates],date=['20220425']*5,
                                tab=['1']*5,video_id=['0']*5,user_id=['u']*5,is_rand=['1']*5,
                                long_view=['UNREADABLE','1','0','UNREADABLE','UNREADABLE']))
        body=frame.to_csv(index=False).encode()
        with tarfile.open(archive,'w:gz') as tar:
            info=tarfile.TarInfo(pilot.LOG);info.size=len(body);tar.addfile(info,io.BytesIO(body))
        selected=window(archive,{'0':0},'2022-04-25T12:00:00+08:00','2022-04-25T18:00:00+08:00')
        assert len(selected)==2 and selected.long_view.sum()==1
        np.testing.assert_array_equal(pd.to_datetime(saved_context(selected)['timestamp_ms'],unit='ms',utc=True).as_unit('ns').asi8,
                                      selected.timestamp.dt.as_unit('ns').astype('int64').to_numpy())
        q=np.tile([.1,.2,.3],(2,1));actions={name:np.zeros(2,int) for name in POLICIES};actions['uniform_catalogue']=None
        rows,contrasts,users,b=evaluate(selected,q,actions,'toy',Path(directory))
        assert len(rows)==8 and len(contrasts)==26 and contrasts[0]['mean']==0
    print('SELF-TEST PASSED: paired user clusters, equal-date weighting, missing-date rejection, time blocks, temporal cutoff, millisecond roundtrip and saved comparisons.')
    print('Artificial data only. No reserved outcomes opened.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--self-test',action='store_true');group.add_argument('--preflight',action='store_true');group.add_argument('--run',action='store_true')
    parser.add_argument('--reproduce',action='store_true')
    args=parser.parse_args()
    if args.reproduce and not args.run:
        parser.error('--reproduce requires --run')
    if args.self_test:
        self_test()
    elif args.preflight:
        self_test();plan,provenance=plan_and_sources();verify_archive(plan)
        print('PREFLIGHT PASSED: committed source, locked protocol, pilot source and input hashes match.')
        print('No real outcome analysis or model training performed. Commit:',provenance['git_commit'])
    else:
        run(args.reproduce)


if __name__=='__main__':
    main()
