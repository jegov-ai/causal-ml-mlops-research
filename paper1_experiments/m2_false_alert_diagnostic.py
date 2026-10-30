
import numpy as np
import pandas as pd
from pathlib import Path

# Independent diagnostic; does not change previous experiments.
OUT = Path("paper1_experiments")
records = []

for seed in range(100, 200):
    rng = np.random.default_rng(seed)
    initial = {}

    for period in range(1, 13):
        for group in ("A", "B"):
            true_effect = (
                20 - 6 * max(0, period - 5)
                if group == "A" else 15
            )

            # Simulate randomized treatment and control groups.
            treatment = rng.integers(0, 2, 400)
            outcome = (
                40 + treatment * true_effect
                + rng.normal(0, 12, 400)
            )

            estimated = (
                outcome[treatment == 1].mean()
                - outcome[treatment == 0].mean()
            )

            if group not in initial:
                initial[group] = estimated

            instability = (
                0.5 * abs(estimated - initial[group])
            )

            records.append({
                "seed": seed,
                "period": period,
                "group": group,
                "true_effect": true_effect,
                "estimated_effect": estimated,
                "instability_score": instability,
                "harmful": true_effect < 0,
                "positive_but_unstable": (
                    true_effect > 0 and instability > 5
                )
            })

df = pd.DataFrame(records)

summary = df.groupby("group").agg(
    mean_instability=("instability_score", "mean"),
    maximum_instability=("instability_score", "max"),
    positive_but_unstable_count=(
        "positive_but_unstable", "sum"
    )
)

df.to_csv(OUT / "m2_diagnostic_details.csv", index=False)
summary.to_csv(OUT / "m2_diagnostic_summary.csv")

print("\nM2 INSTABILITY DIAGNOSTIC")
print(summary)

print("\nPOSITIVE EFFECT BUT HIGH INSTABILITY:")
print(df[df.positive_but_unstable].groupby(
    ["period", "group"]
).size())

print("\nDiagnostic results saved.")
print("Note: this diagnostic is separate from the v2 experiment.")
