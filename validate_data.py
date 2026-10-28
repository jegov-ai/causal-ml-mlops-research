
# Project 1: Causal ML + MLOps Research
# Component 2: Data Validation

import pandas as pd

# Load the dataset generated in Step 11
data = pd.read_csv("customers.csv")

print("DATA VALIDATION REPORT")
print("----------------------")

# Check the number of customer records
print("Total customers:", len(data))

# Check for missing values
missing = data.isnull().sum()
print("\nMissing values:")
print(missing)

# Check for duplicate records
duplicates = data.duplicated().sum()
print("\nDuplicate records:", duplicates)

# Check discount values
valid_discounts = data["discount"].isin([0, 1]).all()
print("\nDiscount values valid:", valid_discounts)

# Check that ages are reasonable
valid_ages = data["age"].between(18, 65).all()
print("Customer ages valid:", valid_ages)

# Check spending values
valid_spending = (data["previous_spending"] >= 0).all()
print("Previous spending valid:", valid_spending)

# Overall validation result
passed = (
    missing.sum() == 0
    and duplicates == 0
    and valid_discounts
    and valid_ages
    and valid_spending
)

if passed:
    print("\nVALIDATION PASSED")
else:
    print("\nVALIDATION FAILED")
