# Paper 1: Methods, Results and Limitations — Draft v1

Working paper title: Evaluation of Causal Machine Learning Integration into MLOps Pipelines for Explainable and Robust Decision Making.

Status: Partial manuscript draft based on completed exploratory simulations. Literature positioning, novelty assessment and supervisor approval remain pending.

## 1. Study objectives

This study evaluated whether additional causal monitoring signals and the timing of model reviews affected treatment-policy decision quality under controlled distribution shifts.

Two questions guided the completed extensions:

1. Does adding subgroup treatment-effect monitoring, a between-group treatment-assignment-rate contrast, or both reduce cumulative treatment-policy regret beyond monitoring conventional statistics and the aggregate treatment effect?
2. Do monitoring-triggered model reviews reduce cumulative treatment-policy regret relative to prospectively specified fixed review calendars under common candidate estimators, acceptance gates and review caps?

These extensions assess monitoring information and review timing. They do not independently establish the superiority of causal-aware monitoring over a purely conventional monitor.

## 2. Methods

### 2.1 Simulation setting

Each simulated stream contained 12 windows of 1,000 customers. Five scenarios were evaluated: stable conditions, covariate shift, treatment-assignment shift, treatment-response shift and opposing subgroup treatment-effect changes. Changes began at window 7 in the four shifted scenarios.

The customer features were age and previous spending. Subgroups were defined as younger customers aged below 35 years and older customers aged 35 years or above.

Baseline treatment effects were 40 for younger customers and 15 for older customers. In the response-shift scenario, the younger-group effect decreased to 5 while the older-group effect remained 15.

In the opposing-change scenario, the younger-group effect decreased from 40 to 5. The older-group effect increased to preserve the population-average treatment effect in expectation. Specifically, with baseline younger-group proportion q = 17/48, the older-group postchange effect was 15 + 35q/(1−q). Finite-window sample averages were not constrained to remain identical.

Treatment decisions used an assumed treatment cost of 10. Synthetic treatment effects were reserved for offline evaluation and were not supplied to the monitoring rules, model fitting or update-acceptance gate.

Labels were immediately available. Logged treatment assignment was exogenous: recommendations from the evaluated policies did not alter subsequent simulated data.

### 2.2 Initial model and monitoring variants

All arms shared one initial T-learner, fitted using random-forest outcome models with seed 42. The evaluation was therefore conditional on this initial fitted model.

The signal-ablation experiment compared four variants:

- M1: conventional feature, assignment, outcome and residual statistics, together with an aggregate augmented inverse-probability-weighted (AIPW) treatment-effect statistic.
- M2-A: M1 plus two subgroup AIPW treatment-effect means.
- M2-B: M1 plus the younger-minus-older treatment-assignment-rate contrast.
- M2-FULL: M1 plus both additions.

M1 already included the overall treatment-assignment rate. M2-B added a between-group contrast rather than introducing assignment monitoring for the first time.

Each arm used the maximum standardized score over its specified monitoring statistics. Explanation diagnostics were recorded separately and did not enter these four monitoring scores.

### 2.3 Calibration and independent stable-run assessment

The ablation experiment used 100 stable streams to estimate monitoring centers and scales, followed by 1,000 separate stable calibration streams.

Each arm's threshold was the empirical higher 95th percentile of its calibration-stream maximum scores across the 12-window horizon. This targeted a common 5% probability of at least one alert per stable stream.

A further 200 independent stable streams assessed achieved any-alert rates. Thresholds were not retuned using these held-out results or the evaluation outcomes.

The scale, calibration, held-out stable and evaluation seed ranges were separate. The evaluation used seeds 340000–340099, paired across monitoring variants, scenarios and review caps.

### 2.4 Alert-triggered reviews and model updates

Each monitoring arm could issue at most two alerts per stream. The first issued alert initiated consecutive model reviews, including a review in the triggering window, until the review cap or stream horizon was reached. Subsequent alerts did not extend the review schedule.

Review caps were 2, 4 and 8. A cap represented a maximum number of reviews rather than a guarantee of equal realized workload.

At each reviewed window, observations were split into 70% candidate-training data and 30% held-out gate data, stratified by subgroup and treatment assignment. Candidate models and gate data were shared across arms, while each arm maintained its own incumbent model.

