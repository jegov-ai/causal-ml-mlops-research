# Evaluating Causal-Aware Monitoring in MLOps: Decision Robustness Under Distribution Shift and Operational Constraints

**Preferred working title, subject to supervisor review.** This supersedes the earlier manuscript working title, “Evaluation of Causal Machine Learning Integration into MLOps Pipelines for Explainable and Robust Decision Making,” for the present draft. It does not represent formal supervisor approval or a change to the thesis or Paper 2 title.

Author: Jegan Govinda (Jegov)  
Consolidated review draft v6 — integrated update, 13 November 2026 (Malaysia)
Original consolidated version: 3 November 2026. The working title and manuscript identity are retained.

**Draft status:** Integrated manuscript for internal and supervisor review. This update retains the two earlier 100-seed studies, restores the subsequent benchmark, model/onset and gate-development findings, and adds the completed independent-stream-seed synthetic gate validation and the prospectively specified five-day ZOZO gate case study. Earlier null and adverse results remain part of the evidence. The earlier literature assessment is retained and supplemented by the explicitly limited primary-source check in Section 2.7; this is not a new comprehensive novelty audit or a submission-readiness assessment.

**Scope of the title:** Decision robustness is measured by oracle-relative treatment-policy opportunity loss in simulation and by estimated click-policy value in a separate real-log case study. Operational constraints concern review caps, review timing and update acceptance. The MLOps scope is the monitoring-to-review-to-update component. The ZOZO experiment uses fixed daily reviews and tests the gate comparison alone; it does not validate M0/M1/FULL monitoring, identify a true shift onset, measure oracle regret or demonstrate production safety.

## Abstract

Monitoring change can alter alerts without improving subsequent decisions. We evaluate monitoring information, review timing and candidate-update acceptance in a synthetic treatment-policy benchmark, followed by a separate real-log gate case study. Two earlier exploratory studies each used 100 paired stream seeds per scenario, five scenarios and review caps of 2, 4 and 8. Additional subgroup-effect and assignment-contrast signals produced no observed incremental regret reduction in the main ablation; the calendar comparison retained occasional adverse subgroup-monitoring outcomes. Benefits against selected calendars depended on the scenario, and simple policy benchmarks qualified those benefits.

Development diagnostics motivated a fixed comparison of frozen versus candidate-refreshed outcome predictions in a held-out AIPW gate. Independent-stream-seed validation evaluated 3,900 initial-fit/scenario/onset/seed configurations using 100 new paired stream seeds, three reused initial fits, onsets 4, 7 and 10, and unchanged monitoring calibration and review procedures. The prespecified M1 refreshed-minus-frozen contrast was −0.054422 mean-per-window oracle-relative loss, with a descriptive paired seed-block 95% bootstrap interval of [−0.068318, −0.041040], approximately 3.64% below frozen M1's balanced shifted-design average. Treat-all nevertheless had lower design-average loss than either M1 gate. M0 and M1 recorded identical loss, FULL occasionally differed, and harmful accepted updates remained.

A prospectively specified five-date case study used ZOZO Open Bandit recommendation logs, separate morning training, midday gate and evening evaluation windows, and a common evaluation outcome model. Both gates rejected every daily candidate and retained the initial policy. Their paired value difference was exactly zero because the selected policies were identical. BTS estimates favored retention over always updating, whereas Random-log estimators disagreed and matching clicks were sparse.

The evidence supports separating monitoring, update acceptance and downstream policy performance. Refreshing reduced loss in the specified synthetic target but did not improve selected real-log gate policies. These conditional findings supplement the earlier null and adverse results; they do not establish causal-monitoring superiority, universal gate benefit or deployment safety.

Keywords: causal machine learning; MLOps; distribution shift; treatment-policy regret; model monitoring; update acceptance; off-policy evaluation.

## 1. Introduction

A machine-learning model used to support treatment or product decisions may encounter changes in customer characteristics, treatment assignment or treatment response. In a discount-allocation setting, these changes raise distinct questions. A change in the customer population may affect the distribution of predictions, whereas a change in treatment response may alter whether offering the discount is beneficial. Monitoring these quantities can inform model review, but detecting a change does not itself determine whether a replacement model should be deployed.

This distinction motivates the present evaluation. A monitoring signal affects decisions through a sequence of operational steps: an alert initiates a review, a candidate model is trained, an acceptance rule compares candidate and incumbent policies, and an accepted update changes subsequent decisions. Additional monitoring information may have little incremental value if an existing monitor already triggers a timely review or if the available candidate does not pass the update gate. Conversely, an early alert may consume limited review opportunities before a later change.

Our project implements a synthetic causal-ML monitoring benchmark in which a T-learner estimates heterogeneous treatment effects and recommends treatment when the estimated effect exceeds an assumed cost. The benchmark separates logged treatment assignment from policy recommendations and reserves known synthetic effects for offline evaluation. This permits calculation of oracle-relative treatment-policy opportunity loss while keeping synthetic truth outside the monitoring and adaptation rules.

Existing research already addresses treatment decisions in dynamic environments, causal estimation on streams, monitoring-triggered adaptation and resource-constrained interventions. For example, Berrevoets et al. (2022) evaluated treatment-effect optimisation under changing conditions. OnlineCML's inspected public examples demonstrate causal pseudo-outcome monitoring and estimator reset. These precedents rule out a broad claim that combining causal estimation, drift monitoring and regret evaluation is itself new. The narrower question is whether a controlled comparison can clarify the incremental value of monitoring signals and review timing under common adaptation procedures.

