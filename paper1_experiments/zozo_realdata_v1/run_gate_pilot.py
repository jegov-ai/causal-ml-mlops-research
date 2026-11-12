"""One-review engineering/development pilot; never a confirmatory validation.

First run --prepare to record settings, then --run. Only the two already
inspected development days are used. Later outcomes are not analysed.
"""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
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

from check_development import SOURCES, sha256

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
NAMES = ['initial_training', 'candidate_training', 'gate_check', 'subsequent_evaluation']
BOUNDS = ['2019-11-24T00:00:00+00:00', '2019-11-25T00:00:00+00:00',
          '2019-11-25T12:00:00+00:00', '2019-11-25T18:00:00+00:00',
          '2019-11-26T00:00:00+00:00']
USER = [f'user_feature_{i}' for i in range(4)]
AFFINITY = [f'user-item_affinity_{i}' for i in range(34)]
SETTINGS = {
    'status': 'exploratory_development_pilot_not_confirmatory',
    'source': 'bts_men', 'position': 1, 'all_34_items_retained': True,
    'interval_bounds_UTC': BOUNDS, 'partition_order': NAMES,
    'model': {'family': 'pooled_logistic_regression', 'solver': 'liblinear',
              'C': 0.1, 'tol': 1e-6, 'max_iter': 500, 'random_state': 42,
              'class_weight': None, 'training_sample_weights': None},
    'features': ['categorical_item_id', 'four_categorical_user_features',
                 'four_categorical_item_features', 'numeric_affinity_for_selected_item'],
    'preprocessing': 'DictVectorizer and MaxAbsScaler fitted on each training partition only',
    'policy': 'deterministic largest predicted click probability; ties use lowest item_id',
    'gate': 'paired DR candidate-minus-initial mean minus 1.96 row standard errors > 0',
    'gate_models': {'frozen': 'initial outcome model', 'refreshed': 'candidate outcome model'},
    'evaluation': 'same candidate-trained outcome model for every policy; report DR and IPS',
    'evaluation_comparators': ['initial', 'candidate', 'uniform', 'frozen_gate', 'refreshed_gate'],
    'exploratory_time_bootstrap': {'block_minutes': 30, 'resamples': 1000, 'seed': 42},
    'weight_clipping': None, 'prediction_batch_rows': 4096,
    'expected_partition_records': [235357, 88983, 65052, 17300],
    'expected_partition_clicks': [1791, 643, 512, 131],
    'limitations': [
        'All two-day development outcome summaries have already been inspected.',
        'This tests one review and gate implementation, not M0/M1/FULL monitoring.',
        'Dates do not establish that a causal effect shift actually occurred.',
        'Row-based gate standard errors ignore dependence and give no sequential safety guarantee.',
        'The 30-minute bootstrap is exploratory, with few time blocks and no guaranteed coverage.',
        'User identity is unavailable; dependence from repeat users cannot be fully accounted for.',
        'Per-position evaluation assumes the other displayed items do not invalidate the reward model.',
        'Logged BTS probabilities are Monte Carlo estimates, not independently reconstructed.',
        'No individual ground truth, oracle regret, causal-monitor superiority, or real profit established.',
    ],
}


def validate_split(plan):
    for i, name in enumerate(NAMES):
        if plan.get(name) != BOUNDS[i:i+2]:
            raise ValueError('Time split differs from the fixed pilot: ' + name)
    if plan.get('position') != 1 or plan.get('source') != 'bts_men':
        raise ValueError('Unexpected source or position')


def load_development(path):
    columns = ['timestamp', 'position', 'item_id', 'click', 'propensity_score'] + USER + AFFINITY
    pieces = []
    for chunk in pd.read_csv(path, usecols=columns, dtype=str, chunksize=25000):
        # Apply the boundary before converting or using any outcome value.
        keep = ((chunk['position'] == '1') &
                chunk['timestamp'].str.slice(0, 10).isin(['2019-11-24', '2019-11-25']))
        part = chunk.loc[keep].copy()
        if part.empty:
            continue
        if part.isna().any().any():
            raise ValueError('Missing development field')
        part['timestamp'] = pd.to_datetime(part['timestamp'], format='ISO8601', utc=True)
        for column in ['item_id', 'click', 'propensity_score'] + AFFINITY:
            part[column] = pd.to_numeric(part[column], errors='raise')
        pieces.append(part)
    if not pieces:
        raise ValueError('No development data')
    data = pd.concat(pieces, ignore_index=True)
    if not data['timestamp'].is_monotonic_increasing:
        raise ValueError('Development records are not chronological')
    if not data['click'].isin([0, 1]).all() or not data['item_id'].isin(range(34)).all():
        raise ValueError('Invalid development action or outcome')
    numeric = data[['propensity_score'] + AFFINITY].to_numpy(dtype=float)
    if not np.isfinite(numeric).all() or not data['propensity_score'].between(0, 1, inclusive='right').all():
        raise ValueError('Invalid development affinity or propensity')
    data['part'] = pd.cut(data['timestamp'], bins=pd.to_datetime(BOUNDS, utc=True),
                          labels=NAMES, right=False)
    if data['part'].isna().any():
        raise ValueError('Development partition boundary failure')
    return [data.loc[data['part'] == name].copy().reset_index(drop=True) for name in NAMES]


