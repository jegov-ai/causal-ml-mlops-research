# Monitoring Signals and Model-Review Timing under Distribution Shift: An Exploratory Treatment-Policy Evaluation

**Proposed scoped title for supervisor discussion.** The recorded project title remains “Evaluation of Causal Machine Learning Integration into MLOps Pipelines for Explainable and Robust Decision Making.” No formal title change is implied.

Author: Jegan Govinda (Jegov)  
Working draft v4 — 3 November 2026 (Malaysia)

**Draft status:** Consolidated manuscript for internal and supervisor review; not submission-ready. References and closest-work coverage remain incomplete. This draft reports the two completed extensions and separately preserves the engineering check; it does not replace historical Project 1 studies.

## Abstract

Monitoring a changing environment does not necessarily improve the decisions made by a machine-learning system. Additional signals may identify change without producing a useful model update, particularly when review opportunities are limited. This study evaluates the incremental decision value of causal monitoring signals and the timing of model reviews in a controlled synthetic treatment-policy benchmark.

Two prospectively specified exploratory experiments used 12 windows of 1,000 customers, five distributional scenarios and review caps of 2, 4 and 8. Each experiment evaluated 100 paired seeds per scenario, conditional on one initial random-forest T-learner. The first separated subgroup treatment-effect signals and a between-group treatment-assignment-rate contrast from a baseline combining conventional statistics with aggregate causal-effect monitoring. The second compared these monitoring variants with selected fixed review calendars. Candidate estimators and held-out AIPW update-acceptance gates were common across arms. Accepted updates affected the following window.

The main ablation produced exactly zero observed paired regret differences between the additional-signal variants and the baseline. In the fresh calendar comparison, additional subgroup signals again provided no improvement and occasionally increased loss. Alert-triggered baseline reviews produced lower mean loss than the selected calendars under treatment-response and opposing subgroup-effect changes, while stable conditions favored calendar reviews. These comparisons depended on review timing and did not establish universal controller superiority.

The findings show that monitoring differences and decision benefits must be evaluated separately. Conclusions remain conditional on the generator, initial model, calibration, update gate, fixed shift onset and chosen calendars. Novelty remains provisional.

Keywords: causal machine learning; MLOps; distribution shift; treatment-policy regret; model monitoring; review budgets.

## 1. Introduction

A machine-learning model used to support treatment or product decisions may encounter changes in customer characteristics, treatment assignment or treatment response. In a discount-allocation setting, these changes raise distinct questions. A change in the customer population may affect the distribution of predictions, whereas a change in treatment response may alter whether offering the discount is beneficial. Monitoring these quantities can inform model review, but detecting a change does not itself determine whether a replacement model should be deployed.

This distinction motivates the present evaluation. A monitoring signal affects decisions through a sequence of operational steps: an alert initiates a review, a candidate model is trained, an acceptance rule compares candidate and incumbent policies, and an accepted update changes subsequent decisions. Additional monitoring information may have little incremental value if an existing monitor already triggers a timely review or if the available candidate does not pass the update gate. Conversely, an early alert may consume limited review opportunities before a later change.

Our project implements a synthetic causal-ML monitoring benchmark in which a T-learner estimates heterogeneous treatment effects and recommends treatment when the estimated effect exceeds an assumed cost. The benchmark separates logged treatment assignment from policy recommendations and reserves known synthetic effects for offline evaluation. This permits calculation of oracle-relative treatment-policy opportunity loss while keeping synthetic truth outside the monitoring and adaptation rules.

Existing research already addresses treatment decisions in dynamic environments, causal estimation on streams, monitoring-triggered adaptation and resource-constrained interventions. For example, Berrevoets et al. (2022) evaluated treatment-effect optimisation under changing conditions. OnlineCML's inspected public examples demonstrate causal pseudo-outcome monitoring and estimator reset. These precedents rule out a broad claim that combining causal estimation, drift monitoring and regret evaluation is itself new. The narrower question is whether a controlled comparison can clarify the incremental value of monitoring signals and review timing under common adaptation procedures.

