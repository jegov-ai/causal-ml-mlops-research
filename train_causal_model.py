from pathlib import Path
ROOT = Path(__file__).resolve().parent

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

# Load our existing dataset
data = pd.read_csv(ROOT / "customers.csv")

# Separate training and testing customers
train, test = train_test_split(
    data, test_size=0.2, random_state=42
)

features = ["age", "previous_spending"]

# Create two separate machine learning models
treated_model = RandomForestRegressor(
    n_estimators=100, min_samples_leaf=5, random_state=42
)

control_model = RandomForestRegressor(
    n_estimators=100, min_samples_leaf=5, random_state=42
)

# Train on customers who received a discount
treated = train[train["discount"] == 1]
treated_model.fit(
    treated[features], treated["purchase_amount"]
)

# Train on customers who did not receive a discount
control = train[train["discount"] == 0]
control_model.fit(
    control[features], control["purchase_amount"]
)

# Predict spending under both possible actions
predicted_treated = treated_model.predict(test[features])
predicted_control = control_model.predict(test[features])

# Estimate each customer's treatment effect
estimated_effect = predicted_treated - predicted_control

# Evaluate against known simulated effects
mae = mean_absolute_error(
    test["true_effect"], estimated_effect
)

print("CAUSAL ML MODEL REPORT")
print("----------------------")
print("Model: T-Learner with Random Forest")
print("Training customers:", len(train))
print("Testing customers:", len(test))
print("Estimated average effect: RM", round(estimated_effect.mean(), 2))
print("Known average true effect: RM", round(test["true_effect"].mean(), 2))
print("Treatment effect MAE: RM", round(mae, 2))

# Save trained models for future use
joblib.dump(treated_model, ROOT / "treated_model.joblib")
joblib.dump(control_model, ROOT / "control_model.joblib")

# Save evaluation results
results = test[features].copy()
results["true_effect"] = test["true_effect"]
results["estimated_effect"] = estimated_effect
results.to_csv(ROOT / "causal_predictions.csv", index=False)

print("Models and predictions saved successfully!")