def feature_records(frame, metadata, action=None):
    user = frame[USER].to_numpy(dtype=str)
    affinity = frame[AFFINITY].to_numpy(dtype=float)
    actions = frame['item_id'].to_numpy(dtype=int) if action is None else np.full(len(frame), action)
    for i, a in enumerate(actions):
        record = {'item': str(a), 'chosen_affinity': float(affinity[i, a])}
        record.update({name: user[i, j] for j, name in enumerate(USER)})
        record.update(metadata[int(a)])
        yield record


def fit_model(frame, metadata):
    if frame['click'].nunique() != 2:
        raise ValueError('Training needs both outcome classes')
    model = make_pipeline(DictVectorizer(sparse=True), MaxAbsScaler(),
                          LogisticRegression(**{k: v for k, v in SETTINGS['model'].items()
                                               if k not in ('family', 'training_sample_weights')}))
    with warnings.catch_warnings():
        warnings.simplefilter('error', ConvergenceWarning)
        model.fit(list(feature_records(frame, metadata)), frame['click'].to_numpy(dtype=int))
    return model


def predict_all(model, frame, metadata):
    result = np.empty((len(frame), 34), dtype=float)
    batch = SETTINGS['prediction_batch_rows']
    for start in range(0, len(frame), batch):
        stop = min(start + batch, len(frame))
        piece = frame.iloc[start:stop]
        for action in range(34):
            result[start:stop, action] = model.predict_proba(
                list(feature_records(piece, metadata, action)))[:, 1]
    if not np.isfinite(result).all() or np.any((result < 0) | (result > 1)):
        raise ValueError('Invalid click predictions')
    return result


def score_policy(frame, q, actions):
    y = frame['click'].to_numpy(dtype=float)
    logged = frame['item_id'].to_numpy(dtype=int)
    p = frame['propensity_score'].to_numpy(dtype=float)
    index = np.arange(len(frame))
    if actions is None:  # Uniform random over all 34 items.
        probability = np.full(len(frame), 1.0 / 34)
        direct = q.mean(axis=1)
    else:
        probability = (logged == actions).astype(float)
        direct = q[index, actions]
    weights = probability / p
    ips = weights * y
    dr = direct + weights * (y - q[index, logged])
    return dr, ips, weights


def row_summary(scores):
    if len(scores) < 2 or not np.isfinite(scores).all():
        raise ValueError('Insufficient or invalid scores')
    mean = float(np.mean(scores))
    se = float(np.std(scores, ddof=1) / np.sqrt(len(scores)))
    return {'mean': mean, 'row_se': se, 'row_lower_95': mean - 1.96 * se,
            'row_upper_95': mean + 1.96 * se}


def weight_summary(weights, outcomes):
    total = float(weights.sum())
    return {'matched_rows': int(np.count_nonzero(weights)),
            'matched_clicks': int(np.count_nonzero((weights > 0) & (outcomes == 1))),
            'weight_ess': total**2 / float(weights @ weights) if total else 0.0,
            'largest_weight_percent': float(100 * weights.max() / total) if total else None}


def time_bootstrap(scores, times):
    codes, values = pd.factorize(times.dt.floor('30min'), sort=True)
    count = len(values)
    if count < 2:
        return {'blocks': count, 'interval': None}
    totals = np.bincount(codes, weights=scores)
    sizes = np.bincount(codes)
    rng = np.random.default_rng(42)
    samples = rng.integers(0, count, size=(1000, count))
    means = totals[samples].sum(axis=1) / sizes[samples].sum(axis=1)
    return {'blocks': count, 'interval': np.quantile(means, [0.025, 0.975]).tolist(),
            'label': 'exploratory 30-minute block percentile interval'}


