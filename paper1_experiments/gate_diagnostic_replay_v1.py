"""Retrospective diagnostic replay. No controller changes or fresh evidence."""
import argparse
import ast
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import platform
import time
import numpy as np
import pandas as pd
import sklearn


def loss_difference(truth, candidate, incumbent, cost):
    """Positive is lower candidate oracle regret on these same observations."""
    return float(np.mean((np.asarray(candidate, float)-np.asarray(incumbent, float))
                         * (np.asarray(truth, float)-cost)))


def compare_frames(actual, expected, keys):
    if actual.duplicated(keys).any() or expected.duplicated(keys).any():
        raise RuntimeError('Duplicate replay keys')
    a=actual.set_index(keys).sort_index()
    b=expected.set_index(keys).sort_index()
    pd.testing.assert_frame_equal(a[b.columns],b,check_dtype=False,
        check_exact=False,rtol=1e-12,atol=1e-12)


def instrument(module, callback):
    # Insert an offline read-only callback immediately before the unchanged gate decision.
    source=inspect.getsource(module.evaluate_stream)
    needle='                if lower > 0:\n'
    assert source.count(needle)==1, 'Frozen controller changed'
    source=source.replace(needle,
        '                diagnostic_callback(row, candidate, st["model"], gate, seed, scenario, period, n, onset)\n'+needle)
    namespace=dict(module.__dict__,diagnostic_callback=callback)
    exec(compile(source,'<instrumented frozen evaluate_stream>','exec'),namespace)
    return namespace['evaluate_stream']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',required=True,type=Path)
    parser.add_argument('--limit',type=int,default=1,
        help='1 is a reproducibility smoke replay; use 117 only after it passes')
    args=parser.parse_args()
    if not 1<=args.limit<=117:parser.error('limit must be 1..117')
    root=Path(__file__).resolve().parent
    reference=args.reference.resolve()
    manifest=json.loads((reference/'manifest.json').read_text())
    if json.loads((reference/'checkpoint.json').read_text()).get('status')!='complete':
        raise RuntimeError('Reference is incomplete')
    current=dict(numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__)
    if current!=manifest['versions']:raise RuntimeError('Software versions differ from reference')
    if platform.python_version()!=manifest['python'].split()[0]:
        raise RuntimeError('Python version differs from reference')
    source=root/'model_onset_sensitivity_v1.py'
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    if digest(source)!=digest(reference/'script_snapshot.py'):
        raise RuntimeError('Sensitivity source differs from archived source')
    for name in ('monitoring_signal_ablation_v1.py','integrated_causal_monitoring_v2_xai.py','monitoring_schedule_comparison_v1.py'):
        if digest(root/name)!=digest(reference/(name+'.snapshot')):
            raise RuntimeError('Frozen source differs: '+name)
    spec=importlib.util.spec_from_file_location('frozen_sensitivity',source)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    expected=pd.read_csv(reference/'period_log.csv')
    configurations=expected[['initial_seed','scenario','onset','seed']].drop_duplicates().iloc[:args.limit]
    output=root/'gate_diagnostic_replay_v1_results'/('run_'+time.strftime('%Y%m%d_%H%M%S'))
    output.mkdir(parents=True,exist_ok=False)
    status=dict(status='running',reference=str(reference),versions=current,
        scope='Retrospective replay of exposed development seeds; not independent evidence',
        selected_configurations=len(configurations),candidate_benefit='incumbent regret minus candidate regret',
        next_window_scope='One-window fixed-model comparison, not a counterfactual future controller trajectory',
        equality_tolerance='rtol=atol=1e-12; categorical event indicators exact',
        runner_sha256=digest(Path(__file__)))
    def checkpoint():
        (output/'checkpoint.json').write_text(json.dumps(status,indent=2))
    checkpoint();diagnostics=[];all_periods=[];started=time.perf_counter()
    initial_fit=None
    for count,config in enumerate(configurations.itertuples(index=False),1):
        fit,scenario,onset,seed=config
        if fit!=initial_fit:
            train,_=module.train_test_split(module.initial_data(fit),test_size=.2,random_state=42)
            baseline=module.fit_models(train,fit)
            background=pd.read_csv(reference/f'background_{fit}.csv')
            explainer=module.base.TwoFeatureShapley(baseline,background)
            calibration=pd.read_csv(reference/f'calibration_{fit}.csv')
            center=calibration.center.to_numpy();scale=calibration.scale.to_numpy()
            thresholds=json.loads((reference/f'thresholds_{fit}.json').read_text())
            initial_fit=fit
        cache={}
        def callback(row,candidate,incumbent,gate,stream,scen,period,n,onset_value):
            key=(period,id(candidate),id(incumbent))
            if key not in cache:
                ca=module.policy(candidate,gate);ia=module.policy(incumbent,gate)
                gate_benefit=loss_difference(gate.true_effect,ca,ia,module.COST)
                next_benefit=None
                if period<module.PERIODS:
                    future=module.make_window(stream,period+1,scen,n,onset=onset_value)
                    next_benefit=loss_difference(future.true_effect,module.policy(candidate,future),
                        module.policy(incumbent,future),module.COST)
                cache[key]=(gate_benefit,next_benefit)
            gate_benefit,next_benefit=cache[key]
            diagnostics.append(dict(initial_seed=fit,**{k:row[k] for k in
                ('seed','scenario','period','method','review_budget','gate_mean','gate_lower')},
                onset=onset,accepted=bool(row['gate_lower']>0),
                true_gate_benefit=gate_benefit,next_window_benefit=next_benefit,
                next_window_available=period<module.PERIODS))
        evaluate=instrument(module,callback)
        rows,runs,bench=evaluate(seed,scenario,1000,baseline,center,scale,thresholds,
            explainer,None,None,None,onset=onset)
        actual=pd.DataFrame(rows).assign(initial_seed=fit,onset=onset)
        subset=expected[(expected.initial_seed==fit)&(expected.scenario==scenario)
                        &(expected.onset==onset)&(expected.seed==seed)]
        try:
            compare_frames(actual,subset,['initial_seed','scenario','onset','seed','period','method','review_budget'])
        except Exception:
            status.update(status='reproduction_failed',failed_configuration=list(config));checkpoint()
            raise
        all_periods.append(actual)
        pd.DataFrame(diagnostics).to_csv(output/'review_diagnostics.csv',index=False)
        status['verified_configurations']=count;checkpoint()
        print(f'REPRODUCED {count}/{len(configurations)}: {list(config)}',flush=True)
    pd.concat(all_periods,ignore_index=True).to_csv(output/'reproduced_period_log.csv',index=False)
    status.update(status='complete',elapsed_seconds=time.perf_counter()-started,
        all_selected_period_fields_reproduced=True)
    checkpoint();print('COMPLETE:',output)


if __name__=='__main__':main()
