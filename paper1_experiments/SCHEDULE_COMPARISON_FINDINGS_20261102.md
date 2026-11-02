# Paper 1: audited fixed-schedule comparison findings

Date: 2 November 2026 (Malaysia).
Run: monitoring_schedule_comparison_v1_results/run_20261102_054710.
Frozen commit: 94f8e62aab67204dc9e92414fc8ac90d444198f8.
Status: completed, audited, prospectively specified exploratory comparison. Not a novelty certification or confirmation of publication readiness.

## Plain-language conclusion
Review timing mattered in this benchmark. Alert-triggered reviews had lower average postchange loss than the chosen fixed calendars when treatment effects changed. Scheduled reviews sometimes had lower loss in stable or other non-response-shift settings. Added subgroup monitoring did not improve upon M1 on any evaluated seed-budget cell and sometimes increased loss. Preserve both the useful timing comparison and the negative subgroup findings.

## Design and scope
Five arms: M1, M2-A, M2-B, M2-FULL and PERIODIC. 100 paired seeds per scenario, five scenarios, three review caps (2/4/8), 12 windows, 1,000 customers/window, shift at 7 and assumed cost 10. Same initial T-learner, candidate estimator and held-out AIPW acceptance gate across arms; accepted updates affect the next window only.
Fresh evaluation seeds 350000-350099. Four alert thresholds/centers/scales intentionally reused unchanged from the audited ablation study. Reference source hash, manifest hash, software versions and initial-model report reconcile. Periodic reviews were fixed prospectively: cap 2 at 4/8; cap 4 at 3/6/9/12; cap 8 at 1/3/4/6/7/9/10/12. Last-window reviews count toward workload but cannot improve within-horizon decisions. PERIODIC has no alerts or meaningful change-detection endpoint.
Runtime: 7,145.938 seconds, 119.10 minutes (about 1 hour 59 minutes). The previous ablation and pilot findings remain separate and unchanged.

## Complete M1-versus-calendar result
Difference = M1 minus PERIODIC in cumulative period-average postchange regret. Negative favors alert-triggered M1. Units are simulated net-benefit opportunity loss, not total company profit. Intervals are pointwise descriptive paired-bootstrap intervals, not multiplicity-adjusted confirmatory tests.

| Scenario | Cap | M1 loss | PERIODIC loss | Paired mean difference | Descriptive 95% interval |
| --- | ---: | ---: | ---: | ---: | --- |
| stable | 2 | 5.711900 | 5.688600 | 0.023300 | [0.000000, 0.057356] |
| stable | 4 | 5.712000 | 5.650300 | 0.061700 | [0.002499, 0.134601] |
| stable | 8 | 5.712000 | 5.620700 | 0.091300 | [0.023447, 0.171054] |
| covariate | 2 | 3.085450 | 3.084450 | 0.001000 | [-0.015350, 0.014350] |
| covariate | 4 | 3.052200 | 3.050850 | 0.001350 | [-0.029151, 0.032551] |
| covariate | 8 | 3.050050 | 3.055850 | -0.005800 | [-0.036952, 0.024755] |
| assignment | 2 | 5.681050 | 5.682700 | -0.001650 | [-0.033601, 0.024400] |
| assignment | 4 | 5.669700 | 5.657850 | 0.011850 | [-0.052651, 0.083010] |
| assignment | 8 | 5.655900 | 5.621800 | 0.034100 | [-0.032100, 0.106451] |
| response | 2 | 15.489650 | 16.082900 | -0.593250 | [-0.970900, -0.266716] |
| response | 4 | 15.258100 | 16.093100 | -0.835000 | [-1.266564, -0.444599] |
| response | 8 | 15.193450 | 15.371450 | -0.178000 | [-0.378659, -0.011350] |
| opposing | 2 | 11.504052 | 19.119119 | -7.615068 | [-9.355841, -5.954485] |
| opposing | 4 | 11.345019 | 24.649376 | -13.304356 | [-14.865089, -11.743961] |
| opposing | 8 | 11.047568 | 11.881339 | -0.833771 | [-1.306201, -0.418000] |

All 75 prespecified interval rows were recalculated, including comparisons of every monitoring arm with PERIODIC and FULL with M1. The table does not replace those full saved results. No favorable subset is treated as a newly selected primary hypothesis.

