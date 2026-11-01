# Project 1 - Evaluation plan v3: aligned implementation record

Date: 1 November 2026 (Malaysia)
Status: EXPLORATORY, documented after inspecting results. Not a preregistration, novelty certification or final supervisor-approved protocol.
Scope: integrated_causal_monitoring_v2_xai.py, repaired code committed as 06e0c79 on project1-inspection-repairs. Keep EVALUATION_PLAN_v2.md as the historical plan for the earlier experiment.

## 1. Literature basis and working question

Paper 1: Evaluation of Causal Machine Learning Integration into MLOps Pipelines for Explainable and Robust Decision Making.

Source documents already supplied by the researcher:
- causal_ml_100_paper_critical_reassessment.md, prepared 30 October 2026.
- causal_ml_100_paper_comparison_matrix.csv.
- Deep Research Report: Causal Machine Learning in MLOps for Explainable and Robust Decision-Making, 19-page PDF.

These documents support a candidate evaluation gap: whether causal-effect-aware monitoring, with explanation diagnostics, improves post-alert treatment decisions beyond conventional monitoring under controlled distribution changes and a common response rule. The reassessment explicitly describes 100 linked records rather than 100 fully verified full-text reviews. Full-text competitor checks and supervisor review remain necessary. This plan records their recommendations without independently certifying their bibliographic claims.

Working question: Under controlled covariate, treatment-assignment and treatment-response shifts, does adding causal-effect monitoring, with or without explanation diagnostics, reduce downstream treatment-policy regret compared with conventional monitoring when the estimator, observed data and alert-response procedure are otherwise shared?

Do not claim that integration, online causal estimation, drift detection or explanation monitoring is itself new. Treat benefit as a hypothesis; null and adverse findings are valid.

## 2. Data, sample size and treatment

Synthetic randomized logged data; two observed features: age and previous_spending. No real customer data and no deployment feedback.

The initial model is trained once on 800 of 1,000 generated customers, with 200 held out. Two random forests form a T-learner, one outcome model per treatment arm (100 trees each, minimum leaf size 5, seed 42).

Treatment is discount assignment coded 1, compared with no discount coded 0. A discount percentage or monetary discount amount is NOT specified. COST=10 is an assumed per-treated-customer campaign cost subtracted from incremental spending; it is not the retraining cost or actual measured business profit.

| Setting | Smoke | Pilot | Study |
|---|---:|---:|---:|
| Customers per monitoring window | 200 | 600 | 1,000 |
| Windows per stream | 12 | 12 | 12 |
| Scale-estimation streams | 3 | 20 | 100 |
| Null calibration streams | 5 | 100 | 1,000 |
| Held-out null streams | 3 | 50 | 200 |
| Evaluation seeds per scenario | 1 | 5 | 50 |

Each window contains NEW synthetic customers. Each seed/scenario is shared across methods and budgets; 4 methods x 3 budgets are repeated evaluations, not 12 independent datasets. Paired statistical units are simulation seeds. One fixed initial model means results are conditional on that initialization.

## 3. Fixed scenarios in current code

Young means age <35; older means age >=35. Baseline young population proportion q=17/48; baseline logging probability 0.5 in each group. Age ranges are 18-34 and 35-65; spending is clipped Normal(200,60). Baseline outcome is 50 + 0.4*spending + Normal(0,20); assigned treatment adds the true effect.

Shift onset is window 7. All scenarios have baseline conditional effects (young, older)=(40,15) in windows 1-6.

| Scenario | Windows 7-12 |
|---|---|
| stable | No mechanism change. |
| covariate | Young population share becomes 0.65; conditional effects stay (40,15). |
| assignment | Logging probabilities become (0.2,0.8); conditional effects stay (40,15). |
| response | Conditional effects become (5,15). |
| opposing | Conditional effects become (5, 15+35*q/(1-q)), approximately (5,34.194). |

The opposing population ATE remains unchanged IN EXPECTATION; finite-sample group composition varies. Stable ATE does not imply stable outcome variance or invisibility to conventional monitoring.

The 40-to-5 change is deliberate. With cost 10, young net treatment value changes from +30 to -5. Do not confuse effect, treatment cost and prediction error.

## 4. Actual monitor definitions

All monitors compare absolute standardized statistics with frozen null centers/scales. Scores take the maximum over included statistics.

| Method | Included statistics |
|---|---|
| M0 | Age mean/SD, spending mean/SD, treatment rate, outcome mean/variance, baseline residual mean/second moment. |
| M1 | M0 plus AIPW average treatment effect. |
| M2 | M1 plus young and older AIPW effects AND young-minus-older treatment-assignment-rate contrast. |
| M3 | M2 plus mean absolute and mean signed Shapley attributions for both features, evaluated using the frozen baseline model on incoming features. |

M2 is not an isolated subgroup-effect ablation: assignment contrast also changes. Attribution of a benefit solely to subgroup-effect monitoring requires a separately specified experiment.

M3 uses exact two-feature coalition enumeration against 16 fixed background rows, balanced eight per age group. This explains the fitted CATE function, not the causal effects of age or spending. The separate offline explanation audit uses 64 fixed anchors and oracle effects. Pure response shifts need not change a frozen-model explanation distribution when features are unchanged.

## 5. Calibration, resources and timing

