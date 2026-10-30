
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from pathlib import Path

OUT = Path("paper1_experiments")
OUT.mkdir(exist_ok=True)

rng = np.random.default_rng(42)
PERIODS = 12
N = 800
BUDGET = 2

methods = ["M0", "M1", "M2"]
policies = {m: {"A": True, "B": True} for m in methods}
alerts = {m: 0 for m in methods}
regrets = {m: 0.0 for m in methods}
records = []

reference = None
baseline_explanation = {}
reference_outcome = None

for period in range(1, PERIODS + 1):

    group = rng.choice(["A", "B"], size=N)
    age = rng.integers(18, 70, size=N)
    spending = rng.normal(200, 50, size=N)
    treatment = rng.integers(0, 2, size=N)

    X = pd.DataFrame({
        "age": age,
        "spending": spending,
        "is_A": (group == "A").astype(int)
    })

    effect_a = (
        20 if period <= 5
        else 20 - 6 * (period - 5)
    )

    true_effect = np.where(group == "A", effect_a, 15.0)

    baseline_profit = (
        40 + 0.05 * (spending - 200)
        - 0.12 * (age - 40)
    )

    outcome = (
        baseline_profit
        + treatment * true_effect
        + rng.normal(0, 8, size=N)
    )

    # Train causal T-Learner
    models = {}

    for t in [0, 1]:
        model = RandomForestRegressor(
            n_estimators=30,
            min_samples_leaf=12,
            random_state=period,
            n_jobs=-1
        )

        model.fit(
            X.loc[treatment == t],
            outcome[treatment == t]
        )

        models[t] = model

    def predict_effect(features):
        return (
            models[1].predict(features)
            - models[0].predict(features)
        )

    if reference is None:
        reference = X.iloc[:200].copy()

    estimates = {}
    explanations = {}

    for g in ["A", "B"]:
        anchor = reference.copy()
        anchor["is_A"] = int(g == "A")

        estimates[g] = float(
            predict_effect(anchor).mean()
        )

        original = predict_effect(anchor)
        importance = []

        for feature in ["age", "spending"]:
            changed = anchor.copy()
            changed[feature] = changed[feature].mean()

            importance.append(
                float(np.mean(np.abs(
                    original - predict_effect(changed)
                )))
            )

        explanations[g] = np.array(importance)

        if period == 1:
            baseline_explanation[g] = explanations[g].copy()

    overall_outcome = float(outcome.mean())

    if reference_outcome is None:
        reference_outcome = overall_outcome

    # Regret: decisions made before new alerts
    for method in methods:
        for g in ["A", "B"]:
            truth = float(effect_a if g == "A" else 15)

            chosen = (
                truth if policies[method][g] else 0.0
            )

            optimal = max(truth, 0.0)

            regrets[method] += optimal - chosen

    # Monitoring signals
    signals = {
        "M0": {
            "ALL": abs(
                overall_outcome - reference_outcome
            ) > 8.0
        },
        "M1": {
            g: estimates[g] < 0
            for g in ["A", "B"]
        },
        "M2": {
            g: (
                estimates[g] < 0
                or np.abs(
                    explanations[g]
                    - baseline_explanation[g]
                ).sum() > 3.0
            )
            for g in ["A", "B"]
        }
    }

    # Same alert cap and next-period response
    for method in methods:

        if alerts[method] >= BUDGET:
            continue

        for target, detected in signals[method].items():

            targets = (
                ["A", "B"] if target == "ALL"
                else [target]
            )

            if detected and any(
                policies[method][g] for g in targets
            ):
                alerts[method] += 1

                for g in targets:
                    policies[method][g] = False

                records.append({
                    "method": method,
                    "period": period,
                    "alert_target": target,
                    "true_A_effect": effect_a,
                    "true_B_effect": 15
                })

                break

    print(
        f"Period {period}: "
        f"True A={effect_a:.1f}, "
        f"Estimated A={estimates['A']:.2f}"
    )

summary = pd.DataFrame([
    {
        "method": m,
        "alerts": alerts[m],
        "cumulative_regret": regrets[m]
    }
    for m in methods
])

alert_log = pd.DataFrame(
    records,
    columns=[
        "method", "period", "alert_target",
        "true_A_effect", "true_B_effect"
    ]
)

summary.to_csv(
    OUT / "final_comparison_summary.csv",
    index=False
)

alert_log.to_csv(
    OUT / "final_comparison_alerts.csv",
    index=False
)

print("\nPILOT COMPARISON")
print(summary.to_string(index=False))

print("\nALERT LOG")
print(alert_log.to_string(index=False))

print("\nResults saved.")
