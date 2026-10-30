
import numpy as np
import pandas as pd

path = "paper1_experiments/"
data = pd.read_csv(path + "integrated_metrics.csv")

paired = data.pivot(
    index="seed",
    columns="method",
    values="cumulative_regret"
).dropna()

# Positive difference means M1 has lower regret
difference = paired["M0"] - paired["M1"]

rng = np.random.default_rng(42)

bootstrap = np.array([
    rng.choice(
        difference.to_numpy(),
        size=len(difference),
        replace=True
    ).mean()
    for _ in range(5000)
])

lower, upper = np.percentile(
    bootstrap, [2.5, 97.5]
)

print("\nPAPER 1 STATISTICAL VALIDATION")
print("Simulation runs:", len(difference))
print("M0 mean regret:", round(paired["M0"].mean(), 2))
print("M1 mean regret:", round(paired["M1"].mean(), 2))
print("Mean regret difference:", round(difference.mean(), 2))
print("95% bootstrap CI:", round(lower, 2), round(upper, 2))
print("M1 lower-regret runs:", int((difference > 0).sum()))

summary = pd.DataFrame([{
    "n_runs": len(difference),
    "mean_M0_regret": paired["M0"].mean(),
    "mean_M1_regret": paired["M1"].mean(),
    "mean_difference": difference.mean(),
    "ci_lower": lower,
    "ci_upper": upper
}])

summary.to_csv(
    path + "statistical_summary.csv",
    index=False
)

print("\nStatistical results saved.")
