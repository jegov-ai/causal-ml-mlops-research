"""Development-only KuaiRand group-policy pilot. Never reads reserved outcomes.

Run --self-test and --prepare; commit source/settings before --run.
This evaluates duration-group selection with uniform sampling within each group,
not individual-video ranking or a real deployment. No 14-date study is run here.
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
import traceback
import uuid
import warnings

import numpy as np
import pandas as pd
import sklearn
from sklearn.exceptions import ConvergenceWarning
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import MaxAbsScaler

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GROUPS = ['short', 'long', 'unknown']
POOL = np.array([1743, 5601, 239])
PROB = POOL / 7583
MD5 = '0820331067a3784d9691136f772b35a7'
LOG = 'KuaiRand-Pure/data/log_random_4_22_to_5_08_pure.csv'
ITEMS = 'KuaiRand-Pure/data/video_features_basic_pure.csv'
LIMIT = pd.Timestamp('2022-04-25T00:00:00+08:00')
SETTINGS = {
    'status': 'exposed_three_date_development_pilot_not_independent_validation',
    'dataset': 'KuaiRand-Pure', 'provider': 'https://zenodo.org/records/10439422',
    'citation': 'Gao et al. (2022), KuaiRand, CIKM, doi:10.1145/3511808.3557624',
    'licence': 'CC BY-SA 4.0; archive LICENSE retained with raw input',
    'archive_md5': MD5, 'source': 'random_interventions_only', 'tab': 1,
    'groups_in_order': GROUPS, 'catalogue_counts': POOL.tolist(),
    'short_definition': 'finite catalogue video_duration > 0 and <= 30000 milliseconds',
    'long_definition': 'finite catalogue video_duration > 30000 milliseconds',
    'unknown_definition': 'missing, nonnumeric, nonfinite or nonpositive catalogue duration',
    'group_logging_probabilities': PROB.tolist(),
    'target_policy': 'choose one duration group; sample a video uniformly within its fixed catalogue group',
    'unknown_items_retained': True,
    'clock': 'time_ms explicitly decoded as Unix milliseconds; calendar UTC+08:00',
    'source_date_field_not_used_for_splits': True,
    'timestamp_mismatch_cause': 'not established; raw date field and mismatch flag retained',
    'outcome': 'long_view (binary)',
    'development_aggregate_outcomes_already_inspected': True,
    'reserved_outcomes_not_analysed': True,
    'intervals': {
        'initial_training': ['2022-04-22T00:00:00+08:00', '2022-04-24T00:00:00+08:00'],
        'candidate_training': ['2022-04-23T12:00:00+08:00', '2022-04-24T12:00:00+08:00'],
        'gate_check': ['2022-04-24T12:00:00+08:00', '2022-04-24T18:00:00+08:00'],
        'subsequent_evaluation': ['2022-04-24T18:00:00+08:00', '2022-04-25T00:00:00+08:00'],
    },
    'candidate_uses_rolling_24_hours': True,
    'training_partitions_overlap_each_other_but_not_gate_or_evaluation': True,
    'difference_from_ZOZO': 'duration-group policies and rolling-24h candidate training; not identical item-ranking replication',
    'features': ['categorical user_id', 'categorical duration group', 'user_id by group',
                 'six-hour clock bin by group', 'day-of-week by group'],
    'excluded_features': ['all released aggregate user/video statistics', 'current/future feedback',
                          'source date field', 'normal recommendation logs'],
    'model': {'solver': 'liblinear', 'C': 0.1, 'tol': 1e-6, 'max_iter': 500,
              'random_state': 42, 'class_weight': None},
    'preprocessing': 'training-only sparse DictVectorizer and MaxAbsScaler',
    'gate_rule': 'paired DR gain minus 1.96 row SE strictly positive; zero-match check on either compared policy',
    'frozen_gate_q': 'initial model', 'refreshed_gate_q': 'candidate model',
    'separate_gate_selection': True, 'evaluation_common_q': 'candidate model for every policy',
    'weight_clipping': None, 'tie_break': 'first in short,long,unknown order',
    'estimators': ['DR', 'IPS'], 'inference': 'descriptive development results only; no inferential claims',
    'limitations': ['Published cohort selected to have at least ten random exposures; no unrestricted population claim.',
                    'Conditional random-insertion group probabilities, not propensities for ordinary recommendations.',
                    'Repeated-user dependence is not represented by row standard errors.',
                    'Policies are evaluated on logged contexts; no policy-induced feedback or whole-feed intervention identified.',
                    'One development review cannot establish superiority or sequential safety.',
                    'Long-view is an engagement metric, not measured profit or individual causal truth.'],
}


def digest(path, algorithm='sha256'):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, algorithm).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')


def classify(values):
    x = pd.to_numeric(values, errors='coerce').to_numpy(dtype=float, na_value=np.nan)
    return np.where(np.isfinite(x) & (x > 0), np.where(x <= 30000, 0, 1), 2)


def load_development(archive):
    with tarfile.open(archive, 'r:gz') as tar:
        with tar.extractfile(ITEMS) as stream:
            items = pd.read_csv(stream, usecols=['video_id', 'video_duration'], dtype=str)
        if items.video_id.duplicated().any() or items.video_id.isna().any():
            raise ValueError('Invalid catalogue IDs')
        items['group'] = classify(items.video_duration)
        if len(items) != 7583 or not np.array_equal(np.bincount(items.group, minlength=3), POOL):
            raise ValueError('Catalogue differs from fixed structural checkpoint')
        catalogue = dict(zip(items.video_id, items.group))
        parts = []
        with tar.extractfile(LOG) as stream:
            for chunk in pd.read_csv(stream, usecols=['time_ms','date','tab','video_id','user_id','is_rand','long_view'], dtype=str, chunksize=50000):
                # Timestamp parsing uses structure only; outcome conversion occurs AFTER cutoff.
                ms = pd.to_numeric(chunk.time_ms, errors='raise')
                clock = pd.to_datetime(ms, unit='ms', utc=True, errors='raise')
                keep = (chunk.tab == '1') & (clock >= pd.Timestamp(SETTINGS['intervals']['initial_training'][0])) & (clock < LIMIT)
                d = chunk.loc[keep].copy()
                if d.empty:
                    continue
                if d.isna().any().any() or not d.is_rand.eq('1').all():
                    raise ValueError('Invalid selected development fields or random flag')
                d['timestamp'] = clock.loc[keep].dt.tz_convert(timezone(timedelta(hours=8)))
                d['time_ms'] = ms.loc[keep].to_numpy(dtype=np.int64)
                d['csv_row_index'] = d.index.to_numpy()
                d['group'] = d.video_id.map(catalogue)
                if d.group.isna().any():
                    raise ValueError('Development action absent from catalogue')
                d['group'] = d.group.astype(int)
                d['long_view'] = pd.to_numeric(d.long_view, errors='raise')
                if not d.long_view.isin([0,1]).all():
                    raise ValueError('Invalid development outcome')
                d['date_mismatch'] = d.timestamp.dt.strftime('%Y%m%d').ne(d.date)
                parts.append(d)
    if not parts:
        raise ValueError('No development observations')
    data = pd.concat(parts, ignore_index=True).sort_values(['time_ms','csv_row_index'], kind='stable').reset_index(drop=True)
    if len(data) != 120645 or int(data.long_view.sum()) != 10128:
        raise ValueError('Development counts disagree with previously inspected summaries')
    data['day'] = data.timestamp.dt.strftime('%Y-%m-%d')
    observed = data.groupby(['day','group']).long_view.agg(records='count', long_views='sum')
    expected = pd.read_csv(HERE/'development_outcomes.csv')
    for row in expected.to_dict('records'):
        key = (row['timestamp_day_UTC_plus_08'], GROUPS.index(row['duration_group']))
        if tuple(observed.loc[key]) != (row['records'], row['long_views']):
            raise ValueError('Development table reconciliation failed: '+str(key))
    return data


def features(frame, group=None):
    users = frame.user_id.astype(str).to_numpy()
    actions = frame.group.to_numpy(int) if group is None else np.full(len(frame),group)
    hours = frame.timestamp.dt.hour.to_numpy()//6
    weekdays = frame.timestamp.dt.day_of_week.to_numpy()
    for user, action, hour, weekday in zip(users,actions,hours,weekdays):
        yield {'user':user, 'group':str(action), 'user_group':user+'|'+str(action),
               'hour_group':str(hour)+'|'+str(action), 'weekday_group':str(weekday)+'|'+str(action)}


def fit(frame):
    if frame.long_view.nunique()!=2:
        raise ValueError('Both outcome classes required')
    model = make_pipeline(DictVectorizer(sparse=True), MaxAbsScaler(), LogisticRegression(**SETTINGS['model']))
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        model.fit(list(features(frame)),frame.long_view.to_numpy(int))
    return model


def predict(model, frame):
    q=np.empty((len(frame),3))
    for start in range(0,len(frame),4096):
        part=frame.iloc[start:start+4096]
        for group in range(3):
            q[start:start+len(part),group]=model.predict_proba(list(features(part,group)))[:,1]
    if not np.isfinite(q).all() or ((q<0)|(q>1)).any():
        raise ValueError('Invalid predictions')
    return q


def scores(frame,q,actions):
    logged=frame.group.to_numpy(int);y=frame.long_view.to_numpy(float)
    if actions is None: # Uniform across all 7583 videos, not uniform across groups.
        w=np.ones(len(frame));direct=q@PROB
    else:
        w=(logged==actions)/PROB[logged]
        direct=q[np.arange(len(frame)),actions]
    ips=w*y
    dr=direct+w*(y-q[np.arange(len(frame)),logged])
    return dr,ips,w


def summary(x):
    if len(x)<2 or not np.isfinite(x).all():
        raise ValueError('Invalid score sample')
    mean=float(np.mean(x));se=float(np.std(x,ddof=1)/np.sqrt(len(x)))
    return dict(mean=mean,row_se=se,row_lower_95=mean-1.96*se,row_upper_95=mean+1.96*se)


def support(w,y,users):
    positive=w>0;total=w.sum()
    return dict(matched_rows=int(positive.sum()),matched_long_views=int(((y==1)&positive).sum()),
                matched_users=int(pd.Series(users[positive]).nunique()),
                weight_ess=float(total**2/(w@w)) if total else 0.,
                largest_weight_percent=float(100*w.max()/total) if total else None)


def decision(frame,q,ca,ia):
    cs=scores(frame,q,ca);ins=scores(frame,q,ia)
    row=summary(cs[0]-ins[0]);zero=not np.any(cs[2]>0) or not np.any(ins[2]>0)
    row.update(candidate_accepted=bool(not zero and row['row_lower_95']>0),zero_match_rejection=zero)
    return row,cs,ins


def committed():
    git=shutil.which('git')
    if not git:
        raise ValueError('Git unavailable')
    def call(*args):
        return subprocess.check_output([git,'-C',str(ROOT),*args],text=True).strip()
    paths=[str((HERE/n).relative_to(ROOT).as_posix()) for n in [Path(__file__).name,'pilot_settings.json','development_outcomes.csv','feasibility_checkpoint.json']]
    call('ls-files','--error-unmatch','--',*paths)
    if call('diff','HEAD','--',*paths):
        raise ValueError('Commit source/settings/development files before --run')
    if json.loads((HERE/'pilot_settings.json').read_text())!=SETTINGS:
        raise ValueError('Pilot settings changed')
    return call('rev-parse','HEAD')


def run():
    commit=committed()
    archive=ROOT/'data/kuairand/raw/KuaiRand-Pure.tar.gz'
    print('Verifying archive...',flush=True)
    if digest(archive,'md5')!=MD5:
        raise ValueError('Archive MD5 mismatch')
    checkpoint=json.loads((HERE/'feasibility_checkpoint.json').read_text())
    sha=digest(archive)
    if sha!=checkpoint['archive_sha256']:
        raise ValueError('Archive SHA-256 mismatch')
    out=ROOT/'data/kuairand/pilot_runs'/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+uuid.uuid4().hex[:8])
    out.mkdir(parents=True,exist_ok=False)
    manifest=dict(status='running',git_commit=commit,archive_sha256=sha,settings=SETTINGS,
                  versions=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__),
                  reserved_outcomes_analysed=False,timestamp_array_unit='ms',windows={})
    snapshots=out/'source_snapshot';snapshots.mkdir()
    names=[Path(__file__).name,'pilot_settings.json','development_outcomes.csv','feasibility_checkpoint.json']
    manifest['source_sha256']={n:digest(HERE/n) for n in names}
    for name in names:
        shutil.copy2(HERE/name,snapshots/name)
    save(out/'manifest.json',manifest)
    print('Output:',out,flush=True)
    try:
        data=load_development(archive)
        windows={}
        for name,(lo,hi) in SETTINGS['intervals'].items():
            windows[name]=data.loc[(data.timestamp>=pd.Timestamp(lo))&(data.timestamp<pd.Timestamp(hi))].reset_index(drop=True)
            frame=windows[name]
            if len(frame)<2:
                raise ValueError('Empty pilot window: '+name)
            manifest['windows'][name]=dict(records=len(frame),long_views=int(frame.long_view.sum()),users=int(frame.user_id.nunique()),date_mismatches=int(frame.date_mismatch.sum()),first_timestamp=str(frame.timestamp.iloc[0]),last_timestamp=str(frame.timestamp.iloc[-1]))
        print('Training initial model...',flush=True);initial=fit(windows['initial_training'])
        print('Training rolling-24h candidate...',flush=True);candidate=fit(windows['candidate_training'])
        gate=windows['gate_check'];qi=predict(initial,gate);qc=predict(candidate,gate)
        ia=qi.argmax(1);ca=qc.argmax(1);gate_rows=[];selected={}
        arrays=dict(timestamp_ms=gate.time_ms.to_numpy(),csv_row_index=gate.csv_row_index.to_numpy(),group=gate.group.to_numpy(),long_view=gate.long_view.to_numpy(),user_id=gate.user_id.astype(str).to_numpy(),date_mismatch=gate.date_mismatch.to_numpy(),frozen_q=qi,refreshed_q=qc,initial_actions=ia,candidate_actions=ca)
        for name,q in [('frozen',qi),('refreshed',qc)]:
            row,cs,ins=decision(gate,q,ca,ia)
            selected[name]=candidate if row['candidate_accepted'] else initial
            gate_rows.append(dict(gate=name,**row))
            arrays.update({name+'_candidate_dr':cs[0],name+'_incumbent_dr':ins[0]})
            print(f"{name}: gain={row['mean']:.6f}; accepted={row['candidate_accepted']}",flush=True)
        pd.DataFrame(gate_rows).to_csv(out/'gate_comparison.csv',index=False)
        np.savez_compressed(out/'gate_scores.npz',**arrays)
        frame=windows['subsequent_evaluation'];qi=predict(initial,frame);qc=predict(candidate,frame)
        actions=dict(initial=qi.argmax(1),candidate=qc.argmax(1),uniform_catalogue=None,
                     always_short=np.zeros(len(frame),int),always_long=np.ones(len(frame),int),always_unknown=np.full(len(frame),2,int))
        actions['frozen_gate']=actions['candidate'] if selected['frozen'] is candidate else actions['initial']
        actions['refreshed_gate']=actions['candidate'] if selected['refreshed'] is candidate else actions['initial']
        rows=[];results={}
        arrays=dict(timestamp_ms=frame.time_ms.to_numpy(),csv_row_index=frame.csv_row_index.to_numpy(),user_id=frame.user_id.astype(str).to_numpy(),group=frame.group.to_numpy(),long_view=frame.long_view.to_numpy(),common_q=qc,date_mismatch=frame.date_mismatch.to_numpy())
        for name,action in actions.items():
            dr,ips,w=scores(frame,qc,action);results[name]=(dr,ips)
            row=dict(policy=name,records=len(frame),users=int(frame.user_id.nunique()),dr_mean=float(dr.mean()),ips_mean=float(ips.mean()),**support(w,frame.long_view.to_numpy(),frame.user_id.to_numpy()))
            rows.append(row)
            arrays.update({name+'_dr':dr,name+'_ips':ips,name+'_weights':w})
            if action is not None:
                arrays[name+'_actions']=action
        pd.DataFrame(rows).to_csv(out/'evaluation.csv',index=False)
        np.savez_compressed(out/'evaluation_scores.npz',**arrays)
        paired={e:summary(results['refreshed_gate'][i]-results['frozen_gate'][i]) for i,e in enumerate(['dr','ips'])}
        save(out/'paired_contrasts.json',paired)
        manifest['status']='complete';save(out/'manifest.json',manifest)
        print(pd.DataFrame(rows).to_string(index=False),flush=True)
        print('DEVELOPMENT PILOT COMPLETE:',out,flush=True)
        print('Reserved dates not analysed. Group selection is not individual-video ranking or a safety guarantee.')
    except BaseException as exc:
        manifest.update(status='failed',error=repr(exc),traceback=traceback.format_exc());save(out/'manifest.json',manifest)
        print('Failure preserved:',out,flush=True)
        raise


def self_test():
    assert classify(pd.Series(['1000','30000','30001','0','-1',None,'inf','bad'])).tolist()==[0,0,1,2,2,2,2,2]
    frame=pd.DataFrame({'group':[0,1,2,0], 'long_view':[1,0,1,0], 'user_id':['u','v','u','w']})
    q=np.tile([.1,.2,.3],(4,1));a=np.zeros(4,int)
    dr,ips,w=scores(frame,q,a)
    close=lambda x,y:np.testing.assert_allclose(x,y,rtol=1e-12,atol=1e-12)
    close(w,[1/PROB[0],0,0,1/PROB[0]])
    close(dr,[.1+.9/PROB[0],.1,.1,.1-.1/PROB[0]])
    close(ips,[1/PROB[0],0,0,0])
    close(scores(frame,q,None)[2],np.ones(4))
    assert not decision(frame,q,a,a)[0]['candidate_accepted']
    absent=frame.loc[frame.group.ne(2)].copy()
    assert decision(absent,q[:3],np.full(3,2),np.zeros(3,int))[0]['zero_match_rejection']
    times=pd.to_datetime(pd.Series([1650787200000,1650787200001]),unit='ms',utc=True)
    close(times.dt.as_unit('ms').astype('int64'),[1650787200000,1650787200001])
    toy=pd.DataFrame({'user_id':['u','v','u','w']*4,'group':[0,1,2,0]*4,'long_view':[1,0,1,0]*4,
                      'timestamp':pd.date_range('2022-04-23',periods=16,freq='h',tz=timezone(timedelta(hours=8)))})
    model=fit(toy);pred=predict(model,toy);assert pred.shape==(16,3)
    # Check that unseen users and clock categories are handled by training-only preprocessing.
    toy.loc[:,'user_id']='new-user';assert np.isfinite(predict(model,toy)).all()
    print('SELF-TEST PASSED: group definitions, known probabilities, DR/IPS, gate rejection, timestamps and model predictions.')
    print('No real archive opened. Reserved outcomes untouched.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--self-test',action='store_true');group.add_argument('--prepare',action='store_true');group.add_argument('--run',action='store_true')
    args=parser.parse_args()
    if args.self_test:
        self_test()
    elif args.prepare:
        self_test()
        path=HERE/'pilot_settings.json'
        with path.open('x',encoding='utf-8') as handle:
            json.dump(SETTINGS,handle,indent=2,allow_nan=False)
        print('Pilot settings recorded:',path)
        print('No data opened. Commit settings and source before --run.')
    else:
        run()


if __name__=='__main__':
    main()
