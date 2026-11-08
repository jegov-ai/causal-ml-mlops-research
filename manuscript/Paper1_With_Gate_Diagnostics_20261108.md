# Evaluating Causal-Aware Monitoring in MLOps: Decision Robustness Under Distribution Shift and Operational Constraints

Author: Jegan Govinda (Jegov)

## Abstract

Monitoring information improves treatment decisions only if it leads to useful adaptation. We evaluate the incremental decision value of causal monitoring statistics and model-review timing in a synthetic treatment-policy benchmark. Two prospectively specified exploratory evaluations used 12 windows of 1,000 customers, five scenarios and review caps of 2, 4 and 8, with 100 paired stream seeds per scenario and one initial random-forest T-learner. A signal ablation separated subgroup-effect and assignment-contrast statistics from a baseline combining conventional and aggregate causal monitoring. A separate evaluation compared alert-triggered reviews with fixed calendars under common candidate estimators and update gates.

The main ablation produced identical observed regret across variants. The calendar study found no incremental subgroup-monitoring benefit and occasional adverse outcomes. Alert-triggered reviews reduced loss relative to the selected calendars under treatment-effect shifts, but post-hoc comparisons showed lower mean loss for treat-all across all calendar-study scenario/cap cells.

A separately specified development check varied three initial training/fitting realizations and shift onsets 4, 7 and 10 using three stream seeds per scenario. Conventional, aggregate-causal and full monitors again produced identical recorded loss. Adaptive policies beat treat-all on mean loss in early opposing-shift cells, with the same benefit achieved by conventional monitoring.

A retrospective replay reproduced the development trajectories and found both helpful and harmful candidates among rejected reviews, indicating that detection alone did not determine adaptation. These dependent diagnostics are explanatory rather than independent validation.

The results document no observed incremental policy benefit from additional causal signals in this benchmark and show why calendar-relative gains require simple-policy comparisons. The development check is descriptive, not population-equivalence evidence. Conclusions remain conditional on the generator, learner, calibration, gate, horizon and review rules.

Keywords: causal machine learning; MLOps; distribution shift; treatment-policy regret; model monitoring; review budgets.

## 1. Introduction

A machine-learning model used to support treatment or product decisions may encounter changes in customer characteristics, treatment assignment or treatment response. In a discount-allocation setting, these changes raise distinct questions. A change in the customer population may affect the distribution of predictions, whereas a change in treatment response may alter whether offering the discount is beneficial. Monitoring these quantities can inform model review, but detecting a change does not itself determine whether a replacement model should be deployed.

This distinction motivates the present evaluation. A monitoring signal affects decisions through a sequence of operational steps: an alert initiates a review, a candidate model is trained, an acceptance rule compares candidate and incumbent policies, and an accepted update changes subsequent decisions. Additional monitoring information may have little incremental value if an existing monitor already triggers a timely review or if the available candidate does not pass the update gate. Conversely, an early alert may consume limited review opportunities before a later change.

We implement a synthetic causal-ML monitoring benchmark in which a T-learner estimates heterogeneous treatment effects and recommends treatment when the estimated effect exceeds an assumed cost. The benchmark separates logged treatment assignment from policy recommendations and reserves known synthetic effects for offline evaluation. This permits calculation of oracle-relative treatment-policy opportunity loss while keeping synthetic truth outside the monitoring and adaptation rules.

Existing research already addresses treatment decisions in dynamic environments, causal estimation on streams, monitoring-triggered adaptation and resource-constrained interventions. For example, Berrevoets et al. (2022) evaluated treatment-effect optimisation under changing conditions. OnlineCML's inspected public examples demonstrate causal pseudo-outcome monitoring and estimator reset. These precedents rule out a broad claim that combining causal estimation, drift monitoring and regret evaluation is itself new. The narrower question is whether a controlled comparison can clarify the incremental value of monitoring signals and review timing under common adaptation procedures.

We examine two research questions within the scope of these extensions. First, does adding subgroup treatment-effect monitoring, a between-group assignment-rate contrast, or both reduce cumulative treatment-policy regret beyond a baseline that already includes conventional statistics and aggregate causal-effect monitoring? Second, how does alert-triggered review timing compare with prospectively specified fixed calendars when candidate estimation, update acceptance and maximum review caps are shared?