We examine two research questions within the scope of these extensions. First, does adding subgroup treatment-effect monitoring, a between-group assignment-rate contrast, or both reduce cumulative treatment-policy regret beyond a baseline that already includes conventional statistics and aggregate causal-effect monitoring? Second, how does alert-triggered review timing compare with prospectively specified fixed calendars when candidate estimation, update acceptance and maximum review caps are shared?

The first experiment compared four monitoring variants. M1 combined conventional statistics with an aggregate AIPW treatment-effect statistic. M2-A added subgroup treatment-effect statistics, M2-B added a between-group assignment-rate contrast, and M2-FULL added both. The second experiment retained these variants and introduced fixed-calendar reviews. Each experiment evaluated five scenarios and three review caps using 100 paired seeds per scenario.

The principal measured outcome was cumulative period-average oracle-relative net-benefit regret over the latter six windows. Alerts, reviews, accepted updates, harmful-treatment rates and detection timing provided complementary operational evidence. Alert thresholds targeted a common stable-stream any-alert probability, with independent held-out assessment. Equal intended calibration targets were distinguished from equal achieved false-alert rates, and common review caps were distinguished from equal realized workload.

The completed results did not show an incremental regret benefit from the additional monitoring signals. The main ablation yielded identical observed regret across variants, while the fresh calendar comparison included occasional adverse subgroup-monitoring outcomes. Alert-triggered M1 reviews reduced loss relative to the selected calendars under treatment-effect changes, but calendar reviews performed better in stable settings. A separate small review-spacing development check also demonstrated that delaying reviews could postpone a useful update. These findings are retained together rather than selecting only favorable comparisons.

The intended contribution is a reproducible, controlled empirical evaluation of how monitoring information and review opportunities translate into downstream policy performance. It is not a new treatment-effect estimator or drift detector. The experiments do not isolate the overall benefit of causal information over a purely conventional monitor because M1 already contains aggregate causal information. They also do not establish an explanation-stability benefit; explanation quantities remain offline diagnostics in these extensions.

The contribution and its limits require further assessment against the closest literature. In particular, the complete CausalStream and OnlineCML manuscripts were unavailable during the audit, and full overlap remains unresolved. The study is therefore presented as exploratory evidence with a provisional research-gap assessment, subject to supervisor review and final manuscript scope alignment.

## 2. Related work and study positioning

### 2.1 Causal decision making in changing environments

Existing research already investigates causal treatment decisions under changing conditions. Berrevoets, Verboven and Verbeke (2022) evaluated treatment-effect optimisation in dynamic environments using uplifted contextual bandits, conventional contextual bandits and uplift random forests. Their experiments included static, sudden-change and gradual-change settings. An ADWIN-based random-forest comparator triggered data recollection and retraining following detected change.

This work establishes that treatment decisions under drift, monitoring-triggered adaptation and oracle-based decision evaluation are not new general contributions of the present study.

An important distinction concerns the outcome definition. Berrevoets et al. defined regret using disagreement with an oracle treatment choice. Our evaluation measures the magnitude of foregone net treatment benefit. These quantities address related but different questions: action disagreement records whether a decision differs, whereas opportunity loss also accounts for the consequence of that difference.

The inspected prior comparison also varied learning and data-collection strategies. Our extensions instead compare monitoring additions and review timing while retaining common candidate estimators and update-acceptance rules. This is an experimental distinction, not evidence of a new causal estimator or proof of novelty.

### 2.2 Streaming causal estimation and adaptation

CausalStream describes an architecture for real-time causal inference on data streams, including incremental doubly robust estimation. Its accessible abstract and first-page preview establish relevant overlap with streaming causal estimation. However, its complete manuscript was unavailable during our audit. Its full monitoring design, adaptation rules and experimental comparisons therefore remain unresolved.

OnlineCML provides additional relevant evidence through public author documentation and software examples. An inspected example applies ADWIN to causal pseudo-outcomes and resets estimation following detected drift, comparing this approach with static and forgetting-factor alternatives. Another example demonstrates cumulative regret for exploration policies in a stationary two-arm setting.

These examples show that causal drift monitoring, estimator adaptation and regret demonstrations already exist. They must not be presented as capabilities introduced by our project.

