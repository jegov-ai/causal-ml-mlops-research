
import numpy as np
import pandas as pd
from pathlib import Path

OUT = Path("paper1_experiments")
OUT.mkdir(exist_ok=True)

PERIODS = 12
N_PER_GROUP = 400
SEEDS = 100
HARM_START = 9

def true_effect(period, group, harmful=True):
    if group == "B":
        return 15.0
    if not harmful or period <= 5:
        return 20.0
    return 20.0 - 6.0 * (period - 5)

def generate_signals(seed, harmful=True):
    rng = np.random.default_rng(seed)
    records = []
    initial = {}

    for period in range(1, PERIODS + 1):
        for group in ["A", "B"]:
            treatment = rng.integers(0, 2, N_PER_GROUP)
            baseline = rng.normal(40, 8, N_PER_GROUP)
            noise = rng.normal(0, 12, N_PER_GROUP)

            outcome = (
                baseline
                + treatment * true_effect(period, group, harmful)
                + noise
            )

            treated = outcome[treatment == 1].mean()
            control = outcome[treatment == 0].mean()
            estimated = treated - control

            if group not in initial:
                initial[group] = estimated

            decline = initial[group] - estimated

            records.append({
                "period": period,
                "group": group,
                "estimated_effect": estimated,
                "decline": decline,
                "true_effect": true_effect(
                    period, group, harmful
                )
            })

    return pd.DataFrame(records)

# Set the warning threshold using independent
# no-harm simulations, not the test data.
null_maxima = []

for seed in range(1000, 1200):
    null_data = generate_signals(seed, harmful=False)
    null_maxima.append(null_data["decline"].max())

WARNING_THRESHOLD = float(np.quantile(null_maxima, 0.95))

def evaluate(seed, policy):
    signals = generate_signals(seed)
    results = []

    for group in ["A", "B"]:
        frame = signals[signals.group == group]
        warned = False
        warning_period = None
        stop_period = None

        for row in frame.itertuples():
            if not warned and row.decline > WARNING_THRESHOLD:
                warned = True
                warning_period = row.period

                if policy == "immediate":
                    stop_period = row.period + 1

            if (
                policy == "warning_first"
                and warned
                and stop_period is None
                and row.estimated_effect < 0
            ):
                stop_period = row.period + 1

        regret = 0.0

        for period in range(1, PERIODS + 1):
            effect = true_effect(period, group)
            treatment_active = (
                stop_period is None or period < stop_period
            )
            optimal_active = effect > 0

            if treatment_active != optimal_active:
                regret += abs(effect) / 2.0

        harmful_stop = (
            group == "A"
            and stop_period is not None
            and stop_period >= HARM_START
        )

        premature_stop = (
            stop_period is not None
            and (
                group == "B"
                or stop_period < HARM_START
            )
        )

        results.append({
            "seed": seed,
            "policy": policy,
            "group": group,
            "warning_period": warning_period,
            "stop_period": stop_period,
            "regret": regret,
            "premature_stop": int(premature_stop),
            "harmful_stop": int(harmful_stop)
        })

    return results

records = []

for seed in range(100, 100 + SEEDS):
    for policy in ["immediate", "warning_first"]:
        records.extend(evaluate(seed, policy))

runs = pd.DataFrame(records)

# Aggregate regret across the two groups per seed.
totals = runs.groupby(
    ["seed", "policy"], as_index=False
).agg(
    cumulative_regret=("regret", "sum"),
    premature_stops=("premature_stop", "sum"),
    harmful_stops=("harmful_stop", "sum")
)

summary = totals.groupby("policy").agg(
    mean_regret=("cumulative_regret", "mean"),
    std_regret=("cumulative_regret", "std"),
    mean_premature_stops=("premature_stops", "mean"),
    harmful_stop_rate=("harmful_stops", "mean")
)

# Paired bootstrap comparison.
wide = totals.pivot(
    index="seed",
    columns="policy",
    values="cumulative_regret"
)

difference = (
    wide["warning_first"] - wide["immediate"]
).to_numpy()

rng = np.random.default_rng(42)
bootstrap = rng.choice(
    difference,
    size=(5000, len(difference)),
    replace=True
).mean(axis=1)

comparison = pd.DataFrame([{
    "comparison": "warning_first minus immediate",
    "mean_difference": difference.mean(),
    "ci95_low": np.quantile(bootstrap, 0.025),
    "ci95_high": np.quantile(bootstrap, 0.975)
}])

runs.to_csv(
    OUT / "m2_warning_policy_runs.csv", index=False
)
totals.to_csv(
    OUT / "m2_warning_policy_totals.csv", index=False
)
summary.to_csv(
    OUT / "m2_warning_policy_summary.csv"
)
comparison.to_csv(
    OUT / "m2_warning_policy_confidence_interval.csv",
    index=False
)

print("\nM2 WARNING POLICY EXPERIMENT")
print("Calibrated warning threshold:",
      round(WARNING_THRESHOLD, 3))

print("\n100-SEED RESULTS")
print(summary.to_string())

print("\nPAIRED 95% CONFIDENCE INTERVAL")
print(comparison.to_string(index=False))

print("\nResults saved.")
print("NOTE: This tests effect-decline warnings,")
print("not formal explanation stability.")
print("This is a controlled policy diagnostic,")
print("not final scientific validation.")