The two 100-seed evaluations retain their original questions and analysis plans. A later, separately specified engineering check examined sensitivity to initial training/fitting realization and shift onset and included a conventional-only M0 arm. Its small development sample is not pooled with the earlier evaluations or promoted to a confirmatory test.

The first experiment compared four monitoring variants. M1 combined conventional statistics with an aggregate AIPW treatment-effect statistic. M2-A added subgroup treatment-effect statistics, M2-B added a between-group assignment-rate contrast, and M2-FULL added both. The second experiment retained these variants and introduced fixed-calendar reviews. Each experiment evaluated five scenarios and three review caps using 100 paired seeds per scenario.

The principal measured outcome was cumulative period-average oracle-relative net-benefit regret over the latter six windows. Alerts, reviews, accepted updates, harmful-treatment rates and detection timing provided complementary operational evidence. Alert thresholds targeted a common stable-stream any-alert probability, with independent held-out assessment. Equal intended calibration targets were distinguished from equal achieved false-alert rates, and common review caps were distinguished from equal realized workload.

The completed results did not show an incremental regret benefit from the additional monitoring signals. The main ablation yielded identical observed regret across variants, while the fresh calendar comparison included occasional adverse subgroup-monitoring outcomes. Alert-triggered M1 reviews reduced loss relative to the selected calendars under treatment-effect changes, but calendar reviews performed better in stable settings. A separate small review-spacing development check also demonstrated that delaying reviews could postpone a useful update. These findings are retained together rather than selecting only favorable comparisons.

The intended contribution is a reproducible, controlled empirical evaluation of how monitoring information and review opportunities translate into downstream policy performance. It is not a new treatment-effect estimator or drift detector. The two 100-seed main studies do not compare causal-statistic monitoring against a purely conventional monitor because their baseline, M1, already contains aggregate causal information. A separate small model/onset development check includes conventional M0 and records equal policy loss across M0, M1 and M2-FULL; this limited check does not establish population equivalence. These evaluations also do not establish an explanation-stability benefit; explanation quantities remain offline diagnostics in these extensions.

The study is an exploratory evaluation of incremental monitoring value under specified adaptation procedures. Conclusions concern the implemented benchmark; they do not establish general superiority or equivalence of monitoring methods. Access limitations affecting the closest-study comparison are described in Section 5.1.

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

Evidence scope: the comparison reflects targeted inspection of the identified sections and author documentation, rather than an exhaustive systematic review.

### 2.6 Average and subgroup causal monitoring under performativity

Feng et al. (2024) compare six monitoring procedures combining three monitoring criteria with observational or interventional data. Section 4.1 distinguishes average and subgroup-specific causal positive/negative predictive values, as well as a stronger conditional calibration criterion; Section 4.3 develops monitoring procedures. This directly establishes that contrasting average and subgroup causal monitoring is not, on its own, our contribution. Their monitored quantities are causal classification-performance criteria, whereas ours are aggregate and subgroup treatment-effect pseudo-outcome means combined with conventional statistics. Our completed extensions measure the incremental downstream opportunity loss after common model reviews and held-out update acceptance. This difference supports a bounded empirical extension; it does not establish priority over all literature. Our exogenous-logging simulation also does not solve the performativity problem motivating their study.

A further close preprint is Dasari (2026), When to Retrain: An Empirical Study of Retraining Policies for Streaming ML Under Concept Drift, Budget, and Latency Constraints (arXiv:2608.19488). Only abstract-level evidence was available through the retrieved arXiv search record; direct manuscript and repository access failed in this session. The record identifies an empirical comparison of retraining policies under budgets and latency. This reinforces that a generic calendar-versus-triggered comparison is not a defensible novelty claim. Its full experimental overlap remains unresolved; no full-text exclusion is asserted.

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

The initial dataset was generated separately from the monitoring windows. Using NumPy default_rng(42), the code sampled 1,000 ages uniformly from the integers 18–65, then clipped normal spending with mean 200 and standard deviation 60, Bernoulli treatment with probability 0.5, and normal outcome noise with standard deviation 20. Outcomes followed the equation in Section 3.1 with baseline effects 40 and 15. This direct age sampling differs from the subgroup-first window sampling, although both give a population younger-group probability of 17/48. The exact draw order is retained in original_data() in the archived integrated_causal_monitoring_v2_xai.py source snapshot.

