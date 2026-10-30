import pandas as pd

# Load simulated customer data
data = pd.read_csv(
    "paper1_experiments/simulated_customers.csv"
)

print("Estimated Treatment Effects")

for group, group_data in data.groupby("group"):

    treated = group_data[group_data["discount"] == 1]
    untreated = group_data[group_data["discount"] == 0]

    treated_profit = treated["observed_profit"].mean()
    untreated_profit = untreated["observed_profit"].mean()

    estimated_effect = treated_profit - untreated_profit

    print(f"Group {group}: RM {estimated_effect:.2f}")

print("\nEstimation Accuracy")

for group, group_data in data.groupby("group"):
    treated = group_data[group_data["discount"] == 1]
    untreated = group_data[group_data["discount"] == 0]

    estimated = (
        treated["observed_profit"].mean()
        - untreated["observed_profit"].mean()
    )

    true_effect = group_data["true_treatment_effect"].mean()

    error = abs(estimated - true_effect)

    print(
        f"Group {group}: "
        f"True = RM{true_effect:.2f}, "
        f"Estimated = RM{estimated:.2f}, "
        f"Error = RM{error:.2f}"
    )