The inspected examples did not establish the exact joint comparison used in our extensions: additional monitoring signals evaluated under common estimators, a common update gate, independently assessed run-level false-alert targets and finite review caps, with downstream treatment-policy opportunity loss as an outcome. This statement is restricted to the inspected evidence. The complete OnlineCML manuscript remained unavailable, so its full overlap cannot be excluded.

### 2.3 Resource-constrained causal intervention

Shoush and Dumas investigated prescriptive process monitoring under resource constraints using causal inference. Their work combines predictive information and estimated intervention effects to allocate scarce intervention resources.

Consequently, combining causal information with resource constraints is not a new general idea. Our review caps concern opportunities to evaluate and potentially update a model. They differ from limits on the number of interventions delivered to individual cases. This distinction clarifies the evaluation setting but does not independently establish originality.

### 2.4 Candidate gap and study positioning

The candidate gap concerns the incremental decision value of monitoring information when adaptation procedures are held common.

A richer monitoring signal can change an alert without changing a treatment decision. Its downstream value depends on whether a review occurs, whether the candidate policy passes the acceptance gate and whether sufficient future decision opportunities remain. Finite review caps can also make early alerts costly by consuming capacity before later changes.

Our study examines these relationships through two completed exploratory comparisons:

1. A signal ablation separating subgroup treatment-effect statistics from a between-group treatment-assignment-rate contrast.
2. A comparison of alert-triggered consecutive reviews with prospectively specified fixed review calendars.

The experiments share initial models, candidate-learning procedures, update gates and simulated streams within each comparison. Independently held-out stable streams assess the achieved alert rates of the monitoring rules. Common calibration targets are distinguished from exactly equal achieved false-alert rates, and equal review caps are distinguished from equal realized workload.

The potential contribution is therefore a controlled empirical evaluation of monitoring information and adaptation timing. Signal ablation, periodic review and causal monitoring are not individually claimed as inventions.

### 2.5 Resource-aware model updating and closest-design comparison

Piaseczny et al. (2025) introduced RCCDA, a model-update policy for concept drift under resource constraints. Their formulation balances model loss and update cost using a time-average resource budget and a virtual queue (Sections 3–4 and Algorithm 1). Thus resource-aware update timing is established prior work. The inspected formulation concerns prediction loss and model updates; our evaluation concerns oracle-relative net treatment benefit and distinguishes a review from an accepted model update. These are differences in objective and experimental organization, not proof that finite budgets or review timing are new.

Berrevoets et al. (2022, Section 5.3) provide an especially important boundary. Their ADWIN-triggered uplift-random-forest comparator recollects data and retrains following drift. They discuss poor downstream performance despite detection, and adverse effects of excessive detector sensitivity. Therefore, neither the general distinction between detection and useful adaptation nor the possibility of harmful sensitivity is introduced by this study. Their Equation 9 measures disagreement with an oracle action; our loss weights mistakes by foregone net treatment benefit. Our comparisons also retain a common candidate estimator and acceptance gate while separating monitoring additions.

| Closest evidence inspected | Established overlap | Difference in the present extensions | Remaining uncertainty |
| --- | --- | --- | --- |
| Berrevoets et al. (2022), Section 5.3 and Equation 9 | Treatment decisions under drift; ADWIN-triggered retraining; oracle-action evaluation; detection/adaptation limitations | Paired monitoring-signal ablation with common candidate estimation and acceptance gate; magnitude-weighted treatment-policy loss | A design difference alone does not demonstrate a sufficiently important research gap |
| RCCDA (2025), Sections 3–4 and Algorithm 1 | Resource-aware update timing, model-loss optimization and cost control | Treatment-policy opportunity loss; review events distinguished from accepted updates under fixed review caps | No direct comparison with an implemented RCCDA controller was performed; its general resource framework is not claimed to exclude finite-horizon budgets |
| OnlineCML example 08 | ADWIN monitoring of causal pseudo-outcomes and reset-on-drift estimation | Joint signal ablation, frozen calibration and common review/update procedures | Only selected public materials were inspected; complete manuscript overlap is unresolved |
| CausalStream accessible abstract and first-page preview | Streaming causal inference and incremental doubly robust estimation | The present evaluation's exact joint comparison is not established by the inspected preview | The full manuscript was unavailable; its design elements must not be labelled absent |

