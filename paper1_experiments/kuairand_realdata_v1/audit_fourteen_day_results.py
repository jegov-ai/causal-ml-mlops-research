"""Independent saved-output audit. No model refits and no raw log loading.

Default mode requires this run's detailed NPZ scores and user aggregates.
--summaries-only checks tables and time blocks, but NOT user-cluster intervals.
An existing successful audit report is never overwritten.
"""
import argparse
from datetime import datetime, timezone, timedelta
import hashlib
import json
from pathlib import Path
import traceback
import uuid

import numpy as np
import pandas as pd

DATES=pd.date_range('2022-04-25','2022-05-08').strftime('%Y-%m-%d').tolist()
GROUP_PROB=np.array([1743,5601,239],float)/7583
POLICIES=['frozen_gate_path','refreshed_gate_path','initial_no_update',
          'always_update_current_candidate','uniform_catalogue','always_short','always_long','always_unknown']
PAIRS=[(POLICIES[1],POLICIES[0])]+[(g,b) for g in POLICIES[:2] for b in POLICIES[2:]]
LABELS=[a+'_minus_'+b+'__'+e for a,b in PAIRS for e in ['dr','ips']]
LOCAL=timezone(timedelta(hours=8))
PROTOCOL_HASH='c277dde946e43957f2c8533a86019d8343459c7e33a802e6a5870d3562d657c3'


def close(actual,expected):
    np.testing.assert_allclose(actual,expected,rtol=1e-9,atol=1e-12,equal_nan=False)


def boolean(value):
    assert str(value).lower() in ['true','false'],'Invalid boolean'
    return str(value).lower()=='true'


def stats(x):
    assert len(x)>=2 and np.isfinite(x).all()
    mean=float(np.mean(x));se=float(np.std(x,ddof=1)/np.sqrt(len(x)))
    return dict(mean=mean,row_se=se,row_lower_95=mean-1.96*se,row_upper_95=mean+1.96*se)


def check_stats(row,x,prefix=''):
    for key,value in stats(x).items():
        close(float(row[prefix+key]),value)


def scores(z,q,actions):
    logged=z['group'];y=z['long_view'];n=len(y)
    assert logged.shape==(n,) and np.isin(logged,[0,1,2]).all()
    assert np.isin(y,[0,1]).all() and q.shape==(n,3)
    assert np.isfinite(q).all() and ((q>=0)&(q<=1)).all()
    if actions is None:
        target=GROUP_PROB[logged];direct=np.sum(q*GROUP_PROB[None,:],axis=1)
    else:
        assert actions.shape==(n,) and np.isin(actions,[0,1,2]).all()
        target=(actions==logged).astype(float);direct=q[np.arange(n),actions.astype(int)]
    weight=target/GROUP_PROB[logged]
    return direct+weight*(y-q[np.arange(n),logged]),weight*y,weight


def check_support(row,z,w,prefix=''):
    positive=w>0;total=float(w.sum())
    expected=dict(matched_rows=int(positive.sum()),matched_long_views=int(((z['long_view']==1)&positive).sum()),
                  matched_users=len(np.unique(z['user_id'][positive])),
                  weight_ess=total**2/float(w@w) if total else 0.,
                  largest_weight_percent=100*float(w.max())/total if total else None)
    for key,value in expected.items():
        if value is None:
            assert pd.isna(row[prefix+key])
        else:
            close(float(row[prefix+key]),value)


def check_context(z,window):
    n=len(z['long_view'])
    assert n==window['records'] and int(z['long_view'].sum())==window['long_views']
    assert len(np.unique(z['user_id']))==window['users']
    assert len(np.unique(z['csv_row_index']))==n
    assert int(z['date_mismatch'].sum())==window['date_mismatches']
    # Always decode explicitly as milliseconds, including on pandas 3.x.
    clock=pd.Series(pd.to_datetime(z['timestamp_ms'],unit='ms',utc=True).tz_convert(LOCAL))
    assert clock.is_monotonic_increasing
    assert clock.iloc[0]==pd.Timestamp(window['first_timestamp'])
    assert clock.iloc[-1]==pd.Timestamp(window['last_timestamp'])
    return clock


