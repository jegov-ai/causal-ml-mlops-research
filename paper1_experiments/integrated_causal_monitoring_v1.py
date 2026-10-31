"""Exploratory causal-ML monitoring benchmark for Paper 1.

Run from the project root with its virtual-environment Python.
Default: a small PILOT, not a confirmatory research result.
M0 = conventional; M1 = M0 + ATE; M2 = M1 + subgroup effects.
M3 explanation monitoring is not implemented in this version.
"""

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

FEATURES = ["age", "previous_spending"]
METHODS = ("M0", "M1", "M2")
SCENARIOS = ("stable", "covariate", "assignment", "response", "opposing")
COST = 10.0
YOUNG_SHARE = 17 / 48
PERIODS = 12
CHANGE = 7
REVIEW_BUDGETS = (2, 4, 8)
SIGNAL_NAMES = (
    "age_mean", "age_sd", "spending_mean", "spending_sd",
    "treatment_rate", "outcome_mean", "outcome_variance",
    "residual_mean", "residual_second_moment", "aipw_ate",
    "aipw_young_effect", "aipw_older_effect", "assignment_contrast",
)


def original_data():
    """Reproduce the user's original baseline generator exactly."""
    rng = np.random.default_rng(42)
    age = rng.integers(18, 66, size=1000)
    spending = np.clip(rng.normal(200, 60, 1000), 0, None)
    treatment = rng.binomial(1, .5, 1000)
    effect = np.where(age < 35, 40.0, 15.0)
    noise = rng.normal(0, 20, 1000)
    return pd.DataFrame({
        "age": age, "previous_spending": spending,
        "discount": treatment,
        "purchase_amount": 50 + .4 * spending + noise + treatment * effect,
        "propensity": .5, "true_effect": effect,
    })


def fit_models(data, seed):
    """Only observed features, treatment and outcomes enter training."""
    models = []
    for arm in (0, 1):
        part = data.loc[data.discount == arm]
        if len(part) < 10:
            raise ValueError("Too few observations in a training arm.")
        model = RandomForestRegressor(
            n_estimators=100, min_samples_leaf=5,
            random_state=seed, n_jobs=1,
        )
        model.fit(part[FEATURES], part.purchase_amount)
        models.append(model)
    return tuple(models)


def outcomes(models, data):
    return tuple(model.predict(data[FEATURES]) for model in models)


def policy(models, data):
    mu0, mu1 = outcomes(models, data)
    return (mu1 - mu0) > COST


def make_window(seed, period, scenario, n):
    """Logged assignments are independent of policy recommendations."""
    rng = np.random.default_rng(np.random.SeedSequence([seed, period]))
    shifted = period >= CHANGE
    share = .65 if scenario == "covariate" and shifted else YOUNG_SHARE
    young = rng.random(n) < share
    age = np.where(young, rng.integers(18, 35, n), rng.integers(35, 66, n))
    spending = np.clip(rng.normal(200, 60, n), 0, None)
    propensity = np.full(n, .5)
    if scenario == "assignment" and shifted:
        propensity = np.where(young, .2, .8)
    treatment = (rng.random(n) < propensity).astype(int)
    effect = np.where(young, 40.0, 15.0)
    if shifted and scenario == "response":
        effect = np.where(young, 5.0, 15.0)
    if shifted and scenario == "opposing":
        # The POPULATION ATE is stable in expectation, not in every sample.
        older = 15.0 + 35.0 * YOUNG_SHARE / (1.0 - YOUNG_SHARE)
        effect = np.where(young, 5.0, older)
    outcome = (
        50 + .4 * spending + rng.normal(0, 20, n)
        + treatment * effect
    )
    return pd.DataFrame({
        "age": age, "previous_spending": spending,
        "discount": treatment, "purchase_amount": outcome,
        "propensity": propensity, "true_effect": effect,
    })


def aipw_effect(data, models):
    """Observed-data pseudo-outcome; known randomized propensities."""
    mu0, mu1 = outcomes(models, data)
    treatment = data.discount.to_numpy()
    y = data.purchase_amount.to_numpy()
    p = data.propensity.to_numpy()
    return (
        mu1 - mu0 + treatment * (y - mu1) / p
        - (1 - treatment) * (y - mu0) / (1 - p)
    )