The original 1,000-customer baseline dataset was divided into 800 training observations and 200 test observations using an unstratified 80/20 split with random state 42. All arms shared one initial T-learner, fitted on the training observations using random-forest outcome models with seed 42 (Breiman, 2001; Künzel et al., 2019). The evaluation was therefore conditional on this initial fitted model. Each outcome model in the T-learner used a random forest with 100 trees, a minimum leaf size of five and one computational worker. The model received age and previous spending as predictors. Separate models were fitted to treated and untreated observations.

The signal-ablation experiment compared four variants:

- M1: conventional feature, assignment, outcome and residual statistics, together with an aggregate augmented inverse-probability-weighted (AIPW) treatment-effect statistic.
- M2-A: M1 plus two subgroup AIPW treatment-effect means.
- M2-B: M1 plus the younger-minus-older treatment-assignment-rate contrast.
- M2-FULL: M1 plus both additions.

M1 already included the overall treatment-assignment rate. M2-B added a between-group contrast rather than introducing assignment monitoring for the first time.

Each arm used the maximum standardized score over its specified monitoring statistics. Explanation diagnostics were recorded separately and did not enter these four monitoring scores.

### 3.2.1 Treatment-effect pseudo-outcomes and signal definitions

Let T_i denote logged treatment, Y_i the observed outcome, p_i the known randomized treatment probability, and μ̂_0(X_i) and μ̂_1(X_i) the frozen baseline outcome predictions. Doubly robust policy evaluation is established methodology (Dudík et al., 2011). The implemented binary-treatment AIPW pseudo-outcome was

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

A further 200 independent stable streams assessed achieved any-alert rates, with Wilson score intervals (Wilson, 1927). Thresholds were not retuned using these held-out results or the evaluation outcomes.

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

Additional outcomes included prechange regret, harmful-treatment rate, alerts, reviews, accepted updates, detection probability and detection delay conditional on detection. Detection was not applicable to stable streams or the PERIODIC arm. Detection was the first issued alert at or after the known shift onset, not simply a raw threshold crossing. The two-alert cap applied across the entire stream, including prechange alerts. An early alert was retained as a false alert and did not count as postchange detection; exhausted alert capacity could prevent later detection. Delay equalled the first postchange issued-alert window minus the onset window. Zero delay therefore means detection at the end of the first shifted window. Streams without an issued postchange alert were classified as missed changes; their delays were undefined and excluded from conditional mean delay. Detection rates used all shifted streams as the denominator. Onset was used only for offline event scoring, not by the monitoring controller.

Both experiments evaluated 100 seeds per scenario across five scenarios and three review caps. Repeated arms and caps were paired evaluations, not independent simulation units.

Paired mean differences and pointwise 95% percentile-bootstrap intervals used 5,000 resamples. Resampling follows the bootstrap framework (Efron, 1979); the implementation resampled paired seed differences and took percentile endpoints. Analyses were exploratory and unadjusted for multiplicity. The replication count was pragmatic rather than based on a formal power calculation.

### 3.7 Provenance and verification

Code and protocols were committed before evaluation. Run records preserved configuration, source snapshots, hashes, seed allocations and completion status.

The ablation audit reconciled 72,000 period rows and 6,000 method-budget run rows. The schedule-comparison audit reconciled 90,000 period rows and 7,500 method-budget run rows.

Checks covered saved-output consistency, aggregation, review schedules, alert caps, recorded gate acceptance, summary statistics and paired bootstrap calculations. They did not independently reproduce every random-forest fit or reconstruct every customer's action from saved predictions.

### 3.8 Saved policy benchmarks and post-hoc diagnostic analysis

Each evaluated stream also recorded treat-all, treat-none and frozen-T-learner policy losses on the same observations. These benchmarks do not review or update models. Their postchange losses sum period means over windows 7–12, using the same oracle-relative scoring rule. Their source generation was part of the saved experiments, but the comprehensive paired comparisons reported in Section 4.4 were added after the prospective analyses and after preparation of review draft v6.

