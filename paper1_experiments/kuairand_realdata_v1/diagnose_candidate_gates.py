"""Post-hoc diagnostics of the exposed KuaiRand run; no experiment rerun.

Daily candidate-minus-predecision-incumbent estimates are computed from saved
scores. Intervals condition on the recorded models/paths. They do NOT establish
false rejection, oracle truth or the performance of an alternative controller.
"""
import argparse
from datetime import datetime,timezone,timedelta
import hashlib
import json
from pathlib import Path
import uuid
import numpy as np
import pandas as pd

LOCAL=timezone(timedelta(hours=8))
DATES=pd.date_range('2022-04-25','2022-05-08').strftime('%Y-%m-%d').tolist()


def digest(path):
    with Path(path).open('rb') as handle:return hashlib.file_digest(handle,'sha256').hexdigest()


def flag(value):
    assert str(value).lower() in ['true','false']
    return str(value).lower()=='true'


def reference(before,selected,accepted):
    if before=='initial':return 'initial_no_update'
    if not accepted and selected==before:return 'frozen_gate_path'
    raise ValueError('Predecision incumbent evaluation scores unavailable; do not substitute the accepted candidate or invent a counterfactual')


def pattern(dr,ips,tolerance=1e-12):
    if dr>tolerance and ips>tolerance:return 'both_positive'
    if dr<-tolerance and ips<-tolerance:return 'both_negative'
    if dr*ips<0 and abs(dr)>tolerance and abs(ips)>tolerance:return 'estimator_sign_disagreement'
    return 'zero_or_near_zero_in_at_least_one_estimator'


def bootstrap(values,users,times):
    """Per-date paired intervals; resampling is NOT independent policy/arm draws."""
    ids,index=np.unique(users,return_inverse=True);n=len(ids)
    counts=np.bincount(index);sums=np.zeros((n,2));np.add.at(sums,index,values)
    if n<2:raise ValueError('Insufficient user clusters')
    rng=np.random.default_rng(42);draws=np.empty((1000,2))
    for start in range(0,1000,32):
        stop=min(start+32,1000)
        w=rng.multinomial(n,np.full(n,1/n),size=stop-start).astype(float)
        draws[start:stop]=(w@sums)/(w@counts)[:,None]
    user_ci=np.quantile(draws,[.025,.975],axis=0).T
    code,blocks=pd.factorize(times.dt.floor('30min'),sort=True)
    if len(blocks)<2:raise ValueError('Insufficient time blocks')
    count=np.bincount(code);total=np.column_stack([np.bincount(code,weights=values[:,j]) for j in range(2)])
    rng=np.random.default_rng(42);chosen=rng.integers(0,len(blocks),size=(1000,len(blocks)))
    averages=total[chosen].sum(1)/count[chosen].sum(1)[:,None]
    return user_ci,np.quantile(averages,[.025,.975],axis=0).T