def bootstrap_time(days):
    rng=np.random.default_rng(42);estimates=[];draws=np.zeros((1000,len(LABELS)))
    for day in days:
        count=np.asarray(day['counts'],float);sums=np.asarray(day['sums'],float).T
        assert len(count)>=2 and (count>0).all() and sums.shape==(len(count),len(LABELS))
        assert np.isfinite(sums).all()
        estimates.append(sums.sum(0)/count.sum())
        selected=rng.integers(0,len(count),size=(1000,len(count)))
        draws+=(sums[selected].sum(1)/count[selected].sum(1)[:,None])/14
    return np.mean(estimates,axis=0),np.quantile(draws,[.025,.975],axis=0).T


def bootstrap_users(days):
    # Independent implementation: compute each date separately for common user draws.
    union=np.unique(np.concatenate([d['users'] for d in days]));n=len(union)
    k=len(LABELS);date_counts=np.zeros((n,14));date_sums=[]
    for i,day in enumerate(days):
        index=np.searchsorted(union,day['users']);assert len(np.unique(index))==len(index)
        date_counts[index,i]=day['counts']
        values=np.zeros((n,k));values[index]=day['sums'];date_sums.append(values)
    rng=np.random.default_rng(42);draws=np.empty((1000,k));prob=np.full(n,1/n)
    for start in range(0,1000,16):
        stop=min(start+16,1000);weights=rng.multinomial(n,prob,size=stop-start).astype(float)
        estimate=np.zeros((stop-start,k))
        for i,values in enumerate(date_sums):
            denominator=weights@date_counts[:,i]
            assert (denominator>0).all(),'Empty bootstrap date'
            estimate+=(weights@values)/denominator[:,None]/14
        draws[start:stop]=estimate
    return np.quantile(draws,[.025,.975],axis=0).T,n