## What changed decisions
In the opposing scenario, first postchange periodic review was window 8 at cap 2 and window 9 at cap 4; at cap 8 it was window 7. The different calendars therefore allocate opportunities differently around the fixed onset. This helps interpret the larger alert advantages at caps 2/4 and smaller cap-8 difference; it is not evidence that every periodic schedule is inferior.
Actual opposing-scenario review counts (across 100 seeds): M1 cap 2 = 2 prechange + 198 postchange; PERIODIC = 100 + 100. At cap 4, M1 = 4 + 396 versus PERIODIC = 200 + 200. At cap 8, M1 = 5 + 597 versus PERIODIC = 400 + 400. Equal caps can provide equal total reviews (caps 2/4 here) but different timing. Cap 8 is not matched actual workload. The schedule, trigger and finite horizon jointly determine these opportunities.
No model update was automatically accepted merely because a review occurred. These outcomes include the same gate and candidate learning constraints in every arm.

## Extra subgroup signals: preserve the adverse evidence
FULL minus M1 regret was zero in most seed-budget cases. Nonzero cases were all adverse:
- Seed 350025, covariate, cap 2: +0.785. FULL reviewed windows 6/7 after an early alert; M1 reviewed 7/8 and accepted at 8; FULL accepted neither.
- Seed 350025, opposing, cap 2: +23.173387. Same 6/7 versus 7/8 review schedules; M1 accepted at 8, FULL did not.
- Seed 350045, opposing, cap 2: +27.49. FULL consumed reviews at 5/6; M1 reviewed 7/8 and accepted at 7.
- Seed 350025, stable, cap 8: +0.36. FULL's early alert led to an accepted update at 11; M1 made no update. Thus the acceptance gate did not guarantee improvement in offline oracle loss.
Across seeds, FULL minus M1 mean regret differences were +0.00785 for covariate/cap 2, +0.506634 for opposing/cap 2, and +0.0036 for stable/cap 8; other cells were zero. These rare-event differences and their unadjusted intervals do not support a universal harmful-effect claim. They do document how early false alerts can consume scarce review opportunities. M2-A matched FULL regret; M2-B matched M1 regret in these results.
The earlier 340000-340099 main ablation found exact zero incremental regret differences. This new seed set provides additional adverse cases; it does not retroactively change the earlier result or justify seed selection.

## Audit
110 checks passed, plus row-wise validation of all 7,500 review/alert schedules. Reconciled 90,000 period rows, 7,500 run rows, 75 summaries, 75 paired interval rows and 18,000 benchmark rows. Checked completion/configuration, exact script/protocol/reference hashes, software versions, untouched reference thresholds, fresh recorded evaluation seeds, full design coverage, unique keys and 12-window histories. Recomputed period-to-run regret and event sums, caps, gate acceptance consistency, exact fixed calendars and alert-triggered schedules, detection applicability/timing, finite/nonnegative metrics, summary means, attribution additivity and every bootstrap mean/interval.
This is saved-output consistency/provenance validation, not an independent reproduction of all random-forest fits. Individual customer actions and calibration-stream maxima were not reconstructed. Existing tests cover signal isolation and next-window timing. Shared cached fitting is joint benchmark compute, not separate per-arm deployment runtime.

## Manuscript contribution and limits
Supported claim: in this controlled synthetic evaluation, the timing of review opportunities affected policy loss; monitoring-triggered reviews outperformed the selected fixed calendars in treatment-effect-shift settings, while richer subgroup signals did not improve on M1 and early false alerts sometimes exhausted scarce reviews.
Do not claim new drift detection, a universally superior controller, causal-aware superiority over conventional M0, or proven novelty. M1 already includes conventional and aggregate causal statistics; M0 was not an arm in these two new studies. No real-world external validation, deployment feedback, delayed labels, alternative initial models, alternative fixed calendars or sequential-safety guarantee is established. Lower-loss comparisons remain exploratory and conditional on this generator, onset, horizon, estimator, gate and chosen schedules. Same review caps are not identical resources. CausalStream and OnlineCML full manuscripts remain unavailable and full overlap unresolved.

## Next checkpoint
The authorized additional comparison is complete and audited. Preserve the raw ZIP, code, protocol and all positive/null/adverse results. Commit this record; then draft Paper 1's methods, results and limitations using the audited studies. Use the literature comparison and supervisor review to assess whether the scoped contribution is sufficient. Do not launch further tests merely to secure a favorable result or promise publication acceptance.
