import pandas as pd
import numpy as np

# Generate reproducible simulated customer data
rng = np.random.default_rng(42)

n_customers = 1000

customers = pd.DataFrame({
    "customer_id": range(1, n_customers + 1),
    "group": rng.choice(["A", "B"], size=n_customers),
    "discount": rng.choice([0, 1], size=n_customers)
})

print(customers.head())
print("Total customers:", len(customers))

# Simulate profit without a discount
customers["profit_without_discount"] = rng.normal(
    loc=40,
    scale=8,
    size=n_customers
).round(2)

# Simulate the effect of giving a discount
customers["true_treatment_effect"] = np.where(
    customers["group"] == "A",
    20,
    -10
)

# Calculate profit if a discount is given
customers["profit_with_discount"] = (
    customers["profit_without_discount"]
    + customers["true_treatment_effect"]
)

print(customers.head())

# Simulate treatment effects after a change
customers["effect_after_shift"] = np.where(
    customers["group"] == "A",
    -10,
    -10
)

# Compare treatment effects before and after
customers["effect_change"] = (
    customers["effect_after_shift"]
    - customers["true_treatment_effect"]
)

print("\nTreatment Effect Changes:")
print(customers[
    ["group", "true_treatment_effect",
     "effect_after_shift", "effect_change"]
].head())

# Monitor treatment-effect changes by subgroup
print("\nSubgroup Monitoring Results:")

for group in ["A", "B"]:
    group_data = customers[customers["group"] == group]

    before = group_data["true_treatment_effect"].mean()
    after = group_data["effect_after_shift"].mean()

    if before > 0 and after < 0:
        print(f"ALERT: Harmful change detected in Group {group}")
    else:
        print(f"Group {group}: No positive-to-negative change detected")

customers.to_csv("paper1_experiments/simulated_customers.csv", index=False)
print("Customer dataset saved successfully!")

# Select the outcome actually observed
customers["observed_profit"] = np.where(
    customers["discount"] == 1,
    customers["profit_with_discount"],
    customers["profit_without_discount"]
)

# Save the updated dataset
customers.to_csv(
    "paper1_experiments/simulated_customers.csv",
    index=False
)

print("\nObserved Outcomes:")
print(customers[
    ["group", "discount", "observed_profit"]
].head())