
import numpy as np
import pandas as pd
from pathlib import Path

OUT = Path("paper1_experiments")
PERIODS = 12
BUDGET = 2
REPETITIONS = 100

def true_effect(period, group, harmful=True):
    if group == "B":
        return 15.0
    if not harmful or period <= 5:
        return 20.0
    return 20.0 - 6.0 * (period - 5)

def simulate(seed, harmful=True):
    rng = np.random.default_rng(seed)
    records = []

    for period in range(1, PERIODS + 1):
        for group in ("A", "B"):
            n = 400
            treatment = rng.integers(0, 2, n)
            baseline = rng.normal(40, 12, n)
            outcome = (
                baseline
                + treatment * true_effect(period, group, harmful)
            )
            records.append(pd.DataFrame({
                "period": period,
                "group": group,
                "treatment": treatment,
                "outcome": outcome
            }))

    return pd.concat(records, ignore_index=True)

def signals(data):
    reference = data.loc[data.period == 1, "outcome"].mean()
    initial = {}
    output = []

    for period, frame in data.groupby("period"):
        overall = frame.outcome.mean()

        for group in ("A", "B"):
            sub = frame.loc[frame.group == group]
            estimated = (
                sub.loc[sub.treatment == 1, "outcome"].mean()
                - sub.loc[sub.treatment == 0, "outcome"].mean()
            )

            if group not in initial:
                initial[group] = estimated

            output.append({
                "period": period,
                "group": group,
                "M0": reference - overall,
                "M1": -estimated,
                "M2": max(
                    -estimated,
                    0.5 * abs(estimated - initial[group])
                )
            })

    return pd.DataFrame(output)

# Independent no-harm calibration.
# Each method gets a comparable 5% run-level
# false-alarm target before deployment.
null_maxima = {"M0": [], "M1": [], "M2": []}

for seed in range(1000, 1200):
    s = signals(simulate(seed, harmful=False))
    s = s.loc[s.period > 1]

    for method in null_maxima:
        null_maxima[method].append(s[method].max())

thresholds = {
    m: max(0.0, float(np.quantile(values, 0.95)))
    for m, values in null_maxima.items()
}

print("CALIBRATED THRESHOLDS:", thresholds)

def evaluate(seed):
    s = signals(simulate(seed, harmful=True))
    results = []

    for method in ("M0", "M1", "M2"):
        disabled = set()
        pending = set()
        alert_count = 0
        false_alerts = 0
        first_detection = None
        regret = 0.0

        for period in range(1, PERIODS + 1):
            # Alerts take effect from the following period.
            disabled.update(pending)
            pending.clear()

            for group in ("A", "B"):
                effect = true_effect(period, group)
                chosen = group not in disabled
                optimal = effect > 0

                if chosen != optimal:
                    regret += abs(effect) / 2.0

            if period == 1 or alert_count >= BUDGET:
                continue

            frame = s.loc[s.period == period]

            if method == "M0":
                candidates = [("ALL", frame.M0.iloc[0])]
            else:
                candidates = list(zip(frame.group, frame[method]))
                candidates.sort(key=lambda x: x[1], reverse=True)

            for target, score in candidates:
                if alert_count >= BUDGET:
                    break

                if score <= thresholds[method]:
                    continue

                targets = (
                    {"A", "B"} if target == "ALL" else {target}
                )

                if targets.issubset(disabled | pending):
                    continue

                alert_count += 1
                pending.update(targets)

                is_true_detection = (
                    period >= 9 and "A" in targets
                )

                if is_true_detection:
                    if first_detection is None:
                        first_detection = period
                else:
                    false_alerts += 1

        results.append({
            "seed": seed,
            "method": method,
            "regret": regret,
            "alerts": alert_count,
            "false_alerts": false_alerts,
            "detected": int(first_detection is not None),
            "detection_delay": (
                first_detection - 9
                if first_detection is not None
                else np.nan
            )
        })

    return results

records = []
for seed in range(100, 100 + REPETITIONS):
    records.extend(evaluate(seed))

runs = pd.DataFrame(records)

summary = runs.groupby("method").agg(
    mean_regret=("regret", "mean"),
    mean_alerts=("alerts", "mean"),
    mean_false_alerts=("false_alerts", "mean"),
    detection_rate=("detected", "mean"),
    mean_detection_delay=("detection_delay", "mean")
)

wide = runs.pivot(
    index="seed",
    columns="method",
    values="regret"
)

rng = np.random.default_rng(42)
comparisons = []

for a, b in (
    ("M1", "M0"),
    ("M2", "M0"),
    ("M2", "M1")
):
    differences = (wide[a] - wide[b]).to_numpy()

    boot = rng.choice(
        differences,
        size=(5000, len(differences)),
        replace=True
    ).mean(axis=1)

    comparisons.append({
        "comparison": f"{a} minus {b}",
        "mean_difference": differences.mean(),
        "ci_low": np.quantile(boot, 0.025),
        "ci_high": np.quantile(boot, 0.975)
    })

runs.to_csv(
    OUT / "replicated_v2_runs.csv",
    index=False
)

summary.to_csv(
    OUT / "replicated_v2_summary.csv"
)

pd.DataFrame(comparisons).to_csv(
    OUT / "replicated_v2_confidence_intervals.csv",
    index=False
)

print("\nCORRECTED 100-SEED PILOT")
print(summary.to_string())
print("\nPAIRED CONFIDENCE INTERVALS")
print(pd.DataFrame(comparisons).to_string(index=False))
print("\nResults saved.")
print("NOTE: M2 uses effect instability, not formal explanations.")
print("These results are preliminary, not publication validation.")