The two original extensions examine two research questions. First, does adding subgroup treatment-effect monitoring, a between-group assignment-rate contrast, or both reduce cumulative treatment-policy regret beyond a baseline that already includes conventional statistics and aggregate causal-effect monitoring? Second, how does alert-triggered review timing compare with prospectively specified fixed calendars when candidate estimation, update acceptance and maximum review caps are shared?

The first experiment compared four monitoring variants. M1 combined conventional statistics with an aggregate AIPW treatment-effect statistic. M2-A added subgroup treatment-effect statistics, M2-B added a between-group assignment-rate contrast, and M2-FULL added both. The second experiment retained these variants and introduced fixed-calendar reviews. Each experiment evaluated five scenarios and three review caps using 100 paired seeds per scenario.

The principal measured outcome was cumulative period-average oracle-relative net-benefit regret over the latter six windows. Alerts, reviews, accepted updates, harmful-treatment rates and detection timing provided complementary operational evidence. Alert thresholds targeted a common stable-stream any-alert probability, with independent held-out assessment. Equal intended calibration targets were distinguished from equal achieved false-alert rates, and common review caps were distinguished from equal realized workload.

The original monitoring comparisons did not show an incremental regret benefit from the additional monitoring signals. The main ablation yielded identical observed regret across variants, while the fresh calendar comparison included occasional adverse subgroup-monitoring outcomes. Alert-triggered M1 reviews reduced loss relative to the selected calendars under treatment-effect changes, but calendar reviews performed better in stable settings. A separate small review-spacing development check also demonstrated that delaying reviews could postpone a useful update. These findings are retained together rather than selecting only favorable comparisons.

The intended contribution is a reproducible, controlled empirical evaluation of how monitoring information and review opportunities translate into downstream policy performance. It is not a new treatment-effect estimator or drift detector. The two original studies do not isolate the overall benefit of causal information over a purely conventional monitor because M1 already contains aggregate causal information. The later model/onset development check and independent-seed gate validation include M0; their observed M0–M1 loss equality is reported separately. They also do not establish an explanation-stability benefit; explanation quantities remain offline diagnostics in these extensions.

The contribution and its limits require further assessment against the closest literature. In particular, the complete CausalStream and OnlineCML manuscripts were unavailable during the audit, and full overlap remains unresolved. The study is therefore presented as exploratory evidence with a provisional research-gap assessment, subject to supervisor review and final manuscript scope alignment.

The later studies ask whether changing only the outcome predictions used by the held-out acceptance gate improves downstream loss, and whether that gate comparison changes selected policies in real chronological recommendation logs. The synthetic validation targets the prespecified, equally weighted shifted design conditional on three fixed initial fits. The real-log study estimates click-policy values under fixed daily reviews and has a distinct endpoint. Neither study replaces the earlier monitoring ablation or justifies pooling unlike outcomes.

The integrated questions and their corresponding evidence are:

| Question | Endpoint and evidence | Observed answer |
| --- | --- | --- |
| RQ1: Do subgroup-effect and assignment-contrast additions improve decisions beyond M1 under common adaptation procedures? | Cumulative oracle-relative loss in the original ablation and separate calendar seed set | No main-ablation improvement; occasional adverse additional-signal outcomes |
| RQ2: How do alert-triggered reviews compare with the selected fixed calendars at common review caps? | Paired cumulative oracle-relative loss and actual review use | Scenario- and calendar-dependent differences; not universal calendar inferiority |
| RQ3: Does refreshing only the gate outcome predictions reduce M1 loss in the fixed shifted synthetic design? | Prespecified independent-stream-seed balanced mean-window contrast, Section 3.12 | Mean difference −0.054422; treat-all remained better on the design average |
| RQ4: Does that gate comparison change selected policies and estimated values in the five-date real-log case study? | Daily decisions and paired evening click-value estimates, Section 3.13 | Both gates retained the initial policy; exact observed path-value difference of zero |

RQ1 and RQ2 retain the original study questions. RQ3 is the later prospectively specified synthetic validation target, and RQ4 is the exploratory external gate question. This mapping does not retroactively designate the development or secondary analyses as confirmatory. The contribution combines an incremental-monitoring evaluation, a controlled gate-input comparison with new-seed validation, and a bounded real-log check. Positive evidence for RQ3 is not presented as positive evidence for RQ1 or RQ4.

| Evidence stage | Independent or temporal allocation | Main purpose and boundary |
| --- | --- | --- |
| Original signal ablation and calendar comparison | 100 paired seeds per scenario in each separate study | Monitoring and review timing; one initial model and onset 7 |
| Model/onset and gate development, including diagnostic replay | Three reused stream seeds and three initial fits; 117 dependent configurations | Exposed development evidence; no new independent validation |
| Frozen-versus-refreshed synthetic validation | 100 new stream seeds; 3,900 dependent factor configurations | Prespecified M1 gate contrast; conditional on three reused initial fits and calibration |
| ZOZO development pilot | Two previously inspected dates; one review | Engineering/development check; both gates retained the initial policy |
| ZOZO five-date gate case study | Five consecutive reserved dates, one review per gate per date | Exploratory real-log gate comparison; no monitoring-arm or known-shift validation |

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

