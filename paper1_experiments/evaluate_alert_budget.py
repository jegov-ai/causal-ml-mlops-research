
import pandas as pd

data = pd.read_csv(
    "paper1_experiments/effects_over_time.csv"
)

ALERT_BUDGET = 2

periods = sorted(data["period"].unique())
groups = sorted(data["group"].unique())

alert_counts = {"M0": 0, "M1": 0}
records = []

for period in periods:
    current = data[data["period"] == period]

    # M0: Overall monitoring signal
    overall_effect = current["estimated_effect"].mean()
    m0_signal = overall_effect < 0

    # M1: Subgroup monitoring signal
    m1_signals = {
        row["group"]: row["estimated_effect"] < 0
        for _, row in current.iterrows()
    }

    # M0 can issue at most one alert per period
    m0_alert = False

    if m0_signal and alert_counts["M0"] < ALERT_BUDGET:
        m0_alert = True
        alert_counts["M0"] += 1

    # M1 uses the same total alert limit
    for group in groups:
        row = current[current["group"] == group].iloc[0]

        m1_alert = False

        if (
            m1_signals[group]
            and alert_counts["M1"] < ALERT_BUDGET
        ):
            m1_alert = True
            alert_counts["M1"] += 1

        records.append({
            "period": period,
            "group": group,
            "actual_harm": bool(row["true_effect"] < 0),
            "M0_alert": m0_alert,
            "M1_alert": m1_alert
        })

results = pd.DataFrame(records)

print("\nMATCHED ALERT BUDGET EVALUATION")
print("Maximum alerts per method:", ALERT_BUDGET)

for method in ["M0", "M1"]:
    alerts = results[f"{method}_alert"]

    if method == "M0":
        # Count each overall alert once
        issued = alert_counts["M0"]
    else:
        issued = alert_counts["M1"]

    detected_harm = (
        results["actual_harm"] & alerts
    ).sum()

    print(f"\n{method}")
    print("Alerts issued:", issued)
    print("Harmful subgroup-periods flagged:", int(detected_harm))

print("\nDetailed results:")
print(results.to_string(index=False))
