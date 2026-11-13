"""Independent saved-output arithmetic audit; no model refits or raw-data reload.

--summaries-only audits committed tables and bootstrap blocks.
Without that flag, also reconstruct every saved gate/evaluation score from NPZ.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

DATES = [f'2019-11-{i}' for i in range(26, 31)]
POLICIES = ['frozen_gate_path', 'refreshed_gate_path', 'initial_no_update',
            'always_update_current_candidate', 'uniform_over_34_products']
PAIRS = [(POLICIES[1], POLICIES[0])] + [(g, b) for g in POLICIES[:2] for b in POLICIES[2:]]
LABELS = [a + '_minus_' + b + '__' + e for a, b in PAIRS for e in ['dr', 'ips']]


def close(actual, expected):
    np.testing.assert_allclose(actual, expected, rtol=1e-9, atol=1e-12, equal_nan=False)


def stats(x):
    mean = float(np.mean(x))
    se = float(np.std(x, ddof=1) / np.sqrt(len(x)))
    return dict(mean=mean, row_se=se, row_lower_95=mean-1.96*se, row_upper_95=mean+1.96*se)


def boolean(x):
    assert str(x).lower() in ['true', 'false'], 'Invalid boolean'
    return str(x).lower() == 'true'


def scores(z, q, actions):
    n = len(z['click'])
    assert q.shape == (n, 34) and np.isfinite(q).all() and ((q >= 0) & (q <= 1)).all()
    y, a, p = z['click'], z['logged_item'], z['propensity']
    assert np.isin(a, np.arange(34)).all() and np.isin(y, [0, 1]).all()
    assert np.isfinite(p).all() and ((p > 0) & (p <= 1)).all()
    if actions is None:
        w = 1 / (34 * p)
        direct = q.mean(axis=1)
    else:
        assert len(actions) == n and np.isin(actions, np.arange(34)).all()
        w = (actions == a) / p
        direct = q[np.arange(n), actions]
    return direct + w*(y-q[np.arange(n), a]), w*y, w


def support(w, y):
    total = w.sum()
    return dict(matched_rows=int((w > 0).sum()), matched_clicks=int(((w > 0) & (y == 1)).sum()),
                weight_ess=float(total**2/(w@w)) if total else 0.,
                largest_weight_percent=float(100*w.max()/total) if total else None)


def check_stats(row, x, prefix=''):
    for k, v in stats(x).items():
        close(float(row[prefix+k]), v)


def check_support(row, w, y, prefix=''):
    for k, v in support(w, y).items():
        if v is None:
            assert pd.isna(row[prefix+k])
        else:
            close(float(row[prefix+k]), v)


def audit(path, summaries_only=False, timestamp_unit="ns"):
    assert timestamp_unit in ["ns", "us"], "Unsupported timestamp unit"
    read = lambda name: json.loads((path/name).read_text(encoding='utf-8'))
    m, blocks, aggregate = read('manifest.json'), read('bootstrap_blocks.json'), read('aggregate_contrasts.json')
    gates = pd.read_csv(path/'gate_comparison.csv')
    evaluation = pd.read_csv(path/'evaluation.csv')
    contrasts = pd.read_csv(path/'daily_paired_contrasts.csv')
    assert m['status'] == 'complete' and m['stage'] == 'complete'
    assert len(gates) == 10 and len(evaluation) == 50 and len(contrasts) == 140
    assert not gates.duplicated(['date','gate']).any()
    assert not evaluation.duplicated(['date','source','policy']).any()
    assert not contrasts.duplicated(['date','source','contrast']).any()
    assert set(gates['date']) == set(DATES) and set(gates['gate']) == {'frozen','refreshed'}
    assert blocks['labels'] == LABELS and set(blocks['sources']) == {'bts','random'}
    assert len(m['windows']) == 21
    paths = dict(frozen='initial', refreshed='initial')
    for date in DATES:
        for gate in paths:
            row = gates.loc[(gates['date']==date) & (gates['gate']==gate)].iloc[0]
            assert row['incumbent_before'] == paths[gate]
            close(row['row_lower_95'], row['mean'] - 1.96*row['row_se'])
            close(row['row_upper_95'], row['mean'] + 1.96*row['row_se'])
            zero = row['candidate_matched_rows'] == 0 or row['incumbent_matched_rows'] == 0
            accepted = not zero and row['row_lower_95'] > 0
            assert boolean(row['zero_match_rejection']) == zero
            assert boolean(row['candidate_accepted']) == accepted
            assert row['reason'] == ('zero_matching_rows' if zero else 'positive_lower_bound' if accepted else 'lower_bound_not_positive')
            assert row['candidate_model'] == date+'_candidate'
            if accepted:
                paths[gate] = row['candidate_model']
            assert row['selected_model'] == paths[gate]
        if not summaries_only:
            with np.load(path/(date+'_gate_scores.npz'), allow_pickle=False) as z:
                times = pd.to_datetime(z['timestamp_ns'], unit=timestamp_unit, utc=True)
                assert ((times >= pd.Timestamp(date+'T12:00Z')) & (times < pd.Timestamp(date+'T18:00Z'))).all()
                for gate in paths:
                    row = gates.loc[(gates['date']==date) & (gates['gate']==gate)].iloc[0]
                    q = z[gate+'_q']
                    parts = {}
                    for policy in ['candidate','incumbent']:
                        actions = z[gate+'_'+policy+'_actions']
                        dr, ips, w = scores(z, q, actions)
                        close(z[gate+'_'+policy+'_dr'], dr)
                        close(z[gate+'_'+policy+'_weights'], w)
                        check_support(row, w, z['click'], policy+'_')
                        parts[policy] = dr
                    check_stats(row, parts['candidate']-parts['incumbent'])
                assert np.array_equal(z['frozen_candidate_actions'], z['refreshed_candidate_actions'])
                assert np.array_equal(z['frozen_candidate_actions'], z['refreshed_q'].argmax(axis=1))
    assert m['final_selected_models'] == paths
    for window in m['windows']:
        date, part = window['date'], window['part']
        if part == 'initial_training':
            assert (window['records'],window['clicks']) == (406692,3077)
            start, end = pd.Timestamp('2019-11-24T00:00Z'), pd.Timestamp('2019-11-26T00:00Z')
        else:
            assert date in DATES
            hours = {'candidate_training':(0,12), 'gate_check':(12,18), 'subsequent_evaluation':(18,24)}
            lo, hi = hours[part]
            start = pd.Timestamp(date, tz='UTC')+pd.Timedelta(hours=lo)
            end = pd.Timestamp(date, tz='UTC')+pd.Timedelta(hours=hi)
        assert start <= pd.Timestamp(window['first_timestamp']) <= pd.Timestamp(window['last_timestamp']) < end
    for source in ['bts','random']:
        daily = blocks['sources'][source]
        assert len(daily) == 5
        rng = np.random.default_rng(42)
        boot = np.zeros((len(LABELS),1000))
        means = []
        for i,date in enumerate(DATES):
            counts = np.asarray(daily[i]['counts'],float)
            sums = np.asarray(daily[i]['sums'],float)
            assert np.isfinite(sums).all() and (counts > 0).all() and len(counts) >= 2
            times = pd.to_datetime(daily[i]['blocks'],utc=True)
            assert len(times) == len(counts) and times.is_monotonic_increasing and not times.duplicated().any()
            assert ((times >= pd.Timestamp(date+'T18:00Z')) & (times < pd.Timestamp(date,tz='UTC')+pd.Timedelta(days=1))).all()
            means.append(sums.sum(axis=1)/counts.sum())
            draws = rng.integers(0,len(counts),size=(1000,len(counts)))
            boot += (sums[:,draws].sum(axis=2)/counts[draws].sum(axis=1))/5
            erows = evaluation.loc[(evaluation['date']==date)&(evaluation['source']==source)].set_index('policy')
            crows = contrasts.loc[(contrasts['date']==date)&(contrasts['source']==source)].set_index('contrast')
            assert set(erows.index)==set(POLICIES) and set(crows.index)==set(LABELS)
            assert (erows['records'] == counts.sum()).all()
            window = [w for w in m['windows'] if w['date']==date and w['source']==source and w['part']=='subsequent_evaluation']
            assert len(window)==1 and window[0]['records']==counts.sum()
            assert (erows['logged_clicks']==window[0]['clicks']).all()
            for j,(left,right) in enumerate(PAIRS):
                for k, estimator in enumerate(['dr','ips']):
                    label = LABELS[j*2+k]
                    expected = erows.loc[left,estimator+'_mean']-erows.loc[right,estimator+'_mean']
                    close(crows.loc[label,'mean'], expected)
                    close(crows.loc[label,'mean'], means[-1][j*2+k])
            if not summaries_only:
                with np.load(path/(date+'_'+source+'_evaluation_scores.npz'),allow_pickle=False) as z:
                    assert len(z['click']) == counts.sum()
                    assert z['click'].sum() == window[0]['clicks']
                    t = pd.Series(pd.to_datetime(z['timestamp_ns'],unit=timestamp_unit,utc=True))
                    assert t.is_monotonic_increasing and ((t>=pd.Timestamp(date+'T18:00Z')) & (t<pd.Timestamp(date,tz='UTC')+pd.Timedelta(days=1))).all()
                    assert len(np.unique(z['csv_row_index'])) == len(t)
                    recomputed = {}
                    for policy in POLICIES:
                        actions = None if policy==POLICIES[-1] else z[policy+'_actions']
                        dr, ips, w = scores(z,z['common_q'],actions)
                        row=erows.loc[policy]
                        check_support(row,w,z['click'])
                        close(w,z[policy+'_weights'])
                        for estimator,values in [('dr',dr),('ips',ips)]:
                            close(values,z[policy+'_'+estimator])
                            check_stats(row,values,estimator+'_')
                            recomputed[policy,estimator]=values
                    close(z['always_update_current_candidate_actions'],z['common_q'].argmax(axis=1))
                    codes,bins=pd.factorize(t.dt.floor('30min'),sort=True)
                    close(np.bincount(codes),counts)
                    assert [str(x) for x in bins]==daily[i]['blocks']
                    for j,(left,right) in enumerate(PAIRS):
                        for k,e in enumerate(['dr','ips']):
                            values=recomputed[left,e]-recomputed[right,e]
                            check_stats(crows.loc[LABELS[j*2+k]],values)
                            close(np.bincount(codes,weights=values),sums[j*2+k])
        for j,label in enumerate(LABELS):
            item=aggregate['sources'][source][label]
            close(item['mean'],np.mean(means,axis=0)[j])
            close(item['exploratory_interval'],np.quantile(boot[j],[.025,.975]))
            assert item['primary'] == (source=='bts' and j==0)
    if not summaries_only:
        for name,expected in m['source_sha256_LF_normalized'].items():
            data=(path/'source_snapshot'/name).read_bytes().replace(b'\r\n',b'\n')
            assert hashlib.sha256(data).hexdigest()==expected
    report={'status':'passed','run_id':m['run_id'],'mode':'summary_arithmetic_only' if summaries_only else 'saved_score_and_summary_audit',
            'saved_timestamp_field':'timestamp_ns', 'saved_timestamp_actual_unit':timestamp_unit,
            'timestamp_field_mislabelled':timestamp_unit != 'ns',
            'timestamp_unit_source':'explicit audit argument; checked against registered windows and saved blocks',
            'models_independently_refitted':False,'raw_input_rows_independently_reloaded':False,
            'checked':['all five dates and separate logging sources','gate rules and incumbent carry-forward',
                       'window boundaries and counts','paired contrasts and equal-date averages','1000 paired block resamples'],
            'source_file_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    if not summaries_only:
        report['checked'] += ['all saved gate and evaluation score arrays','weight support diagnostics','source snapshot hashes']
        destination=path/'saved_output_audit.json'
        with destination.open('x',encoding='utf-8') as handle:
            json.dump(report,handle,indent=2)
        print('Audit saved:',destination)
    print('AUDIT PASSED:',report['mode'])
    print('No models refitted. No raw research data opened.')
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run_directory',type=Path)
    parser.add_argument('--summaries-only',action='store_true')
    parser.add_argument('--timestamp-unit',choices=['ns','us'],default='ns',
                        help='Explicit saved integer unit. The pandas 3.1 run stored microseconds in timestamp_ns.')
    args=parser.parse_args()
    audit(args.run_directory,args.summaries_only,args.timestamp_unit)
