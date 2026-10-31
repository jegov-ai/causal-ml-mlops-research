"""Controlled monitoring validation; synthetic randomized data only.
Not a complete causal-ML/MLOps or explainability validation.
"""

from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("paper1_experiments/monitoring_validation_v2_followup_results")

PERIODS = 12
CHANGE_PERIOD = 6
N_PER_GROUP = 400
ALERT_BUDGET = 2
CALIBRATION_RUNS = 500
TEST_RUNS = 100
METHODS = ("M0", "M1", "M2")
SCENARIOS = ("stable", "response_shift")
REFERENCE_SIZE = 10000


def generate(rng, period, scenario, n=N_PER_GROUP):
    group = np.repeat([0, 1], n)
    x = rng.normal(0, 1, 2 * n)
    treatment = rng.binomial(1, 0.5, 2 * n)

    # Group A is coded 0; group B is coded 1.
    effect = np.where(group == 0, 20.0, 15.0)

    if scenario == "response_shift":
        change = 6.0 * max(0, period - 5)
        effect = effect - (group == 0) * change

    outcome = (
        40.0 + 2.0 * x
        + treatment * effect
        + rng.normal(0, 12, 2 * n)
    )
    return group, x, treatment, outcome, effect


def summarize(data):
    group, x, treatment, outcome, _ = data
    estimates = []
    errors = []

    for g in (0, 1):
        treated = outcome[(group == g) & (treatment == 1)]
        control = outcome[(group == g) & (treatment == 0)]

        estimates.append(treated.mean() - control.mean())
        errors.append(np.sqrt(
            treated.var(ddof=1) / len(treated)
            + control.var(ddof=1) / len(control)
        ))

    estimates = np.asarray(estimates)
    errors = np.asarray(errors)

    # Equal group sizes: ATE is the average group effect.
    vector = np.array([
        x.mean(),
        treatment.mean(),
        outcome.mean(),
        outcome.var(ddof=1),
        estimates.mean(),
        estimates[0],
        estimates[1],
    ])
    return vector, estimates, errors


def stream(seed, scenario):
    rng = np.random.default_rng(seed)

    # Historical reference is independent of monitoring windows.
    reference, _, _ = summarize(
        generate(rng, 1, "stable", n=REFERENCE_SIZE)
    )

    vectors = []
    estimates = []
    errors = []
    truths = []

    for period in range(1, PERIODS + 1):
        data = generate(rng, period, scenario)
        vector, estimate, error = summarize(data)
        vectors.append(vector - reference)
        estimates.append(estimate)
        errors.append(error)

        group, _, _, _, effect = data
        truths.append([
            effect[group == g].mean() for g in (0, 1)
        ])

    return (
        np.asarray(vectors),
        np.asarray(estimates),
        np.asarray(errors),
        np.asarray(truths),
    )


