from pathlib import Path
ROOT = Path(__file__).resolve().parent

import pandas as pd
import json
from datetime import datetime, timezone
from sklearn.metrics import mean_absolute_error

# Read predictions saved by our causal ML model
results = pd.read_csv(ROOT / "causal_predictions.csv")

# Calculate evaluation metrics
mae = mean_absolute_error(
    results["true_effect"],
    results["estimated_effect"]
)

experiment = {
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "model": "T-Learner Random Forest",
    "test_customers": len(results),
    "estimated_average_effect": round(
        results["estimated_effect"].mean(), 2
    ),
    "true_average_effect": round(
        results["true_effect"].mean(), 2
    ),
    "treatment_effect_mae": round(float(mae), 2)
}

# Save our experiment results
with open(ROOT / "experiment_log.json", "w") as file:
    json.dump(experiment, file, indent=4)

print("MLOPS EXPERIMENT REPORT")
print("-----------------------")
print(json.dumps(experiment, indent=4))
print("Experiment log saved successfully!")
