"""Fixed ZOZO five-day exploratory gate study. No reserved data in --self-test.

Use --self-test, commit this source, then --preflight and --run.
A repeated execution requires --run --reproduce and is labelled reproduction.
Protocol and unchanged pilot helpers are checked before reading outcome data.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import traceback
import uuid

import numpy as np
import pandas as pd
import sklearn
from run_gate_pilot import (AFFINITY, USER, ROOT, HERE, SETTINGS, fit_model,
                            predict_all, score_policy, row_summary, weight_summary)
from check_development import sha256

PROTOCOL = 'five_day_protocol_v1.json'
LOCKS = {
    PROTOCOL: '6aef95eff7ef3eeb78a244269b343fba04b9434f5b294aa113ee6a70493d149b',
    'run_gate_pilot.py': '664cc9c90e7fa90a86164bf74657142efb064d73ed6f24e02a6c92e75724b3f5',
    'check_development.py': 'ed92dc915a0a8a7719345f154725a414548efce4146786822eea965730ac8f85',
}
DATES = [f'2019-11-{d}' for d in range(26, 31)]
POLICIES = ['frozen_gate_path', 'refreshed_gate_path', 'initial_no_update',
            'always_update_current_candidate', 'uniform_over_34_products']
PAIRS = [('refreshed_gate_path', 'frozen_gate_path')] + [
    (gate, baseline) for gate in POLICIES[:2] for baseline in POLICIES[2:]]
COLUMNS = ['timestamp', 'position', 'item_id', 'click', 'propensity_score'] + USER + AFFINITY


def text_hash(path):
    return hashlib.sha256(Path(path).read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def write_json(path, value):
    # Atomic replacement of this run's own manifest; never reuse a run directory.
    path = Path(path)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False), encoding='utf-8')
    temporary.replace(path)


def source_checks(require_commit=True):
    for name, expected in LOCKS.items():
        if text_hash(HERE / name) != expected:
            raise ValueError('Registered source/protocol changed: ' + name)
    plan = json.loads((HERE / PROTOCOL).read_text(encoding='utf-8'))
    if plan['evaluation_dates_UTC'] != DATES:
        raise ValueError('Unexpected dates')
    for key, value in SETTINGS['model'].items():
        if plan['model'][key] != value:
            raise ValueError('Pilot/protocol model mismatch: ' + key)
    names = list(LOCKS) + [Path(__file__).name]
    versions = {'python': platform.python_version(), 'numpy': np.__version__,
                'pandas': pd.__version__, 'sklearn': sklearn.__version__}
    source = {n: text_hash(HERE / n) for n in names}
    commit = None
    if require_commit:
        git = shutil.which('git')
        if not git:
            raise RuntimeError('Git executable not found')
        def command(*args):
            return subprocess.check_output([git, '-C', str(ROOT), *args], text=True).strip()
        files = [(HERE / n).relative_to(ROOT).as_posix() for n in names]
        command('ls-files', '--error-unmatch', '--', *files)
        if command('diff', 'HEAD', '--', *files):
            raise ValueError('Commit the study source and protocol before running')
        commit = command('rev-parse', 'HEAD')
    return plan, {'git_commit': commit, 'source_sha256_LF_normalized': source,
                  'versions': versions}


def verify_inputs(plan):
    raw = ROOT / 'data/zozo_open_bandit/raw'
    actual = {}
    for name, expected in plan['dataset']['input_sha256'].items():
        print('Verifying ' + name + '...', flush=True)
        actual[name] = sha256(raw / name)
        if actual[name] != expected:
            raise ValueError('Input checksum mismatch: ' + name)
    return raw, actual


def load_window(path, start, end):
    """Filter string timestamps and position BEFORE converting any click value."""
    start, end = pd.Timestamp(start), pd.Timestamp(end)
    dates = pd.date_range(start.normalize(), end, inclusive='left', freq='D').strftime('%Y-%m-%d')
    pieces = []
    for chunk in pd.read_csv(path, usecols=COLUMNS, dtype=str, chunksize=25000):
        mask = (chunk['position'] == '1') & chunk['timestamp'].str[:10].isin(dates)
        part = chunk.loc[mask].copy()
        if part.empty:
            continue
        times = pd.to_datetime(part['timestamp'], format='ISO8601', utc=True, errors='raise')
        mask = (times >= start) & (times < end)
        part = part.loc[mask].copy()
        if part.empty:
            continue
        part['timestamp'] = times.loc[mask]
        if part.isna().any().any():
            raise ValueError('Missing selected-window field')
        for column in ['item_id', 'click', 'propensity_score'] + AFFINITY:
            part[column] = pd.to_numeric(part[column], errors='raise')
        # Preserve the CSV data-row index for saved score audits.
        part['csv_row_index'] = part.index.to_numpy()
        pieces.append(part)
    if not pieces:
        raise ValueError('Empty study window: ' + str(start))
    frame = pd.concat(pieces, ignore_index=True)
    if not frame['timestamp'].is_monotonic_increasing:
        raise ValueError('Nonchronological study window')
    if not frame['item_id'].isin(range(34)).all() or not frame['click'].isin([0, 1]).all():
        raise ValueError('Invalid item or click in selected window')
    if not np.isfinite(frame[['propensity_score'] + AFFINITY].to_numpy(float)).all():
        raise ValueError('Nonfinite propensity or affinity')
    if not frame['propensity_score'].between(0, 1, inclusive='right').all():
        raise ValueError('Propensity must be positive and at most one')
    return frame


def metadata_from(path):
    items = pd.read_csv(path, dtype=str)
    fields = [f'item_feature_{i}' for i in range(4)]
    if items[['item_id'] + fields].isna().any().any():
        raise ValueError('Missing item metadata')
    if items['item_id'].duplicated().any() or set(items['item_id'].astype(int)) != set(range(34)):
        raise ValueError('Invalid product metadata')
    return {int(row['item_id']): {k: str(row[k]) for k in fields}
            for row in items.to_dict('records')}


def gate_decision(frame, q, candidate_actions, incumbent_actions):
    candidate = score_policy(frame, q, candidate_actions)
    incumbent = score_policy(frame, q, incumbent_actions)
    summary = row_summary(candidate[0] - incumbent[0])
    supported = bool(np.any(candidate[2] > 0) and np.any(incumbent[2] > 0))
    accepted = bool(supported and summary['row_lower_95'] > 0)
    summary.update(candidate_accepted=accepted, zero_match_rejection=not supported,
                   reason=('zero_matching_rows' if not supported else
                           'positive_lower_bound' if accepted else 'lower_bound_not_positive'))
    for label, result in [('candidate', candidate), ('incumbent', incumbent)]:
        for key, value in weight_summary(result[2], frame['click'].to_numpy()).items():
            summary[label + '_' + key] = value
    arrays = {'candidate_actions': candidate_actions, 'incumbent_actions': incumbent_actions,
              'candidate_dr': candidate[0], 'incumbent_dr': incumbent[0],
              'candidate_weights': candidate[2], 'incumbent_weights': incumbent[2]}
    return summary, arrays


def block_summaries(times, values):
    codes, blocks = pd.factorize(times.dt.floor('30min'), sort=True)
    return {'blocks': [str(b) for b in blocks], 'counts': np.bincount(codes).tolist(),
            'sums': [np.bincount(codes, weights=values[:, j]).tolist()
                     for j in range(values.shape[1])]}


def aggregate_days(days):
    """Columns share paired bootstrap draws; dates always have equal weight."""
    if len(days) != 5:
        raise ValueError('All five dates are required; no omitted-date analysis')
    daily = []
    rng = np.random.default_rng(42)
    boot = None
    enough_blocks = True
    for day in days:
        counts = np.asarray(day['counts'], dtype=float)
        sums = np.asarray(day['sums'], dtype=float)
        if not len(counts) or np.any(counts <= 0):
            raise ValueError('Empty bootstrap block')
        daily.append(sums.sum(axis=1) / counts.sum())
        n = len(counts)
        enough_blocks = enough_blocks and n >= 2
        draws = rng.integers(0, n, size=(1000, n))
        # Same block draws across all paired contrasts and estimators.
        means = sums[:, draws].sum(axis=2) / counts[draws].sum(axis=1)[None, :]
        boot = means / 5 if boot is None else boot + means / 5
    means = np.mean(daily, axis=0)
    interval = np.quantile(boot, [.025, .975], axis=1).T if enough_blocks else None
    return means, interval


def evaluate(frame, q, actions, date, source, output):
    results, rows = {}, []
    arrays = {'csv_row_index': frame['csv_row_index'].to_numpy(),
              'timestamp_ns': frame['timestamp'].astype('int64').to_numpy(),
              'logged_item': frame['item_id'].to_numpy(int), 'click': frame['click'].to_numpy(int),
              'propensity': frame['propensity_score'].to_numpy(float), 'common_q': q}
    for name in POLICIES:
        dr, ips, weights = score_policy(frame, q, actions[name])
        results[name] = {'dr': dr, 'ips': ips}
        row = {'date': date, 'source': source, 'policy': name, 'records': len(frame),
               'logged_clicks': int(frame['click'].sum()),
               **weight_summary(weights, frame['click'].to_numpy())}
        for estimator, scores in [('dr', dr), ('ips', ips)]:
            row.update({estimator + '_' + k: v for k, v in row_summary(scores).items()})
            arrays[name + '_' + estimator] = scores
        arrays[name + '_weights'] = weights
        if actions[name] is not None:
            arrays[name + '_actions'] = actions[name]
        rows.append(row)
    labels, contrasts, contrast_rows = [], [], []
    for left, right in PAIRS:
        for estimator in ['dr', 'ips']:
            label = left + '_minus_' + right + '__' + estimator
            values = results[left][estimator] - results[right][estimator]
            labels.append(label)
            contrasts.append(values)
            contrast_rows.append({'date': date, 'source': source, 'contrast': label,
                                  **row_summary(values)})
    blocks = block_summaries(frame['timestamp'], np.column_stack(contrasts))
    np.savez_compressed(output / (date + '_' + source + '_evaluation_scores.npz'), **arrays)
    return rows, contrast_rows, labels, blocks


def run(reproduce=False):
    plan, provenance = source_checks()
    raw, inputs = verify_inputs(plan)
    base = ROOT / 'data/zozo_open_bandit/five_day_runs'
    base.mkdir(parents=True, exist_ok=True)
    marker = base / 'first_execution.json'
    if marker.exists():
        first = json.loads(marker.read_text(encoding='utf-8'))
        if not reproduce:
            raise RuntimeError('First execution already recorded. Inspect it; repeats require --reproduce.')
        if first['source_sha256_LF_normalized'] != provenance['source_sha256_LF_normalized']:
            raise ValueError('Sources changed since first execution; a protocol deviation needs explicit review')
    elif reproduce:
        raise ValueError('No first execution exists to reproduce')
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid.uuid4().hex[:8]
    output = base / run_id
    output.mkdir(exist_ok=False)
    if not marker.exists():
        with marker.open('x', encoding='utf-8') as handle:
            json.dump({'run_id': run_id, **provenance}, handle, indent=2)
    manifest = {'status': 'running', 'run_id': run_id, 'reproduction': reproduce,
                'first_execution_marker': str(marker), 'input_sha256': inputs,
                **provenance, 'windows': [], 'reserved_outcomes_processing_started': False,
                'limitations': plan['uncertainty_and_diagnostics'],
                'scope': plan['execution_and_reporting']['contribution_scope']}
    print('Output directory: ' + str(output), flush=True)
    snapshots = output / 'source_snapshot'
    snapshots.mkdir()
    for name in provenance['source_sha256_LF_normalized']:
        shutil.copy2(HERE / name, snapshots / name)
    def checkpoint(stage):
        manifest['stage'] = stage
        write_json(output / 'manifest.json', manifest)
    def record(frame, date, source, part):
        manifest['windows'].append({'date': date, 'source': source, 'part': part,
                                   'records': len(frame), 'clicks': int(frame['click'].sum()),
                                   'first_timestamp': str(frame['timestamp'].iloc[0]),
                                   'last_timestamp': str(frame['timestamp'].iloc[-1])})
    try:
        checkpoint('initial_training')
        metadata = metadata_from(raw / 'item_context.csv')
        initial_data = load_window(raw / 'men_bts.csv', '2019-11-24T00:00Z', '2019-11-26T00:00Z')
        if len(initial_data) != plan['initial_training']['records'] or int(initial_data['click'].sum()) != plan['initial_training']['clicks']:
            raise ValueError('Initial development counts differ from registration')
        record(initial_data, '2019-11-24/25', 'bts', 'initial_training')
        print('Training initial model on the two development days...', flush=True)
        models = {'initial': fit_model(initial_data, metadata)}
        del initial_data
        paths = {'frozen': 'initial', 'refreshed': 'initial'}
        gates, evaluations, contrasts = [], [], []
        all_blocks = {'bts': [], 'random': []}
        manifest['reserved_outcomes_processing_started'] = True
        for date in DATES:
            checkpoint(date + ': candidate_training')
            print(date + ': loading morning training records...', flush=True)
            morning = load_window(raw / 'men_bts.csv', date + 'T00:00Z', date + 'T12:00Z')
            record(morning, date, 'bts', 'candidate_training')
            candidate_id = date + '_candidate'
            print(date + ': training candidate...', flush=True)
            models[candidate_id] = fit_model(morning, metadata)
            del morning
            checkpoint(date + ': gate_check')
            gate = load_window(raw / 'men_bts.csv', date + 'T12:00Z', date + 'T18:00Z')
            record(gate, date, 'bts', 'gate_check')
            print(date + ': predicting gate policies...', flush=True)
            predictions = {key: predict_all(models[key], gate, metadata)
                           for key in sorted({'initial', candidate_id, *paths.values()})}
            candidate_actions = predictions[candidate_id].argmax(axis=1)
            gate_arrays = {'timestamp_ns': gate['timestamp'].astype('int64').to_numpy(),
                           'csv_row_index': gate['csv_row_index'].to_numpy(),
                           'logged_item': gate['item_id'].to_numpy(int),
                           'click': gate['click'].to_numpy(int),
                           'propensity': gate['propensity_score'].to_numpy(float),
                           'frozen_q': predictions['initial'], 'refreshed_q': predictions[candidate_id]}
            for name in ['frozen', 'refreshed']:
                previous = paths[name]
                q = predictions['initial' if name == 'frozen' else candidate_id]
                summary, arrays = gate_decision(gate, q, candidate_actions,
                                                predictions[previous].argmax(axis=1))
                if summary['candidate_accepted']:
                    paths[name] = candidate_id
                gates.append({'date': date, 'gate': name, 'candidate_model': candidate_id,
                              'incumbent_before': previous, 'selected_model': paths[name], **summary})
                gate_arrays.update({name + '_' + k: v for k, v in arrays.items()})
                print(f"  {name}: gain={summary['mean']:.6f}; accepted={summary['candidate_accepted']}", flush=True)
            np.savez_compressed(output / (date + '_gate_scores.npz'), **gate_arrays)
            pd.DataFrame(gates).to_csv(output / 'gate_comparison.csv', index=False)
            del gate, predictions, gate_arrays
            for source, filename in [('bts', 'men_bts.csv'), ('random', 'men.csv')]:
                checkpoint(date + ': evaluation_' + source)
                end = str((pd.Timestamp(date, tz='UTC') + pd.Timedelta(days=1)).isoformat())
                frame = load_window(raw / filename, date + 'T18:00Z', end)
                record(frame, date, source, 'subsequent_evaluation')
                print(date + ': evaluating ' + source + '...', flush=True)
                predictions = {key: predict_all(models[key], frame, metadata)
                               for key in sorted({'initial', candidate_id, *paths.values()})}
                actions = {'frozen_gate_path': predictions[paths['frozen']].argmax(axis=1),
                           'refreshed_gate_path': predictions[paths['refreshed']].argmax(axis=1),
                           'initial_no_update': predictions['initial'].argmax(axis=1),
                           'always_update_current_candidate': predictions[candidate_id].argmax(axis=1),
                           'uniform_over_34_products': None}
                rows, paired, labels, blocks = evaluate(frame, predictions[candidate_id], actions,
                                                         date, source, output)
                evaluations.extend(rows)
                contrasts.extend(paired)
                all_blocks[source].append(blocks)
                pd.DataFrame(evaluations).to_csv(output / 'evaluation.csv', index=False)
                pd.DataFrame(contrasts).to_csv(output / 'daily_paired_contrasts.csv', index=False)
                write_json(output / 'bootstrap_blocks.json', {'labels': labels, 'sources': all_blocks})
                del frame, predictions, actions
            models = {key: model for key, model in models.items() if key in {'initial', *paths.values()}}
            checkpoint(date + ': complete')
        aggregate = {'date_weighting': 'equal across all five dates',
                     'interval_label': 'exploratory paired within-date 30-minute block percentile interval',
                     'interval_is_population_equivalence_or_safety_proof': False,
                     'bootstrap_resamples': 1000, 'seed': 42, 'sources': {}}
        for source in ['bts', 'random']:
            means, intervals = aggregate_days(all_blocks[source])
            aggregate['sources'][source] = {
                label: {'mean': float(means[j]),
                        'exploratory_interval': intervals[j].tolist() if intervals is not None else None,
                        'primary': source == 'bts' and j == 0}
                for j, label in enumerate(labels)}
        write_json(output / 'aggregate_contrasts.json', aggregate)
        manifest['status'] = 'complete'
        manifest['final_selected_models'] = paths
        checkpoint('complete')
        print('COMPLETE: ' + str(output), flush=True)
        print('Exploratory five-day gate case study; not proof of monitoring superiority or deployment safety.')
    except BaseException as exc:
        manifest.update(status='failed', error=repr(exc), traceback=traceback.format_exc())
        write_json(output / 'manifest.json', manifest)
        print('STOPPED. Partial output preserved: ' + str(output), flush=True)
        raise


def self_test():
    """Artificial records only; never opens research logs or first-run marker."""
    source_checks(require_commit=False)
    n = 4
    q = np.zeros((n, 34))
    q[:, 0], q[:, 1] = .2, .4
    frame = pd.DataFrame({'item_id': [0, 1, 0, 1], 'click': [1, 0, 0, 1],
                          'propensity_score': [.5] * n})
    a, b = np.zeros(n, dtype=int), np.ones(n, dtype=int)
    dr, ips, weights = score_policy(frame, q, a)
    np.testing.assert_allclose(dr, [1.8, .2, -.2, .2])
    np.testing.assert_allclose(ips, [2, 0, 0, 0])
    identical, _ = gate_decision(frame, q, a, a)
    assert identical['mean'] == 0 and not identical['candidate_accepted']
    positive = frame.copy()
    positive['item_id'] = [1, 0, 1, 0]
    positive['click'] = [1, 0, 1, 0]
    accepted, _ = gate_decision(positive, q, b, a)
    assert accepted['candidate_accepted']
    unsupported, _ = gate_decision(frame, q, np.full(n, 2), a)
    assert unsupported['zero_match_rejection'] and not unsupported['candidate_accepted']
    days = [{'counts': [1, 9], 'sums': [[v, v * 9], [0, 0]]}
            for v in [0, 1, 2, 3, 4]]
    means, interval = aggregate_days(days)
    np.testing.assert_allclose(means, [2, 0])
    np.testing.assert_allclose(interval, [[2, 2], [0, 0]], atol=1e-14)
    # Unequal date sizes still give each date the same weight.
    days[0] = {'counts': [100, 900], 'sums': [[0, 0], [0, 0]]}
    np.testing.assert_allclose(aggregate_days(days)[0], [2, 0])
    # Unequal block sizes use resampled record counts, not mean-of-block-means.
    block = block_summaries(pd.Series(pd.to_datetime(['2020-01-01T00:00Z',
                             '2020-01-01T00:30Z', '2020-01-01T00:31Z'])),
                             np.array([[0], [3], [3]]))
    assert block['counts'] == [1, 2] and block['sums'] == [[0.0, 6.0]]
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'toy.csv'
        rows = []
        for time, click, position in [('2019-11-26T11:59:59Z', 'bad', '1'),
                                       ('2019-11-26T12:00:00Z', '1', '1'),
                                       ('2019-11-26T17:59:59.1Z', '0', '1'),
                                       ('2019-11-26T18:00:00Z', 'bad', '1'),
                                       ('2019-11-27T12:00:00Z', 'bad', '1'),
                                       ('2019-11-26T13:00:00Z', 'bad', '2')]:
            rows.append({'timestamp': time, 'position': position, 'item_id': '0',
                         'click': click, 'propensity_score': '.5',
                         **{k: 'group' for k in USER}, **{k: '.2' for k in AFFINITY}})
        pd.DataFrame(rows).to_csv(path, index=False)
        window = load_window(path, '2019-11-26T12:00Z', '2019-11-26T18:00Z')
        assert len(window) == 2 and window['click'].sum() == 1
        assert window['csv_row_index'].tolist() == [1, 2]
        rows[1]['propensity_score'] = '0'
        pd.DataFrame(rows).to_csv(path, index=False)
        try:
            load_window(path, '2019-11-26T12:00Z', '2019-11-26T18:00Z')
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid selected-window propensity was accepted')
        # Fit the unchanged model and exercise saved evaluation arrays with toy data.
        window['csv_row_index'] = [0, 1]
        metadata = {i: {f'item_feature_{j}': str(i % 3) for j in range(4)} for i in range(34)}
        model = fit_model(window, metadata)
        probabilities = predict_all(model, window, metadata)
        assert probabilities.shape == (2, 34)
        actions = {name: probabilities.argmax(axis=1) for name in POLICIES}
        actions[POLICIES[-1]] = None
        rows, paired, labels, blocks = evaluate(window, probabilities, actions, 'toy', 'bts', Path(directory))
        assert len(rows) == 5 and len(paired) == 14
        assert paired[0]['mean'] == 0 and paired[1]['mean'] == 0
        assert (Path(directory) / 'toy_bts_evaluation_scores.npz').is_file()
    print('SELF-TEST PASSED: artificial-record scoring, gate rules, boundaries, validation, model, saved arrays and equal-date bootstrap.')
    print('No real logs or reserved outcomes opened.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--self-test', action='store_true')
    modes.add_argument('--preflight', action='store_true')
    modes.add_argument('--run', action='store_true')
    parser.add_argument('--reproduce', action='store_true')
    args = parser.parse_args()
    if args.reproduce and not args.run:
        parser.error('--reproduce requires --run')
    if args.self_test:
        self_test()
    elif args.preflight:
        plan, provenance = source_checks()
        verify_inputs(plan)
        print('PREFLIGHT PASSED: committed sources, registered protocol and all input checksums match.')
        print('No outcome analysis or model training performed. Commit: ' + provenance['git_commit'])
    else:
        run(args.reproduce)


if __name__ == '__main__':
    main()