All five calendar-study arms were compared with all three benchmarks across five scenarios and three caps, yielding 225 post-hoc diagnostic contrasts. Seed-wise differences were bootstrapped with 5,000 resamples using RNG seed 20261103. These pointwise intervals are descriptive and unadjusted for multiplicity. These comparisons are not retroactively designated prospective outcomes. Full results are supplied in support/POSTHOC_SAVED_BENCHMARK_CONTRASTS_20261103.csv.

### 3.9 Separately specified model/onset development check

Following the prior studies and their critical review, the development protocol varied initial data/fitting seeds 42, 1042 and 2042 and shifted-scenario onsets 4, 7 and 10. Initial seeds changed both the generated 1,000-row training-source dataset and forest fitting randomness; the 800/200 split procedure remained fixed. This was a joint initial-training/fitting sensitivity check, not an isolated experiment on forest randomness.

The generator's baseline/postshift magnitudes, cost 10, 12-window horizon and 1,000-customer windows remained fixed. M0 used the nine conventional statistics; M1 added aggregate AIPW; M2-FULL added both subgroup means and the assignment-rate contrast. The fourth adaptive arm was PERIODIC with the original fixed calendars. Review caps, candidate/gate procedures, next-window updates and the three fixed policy benchmarks were preserved. No conventional-only comparison is retroactively added to the two earlier evaluations.

For each initial fit, stable centers/scales were estimated from 10 streams, thresholds from 40 calibration streams, and held-out alert rates from 20 further streams. The calibration and null allocations were engineering counts, not precise false-alert validation. Independent role namespaces began at 420010, 420100, 420200 and 420300, respectively. Three evaluation stream seeds (420300–420302) were paired across arms, caps, initial fits and onset views. Stable streams were evaluated once with a scoring marker of 7 rather than counted repeatedly under identical onsets.

The run contained 117 fit/scenario/onset/stream configurations, 1,404 method-budget run rows and 16,848 period rows. The 117 configurations are dependent factor evaluations, not 117 independent stream replications. Within each initial-fit/scenario/onset/cap cell, the reported difference averages its three stream-seed differences. No development p-values, inferential bootstrap intervals or population-equivalence claims were generated.

The development endpoint was mean period-average loss across the available post-onset windows, with cumulative loss and trajectories also saved. Mean-per-window scoring makes unequal horizons explicit but does not remove differences in remaining adaptation opportunities. Stable scoring used windows 7–12 without a real change. The earlier studies retain their original cumulative windows-7–12 endpoint; results are not pooled across studies.

The development runner recalculated calibration per initial fit and saved all comparisons against M0, M1, PERIODIC and the three fixed benchmarks specified by its protocol. Incumbent explanation audits were omitted; frozen live explanation summaries remained computed but excluded from monitor scores. Runtime therefore differs from the earlier XAI-heavy evaluations. The development run took 32.08 minutes, with 35 Windows unit tests passing before execution and 95 subsequent saved-output/provenance checks passing. These checks do not reproduce every model fit or individual action.

### 3.10 Retrospective diagnostic replay of update acceptance

After inspecting the development results, we replayed all 117 development configurations with the original data/fitting seeds, archived calibration and unchanged controller. An added read-only callback measured candidate and incumbent policy loss without supplying synthetic truth to the acceptance rule. Every original field in the 16,848 period records reconciled with the saved development run; floating comparisons used absolute and relative tolerances of 10⁻¹². This is retrospective explanation of exposed trajectories, not new independent evaluation.

At each review, candidate benefit was incumbent oracle regret minus candidate oracle regret on the same gate observations and, separately, the next simulated window. Positive values favor the candidate. Classification as helpful, harmful or tied used tolerance 10⁻¹⁰. Window-12 reviews had no next-window measurement. The next-window comparison holds both models fixed; it does not reconstruct an alternative future controller, identify population value or estimate total regret saved by changing acceptance. Repeated methods, caps, fits and onsets are dependent evaluations. No additional inferential tests were conducted.

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

### 4.4 Saved policy benchmarks: post-hoc diagnostic results

