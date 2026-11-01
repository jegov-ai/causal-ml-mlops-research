from pathlib import Path
ROOT = Path(__file__).resolve().parent

# Project 1: Causal ML + MLOps Research
# Component 2: Data Validation

import pandas as pd
import numpy as np

# Load the dataset generated in Step 11
data = pd.read_csv(ROOT / "customers.csv")

required = ["age", "previous_spending", "discount", "purchase_amount", "true_effect"]
missing_columns = sorted(set(required) - set(data.columns))
if missing_columns:
    raise SystemExit(f"VALIDATION FAILED: missing columns {missing_columns}")
try:
    numeric = data[required].apply(pd.to_numeric, errors="raise")
except (ValueError, TypeError) as exc:
    raise SystemExit(f"VALIDATION FAILED: nonnumeric data: {exc}")
finite = bool(np.isfinite(numeric.to_numpy(dtype=float)).all())
integer_ages = bool((numeric.age % 1 == 0).all())
both_arms = set(numeric.discount.unique()) == {0, 1}
valid_truth = bool(np.array_equal(numeric.true_effect, np.where(numeric.age < 35, 40.0, 15.0)))

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
    len(data) == 1000
    and finite
    and integer_ages
    and both_arms
    and valid_truth
    and missing.sum() == 0
    and duplicates == 0
    and valid_discounts
    and valid_ages
    and valid_spending
)

if passed:
    print("\nVALIDATION PASSED")
else:
    raise SystemExit("VALIDATION FAILED: expected 1,000 finite records, both arms, integer ages and declared synthetic effects.")
