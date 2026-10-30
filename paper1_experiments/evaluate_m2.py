import pandas as pd

path = "paper1_experiments/"

data = pd.read_csv(
    path + "m2_explanation_results.csv"
)

# Known harmful change in this simulation:
# Group A becomes harmful from period 9.
data["actual_harm"] = (
    (data["group"] == "A") &
    (data["period"] >= 9)
)

data["alert"] = data["m2_signal"].astype(bool)

tp = (data["alert"] & data["actual_harm"]).sum()
fp = (data["alert"] & ~data["actual_harm"]).sum()
fn = (~data["alert"] & data["actual_harm"]).sum()

precision = tp / (tp + fp) if tp + fp else float("nan")
recall = tp / (tp + fn) if tp + fn else float("nan")

harm_period = 9
detected = data[
    (data["group"] == "A") &
    (data["alert"]) &
    (data["period"] >= harm_period)
]

first_detection = (
    int(detected["period"].min())
    if not detected.empty else None
)

delay = (
    first_detection - harm_period
    if first_detection is not None else None
)

print("\nM2 PRELIMINARY EVALUATION")
print("True positive periods:", tp)
print("False positive periods:", fp)
print("Missed harmful periods:", fn)
print(f"Precision: {precision:.2%}")
print(f"Recall: {recall:.2%}")
print("Detection delay:", delay)

data.to_csv(
    path + "m2_evaluation.csv",
    index=False
)

print("\nM2 evaluation saved.")