Treat-all had lower mean cumulative postchange regret than both M1 and PERIODIC in all 15 scenario/cap cells for each method in the calendar study. Treat-all was oracle-optimal by construction in stable, covariate and assignment scenarios because both subgroup effects exceeded cost 10. In response and opposing scenarios, its loss was positive, but remained below the adaptive-arm means. This is not a claim of uniform seed-wise or population dominance.

| Scenario | Cap | M1 loss | Treat-all loss | M1 minus treat-all |
| --- | ---: | ---: | ---: | ---: |
| assignment | 2 | 5.681050 | 0.000000 | 5.681050 |
| assignment | 4 | 5.669700 | 0.000000 | 5.669700 |
| assignment | 8 | 5.655900 | 0.000000 | 5.655900 |
| covariate | 2 | 3.085450 | 0.000000 | 3.085450 |
| covariate | 4 | 3.052200 | 0.000000 | 3.052200 |
| covariate | 8 | 3.050050 | 0.000000 | 3.050050 |
| opposing | 2 | 11.504052 | 10.659150 | 0.844902 |
| opposing | 4 | 11.345019 | 10.659150 | 0.685869 |
| opposing | 8 | 11.047568 | 10.659150 | 0.388418 |
| response | 2 | 15.489650 | 10.659150 | 4.830500 |
| response | 4 | 15.258100 | 10.659150 | 4.598950 |
| response | 8 | 15.193450 | 10.659150 | 4.534300 |
| stable | 2 | 5.711900 | 0.000000 | 5.711900 |
| stable | 4 | 5.712000 | 0.000000 | 5.712000 |
| stable | 8 | 5.712000 | 0.000000 | 5.712000 |

All 225 comparisons, including treat-none and the frozen T-learner, are supplied without selecting favorable contrasts. Their intervals are post-hoc diagnostics. M1's first shifted-window detection in all 100 opposing streams left no earlier window-level detection opportunity for additional subgroup signals. In the response scenario, at least one M1 update was accepted in only 16%, 24% and 32% of streams at caps 2, 4 and 8. These rates show that alerts and available reviews did not guarantee an accepted update; they do not identify whether candidate fitting or the gate caused the limited adaptation.

### 4.5 Model/onset development results

M1-minus-M0 and M2-FULL-minus-M1 regret differences were exactly zero in all 351 paired method-budget observations, for both cumulative and mean-per-window loss. These observations repeatedly use the same three evaluation seeds across factors. Their equality does not establish population equivalence or general causal-monitoring redundancy.

Relative to M0, M1 scores differed in 279 period rows but alert, review and accepted-update indicators did not differ. FULL scores differed in 1,872 period rows, and its alerts and reviews each differed in 18 rows; accepted-update indicators and recorded loss still agreed. These are repeated period/cap records, not independent incidents. Individual action arrays were not saved.

The following table summarizes all 117 initial-fit/scenario/onset/cap cell means, each computed from three stream seeds. The cells are dependent, so these tallies are neither significance tests nor equally weighted estimates of a population treatment effect. Numerical ties for nonzero comparisons use an absolute tolerance of 10⁻¹⁰.

| First policy minus comparator | Lower mean loss | Tied mean loss | Higher mean loss |
| --- | ---: | ---: | ---: |
| M2-FULL minus M1 | 0 | 117 | 0 |
| M1 minus M0 | 0 | 117 | 0 |
| M1 minus PERIODIC | 24 | 77 | 16 |
| M1 minus treat-all | 9 | 0 | 108 |
| M1 minus frozen initial policy | 33 | 84 | 0 |

All nine cell means favoring M1 over treat-all were opposing shifts at onset 4: three initial fits and three caps. M0 and FULL obtained the same loss, so the benefit cannot be attributed to adding causal statistics. The other 108 cell means favored treat-all. This qualifies, rather than contradicts, the earlier calendar-study result: that evaluation fixed onset at 7 and used a different stream-seed set. The studies must not be pooled or compared as though their only difference were onset.

M0 detected every covariate, response and opposing change in the first shifted window. Assignment changes were also detected in every evaluated stream, with at most one window of delay. Thus added signals had little or no earlier window-level detection opportunity. Per-fit held-out alert counts were 0/20, 2/20 and 0/20 for initial seeds 42, 1042 and 2042, respectively, for each of the three monitors. These small samples and shared streams do not certify equal achieved false-alert rates or a precise 5% target.

