
import pandas as pd

# Load causal ML predictions
data = pd.read_csv("causal_predictions.csv")

# Hypothetical campaign cost per customer
campaign_cost = 10

# Estimate net spending gain after campaign cost
data["estimated_net_gain"] = (
    data["estimated_effect"] - campaign_cost
)

# Recommend a discount when estimated net gain is positive
data["recommend_discount"] = (
    data["estimated_net_gain"] > 0
)

# Save decisions
data.to_csv("optimization_results.csv", index=False)

print("PRODUCT OPTIMIZATION REPORT")
print("---------------------------")
print("Customers evaluated:", len(data))
print("Discounts recommended:", data["recommend_discount"].sum())
print("Discounts not recommended:", (~data["recommend_discount"]).sum())

print("\nOptimization results saved successfully!")