def scores(vectors, center, scale):
    z = np.abs((vectors - center) / scale)

    # Nested monitors: each additional arm adds information.
    return {
        "M0": z[:, :4].max(axis=1),
        "M1": z[:, :5].max(axis=1),
        "M2": z.max(axis=1),
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    print("Estimating stable signal scales...", flush=True)
    scale_vectors = np.concatenate([
        stream(seed, "stable")[0]
        for seed in range(1000, 1100)
    ])
    center = scale_vectors.mean(axis=0)
    scale = np.maximum(
        scale_vectors.std(axis=0, ddof=1), 1e-8
    )

    print("Calibrating run-level thresholds...", flush=True)
    null_maxima = {method: [] for method in METHODS}

    for seed in range(2000, 2000 + CALIBRATION_RUNS):
        vectors, _, _, _ = stream(seed, "stable")
        signals = scores(vectors, center, scale)

        for method in METHODS:
            null_maxima[method].append(signals[method].max())

    thresholds = {
        method: float(np.quantile(
            null_maxima[method], 0.95, method="higher"
        ))
        for method in METHODS
    }
    print("Thresholds:", thresholds, flush=True)

    rows = []
    period_rows = []

    for scenario in SCENARIOS:
        for seed in range(10000, 10000 + TEST_RUNS):
            vectors, estimates, errors, truths = stream(
                seed, scenario
            )
            signals = scores(vectors, center, scale)

            for method in METHODS:
                active = np.array([True, True])
                alerts = 0
                first_change_alert = None
                prechange_alerts = 0
                prechange_regret = 0.0
                postchange_regret = 0.0
                harmful_treatment_windows = 0

                for index in range(PERIODS):
                    period = index + 1
                    truth = truths[index]

                    # Score the incumbent action BEFORE current labels
                    # can trigger a response.
                    chosen_value = np.where(active, truth, 0.0)
                    oracle_value = np.maximum(truth, 0.0)

                    # Equal group weights; outcome units per customer.
                    regret = float(
                        (oracle_value - chosen_value).mean()
                    )

                    if period < CHANGE_PERIOD:
                        prechange_regret += regret
                    else:
                        postchange_regret += regret

                    harmful_treatment_windows += int(
                        np.any(active & (truth < 0))
                    )

                    period_rows.append({
                        "seed": seed,
                        "scenario": scenario,
                        "method": method,
                        "period": period,
                        "score": float(signals[method][index]),
                        "threshold": thresholds[method],
                        "alerts_used_before": alerts,
                        "budget_exhausted": alerts >= ALERT_BUDGET,
                        "alert_issued": (
                            alerts < ALERT_BUDGET
                            and signals[method][index] > thresholds[method]
                        ),
                        "active_A_before": bool(active[0]),
                        "active_B_before": bool(active[1]),
                        "estimated_effect_A": estimates[index, 0],
                        "estimated_effect_B": estimates[index, 1],
                        "upper_bound_A": (
                            estimates[index, 0]
                            + 1.96 * errors[index, 0]
                        ),
                        "true_effect_A": truth[0],
                        "true_effect_B": truth[1],
                        "period_regret": regret,
                    })

                    issue_alert = (
                        alerts < ALERT_BUDGET
                        and signals[method][index] > thresholds[method]
                    )
                    if issue_alert:
                        alerts += 1
                        if period < CHANGE_PERIOD:
                            prechange_alerts += 1
                        elif (
                            scenario == "response_shift"
                            and first_change_alert is None
                        ):
                            first_change_alert = period

                    # Follow-up reviews are additional resource use.
                    review_now = alerts > 0
                    period_rows[-1]["review_performed"] = review_now
                    if not review_now:
                        continue

                    lower = estimates[index] - 1.96 * errors[index]
                    upper = estimates[index] + 1.96 * errors[index]
                    next_active = active.copy()
                    next_active[upper < 0] = False
                    next_active[lower > 0] = True
                    # Current labels affect next period's actions only.
                    active = next_active

                rows.append({
                    "seed": seed,
                    "scenario": scenario,
                    "method": method,
                    "alerts": alerts,
                    "any_alert": int(alerts > 0),
                    "prechange_alerts": prechange_alerts,
                    "change_detected": int(
                        first_change_alert is not None
                    ),
                    "change_detection_delay": (
                        first_change_alert - CHANGE_PERIOD
                        if first_change_alert is not None
                        else np.nan
                    ),
                    "prechange_regret": prechange_regret,
                    "postchange_regret": postchange_regret,
                    "harmful_treatment_windows":
                        harmful_treatment_windows,
                })

        print("Completed:", scenario, flush=True)

    diagnostic_out = Path(
        "paper1_experiments/monitoring_validation_v2_followup_diagnostic_results"
    )
    diagnostic_out.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(period_rows).to_csv(
        diagnostic_out / "period_log.csv", index=False
    )
    print("Diagnostic log saved to:", diagnostic_out.resolve())

    runs = pd.DataFrame(rows)
    review_counts = (
        pd.DataFrame(period_rows)
        .groupby(["seed", "scenario", "method"])["review_performed"]
        .sum().rename("decision_reviews").reset_index()
    )
    runs = runs.merge(
        review_counts, on=["seed", "scenario", "method"],
        validate="one_to_one"
    )

    summary = runs.groupby(["scenario", "method"]).agg(
        runs=("seed", "size"),
        any_alert_rate=("any_alert", "mean"),
        mean_alerts=("alerts", "mean"),
        mean_decision_reviews=("decision_reviews", "mean"),
        mean_prechange_alerts=("prechange_alerts", "mean"),
        change_detection_rate=("change_detected", "mean"),
        mean_change_delay=("change_detection_delay", "mean"),
        mean_prechange_regret=("prechange_regret", "mean"),
        mean_postchange_regret=("postchange_regret", "mean"),
        mean_harmful_windows=("harmful_treatment_windows", "mean"),
    ).reset_index()

    shifted = runs.loc[runs.scenario == "response_shift"]
    wide = shifted.pivot(
        index="seed", columns="method",
        values="postchange_regret"
    )

    rng = np.random.default_rng(42)
    comparisons = []

    for a, b in (("M2", "M0"), ("M2", "M1"), ("M1", "M0")):
        differences = (wide[a] - wide[b]).to_numpy()
        bootstrap = rng.choice(
            differences,
            size=(5000, len(differences)),
            replace=True
        ).mean(axis=1)

        comparisons.append({
            "comparison": f"{a} minus {b}",
            "mean_regret_difference": differences.mean(),
            "ci_low": np.quantile(bootstrap, 0.025),
            "ci_high": np.quantile(bootstrap, 0.975),
        })

    intervals = pd.DataFrame(comparisons)
    runs.to_csv(OUT / "runs.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)
    intervals.to_csv(OUT / "paired_intervals.csv", index=False)

    pd.DataFrame([
        {"method": m, "threshold": thresholds[m]}
        for m in METHODS
    ]).to_csv(OUT / "thresholds.csv", index=False)

    print("\nSUMMARY")
    print(summary.round(4).to_string(index=False))
    print("\nPAIRED REGRET DIFFERENCES")
    print(intervals.round(4).to_string(index=False))
    print("\nSaved to:", OUT.resolve())
    print("Stable any_alert_rate estimates held-out false alarms.")
    print("Delay averages include detected runs only.")
    print("Intervals are exploratory and not multiplicity-adjusted.")
    print("No causal ML, explanation or production claims yet.")


if __name__ == "__main__":
    main()