### 4.6 Retrospective diagnosis of candidate acceptance

The replay yielded 5,310 diagnostic review records, each reconciling with a recorded review and acceptance decision. M1 had 1,224 reviews: 92 accepted and 1,132 rejected. Among rejected reviews with a next window, 551 candidates reduced next-window oracle loss, 466 increased it and four tied; 111 rejected final-window reviews had no next-window endpoint. All 92 accepted M1 review records reduced next-window loss in this replay.

| M1 review decision | Helpful next window | Harmful next window | Tied | No next window |
| --- | ---: | ---: | ---: | ---: |
| Accepted | 92 | 0 | 0 | 0 |
| Rejected | 551 | 466 | 4 | 111 |

In response-shift records, 265 rejected candidates were helpful on the next window and seven harmful, while 27 rejected final-window reviews lacked a next-window endpoint. Seven accepted updates were helpful. Thus timely detection and review sometimes produced useful candidates that did not pass the estimated acceptance rule. These repeated records do not represent independent missed opportunities, and their potential gains cannot be summed as achievable future savings.

M0 had the same aggregate classification counts as M1. FULL had 554 helpful, 466 harmful and four tied rejected next-window comparisons, plus 108 rejected final-window reviews, and 92 helpful accepted comparisons. PERIODIC had 84 helpful and two harmful accepted next-window comparisons, plus five accepted final-window reviews. The two harmful records repeat one fit/seed/scenario/window at caps four and eight: fit 42, seed 420302, covariate scenario with onset 10, review at window 9. The candidate benefit was +0.05 on the gate sample but −0.065 on the next window. This illustrates that current-sample benefit need not persist across a shift.

The gate rejected both helpful and harmful candidates. These findings support a descriptive explanation involving update acceptance in the recorded trajectories; they do not justify removing the gate, establish a unique causal bottleneck or show incremental benefit from causal monitoring. Individual diagnostic action arrays were not saved, so consistency checks cannot independently reconstruct each reported candidate benefit from customer-level predictions.

## 5. Discussion and limitations

The completed experiments distinguish monitoring differences from decision improvements.

The comparison with fixed review calendars does not establish superiority over simple treatment policies. In the saved calendar-study streams, treating every customer had lower mean postchange opportunity loss than both M1 and PERIODIC at every evaluated cap and scenario. In stable, covariate and assignment scenarios, both subgroup effects exceeded the assumed cost, making treat-all the oracle action by construction. Under response and opposing changes, treat-all incurred positive regret but still had lower mean loss than the evaluated adaptive arms. Consequently, the observed benefit of alert-timed reviews is a relative improvement over the selected calendars within this benchmark, rather than evidence of a best-performing treatment strategy. These benchmark comparisons were added post hoc and are reported as descriptive diagnostics.

 Additional signals sometimes changed alerts or reviews without improving accepted updates or treatment-policy regret.

Review timing affected outcomes, but its usefulness depended on change timing, available review opportunities and the common acceptance gate. Early alerts could exhaust scarce resources, while spacing could delay helpful adaptation.

The two 100-seed evaluations condition on one initial fitted model and shift onset 7. The later development check considers three initial training/fitting realizations and three onsets, but only three evaluation stream seeds and small calibration/null allocations. It therefore provides limited descriptive sensitivity evidence, not broad robustness across learned models or a confirmatory conventional-versus-causal comparison. All findings remain conditional on a synthetic generator, immediate labels, exogenous logging, a finite horizon, selected calendars and one update gate. They do not establish real-world profitability or deployment safety.

M1 combined conventional and aggregate causal statistics. The two 100-seed extensions did not include M0, so they do not isolate the overall value of causal information over conventional monitoring. M0 appears only in the separately labelled development check, where its recorded loss matched M1 and FULL. That small check must not be used to claim a general absence of benefit from causal information.

Explanation statistics remained offline diagnostics. These experiments do not establish an explanation-stability benefit.

The interval estimates were exploratory and pointwise, without multiplicity adjustment or a prespecified equivalence margin. Null differences should not be interpreted as proof of equivalence.

### 5.1 Literature coverage and contribution uncertainty