The original studies examine these relationships through two completed exploratory comparisons:

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

The original narrow candidate contribution is an empirical attribution of the incremental policy value of subgroup monitoring under a specified common adaptation procedure. The integrated manuscript additionally evaluates a controlled gate-input change and its observed external boundary; these are extensions of the evaluation, not inventions of the underlying estimation methods. The main ablation found no observed incremental benefit, and the fresh schedule study documented occasional adverse outcomes. The contribution is not merely that timing matters, and the results do not establish that subgroup monitoring is generally unhelpful. A defensible novelty argument still requires checking whether the closest literature already provides substantially the same comparison and insight.

Evidence scope: these related-work paragraphs retain the targeted inspection recorded in the earlier draft. They are not an exhaustive full-text review of the entire corpus. The new experiments reported below do not establish an unoccupied literature gap.

### 2.6 Average and subgroup causal monitoring under performativity

Feng et al. (2024) compare six monitoring procedures combining three monitoring criteria with observational or interventional data. Section 4.1 distinguishes average and subgroup-specific causal positive/negative predictive values, as well as a stronger conditional calibration criterion; Section 4.3 develops monitoring procedures. This directly establishes that contrasting average and subgroup causal monitoring is not, on its own, our contribution. Their monitored quantities are causal classification-performance criteria, whereas ours are aggregate and subgroup treatment-effect pseudo-outcome means combined with conventional statistics. Our completed extensions measure the incremental downstream opportunity loss after common model reviews and held-out update acceptance. This difference supports a bounded empirical extension; it does not establish priority over all literature. Our exogenous-logging simulation also does not solve the performativity problem motivating their study.

A further close preprint is Dasari (2026), When to Retrain: An Empirical Study of Retraining Policies for Streaming ML Under Concept Drift, Budget, and Latency Constraints (arXiv:2608.19488). Only abstract-level evidence was available through the retrieved arXiv search record; direct manuscript and repository access failed in this session. The record identifies an empirical comparison of retraining policies under budgets and latency. This reinforces that a generic calendar-versus-triggered comparison is not a defensible novelty claim. Its full experimental overlap remains unresolved; no full-text exclusion is asserted.

### 2.7 Off-policy evaluation, nonstationarity and policy-improvement overlap

The gate extension also requires comparison with off-policy evaluation literature, beyond causal-monitoring references. A targeted primary proceedings-page and abstract check on 13 November 2026 identified three relevant established strands. These records were checked at that limited level for this revision; they are not newly completed full-text reviews or additions to a claimed systematic-review count.

Dudík et al. (2012) combine importance weighting, doubly robust evaluation and nonstationary policy evaluation for contextual bandits. Thus combining these ingredients, or applying off-policy evaluation to a changing policy, is not an originality claim here. Their use of nonstationary policy evaluation should not automatically be equated with every form of reward-environment drift.

Liu et al. (2023) study contextual-bandit and finite-horizon policy evaluation in nonstationary environments and propose regression-assisted doubly robust estimation when reusing old data. This directly overlaps the broader issue of using historical information for policy evaluation under change. Our implemented comparison retains the existing AIPW/DR form and switches initial versus current-candidate outcome predictions; it neither introduces their estimator nor claims to supersede its estimation or confidence-interval results. No implemented comparison against that estimator has been performed.

Jiang and Li (2016) extend doubly robust off-policy evaluation to reinforcement learning and illustrate its use in safe policy improvement. Consequently, using doubly robust value estimates to inform whether a policy should replace a baseline is established. Our repeated mean-minus-1.96-row-SE rule is a pointwise empirical heuristic, not a new safe-policy-improvement guarantee, and the binary-treatment and contextual-bandit studies here do not implement a general sequential-decision method.

These primary abstracts establish overlap in the ingredients; they do not establish whether those papers evaluated the same frozen-versus-candidate-refreshed gate switch under matched monitoring/review schedules and downstream treatment-policy opportunity loss. That exact comparison remains a full-text verification task rather than a demonstrated literature absence. The strongest supported manuscript statement is the observed empirical attribution under the specified common pipeline, including adverse and null outcomes. Neither a positive synthetic result nor real-data use independently establishes publication-level novelty.

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

Additional outcomes included prechange regret, harmful-treatment rate, alerts, reviews, accepted updates, detection probability and detection delay conditional on detection. Detection was not applicable to stable streams or the PERIODIC arm.

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

### 3.11 Exploratory comparison of frozen and refreshed gate outcome models

Motivated by the retrospective diagnostics, a subsequent development comparison changed only the outcome predictions used inside the AIPW gate. The frozen variant used the initial outcome models; the refreshed variant used the current candidate models, fitted on the current window's 70% training partition. Gate outcomes remained in the separate 30% partition. Both the candidate and incumbent policies were evaluated using the same pseudo-outcomes within each gate variant. The acceptance rule retained the 1.96 standard-error multiplier and positive lower-bound requirement. Monitoring references and review schedules were unchanged, and each variant maintained a separate incumbent trajectory. Accepted replacements affected the next window only.

This comparison reused all 117 previously exposed development configurations described in Section 3.9. It was not a fresh independent validation. The protocol and code were recorded before running this comparison, after inspection of earlier diagnostic findings. The original gate had to reproduce every original period field, and the refreshed variant had to preserve the same scores, thresholds, alerts and review flags. Both checks passed. Runtime was 44.13 minutes.

