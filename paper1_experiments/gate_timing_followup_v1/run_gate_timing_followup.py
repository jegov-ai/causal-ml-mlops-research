"""Fixed protocol v1: artificial self-test, provenance preflight, then engineering pilot.

Usage: --prepare; commit source and .gitignore; --preflight; --run.
Validation requires --mode validation AND a completed pilot. No automatic retries.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import math
import platform
import subprocess
import sys
import time
import traceback
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / 'data/gate_timing_followup'
PROTOCOL = HERE / 'gate_timing_protocol_v1.json'
PROTOCOL_HASH = 'c8ab8a4f0745acb7a93aaee3cfd42aede6e5f8ef4e8537fae878ed47eff3c89c'
RULE = 'data/gate_timing_followup/'
TOL = 1e-10


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(content):
    return hashlib.sha256(content).hexdigest()


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def write_json(path, obj, exclusive=False):
    with path.open('x' if exclusive else 'w', encoding='utf-8', newline='\n') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')


def plan():
    obj = json.loads(PROTOCOL.read_text(encoding='utf-8'))
    require(digest(canonical(obj)) == PROTOCOL_HASH, 'Protocol differs from the specified v1.')
    return obj


def versions():
    return dict(python=platform.python_version(), numpy=np.__version__,
                pandas=pd.__version__, sklearn=sklearn.__version__)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def provenance(p):
    require(versions() == p['execution']['expected_versions'],
            'Version mismatch: ' + json.dumps(versions()) + '; stop before simulation.')
    files = [Path(__file__).resolve(), PROTOCOL, ROOT / '.gitignore']
    hashes = {}
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        subprocess.check_call(['git', 'ls-files', '--error-unmatch', rel], cwd=ROOT,
                              stdout=subprocess.DEVNULL)
        committed = subprocess.check_output(['git', 'show', 'HEAD:' + rel], cwd=ROOT)
        normal = path.read_bytes().replace(b'\r\n', b'\n')
        require(normal == committed.replace(b'\r\n', b'\n'), 'Uncommitted change: ' + rel)
        hashes[rel] = digest(normal)
    ignored = subprocess.run(['git', 'check-ignore', '-q', 'data/gate_timing_followup/probe'], cwd=ROOT)
    require(ignored.returncode == 0, 'Run --prepare and commit the data exclusion first.')
    return dict(commit=git('rev-parse', 'HEAD'), hashes=hashes, versions=versions())


def seeds_for(p, mode):
    a = p['sample_allocation']
    return (a['engineering_pilot_master_seeds'] if mode == 'pilot' else
            list(range(a['validation_master_seeds_start_inclusive'],
                       a['validation_master_seeds_end_exclusive'])))


def inventory():
    # Scan saved CSVs and ZIP-contained CSVs; exclude runtime/dependency trees.
    import os
    result = []
    excluded = {'.git', '.venv', '__pycache__', 'node_modules'}
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in excluded)
        for name in sorted(names):
            path = Path(base) / name
            if path.suffix.lower() in {'.csv', '.zip'}:
                st = path.stat()
                result.append([path.relative_to(ROOT).as_posix(), st.st_size, st.st_mtime_ns])
    return result


def scan_freshness(entries, seeds):
    hits, inspected, fields_seen = [], 0, []
    wanted = set(seeds)
    def check(stream, label):
        nonlocal inspected
        reader = csv.reader(stream)
        header = next(reader, [])
        cols = [i for i, v in enumerate(header) if v.strip().lower() == 'seed'
                or v.strip().lower().endswith('_seed')]
        if not cols:
            return
        inspected += 1
        fields_seen.append(dict(file=label, fields=[header[i] for i in cols]))
        for rowno, row in enumerate(reader, 2):
            for i in cols:
                require(i < len(row), f'Malformed seed row {label}:{rowno}')
                value = row[i].strip()
                if not value or value.lower() in {'nan', 'none', 'null'}:
                    continue
                try:
                    number = float(value)
                except ValueError as exc:
                    raise ValueError(f'Non-numeric seed field {label}:{rowno}: {value}') from exc
                require(math.isfinite(number) and number.is_integer(),
                        f'Invalid seed field {label}:{rowno}')
                if int(number) in wanted:
                    hits.append(dict(file=label, row=rowno, field=header[i], seed=int(number)))
    for rel, _, _ in entries:
        path = ROOT / rel
        if path.suffix.lower() == '.csv':
            with path.open(encoding='utf-8-sig', newline='') as f:
                check(f, rel)
        else:
            print('Scanning seed fields in:', rel, flush=True)
            with zipfile.ZipFile(path) as archive:
                for name in archive.namelist():
                    if name.lower().endswith('.csv'):
                        with archive.open(name) as raw:
                            with io.TextIOWrapper(raw, encoding='utf-8-sig', newline='') as f:
                                check(f, rel + '::' + name)
    return dict(scope='Project CSV seed/_seed columns and CSV members of ZIP archives; '
                      'not undocumented external runs or nested archives.',
                files_with_seed_columns=inspected, fields=fields_seen, collisions=hits)


def preflight(p, mode):
    DATA.mkdir(parents=True, exist_ok=True)
    require(not (DATA / (mode + '_first_execution.json')).exists(),
            'This phase already started. Preserve it; no automatic retries.')
    prov = provenance(p)
    entries = inventory()
    try:
        report = scan_freshness(entries, seeds_for(p, mode))
    except Exception:
        failure = DATA / ('preflight_failure_' + uuid.uuid4().hex[:12] + '.json')
        write_json(failure, dict(mode=mode, provenance=prov, error=traceback.format_exc()))
        raise
    ticket = dict(mode=mode, provenance=prov, inventory_hash=digest(canonical(entries)),
                  seeds=seeds_for(p, mode), freshness=report)
    write_json(DATA / (mode + '_preflight_' + uuid.uuid4().hex[:12] + '.json'), ticket, exclusive=True)
    write_json(DATA / (mode + '_preflight.json'), ticket)
    require(not report['collisions'], 'Allocated master seed collision; see preflight report.')
    print('PREFLIGHT PASSED:', mode, '; committed source, versions, exclusions and scoped seed scan.')
    print('No study outcomes generated. Commit:', prov['commit'])


def child(master, role):
    return int(np.random.SeedSequence([master, role]).generate_state(1, dtype=np.uint32)[0])


def features(rng, n, p):
    young = rng.random(n) < p['generator']['younger_probability']
    age = np.where(young, rng.integers(18, 35, n), rng.integers(35, 66, n))
    return np.column_stack((age, np.maximum(rng.normal(200, 60, n), 0)))


def observed(master, role, n, p):
    rng = np.random.default_rng(np.random.SeedSequence([master, role]))
    x = features(rng, n, p)
    return x, rng.binomial(1, .5, n), rng.normal(0, 20, n)


def effect(x, values):
    return np.where(x[:, 0] < 35, values['younger'], values['older'])


def fit(x, t, y, indices, master, codes, p):
    params = p['models_and_gate']['random_forest'].copy()
    params.pop('random_state')
    models = []
    for arm, code in enumerate(codes):
        idx = indices[t[indices] == arm]
        require(len(idx) >= 5, 'Insufficient arm records.')
        model = RandomForestRegressor(**params, random_state=child(master, code))
        model.fit(x[idx], y[idx])
        models.append(model)
    return models


def predict(models, x):
    value = np.column_stack([m.predict(x) for m in models])
    require(np.isfinite(value).all(), 'Nonfinite model prediction.')
    return value


def actions(mu, cost):
    return (mu[:, 1] - mu[:, 0] > cost).astype(np.int8)


def aipw(mu, t, y, propensity=.5):
    require(0 < propensity < 1, 'Invalid propensity.')
    require(np.isin(t, [0, 1]).all(), 'Invalid treatment.')
    return (mu[:, 1] - mu[:, 0] + t * (y - mu[:, 1]) / propensity
            - (1 - t) * (y - mu[:, 0]) / (1 - propensity))


def gate(g):
    require(len(g) > 1 and np.isfinite(g).all(), 'Invalid gate scores.')
    mean = float(np.mean(g))
    se = float(np.std(g, ddof=1) / np.sqrt(len(g)))
    lower = mean - 1.96 * se
    return dict(estimated_gain=mean, se=se, lower_95=lower, accepted=bool(lower > 0))


def multiplier(profile, h):
    return {'unchanged': 0, 'gradual_continue': h / 2, 'gradual_reverse': -h / 2,
            'abrupt_continue': int(h > 0), 'abrupt_reverse': -int(h > 0)}[profile]


def pair_loss(delta, accept):
    return max(delta, 0.) - int(accept) * delta


def oracle_loss(a, tau, cost):
    return float(np.mean(np.maximum(tau - cost, 0) - a * (tau - cost)))


def fingerprint(a):
    a = np.ascontiguousarray(a)
    return digest(canonical(dict(shape=a.shape, dtype=str(a.dtype))) + a.tobytes())


def experiment(master, p):
    started = time.perf_counter()
    cfg, allocation = p['generator'], p['sample_allocation']
    cost = cfg['cost']
    xi, ti, ei = observed(master, 0, cfg['initial_records'], p)
    xc, tc, ec = observed(master, 1, cfg['current_records'], p)
    xd = features(np.random.default_rng(np.random.SeedSequence([master, 2])),
                  cfg['deployment_feature_panel_records'], p)
    yi = 50 + .4 * xi[:, 1] + ti * effect(xi, cfg['initial_effects']) + ei
    itr, ihold = train_test_split(np.arange(len(xi)), test_size=.2, random_state=42)
    strata = (xc[:, 0] < 35).astype(int) * 2 + tc
    require(np.min(np.bincount(strata, minlength=4)) >= 2, 'Inadequate split strata.')
    ctr, cg = train_test_split(np.arange(len(xc)), test_size=.3,
                              random_state=child(master, 90), stratify=strata)
    require(len(set(ctr) & set(cg)) == 0 and len(ctr) + len(cg) == len(xc), 'Split overlap.')
    require(len(set(itr) & set(ihold)) == 0 and len(itr) + len(ihold) == len(xi), 'Initial split overlap.')
    require(np.isfinite(xi).all() and np.isfinite(xc).all() and np.isfinite(xd).all(), 'Malformed features.')
    # Row identity is (master, role, index); deployment has independent role 2.
    initial = fit(xi, ti, yi, itr, master, [10, 11], p)
    imug, imud = predict(initial, xc[cg]), predict(initial, xd)
    ai_g, ai_d = actions(imug, cost), actions(imud, cost)
    arrays = dict(initial_x=xi, initial_t=ti, initial_noise=ei, initial_y=yi,
                  initial_train=itr, initial_holdout=ihold, current_x=xc, current_t=tc,
                  current_noise=ec, current_train=ctr, gate_indices=cg, deployment_x=xd,
                  initial_gate_mu=imug, initial_deployment_mu=imud)
    decisions, outcomes, benchmarks = [], [], []
    primary = p['outcomes']['primary_regime']
    for ci, condition in enumerate(allocation['current_response_conditions']):
        current_tau = effect(xc, cfg['current_effects'][condition])
        yc = 50 + .4 * xc[:, 1] + tc * current_tau + ec
        candidate = fit(xc, tc, yc, ctr, master, [100 + 10 * ci, 101 + 10 * ci], p)
        cmug, cmud = predict(candidate, xc[cg]), predict(candidate, xd)
        ac_g, ac_d = actions(cmug, cost), actions(cmud, cost)
        diff_g, diff_d = ac_g - ai_g, ac_d - ai_d
        tau_g = current_tau[cg]
        tau_d = effect(xd, cfg['current_effects'][condition])
        step_g = effect(xc[cg], cfg['future_step_vectors'][condition])
        step_d = effect(xd, cfg['future_step_vectors'][condition])
        true_current = float(np.mean(diff_g * (tau_g - cost)))
        states = {}
        for label, mu in [('frozen', imug), ('refreshed', cmug)]:
            states[label] = gate(diff_g * (aipw(mu, tc[cg], yc[cg]) - cost))
            decisions.append(dict(master_seed=master, condition=condition, gate=label,
                                  true_current_gain_gate_panel=true_current, **states[label]))
        arrays[condition + '_y'] = yc
        arrays[condition + '_gate_mu'] = cmug
        arrays[condition + '_deployment_mu'] = cmud
        for profile in allocation['future_profiles']:
            for h in allocation['delays_periods']:
                m = multiplier(profile, h)
                future_g, future_d = tau_g + m * step_g, tau_d + m * step_d
                delta = float(np.mean(diff_d * (future_d - cost)))
                gate_future = float(np.mean(diff_g * (future_g - cost)))
                common = dict(master_seed=master, condition=condition, profile=profile, delay=h,
                              true_pair_gain=delta, future_younger=cfg['current_effects'][condition]['younger'] + m * cfg['future_step_vectors'][condition]['younger'],
                              future_older=cfg['current_effects'][condition]['older'] + m * cfg['future_step_vectors'][condition]['older'],
                              primary=condition in primary['current_conditions'] and profile == primary['future_profile'] and h == primary['delay_periods'])
                for label, state in states.items():
                    estimate, accepted = state['estimated_gain'], state['accepted']
                    error = estimate - delta
                    decomposition = [estimate - true_current, true_current - gate_future, gate_future - delta]
                    require(abs(sum(decomposition) - error) < TOL, 'Decomposition failure.')
                    loss = pair_loss(delta, accepted)
                    require(loss >= -TOL, 'Negative pair selection loss.')
                    selected = ac_d if accepted else ai_d
                    outcomes.append(dict(**common, gate=label, **state, selection_loss=loss,
                        signed_error=error, absolute_error=abs(error), squared_error=error ** 2,
                        current_estimation_error=decomposition[0], response_transfer=decomposition[1],
                        panel_composition=decomposition[2], accepted_harmful=accepted and delta < -TOL,
                        rejected_helpful=(not accepted) and delta > TOL, tied=abs(delta) <= TOL,
                        individual_oracle_regret=oracle_loss(selected, future_d, cost),
                        harmful_treatment_fraction=float(np.mean((selected == 1) & (future_d < cost)))))
                for label, a, choice in [('always_retain', ai_d, False), ('always_accept', ac_d, True),
                         ('offline_best_of_two', ac_d if delta > 0 else ai_d, delta > 0),
                         ('treat_all', np.ones(len(xd)), None), ('treat_none', np.zeros(len(xd)), None)]:
                    loss = None if choice is None else pair_loss(delta, choice)
                    require(label != 'offline_best_of_two' or abs(loss) < TOL, 'Oracle pair reference failure.')
                    benchmarks.append(dict(**common, policy=label, selection_loss=loss,
                                           individual_oracle_regret=oracle_loss(a, future_d, cost)))
    frame = pd.DataFrame(outcomes)
    require(len(decisions) == 6 and len(frame) == 90 and len(benchmarks) == 225, 'Missing factor cells.')
    for _, group in frame.groupby(['condition', 'gate']):
        require(group.estimated_gain.nunique() == 1 and group.accepted.nunique() == 1, 'Gate changed with future.')
        zero = group[group.delay == 0]
        require(np.ptp(zero.true_pair_gain.to_numpy()) < TOL, 'Zero-delay identity failure.')
    pri = frame[frame.primary].pivot(index='condition', columns='gate', values='selection_loss')
    require(len(pri) == 2 and not pri.isna().any().any(), 'Primary cell count failure.')
    seed_result = dict(master_seed=master, primary_difference=float((pri.refreshed - pri.frozen).mean()),
                       runtime_seconds=time.perf_counter() - started,
                       fingerprints={k: fingerprint(v) for k, v in arrays.items()},
                       child_seeds={str(code): child(master, code) for code in [0, 1, 2, 10, 11, 90, 100, 101, 110, 111, 120, 121]},
                       row_identity='(master_seed, role_code, row_index); initial=0,current=1,deployment=2')
    return decisions, outcomes, benchmarks, seed_result, arrays


def bootstrap_primary(values, resamples, seed):
    values = np.asarray(values, dtype=float)
    require(values.ndim == 1 and len(values) > 1 and np.isfinite(values).all(), 'Invalid master-seed values.')
    rng = np.random.default_rng(seed)
    boots = values[rng.integers(0, len(values), size=(resamples, len(values)))].mean(axis=1)
    return np.quantile(boots, [.025, .975]).tolist()


def self_test(p):
    require(pair_loss(2, False) == 2 and pair_loss(-2, True) == 2 and pair_loss(-2, False) == 0, 'Loss test.')
    require(not gate(np.zeros(20))['accepted'], 'Strict zero must reject.')
    require(gate(np.ones(20))['accepted'], 'Positive constant must accept.')
    mu = np.array([[2., 5.], [2., 5.]])
    np.testing.assert_allclose(aipw(mu, np.array([0, 1]), np.array([2., 5.])), [3., 3.])
    np.testing.assert_allclose(aipw(np.zeros((2, 2)), np.array([0, 1]), np.array([2., 5.])), [-4., 10.])
    require(actions(np.array([[0., 10.], [0., 11.]]), 10).tolist() == [0, 1], 'Policy threshold.')
    try:
        aipw(mu, np.array([0, 1]), np.array([2., 5.]), 0)
        raise AssertionError('Invalid probability accepted.')
    except ValueError:
        pass
    toy = json.loads(json.dumps(p))
    toy['generator'].update(initial_records=120, current_records=160, deployment_feature_panel_records=200)
    # Artificial software-test seed only; never uses allocated pilot/validation roots.
    d, o, b, result, arrays = experiment(12345, toy)
    require(result['master_seed'] not in seeds_for(p, 'pilot') + seeds_for(p, 'validation'), 'Test seed collision.')
    require(len(set(arrays['current_train']) & set(arrays['gate_indices'])) == 0, 'Train/gate reuse.')
    for group in toy['sample_allocation']['current_response_conditions']:
        state = [v for v in d if v['condition'] == group and v['gate'] == 'frozen'][0]
        idx = arrays['gate_indices']
        a0 = actions(arrays['initial_gate_mu'], 10)
        a1 = actions(arrays[group + '_gate_mu'], 10)
        recomputed = gate((a1-a0) * (aipw(arrays['initial_gate_mu'], arrays['current_t'][idx], arrays[group+'_y'][idx])-10))
        require(state['accepted'] == recomputed['accepted'] and state['estimated_gain'] == recomputed['estimated_gain'], 'Saved score reconstruction.')
    buffer = io.BytesIO()
    np.savez_compressed(buffer, **arrays)
    buffer.seek(0)
    with np.load(buffer, allow_pickle=False) as saved:
        for key, value in arrays.items():
            require(fingerprint(saved[key]) == fingerprint(value), 'Saved array roundtrip failure.')
    require(bootstrap_primary([0., 0., 0.], 50, 13) == [0., 0.], 'Zero bootstrap failure.')
    require(bootstrap_primary([-1., 0., 2.], 50, 13) == bootstrap_primary([-1., 0., 2.], 50, 13), 'Bootstrap reproducibility.')
    require(child(12345, 90) == child(12345, 90) and child(12345, 1) != child(12345, 2), 'Child seed allocation.')
    require(all(v['selection_loss'] is None for v in b if v['policy'] in ['treat_all','treat_none']), 'Undefined benchmark loss.')
    print('SELF-TEST PASSED: artificial models, AIPW, strict gates, split separation, fixed decisions, '
          '45 cells, two primary cells, oracle references and timing decomposition.')
    print('No allocated pilot or validation seeds generated.')


def run(p, mode):
    ticket_path = DATA / (mode + '_preflight.json')
    require(ticket_path.is_file(), 'Run --preflight first.')
    ticket = json.loads(ticket_path.read_text())
    require(ticket['provenance'] == provenance(p), 'Preflight source/version changed.')
    require(ticket['inventory_hash'] == digest(canonical(inventory())), 'Saved CSV/ZIP inventory changed; repeat preflight.')
    require(ticket['seeds'] == seeds_for(p, mode) and not ticket['freshness']['collisions'], 'Invalid preflight ticket.')
    if mode == 'validation':
        marker = DATA / 'pilot_first_execution.json'
        require(marker.is_file(), 'Complete engineering pilot first.')
        pilot = json.loads(marker.read_text())
        report = json.loads((DATA / pilot['output_relative'] / 'manifest.json').read_text())
        require(report['status'] == 'complete' and report['completed_seeds'] == seeds_for(p, 'pilot'), 'Pilot incomplete.')
        print('Pilot runtime seconds:', round(report['runtime_seconds'], 2), flush=True)
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '_' + uuid.uuid4().hex[:8]
    out = DATA / (mode + '_runs') / stamp
    out.mkdir(parents=True, exist_ok=False)
    write_json(DATA / (mode + '_first_execution.json'),
               dict(output_relative=out.relative_to(DATA).as_posix(), seeds=seeds_for(p, mode)), exclusive=True)
    print('Output directory:', out, flush=True)
    manifest = dict(status='started', mode=mode, seeds=seeds_for(p, mode), completed_seeds=[],
                    provenance=ticket['provenance'], protocol_sha256=PROTOCOL_HASH,
                    estimator_parameters=p['models_and_gate']['random_forest'],
                    audit_scope='Runtime invariants and saved data only; no independent model refits.',
                    pilot_purpose=p['execution']['pilot_purpose'])
    write_json(out / 'manifest.json', manifest)
    write_json(out / 'preflight.json', ticket)
    (out / PROTOCOL.name).write_text(PROTOCOL.read_text(), encoding='utf-8')
    (out / Path(__file__).name).write_text(Path(__file__).read_text(), encoding='utf-8')
    start = time.perf_counter()
    decisions, outcomes, benchmarks, seeds = [], [], [], []
    try:
        for master in seeds_for(p, mode):
            print('Running', mode, 'master seed', master, flush=True)
            d, o, b, seed, arrays = experiment(master, p)
            temporary = out / f'seed_{master}.npz.partial'
            with temporary.open('xb') as f:
                np.savez_compressed(f, **arrays)
            temporary.rename(out / f'seed_{master}.npz')
            write_json(out / f'seed_{master}.json', seed, exclusive=True)
            decisions.extend(d); outcomes.extend(o); benchmarks.extend(b); seeds.append(seed)
            for name, rows in [('gate_decisions.csv',decisions), ('gate_outcomes.csv',outcomes),
                               ('benchmark_outcomes.csv',benchmarks)]:
                pd.DataFrame(rows).to_csv(out / name, index=False)
            pd.DataFrame([{k:s[k] for k in ['master_seed','primary_difference','runtime_seconds']} for s in seeds]).to_csv(out / 'primary_seed_differences.csv', index=False)
            manifest['completed_seeds'].append(master)
            write_json(out / 'manifest.json', manifest)
        values = np.array([s['primary_difference'] for s in seeds])
        analysis = dict(mode=mode, independent_master_seeds=len(values), primary_mean=float(values.mean()),
                        negative_favors='refreshed', protocol_primary=p['outcomes']['primary_regime'],
                        interpretation='Fixed synthetic setting only; no safety, equivalence or universal superiority claim.',
                        bootstrap_interval=None, monte_carlo_se=None)
        if mode == 'validation':
            cfg = p['analysis']['primary_bootstrap']
            analysis.update(bootstrap_interval=bootstrap_primary(values, cfg['resamples'], cfg['seed']),
                            monte_carlo_se=float(values.std(ddof=1)/np.sqrt(len(values))),
                            bootstrap_resamples=cfg['resamples'], bootstrap_seed=cfg['seed'])
        else:
            analysis['inference'] = 'Engineering pilot only; no inferential interval; excluded from validation.'
        frame = pd.DataFrame(outcomes)
        secondary = frame.groupby(['condition','profile','delay','gate'], as_index=False)[['selection_loss','signed_error','absolute_error','squared_error','individual_oracle_regret','accepted_harmful','rejected_helpful']].mean()
        secondary.to_csv(out / 'secondary_descriptive.csv', index=False)
        write_json(out / 'analysis.json', analysis)
        manifest.update(status='complete', runtime_seconds=time.perf_counter()-start)
        write_json(out / 'manifest.json', manifest)
        print('COMPLETE:', out, flush=True)
        if mode == 'pilot':
            print('Pilot runtime seconds:', round(manifest['runtime_seconds'],2))
            print('Review engineering feasibility before validation. All 100 validation seeds remain unused.')
        else:
            print('Primary refreshed-minus-frozen selection loss:', analysis['primary_mean'])
            print('Paired master-seed interval:', analysis['bootstrap_interval'])
    except BaseException:
        manifest.update(status='failed', runtime_seconds=time.perf_counter()-start, failure=traceback.format_exc())
        write_json(out / 'manifest.json', manifest)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    for flag in ['self-test','prepare','preflight','run']:
        group.add_argument('--'+flag, action='store_true')
    parser.add_argument('--mode', choices=['pilot','validation'], default='pilot')
    args = parser.parse_args()
    p = plan()
    if args.self_test or args.prepare:
        self_test(p)
        if args.prepare:
            path = ROOT / '.gitignore'
            text = path.read_text(encoding='utf-8')
            if RULE not in text.splitlines():
                path.write_text(text.rstrip()+'\n\n'+RULE+'\n', encoding='utf-8')
            DATA.mkdir(parents=True, exist_ok=True)
            print('Data exclusion prepared. Commit .gitignore and this runner before --preflight.')
    elif args.preflight:
        preflight(p, args.mode)
    else:
        run(p, args.mode)


if __name__ == '__main__':
    main()
