
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor

OUT = Path(__file__).resolve().parent / "m2_explanation_stability_v1_repaired"
OUT.mkdir(parents=True, exist_ok=True)
OUT.mkdir(exist_ok=True)

PERIODS = 12
N = 600
FEATURES = ["age", "spending", "group_A"]

def true_effect(period, group):
    if group == 0:
        return 15.0
    return 20.0 if period <= 5 else 20.0 - 6 * (period - 5)

def make_data(seed, period, stable=False):
    rng = np.random.default_rng(seed * 100 + period)
    group = rng.integers(0, 2, N)
    age = rng.normal(40, 12, N)
    spending = rng.normal(100, 20, N)
    treatment = rng.integers(0, 2, N)

    effect = np.array([
        true_effect(1 if stable else period, g)
        for g in group
    ])

    baseline = (
        40 + 0.12 * (age - 40)
        + 0.04 * (spending - 100)
    )
    outcome = (
        baseline + treatment * effect
        + rng.normal(0, 8, N)
    )

    return pd.DataFrame({
        "age": age,
        "spending": spending,
        "group_A": group,
        "treatment": treatment,
        "outcome": outcome
    })

def fit_models(data, seed):
    treated = data[data.treatment == 1]
    control = data[data.treatment == 0]

    def fit(frame):
        model = RandomForestRegressor(
            n_estimators=40,
            min_samples_leaf=12,
            random_state=seed,
            n_jobs=-1
        )
        model.fit(frame[FEATURES], frame.outcome)
        return model

    return fit(treated), fit(control)

def predict_effect(models, x):
    treated, control = models
    return treated.predict(x) - control.predict(x)

def explanation(models, anchors):
    # Fixed-background feature replacement gives an
    # approximate perturbation-based attribution.
    base = predict_effect(models, anchors)
    values = []

    for feature in FEATURES:
        changed = anchors.copy()
        if feature == "group_A":
            # Valid binary contrast on a balanced audit population.
            changed[feature] = 1 - anchors[feature]
        else:
            changed[feature] = anchors[feature].mean()
        altered = predict_effect(models, changed)
        values.append(np.mean(np.abs(base - altered)))

    return np.array(values)

def experiment(seed, stable=False):
    anchor_rng = np.random.default_rng(9999)
    anchors = pd.DataFrame({
        "age": anchor_rng.normal(40, 12, 200),
        "spending": anchor_rng.normal(100, 20, 200),
        "group_A": np.tile([0, 1], 100)
    })

    previous = None
    output = []

    for period in range(1, PERIODS + 1):
        data = make_data(seed, period, stable)
        models = fit_models(data, seed + period)
        contributions = explanation(models, anchors)
        estimated_effect = predict_effect(models, anchors.loc[anchors.group_A == 1]).mean()

        change = (
            0.0 if previous is None
            else np.abs(contributions - previous).sum()
        )

        output.append({
            "seed": seed,
            "period": period,
            "stable": stable,
            "estimated_effect_A": estimated_effect,
            "explanation_change": change,
            "age_contribution": contributions[0],
            "spending_contribution": contributions[1],
            "group_contribution": contributions[2],
            "true_effect_A": (
                20.0 if stable else true_effect(period, 1)
            )
        })

        previous = contributions.copy()

    return output

print("Calibrating on separate stable simulations...", flush=True)

calibration = []
for seed in range(1000, 1010):
    calibration.extend(experiment(seed, stable=True))

cal = pd.DataFrame(calibration)
threshold = cal.loc[
    cal.period > 1, "explanation_change"
].quantile(0.95)

print("Testing 20 independent simulations...", flush=True)

results = []
for seed in range(100, 120):
    results.extend(experiment(seed))

df = pd.DataFrame(results)
df["explanation_alert"] = (
    (df.period > 1) &
    (df.explanation_change > threshold)
)

df["harmful_now"] = df.true_effect_A < 0
df["false_alert"] = (
    df.explanation_alert & ~df.harmful_now
)
df["harmful_detection"] = (
    df.explanation_alert & df.harmful_now
)

summary = pd.DataFrame([{
    "threshold": threshold,
    "simulations": df.seed.nunique(),
    "false_alert_count": int(df.false_alert.sum()),
    "harmful_detection_count": int(df.harmful_detection.sum()),
    "seeds_with_harmful_detection": int(
        df.groupby("seed").harmful_detection.any().sum()
    )
}])

df.to_csv(
    OUT / "m2_explanation_stability_v1_results.csv",
    index=False
)
summary.to_csv(
    OUT / "m2_explanation_stability_v1_summary.csv",
    index=False
)

print("\nEXPLANATION-STABILITY DIAGNOSTIC")
print(summary.to_string(index=False))
print("\nResults saved.")
print("NOTE: Balanced-anchor perturbation proxy; group contribution is a binary flip contrast, not formal SHAP. Historical outputs are not comparable without rerunning.")
print("Not yet an end-to-end M0/M1/M2 validation.")
