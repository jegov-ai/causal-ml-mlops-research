
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
