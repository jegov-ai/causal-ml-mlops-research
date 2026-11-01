# Paper 1: audited signal-ablation main-run findings

Date: 2 November 2026 (Malaysia).
Run: monitoring_signal_ablation_v1_study/run_20261102_012152.
Frozen source commit: 4fd595ac5dc65899c5a2273ac4c56fb7e92810fe.
Status: completed and audited exploratory simulation. Not confirmation of novelty, equivalence, or journal readiness.

## Plain-language finding
Adding the subgroup-effect clues, the group assignment-rate clue, or both did not reduce decision loss beyond M1 in this completed experiment. This is a valid negative result. We must preserve it rather than alter the experiment to obtain a win.

## Scope and provenance
All five scenarios, review caps 2/4/8, 100 paired evaluation seeds per scenario, 1,000 customers/window and 12 windows were retained. The evaluation seeds were 340000-340099; stable scale/calibration/null ranges began at 310000/320000/330000, with 100/1000/200 streams respectively. Labels were immediate; logging was exogenous; inference is conditional on one initial T-learner and the specified controller. Runtime was 9754.179 seconds (162.57 minutes, about 2 hours 43 minutes).
The source snapshot's raw SHA-256 matches the manifest and launch record. The protocol snapshot matches the frozen protocol SHA-256 after normalizing Windows CRLF line endings to LF. The saved protocol text has a line-ending difference, not a substantive protocol change.

## Numerical result
Every saved seed-wise postchange-regret difference is exactly zero for A-M1, B-M1, FULL-M1, FULL-A and FULL-B. The descriptive interaction is also zero. This holds across all four shifted scenarios and all three review caps. Stable-run regret also agrees across arms. All 72 saved paired bootstrap rows were independently recalculated and reconcile, including their zero-width [0,0] intervals.
Zero empirical bootstrap intervals here arise because the observed paired differences are all zero. They do not prove population equivalence or rule out differences in new scenarios, models or random initializations.

The following cumulative period-average regret values apply to all four variants within each cell. Lower is better; these are simulation net-benefit opportunity-loss units, not total company profit.

| Scenario | Review cap 2 | Review cap 4 | Review cap 8 |
| --- | ---: | ---: | ---: |
| stable | 5.746850 | 5.746850 | 5.746850 |
| covariate | 3.130400 | 3.110850 | 3.109250 |
| assignment | 5.747150 | 5.735300 | 5.735300 |
| response | 15.784550 | 15.573800 | 15.526250 |
| opposing | 12.904090 | 12.256387 | 11.789998 |

## Monitoring and resource findings
The arms did compute different monitoring scores: compared with M1, scores differed in 4,377 period rows for M2-A, 2,877 for M2-B and 7,029 for M2-FULL. Thus the zero regret differences are not simply identical score definitions.
M2-A had the same issued alerts, review schedule and accepted-update indicators as M1. M2-B and M2-FULL each differed from M1 in 24 alert-issue rows and 10 review-performed rows, with two extra review events in total across the saved method-budget evaluations. Their accepted-update indicators, recorded treatment/harm rates and regret remained the same. Event counts across budgets are repeated evaluations, not independent incidents.
For the assignment shift, mean detection delay was 0.02 windows for M1/M2-A versus zero for M2-B/FULL; every arm detected all 100 shifted streams. In covariate, response and opposing scenarios, every arm already detected at the first shifted window. That leaves no earlier window-level detection opportunity for the added signals in those cases. This ceiling is an interpretation of the recorded timing, not proof that added signals never matter.
Independent held-out stable any-alert rates: M1 and M2-B 5/200 (2.5%; Wilson 95% interval approximately 1.07%-5.72%); M2-A and FULL 7/200 (3.5%; approximately 1.71%-7.05%). The intended calibration target was common, but achieved rates were not exactly equal. Do not retune using these held-out results.

## Audit performed
104 aggregate checks passed, plus row-wise schedule validation over all 6,000 method-budget runs. Checked completion; configuration/commit/source/protocol provenance; 72,000 period rows, 6,000 run rows, 60 summary rows, 800 held-out-null rows, 18,000 benchmark rows and 72 interval rows; unique keys; complete windows; evaluation/null seeds; regret aggregation; alerts/reviews/accepted-update totals and caps; score-threshold alert logic; consecutive review schedules; detection timing; acceptance only on reviews with positive recorded gate lower bound; nonnegative/finite scoring fields; summary means; Shapley additivity; null summaries/Wilson intervals; and bootstrap contrast means and intervals.
This is consistency and provenance validation, not an independent reproduction of every model fit. The archive does not save each customer's action or all calibration-stream maxima; individual-action regret and empirical calibration quantiles were not independently recomputed from raw model predictions. Existing code tests cover signal isolation and next-window update behavior.

## Research interpretation and next action
Supported wording: “Under this fixed synthetic benchmark, adding subgroup-effect or group assignment-contrast monitoring yielded no observed incremental treatment-policy regret reduction beyond aggregate-effect monitoring, despite some alert and review differences.”
This four-arm extension compares additions to M1; it does not by itself establish the broader causal-versus-conventional M0 effect. M1 already contains conventional outcome/residual/feature/assignment signals and aggregate AIPW. Do not infer that causal monitoring in general is unnecessary. Do not infer equivalence or real-world safety from exact observed equality.
Preserve the adverse development-pilot findings separately; they are not replaced by the main run's zero differences. The periodic-review extension is deferred, not completed. CausalStream and OnlineCML complete manuscripts remain unavailable and full overlap unresolved. This result neither certifies nor eliminates the candidate research gap.
Next: preserve the raw archive and these audited findings in the project record, then use existing evidence to draft the evaluation results and limitations for supervisor review. No new experiment is justified merely to obtain superiority. Any future extension needs a separately documented question and prospective protocol.