def run(settings_path, split_path):
    if json.loads(settings_path.read_text(encoding='utf-8')) != SETTINGS:
        raise ValueError('Settings differ from the fixed pilot implementation')
    validate_split(json.loads(split_path.read_text(encoding='utf-8')))
    raw = ROOT / 'data/zozo_open_bandit/raw'
    inputs = {}
    for source in ('bts', 'items'):
        filename, expected = SOURCES[source]
        print('Verifying ' + filename + '...', flush=True)
        actual = sha256(raw / filename)
        if actual != expected:
            raise ValueError('Input checksum mismatch: ' + filename)
        inputs[filename] = actual
    initial_data, candidate_data, gate, evaluation = load_development(raw / SOURCES['bts'][0])
    partitions = [initial_data, candidate_data, gate, evaluation]
    for i, frame in enumerate(partitions):
        if len(frame) != SETTINGS['expected_partition_records'][i] or int(frame['click'].sum()) != SETTINGS['expected_partition_clicks'][i]:
            raise ValueError('Partition count mismatch: ' + NAMES[i])
    items = pd.read_csv(raw / SOURCES['items'][0], dtype=str)
    if items['item_id'].duplicated().any() or set(items['item_id'].astype(int)) != set(range(34)):
        raise ValueError('Invalid product metadata')
    metadata = {int(row['item_id']): {k: str(row[k]) for k in [f'item_feature_{j}' for j in range(4)]}
                for row in items.to_dict('records')}
    output = ROOT / 'data/zozo_open_bandit/pilot_runs' / (
        datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid.uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    manifest = {'status': 'running', 'settings': SETTINGS, 'input_sha256': inputs,
                'source_sha256': sha256(Path(__file__)), 'audit_source_sha256': sha256(HERE / 'check_development.py'),
                'settings_sha256': sha256(settings_path), 'split_sha256': sha256(split_path),
                'versions': {'python': platform.python_version(), 'numpy': np.__version__,
                             'pandas': pd.__version__, 'sklearn': sklearn.__version__},
                'later_outcomes_analysed': False}
    manifest_path = output / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print('Output directory: ' + str(output), flush=True)
    try:
        print('Training initial model on 24 November...', flush=True)
        initial = fit_model(initial_data, metadata)
        print('Training candidate on 25 November before noon...', flush=True)
        candidate = fit_model(candidate_data, metadata)
        print('Predicting gate recommendations for all 34 products...', flush=True)
        q_old = predict_all(initial, gate, metadata)
        q_new = predict_all(candidate, gate, metadata)
        old_actions, new_actions = q_old.argmax(axis=1), q_new.argmax(axis=1)
        gates = []
        score_arrays = {}
        for name, q in [('frozen', q_old), ('refreshed', q_new)]:
            a = score_policy(gate, q, new_actions)[0]
            b = score_policy(gate, q, old_actions)[0]
            delta = a - b
            summary = row_summary(delta)
            accepted = bool(summary['row_lower_95'] > 0)
            gates.append({'gate': name, **summary, 'candidate_accepted': accepted})
            score_arrays['gate_' + name + '_delta'] = delta
            print(f'{name}: estimated gain={summary["mean"]:.6f}; accepted={accepted}', flush=True)
        print('Predicting subsequent-period recommendations...', flush=True)
        q_eval_old = predict_all(initial, evaluation, metadata)
        q_eval_new = predict_all(candidate, evaluation, metadata)
        initial_actions = q_eval_old.argmax(axis=1)
        candidate_actions = q_eval_new.argmax(axis=1)
        policies = {'initial': initial_actions, 'candidate': candidate_actions, 'uniform': None,
                    'frozen_gate': candidate_actions if gates[0]['candidate_accepted'] else initial_actions,
                    'refreshed_gate': candidate_actions if gates[1]['candidate_accepted'] else initial_actions}
        values = []
        for name, actions in policies.items():
            dr, ips, weights = score_policy(evaluation, q_eval_new, actions)
            values.append({'policy': name, 'dr_mean': float(dr.mean()), 'ips_mean': float(ips.mean()),
                           **weight_summary(weights, evaluation['click'].to_numpy())})
            score_arrays['evaluation_' + name + '_dr'] = dr
            score_arrays['evaluation_' + name + '_ips'] = ips
        contrasts = {}
        for estimator in ('dr', 'ips'):
            delta = (score_arrays['evaluation_refreshed_gate_' + estimator]
                     - score_arrays['evaluation_frozen_gate_' + estimator])
            contrasts[estimator] = {**row_summary(delta),
                                    'time_bootstrap': time_bootstrap(delta, evaluation['timestamp'])}
        pd.DataFrame(gates).to_csv(output / 'gate_comparison.csv', index=False)
        pd.DataFrame(values).to_csv(output / 'evaluation.csv', index=False)
        (output / 'paired_contrasts.json').write_text(json.dumps(contrasts, indent=2), encoding='utf-8')
        score_arrays.update({'gate_logged_actions': gate['item_id'].to_numpy(),
                             'gate_initial_actions': old_actions, 'gate_candidate_actions': new_actions,
                             'evaluation_initial_actions': initial_actions,
                             'evaluation_candidate_actions': candidate_actions})
        np.savez_compressed(output / 'score_arrays.npz', **score_arrays)
        manifest.update(status='complete', gate_results=gates, paired_contrasts=contrasts,
                        evaluation_disagreement_rows=int(np.count_nonzero(initial_actions != candidate_actions)))
        print(pd.DataFrame(values).to_string(index=False))
        print('DEVELOPMENT PILOT COMPLETE. Results: ' + str(output))
        print('This is not proof of gate safety or monitoring superiority. Later five days remain reserved.')
    except Exception as error:
        manifest.update(status='failed', error=repr(error))
        raise
    finally:
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--prepare', action='store_true')
    modes.add_argument('--run', action='store_true')
    args = parser.parse_args()
    settings = HERE / 'pilot_settings.json'
    split = HERE / 'pilot_time_split.json'
    validate_split(json.loads(split.read_text(encoding='utf-8')))
    if args.prepare:
        with settings.open('x', encoding='utf-8') as stream:
            json.dump(SETTINGS, stream, indent=2)
            stream.write('\n')
        print('Pilot settings recorded: ' + str(settings))
        print('No models trained. Review and preserve settings before running --run.')
    else:
        run(settings, split)


if __name__ == '__main__':
    main()
