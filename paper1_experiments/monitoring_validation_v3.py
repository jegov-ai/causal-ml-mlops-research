"""Controlled monitoring validation; synthetic randomized data only.
Not a complete causal-ML/MLOps or explainability validation.
"""

from pathlib import Path
import numpy as np
import pandas as pd

OUT = Path("paper1_experiments/monitoring_validation_v3_results")

PERIODS = 12
CHANGE_PERIOD = 6
N_PER_GROUP = 400
ALERT_BUDGET = 2
CALIBRATION_RUNS = 500
TEST_RUNS = 200
METHODS = ("M0", "M1", "M2")
SCENARIOS = ("stable", "response_shift", "opposing_shift")
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

    if scenario == "opposing_shift" and period >= CHANGE_PERIOD:
        effect = np.where(group == 0, -10.0, 45.0)

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


# EXPLORATORY DESIGN, fixed before running this extension:
# 200 paired fresh seeds; 500 calibration runs; budgets 2/4/8.
# Equal group weights; two issued alerts maximum; reviews are separate.
# Delay starts at period 6; detection means any issued post-change alert.
# Missed events have missing delay and are reported separately.
# Report 95% paired bootstrap intervals descriptively, no significance claims.
# No primary budget selected: report the complete budget grid.
BUDGETS = (2, 4, 8)


