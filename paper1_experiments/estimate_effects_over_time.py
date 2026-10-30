
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
results = []

for period in range(1, 11):
    for group in ["A", "B"]:
        n = 500

        # Randomly assign discounts
        discount = rng.integers(0, 2, size=n)

        # Simulate customer baseline profit
        baseline = rng.normal(40, 8, size=n)

        # True treatment effects in our simulation
        if group == "A":
            true_effect = 20 if period <= 5 else 20 - 6 * (period - 5)
        else:
            true_effect = 15

        # Observe profit under assigned treatment
        observed_profit = baseline + discount * true_effect

        # Estimate the treatment effect
        estimated_effect = (
            observed_profit[discount == 1].mean()
            - observed_profit[discount == 0].mean()
        )

        results.append({
            "period": period,
            "group": group,
            "estimated_effect": estimated_effect,
            "true_effect": true_effect
        })

data = pd.DataFrame(results)

print(data.round(2))

data.to_csv(
    "paper1_experiments/effects_over_time.csv",
    index=False
)

print("\nTime-based estimates saved successfully!")
