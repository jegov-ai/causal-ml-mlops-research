
import pandas as pd

data = pd.read_csv(
    "paper1_experiments/effects_over_time.csv"
)

results = []

for group, group_data in data.groupby("group"):
    group_data = group_data.sort_values("period")

    # Ground truth is used only for evaluation
    harmful = group_data[
        group_data["true_effect"] < 0
    ]

    # Monitoring uses estimated effects only
    alerts = group_data[
        group_data["estimated_effect"] < 0
    ]

    first_harm = (
        int(harmful["period"].min())
        if not harmful.empty else None
    )

    first_alert = (
        int(alerts["period"].min())
        if not alerts.empty else None
    )

    false_alerts = sum(
        (group_data["estimated_effect"] < 0)
        & (group_data["true_effect"] >= 0)
    )

    missed_periods = sum(
        (group_data["estimated_effect"] >= 0)
        & (group_data["true_effect"] < 0)
    )

    detection_delay = (
        max(0, first_alert - first_harm)
        if first_harm is not None
        and first_alert is not None
        and first_alert >= first_harm
        else None
    )

    results.append({
        "group": group,
        "first_harm": first_harm,
        "first_alert": first_alert,
        "detection_delay": detection_delay,
        "false_alert_periods": int(false_alerts),
        "missed_harmful_periods": int(missed_periods)
    })

print(pd.DataFrame(results))