The narrow candidate contribution is an empirical attribution of the incremental policy value of subgroup monitoring under a specified common adaptation procedure. The main ablation found no observed incremental benefit, and the fresh schedule study documented occasional adverse outcomes. The contribution is not merely that timing matters, and the results do not establish that subgroup monitoring is generally unhelpful. A defensible novelty argument still requires checking whether the closest literature already provides substantially the same comparison and insight.

Evidence scope: these paragraphs reflect targeted inspection of the identified sections and author documentation. They are not an exhaustive full-text review of the entire corpus. No new benchmark was run for this revision.

## 3. Methods

### 3.1 Simulation setting

Each simulated stream contained 12 windows of 1,000 customers. Five scenarios were evaluated: stable conditions, covariate shift, treatment-assignment shift, treatment-response shift and opposing subgroup treatment-effect changes. Changes began at window 7 in the four shifted scenarios.

The customer features were age and previous spending. Subgroups were defined as younger customers aged below 35 years and older customers aged 35 years or above.

Baseline treatment effects were 40 for younger customers and 15 for older customers. In the response-shift scenario, the younger-group effect decreased to 5 while the older-group effect remained 15.

In the opposing-change scenario, the younger-group effect decreased from 40 to 5. The older-group effect increased to preserve the population-average treatment effect in expectation. Specifically, with baseline younger-group proportion q = 17/48, the older-group postchange effect was 15 + 35q/(1−q). Finite-window sample averages were not constrained to remain identical.

Treatment decisions used an assumed treatment cost of 10. Synthetic treatment effects were reserved for offline evaluation and were not supplied to the monitoring rules, model fitting or update-acceptance gate.

Labels were immediately available. Logged treatment assignment was exogenous: recommendations from the evaluated policies did not alter subsequent simulated data.

Each monitoring window independently generated customers using a random-number generator initialized from the evaluation seed and window index.

The baseline probability of belonging to the younger group was 17/48 (approximately 35.4%). Ages were sampled uniformly from integers 18–34 for younger customers and 35–65 for older customers. In the covariate-shift scenario, the younger-group probability increased to 0.65 from window 7; within-group age distributions remained unchanged.

Previous spending was sampled from a normal distribution with mean 200 and standard deviation 60, with negative values clipped to zero.

Treatment assignment followed a Bernoulli distribution with probability 0.5 under baseline conditions. In the assignment-shift scenario, this probability changed from window 7 to 0.2 for younger customers and 0.8 for older customers. These known assignment probabilities were available to the AIPW calculations.

The observed outcome was generated as:

Y = 50 + 0.4 × previous spending + T × τ(age, window, scenario) + ε,

where T denotes binary treatment assignment, τ denotes the scenario-specific treatment effect, and ε was independent normally distributed noise with mean zero and standard deviation 20.

The stable scenario retained baseline conditions throughout. The covariate and assignment scenarios retained baseline subgroup treatment effects. Response and opposing-effect changes followed the trajectories described in Section 3.1.

### 3.2 Initial model and monitoring variants

The original 1,000-customer baseline dataset was divided into 800 training observations and 200 test observations using an unstratified 80/20 split with random state 42. All arms shared one initial T-learner, fitted on the training observations using random-forest outcome models with seed 42. The evaluation was therefore conditional on this initial fitted model. Each outcome model in the T-learner used a random forest with 100 trees, a minimum leaf size of five and one computational worker. The model received age and previous spending as predictors. Separate models were fitted to treated and untreated observations.

The signal-ablation experiment compared four variants:

- M1: conventional feature, assignment, outcome and residual statistics, together with an aggregate augmented inverse-probability-weighted (AIPW) treatment-effect statistic.
- M2-A: M1 plus two subgroup AIPW treatment-effect means.
- M2-B: M1 plus the younger-minus-older treatment-assignment-rate contrast.
- M2-FULL: M1 plus both additions.

