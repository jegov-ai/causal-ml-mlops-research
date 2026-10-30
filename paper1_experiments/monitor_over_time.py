
import pandas as pd

# Simulated treatment effects over 10 periods
data = pd.DataFrame({
    "period": range(1, 11),
    "group_A": [20, 19, 21, 18, 15, 10, 5, -2, -8, -10],
    "group_B": [15, 16, 14, 17, 15, 16, 14, 15, 17, 16]
})

print("Treatment Effects Over Time")
print(data)

print("\nMonitoring Alerts")

for _, row in data.iterrows():
    if row["group_A"] < 0:
        print(f"Period {int(row['period'])}: ALERT for Group A")

    if row["group_B"] < 0:
        print(f"Period {int(row['period'])}: ALERT for Group B")
