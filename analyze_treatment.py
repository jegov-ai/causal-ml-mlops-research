from pathlib import Path
ROOT = Path(__file__).resolve().parent

# Project 1: Causal ML + MLOps Research
# Component 3: Average Treatment Effect (ATE)

import pandas as pd

# Load our customer dataset
data = pd.read_csv(ROOT / "customers.csv")

# Separate customers into two groups
treatment = data[data["discount"] == 1]
control = data[data["discount"] == 0]

# Calculate average spending for each group
treatment_mean = treatment["purchase_amount"].mean()
control_mean = control["purchase_amount"].mean()

# Estimate the Average Treatment Effect
ate = treatment_mean - control_mean

# Display the results
print("CAUSAL ANALYSIS REPORT")
print("----------------------")

print("Treatment group customers:", len(treatment))
print("Control group customers:", len(control))

print("Average treatment spending:", round(treatment_mean, 2))
print("Average control spending:", round(control_mean, 2))

print("Estimated ATE:", round(ate, 2))

# Compare our estimate with the known simulated effect
true_ate = data["true_effect"].mean()
print("Known average true effect:", round(true_ate, 2))