The outcomes were paired refreshed-minus-frozen cumulative and mean-per-window post-onset regret, together with accepted-update counts and offline gate/next-window candidate-benefit diagnostics. Negative regret differences favor refreshed. All settings were retained. Signs used an absolute tolerance of 10⁻¹⁰; no inferential tests or equivalence claims were made. Outcome-model refresh is an application of existing doubly robust evaluation methodology (Dudík et al., 2011), not a proposed new estimator. Its possible effect on evaluation variance does not guarantee lower policy regret or sequential safety.

### 3.12 Independent-stream-seed frozen-versus-refreshed validation

A prospective protocol was specified after the exposed development comparison. The engineering pilot used seed 490000 and was excluded from the primary analysis. The completed validation used stream seeds 500000–500099. Three initial training/fitting realizations (42, 1042 and 2042) and their archived calibration were intentionally reused. Stable scoring used marker 7; the four shifted scenarios each used onsets 4, 7 and 10. These factors yield 39 fit/scenario/onset combinations per stream seed and 3,900 configurations overall, not 3,900 independent replications. M0, M1, M2-FULL and PERIODIC, review caps 2, 4 and 8, both gates and the fixed-policy benchmarks were retained.

M0 uses the nine conventional statistics in Section 3.2.1. M1 adds the aggregate AIPW mean; M2-FULL adds the two subgroup means and group assignment-rate contrast. Candidate fitting, the current-window 70/30 training/gate split, monitoring references, threshold calibration, review schedules, cost and next-window application remained unchanged. The sole gate switch was initial versus current-candidate outcome predictions in the common AIPW pseudo-outcome. Both variants maintained separate incumbent paths. Exact monitoring scores, thresholds, issued alerts and review indicators were required to match across gates. Known synthetic effects remained restricted to offline scoring and diagnostics.

For each shifted configuration, the endpoint was mean period-average oracle-relative loss from its onset through window 12. The primary contrast was M1 refreshed-minus-frozen loss averaged equally over the 108 initial-fit/scenario/onset/cap cells within each stream seed, then averaged across the 100 seeds. This is a deliberately balanced design average, not an estimated deployment mixture. It differs from the cumulative windows-7–12 endpoint of the earlier main studies. Mean-per-window normalization accommodates different scoring horizons but does not equalize remaining adaptation opportunities.

The paired seed-block percentile bootstrap resampled the 100 seed-level averages 5,000 times using RNG seed 20261108; repeated periods, fits, onsets, arms and caps were kept within seed blocks. The Monte Carlo standard error was the sample standard deviation of those seed averages divided by the square root of 100. Stable records were retained as separate harm diagnostics, outside the shifted primary average. Secondary fixed-policy and cell comparisons remain descriptive. Helpful/harmful/tied accepted-update diagnostics used next-window fixed-model oracle benefit and tolerance 10⁻¹⁰; final-window benefit was missing, not zero. Repeated diagnostic events are dependent and cannot be interpreted as independent failure probabilities or summed as achievable savings.

The completed run was `run_20261110_131649_504254`, source commit `aa7db7a3ef14cd51a893bd6818418cc50dcb63b8`. It saved 1,123,200 period records, 93,600 method-budget-gate outcome records and 46,800 paired method-budget records. The earlier saved-output audit reported 29 passed checks without independently refitting every model. For this manuscript integration, the archived seed-level primary mean and bootstrap endpoints were recalculated from saved outputs; no models were retrained. The archive, source snapshots and checkpoint establish the recorded execution, not clean-checkout reproducibility of every fitting step.

### 3.13 Prospectively specified exploratory ZOZO gate case study

#### Data, prior exposure and chronological allocation

We used the men campaign, display position 1, from the ZOZO Open Bandit Dataset, which supplies real recommendation logs from ZOZOTOWN under multiple logging policies (Saito et al., 2021). Files came from provider revision `90a1283aecd19026caf15a0840af1176a41f6a76` of `zozonext/open-bandit`. The dataset is attributed to ZOZO NEXT/ZOZO under its stated CC BY 4.0 data licence. The Random and BTS sources were analysed separately. Products comprised 34 item IDs with four categorical item features. BTS recorded selection probabilities were used as supplied; they were not independently reconstructed.

Only the outcomes of 24–25 November 2019 UTC were inspected during development. Later date/position counts and propensity ranges had been inspected, but later click outcomes had not been analysed in the recorded workflow. Development included a one-review pilot in which both gates rejected the candidate; those pilot results informed the study context and are not fresh validation evidence. The five-date protocol was committed at `8bebea1` and runner at `b216bd8` before reserved-outcome analysis. The later study therefore is a prospectively specified exploratory external gate case study after development, not an untouched end-to-end confirmatory validation.

The initial outcome model used all 406,692 BTS position-1 records from 24–25 November, including 3,077 clicks. On each of 26–30 November, the same-date BTS morning window [00:00, 12:00) trained one candidate, [12:00, 18:00) checked it, and [18:00, 24:00) evaluated selected policies. All times are UTC and endpoints are start-inclusive/end-exclusive. Candidates used only that morning's observations, not cumulative training. Both gates started from the same initial model and received the same candidate, but maintained separate incumbent paths. Each had one review opportunity per date, at most five overall. Selection at the gate affected the subsequent evaluation window and was carried to the next date. Performance outside the evening evaluation windows was not an endpoint.