M1 already included the overall treatment-assignment rate. M2-B added a between-group contrast rather than introducing assignment monitoring for the first time.

Each arm used the maximum standardized score over its specified monitoring statistics. Explanation diagnostics were recorded separately and did not enter these four monitoring scores.

### 3.2.1 Treatment-effect pseudo-outcomes and signal definitions

Let T_i denote logged treatment, Y_i the observed outcome, p_i the known randomized treatment probability, and μ̂_0(X_i) and μ̂_1(X_i) the frozen baseline outcome predictions. The AIPW pseudo-outcome was

$$
\psi_i=\hat\mu_1(X_i)-\hat\mu_0(X_i)
+\frac{T_i\{Y_i-\hat\mu_1(X_i)\}}{p_i}
-\frac{(1-T_i)\{Y_i-\hat\mu_0(X_i)\}}{1-p_i}.
$$

Aggregate and subgroup monitoring statistics were the corresponding sample means of ψ_i. These were observed-data statistics using known logging probabilities, not averages of synthetic true effects. The gate's AIPW helper rejected nonfinite propensities and probabilities outside the open interval (0,1).

The observed-treatment residual was r_i = Y_i − μ̂_{T_i}(X_i). The nine conventional statistics were age mean and sample standard deviation; spending mean and sample standard deviation; overall treatment rate; outcome mean and sample variance; residual mean; and the residual second moment, n⁻¹Σr_i². The residual second moment was not a centered residual variance. Sample standard deviations and outcome variance used denominator n−1.

| Arm | Statistics entering its maximum score | Count |
| --- | --- | ---: |
| M1 | Nine conventional statistics and the aggregate mean of ψ_i | 10 |
| M2-A | M1 and the younger- and older-group means of ψ_i | 12 |
| M2-B | M1 and the younger-minus-older treatment-rate contrast | 11 |
| M2-FULL | M1, both subgroup means and the treatment-rate contrast | 13 |

Outcome predictions used for monitoring remained frozen at the initial baseline models. Updating an arm's decision model did not reset its monitoring reference. Shapley summaries were computed for diagnostics but excluded from all four score definitions.

### 3.3 Calibration and independent stable-run assessment

The ablation experiment used 100 stable streams to estimate monitoring centers and scales, followed by 1,000 separate stable calibration streams.

For statistic j, the center c_j was its arithmetic mean across all 1,200 windows from the 100 stable scale-estimation streams. Its scale s_j was the sample standard deviation across those windows, floored at 10⁻⁸. The score for arm m in window t was

$$
S_{m,t}=\max_{j\in J_m}\left|\frac{v_{t,j}-c_j}{s_j}\right|,
$$

where J_m is the arm's specified statistic set. Scores were two-sided absolute standardized deviations. Centers, scales and thresholds remained fixed during evaluation. An alert required a score strictly greater than its arm's threshold, subject to the issued-alert cap.

Each arm's threshold was the empirical higher 95th percentile of its calibration-stream maximum scores across the 12-window horizon. This targeted a common 5% probability of at least one alert per stable stream.

A further 200 independent stable streams assessed achieved any-alert rates. Thresholds were not retuned using these held-out results or the evaluation outcomes.

The scale, calibration, held-out stable and evaluation seed ranges were separate. The evaluation used seeds 340000–340099, paired across monitoring variants, scenarios and review caps.

### 3.4 Alert-triggered reviews and model updates

Each monitoring arm could issue at most two alerts per stream. The first issued alert initiated consecutive model reviews, including a review in the triggering window, until the review cap or stream horizon was reached. Subsequent alerts did not extend the review schedule.

Review caps were 2, 4 and 8. A cap represented a maximum number of reviews rather than a guarantee of equal realized workload.

At each reviewed window, observations were split into 70% candidate-training data and 30% held-out gate data, stratified by subgroup and treatment assignment. Candidate models and gate data were shared across arms, while each arm maintained its own incumbent model.

Candidate and incumbent policies were compared using AIPW net-benefit pseudo-outcomes calculated with the frozen baseline nuisance models. An update was accepted when the estimated mean gain minus 1.96 standard errors was greater than zero.

