
import numpy as np
import pandas as pd
from pathlib import Path

OUT = Path("paper1_experiments")
OUT.mkdir(exist_ok=True)

PERIODS = 12
N = 800
BUDGET = 2

def effect(period, group, harmful=True):
    if group == "B":
        return 15.0
    if not harmful or period <= 5:
        return 20.0
    return 20.0 - 6.0 * (period - 5)

def simulate(seed, harmful=True):
    rng = np.random.default_rng(seed)
    rows = []
    for period in range(1, PERIODS + 1):
        group = rng.choice(["A", "B"], N)
        treatment = rng.integers(0, 2, N)
        age = rng.normal(40, 12, N)
        spending = rng.normal(100, 20, N)
        baseline = 40 + .12 * (age - 40) + .04 * (spending - 100)
        effects = np.where(group == "A",
                           effect(period, "A", harmful), 15.0)
        outcome = baseline + treatment * effects + rng.normal(0, 12, N)
        rows.append(pd.DataFrame({
            "period": period, "group": group,
            "treatment": treatment, "outcome": outcome
        }))
    return pd.concat(rows, ignore_index=True)

def get_signals(data):
    baseline = data.loc[data.period == 1, "outcome"].mean()
    first_effects = {}
    rows = []

    for period, frame in data.groupby("period"):
        drift = abs(frame.outcome.mean() - baseline)
        for group in ["A", "B"]:
            sub = frame.loc[frame.group == group]
            treated = sub.loc[sub.treatment == 1, "outcome"].mean()
            control = sub.loc[sub.treatment == 0, "outcome"].mean()
            estimated = treated - control

            if group not in first_effects:
                first_effects[group] = estimated

            change = abs(estimated - first_effects[group])
            rows.append({
                "period": period, "group": group,
                "M0": drift,
                "M1": -estimated,
                "M2": max(-estimated, change)
            })

    return pd.DataFrame(rows)

# Calibrate thresholds on separate no-harm simulations.
calibration = pd.concat(
    [get_signals(simulate(seed, False))
     for seed in range(1000, 1040)],
    ignore_index=True
)

thresholds = {
    method: calibration[method].quantile(.99)
    for method in ["M0", "M1", "M2"]
}

def evaluate(seed):
    signals = get_signals(simulate(seed))
    results = []

    for method in ["M0", "M1", "M2"]:
        disabled = set()
        pending = set()
        alerts = 0
        false_alerts = 0
        regret = 0.0
        detected = None

        for period in range(1, PERIODS + 1):
            disabled.update(pending)
            pending.clear()

            for group in ["A", "B"]:
                actual = group not in disabled
                optimal = effect(period, group) > 0
                if actual != optimal:
                    regret += abs(effect(period, group)) / 2

            if alerts >= BUDGET:
                continue

            frame = signals[signals.period == period]

            if method == "M0":
                candidates = [("ALL", frame.M0.iloc[0])]
            else:
                candidates = list(zip(frame.group, frame[method]))
                candidates.sort(key=lambda x: x[1], reverse=True)

            for target, score in candidates:
                if alerts >= BUDGET:
                    break
                if score <= thresholds[method]:
                    continue

                targets = {"A", "B"} if target == "ALL" else {target}
                if targets.issubset(disabled | pending):
                    continue

                alerts += 1
                pending.update(targets)

                harmful_alert = any(
                    effect(period, g) < 0 for g in targets
                )

                if not harmful_alert:
                    false_alerts += 1
                elif detected is None:
                    detected = period

        results.append({
            "seed": seed,
            "method": method,
            "regret": regret,
            "alerts": alerts,
            "false_alerts": false_alerts,
            "detected_period": detected
        })

    return results

# Repeat experiments with 100 independent seeds.
records = []
for seed in range(100, 200):
    records.extend(evaluate(seed))

runs = pd.DataFrame(records)

summary = runs.groupby("method").agg(
    mean_regret=("regret", "mean"),
    std_regret=("regret", "std"),
    mean_alerts=("alerts", "mean"),
    mean_false_alerts=("false_alerts", "mean"),
    detection_rate=("detected_period", lambda x: x.notna().mean())
)

# Paired bootstrap confidence intervals.
wide = runs.pivot(index="seed", columns="method", values="regret")
rng = np.random.default_rng(42)
comparisons = []

for a, b in [("M1", "M0"), ("M2", "M0"), ("M2", "M1")]:
    differences = (wide[a] - wide[b]).to_numpy()
    bootstrap = rng.choice(
        differences,
        size=(5000, len(differences)),
        replace=True
    ).mean(axis=1)

    comparisons.append({
        "comparison": f"{a} minus {b}",
        "mean_difference": differences.mean(),
        "ci95_low": np.quantile(bootstrap, .025),
        "ci95_high": np.quantile(bootstrap, .975)
    })

runs.to_csv(OUT / "replicated_runs.csv", index=False)
summary.to_csv(OUT / "replicated_summary.csv")
pd.DataFrame(comparisons).to_csv(
    OUT / "replicated_confidence_intervals.csv",
    index=False
)

print("\n100-SEED PILOT RESULTS")
print(summary)
print("\n95% CONFIDENCE INTERVALS")
print(pd.DataFrame(comparisons))
print("\nResults saved successfully.")
print("NOTE: M2 currently uses an effect-stability proxy.")
print("Formal explanation-stability monitoring remains to be implemented.")