#### Models, gate rule and value estimators

The pilot's pooled logistic regression and preprocessing were reused unchanged: `liblinear`, C = 0.1, tolerance 10⁻⁶, 500 maximum iterations and random seed 42, with no class balancing or training sample weights. Features comprised categorical item ID, four categorical user features, four categorical item features and the numeric user–item affinity for the requested product. A sparse dictionary vectorizer and maximum-absolute scaling were fitted only on each training partition. All 34 products were retained. A policy selected the product with largest predicted click probability, breaking ties by lowest item ID. Timestamps, outcomes and logged probabilities were excluded from prediction features.

For observation i, logged action A_i, click Y_i, recorded selection probability p_i, outcome predictions q̂_i(a), and target policy probabilities π_i(a), the implemented scores were

$$
\widehat V_i^{\mathrm{IPS}}(\pi)=\frac{\pi_i(A_i)}{p_i}Y_i,
\qquad
\widehat V_i^{\mathrm{DR}}(\pi)=\sum_{a=0}^{33}\pi_i(a)\hat q_i(a)
+\frac{\pi_i(A_i)}{p_i}\{Y_i-\hat q_i(A_i)\}.
$$

The gate evaluated paired candidate-minus-current-incumbent DR scores. The frozen gate always used the initial two-day outcome model for q̂; the refreshed gate used that morning's candidate outcome model. Each gate accepted only if the mean paired gain minus 1.96 row standard errors was strictly positive. Unlike the pilot, an explicitly specified fail-closed safeguard rejected either comparison if its candidate or its own incumbent had zero matching logged actions. This check was applied independently and identically to each gate. No weights were clipped and no products were dropped after seeing outcomes. Row standard errors and this pointwise rule do not provide a repeated-review safety guarantee.

Evening evaluation used one common q̂ model—the current morning's candidate—across all five policies: frozen-gate path, refreshed-gate path, initial/no-update, always-update/current-candidate and uniform over the 34 products. The evaluation q̂ model was fixed before the gate and evening windows. IPS and DR were computed on the same rows within each logging source, without pooling BTS and Random. Uniform recommendation is a random product choice, not offering every product or giving every customer a discount.

#### Endpoints, uncertainty and output audit

The primary endpoint was the equal-weight mean across five dates of the within-date BTS evening DR value difference, refreshed path minus frozen path; positive favors refreshing. Corresponding BTS IPS and Random DR/IPS comparisons, and each gate versus the three baselines, were secondary. These click-value endpoints have different units and sign conventions from synthetic oracle loss and were not pooled with it.

All daily contrasts were retained. The exploratory bootstrap used 1,000 resamples with seed 42, resampling nonempty contiguous 30-minute blocks within each date with common paired draws, recomputing each resampled date's row mean and then averaging the five dates equally. The interval conditions on the fitted/selected paths and observed dates. It does not incorporate full retraining or policy-selection uncertainty, repeated-user clustering or all temporal dependence. Matching rows/clicks, weight effective sample size (ESS) and largest normalized weight share were reported. ESS measures weight concentration, not independent sample size or a power calculation. Sparse clicks and estimator disagreements were treated as limitations on interpretation; no secondary multiplicity-unadjusted superiority claim was made.

Run `20261112T235857Z_173ba8d4` completed under Python 3.12.10, pandas 3.1.0, NumPy 2.5.4 and scikit-learn 1.9.1. Input hashes matched the protocol. Summaries were committed at `9f94b55`; the saved-score audit and disclosure were committed at `10134a1`. The audit recomputed saved gate/evaluation scores, weight diagnostics, daily contrasts, equal-date means and block intervals and checked source snapshots. It did not refit models or independently reload all raw input rows.

A timestamp serialization defect was identified during audit: integer arrays named `timestamp_ns` actually stored microseconds in this environment. The corrected audit explicitly decoded them with `--timestamp-unit us` and passed, recording the field-name mismatch. The experiment was not rerun and its original outputs were retained. Gate/evaluation window selection and bootstrap block construction in the runner used parsed datetimes, rather than decoding these saved integer arrays; the defect concerns the serialized audit field, not a change to the preplanned windows or calculated policy scores.

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

### 4.7 Refreshed gate: benefits and adverse outcomes in development

The comparison reconciled 33,696 period records, 10,620 review-diagnostic records and all 1,404 paired outcome records. The frozen variant reproduced the original 16,848 period records. Monitoring and review opportunities agreed across gate variants, while accepted updates and incumbent trajectories could differ. These are consistency and provenance checks, not independent reconstruction of every individual diagnostic action.

| Monitor | Lower refreshed loss | Tied loss | Higher refreshed loss | Paired records |
| --- | ---: | ---: | ---: | ---: |
| M0 | 29 | 307 | 15 | 351 |
| M1 | 29 | 307 | 15 | 351 |
| M2-FULL | 29 | 307 | 15 | 351 |
| PERIODIC | 8 | 324 | 19 | 351 |

