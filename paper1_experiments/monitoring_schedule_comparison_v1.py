"""Prospective fixed-calendar vs alert-triggered review comparison.

Reuses the frozen ablation calibration; fresh evaluation streams only.
No main evaluation starts until reference, protocol, versions, Git and seeds pass.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import pandas as pd
import sklearn
from sklearn.model_selection import train_test_split

BASE_PATH = Path(__file__).with_name("monitoring_signal_ablation_v1.py")
spec = importlib.util.spec_from_file_location("schedule_frozen_base", BASE_PATH)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
METHODS = (*base.METHODS, "PERIODIC")
CALENDARS = {2: (4, 8), 4: (3, 6, 9, 12), 8: (1, 3, 4, 6, 7, 9, 10, 12)}
SCENARIOS, REVIEW_BUDGETS = base.SCENARIOS, base.REVIEW_BUDGETS
FEATURES, PERIODS, CHANGE, COST = base.FEATURES, base.PERIODS, base.CHANGE, base.COST
make_window, outcomes, policy = base.make_window, base.outcomes, base.policy
fit_models, aipw_effect = base.fit_models, base.aipw_effect
monitor_vector, decision_metrics = base.monitor_vector, base.decision_metrics
attribution_audit = base.attribution_audit
EVALUATION_START, EVALUATION_RUNS = 350000, 100


def monitor_scores(vectors, center, scale):
    result = base.monitor_scores(vectors, center, scale)
    result["PERIODIC"] = np.zeros(len(vectors))
    return result


def evaluate_stream(seed, scenario, n, baseline, center, scale, thresholds,
                    explainer, background, anchors, baseline_phi):
    states = {(method, budget): {
        "model": baseline, "alerts": 0, "started": False,
        "reviews": 0, "accepted": 0, "first_detection": None,
    } for method in METHODS for budget in REVIEW_BUDGETS}
    records = []
    benchmarks = []
    audit_cache = {}
    for period in range(1, PERIODS + 1):
        data = make_window(seed, period, scenario, n)
        vector = monitor_vector(data, baseline, explainer)
        scores = monitor_scores(vector[None, :], center, scale)
        prediction_cache = {}

        def cached_outcomes(models):
            key = id(models)
            if key not in prediction_cache:
                prediction_cache[key] = outcomes(models, data)
            return prediction_cache[key]

        baseline_mu0, baseline_mu1 = cached_outcomes(baseline)
        # All incumbent decisions are scored before current outcomes are used.
        for name, action in (
            ("treat_all", np.ones(n, dtype=bool)),
            ("treat_none", np.zeros(n, dtype=bool)),
            ("frozen_tlearner", (baseline_mu1 - baseline_mu0) > COST),
        ):
            benchmarks.append(dict(seed=seed, scenario=scenario, period=period,
                                   benchmark=name, **decision_metrics(data, action)))
        pending_records = []
        for (method, budget), st in states.items():
            mu0, mu1 = cached_outcomes(st["model"])
            action = (mu1 - mu0) > COST
            cate_error = float(np.mean(
                ((mu1 - mu0) - data.true_effect.to_numpy()) ** 2
            ) ** .5)
            score = float(scores[method][0])
            issue = method != "PERIODIC" and score > thresholds[method] and st["alerts"] < 2
            if issue:
                st["alerts"] += 1
                st["started"] = True
                if (scenario != "stable" and period >= CHANGE
                        and st["first_detection"] is None):
                    st["first_detection"] = period
            review = (period in CALENDARS[budget] if method == "PERIODIC"
                      else st["started"] and st["reviews"] < budget)
            row = dict(
                seed=seed, scenario=scenario, period=period,
                method=method, review_budget=budget,
                score=score, threshold=thresholds[method],
                alert_issued=bool(issue), review_performed=bool(review),
                retrain_accepted=False, gate_mean=np.nan, gate_lower=np.nan,
                cate_rmse=cate_error, **decision_metrics(data, action),
            )
            # The following audit sees truth ONLY for ex-post scoring.
            # Its outputs never enter alerts, review schedules or update gates.
            row.update(attribution_audit(
                st["model"], background, anchors, audit_cache,
                baseline_phi, period, scenario,
            ))
            pending_records.append((row, st))
        # A common candidate and common holdout are shared across all arms.
        # Cache avoids repeated actual fitting; per-arm reviews are still counted.
        if any(row["review_performed"] for row, _ in pending_records):
            strata = (data.age.lt(35).astype(int) * 2 + data.discount)
            training, gate = train_test_split(
                data, test_size=.30, stratify=strata,
                random_state=seed + period,
            )
            candidate = fit_models(training, seed + period)
            candidate_action = policy(candidate, gate)
            # Baseline nuisance models are independent of this gate dataset.
            net_pseudo = aipw_effect(gate, baseline) - COST
            gate_cache = {}
            for row, st in pending_records:
                if not row["review_performed"]:
                    continue
                st["reviews"] += 1
                key = id(st["model"])
                if key not in gate_cache:
                    gate_cache[key] = policy(st["model"], gate)
                incumbent_action = gate_cache[key]
                gain = (candidate_action.astype(float)
                        - incumbent_action.astype(float)) * net_pseudo
                mean = float(gain.mean())
                lower = mean - 1.96 * float(gain.std(ddof=1)) / np.sqrt(len(gain))
                row.update(gate_mean=mean, gate_lower=lower)
                if lower > 0:
                    st["model"] = candidate
                    st["accepted"] += 1
                    row["retrain_accepted"] = True
        records.extend(row for row, _ in pending_records)
    rows = pd.DataFrame(records)
    summaries = []
    for (method, budget), st in states.items():
        part = rows[(rows.method == method) & (rows.review_budget == budget)]
        post = part.loc[part.period >= CHANGE]
        detection = st["first_detection"]
        summaries.append(dict(
            seed=seed, scenario=scenario, method=method, review_budget=budget,
            alerts=st["alerts"], any_alert=int(st["alerts"] > 0),
            reviews=st["reviews"], accepted_retrains=st["accepted"],
            prechange_regret=part.loc[part.period < CHANGE, "regret"].sum(),
            postchange_regret=post.regret.sum(),
            mean_cate_rmse=post.cate_rmse.mean(),
            attribution_mae=post.audit_attribution_mae.mean(),
            explanation_change=post.audit_change_from_original.mean(),
            harmful_treatment_rate=post.harmful_treatment_rate.mean(),
            change_detected=(int(detection is not None)
                             if scenario != "stable" and method != "PERIODIC" else np.nan),
            detection_delay=(detection - CHANGE if detection is not None else np.nan),
        ))
    return records, summaries, benchmarks


def preflight(reference):
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((reference / 'manifest.json').read_text())
    if manifest['mode'] != 'study' or manifest['n'] != 1000:
        raise RuntimeError('Expected the completed 1000-customer ablation study reference.')
    frozen = '47a5d523ea995b6a7697759f0217c3e7342513b4585de476f44e2adcaede000f'
    if hashlib.sha256(BASE_PATH.read_bytes()).hexdigest() != frozen or manifest['script_sha256'] != frozen:
        raise RuntimeError('Ablation source differs from the audited frozen study; stop for review.')
    if json.loads((reference/'checkpoint.json').read_text())['status'] != 'complete':
        raise RuntimeError('Reference run is incomplete.')
    for name, actual in [('numpy',np.__version__),('pandas',pd.__version__),('sklearn',sklearn.__version__)]:
        if manifest[name] != actual:
            raise RuntimeError(f'{name} version differs from reference; do not combine environments silently.')
    if hashlib.sha256(BASE_PATH.with_name('integrated_causal_monitoring_v2_xai.py').read_bytes()).hexdigest() != manifest['source_baseline_sha256']:
        raise RuntimeError('Historical baseline source changed.')
    protocol = Path(__file__).with_name('SCHEDULE_COMPARISON_PROTOCOL_v1.md')
    expected = '784e5a744ce1b2d9694602632abfac8ba8cbf1ec3d79eeb663a513935fbd8e97'
    if hashlib.sha256(protocol.read_bytes()).hexdigest() != expected:
        raise RuntimeError('Schedule protocol differs from the prospective version.')
    if subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=root,text=True).strip():
        raise RuntimeError('Tracked changes exist; review and commit before evaluation.')
    for path in [Path(__file__),protocol]:
        subprocess.check_call(['git','ls-files','--error-unmatch',path.resolve().relative_to(root).as_posix()],cwd=root,stdout=subprocess.DEVNULL)
    checked=0
    for path in root.rglob('*.csv'):
        if any(part in {'.git','.venv','venv','__pycache__'} for part in path.relative_to(root).parts):
            continue
        cols = pd.read_csv(path,nrows=0).columns
        if 'seed' not in cols:
            continue
        checked+=1
        for chunk in pd.read_csv(path,usecols=['seed'],chunksize=100000):
            seeds=pd.to_numeric(chunk['seed'],errors='raise')
            if seeds.between(EVALUATION_START,EVALUATION_START+EVALUATION_RUNS-1).any():
                raise RuntimeError(f'Evaluation seeds already recorded in {path}; preserve files and review before repeating.')
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
    return manifest,protocol,dict(git_commit=commit,protocol_sha256=expected,seed_csv_files_checked=checked)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',type=Path,default=Path(__file__).with_name('monitoring_signal_ablation_v1_study')/'run_20261102_012152')
    parser.add_argument('--output',type=Path)
    parser.add_argument('--preflight-only',action='store_true')
    args=parser.parse_args()
    reference=args.reference.resolve()
    manifest,protocol,provenance=preflight(reference)
    print('PREFLIGHT PASSED:',provenance,flush=True)
    if args.preflight_only:
        print('No evaluation data generated.'); return
    started=time.perf_counter()
    train,test=train_test_split(base.original_data(),test_size=.2,random_state=42)
    baseline=fit_models(train,42)
    mu0,mu1=outcomes(baseline,test)
    saved=json.loads((reference/'baseline.json').read_text())
    report={'cate_mae':float(np.abs(mu1-mu0-test.true_effect).mean()),
            'recommended':int(((mu1-mu0)>COST).sum()),
            **decision_metrics(test,(mu1-mu0)>COST)}
    for field,value in report.items():
        if not np.isclose(value,saved[field],rtol=0,atol=1e-10):
            raise RuntimeError('Initial model does not reproduce reference baseline: '+field)
    calibration=pd.read_csv(reference/'signal_calibration.csv')
    if list(calibration.signal)!=list(base.SIGNAL_NAMES):
        raise RuntimeError('Reference signal calibration ordering differs.')
    center=calibration.center.to_numpy();scale=calibration.scale.to_numpy()
    if not np.isfinite(center).all() or not np.isfinite(scale).all() or not (scale>0).all():
        raise RuntimeError('Invalid frozen signal calibration.')
    thresholds={**manifest['thresholds'],'PERIODIC':0.0}
    background=pd.read_csv(reference/'explanation_background.csv')
    anchors=pd.read_csv(reference/'explanation_anchors.csv')
    explainer=base.TwoFeatureShapley(baseline,background)
    baseline_phi,_=explainer.explain(anchors)
    out=(args.output or Path(__file__).with_name('monitoring_schedule_comparison_v1_results'))/time.strftime('run_%Y%m%d_%H%M%S')
    out.mkdir(parents=True,exist_ok=False)
    (out/'script_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (out/'protocol_snapshot.md').write_bytes(protocol.read_bytes())
    launch={**provenance,'status':'started','reference':str(reference),'evaluation_start':EVALUATION_START,
            'test_runs':EVALUATION_RUNS,'calendars':CALENDARS,'thresholds':thresholds,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'base_sha256':hashlib.sha256(BASE_PATH.read_bytes()).hexdigest(),
            'reference_manifest_sha256':hashlib.sha256((reference/'manifest.json').read_bytes()).hexdigest(),
            'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__,'python':sys.version,
            'initial_model_report':report,'scope':'Prospective exploratory schedule comparison, fixed initial model; reused frozen calibration, fresh evaluation seeds.'}
    (out/'launch.json').write_text(json.dumps(launch,indent=2))
    print('Results folder:',out.resolve(),flush=True)
    print('Using unchanged frozen alert calibration; PERIODIC has no alerts or detection metric.',flush=True)
    records=[];results=[];benchmarks=[]
    for scenario in SCENARIOS:
        for index,seed in enumerate(range(EVALUATION_START,EVALUATION_START+EVALUATION_RUNS)):
            rows,runs,bench=evaluate_stream(seed,scenario,1000,baseline,center,scale,thresholds,explainer,background,anchors,baseline_phi)
            records.extend(rows);results.extend(runs);benchmarks.extend(bench)
            print(scenario,index+1,'/',EVALUATION_RUNS,flush=True)
        pd.DataFrame(records).to_csv(out/'period_log.csv',index=False)
        pd.DataFrame(results).to_csv(out/'run_results.csv',index=False)
        pd.DataFrame(benchmarks).to_csv(out/'benchmarks.csv',index=False)
        (out/'checkpoint.json').write_text(json.dumps({'status':'partial','last_completed_scenario':scenario},indent=2))
    runs=pd.DataFrame(results)
    summary=runs.groupby(['scenario','review_budget','method']).agg(
        seeds=('seed','size'),mean_postchange_regret=('postchange_regret','mean'),
        mean_prechange_regret=('prechange_regret','mean'),mean_reviews=('reviews','mean'),
        mean_alerts=('alerts','mean'),mean_accepted_retrains=('accepted_retrains','mean'),
        mean_harmful_treatment_rate=('harmful_treatment_rate','mean')).reset_index()
    summary.to_csv(out/'summary.csv',index=False)
    intervals=[];rng=np.random.default_rng(518)
    contrasts=[(method,'PERIODIC') for method in base.METHODS]+[('M2-FULL','M1')]
    for scenario in SCENARIOS:
        for budget in REVIEW_BUDGETS:
            wide=runs.query('scenario==@scenario and review_budget==@budget').pivot(index='seed',columns='method',values='postchange_regret')
            for left,right in contrasts:
                d=(wide[left]-wide[right]).to_numpy()
                boot=rng.choice(d,(5000,len(d)),replace=True).mean(axis=1)
                intervals.append(dict(scenario=scenario,review_budget=budget,comparison=left+' minus '+right,
                    seeds=len(d),mean_difference=float(d.mean()),ci_low=float(np.quantile(boot,.025)),ci_high=float(np.quantile(boot,.975))))
    pd.DataFrame(intervals).to_csv(out/'paired_descriptive_intervals.csv',index=False)
    final={**launch,'status':'complete','elapsed_seconds':time.perf_counter()-started,
           'n':1000,'periods':PERIODS,'change_period':CHANGE,'cost':COST,'review_budgets':REVIEW_BUDGETS,
           'period_rows':len(records),'run_rows':len(results),
           'interpretation':'Negative monitor-minus-PERIODIC regret difference favors alerts. Pointwise paired descriptive bootstrap; no multiplicity-adjusted inference. PERIODIC has no detection/false-alert endpoint. Same caps are not equal actual workload.'}
    (out/'manifest.json').write_text(json.dumps(final,indent=2))
    (out/'checkpoint.json').write_text(json.dumps({'status':'complete','manifest':'manifest.json'},indent=2))
    print(summary.to_string(index=False));print('COMPLETE:',out.resolve(),flush=True)
    print('Elapsed minutes:',round(final['elapsed_seconds']/60,2))

if __name__=='__main__':
    main()