The related-work comparison is targeted rather than systematic. Published studies already establish treatment decisions under drift, subgroup causal monitoring and resource-aware update timing. The empirical distinction examined here is the incremental policy value of specified monitoring statistics under shared candidate estimators, update acceptance and review caps. This experimental distinction should not be read as a claim that the broader ingredients or detection/adaptation limitations are new.

The complete CausalStream and OnlineCML manuscripts were unavailable through the access routes used. Claims about those studies are therefore limited to the abstracts, preview and selected author documentation identified in Section 2. Their complete experimental overlap remains unresolved. The same caution applies to the abstract-level Dasari record. Absence of an identical comparison from inspected materials is not evidence of absence from the literature.

### 5.2 Cross-study synthesis and empirical contribution

The contribution is a controlled evaluation of how additional monitoring statistics translate into treatment-policy performance under specified review and update procedures. The evidence supports three bounded findings: added signals had no incremental regret benefit in the main ablation; separate-seed calendar comparisons included occasional adverse subgroup-monitoring outcomes; and descriptive onset/model sensitivity retained equal loss across conventional and causal-statistic monitors while revealing conditional adaptation gains against fixed policies. No result establishes a new estimator, detector or universally superior controller.

The comparison exposes a benchmark boundary: conventional statistics already detected the studied treatment-effect changes promptly, and useful policy changes depended on the shared candidate-learning and acceptance process. These observations motivate reporting the full chain from score to alert, review, accepted update and policy loss. They do not identify a unique causal bottleneck, as the learner and gate were not independently ablated. The practical implication is to justify additional monitoring complexity through downstream policy comparisons, while retaining simple fixed policies and adaptation timing as explicit comparators.

These findings provide an exploratory account of the conditions under which additional monitoring statistics failed to change policy loss. Their interpretation depends on the detection ceiling, selected calendars, common learner and gate, and limited development replication. They motivate testing incremental decision value rather than assuming that additional monitored quantities will improve decisions.

## 6. Conclusion

In this controlled synthetic benchmark, richer causal monitoring statistics did not produce incremental regret reduction in the main signal ablation and occasionally worsened loss in a separate calendar-comparison seed set. Alert-triggered reviews improved on the selected calendars under treatment-effect shifts, but those gains did not outperform treat-all on mean loss in that calendar study. A separately specified small development check found equal recorded loss for M0, M1 and FULL across its initial-model and onset settings. Early opposing changes allowed adaptation to beat treat-all in some development cells, with the same benefit obtained by conventional monitoring. The evidence supports evaluating monitoring complexity through downstream policy outcomes, simple-policy comparators and actual review/update behavior. It does not establish general equivalence, causal-monitoring superiority or a universally best review strategy.

## References and evidence-limited records

Primary-method and related-work references used in this draft are listed below. Records explicitly marked evidence-limited do not represent full-text reviews; final journal formatting remains to be applied.

- Berrevoets, J., Verboven, S., and Verbeke, W. (2022). Treatment effect optimisation in dynamic environments. Journal of Causal Inference, 10(1), 106–122. https://doi.org/10.1515/jci-2020-0009

- El quammah et al. (2026). CausalStream: A General Architecture for Real-Time Causal Inference on Data Streams. Concurrency and Computation: Practice and Experience. https://doi.org/10.1002/cpe.70756
  Evidence inspected: abstract and first-page preview; complete manuscript unavailable.

- Hammad, A. T. (2026). OnlineCML: A Python Library for Online Causal Machine Learning. SSRN record 6598878. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6598878
  Evidence inspected: available descriptions, selected author documentation and repository examples; complete manuscript unavailable. Peer-reviewed publication status not established.

- OnlineCML author documentation:
  https://athammad.github.io/onlinecml/examples/08_concept_drift/
  https://athammad.github.io/onlinecml/examples/05_policy_exploration/
  Repository inspection anchor: commit 0b5644eb076ef13da52898ad0b22a08db5ef4335.

- Shoush, M., & Dumas, M. (2022). Prescriptive Process Monitoring Under Resource Constraints: A Causal Inference Approach. Process Mining Workshops, LNBIP 433, 180–193. https://doi.org/10.1007/978-3-030-98581-3_14

