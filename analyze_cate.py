from pathlib import Path
ROOT = Path(__file__).resolve().parent

# Project 1: Causal ML + MLOps Research
# Component 4: CATE Analysis by Age Group

import pandas as pd

# Load our existing customer dataset
data = pd.read_csv(ROOT / "customers.csv")

# Create two age groups
young = data[data["age"] < 35]
older = data[data["age"] >= 35]

# Calculate the estimated treatment effect for each group
def calculate_cate(group):
    treatment = group[group["discount"] == 1]
    control = group[group["discount"] == 0]

    treatment_mean = treatment["purchase_amount"].mean()
    control_mean = control["purchase_amount"].mean()

    return treatment_mean - control_mean

# Calculate CATE for each age group
young_cate = calculate_cate(young)
older_cate = calculate_cate(older)

# Display results
print("CATE ANALYSIS REPORT")
print("--------------------")

print("Customers under 35:", len(young))
print("Customers aged 35 and above:", len(older))

print("\nEstimated CATE for under 35:", round(young_cate, 2))
print("Estimated CATE for 35 and above:", round(older_cate, 2))

# Compare estimates with known simulated effects
print("\nKnown true effect for under 35: RM40")
print("Known true effect for 35 and above: RM15")

print("\nCATE analysis completed!")