Each record pairs one initial fit, scenario, onset, stream seed, monitor and cap across gates. The same three stream seeds are reused across factors. These counts therefore are not independent replications, population win probabilities or evidence that the gate with more favorable records is preferable overall. Across 117 three-seed cell means per monitor, M0, M1 and FULL each had 22 lower-loss, 83 tied and 12 higher-loss means. PERIODIC had seven lower, 92 tied and 18 higher.

For M1, response-shift cell-mean differences were nonpositive across the initial-fit/onset/cap settings. Averaging mean-per-window differences across fits and caps within onsets 4, 7 and 10 gave −0.166091, −0.033889 and −0.101667, respectively. Opposing-shift results changed direction: +0.059048, −0.276538 and +0.160370 at those onsets. These are descriptive averages of dependent cells with different remaining horizons. An adverse opposing-shift case at initial fit 1042, seed 420302 and onset 10 increased cumulative post-onset regret by 4.33 at each cap. The repeated cap records concern one underlying stream.

For each of M0, M1 and FULL, the frozen gate accepted 92 review records, all helpful on the next window in this sample. The refreshed gate accepted 118: 109 helpful and nine harmful on the next window. This is an aggregate comparison rather than a one-to-one attribution of extra acceptances, because incumbent policies diverged across gates. PERIODIC changed from 84 helpful, two harmful and five final-window accepted records to 73 helpful, zero harmful and seven final-window accepted records. Final-window reviews have no next-window diagnostic and must not be counted as harmless.

M0, M1 and FULL retained identical period-level regret within each gate variant. The modification therefore did not reveal incremental causal-monitoring benefit. The results describe a trade-off: refreshing gate outcome models sometimes reduced loss but also introduced adverse accepted updates and worse trajectories. They do not establish an overall improved gate, and no replacement of the original baseline is justified by this development sample alone.

### 4.8 Independent-stream-seed synthetic gate validation

The validation completed all 3,900 planned configurations. The primary M1 refreshed-minus-frozen mean-per-window loss difference was −0.054422, with descriptive paired seed-block 95% bootstrap interval [−0.068318, −0.041040] and Monte Carlo standard error 0.007005. Frozen and refreshed M1 balanced shifted-design means were 1.495995 and 1.441573, respectively, a reduction of approximately 3.64% relative to the frozen mean. This supports lower design-average loss under the specified synthetic target, conditional on the three fixed initial fits and reused calibration.

| Balanced shifted-design policy | Mean-per-window oracle-relative loss |
| --- | ---: |
| M1, frozen gate | 1.495995 |
| M1, refreshed gate | 1.441573 |
| Fixed initial T-learner | 2.443229 |
| Treat-all | 0.886932 |
| Treat-none | 13.490644 |

Treat-all remained below both M1 variants on this design average. Improving the gate relative to its frozen version therefore does not establish that the adaptive pipeline was the best evaluated decision strategy. The average also does not imply improvement in every scenario, onset, fit, cap or seed.

M0 and M1 recorded identical mean-window loss within each gate variant throughout this validation; M2-FULL occasionally differed. The primary benefit cannot therefore be attributed to adding the aggregate causal monitoring statistic. The compared gate variants retained identical monitoring scores, thresholds, issued alerts and review indicators, isolating the implemented gate-input switch within this pipeline while allowing different incumbent paths.

Adverse results remained. Across all methods, caps, initial fits, scenarios and onset settings, the frozen gate recorded 14,867 accepted-review records and the refreshed gate 15,954. Among records with an available next window, the helpful/harmful counts were 12,642/1,163 for frozen and 13,692/1,293 for refreshed; 1,062 and 969 accepted final-window records, respectively, had no next-window diagnostic. These are dependent repeated records with diverging incumbents, not independent safety probabilities or a one-to-one attribution of extra acceptances. Both gates accepted candidates that worsened next-window oracle loss despite the favorable average contrast for refreshing.

### 4.9 Five-date ZOZO gate case study

Both gates rejected all five daily candidates and retained the initial policy. Their gain estimates differed, but no comparison satisfied the positive-lower-bound acceptance rule. The primary refreshed-minus-frozen BTS DR contrast was exactly 0, with exploratory interval [0, 0]. Each of the five daily primary contrasts was also exactly 0; BTS IPS and both Random estimators likewise cancelled. This arithmetic cancellation follows identical selected policies on the observed rows, not proof that distinct gates are equivalent in other settings.

The evening BTS windows contained 100,426 records and 648 logged clicks; Random contained 11,050 records and 38 logged clicks. These are records from five dates, not that many independent temporal replications. For the retained initial policy, the logged recommendation matched 34 clicks in BTS and only two in Random across all five evaluation windows.

| Logging source | Paired comparison: retained gate policy minus comparator | Estimator | Equal-date mean | Exploratory block interval |
| --- | --- | --- | ---: | --- |
| BTS | Always-update/current-candidate | DR | +0.007127 | [0.002004, 0.012209] |
| BTS | Always-update/current-candidate | IPS | +0.004026 | [0.000827, 0.007981] |
| BTS | Uniform product policy | DR | +0.001091 | [−0.002934, 0.005176] |
| BTS | Uniform product policy | IPS | +0.000935 | [−0.002781, 0.005019] |
| Random | Always-update/current-candidate | DR | +0.003625 | [−0.008052, 0.011855] |
| Random | Always-update/current-candidate | IPS | −0.003221 | [−0.011765, 0.000000] |
| Random | Uniform product policy | DR | +0.003321 | [−0.003640, 0.011989] |
| Random | Uniform product policy | IPS | +0.002174 | [−0.004153, 0.010377] |