Candidate and incumbent policies were compared using AIPW net-benefit pseudo-outcomes calculated with the frozen baseline nuisance models. An update was accepted when the estimated mean gain minus 1.96 standard errors was greater than zero.

Accepted updates affected decisions from the following window. A review did not automatically produce an update. The repeated pointwise acceptance rule did not provide a sequential-safety guarantee.

### 2.5 Fixed-calendar comparison

A separate experiment compared the four frozen monitoring variants with a PERIODIC arm using prospectively specified review calendars:

| Review cap | Review windows |
| --- | --- |
| 2 | 4, 8 |
| 4 | 3, 6, 9, 12 |
| 8 | 1, 3, 4, 6, 7, 9, 10, 12 |

PERIODIC used the same candidate estimator, training/gate split and acceptance rule. It issued no alerts and had no applicable change-detection-delay endpoint.

Reviews in window 12 counted toward workload, although accepted updates could not improve decisions within the observed horizon.

The experiment reused the frozen monitoring calibration and evaluated fresh seeds 350000–350099. The achieved stable-run alert rates from the previous experiment remained calibration diagnostics, rather than new independent evidence.

### 2.6 Outcomes and analysis

The principal measured outcome was cumulative period-average oracle-relative net-benefit regret over windows 7–12.

For customer i, true treatment effect τ_i, treatment cost c and binary policy action a_i, the offline loss was:

max(τ_i − c, 0) − a_i(τ_i − c).

Customer losses were averaged within each window and summed across the postchange evaluation horizon. These units represent simulated net-benefit opportunity loss, not total company profit. For stable streams, windows 7–12 provided the corresponding comparison horizon without an actual change.

Additional outcomes included prechange regret, harmful-treatment rate, alerts, reviews, accepted updates, detection probability and detection delay conditional on detection. Detection was not applicable to stable streams or the PERIODIC arm.

Both experiments evaluated 100 seeds per scenario across five scenarios and three review caps. Repeated arms and caps were paired evaluations, not independent simulation units.

Paired mean differences and pointwise 95% percentile-bootstrap intervals used 5,000 resamples. Analyses were exploratory and unadjusted for multiplicity. The replication count was pragmatic rather than based on a formal power calculation.

### 2.7 Provenance and verification

Code and protocols were committed before evaluation. Run records preserved configuration, source snapshots, hashes, seed allocations and completion status.

The ablation audit reconciled 72,000 period rows and 6,000 method-budget run rows. The schedule-comparison audit reconciled 90,000 period rows and 7,500 method-budget run rows.

Checks covered saved-output consistency, aggregation, review schedules, alert caps, recorded gate acceptance, summary statistics and paired bootstrap calculations. They did not independently reproduce every random-forest fit or reconstruct every customer's action from saved predictions.

## 3. Results

### 3.1 Incremental monitoring signals

In the main ablation experiment, all observed seed-wise postchange-regret differences between the additional-signal variants and M1 were exactly zero across the evaluated scenarios and review caps.

Monitoring scores were not identical. Assignment-contrast variants also produced some different alert and review events, but these differences did not change accepted-update indicators or recorded policy regret.

In the assignment-shift scenario, mean detection delay was 0.02 windows for M1 and M2-A, compared with zero for M2-B and M2-FULL. This small detection advantage did not translate into lower regret.

In the covariate, response and opposing scenarios, every arm already detected change in the first shifted window, leaving no earlier window-level detection opportunity in those evaluated streams.

Held-out stable any-alert rates were 5/200 (2.5%) for M1 and M2-B, and 7/200 (3.5%) for M2-A and M2-FULL. Thus a common calibration target did not yield exactly equal achieved false-alert rates.

The zero paired bootstrap intervals reflected identical observed differences. They did not establish population equivalence.

### 3.2 Alert-triggered versus fixed-calendar reviews

M1 had lower mean postchange regret than the selected fixed calendars in the response and opposing-change scenarios.

