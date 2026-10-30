
import pandas as pd

# Load previously estimated treatment effects
data = pd.read_csv(
    "paper1_experiments/effects_over_time.csv"
)

print("Treatment Effect Monitoring Results")

for group, group_data in data.groupby("group"):
    group_data = group_data.sort_values("period")

    for _, row in group_data.iterrows():
        period = int(row["period"])
        estimated = row["estimated_effect"]

        if estimated < 0:
            print(
                f"Period {period}: ALERT for Group {group} "
                f"(Estimated Effect = RM{estimated:.2f})"
            )
