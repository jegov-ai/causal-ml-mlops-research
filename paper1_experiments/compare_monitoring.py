
import pandas as pd

# Simulated treatment effects before and after
data = pd.DataFrame({
    "group": ["A", "B"],
    "before": [20, 15],
    "after": [-10, 45]
})

# M0: Overall monitoring
overall_before = data["before"].mean()
overall_after = data["after"].mean()

print("M0 - Overall Monitoring")
print("Before:", overall_before)
print("After:", overall_after)

if overall_before > 0 and overall_after < 0:
    print("ALERT: Overall effect became negative!")
else:
    print("No overall positive-to-negative alert.")

# M1: Subgroup-aware monitoring
print("\nM1 - Subgroup Monitoring")

for _, row in data.iterrows():
    if row["before"] > 0 and row["after"] < 0:
        print(f"ALERT: Harmful change in Group {row['group']}")
    else:
        print(f"Group {row['group']}: No sign-change alert")



import pandas as pd

# Load the simulated customer dataset
data = pd.read_csv(
    "paper1_experiments/simulated_customers.csv"
)

print("Customers loaded:", len(data))

# M0: Overall treatment-effect monitoring
overall_before = data["true_treatment_effect"].mean()
overall_after = data["effect_after_shift"].mean()

print("\nM0 - Overall Monitoring")
print("Before:", round(overall_before, 2))
print("After:", round(overall_after, 2))

if overall_before > 0 and overall_after < 0:
    print("ALERT: Overall effect became negative!")
else:
    print("No overall positive-to-negative alert.")

# M1: Subgroup-aware treatment-effect monitoring
print("\nM1 - Subgroup Monitoring")

for group, group_data in data.groupby("group"):
    before = group_data["true_treatment_effect"].mean()
    after = group_data["effect_after_shift"].mean()

    print(f"Group {group}: {before:.2f} -> {after:.2f}")

    if before > 0 and after < 0:
        print(f"ALERT: Harmful change in Group {group}!")
    else:
        print(f"No positive-to-negative alert for Group {group}.")


import pandas as pd

# Load time-based treatment effect estimates
data = pd.read_csv(
    "paper1_experiments/effects_over_time.csv"
)

print("M0 vs M1 Monitoring Comparison\n")

# M0: Monitor the overall estimated treatment effect
overall = data.groupby("period")["estimated_effect"].mean()

# M1: Monitor each subgroup separately
subgroups = data.sort_values(["period", "group"])

for period in sorted(data["period"].unique()):
    overall_effect = overall.loc[period]

    # M0 overall alert
    m0_alert = overall_effect < 0

    # M1 subgroup alerts
    period_data = subgroups[subgroups["period"] == period]
    m1_alerts = period_data[
        period_data["estimated_effect"] < 0
    ]["group"].tolist()

    print(
        f"Period {period}: "
        f"M0={'ALERT' if m0_alert else 'No Alert'}, "
        f"M1={m1_alerts if m1_alerts else 'No Alert'}"
    )