For a held-out gate observation, define d_i as the candidate action minus the incumbent action, with each action equal to one when its estimated treatment effect exceeded cost 10. The estimated gain observation was g_i = d_i(ψ_i − 10), using frozen baseline nuisance predictions in ψ_i. The gate accepted the candidate if

$$
\bar g-1.96\frac{s_g}{\sqrt{n_{\mathrm{gate}}}}>0,
$$

where s_g is the sample standard deviation of the gain observations. This comparison evaluated policy value differences rather than treatment-effect prediction error. Candidate fitting and the stratified split used random state equal to the stream seed plus the window index.

Accepted updates affected decisions from the following window. A review did not automatically produce an update. The repeated pointwise acceptance rule did not provide a sequential-safety guarantee.

### 3.5 Fixed-calendar comparison

A separate experiment compared the four frozen monitoring variants with a PERIODIC arm using prospectively specified review calendars:

| Review cap | Review windows |
| --- | --- |
| 2 | 4, 8 |
| 4 | 3, 6, 9, 12 |
| 8 | 1, 3, 4, 6, 7, 9, 10, 12 |

PERIODIC used the same candidate estimator, training/gate split and acceptance rule. It issued no alerts and had no applicable change-detection-delay endpoint.

Reviews in window 12 counted toward workload, although accepted updates could not improve decisions within the observed horizon.

The experiment reused the frozen monitoring calibration and evaluated fresh seeds 350000–350099. The achieved stable-run alert rates from the previous experiment remained calibration diagnostics, rather than new independent evidence.

### 3.6 Outcomes and analysis

The principal measured outcome was cumulative period-average oracle-relative net-benefit regret over windows 7–12.

For customer i, true treatment effect τ_i, treatment cost c and binary policy action a_i, the offline loss was:

max(τ_i − c, 0) − a_i(τ_i − c).

Customer losses were averaged within each window and summed across the postchange evaluation horizon. These units represent simulated net-benefit opportunity loss, not total company profit. For stable streams, windows 7–12 provided the corresponding comparison horizon without an actual change.

Additional outcomes included prechange regret, harmful-treatment rate, alerts, reviews, accepted updates, detection probability and detection delay conditional on detection. Detection was not applicable to stable streams or the PERIODIC arm.

Both experiments evaluated 100 seeds per scenario across five scenarios and three review caps. Repeated arms and caps were paired evaluations, not independent simulation units.

Paired mean differences and pointwise 95% percentile-bootstrap intervals used 5,000 resamples. Analyses were exploratory and unadjusted for multiplicity. The replication count was pragmatic rather than based on a formal power calculation.

### 3.7 Provenance and verification

Code and protocols were committed before evaluation. Run records preserved configuration, source snapshots, hashes, seed allocations and completion status.

The ablation audit reconciled 72,000 period rows and 6,000 method-budget run rows. The schedule-comparison audit reconciled 90,000 period rows and 7,500 method-budget run rows.

Checks covered saved-output consistency, aggregation, review schedules, alert caps, recorded gate acceptance, summary statistics and paired bootstrap calculations. They did not independently reproduce every random-forest fit or reconstruct every customer's action from saved predictions.

## 4. Results

### 4.1 Incremental monitoring signals

In the main ablation experiment, all observed seed-wise postchange-regret differences between the additional-signal variants and M1 were exactly zero across the evaluated scenarios and review caps.

Monitoring scores were not identical. Assignment-contrast variants also produced some different alert and review events, but these differences did not change accepted-update indicators or recorded policy regret.

In the assignment-shift scenario, mean detection delay was 0.02 windows for M1 and M2-A, compared with zero for M2-B and M2-FULL. This small detection advantage did not translate into lower regret.

In the covariate, response and opposing scenarios, every arm already detected change in the first shifted window, leaving no earlier window-level detection opportunity in those evaluated streams.

Held-out stable any-alert rates were 5/200 (2.5%) for M1 and M2-B, and 7/200 (3.5%) for M2-A and M2-FULL. Thus a common calibration target did not yield exactly equal achieved false-alert rates.

