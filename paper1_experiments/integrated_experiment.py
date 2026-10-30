
import numpy as np
import pandas as pd
from pathlib import Path

OUT = Path("paper1_experiments")
OUT.mkdir(exist_ok=True)

SEEDS = range(20)
PERIODS = 12
N = 300
BUDGET = 2


def run_experiment(seed):
    rng = np.random.default_rng(seed)

    policies = {
        "M0": {"A": True, "B": True},
        "M1": {"A": True, "B": True}
    }

    alerts = {"M0": 0, "M1": 0}
    regrets = {"M0": 0.0, "M1": 0.0}
    first_alert = {"M0": None, "M1": None}
    observations = []

    for period in range(1, PERIODS + 1):
        current = []

        for group in ["A", "B"]:
            discount = rng.integers(0, 2, N)
            baseline = rng.normal(40, 8, N)

            if group == "A":
                true_effect = (
                    20 if period <= 5
                    else 20 - 6 * (period - 5)
                )
            else:
                true_effect = 15

            observed_profit = (
                baseline + discount * true_effect
            )

            estimated_effect = (
                observed_profit[discount == 1].mean()
                - observed_profit[discount == 0].mean()
            )

            current.append((
                group,
                true_effect,
                estimated_effect,
                observed_profit.mean()
            ))

        # Calculate regret before applying new alerts
        for method in policies:
            for group, effect, _, _ in current:
                chosen = (
                    effect if policies[method][group] else 0
                )
                optimal = max(effect, 0)

                regrets[method] += optimal - chosen

        # M0: simple overall outcome-drift baseline
        overall = np.mean([r[3] for r in current])

        if period == 1:
            reference = overall

        m0_signal = abs(overall - reference) > 8

        if (
            m0_signal
            and alerts["M0"] < BUDGET
            and any(policies["M0"].values())
        ):
            alerts["M0"] += 1

            if first_alert["M0"] is None:
                first_alert["M0"] = period

            for group in policies["M0"]:
                policies["M0"][group] = False

        # M1: subgroup-aware causal monitoring
        for group, truth, estimate, observed in current:
            if (
                estimate < 0
                and policies["M1"][group]
                and alerts["M1"] < BUDGET
            ):
                alerts["M1"] += 1
                policies["M1"][group] = False

                if first_alert["M1"] is None:
                    first_alert["M1"] = period

            observations.append({
                "seed": seed,
                "period": period,
                "group": group,
                "true_effect": truth,
                "estimated_effect": estimate,
                "observed_mean": observed
            })

    summary = []

    for method in ["M0", "M1"]:
        alert_period = first_alert[method]

        delay = (
            alert_period - 9
            if alert_period is not None
            and alert_period >= 9
            else np.nan
        )

        summary.append({
            "seed": seed,
            "method": method,
            "alerts": alerts[method],
            "detection_delay": delay,
            "cumulative_regret": regrets[method]
        })

    return observations, summary


all_observations = []
all_results = []

for seed in SEEDS:
    observations, results = run_experiment(seed)
    all_observations.extend(observations)
    all_results.extend(results)

pd.DataFrame(all_observations).to_csv(
    OUT / "integrated_observations.csv",
    index=False
)

metrics = pd.DataFrame(all_results)

metrics.to_csv(
    OUT / "integrated_metrics.csv",
    index=False
)

print("\nINTEGRATED EXPERIMENT RESULTS")
print(
    metrics.groupby("method")[
        ["alerts", "detection_delay", "cumulative_regret"]
    ].mean().round(2)
)

print("\n20 simulation runs completed.")
print("Research result files saved.")