def evaluate(signals, estimates, errors, truths, thresholds,
             seed, scenario, budget, log):
    results = []
    for method in METHODS:
        active = np.array([True, True])
        alerts = 0
        reviews = 0
        started = False
        detected = None
        before = 0.0
        after = 0.0
        harm_windows = 0
        for index in range(PERIODS):
            period = index + 1
            truth = truths[index]
            regret = float((np.maximum(truth, 0)
                            - np.where(active, truth, 0)).mean())
            if period < CHANGE_PERIOD:
                before += regret
            else:
                after += regret
            harm_windows += int(np.any(active & (truth < 0)))
            issue = (alerts < ALERT_BUDGET
                     and signals[method][index] > thresholds[method])
            if issue:
                alerts += 1
                started = True
                if (scenario != "stable" and period >= CHANGE_PERIOD
                        and detected is None):
                    detected = period
            review = started and reviews < budget
            previous = active.copy()
            if review:
                reviews += 1
                lower = estimates[index] - 1.96 * errors[index]
                upper = estimates[index] + 1.96 * errors[index]
                active = active.copy()
                active[upper < 0] = False
                active[lower > 0] = True
            assert reviews <= budget
            assert alerts <= ALERT_BUDGET
            assert regret >= -1e-10
            if not review:
                assert np.array_equal(active, previous)
            log.append(dict(
                seed=seed, scenario=scenario, review_budget=budget,
                method=method, period=period,
                score=signals[method][index], threshold=thresholds[method],
                alert_issued=bool(issue), review_performed=bool(review),
                reviews_used=reviews,
                active_A_before=bool(previous[0]),
                active_B_before=bool(previous[1]),
                active_A_next=bool(active[0]),
                active_B_next=bool(active[1]),
                true_effect_A=truth[0], true_effect_B=truth[1],
                estimated_effect_A=estimates[index, 0],
                estimated_effect_B=estimates[index, 1],
                period_regret=regret,
            ))
        results.append(dict(
            seed=seed, scenario=scenario, review_budget=budget,
            method=method, alerts=alerts, any_alert=int(alerts > 0),
            decision_reviews=reviews,
            change_detected=(int(detected is not None)
                             if scenario != "stable" else np.nan),
            missed_change=(int(detected is None)
                           if scenario != "stable" else np.nan),
            detection_delay=(detected - CHANGE_PERIOD
                             if detected is not None else np.nan),
            prechange_regret=before, postchange_regret=after,
            harmful_treatment_windows=harm_windows,
        ))
    return results


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    print("Exploratory v3: calibrating on independent stable runs...", flush=True)
    scale_vectors = np.concatenate([
        stream(s, "stable")[0] for s in range(4000, 4100)
    ])
    center = scale_vectors.mean(axis=0)
    scale = np.maximum(scale_vectors.std(axis=0, ddof=1), 1e-8)
    maxima = {m: [] for m in METHODS}
    for seed in range(5000, 5000 + CALIBRATION_RUNS):
        vectors, _, _, _ = stream(seed, "stable")
        signal = scores(vectors, center, scale)
        for m in METHODS:
            maxima[m].append(signal[m].max())
    thresholds = {
        m: float(np.quantile(maxima[m], .95, method="higher"))
        for m in METHODS
    }
    print("Thresholds:", thresholds, flush=True)
    rows, log = [], []
    for scenario in SCENARIOS:
        for seed in range(30000, 30000 + TEST_RUNS):
            vectors, estimates, errors, truths = stream(seed, scenario)
            if scenario == "opposing_shift":
                assert np.allclose(truths.mean(axis=1), 17.5)
                assert np.all(truths[5:, 0] < 0)
            signal = scores(vectors, center, scale)
            for budget in BUDGETS:
                rows.extend(evaluate(
                    signal, estimates, errors, truths, thresholds,
                    seed, scenario, budget, log
                ))
        print("Completed:", scenario, flush=True)
    runs = pd.DataFrame(rows)
    summary = runs.groupby(["scenario", "review_budget", "method"]).agg(
        runs=("seed", "size"), any_alert_rate=("any_alert", "mean"),
        mean_reviews=("decision_reviews", "mean"),
        change_detection_rate=("change_detected", "mean"),
        missed_change_rate=("missed_change", "mean"),
        mean_detection_delay=("detection_delay", "mean"),
        mean_prechange_regret=("prechange_regret", "mean"),
        mean_postchange_regret=("postchange_regret", "mean"),
        mean_harmful_windows=("harmful_treatment_windows", "mean"),
    ).reset_index()
    rng = np.random.default_rng(73)
    comparisons = []
    for scenario in SCENARIOS:
        if scenario == "stable":
            continue
        for budget in BUDGETS:
            part = runs[(runs.scenario == scenario)
                        & (runs.review_budget == budget)]
            wide = part.pivot(index="seed", columns="method",
                              values="postchange_regret")
            for a, b in (("M2", "M0"), ("M2", "M1"), ("M1", "M0")):
                diff = (wide[a] - wide[b]).to_numpy()
                boot = rng.choice(diff, (5000, len(diff)), replace=True).mean(axis=1)
                comparisons.append(dict(
                    scenario=scenario, review_budget=budget,
                    comparison=f"{a} minus {b}", mean_difference=diff.mean(),
                    ci_low=np.quantile(boot, .025),
                    ci_high=np.quantile(boot, .975),
                ))
    intervals = pd.DataFrame(comparisons)
    runs.to_csv(OUT / "runs.csv", index=False)
    summary.to_csv(OUT / "summary.csv", index=False)
    pd.DataFrame(log).to_csv(OUT / "period_log.csv", index=False)
    intervals.to_csv(OUT / "paired_intervals.csv", index=False)
    pd.DataFrame([dict(method=m, threshold=thresholds[m])
                  for m in METHODS]).to_csv(OUT / "thresholds.csv", index=False)
    (OUT / "design.txt").write_text(
        "Exploratory v3. 200 test seeds 30000:30200; scale seeds 4000:4100; "
        "500 calibration seeds 5000:5500. All ranges exclude upper bound. "
        "Review budgets 2,4,8; alert cap 2; all budgets reported. "
        "First alert starts consecutive reviews including triggering period. "
        "12 windows, 400 per group; labels at window end; actions next window. "
        "Opposing shift: (20,15) to (-10,45) at period 6. "
        "Decision loss: sum of per-window population-average oracle-relative "
        "net-effect loss, equal group weights, zero extra treatment cost. "
        "Detection: any issued alert at/after known shift onset; "
        "delay conditional on detection. This is not harm-specific precision. "
        "95% paired bootstrap intervals are unadjusted and descriptive. "
        "Pointwise gate intervals do not guarantee sequential safety. "
        "No causal ML or explanation evaluation. No deployment feedback.\n"
    )
    print("\nSUMMARY\n", summary.round(4).to_string(index=False))
    print("\nPAIRED EXPLORATORY INTERVALS\n", intervals.round(4).to_string(index=False))
    print("\nSaved to:", OUT.resolve())
    print("All budgets reported; unadjusted descriptive intervals only.")
    print("Matched review caps do not imply identical realized workloads.")


if __name__ == "__main__":
    main()