The zero paired bootstrap intervals reflected identical observed differences. They did not establish population equivalence.

### 4.2 Alert-triggered versus fixed-calendar reviews

M1 had lower mean postchange regret than the selected fixed calendars in the response and opposing-change scenarios.

| Scenario | Cap | M1 regret | PERIODIC regret | M1 minus PERIODIC | Descriptive 95% interval |
| --- | ---: | ---: | ---: | ---: | --- |
| Stable | 2 | 5.711900 | 5.688600 | +0.023300 | [0.000000, 0.057356] |
| Stable | 4 | 5.712000 | 5.650300 | +0.061700 | [0.002499, 0.134601] |
| Stable | 8 | 5.712000 | 5.620700 | +0.091300 | [0.023447, 0.171054] |
| Covariate | 2 | 3.085450 | 3.084450 | +0.001000 | [−0.015350, 0.014350] |
| Covariate | 4 | 3.052200 | 3.050850 | +0.001350 | [−0.029151, 0.032551] |
| Covariate | 8 | 3.050050 | 3.055850 | −0.005800 | [−0.036952, 0.024755] |
| Assignment | 2 | 5.681050 | 5.682700 | −0.001650 | [−0.033601, 0.024400] |
| Assignment | 4 | 5.669700 | 5.657850 | +0.011850 | [−0.052651, 0.083010] |
| Assignment | 8 | 5.655900 | 5.621800 | +0.034100 | [−0.032100, 0.106451] |
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

### 4.3 Adverse additional-signal findings

In the fresh schedule-comparison seed set, added subgroup monitoring again provided no observed regret improvement over M1 and occasionally increased regret.

M2-FULL-minus-M1 mean differences were +0.00785 for covariate shift at cap 2, +0.506634 for opposing changes at cap 2 and +0.0036 for stable streams at cap 8. Other cells were zero.

Recorded cases showed early alerts consuming reviews before a later useful update opportunity. One stable-stream case also showed that an update accepted by the estimated gate could increase offline oracle-relative loss.

These cases illustrate possible failure mechanisms under the specified controller; they do not establish universal harm from subgroup monitoring.

## 5. Discussion and limitations

The completed experiments distinguish monitoring differences from decision improvements. Additional signals sometimes changed alerts or reviews without improving accepted updates or treatment-policy regret.

Review timing affected outcomes, but its usefulness depended on change timing, available review opportunities and the common acceptance gate. Early alerts could exhaust scarce resources, while spacing could delay helpful adaptation.

The findings are conditional on a synthetic generator, one initial fitted model, immediate labels, exogenous logging, a fixed change onset, a finite horizon, selected review calendars and one update-acceptance rule. They do not establish real-world profitability, deployment safety or robustness across model initializations.

M1 combined conventional and aggregate causal statistics. The two main extensions did not include a purely conventional M0 arm. Therefore, their results cannot isolate the overall benefit of adding causal information to conventional monitoring.

Explanation statistics remained offline diagnostics. These experiments do not establish an explanation-stability benefit.

The interval estimates were exploratory and pointwise, without multiplicity adjustment or a prespecified equivalence margin. Null differences should not be interpreted as proof of equivalence.

### 5.1 Literature coverage and contribution uncertainty

The existing corpus contains 100 records; it must not be described as 100 completed full-text reviews. Nine particularly relevant papers were previously selected, of which seven received selective full-text inspection. The complete CausalStream and OnlineCML manuscripts remained unavailable.

The exact controlled comparison remains a plausible evaluation contribution rather than a verified absence in prior research. Before submission, the literature assessment must also reconcile closely related work on resource-aware model updating and retraining timing, including retraining-timing studies beyond the targeted RCCDA comparison in Section 2.5.

No claim of being the first, uniquely novel or universally superior is supported. Supervisor assessment and a source-verified comparison with the closest studies remain necessary to judge whether the contribution is sufficient for the intended manuscript and venue.

## 6. Conclusion