The frozen and refreshed gate rows are identical, so the table reports their shared retained policy once. Each gate also equalled the no-update baseline exactly. Positive differences favor retention. Values are estimated click-probability differences, not relative percentages, realized click gains or measured profit; DR estimates are not constrained to [0,1] in finite samples. The intervals are exploratory secondary comparisons rather than simultaneous or sequential superiority guarantees.

BTS point estimates favored retaining the initial policy over always updating. Random estimates disagreed in sign between DR and IPS for that comparison, with sparse policy-matching clicks. Results against uniform recommendation were uncertain. This case study supplies no observed advantage from refreshing gate outcome predictions, and does not corroborate a general real-world benefit from either gate over all baselines. It remains informative about conservative update selection and the limits of evaluating many-product policies with rare click outcomes.

## 5. Discussion and limitations

The completed experiments distinguish monitoring differences from decision improvements. Additional signals sometimes changed alerts or reviews without improving accepted updates or treatment-policy regret.

Review timing affected outcomes, but its usefulness depended on change timing, available review opportunities and the common acceptance gate. Early alerts could exhaust scarce resources, while spacing could delay helpful adaptation.

The original main studies were conditional on one initial fitted model and change onset 7. Later development and validation varied three initial training/fitting realizations and onsets 4, 7 and 10, extending that scope without sampling a population of initial models. The generator, immediate labels, exogenous logging, finite horizon and selected calendars remain restrictions. The validation reused small development calibration allocations; it is not fresh evidence that monitoring false-alert probabilities are precisely calibrated. Its 100 seeds support uncertainty assessment for the fixed design, not unrestricted generalization.

M1 combined conventional and aggregate causal statistics. The two original studies did not include a purely conventional M0 arm. The later conventional-only comparisons found identical recorded M0–M1 loss in development and in the independent-seed gate validation. Consequently, the observed synthetic gate benefit is not evidence that adding aggregate causal monitoring improved the decisions.

Explanation statistics remained offline diagnostics. These experiments do not establish an explanation-stability benefit.

The interval estimates were exploratory and pointwise, without multiplicity adjustment or a prespecified equivalence margin. Null differences should not be interpreted as proof of equivalence.

The development-to-validation sequence separates an exposed engineering finding from its fixed new-stream-seed evaluation. Refreshing improved M1's balanced synthetic loss on average, while harmful acceptances and a stronger simple-policy benchmark remained. This supports a bounded gate-design finding rather than a general recommendation to accept more updates. Greater candidate acceptance is not itself an objective.

The real-data study addresses a different question with estimated click values and five fixed review opportunities. Identical rejection paths give an exact null difference for these observed policies and dates; they do not measure gate sensitivity under a broad range of candidate qualities. This result neither overturns the synthetic design-average benefit nor confirms its transport to recommendation settings. A larger row count cannot replace more temporal regimes or independent deployments.

Real-log off-policy estimates require valid recorded probabilities and sufficient action support, usable context/outcome measurements and an appropriate per-position reward interpretation despite other products appearing in the slate. BTS probabilities were supplied estimates. Repeated-user identities were unavailable; the exploratory time-block analysis cannot fully account for that clustering. Training-only preprocessing and chronological splits reduce direct outcome reuse but do not establish causal identification under every unmeasured interaction. Random logging supplies a separate check, yet rare matching clicks make its estimates imprecise. The BTS and Random populations/logging sources were not pooled or assumed interchangeable. No individual counterfactual truth, known shift onset, production feedback experiment or real monetary benefit is available in this case study.

### 5.1 Literature coverage and contribution uncertainty

The existing corpus contains 100 records; it must not be described as 100 completed full-text reviews. Nine particularly relevant papers were previously selected, of which seven received selective full-text inspection. The complete CausalStream and OnlineCML manuscripts remained unavailable.

Our completed targeted assessment supports an incremental empirical-extension framing, not an established first-of-its-kind result. The jointly inspected studies establish the broader ingredients, including subgroup causal monitoring and resource-aware update timing. The inspected evidence does not demonstrate the identical joint treatment-policy ablation, but unavailable manuscripts and limited retraining-study access prevent a conclusive absence claim. Details and a source-by-source decision matrix are provided in support/PAPER1_NOVELTY_ASSESSMENT_20261103.md.

No claim of being the first, uniquely novel or universally superior is supported. Supervisor assessment and a source-verified comparison with the closest studies remain necessary to judge whether the contribution is sufficient for the intended manuscript and venue.

## 6. Conclusion

The original monitoring ablation found no incremental regret reduction from subgroup and assignment-contrast additions, and the calendar comparison retained adverse subgroup-monitoring cases and scenario-dependent timing effects. Development diagnostics and a subsequent fixed, independent-stream-seed validation identified a narrower gate-design result: candidate-refreshed AIPW outcome predictions reduced M1 balanced shifted-design mean-window loss by approximately 3.64% relative to the frozen gate. The improvement was conditional on the specified generator, three fixed initial fits and reused calibration. Treat-all remained better on the same average, M0 and M1 recorded identical loss, and harmful accepted updates persisted.