def diagnose(run):
    run=Path(run)
    manifest=json.loads((run/'manifest.json').read_text())
    audited=json.loads((run/'saved_output_audit.json').read_text())
    assert manifest['status']=='complete' and audited['status']=='passed'
    assert audited['run_id']==manifest['run_id'] and audited['mode']=='saved_score_and_summary_audit'
    gates=pd.read_csv(run/'gate_comparison.csv')
    evaluation=pd.read_csv(run/'evaluation.csv')
    assert len(gates)==28 and len(evaluation)==112
    output=run.parent.parent/'diagnostic_runs'/('posthoc_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8])
    output.mkdir(parents=True,exist_ok=False)
    record=dict(status='running',posthoc=True,original_run_id=manifest['run_id'],original_run_commit=manifest['git_commit'],
                outcome_exposure='All original results and preliminary daily contrasts inspected before this diagnostic script.',
                models_refitted=False,raw_logs_reloaded=False,original_protocol_or_outputs_modified=False,
                bootstrap_resamples=1000,bootstrap_seed=42,
                intervals='Per-date exploratory paired user-cluster and separate 30-minute-block percentile intervals.',
                limitations=['Conditional on recorded fitted models, incumbent paths and observed contexts.',
                  'Daily intervals are unadjusted for multiple comparisons and do not constitute prospective validation.',
                  'User and time resampling handle different dependence; neither captures all training, selection and temporal uncertainty.',
                  'Positive later estimates do not identify true missed beneficial updates or prove an earlier gate was overly cautious.',
                  'No counterfactual controller paths, alternative training windows, review schedules or threshold outcomes are simulated.',
                  'Daily gains must not be summed as achievable savings; old incumbents would change under alternative decisions.'],
                input_sha256={n:digest(run/n) for n in ['manifest.json','gate_comparison.csv','evaluation.csv','saved_output_audit.json']},
                diagnostic_source_sha256_LF_normalized=hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n',b'\n')).hexdigest())
    report=output/'diagnostic_manifest.json'
    def save():report.write_text(json.dumps(record,indent=2,allow_nan=False),encoding='utf-8')
    save();rows=[]
    try:
        for date in DATES:
            g=gates.loc[gates.date.eq(date)].set_index('gate')
            assert set(g.index)=={'frozen','refreshed'}
            f,r=g.loc['frozen'],g.loc['refreshed'];accepted=flag(f.candidate_accepted)
            assert accepted==flag(r.candidate_accepted)
            assert f.incumbent_before==r.incumbent_before and f.selected_model==r.selected_model
            ref=reference(f.incumbent_before,f.selected_model,accepted)
            filename=date+'_evaluation_scores.npz';record['input_sha256'][filename]=digest(run/filename)
            with np.load(run/filename,allow_pickle=False) as z:
                assert np.array_equal(z['frozen_gate_path_actions'],z['refreshed_gate_path_actions'])
                times=pd.Series(pd.to_datetime(z['timestamp_ms'],unit='ms',utc=True).tz_convert(LOCAL))
                assert times.ge(pd.Timestamp(date+'T18:00:00+08:00')).all()
                assert times.lt(pd.Timestamp(date,tz=LOCAL)+pd.Timedelta(days=1)).all()
                values=np.column_stack([z['always_update_current_candidate_'+e]-z[ref+'_'+e] for e in ['dr','ips']])
                assert np.isfinite(values).all()
                uci,tci=bootstrap(values,z['user_id'],times)
                er=evaluation.loc[evaluation.date.eq(date)].set_index('policy')
                for j,e in enumerate(['dr','ips']):
                    np.testing.assert_allclose(values[:,j].mean(),er.loc['always_update_current_candidate',e+'_mean']-er.loc[ref,e+'_mean'],atol=1e-12,rtol=1e-9)
                row=dict(date=date,accepted=accepted,incumbent_before=f.incumbent_before,selected_model=f.selected_model,
                         later_reference_policy=ref,records=len(times),users=len(np.unique(z['user_id'])),
                         candidate_incumbent_action_disagreement=float(np.mean(z['always_update_current_candidate_actions']!=z[ref+'_actions'])))
                for name,source in [('frozen',f),('refreshed',r)]:
                    row[name+'_gate_mean']=float(source['mean']);row[name+'_gate_lower_95']=float(source.row_lower_95)
                    row[name+'_rejection_basis']=('accepted' if accepted else 'zero_matching_rows' if flag(source.zero_match_rejection)
                        else 'nonpositive_gate_mean' if source['mean']<=0 else 'positive_gate_mean_but_lower_bound_not_positive')
                for j,e in enumerate(['dr','ips']):
                    row['later_'+e+'_mean']=float(values[:,j].mean())
                    row['later_'+e+'_user_lower']=float(uci[j,0]);row['later_'+e+'_user_upper']=float(uci[j,1])
                    row['later_'+e+'_time_lower']=float(tci[j,0]);row['later_'+e+'_time_upper']=float(tci[j,1])
                row['later_point_estimate_pattern']=pattern(row['later_dr_mean'],row['later_ips_mean'])
                row['both_pointwise_user_intervals_positive']=bool(np.all(uci[:,0]>0))
                rows.append(row)
            print('Diagnosed:',date,flush=True)
            pd.DataFrame(rows).to_csv(output/'daily_candidate_diagnostics.csv',index=False);save()
        frame=pd.DataFrame(rows);rejected=frame.loc[~frame.accepted]
        summary=dict(posthoc=True,dates=len(frame),accepted_dates=frame.loc[frame.accepted,'date'].tolist(),
                     rejected_dates=len(rejected),rejected_point_estimate_patterns=rejected.later_point_estimate_pattern.value_counts().to_dict(),
                     rejected_both_positive_dates=rejected.loc[rejected.later_point_estimate_pattern.eq('both_positive'),'date'].tolist(),
                     rejected_both_pointwise_user_intervals_positive_dates=rejected.loc[rejected.both_pointwise_user_intervals_positive,'date'].tolist(),
                     interpretation='Descriptive diagnostics on exposed data; not true false-rejection rates, operational-constraint effects or alternative-policy value.')
        (output/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        record['status']='complete';save()
        columns=['date','accepted','later_dr_mean','later_dr_user_lower','later_dr_user_upper','later_ips_mean','later_ips_user_lower','later_ips_user_upper']
        print(frame[columns].round(6).to_string(index=False))
        print('POST-HOC DIAGNOSTICS COMPLETE:',output)
        return output
    except BaseException as error:
        record.update(status='failed',error=repr(error));save();raise


def self_test():
    assert reference('initial','replacement',True)=='initial_no_update'
    assert reference('old','old',False)=='frozen_gate_path'
    try:reference('old','new',True)
    except ValueError:pass
    else:raise AssertionError('Unavailable old-incumbent predictions silently replaced')
    assert pattern(1,-1)=='estimator_sign_disagreement'
    assert pattern(1,2)=='both_positive' and pattern(-1,-2)=='both_negative'
    times=pd.Series(pd.to_datetime(['2022-04-25T18:00:00+08:00','2022-04-25T18:30:00+08:00']))
    values=np.array([[0.,0.],[2.,0.]])
    u,t=bootstrap(values,np.array(['a','b']),times)
    np.testing.assert_allclose(u,[[0,2],[0,0]]);np.testing.assert_allclose(t,[[0,2],[0,0]])
    print('SELF-TEST PASSED: predecision reference, unavailable-reference rejection, signs and paired intervals.')
    print('No research files opened.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_directory',type=Path,nargs='?');parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:self_test()
    elif args.run_directory is None:parser.error('Provide the completed original run directory')
    else:diagnose(args.run_directory)