Under the evaluated synthetic conditions, additional subgroup-effect and assignment-contrast signals did not reduce regret beyond M1 in the main ablation. A fresh comparison identified occasional adverse subgroup-monitoring outcomes. Alert-triggered reviews reduced loss relative to the selected fixed calendars under treatment-effect changes, while calendar reviews had lower mean loss in stable conditions. These results support evaluating monitoring information together with adaptation timing and realized review use. They do not establish causal-monitoring superiority over a conventional-only baseline, universal controller superiority or real-world benefit.

## Working references — verification pending

These records identify sources used in the existing audit. Complete bibliographic metadata and publication status must be verified before submission.

- Berrevoets, J., Verboven, S., and Verbeke, W. (2022). Treatment effect optimisation in dynamic environments. Journal of Causal Inference, 10, 106–122. https://doi.org/10.1515/jci-2020-0009

- El quammah et al. (2026). CausalStream: A General Architecture for Real-Time Causal Inference on Data Streams. Concurrency and Computation: Practice and Experience. https://doi.org/10.1002/cpe.70756
  Evidence inspected: abstract and first-page preview; complete manuscript unavailable.

- Hammad, A. T. (2026). OnlineCML: A Python Library for Online Causal Machine Learning. SSRN record 6598878. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6598878
  Evidence inspected: available descriptions, selected author documentation and repository examples; complete manuscript unavailable. Peer-reviewed publication status not established.

- OnlineCML author documentation:
  https://athammad.github.io/onlinecml/examples/08_concept_drift/
  https://athammad.github.io/onlinecml/examples/05_policy_exploration/
  Repository inspection anchor: commit 0b5644eb076ef13da52898ad0b22a08db5ef4335.

- Shoush and Dumas. Prescriptive Process Monitoring Under Resource Constraints: A Causal Inference Approach. https://doi.org/10.1007/978-3-030-98581-3_14

- Piaseczny, A., Chowdhury Shisher, M. K., Wang, S., and Brinton, C. G. (2025). RCCDA: Adaptive Model Updates in the Presence of Concept Drift under a Constrained Resource Budget. Advances in Neural Information Processing Systems, 38. https://doi.org/10.52202/085713-5183
  Official proceedings and author listing: https://proceedings.neurips.cc/paper_files/paper/2025/hash/e3d1b6d954a204267fd334cbaf9cd4af-Abstract-Conference.html
  Full paper, targeted Sections 3–4 and Algorithm 1: https://proceedings.neurips.cc/paper_files/paper/2025/file/e3d1b6d954a204267fd334cbaf9cd4af-Paper-Conference.pdf

## Appendix A. Review-spacing engineering check

A subsequent engineering check compared consecutive reviews with score-conditioned spaced reviews using only two development seeds per scenario.

Spacing generally produced unchanged regret. It reduced mean regret by 0.085 in the covariate-shift setting at cap 4, but increased mean regret by approximately 2.374919 in the opposing-change scenario at each review cap. These patterns occurred for both M1 and FULL.

In one opposing-change seed, spacing delayed acceptance of a helpful update from window 8 to window 9. This delayed adaptation increased loss.

This small development check is reported separately from the 100-seed studies. It does not support inferential claims or establish general controller superiority.

## Appendix B. Editorial and reproducibility checklist

- Complete bibliographic verification and primary methodological citations. A targeted RCCDA comparison is now in Section 2.5; extend the closest-work comparison to other retraining-timing studies before finalizing the gap.
- Preserve the full-text access limitation for CausalStream and OnlineCML; seek institutional or author copies before stronger overlap claims.
- Estimator, monitoring and gate equations have now been transcribed from the uploaded ablation source. Verify the final manuscript against the archived source snapshots and add primary methodological citations.
- Add the complete saved contrasts, actual review counts, accepted updates, harm and detection summaries to supplementary tables. The 15-row table here covers M1 versus PERIODIC; it is not the full set of 75 schedule-comparison contrasts.
- Initial training/test allocation is described in Section 3.2. Add software versions, source hashes, complete seed ranges and run locations to a reproducibility appendix.
- Reconcile any inclusion of older M0/M1/M2/M3 studies separately; do not merge their evidence with these extensions without documenting design differences.
- Obtain supervisor feedback on scope, title and the sufficiency of the contribution before journal selection or submission.
