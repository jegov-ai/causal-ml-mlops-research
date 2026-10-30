
import pandas as pd

data = pd.read_csv(
    "paper1_experiments/effects_over_time.csv"
)

periods = sorted(data["period"].unique())
groups = sorted(data["group"].unique())

records = []

for period in periods:
    current = data[data["period"] == period]

    # M0: Overall estimated effect
    m0_alert = current["estimated_effect"].mean() < 0

    # M1: Subgroup estimated effects
    for group in groups:
        row = current[current["group"] == group].iloc[0]

        actual_harm = row["true_effect"] < 0
        m1_alert = row["estimated_effect"] < 0

        records.append({
            "period": period,
            "group": group,
            "actual_harm": actual_harm,
            "M0_alert": m0_alert,
            "M1_alert": m1_alert
        })

results = pd.DataFrame(records)

for method in ["M0", "M1"]:
    alert = results[f"{method}_alert"]
    harm = results["actual_harm"]

    tp = int((alert & harm).sum())
    fp = int((alert & ~harm).sum())
    fn = int((~alert & harm).sum())

    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0

    print(f"\n{method} Monitoring")
    print("True positives:", tp)
    print("False positives:", fp)
    print("Missed harmful periods:", fn)
    print(f"Precision: {precision:.2%}")
    print(f"Recall: {recall:.2%}")
