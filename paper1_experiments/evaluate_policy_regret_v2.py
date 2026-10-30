
import pandas as pd

PATH = "paper1_experiments/"
BUDGET = 1

data = pd.read_csv(PATH + "effects_over_time.csv")
data = data.sort_values(["period", "group"])

assert not data.duplicated(["period", "group"]).any()

groups = sorted(data["group"].unique())


def evaluate(method):
    active = {g: True for g in groups}
    alert_count = 0
    records = []

    for period, current in data.groupby("period", sort=True):

        # Evaluate decisions made before this period
        for _, row in current.iterrows():
            group = row["group"]
            truth = float(row["true_effect"])

            chosen = truth if active[group] else 0.0
            optimal = max(truth, 0.0)

            records.append({
                "method": method,
                "period": period,
                "group": group,
                "regret": optimal - chosen
            })

        # Monitoring uses estimated effects only
        if alert_count >= BUDGET:
            continue

        if method == "M0":
            estimate = current["estimated_effect"].mean()

            if estimate < 0 and any(active.values()):
                alert_count += 1
                for group in groups:
                    active[group] = False

                print(f"M0 ALERT at period {period}")

        elif method == "M1":
            for _, row in current.iterrows():
                group = row["group"]

                if alert_count >= BUDGET:
                    break

                if active[group] and row["estimated_effect"] < 0:
                    alert_count += 1
                    active[group] = False

                    print(
                        f"M1 ALERT: Group {group}, "
                        f"period {period}"
                    )

    return pd.DataFrame(records), alert_count


summaries = []
all_records = []

for method in ["M0", "M1"]:
    records, alerts = evaluate(method)
    all_records.append(records)

    summaries.append({
        "method": method,
        "alerts_issued": alerts,
        "cumulative_regret": records["regret"].sum()
    })

summary = pd.DataFrame(summaries)

print("\nPOLICY REGRET EVALUATION V2")
print(summary.to_string(index=False))

pd.concat(all_records).to_csv(
    PATH + "policy_regret_v2_details.csv",
    index=False
)