def audit(path,summaries_only=False):
    path=Path(path)
    if not summaries_only and (path/'saved_output_audit.json').exists():
        raise FileExistsError('A successful audit is already saved; it will not be overwritten')
    read=lambda name:json.loads((path/name).read_text(encoding='utf-8'))
    manifest=read('manifest.json');aggregate=read('aggregate_contrasts.json');blocks=read('bootstrap_blocks.json')
    gates=pd.read_csv(path/'gate_comparison.csv');evaluation=pd.read_csv(path/'evaluation.csv')
    contrasts=pd.read_csv(path/'daily_paired_contrasts.csv')
    assert manifest['status']=='complete' and manifest['stage']=='complete'
    assert manifest['timestamp_array_unit']=='ms' and manifest['timestamp_array_field']=='timestamp_ms'
    assert manifest['protocol_canonical_sha256']==PROTOCOL_HASH
    assert aggregate['dates']==DATES and blocks['dates']==DATES and blocks['labels']==LABELS
    assert aggregate['bootstrap_resamples']==1000 and aggregate['seed']==42
    assert len(gates)==28 and len(evaluation)==112 and len(contrasts)==364
    assert set(gates.date)==set(DATES) and set(gates.gate)=={'frozen','refreshed'}
    assert not gates.duplicated(['date','gate']).any()
    assert not evaluation.duplicated(['date','policy']).any()
    assert not contrasts.duplicated(['date','contrast']).any()
    windows={(w['date'],w['part']):w for w in manifest['windows']}
    assert len(windows)==43 and len(manifest['windows'])==43
    assert set(windows)=={('development','initial_training')}|{(d,p) for d in DATES for p in ['candidate_training','gate_check','subsequent_evaluation']}
    initial=windows['development','initial_training']
    assert initial['records']==120645 and initial['long_views']==10128
    for (date,part),w in windows.items():
        assert 0<=w['long_views']<=w['records'] and 0<w['users']<=w['records']
        if part=='initial_training':
            lo,hi=pd.Timestamp('2022-04-22T00:00+08:00'),pd.Timestamp('2022-04-25T00:00+08:00')
        else:
            day=pd.Timestamp(date,tz=LOCAL)
            hours={'candidate_training':(-12,12),'gate_check':(12,18),'subsequent_evaluation':(18,24)}
            a,b=hours[part];lo,hi=day+pd.Timedelta(hours=a),day+pd.Timedelta(hours=b)
        assert lo<=pd.Timestamp(w['first_timestamp'])<=pd.Timestamp(w['last_timestamp'])<hi
    paths={'frozen':'initial','refreshed':'initial'};user_days=[];seen_rows=[]
    for date_index,date in enumerate(DATES):
        gate_rows=gates.loc[gates.date==date].set_index('gate')
        for name in paths:
            row=gate_rows.loc[name]
            assert row.incumbent_before==paths[name] and row.candidate_model==date+'_candidate'
            close(row.row_lower_95,row['mean']-1.96*row.row_se)
            close(row.row_upper_95,row['mean']+1.96*row.row_se)
            zero=row.candidate_matched_rows==0 or row.incumbent_matched_rows==0
            accepted=not zero and row.row_lower_95>0
            assert boolean(row.zero_match_rejection)==zero and boolean(row.candidate_accepted)==accepted
            assert row.reason==('zero_matching_rows' if zero else 'positive_lower_bound' if accepted else 'lower_bound_not_positive')
            if accepted:paths[name]=date+'_candidate'
            assert row.selected_model==paths[name]
        if not summaries_only:
            with np.load(path/(date+'_gate_scores.npz'),allow_pickle=False) as z:
                check_context(z,windows[date,'gate_check'])
                assert np.array_equal(z['candidate_actions'],z['refreshed_q'].argmax(1))
                if gate_rows.loc['frozen','incumbent_before']==gate_rows.loc['refreshed','incumbent_before']:
                    assert np.array_equal(z['frozen_incumbent_actions'],z['refreshed_incumbent_actions'])
                for name in paths:
                    row=gate_rows.loc[name];q=z[name+'_q']
                    if row.incumbent_before=='initial':
                        assert np.array_equal(z[name+'_incumbent_actions'],z['frozen_q'].argmax(1))
                    candidate=scores(z,q,z['candidate_actions']);incumbent=scores(z,q,z[name+'_incumbent_actions'])
                    for label,result in [('candidate',candidate),('incumbent',incumbent)]:
                        close(result[0],z[name+'_'+label+'_dr']);close(result[2],z[name+'_'+label+'_weights'])
                        check_support(row,z,result[2],label+'_')
                    check_stats(row,candidate[0]-incumbent[0])
        erows=evaluation.loc[evaluation.date==date].set_index('policy')
        crows=contrasts.loc[contrasts.date==date].set_index('contrast')
        assert set(erows.index)==set(POLICIES) and set(crows.index)==set(LABELS)
        w=windows[date,'subsequent_evaluation'];day=blocks['days'][date_index]
        assert (erows.records==w['records']).all() and (erows.logged_long_views==w['long_views']).all()
        assert (erows.users==w['users']).all() and sum(day['counts'])==w['records']
        block_times=pd.to_datetime(day['blocks'],utc=True)
        assert len(block_times)==len(day['counts']) and not block_times.duplicated().any()
        assert block_times.is_monotonic_increasing
        lo=pd.Timestamp(date+'T18:00:00+08:00');hi=pd.Timestamp(date,tz=LOCAL)+pd.Timedelta(days=1)
        assert ((block_times>=lo)&(block_times<hi)).all()
        for j,(left,right) in enumerate(PAIRS):
            for i,estimator in enumerate(['dr','ips']):
                label=LABELS[2*j+i]
                close(crows.loc[label,'mean'],erows.loc[left,estimator+'_mean']-erows.loc[right,estimator+'_mean'])
                close(crows.loc[label,'mean'],sum(day['sums'][2*j+i])/sum(day['counts']))
        if not summaries_only:
            print('Auditing saved scores:',date,flush=True)
            with np.load(path/(date+'_evaluation_scores.npz'),allow_pickle=False) as z:
                clock=check_context(z,w);seen_rows.append(z['csv_row_index'])
                expected={'always_short':0,'always_long':1,'always_unknown':2}
                for name,value in expected.items():assert np.all(z[name+'_actions']==value)
                assert np.array_equal(z['always_update_current_candidate_actions'],z['common_q'].argmax(1))
                if paths['frozen']==paths['refreshed']:
                    assert np.array_equal(z['frozen_gate_path_actions'],z['refreshed_gate_path_actions'])
                for gate in paths:
                    if paths[gate] in ['initial',date+'_candidate']:
                        reference='initial_no_update' if paths[gate]=='initial' else 'always_update_current_candidate'
                        assert np.array_equal(z[gate+'_gate_path_actions'],z[reference+'_actions'])
                computed={}
                for name in POLICIES:
                    action=None if name=='uniform_catalogue' else z[name+'_actions']
                    dr,ips,weights=scores(z,z['common_q'],action)
                    check_support(erows.loc[name],z,weights);close(weights,z[name+'_weights'])
                    for estimator,values in [('dr',dr),('ips',ips)]:
                        close(values,z[name+'_'+estimator]);check_stats(erows.loc[name],values,estimator+'_')
                        computed[name,estimator]=values
                close(computed['uniform_catalogue','ips'].mean(),z['long_view'].mean())
                vectors=[]
                for left,right in PAIRS:
                    for estimator in ['dr','ips']:
                        values=computed[left,estimator]-computed[right,estimator]
                        check_stats(crows.loc[left+'_minus_'+right+'__'+estimator],values);vectors.append(values)
                values=np.column_stack(vectors)
                user_ids,codes=np.unique(z['user_id'],return_inverse=True)
                user_counts=np.bincount(codes);user_sums=np.zeros((len(user_ids),len(LABELS)))
                np.add.at(user_sums,codes,values)
                with np.load(path/(date+'_user_aggregates.npz'),allow_pickle=False) as saved:
                    assert np.array_equal(saved['user_id'],user_ids)
                    close(saved['counts'],user_counts);close(saved['contrast_sums'],user_sums)
                user_days.append(dict(users=user_ids,counts=user_counts,sums=user_sums))
                block_codes,bins=pd.factorize(clock.dt.floor('30min'),sort=True)
                assert [str(b) for b in bins]==day['blocks']
                close(np.bincount(block_codes),day['counts'])
                for j in range(len(LABELS)):
                    close(np.bincount(block_codes,weights=values[:,j]),day['sums'][j])
    assert manifest['final_selected_models']==paths
    means,time_interval=bootstrap_time(blocks['days'])
    assert len(blocks['days'])==14
    for j,label in enumerate(LABELS):
        item=aggregate['contrasts'][label]
        close(item['mean'],means[j]);close(item['time_block_sensitivity_interval'],time_interval[j])
        assert item['primary']==(j==0)
    if not summaries_only:
        all_rows=np.concatenate(seen_rows);assert len(np.unique(all_rows))==len(all_rows)
        print('Auditing 1,000 paired user-cluster replicates...',flush=True)
        intervals,n=bootstrap_users(user_days)
        assert n==aggregate['user_clusters']==manifest['evaluation_user_clusters']
        for j,label in enumerate(LABELS):close(aggregate['contrasts'][label]['user_cluster_interval'],intervals[j])
        for name,expected in manifest['source_sha256_LF_normalized'].items():
            data=(path/'source_snapshot'/name).read_bytes().replace(b'\r\n',b'\n')
            assert hashlib.sha256(data).hexdigest()==expected
        protocol=json.loads((path/'source_snapshot/fourteen_day_protocol_v1.json').read_text())
        content=json.dumps(protocol,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
        assert hashlib.sha256(content).hexdigest()==PROTOCOL_HASH
    checked=['43 recorded window boundaries and counts','28 gate rules and incumbent carry-forward decisions',
             '112 policy evaluation rows and 364 daily paired contrasts','all 14 dates equally weighted',
             '1000 paired within-date time-block resamples']
    if not summaries_only:
        checked+=['all saved gate/evaluation score arrays and weight diagnostics','saved action identities where independently comparable',
                  'reconstructed per-user and per-time-block aggregates','1000 paired user-cluster resamples across dates',
                  'explicit millisecond timestamp decoding','source snapshot and protocol hashes']
    report=dict(status='passed',run_id=manifest['run_id'],mode='summary_arithmetic_only' if summaries_only else 'saved_score_and_summary_audit',
                checked=checked,models_independently_refitted=False,raw_input_rows_independently_reloaded=False,
                all_incumbent_model_predictions_independently_reproduced=False,
                inference_scope='Conditional saved-output arithmetic audit; no population-equivalence, safety or novelty certificate.',
                audit_source_sha256_LF_normalized=hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n',b'\n')).hexdigest())
    if not summaries_only:
        with (path/'saved_output_audit.json').open('x',encoding='utf-8') as handle:json.dump(report,handle,indent=2)
        print('Audit saved:',path/'saved_output_audit.json')
    print('AUDIT PASSED:',report['mode'])
    print('No models refitted. No raw research logs opened.')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_directory',type=Path);parser.add_argument('--summaries-only',action='store_true')
    args=parser.parse_args()
    try:
        audit(args.run_directory,args.summaries_only)
    except Exception as exc:
        if not args.summaries_only and args.run_directory.is_dir():
            path=args.run_directory/('audit_failure_'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8]+'.json')
            path.write_text(json.dumps(dict(status='failed',error=repr(exc),traceback=traceback.format_exc()),indent=2),encoding='utf-8')
            print('Audit failure preserved:',path)
        raise
