# Paper 1: fixed-schedule review comparison, protocol v1

Prepared 2 November 2026 (Malaysia), after reviewing the completed ablation run and before the new evaluation. Authorized as one additional test. Prospectively specified exploratory extension, not a preregistration, final novelty claim or supervisor-approved protocol.

## Question
Does using monitoring alerts to time model reviews reduce cumulative treatment-policy regret compared with a fixed calendar, under the same candidate estimator, acceptance gate and maximum review opportunities?
This implements Extension B already proposed in PAPER1_PROSPECTIVE_EXTENSION_PROTOCOL_DRAFT_v1.md. The completed ablation remains unchanged, including its zero main-run incremental regret effects and adverse development pilot. The schedule was specified before these main results and is not selected to beat a monitor. This test is informative even if scheduled reviews tie or outperform alerts.

## Fixed design
Five arms: the four frozen ablation arms (M1, M2-A, M2-B, M2-FULL) and PERIODIC. Existing M1 conventional/ATE signals and extra subgroup/assignment statistics remain unchanged. PERIODIC issues no alarms and uses these 1-indexed review windows:
- Cap 2: 4, 8.
- Cap 4: 3, 6, 9, 12.
- Cap 8: 1, 3, 4, 6, 7, 9, 10, 12.
PERIODIC uses the SAME current-window 70/30 training/gate split, candidate fit, AIPW net-value comparison and positive pointwise lower-bound acceptance rule. Accepted updates affect the next window only. A review at window 12 consumes a unit without a within-horizon policy benefit; keep it in workload reports. The two-alert cap does not apply to PERIODIC. It has no meaningful detection delay or false-alert endpoint. Alert arms retain their two-alert cap and first-alert consecutive-review controller.

Unchanged: five scenarios stable/covariate/assignment/response/opposing, shift at window 7, 12 windows, 1,000 customers per window, cost 10, original T-learner fit with seed 42, immediate labels, exogenous randomized logging and truth reserved for offline evaluation. Shared streams and candidate fits across arms. Explanations remain diagnostics, not inputs to these policies. No new M0-only arm is added; this test compares alert-based review including causal information to a calendar, not a complete conventional-versus-causal comparison.

## Reference calibration and provenance
Reuse exactly the frozen centers/scales and four alert thresholds from monitoring_signal_ablation_v1_study/run_20261102_012152. No new threshold optimization or retuning to the inspected null/evaluation results. The existing calibration is intentionally reused, not claimed to be fresh independent evidence. The previous null rates remain the diagnostic evidence for the unchanged alert rules. PERIODIC has no false-alert target; do not compare it on false-alert calibration.
Require identical NumPy/pandas/scikit-learn versions and exact source hashes against the reference manifest; verify the initial baseline numerical report. Record Git commit, source/protocol/reference hashes and source snapshots before new evaluation. Fail if tracked changes remain uncommitted or intended source/protocol files are untracked. Do not modify the frozen ablation script to accommodate failures.

## Fresh evaluation and resource accounting
100 paired seeds per scenario in [350000,350100), upper bound excluded. Before evaluation, scan saved project CSV seed columns and stop on any recorded collision. Prior source-seed inspection did not identify this range, but that was not proof of every external run. Record any known undocumented use before launch. A mocked engineering test uses 360009 and is not research evaluation.
500 paired scenario streams, 7,500 method-budget run rows and 90,000 period rows are expected. Seeds pair methods and budgets; do not treat repeated arms/budgets as independent replications. Same maximum cap is not equal actual reviews or compute. Report actual reviews, alerts, accepted changes and wall time. Shared candidate caching means measured joint runtime is not separate per-arm operational compute.
100 seeds is a pragmatic replication count, not a formal power calculation. This experiment is conditional on one initial model and one selected fixed calendar per budget; it cannot establish the universally best schedule or generalize over model initializations.

## Analysis and interpretation fixed before evaluation
Primary measured outcome: cumulative period-average oracle-relative regret across windows 7-12. Report all five scenarios and caps 2/4/8, including stable runs and adverse outcomes. No privileged winning scenario/budget or confirmatory primary test. Prechange regret and harmful-treatment rate provide additional context; do not change the primary horizon after observing results.
For every scenario/budget report M1 minus PERIODIC, M2-A minus PERIODIC, M2-B minus PERIODIC, M2-FULL minus PERIODIC, plus M2-FULL minus M1. Negative differences favor the first arm. Compute paired mean differences and pointwise 95% percentile-bootstrap intervals with 5,000 resamples (resampling RNG 518). Intervals are descriptive, unadjusted for multiplicity, and do not establish equivalence. Include paired distributions during audit.
If calendar wins, report that result; do not redesign dates after inspecting outcomes. If alerts win, distinguish decision benefit from unequal realized workload and calendar selection. Do not claim the generic monitoring-versus-adaptation issue is new. Prior studies already address adaptive treatment decisions, detection and retraining. CausalStream and OnlineCML complete manuscript overlap remains unresolved.

## Execution boundary
No automatic retry/resume. Preserve partial output on failure and diagnose before repeating exposed seeds. Checkpoint after each scenario. A repeated run is reproducibility, not fresh evidence. Commit code, this protocol and checks before launch. Expected runtime is approximately the previous evaluation phase (73 minutes) plus added schedule-triggered fits and diagnostics; allow roughly 1-3 hours, not a guarantee. Do not stop or reduce replication based on favorable results. This is one additional comparison, not a promise of publication readiness.
