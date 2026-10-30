
import pandas as pd

data = pd.read_csv(
    "paper1_experiments/effects_over_time.csv"
)

data = data.sort_values(["period", "group"])

# Same initial policy for both methods:
# Give discounts to both groups.
# After an alert, stop discounts for that group
# starting from the NEXT period.

def evaluate_policy(method):
    active = {group: True for group in data["group"].unique()}
    records = []

    for period, current in data.groupby("period", sort=True):
        overall_estimate = current["estimated_effect"].mean()

        # Apply the decisions made before this period
        for _, row in current.iterrows():
            group = row["group"]
            true_effect = row["true_effect"]

            chosen_value = true_effect if active[group] else 0
            optimal_value = max(true_effect, 0)

            regret = optimal_value - chosen_value

            records.append({
                "method": method,
                "period": period,
                "group": group,
                "regret": regret
            })

        # Monitoring alerts affect the NEXT period
        if method == "M0":
            if overall_estimate < 0:
                for group in active:
                    active[group] = False

        elif method == "M1":
            for _, row in current.iterrows():
                if row["estimated_effect"] < 0:
                    active[row["group"]] = False

    return pd.DataFrame(records)


results = pd.concat([
    evaluate_policy("M0"),
    evaluate_policy("M1")
])

summary = (
    results.groupby("method")["regret"]
    .sum()
    .reset_index()
)

print("\nCUMULATIVE POLICY REGRET")
print(summary.to_string(index=False))

results.to_csv(
    "paper1_experiments/policy_regret_results.csv",
    index=False
)
