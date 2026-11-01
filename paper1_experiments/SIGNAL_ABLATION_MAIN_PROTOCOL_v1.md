# Signal ablation: prospective main-run protocol v1

Prepared 2 November 2026 (Malaysia), after development pilot and before main evaluation.
Status: exploratory, prospectively specified extension; not preregistered or specifically supervisor-approved. Candidate novelty remains provisional.

## Question and scope
Does adding subgroup AIPW effect monitoring and/or a group assignment-rate contrast change cumulative treatment-policy regret beyond M1, with common estimators, data, response gates and review caps?
This is Extension A of PAPER1_PROSPECTIVE_EXTENSION_PROTOCOL_DRAFT_v1.md. Periodic-review Extension B is deferred. This four-arm ablation addresses incremental value beyond aggregate-effect monitoring; it alone does not re-estimate the broader conventional M0 comparison. Historical M0/M1/M2/M3 studies and their negative results remain separate exploratory evidence.

## Fixed arms and inherited conditions
M1: original conventional statistics plus aggregate AIPW effect. M2-A: M1 plus two subgroup AIPW means. M2-B: M1 plus young-minus-older assignment-rate contrast. M2-FULL: both additions, matching original M2. M1 already includes overall assignment rate; this is not removal of every assignment-related statistic. The maximum standardized score uses only the specified indices. Existing explanation diagnostics remain offline; no explanation statistic enters these four scores.
Generator, age groups, baseline T-learner, cost 10, five scenarios (stable, covariate, assignment, response, opposing), 12 windows, shift at 7, current-window 70/30 candidate/gate split, frozen nuisance models and pointwise AIPW acceptance rule stay unchanged. Only next-window policies can change. True effects remain offline evaluation only. No deployed-policy feedback or label delay is introduced. Population-stable opposing ATE holds in expectation, not every sample.
All arms share streams, candidate fits and gates; each has its own incumbent state. Two issued alerts maximum. First alert starts consecutive reviews, with caps 2, 4 and 8; later alerts do not extend reviews. Same caps are not equal realized workload. Retain prechange alerts and exhausted budgets as outcomes, not errors.

## Frozen main configuration
- 1,000 new customers/window; same one initial baseline fit, seed 42.
- Scale: 100 stable streams, seeds [310000,310100).
- Calibration: 1,000 stable streams, seeds [320000,321000).
- Independent held-out null assessment: 200 stable streams, seeds [330000,330200).
- Evaluation: 100 paired seeds/scenario, seeds [340000,340100), same seeds across arms and budgets.
Ranges exclude the upper endpoint. The five scenarios yield 500 evaluated streams, 6,000 run rows and 72,000 period rows. These repeated method/budget evaluations are not independent simulation units.
Threshold for EACH arm: higher 95th percentile of its own stable-stream maximum scores across 12 windows. Common intended 5% any-alert target; no forcing equal thresholds or realized alert rates. Check independent null rates with Wilson intervals; do not retune from held-out null or main outcomes. If rates differ, disclose differences rather than claim exact false-alert matching.

## Analysis locked before main outcomes
All five scenarios and three budgets will be reported. This entire extension remains exploratory: no single primary scenario/budget and no confirmatory significance claims. Main endpoint is the sum of period-average oracle-relative net-benefit opportunity loss over windows 7-12, not total business profit. Negative signed differences mean less regret for the first arm.
For shifted scenarios, descriptive paired contrasts: A-M1, B-M1, FULL-M1, FULL-A, FULL-B, and FULL-A-B+M1. Resample paired seed-wise differences, 5,000 percentile bootstrap resamples and 95% intervals. These are pointwise intervals unadjusted across scenarios, budgets and contrasts. Stable regret is retained in summaries. No selectively highlighted favorable cell is a confirmed discovery. The factorial contrast describes these operational variants, including calibration and controller effects, not a general causal mechanism.
Report actual alerts/reviews/accepted updates, pre/postchange regret, harmful-treatment rate, detection probability, missed runs and delay conditional on detection. Stable detection is not applicable. Window-end detection delay zero is not instantaneous real-time detection. Earlier detection does not establish lower regret. Repeated pointwise gates have no sequential-safety guarantee.
100 paired seeds is a pragmatic replication count from the earlier draft, not a formal power calculation. Report attained uncertainty and raw paired distributions; do not interpret a wide interval as equivalence or no effect. No minimum important effect or equivalence margin is established by this exploratory study. Tiny pilot variance is insufficient to certify power. Any later confirmatory study needs its own meaningful-effect and power justification.

## Prior exposure and audit
Historical pilot/study data were inspected before this extension. Development evaluation seeds 300000 and 300001-300003 were also inspected. Development scale/calibration/null seeds occupy separately documented ranges below 310000; mocked unit-test seed 300009 is development only. Do not count any repeated development run as fresh evidence.
Before development, searches of tracked Python seed code, relevant script/JSON/Markdown records, and 26 seed-bearing CSV files (66 CSV files found) showed no apparent conflicts with the proposed range. This is a scoped repository audit, not proof of every external run. Repeat the CSV check on [310000,350000) before main launch and inspect new/untracked seed-generating scripts if any appeared. Do not knowingly reuse a previously inspected main stream. Fixed initial training data and explanation anchors are intentionally historical and reused; inference is conditional on this fixed model.
Development pilot run_20261102_001734: 3 seeds/scenario, 1,000/window, 443.6355 seconds (7.39 minutes); 2,160 period and 180 run rows reconciled. A seed had a prechange assignment-contrast alert, early review use and worse later regret. Retain this adverse finding. Neither scenarios nor gates were changed in response.

## Compute, provenance and failure handling
Pilot phase timings were not separately measured. Scaling its total by the largest phase multiplier (100/3) gives about 246 minutes, approximately 4.1 hours, under linear-cost assumptions. Treat roughly 3-5 hours as a planning estimate, not a runtime guarantee; machine load, memory and output costs may change it. Scale/calibration counts increase by 10x/25x, null by 10x, evaluation by 33.3x. The main version records phase timings for assessment. Do not shrink replication/calibration midway or stop because results look favorable.
Review diff, pass tests, commit script and this protocol, and record the commit before launch. Study mode verifies this protocol's SHA-256, requires a clean Git working tree for tracked files, and saves commit/configuration/source snapshots before generating main data. Untracked output files may remain; add and commit the intended main files explicitly. Each run gets a new directory. No automatic resume or repeated independent-run claim is supported. If interrupted, preserve partial output and diagnose before rerunning. Settings changes after first main outcome require a new protocol version and explicit exploratory labeling.

## Interpretation boundary
No first/unique/100-percent-novel claim. CausalStream and OnlineCML full manuscripts remain inaccessible; complete overlap remains unknown. Broad causal monitoring, adaptation and regret ingredients are published. This study evaluates a narrower controlled comparison and can yield beneficial, null or adverse findings. No journal acceptance, real-world profitability or overall explanation benefit is established by completion.
