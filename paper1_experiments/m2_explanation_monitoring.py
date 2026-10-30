
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

rng = np.random.default_rng(42)
records = []
reference = None

for period in range(1, 13):
    n = 1200

    age = rng.integers(18, 70, n)
    spending = rng.normal(200, 50, n)
    group = rng.integers(0, 2, n)
    treatment = rng.integers(0, 2, n)

    # Controlled treatment-effect change
    effect_a = 20 if period <= 5 else 20 - 6 * (period - 5)

    true_effect = np.where(group == 0, effect_a, 15)

    baseline = (
        40 + 0.08 * spending - 0.1 * age
        + rng.normal(0, 8, n)
    )

    outcome = baseline + treatment * true_effect

    X = pd.DataFrame({
        "age": age,
        "previous_spending": spending,
        "group": group
    })

    models = {}

    for t in [0, 1]:
        model = RandomForestRegressor(
            n_estimators=40,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X[treatment == t], outcome[treatment == t])
        models[t] = model

    def predict_effect(features):
        return (
            models[1].predict(features)
            - models[0].predict(features)
        )

    # Fixed reference customers for explanation comparison
    if reference is None:
        reference = X.iloc[:200].copy()

    for g in [0, 1]:
        sample = reference[reference["group"] == g].copy()

        # Feature-perturbation explanation diagnostic
        original = predict_effect(sample)
        importance = []

        for feature in ["age", "previous_spending"]:
            changed = sample.copy()
            changed[feature] = changed[feature].mean()

            importance.append(
                float(np.mean(
                    np.abs(original - predict_effect(changed))
                ))
            )

        records.append({
            "period": period,
            "group": "A" if g == 0 else "B",
            "estimated_effect": float(original.mean()),
            "age_importance": importance[0],
            "spending_importance": importance[1]
        })

results = pd.DataFrame(records)

# Compare explanations with the first period
baseline_explanations = results[results["period"] == 1].set_index("group")

for group in ["A", "B"]:
    mask = results["group"] == group
    first = baseline_explanations.loc[group]

    results.loc[mask, "explanation_change"] = (
        abs(results.loc[mask, "age_importance"] - first["age_importance"])
        + abs(
            results.loc[mask, "spending_importance"]
            - first["spending_importance"]
        )
    )

# Exploratory threshold only; not statistically calibrated
results["m2_signal"] = (
    (results["estimated_effect"] < 0)
    | (results["explanation_change"] > 3)
)

results.to_csv(
    "paper1_experiments/m2_explanation_results.csv",
    index=False
)

print("\nM2 EXPLANATION-STABILITY PILOT")
print(results.round(2).to_string(index=False))
print("\nM2 results saved.")
