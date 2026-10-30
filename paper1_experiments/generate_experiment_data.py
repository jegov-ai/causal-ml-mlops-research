
import pandas as pd

# Create sample customer data
customers = pd.DataFrame({
    "customer_id": [1, 2, 3, 4, 5],
    "group": ["A", "A", "B", "B", "A"],
    "discount": [1, 0, 1, 0, 1]
})

print(customers)
# Sample revenue and cost in RM
customers["revenue"] = [80, 100, 80, 100, 80]
customers["cost"] = [60, 60, 60, 60, 60]

# Calculate profit
customers["profit"] = customers["revenue"] - customers["cost"]

print(customers)

# Hypothetical profit under two conditions
profit_without_discount = 0
profit_with_discount = 20

# Calculate treatment effect
treatment_effect = profit_with_discount - profit_without_discount

print("Treatment Effect: RM", treatment_effect)

# Treatment effect before and after a change
effect_before = 20
effect_after = -10

# Calculate how much the effect changed
effect_change = effect_after - effect_before

print("Treatment Effect Before: RM", effect_before)
print("Treatment Effect After: RM", effect_after)
print("Treatment Effect Change: RM", effect_change)

# Detect harmful treatment effect changes
if effect_before > 0 and effect_after < 0:
    print("ALERT: Treatment effect changed from positive to negative!")
else:
    print("No positive-to-negative treatment effect change detected.")

# Monitor treatment effects for each subgroup
subgroup_effects = {
    "A": {"before": 20, "after": -10},
    "B": {"before": 15, "after": 18}
}

for group, effects in subgroup_effects.items():
    before = effects["before"]
    after = effects["after"]

    print(f"Group {group}: Before = RM{before}, After = RM{after}")

    if before > 0 and after < 0:
        print(f"ALERT: Harmful treatment effect change in Group {group}!")
    else:
        print(f"No positive-to-negative change detected in Group {group}.")