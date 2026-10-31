# Project 1 — Evaluation plan v2
Date: 31 October 2026
Status: Exploratory plan; originality not yet verified.

## Experimental question
When subgroup treatment effects change while the overall
average stays stable, does subgroup-aware monitoring detect
change sooner and reduce decision loss compared with
conventional and average-effect monitoring?

## Methods
M0: conventional monitoring.
M1: M0 plus average treatment-effect monitoring.
M2: M1 plus subgroup treatment-effect monitoring.

Use identical data, treatment-effect estimators, label timing,
calibration procedures and response rules across methods.

## Scenarios
1. No change: evaluate false alerts.
2. Existing one-group deterioration: preserve as a benchmark.
3. Opposing subgroup-effect changes with a stable overall ATE.

Specify scenario 3's effect trajectories, onset and magnitudes
before running it. Do not adjust them to favor a method.

## Hypotheses
H1: M2 detects the opposing subgroup-effect changes sooner.
H2: M2 reduces post-change decision loss under common
response rules and matched review-resource constraints.

These hypotheses may be unsupported.

## Outcomes
Primary: cumulative post-change oracle-relative decision loss.
Primary contrast: M2 minus M0.
Secondary contrast: M2 minus M1.

Secondary outcomes:
- Detection probability and delay.
- Missed changes.
- Stable-run false-alert probability.
- Harmful treatment exposure.
- Alerts and decision reviews used.

Define event matching and censoring before implementation.
Report detection delay alongside missed-change rates.

## Fairness and resource accounting
Keep run-level false-alert calibration separate from alert caps.
Validate false-alert rates on independent stable test runs.

An alert, a follow-up review and an action change are different
events; record them separately.

Specify a common review-budget allocation rule before testing.
Compare multiple fixed review budgets selected in advance.
Retain the original capped-alert and ongoing-review controllers
as exploratory sensitivity comparisons.

All decisions use observed data only.
True effects are reserved for offline evaluation.
Responses affect the next period only.

## Statistical plan
Freeze the implementation and configuration before testing.
Use fresh test seeds, paired across methods.
Report paired effect estimates and 95% confidence intervals.
Specify multiplicity handling before confirmatory analysis.
Do not select favorable seeds or discard unfavorable results.

## Scope
This experiment isolates monitoring and response behavior.
Causal-ML estimators, explainability and broader MLOps
integration require separate evaluation.

A stable ATE does not guarantee conventional monitoring
cannot detect changes in other outcome-distribution signals.

## Before the next run
Finalize effect trajectories, resource allocation, event metrics,
sample sizes, seeds and acceptance checks.
Document departures from this plan.


## Fixed settings for the next exploratory experiment

### Opposing subgroup-effect changes
Equal-sized groups throughout.
Periods 1–5: A = +20, B = +15.
Periods 6–12: A = -10, B = +45.
Overall ATE remains +17.5.
No treatment cost beyond what is represented in the net effect.
Conventional outcome-distribution signals remain available.

### Common response and review budgets
Evaluate budgets of 2, 4 and 8 decision reviews per run.
The first issued alert starts consecutive per-period reviews.
Each review checks both groups and consumes one review unit.
The triggering period counts as the first review.
Further alerts do not restart or extend the review schedule.
Unused review capacity at the run's end remains unused.

Use the same decision rule for every method:
- Stop treatment if the effect's upper 95% confidence bound is negative.
- Start treatment if its lower 95% confidence bound is positive.
- Otherwise retain the current action.

Current-period outcomes affect next-period actions only.
These pointwise intervals are an exploratory decision rule,
not a guarantee of sequential safety.

### Interpretation
The scenario and controller are exploratory choices.
Do not modify them after inspecting results without recording
the modification and using new test seeds.