| Scenario | Review cap | M1 regret | PERIODIC regret | M1 minus PERIODIC | Descriptive 95% interval |
| --- | ---: | ---: | ---: | ---: | --- |
| Response | 2 | 15.489650 | 16.082900 | −0.593250 | [−0.970900, −0.266716] |
| Response | 4 | 15.258100 | 16.093100 | −0.835000 | [−1.266564, −0.444599] |
| Response | 8 | 15.193450 | 15.371450 | −0.178000 | [−0.378659, −0.011350] |
| Opposing | 2 | 11.504052 | 19.119119 | −7.615068 | [−9.355841, −5.954485] |
| Opposing | 4 | 11.345019 | 24.649376 | −13.304356 | [−14.865089, −11.743961] |
| Opposing | 8 | 11.047568 | 11.881339 | −0.833771 | [−1.306201, −0.418000] |

These differences depended on the selected calendars and fixed shift onset. In the opposing scenario, the first postchange calendar review occurred at window 8 under cap 2, window 9 under cap 4 and window 7 under cap 8.

The complete results also included settings favoring PERIODIC. In stable streams, M1-minus-PERIODIC mean differences were +0.0233, +0.0617 and +0.0913 at caps 2, 4 and 8, respectively.

Covariate-shift differences were +0.0010, +0.00135 and −0.0058. Assignment-shift differences were −0.00165, +0.01185 and +0.0341. Their descriptive intervals included zero.

Equal review caps did not ensure equal timing or realized workload. Consequently, these results do not establish that alert-triggered reviews outperform every fixed schedule.

### 3.3 Adverse additional-signal findings

In the fresh schedule-comparison seed set, added subgroup monitoring again provided no observed regret improvement over M1 and occasionally increased regret.

M2-FULL-minus-M1 mean differences were +0.00785 for covariate shift at cap 2, +0.506634 for opposing changes at cap 2 and +0.0036 for stable streams at cap 8. Other cells were zero.

Recorded cases showed early alerts consuming reviews before a later useful update opportunity. One stable-stream case also showed that an update accepted by the estimated gate could increase offline oracle-relative loss.

These cases illustrate possible failure mechanisms under the specified controller; they do not establish universal harm from subgroup monitoring.

### 3.4 Review-spacing development check

A subsequent engineering check compared consecutive reviews with score-conditioned spaced reviews using only two development seeds per scenario.

Spacing generally produced unchanged regret. It reduced mean regret by 0.085 in the covariate-shift setting at cap 4, but increased mean regret by approximately 2.374919 in the opposing-change scenario at each review cap. These patterns occurred for both M1 and FULL.

In one opposing-change seed, spacing delayed acceptance of a helpful update from window 8 to window 9. This delayed adaptation increased loss.

This small development check is reported separately from the 100-seed studies. It does not support inferential claims or establish general controller superiority.

## 4. Discussion and limitations

The completed experiments distinguish monitoring differences from decision improvements. Additional signals sometimes changed alerts or reviews without improving accepted updates or treatment-policy regret.

Review timing affected outcomes, but its usefulness depended on change timing, available review opportunities and the common acceptance gate. Early alerts could exhaust scarce resources, while spacing could delay helpful adaptation.

The findings are conditional on a synthetic generator, one initial fitted model, immediate labels, exogenous logging, a fixed change onset, a finite horizon, selected review calendars and one update-acceptance rule. They do not establish real-world profitability, deployment safety or robustness across model initializations.

M1 combined conventional and aggregate causal statistics. The two main extensions did not include a purely conventional M0 arm. Therefore, their results cannot isolate the overall benefit of adding causal information to conventional monitoring.

Explanation statistics remained offline diagnostics. These experiments do not establish an explanation-stability benefit.

The interval estimates were exploratory and pointwise, without multiplicity adjustment or a prespecified equivalence margin. Null differences should not be interpreted as proof of equivalence.

## 5. Contribution boundary and remaining work

The supported empirical contribution is a controlled evaluation showing that review timing affected treatment-policy loss, while richer subgroup monitoring provided no incremental improvement under the evaluated conditions.

This is not a claim of a new causal estimator, new drift detector or universally superior review controller.

Prior research already addresses causal decisions under drift, monitoring-triggered adaptation and regret evaluation. Exact overlap with the unavailable full manuscripts of CausalStream and OnlineCML remains unresolved. Novelty and publication readiness remain provisional.

Before submission, the manuscript requires a source-verified related-work section, complete scenario-generation details checked against code, full results tables, reproducibility documentation and supervisor review. Historical positive, null and adverse findings must remain preserved.