"""Audit saved gate-timing arrays and every reported row, without fitting models.
Usage: python audit_gate_timing_results.py RUN_DIRECTORY
The audit verifies saved predictions and accounting, not how forests were fitted.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
import pandas as pd

EXPECTED_PROTOCOL_HASH = 'c8ab8a4f0745acb7a93aaee3cfd42aede6e5f8ef4e8537fae878ed47eff3c89c'
TOL = 1e-9


def check(value, message):
    if not value:
        raise ValueError(message)


def near(actual, expected, message):
    check(np.allclose(actual, expected, atol=TOL, rtol=TOL, equal_nan=True), message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def sha(value):
    return hashlib.sha256(value).hexdigest()


def fingerprint(value):
    value = np.ascontiguousarray(value)
    return sha(canonical(dict(shape=value.shape, dtype=str(value.dtype))) + value.tobytes())


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def boolean(value):
    if isinstance(value, (bool, np.bool_)):
        return bool(value)
    check(str(value).lower() in {'true', 'false'}, 'Malformed boolean: ' + str(value))
    return str(value).lower() == 'true'


def indexed(path, columns, count):
    frame = pd.read_csv(path)
    check(len(frame) == count, 'Unexpected row count: ' + path.name)
    check(not frame.duplicated(columns).any(), 'Duplicate keys: ' + path.name)
    return frame.set_index(columns)


def compare(row, values, label):
    for key, value in values.items():
        check(key in row.index, label + ': missing ' + key)
        actual = row[key]
        if value is None:
            check(pd.isna(actual), label + ': undefined value ' + key)
        elif isinstance(value, bool):
            check(boolean(actual) == value, label + ': boolean mismatch ' + key)
        else:
            near(actual, value, label + ': numeric mismatch ' + key)


def tau(x, values):
    return np.where(x[:, 0] < 35, values['younger'], values['older'])


def choice(mu, cost):
    return (mu[:, 1] - mu[:, 0] > cost).astype(int)


def gain_scores(mu, treatment, outcome, delta_actions, cost):
    pseudo = mu[:, 1] - mu[:, 0] + 2 * treatment * (outcome - mu[:, 1]) - 2 * (1-treatment) * (outcome-mu[:, 0])
    scores = delta_actions * (pseudo-cost)
    mean = float(np.mean(scores))
    se = float(np.std(scores, ddof=1) / np.sqrt(len(scores)))
    return dict(estimated_gain=mean, se=se, lower_95=mean-1.96*se, accepted=bool(mean-1.96*se > 0))


def pair_loss(delta, accept):
    return (delta if delta > 0 else 0.) - float(accept) * delta


def individual_regret(action, effects, cost):
    return float(np.mean(np.maximum(effects-cost, 0) - action * (effects-cost)))


def factor(profile, delay):
    if profile == 'unchanged': return 0
    if profile == 'gradual_continue': return delay * .5
    if profile == 'gradual_reverse': return -delay * .5
    if profile == 'abrupt_continue': return float(delay != 0)
    if profile == 'abrupt_reverse': return -float(delay != 0)
    raise ValueError('Unknown future profile')


def validate_split(train, holdout, size, label):
    check(train.dtype.kind in 'iu' and holdout.dtype.kind in 'iu', label + ': noninteger row IDs')
    check(len(np.unique(train)) == len(train) and len(np.unique(holdout)) == len(holdout), label + ': duplicate row IDs')
    check(not np.intersect1d(train, holdout).size, label + ': overlapping row IDs')
    check(np.array_equal(np.sort(np.r_[train, holdout]), np.arange(size)), label + ': incomplete partition')


def audit(directory):
    directory = Path(directory).resolve()
    p = load(directory / 'gate_timing_protocol_v1.json')
    check(sha(canonical(p)) == EXPECTED_PROTOCOL_HASH, 'Protocol snapshot hash mismatch')
    manifest = load(directory / 'manifest.json')
    preflight = load(directory / 'preflight.json')
    check(manifest['status'] == 'complete', 'Run is incomplete')
    check(manifest['protocol_sha256'] == EXPECTED_PROTOCOL_HASH, 'Manifest protocol mismatch')
    check(manifest['provenance'] == preflight['provenance'], 'Preflight provenance mismatch')
    check(manifest['provenance']['versions'] == p['execution']['expected_versions'], 'Recorded run versions mismatch')
    check(not preflight['freshness']['collisions'], 'Preflight recorded seed collisions')
    check(manifest['estimator_parameters'] == p['models_and_gate']['random_forest'], 'Estimator declaration mismatch')
    hashes = manifest['provenance']['hashes']
    for name in ['run_gate_timing_followup.py', 'gate_timing_protocol_v1.json']:
        matches = [value for key, value in hashes.items() if key.endswith('/'+name)]
        check(len(matches) == 1, 'Missing source hash ' + name)
        check(sha((directory/name).read_bytes().replace(b'\r\n',b'\n')) == matches[0], 'Snapshot source hash mismatch ' + name)
    allocation, cfg = p['sample_allocation'], p['generator']
    mode = manifest['mode']
    check(mode in ['pilot','validation'], 'Unknown phase')
    seeds = (allocation['engineering_pilot_master_seeds'] if mode == 'pilot' else
             list(range(allocation['validation_master_seeds_start_inclusive'], allocation['validation_master_seeds_end_exclusive'])))
    check(manifest['seeds'] == seeds and manifest['completed_seeds'] == seeds and preflight['seeds'] == seeds, 'Incomplete or altered master seeds')
    n = len(seeds)
    decision = indexed(directory/'gate_decisions.csv', ['master_seed','condition','gate'], 6*n)
    outcome = indexed(directory/'gate_outcomes.csv', ['master_seed','condition','profile','delay','gate'], 90*n)
    baseline = indexed(directory/'benchmark_outcomes.csv', ['master_seed','condition','profile','delay','policy'], 225*n)
    primary = indexed(directory/'primary_seed_differences.csv', ['master_seed'], n)
    check(set(primary.index) == set(seeds), 'Wrong primary master seeds')
    primary_values, max_residual = [], 0.
    cost = cfg['cost']
    for master in seeds:
        print('Auditing saved arrays:', master, flush=True)
        details = load(directory/f'seed_{master}.json')
        check(details['master_seed'] == master, 'Seed metadata mismatch')
        with np.load(directory/f'seed_{master}.npz', allow_pickle=False) as saved:
            arrays = {key:saved[key] for key in saved.files}
        check(set(arrays) == set(details['fingerprints']), 'Saved array keys mismatch')
        for key, a in arrays.items():
            check(fingerprint(a) == details['fingerprints'][key], f'{master}: fingerprint mismatch {key}')
            check(np.isfinite(a).all(), f'{master}: nonfinite array {key}')
        x0, x, xd = arrays['initial_x'], arrays['current_x'], arrays['deployment_x']
        check(x0.shape == (cfg['initial_records'],2) and x.shape == (cfg['current_records'],2) and xd.shape == (cfg['deployment_feature_panel_records'],2), 'Feature shapes mismatch')
        for value in [x0,x,xd]:
            check(((value[:,0]>=18)&(value[:,0]<=65)&(value[:,0]==np.floor(value[:,0]))).all(), 'Invalid ages')
            check((value[:,1]>=0).all(), 'Negative spending')
        for prefix, size in [('initial',len(x0)),('current',len(x))]:
            check(arrays[prefix+'_t'].shape == (size,) and np.isin(arrays[prefix+'_t'],[0,1]).all(), 'Invalid treatment')
            check(arrays[prefix+'_noise'].shape == (size,), 'Noise shape mismatch')
        tr, hold = arrays['initial_train'], arrays['initial_holdout']
        ct, cg = arrays['current_train'], arrays['gate_indices']
        validate_split(tr,hold,len(x0),'initial'); validate_split(ct,cg,len(x),'current')
        check(len(tr)==int(.8*len(x0)) and len(ct)==int(.7*len(x)), 'Wrong split sizes')
        strata = (x[:,0]<35).astype(int)*2+arrays['current_t']
        check(len(np.unique(strata[ct]))==4 and len(np.unique(strata[cg]))==4, 'Missing split stratum')
        near(arrays['initial_y'], 50+.4*x0[:,1]+arrays['initial_t']*tau(x0,cfg['initial_effects'])+arrays['initial_noise'], 'Initial outcome formula')
        for code, value in details['child_seeds'].items():
            expected = int(np.random.SeedSequence([master,int(code)]).generate_state(1,dtype=np.uint32)[0])
            check(value == expected, 'Child seed allocation mismatch')
        imug, imud = arrays['initial_gate_mu'],arrays['initial_deployment_mu']
        check(imug.shape==(len(cg),2) and imud.shape==(len(xd),2), 'Initial prediction shape')
        ai_g, ai_d = choice(imug,cost),choice(imud,cost)
        seed_primary = []
        for condition in allocation['current_response_conditions']:
            y = arrays[condition+'_y']
            near(y, 50+.4*x[:,1]+arrays['current_t']*tau(x,cfg['current_effects'][condition])+arrays['current_noise'], 'Current outcome formula')
            cmug, cmud = arrays[condition+'_gate_mu'],arrays[condition+'_deployment_mu']
            check(cmug.shape==(len(cg),2) and cmud.shape==(len(xd),2), 'Candidate prediction shape')
            ac_g, ac_d = choice(cmug,cost),choice(cmud,cost)
            current_g = tau(x[cg],cfg['current_effects'][condition])
            current_d = tau(xd,cfg['current_effects'][condition])
            current_truth = float(np.mean((ac_g-ai_g)*(current_g-cost)))
            states = {}
            for label,mu in [('frozen',imug),('refreshed',cmug)]:
                states[label] = gain_scores(mu,arrays['current_t'][cg],y[cg],ac_g-ai_g,cost)
                compare(decision.loc[(master,condition,label)],dict(**states[label],true_current_gain_gate_panel=current_truth),'gate decision')
            zero_controls = []
            for profile in allocation['future_profiles']:
                for delay in allocation['delays_periods']:
                    m = factor(profile,delay)
                    fg = current_g + m*tau(x[cg],cfg['future_step_vectors'][condition])
                    fd = current_d + m*tau(xd,cfg['future_step_vectors'][condition])
                    delta = float(np.mean((ac_d-ai_d)*(fd-cost)))
                    truth_on_gate = float(np.mean((ac_g-ai_g)*(fg-cost)))
                    target = p['outcomes']['primary_regime']
                    is_primary = condition in target['current_conditions'] and profile==target['future_profile'] and delay==target['delay_periods']
                    common = dict(true_pair_gain=delta,primary=is_primary,
                        future_younger=cfg['current_effects'][condition]['younger']+m*cfg['future_step_vectors'][condition]['younger'],
                        future_older=cfg['current_effects'][condition]['older']+m*cfg['future_step_vectors'][condition]['older'])
                    losses = {}
                    if delay==0: zero_controls.append(delta)
                    for label,state in states.items():
                        accept, estimate = state['accepted'],state['estimated_gain']
                        error = estimate-delta
                        terms = [estimate-current_truth,current_truth-truth_on_gate,truth_on_gate-delta]
                        residual = abs(sum(terms)-error); max_residual=max(max_residual,residual)
                        check(residual < TOL, 'Timing decomposition failed')
                        loss = pair_loss(delta,accept); losses[label]=loss
                        check(loss>=-TOL, 'Negative selection loss')
                        selected = ac_d if accept else ai_d
                        values = dict(**common,**state,selection_loss=loss,signed_error=error,absolute_error=abs(error),squared_error=error*error,
                            current_estimation_error=terms[0],response_transfer=terms[1],panel_composition=terms[2],
                            accepted_harmful=bool(accept and delta < -1e-10),rejected_helpful=bool(not accept and delta > 1e-10),tied=bool(abs(delta)<=1e-10),
                            individual_oracle_regret=individual_regret(selected,fd,cost),harmful_treatment_fraction=float(np.mean((selected==1)&(fd<cost))))
                        compare(outcome.loc[(master,condition,profile,delay,label)],values,'gate outcome')
                    if is_primary: seed_primary.append(losses['refreshed']-losses['frozen'])
                    for label,a,accept in [('always_retain',ai_d,False),('always_accept',ac_d,True),('offline_best_of_two',ac_d if delta>0 else ai_d,delta>0),('treat_all',np.ones(len(xd)),None),('treat_none',np.zeros(len(xd)),None)]:
                        loss = None if accept is None else pair_loss(delta,accept)
                        check(label!='offline_best_of_two' or abs(loss)<TOL, 'Nonzero best-of-two loss')
                        compare(baseline.loc[(master,condition,profile,delay,label)],dict(**common,selection_loss=loss,individual_oracle_regret=individual_regret(a,fd,cost)),'baseline outcome')
            near(zero_controls,np.repeat(zero_controls[0],len(zero_controls)),'Zero-delay profile identity')
        check(len(seed_primary)==2,'Wrong primary cell count')
        value = float(np.mean(seed_primary)); primary_values.append(value)
        near(value,details['primary_difference'],'Per-seed JSON primary mismatch')
        near(value,primary.loc[master,'primary_difference'],'Primary CSV mismatch')
        near(details['runtime_seconds'],primary.loc[master,'runtime_seconds'],'Runtime summary mismatch')
    summary = load(directory/'analysis.json')
    values = np.asarray(primary_values)
    check(summary['mode']==mode and summary['independent_master_seeds']==n, 'Analysis phase or count')
    check(summary['protocol_primary']==p['outcomes']['primary_regime'] and summary['negative_favors']=='refreshed','Analysis target mismatch')
    near(summary['primary_mean'],np.mean(values),'Primary average mismatch')
    interval = None
    if mode=='validation':
        cfg_boot = p['analysis']['primary_bootstrap']
        check(summary['bootstrap_resamples']==cfg_boot['resamples'] and summary['bootstrap_seed']==cfg_boot['seed'],'Bootstrap settings')
        rng = np.random.default_rng(cfg_boot['seed'])
        indices = rng.integers(0,n,size=(cfg_boot['resamples'],n))
        replicates = np.sum(values[indices],axis=1)/n
        interval = np.percentile(replicates,[2.5,97.5]).tolist()
        near(summary['bootstrap_interval'],interval,'Paired master-seed bootstrap mismatch')
        near(summary['monte_carlo_se'],np.std(values,ddof=1)/np.sqrt(n),'Monte Carlo SE mismatch')
    else:
        check(summary['bootstrap_interval'] is None and summary['monte_carlo_se'] is None,'Pilot must not report inferential interval')
    metrics=['selection_loss','signed_error','absolute_error','squared_error','individual_oracle_regret','accepted_harmful','rejected_helpful']
    calculated=outcome.reset_index().groupby(['condition','profile','delay','gate'])[metrics].mean().sort_index()
    secondary=indexed(directory/'secondary_descriptive.csv',['condition','profile','delay','gate'],90).sort_index()
    check(calculated.index.equals(secondary.index),'Secondary factor keys mismatch')
    near(calculated.to_numpy(dtype=float),secondary[metrics].to_numpy(dtype=float),'Secondary summary mismatch')
    return dict(status='passed',scope='saved_predictions_scores_and_summary_audit',mode=mode,master_seeds=n,
                gate_decisions_checked=6*n,gate_outcomes_checked=90*n,benchmark_rows_checked=225*n,
                primary_mean=float(values.mean()),bootstrap_interval=interval,max_decomposition_residual=max_residual,
                model_refits=False,raw_real_world_logs_opened=False,new_study_seeds_generated=False,
                verified=['protocol and source snapshots','saved array fingerprints and shapes','outcome formulas',
                    'split row partitions and strata','declared child seeds','AIPW and strict acceptance',
                    'all future profiles and delays','selection loss and individual-oracle regret',
                    'adverse decisions and simple baselines','three-term decomposition','zero-delay identity',
                    'paired primary aggregation and seed-block bootstrap','all secondary descriptive means'],
                limitations=['No independent refit of forests or verification of the fitting process from model objects.',
                    'Freshness report and recorded version/source provenance checked; historical scan not repeated.',
                    'No inference of real-world safety, equivalence or universal superiority.'])


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_directory',type=Path)
    args=parser.parse_args()
    output=args.run_directory/'saved_output_audit.json'
    check(not output.exists(),'Audit output exists; do not overwrite it.')
    try:
        report=audit(args.run_directory)
    except Exception as exc:
        # Preserve the failure without changing the research outputs.
        report=dict(status='failed',error=repr(exc),model_refits=False)
        output=args.run_directory/('saved_output_audit_FAILED_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.json')
        output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        raise
    report.update(audit_time_UTC=datetime.now(timezone.utc).isoformat(),auditor_sha256=sha(Path(__file__).read_bytes().replace(b'\r\n',b'\n')),
                  audit_versions=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__))
    with output.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2,allow_nan=False)
    print('AUDIT PASSED:',report['scope'])
    print('Audit saved:',output)
    print('No models refitted. No new research seeds generated.')


if __name__=='__main__':
    main()