def monitor_vector(data, baseline):
    mu0, mu1 = outcomes(baseline, data)
    treatment = data.discount.to_numpy()
    y = data.purchase_amount.to_numpy()
    p = data.propensity.to_numpy()
    young = data.age.to_numpy() < 35
    residual = y - np.where(treatment == 1, mu1, mu0)
    pseudo = (
        mu1 - mu0 + treatment * (y - mu1) / p
        - (1 - treatment) * (y - mu0) / (1 - p)
    )
    vector = np.array([
        data.age.mean(), data.age.std(ddof=1),
        data.previous_spending.mean(), data.previous_spending.std(ddof=1),
        treatment.mean(), y.mean(), y.var(ddof=1),
        residual.mean(), np.mean(residual ** 2), pseudo.mean(),
        pseudo[young].mean(), pseudo[~young].mean(),
        treatment[young].mean() - treatment[~young].mean(),
    ])
    if not np.isfinite(vector).all():
        raise ValueError("A monitor statistic is undefined.")
    return vector


def monitor_scores(vectors, center, scale):
    z = np.abs((vectors - center) / scale)
    return {"M0": z[:, :9].max(axis=1),
            "M1": z[:, :10].max(axis=1),
            "M2": z.max(axis=1)}


def stream_vectors(seed, scenario, n, baseline):
    return np.asarray([
        monitor_vector(make_window(seed, p, scenario, n), baseline)
        for p in range(1, PERIODS + 1)
    ])


def decision_metrics(data, action):
    """Latent truth is used ONLY for offline scoring."""
    net = data.true_effect.to_numpy() - COST
    regret = float(np.mean(np.maximum(net, 0) - action * net))
    return {
        "regret": regret,
        "harmful_treatment_rate": float(np.mean(action & (net < 0))),
        "treatment_rate": float(np.mean(action)),
    }