In the separate five-date ZOZO gate case study, both gates rejected every candidate and retained the same initial model. Their observed policy-value difference was exactly zero. BTS estimates favored retention over always updating, while Random estimators disagreed and matching clicks were sparse. This provides a real-data boundary on the gate findings rather than evidence of real-world refreshed-gate superiority.

Together, the studies support evaluating monitoring information, review timing, acceptance decisions and simple-policy benchmarks as distinct parts of an adaptation pipeline. The contribution is a conditional, reproducible empirical evaluation using established methods. Prior-art overlap, supervisor review and journal-specific preparation remain separate from completion of the experiments.

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

- Saito, Y., Aihara, S., Matsutani, M., and Narita, Y. (2021). Open Bandit Dataset and Pipeline: Towards Realistic and Reproducible Off-Policy Evaluation. NeurIPS Datasets and Benchmarks. https://arxiv.org/abs/2008.07146
  Dataset provider: https://huggingface.co/datasets/zozonext/open-bandit ; pinned revision 90a1283aecd19026caf15a0840af1176a41f6a76. Attribution and input hashes are retained in the case-study protocol.

- Dudík, M., Erhan, D., Langford, J., and Li, L. (2012). Sample-efficient Nonstationary Policy Evaluation for Contextual Bandits. Proceedings of the 28th Conference on Uncertainty in Artificial Intelligence, 245–252. https://proceedings.mlr.press/r10/dudik12a.html
  Integration check: primary proceedings page and abstract; not a new full-text review.

- Liu, V., Chandak, Y., Thomas, P., and White, M. (2023). Asymptotically Unbiased Off-Policy Policy Evaluation when Reusing Old Data in Nonstationary Environments. Proceedings of the 26th International Conference on Artificial Intelligence and Statistics, PMLR 206, 5474–5492. https://proceedings.mlr.press/v206/liu23d.html
  Integration check: primary proceedings page and abstract; exact gate-comparison overlap unresolved.

- Jiang, N., and Li, L. (2016). Doubly Robust Off-policy Value Evaluation for Reinforcement Learning. Proceedings of the 33rd International Conference on Machine Learning, PMLR 48, 652–661. https://proceedings.mlr.press/v48/jiang16.html
  Integration check: primary proceedings page and abstract; not an implemented experimental comparator.

## Appendix A. Review-spacing engineering check

A subsequent engineering check compared consecutive reviews with score-conditioned spaced reviews using only two development seeds per scenario.

Spacing generally produced unchanged regret. It reduced mean regret by 0.085 in the covariate-shift setting at cap 4, but increased mean regret by approximately 2.374919 in the opposing-change scenario at each review cap. These patterns occurred for both M1 and FULL.

In one opposing-change seed, spacing delayed acceptance of a helpful update from window 8 to window 9. This delayed adaptation increased loss.

This small development check is reported separately from the 100-seed studies. It does not support inferential claims or establish general controller superiority.

## Appendix B. Supporting documents and review status

The accompanying support/PAPER1_SUPPORTING_TABLES_v1.md contains all main-study summaries, all 72 ablation contrasts, all 75 calendar contrasts, shifted-stream detection summaries and held-out null summaries. It preserves beneficial, null and adverse results. The main table is not a selectively designated confirmatory test.

support/PAPER1_REPRODUCIBILITY_v1.md records software, source hashes, seed ranges, model allocation and operational assumptions. support/PAPER1_NOVELTY_ASSESSMENT_20261103.md records the completed targeted literature assessment, its search scope and unresolved access limits. support/PROJECT1_PAPER1_COMPLETION_RECORD_20261103.md distinguishes completed work from unperformed robustness extensions.

This integrated revision includes the later model/onset development, diagnostic replay, refreshed-gate development comparison, independent-stream-seed gate validation and exploratory real-log gate case study. It supersedes the original v6 statement that no such extensions had been performed. It does not relabel exposed development evidence as independent validation or broaden the real-data experiment to monitoring validation.

The restored development sections refer to the preserved 8 November manuscript and its support records. Synthetic validation evidence comes from `Project1_Gate_Validation_Complete_504254.zip`, containing `run_20261110_131649_504254`, its prospective protocol, source snapshots, checkpoint, seed-level contrasts and full outcome tables. This archive was retrieved and inspected for the integration. The earlier reported 29-check audit is distinguished from the present arithmetic recalculation and from independent model refitting, which was not performed.

ZOZO protocol and source are in `paper1_experiments/zozo_realdata_v1/`; the protocol, runner, results and audit commits are respectively `8bebea1`, `b216bd8`, `9f94b55` and `10134a1` on branch `paper1-realdata-validation`. Small result tables and audit disclosure are in `five_day_results_20261112_235857/`. Raw datasets and detailed score arrays remain outside Git under `data/zozo_open_bandit/`; their exclusion means the repository alone is not a self-contained copy of every raw artifact. The original source/run and microsecond timestamp disclosure must be retained. The complete synthetic validation run archive is now preserved at `paper1_experiments/Project1_Gate_Validation_Complete_504254.zip`, committed and pushed at `c3d60b8`. Preservation of other untracked local historical results is a separate issue; their presence in local folders alone does not establish repository preservation.

The inherited related-work and novelty-access limitations have not been resolved by adding experiments. Final bibliography verification, supervisor/authorship and affiliation review, venue requirements and any applicable AI-use disclosure remain before submission. No publication acceptance or first-of-its-kind claim follows from the audit results.