Separate scale-estimation, null calibration, held-out null and evaluation seed ranges. Calibrate each method's threshold at the 95th percentile (higher quantile) of stable-stream maximum scores over all 12 windows. The intended operating point is about 5% any-alert probability per stable stream; finite calibration does not guarantee exact 5%. Report held-out rates with Wilson intervals.

Each method has a cap of two issued alerts. First alert starts consecutive reviews, including that window; review caps are 2, 4 and 8. Further alerts do not extend the review schedule. Same caps do not imply equal realized workloads or computational cost. Logging labels are shared and immediately available at window end; delayed or budgeted label acquisition is not implemented.

Score current incumbent decisions before applying updates. A review fits a common candidate using 70% of the current labelled window; 30% is a holdout stratified by age-group x treatment. Compare candidate and incumbent policies using held-out AIPW net-value differences with frozen baseline nuisance models. Accept if mean gain minus 1.96*SE exceeds zero; otherwise retain incumbent. Accepted models affect the NEXT window only.

Repeated pointwise gate intervals offer no anytime-valid or sequential safety guarantee. True effects are used only for offline scoring and oracle audits, never for fitting, monitoring or acceptance gates.

## 6. Outcomes and interpretation

For window t, net value g_i=true_effect_i-10, action a_i in {0,1}:

    window_regret = mean(max(g_i,0) - a_i*g_i)
    postchange_cumulative_regret = sum(window_regret for windows 7 through 12)

This sum has units of incremental-spending-minus-assumed-cost per customer, summed across windows. It is not total profit across all customers. mean_loss remains a compatibility alias for the mean cumulative result across seeds. The explicit per-period field divides it by six.

Main comparison of interest: paired M2 minus M0 regret; also inspect M2 minus M1 and incremental M3 minus M2. Current code additionally reports M1 minus M0. Report every scenario and all budgets; no primary budget or winning scenario is retrospectively selected. These are exploratory contrasts, not a newly declared confirmatory primary analysis.

Secondary outcomes:
- Change detection probability, missed-run count, delay conditional on detection.
- Detection means first ISSUED alert at/after window 7; delay 0 means same-window detection after labels, not zero real-world latency. Prechange alerts can exhaust the alert cap. Detection is a mechanism-change endpoint, not necessarily harmful-policy detection.
- Stable detection fields are not applicable (NaN), while stable false-alert probability remains defined.
- Alerts, reviews and accepted retrains, reported separately.
- Mean window CATE RMSE (not pooled RMSE); attribution MAE against synthetic oracle attributions; change from original fitted-model attributions.
- harmful_treatment_rate is the fraction of ALL customers treated with negative net effect; it is not conditional on being treated.
- Frozen T-learner, treat-all and treat-none benchmark policies are saved in benchmarks.csv.

Harm-specific precision/recall, real profitability, label-delay robustness, context-aware detector baselines, periodic retraining and multiple-estimator sensitivity are NOT currently established by this benchmark. Do not describe them as completed.

## 7. Statistics and seed history

Paired percentile bootstrap over seeds: 5,000 resamples, 95% descriptive intervals, no multiplicity-adjusted significance claims. Five pilot seeds are insufficient for robust inference; an interval excluding zero here is not a confirmatory discovery.

Pilot: scale 110000:110020; calibration 120000:120100; held-out null 140000:140050; evaluation 100000:100005. Study: scale 210000:210100; calibration 220000:221000; held-out null 240000:240200; evaluation 200000:200050. Upper endpoints excluded.

These seeds and original study results have ALREADY been inspected. The repaired pilot reproduces the original pilot's saved numerical results exactly on the same seeds. That establishes reproducibility, not new independent evidence. A study rerun on the same seeds would likewise be a reproducibility run. New hypotheses, methods or confirmatory analyses require a separately recorded prospective protocol and untouched evaluation seeds; no new seed ranges are selected in this document.

## 8. Departures from previous plan and literature recommendations

The historical v2 document specifies equal groups, effects (20,15) to (-10,45), change at 6, zero extra cost, three monitors and group confidence-bound actions. This implementation instead has random age groups, effects tied to age, shift at 7, assumed cost 10, four monitors and candidate-model gates. Preserve both versions; do not backdate alignment.

The reassessment recommended richer covariates, additional estimators, context-aware detection, delays, label budgets, periodic retraining and external validation. Current code is a narrower synthetic exploratory prototype, not fulfilment of that entire recommended protocol. Whether extensions are needed depends on the final literature audit and agreed paper claims.

## 9. Checkpoint and next actions

Completed: verified source repairs, 14 tests on the researcher's laptop, basic pipeline, smoke run, pilot run_20261101_105657, period/run arithmetic reconciliation, exact old/new pilot reproducibility, repair branch pushed at 06e0c79.

Next sequence:
1. Save this aligned plan alongside the historical v2 document and commit the documentation.
2. Audit the closest literature sources identified by the reassessment: first Feng's monitoring comparison, OnlineCML/CausalStream, conditional drift work and explanation audits. Record full-text evidence or unknown, never infer absence from missing details. The document's citations themselves still require verification.
3. Map the precise intended contribution to what current code measures; decide needed extensions before expanding experiments. In particular, distinguish subgroup effect monitoring from assignment contrast and explanation stability from effect correctness.
4. Only then define the next prospective experimental protocol, compute budget, untouched seeds and any multiplicity strategy. Retain all earlier favourable, null and adverse results.

Do not claim full publication readiness, universal novelty or superiority of M2/M3 from these checks. No extra experiment is required merely to make the hypotheses look successful.