- Piaseczny, A., Chowdhury Shisher, M. K., Wang, S., and Brinton, C. G. (2025). RCCDA: Adaptive Model Updates in the Presence of Concept Drift under a Constrained Resource Budget. Advances in Neural Information Processing Systems, 38. https://doi.org/10.52202/085713-5183
  Official proceedings and author listing: https://proceedings.neurips.cc/paper_files/paper/2025/hash/e3d1b6d954a204267fd334cbaf9cd4af-Abstract-Conference.html
  Full paper, targeted Sections 3–4 and Algorithm 1: https://proceedings.neurips.cc/paper_files/paper/2025/file/e3d1b6d954a204267fd334cbaf9cd4af-Paper-Conference.pdf

- Feng, J., Subbaswamy, A., Gossmann, A., Singh, H., Sahiner, B., Kim, M.-O., Pennello, G. A., Petrick, N., Pirracchio, R., & Xia, F. (2024). Designing monitoring strategies for deployed machine learning algorithms: navigating performativity through a causal lens. Proceedings of the Third Conference on Causal Learning and Reasoning, PMLR 236, 587–608. https://proceedings.mlr.press/v236/feng24a.html

- Künzel, S. R., Sekhon, J. S., Bickel, P. J., & Yu, B. (2019). Metalearners for estimating heterogeneous treatment effects using machine learning. Proceedings of the National Academy of Sciences, 116(10), 4156–4165. https://doi.org/10.1073/pnas.1804597116

- Breiman, L. (2001). Random forests. Machine Learning, 45, 5–32. https://doi.org/10.1023/A:1010933404324

- Dudík, M., Langford, J., & Li, L. (2011). Doubly robust policy evaluation and learning. Proceedings of the 28th International Conference on Machine Learning. Official manuscript: https://icml.cc/2011/papers/554_icmlpaper.pdf

- Efron, B. (1979). Bootstrap methods: Another look at the jackknife. The Annals of Statistics, 7(1), 1–26. https://doi.org/10.1214/aos/1176344552

- Wilson, E. B. (1927). Probable inference, the law of succession, and statistical inference. Journal of the American Statistical Association, 22(158), 209–212. https://doi.org/10.1080/01621459.1927.10502953

- Dasari, S. (2026). When to Retrain: An Empirical Study of Retraining Policies for Streaming ML Under Concept Drift, Budget, and Latency Constraints. arXiv:2608.19488. https://arxiv.org/abs/2608.19488
  Evidence-limited preprint record: abstract-level retrieval only in this audit; direct full-text access failed. Publication status beyond the preprint not established.

## Appendix A. Review-spacing engineering check

A subsequent engineering check compared consecutive reviews with score-conditioned spaced reviews using only two development seeds per scenario.

Spacing generally produced unchanged regret. It reduced mean regret by 0.085 in the covariate-shift setting at cap 4, but increased mean regret by approximately 2.374919 in the opposing-change scenario at each review cap. These patterns occurred for both M1 and FULL.

In one opposing-change seed, spacing delayed acceptance of a helpful update from window 8 to window 9. This delayed adaptation increased loss.

This small development check is reported separately from the 100-seed studies. It does not support inferential claims or establish general controller superiority.

## Appendix B. Reproducibility and supplementary material

The accompanying supplementary tables retain all main-study summaries, all 72 ablation contrasts, all 75 calendar contrasts, shifted-stream detection summaries and held-out null summaries. The post-hoc benchmark file supplies all 225 comparisons. The sensitivity file supplies descriptive cell means separately from the earlier main-study analyses.

Archived protocols, source snapshots, seed allocations, software versions and consistency-audit records accompany the results. The audits check saved-output consistency and provenance; they do not independently reproduce every model fit or reconstruct every individual policy action. The studies are not pooled, and development and post-hoc analyses retain their separate status.

Real-data validation, a large initial-model/onset study, alternative update gates and sequential-safety guarantees remain outside the completed evaluation. The small development check does not establish these properties.

Retrospective diagnostic supplement: paper1_experiments/GATE_DIAGNOSTIC_FINDINGS_20261108.md and manuscript/support/gate_diagnostics_20261108/. Diagnostic code and findings were preserved at repository commit cbf5e20.