def evaluate_stream(seed, scenario, n, baseline, center, scale, thresholds):
    states = {(method, budget): {
        "model": baseline, "alerts": 0, "started": False,
        "reviews": 0, "accepted": 0, "first_detection": None,
    } for method in METHODS for budget in REVIEW_BUDGETS}
    records = []
    benchmarks = []
    for period in range(1, PERIODS + 1):
        data = make_window(seed, period, scenario, n)
        vector = monitor_vector(data, baseline)
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
            issue = score > thresholds[method] and st["alerts"] < 2
            if issue:
                st["alerts"] += 1
                st["started"] = True
                if (scenario != "stable" and period >= CHANGE
                        and st["first_detection"] is None):
                    st["first_detection"] = period
            review = st["started"] and st["reviews"] < budget
            row = dict(
                seed=seed, scenario=scenario, period=period,
                method=method, review_budget=budget,
                score=score, threshold=thresholds[method],
                alert_issued=bool(issue), review_performed=bool(review),
                retrain_accepted=False, gate_mean=np.nan, gate_lower=np.nan,
                cate_rmse=cate_error, **decision_metrics(data, action),
            )
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
            harmful_treatment_rate=post.harmful_treatment_rate.mean(),
            change_detected=(int(detection is not None)
                             if scenario != "stable" else np.nan),
            detection_delay=(detection - CHANGE if detection is not None else np.nan),
        ))
    return records, summaries, benchmarks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("pilot", "study"), default="pilot")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    config = ({"n": 600, "scale_runs": 20, "calibration_runs": 100,
               "null_runs": 50, "test_runs": 5} if args.mode == "pilot" else
              {"n": 1000, "scale_runs": 100, "calibration_runs": 1000,
               "null_runs": 200, "test_runs": 50})
    out = args.output or Path("paper1_experiments") / (
        "integrated_causal_monitoring_v1_" + args.mode
    )
    # Each execution has its own folder, so earlier results are retained.
    out = out / time.strftime("run_%Y%m%d_%H%M%S")
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    print("MODE:", args.mode, "| exploratory synthetic benchmark", flush=True)
    print("Results folder:", out.resolve(), flush=True)
    train, test = train_test_split(original_data(), test_size=.2, random_state=42)
    baseline = fit_models(train, 42)
    mu0, mu1 = outcomes(baseline, test)
    baseline_report = {
        "train_n": len(train), "test_n": len(test),
        "cate_mae": float(np.abs(mu1 - mu0 - test.true_effect).mean()),
        "recommended": int(((mu1 - mu0) > COST).sum()),
        **decision_metrics(test, (mu1 - mu0) > COST),
    }
    print("ORIGINAL MODEL BASELINE:", baseline_report, flush=True)
    print("Estimating stable signal scales...", flush=True)
    scale_data = np.concatenate([
        stream_vectors(seed, "stable", config["n"], baseline)
        for seed in range(50000, 50000 + config["scale_runs"])
    ])
    center = scale_data.mean(axis=0)
    scale = np.maximum(scale_data.std(axis=0, ddof=1), 1e-8)
    maxima = {m: [] for m in METHODS}
    print("Calibrating independent null-run maxima...", flush=True)
    for index, seed in enumerate(range(60000, 60000 + config["calibration_runs"])):
        v = stream_vectors(seed, "stable", config["n"], baseline)
        scores = monitor_scores(v, center, scale)
        for m in METHODS:
            maxima[m].append(float(scores[m].max()))
        if (index + 1) % 25 == 0:
            print("Calibration:", index + 1, "/", config["calibration_runs"], flush=True)
    thresholds = {m: float(np.quantile(maxima[m], .95, method="higher"))
                  for m in METHODS}
    print("Thresholds:", thresholds, flush=True)
    null_records = []
    print("Checking false alerts on held-out stable runs...", flush=True)
    for seed in range(90000, 90000 + config["null_runs"]):
        scores = monitor_scores(
            stream_vectors(seed, "stable", config["n"], baseline), center, scale
        )
        for m in METHODS:
            null_records.append(dict(seed=seed, method=m,
                                     any_alert=int(np.any(scores[m] > thresholds[m]))))
    null = pd.DataFrame(null_records)
    records, results, benchmarks = [], [], []
    for scenario in SCENARIOS:
        for index, seed in enumerate(range(80000, 80000 + config["test_runs"])):
            r, s, b = evaluate_stream(
                seed, scenario, config["n"], baseline, center, scale, thresholds
            )
            records.extend(r)
            results.extend(s)
            benchmarks.extend(b)
            print(scenario, "seed", index + 1, "/", config["test_runs"], flush=True)
        # Checkpoint each completed scenario.
        pd.DataFrame(results).to_csv(out / "run_results.csv", index=False)
    runs = pd.DataFrame(results)
    summary = runs.groupby(["scenario", "review_budget", "method"]).agg(
        runs=("seed", "size"), mean_loss=("postchange_regret", "mean"),
        mean_reviews=("reviews", "mean"),
        accepted_retrains=("accepted_retrains", "mean"),
        detection_rate=("change_detected", "mean"),
        detection_delay=("detection_delay", "mean"),
        mean_cate_rmse=("mean_cate_rmse", "mean"),
        harmful_treatment_rate=("harmful_treatment_rate", "mean"),
    ).reset_index()
    pd.DataFrame(records).to_csv(out / "period_log.csv", index=False)
    pd.DataFrame(benchmarks).to_csv(out / "benchmarks.csv", index=False)
    summary.to_csv(out / "summary.csv", index=False)
    null.to_csv(out / "heldout_null_runs.csv", index=False)
    pd.DataFrame({"signal": SIGNAL_NAMES, "center": center, "scale": scale}).to_csv(
        out / "signal_calibration.csv", index=False
    )
    (out / "baseline.json").write_text(json.dumps(baseline_report, indent=2))
    manifest = {
        **config, "mode": args.mode, "thresholds": thresholds,
        "cost": COST, "periods": PERIODS, "change_period": CHANGE,
        "review_budgets": REVIEW_BUDGETS, "alert_cap": 2,
        "seeds": {"baseline": 42, "scale_start": 50000,
                  "calibration_start": 60000, "evaluation_start": 80000,
                  "heldout_null_start": 90000},
        "python": sys.version, "platform": platform.platform(),
        "numpy": np.__version__, "pandas": pd.__version__,
        "sklearn": sklearn.__version__,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "elapsed_seconds": time.perf_counter() - started,
        "scope": "Exploratory synthetic offline replay, conditional on one initial model.",
        "gate": "Same-window holdout AIPW improvement lower pointwise 95% bound > 0; no sequential safety guarantee.",
        "timing": "Score decisions first; current labels can update the next period only.",
        "monitor": "Frozen common baseline nuisance model; no threshold/reference reset.",
        "budgets": "First alert starts consecutive reviews; each review fits/evaluates one common candidate; actual computation cached across arms.",
        "truth": "Known effects used only for offline scores, never training/alerts/gates.",
        "omissions": "No M3, confounding, deployment feedback, delayed labels or external data. Study mode alone is not confirmatory preregistration.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("\nHELD-OUT NULL FALSE-ALERT RATES")
    print(null.groupby("method").any_alert.mean().to_string())
    print("\nEXPLORATORY RESULTS")
    print(summary.round(4).to_string(index=False))
    print("\nSaved to:", out.resolve())
    print("M3 is not implemented. Small pilot results do not establish superiority.")
    print("Loss is spending gain minus assumed campaign cost, not actual profit.")


if __name__ == "__main__":
    main()
