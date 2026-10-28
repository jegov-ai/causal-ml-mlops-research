
# Project 1: Causal ML + MLOps Research
# Component 1: Synthetic data generation

import numpy as np
import pandas as pd

# Use a fixed seed so results can be reproduced
rng = np.random.default_rng(42)

# Number of simulated customers
n_customers = 1000

# Generate customer characteristics
age = rng.integers(18, 66, size=n_customers)
previous_spending = rng.normal(200, 60, n_customers)
previous_spending = np.clip(previous_spending, 0, None)

# Randomly assign a discount to approximately half
discount = rng.binomial(1, 0.5, n_customers)

# Define the true discount effect for each customer
true_effect = np.where(age < 35, 40.0, 15.0)

# Generate purchasing outcomes
noise = rng.normal(0, 20, n_customers)
baseline = 50 + 0.4 * previous_spending + noise
purchase_amount = baseline + discount * true_effect

# Create a dataset
data = pd.DataFrame({
    "age": age,
    "previous_spending": previous_spending,
    "discount": discount,
    "purchase_amount": purchase_amount,
    "true_effect": true_effect
})

# Save the dataset
data.to_csv("customers.csv", index=False)

# Display basic information
print("Dataset generated successfully!")
print("Number of customers:", len(data))
print("Discount assignment counts:")
print(data["discount"].value_counts())
print("First five customers:")
print(data.head())
