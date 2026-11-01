"""Paper 1: exploratory development of the M2 signal ablation.

M1 baseline; M2-A adds subgroup effects; M2-B adds assignment contrast;
M2-FULL adds both. Original historical script and outputs stay unchanged.
Only development smoke/pilot modes are enabled; no unseen study seeds are used.
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
METHODS = ("M1", "M2-A", "M2-B", "M2-FULL")
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
    "age_mean_abs_shap", "spending_mean_abs_shap",
    "age_mean_signed_shap", "spending_mean_signed_shap",
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
    if scenario not in SCENARIOS:
        raise ValueError(f"Unknown scenario: {scenario}")
    if n < 20 or period < 1 or period > PERIODS:
        raise ValueError("Expected n >= 20 and a period within the monitoring horizon.")
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


def estimated_effect(models, data):
    mu0, mu1 = outcomes(models, data)
    return mu1 - mu0


class TwoFeatureShapley:
    """Enumerate all four coalitions against a fixed empirical background.

    v(empty) = mean f(B), v(age) = mean f(age_x, spending_B),
    v(spending) = mean f(age_B, spending_x), v(both) = f(x).
    phi_age = ((v(age)-v(empty)) + (v(both)-v(spending))) / 2.
    phi_spending is the analogous average over the two feature orderings.
    Exact for this finite background; background choice remains a limitation.
    No dependency on the SHAP Python package is required.
    """

    def __init__(self, models, background):
        self.models = models
        self.background = background[FEATURES].reset_index(drop=True).copy()
        self.expected = float(estimated_effect(models, self.background).mean())
        self.age_values = {}
        self.live_cache = {}
        self.compute_seconds = 0.0
        for age in range(18, 66):
            masked = self.background.copy()
            masked["age"] = age
            self.age_values[age] = float(estimated_effect(models, masked).mean())

    def explain(self, frame):
        x = frame[FEATURES].reset_index(drop=True)
        count, size = len(x), len(self.background)
        age_terms = []
        for age in x.age.to_numpy():
            if age not in self.age_values:
                masked = self.background.copy()
                masked["age"] = age
                self.age_values[age] = float(estimated_effect(self.models, masked).mean())
            age_terms.append(self.age_values[age])
        age_terms = np.asarray(age_terms)
        masked = pd.DataFrame({
            "age": np.tile(self.background.age.to_numpy(), count),
            "previous_spending": np.repeat(x.previous_spending.to_numpy(), size),
        })
        spending_terms = estimated_effect(self.models, masked).reshape(count, size).mean(axis=1)
        full = estimated_effect(self.models, x)
        phi = np.column_stack((
            .5 * (age_terms - self.expected + full - spending_terms),
            .5 * (spending_terms - self.expected + full - age_terms),
        ))
        error = float(np.max(np.abs(phi.sum(axis=1) + self.expected - full)))
        if error > 1e-8:
            raise RuntimeError("Shapley additivity check failed.")
        return phi, error

    def live_summary(self, frame):
        key = hashlib.sha256(frame[FEATURES].to_numpy(dtype=float).tobytes()).digest()
        if key not in self.live_cache:
            started = time.perf_counter()
            phi, _ = self.explain(frame)
            self.live_cache[key] = np.r_[np.abs(phi).mean(axis=0), phi.mean(axis=0)]
            self.compute_seconds += time.perf_counter() - started
        return self.live_cache[key].copy()


def oracle_effect_for_audit(frame, period, scenario):
    """Offline-only synthetic truth: never called by alerts or the gate."""
    young = frame.age.to_numpy() < 35
    if period >= CHANGE and scenario == "response":
        return np.where(young, 5.0, 15.0)
    if period >= CHANGE and scenario == "opposing":
        older = 15.0 + 35.0 * YOUNG_SHARE / (1.0 - YOUNG_SHARE)
        return np.where(young, 5.0, older)
    return np.where(young, 40.0, 15.0)


def attribution_audit(models, background, anchors, cache, baseline_phi, period, scenario):
    key = id(models)
    if key not in cache:
        explainer = TwoFeatureShapley(models, background)
        phi, error = explainer.explain(anchors)
        # Retain a model reference to prevent Python id reuse in this cache.
        cache[key] = (models, phi, error)
    _, phi, error = cache[key]
    truth = oracle_effect_for_audit(anchors, period, scenario)
    reference_truth = oracle_effect_for_audit(background, period, scenario).mean()
    oracle_phi = np.column_stack((truth - reference_truth, np.zeros(len(truth))))
    return {
        "audit_age_mean_abs_shap": float(np.abs(phi[:, 0]).mean()),
        "audit_spending_mean_abs_shap": float(np.abs(phi[:, 1]).mean()),
        "audit_attribution_mae": float(np.abs(phi - oracle_phi).mean()),
        "audit_change_from_original": float(np.abs(phi - baseline_phi).mean()),
        "audit_additivity_error": error,
    }


def aipw_effect(data, models):
    """Observed-data pseudo-outcome; known randomized propensities."""
    mu0, mu1 = outcomes(models, data)
    treatment = data.discount.to_numpy()
    y = data.purchase_amount.to_numpy()
    p = data.propensity.to_numpy()
    if not np.isfinite(p).all() or not ((p > 0) & (p < 1)).all():
        raise ValueError("AIPW requires finite propensities strictly between 0 and 1.")
    return (
        mu1 - mu0 + treatment * (y - mu1) / p
        - (1 - treatment) * (y - mu0) / (1 - p)
    )


def monitor_vector(data, baseline, explainer):
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
    vector = np.r_[vector, explainer.live_summary(data)]
    if not np.isfinite(vector).all():
        raise ValueError("A monitor statistic is undefined.")
    return vector


def monitor_scores(vectors, center, scale):
    z = np.abs((vectors - center) / scale)
    # M1 includes all conventional signals, including the overall treatment rate.
    # Only the EXTRA group assignment contrast (index 12) is ablated here.
    return {"M1": z[:, :10].max(axis=1),
            "M2-A": z[:, :12].max(axis=1),
            "M2-B": z[:, list(range(10)) + [12]].max(axis=1),
            "M2-FULL": z[:, :13].max(axis=1)}


def stream_vectors(seed, scenario, n, baseline, explainer):
    return np.asarray([
        monitor_vector(make_window(seed, p, scenario, n), baseline, explainer)
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
                             if scenario != "stable" else np.nan),
            detection_delay=(detection - CHANGE if detection is not None else np.nan),
        ))
    return records, summaries, benchmarks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("smoke", "pilot"), default="smoke")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    # Development-only runs. Study execution is deliberately not exposed until
    # CSV seed audit, compute assessment and prospective protocol freeze finish.
    config = {"n": 1000, "scale_runs": 10, "calibration_runs": 40,
              "null_runs": 20, "test_runs": 3}
    starts = {"scale": 301000, "calibration": 302000,
              "null": 303000, "evaluation": 300001}
    if args.mode == "smoke":
        config = {"n": 200, "scale_runs": 3, "calibration_runs": 5,
                  "null_runs": 3, "test_runs": 1}
        starts = {"scale": 300010, "calibration": 300020,
                  "null": 300030, "evaluation": 300000}
    out = args.output or Path(__file__).resolve().parent / (
        "monitoring_signal_ablation_v1_" + args.mode
    )
    # Each execution has its own folder, so earlier results are retained.
    out = out / time.strftime("run_%Y%m%d_%H%M%S")
    out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    print("MODE:", args.mode, "| exploratory synthetic benchmark", flush=True)
    print("Results folder:", out.resolve(), flush=True)
    if args.mode == "smoke":
        print("SMOKE TEST ONLY: thresholds and results are not research estimates.", flush=True)
    train, test = train_test_split(original_data(), test_size=.2, random_state=42)
    baseline = fit_models(train, 42)
    # Fixed balanced background: eight original training rows per age group.
    background = pd.concat([
        train.loc[train.age < 35, FEATURES].sample(n=8, random_state=123),
        train.loc[train.age >= 35, FEATURES].sample(n=8, random_state=456),
    ], ignore_index=True)
    anchors = make_window(70000, 1, "stable", 64)[FEATURES]
    explainer = TwoFeatureShapley(baseline, background)
    baseline_phi, _ = explainer.explain(anchors)
    background.to_csv(out / "explanation_background.csv", index=False)
    anchors.to_csv(out / "explanation_anchors.csv", index=False)
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
        stream_vectors(seed, "stable", config["n"], baseline, explainer)
        for seed in range(starts["scale"], starts["scale"] + config["scale_runs"])
    ])
    center = scale_data.mean(axis=0)
    scale = np.maximum(scale_data.std(axis=0, ddof=1), 1e-8)
    maxima = {m: [] for m in METHODS}
    print("Calibrating independent null-run maxima...", flush=True)
    for index, seed in enumerate(range(starts["calibration"], starts["calibration"] + config["calibration_runs"])):
        v = stream_vectors(seed, "stable", config["n"], baseline, explainer)
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
    for seed in range(starts["null"], starts["null"] + config["null_runs"]):
        scores = monitor_scores(
            stream_vectors(seed, "stable", config["n"], baseline, explainer), center, scale
        )
        for m in METHODS:
            null_records.append(dict(seed=seed, method=m,
                                     any_alert=int(np.any(scores[m] > thresholds[m]))))
    null = pd.DataFrame(null_records)
    records, results, benchmarks = [], [], []
    for scenario in SCENARIOS:
        for index, seed in enumerate(range(starts["evaluation"], starts["evaluation"] + config["test_runs"])):
            r, s, b = evaluate_stream(
                seed, scenario, config["n"], baseline, center, scale, thresholds,
                explainer, background, anchors, baseline_phi
            )
            records.extend(r)
            results.extend(s)
            benchmarks.extend(b)
            print(scenario, "seed", index + 1, "/", config["test_runs"], flush=True)
        # Checkpoint each completed scenario.
        pd.DataFrame(results).to_csv(out / "run_results.csv", index=False)
        pd.DataFrame(records).to_csv(out / "period_log.csv", index=False)
        pd.DataFrame(benchmarks).to_csv(out / "benchmarks.csv", index=False)
        (out / "checkpoint.json").write_text(json.dumps({
            "status": "partial", "last_completed_scenario": scenario,
            "mode": args.mode, "config": config, "seed_starts": starts,
            "thresholds": thresholds,
            "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        }, indent=2))
    runs = pd.DataFrame(results)
    summary = runs.groupby(["scenario", "review_budget", "method"]).agg(
        runs=("seed", "size"), mean_loss=("postchange_regret", "mean"),
        mean_reviews=("reviews", "mean"),
        accepted_retrains=("accepted_retrains", "mean"),
        detection_rate=("change_detected", "mean"),
        detection_delay=("detection_delay", "mean"),
        mean_cate_rmse=("mean_cate_rmse", "mean"),
        attribution_mae=("attribution_mae", "mean"),
        explanation_change=("explanation_change", "mean"),
        harmful_treatment_rate=("harmful_treatment_rate", "mean"),
    ).reset_index()
    summary["mean_postchange_cumulative_regret"] = summary["mean_loss"]
    summary["mean_postchange_regret_per_period"] = summary["mean_loss"] / (PERIODS - CHANGE + 1)
    counts = runs.groupby(["scenario", "review_budget", "method"]).agg(
        detected_runs=("change_detected", "sum"),
        eligible_shift_runs=("change_detected", "count"),
    ).reset_index()
    summary = summary.merge(counts, on=["scenario", "review_budget", "method"], validate="one_to_one")
    summary["missed_runs"] = summary.eligible_shift_runs - summary.detected_runs
    summary.loc[summary.eligible_shift_runs == 0, ["detected_runs", "missed_runs"]] = np.nan
    # Paired, per-scenario/per-budget descriptive intervals; no p-value claims.
    intervals = []
    bootstrap_rng = np.random.default_rng(518)
    for scenario in SCENARIOS:
        if scenario == "stable":
            continue
        for budget in REVIEW_BUDGETS:
            subset = runs[(runs.scenario == scenario) & (runs.review_budget == budget)]
            wide = subset.pivot(index="seed", columns="method", values="postchange_regret")
            contrasts = (
                ("M2-A minus M1", {"M2-A": 1, "M1": -1}),
                ("M2-B minus M1", {"M2-B": 1, "M1": -1}),
                ("M2-FULL minus M1", {"M2-FULL": 1, "M1": -1}),
                ("M2-FULL minus M2-A", {"M2-FULL": 1, "M2-A": -1}),
                ("M2-FULL minus M2-B", {"M2-FULL": 1, "M2-B": -1}),
                ("descriptive interaction", {"M2-FULL": 1, "M2-A": -1,
                                             "M2-B": -1, "M1": 1}),
            )
            for label, weights in contrasts:
                differences = sum(wide[m] * weight for m, weight in weights.items()).to_numpy()
                boot = bootstrap_rng.choice(differences, (5000, len(differences)), replace=True).mean(axis=1)
                intervals.append(dict(
                    scenario=scenario, review_budget=budget, comparison=label,
                    seeds=len(differences), mean_loss_difference=differences.mean(),
                    ci_low=np.quantile(boot, .025), ci_high=np.quantile(boot, .975),
                ))
    pd.DataFrame(intervals).to_csv(out / "paired_descriptive_intervals.csv", index=False)
    # Wilson intervals show the imprecision of the held-out null checks.
    null_summary = null.groupby("method").any_alert.agg(["sum", "count", "mean"])
    z = 1.96
    for method in METHODS:
        count = null_summary.loc[method, "count"]
        rate = null_summary.loc[method, "mean"]
        denominator = 1 + z*z/count
        midpoint = (rate + z*z/(2*count)) / denominator
        half = z * np.sqrt(rate*(1-rate)/count + z*z/(4*count*count)) / denominator
        null_summary.loc[method, "wilson_low"] = midpoint - half
        null_summary.loc[method, "wilson_high"] = midpoint + half
    null_summary.to_csv(out / "heldout_null_summary.csv")
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
        "seeds": {"baseline": 42, "scale_start": starts["scale"],
                  "calibration_start": starts["calibration"],
                  "evaluation_start": starts["evaluation"], "heldout_null_start": starts["null"]},
        "python": sys.version, "platform": platform.platform(),
        "numpy": np.__version__, "pandas": pd.__version__,
        "sklearn": sklearn.__version__,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "elapsed_seconds": time.perf_counter() - started,
        "method_definitions": {
            "M1": "conventional signals 0:9 plus AIPW ATE (index 9)",
            "M2-A": "M1 plus subgroup AIPW effects (indices 10,11)",
            "M2-B": "M1 plus group assignment contrast (index 12)",
            "M2-FULL": "M1 plus subgroup AIPW effects AND group assignment contrast",
        },
        "source_baseline_sha256": hashlib.sha256(
            Path(__file__).with_name("integrated_causal_monitoring_v2_xai.py").read_bytes()
        ).hexdigest(),
        "phase": "engineering development only; not unseen main evaluation",
        "protocol": "SIGNAL_ABLATION_DEVELOPMENT_PROTOCOL_v1.md",
        "compute_note": "Historical explanation diagnostics retained in all arms; Shapley signals never enter ablation scores. Runtime includes diagnostics and caching.",
        "loss_units": "mean_loss is a legacy alias for the sum of period-average regret over periods 7 through 12; mean_postchange_regret_per_period divides by 6.",
        "harm_units": "harmful_treatment_rate is the fraction of ALL customers treated despite negative effect minus assumed cost; it is not conditional on treatment.",
        "scope": "Exploratory synthetic offline replay, conditional on one initial model.",
        "gate": "Same-window holdout AIPW improvement lower pointwise 95% bound > 0; no sequential safety guarantee.",
        "timing": "Score decisions first; current labels can update the next period only.",
        "monitor": "Frozen common baseline nuisance model; no threshold/reference reset.",
        "budgets": "First alert starts consecutive reviews; each review fits/evaluates one common candidate; actual computation cached across arms.",
        "truth": "Known effects used only for offline scores, never training/alerts/gates.",
        "explanations": "Exact 2-feature Shapley enumeration, interventional masking against 16 fixed observed background rows; explains the fitted CATE function, not input-feature causal effects.",
        "explanation_audit": "64 fixed independent anchors; oracle attribution error is offline synthetic evaluation only; no gate/alert access.",
        "xai_blind_spot": "Frozen-model explanations cannot independently reveal a pure response shift when the feature distribution is unchanged.",
        "xai_shared_live_compute_seconds": explainer.compute_seconds,
        "intervals": "Paired percentile bootstrap 95% descriptive intervals; unadjusted across scenarios, budgets and contrasts; development runs are insufficient for research inference.",
        "omissions": "No confounding, deployment feedback, delayed labels or external data. Main study is unavailable until a separate prospective freeze.",
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    (out / "checkpoint.json").write_text(json.dumps({"status": "complete", "manifest": "manifest.json"}, indent=2))
    print("\nHELD-OUT NULL FALSE-ALERT RATES")
    print(null_summary.round(4).to_string())
    print("\nEXPLORATORY RESULTS")
    print(summary.round(4).to_string(index=False))
    print("\nSaved to:", out.resolve())
    print("Four-arm signal ablation; development results do not establish superiority.")
    print("Attributions explain the fitted model; stable explanations do not prove reliable effects.")
    print("Intervals are exploratory; no multiplicity-adjusted significance claim.")
    print("Loss is spending gain minus assumed campaign cost, not actual profit.")


if __name__ == "__main__":
    main()
