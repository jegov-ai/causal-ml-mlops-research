# Paper 1: model/onset sensitivity development findings

Audit date: 8 November 2026 (Malaysia). Evaluation performed 6 November 2026.
Run: model_onset_sensitivity_v1_development/run_20261106_102857_143041.
Committed source: 75190bb4762667dc9c0fec8a4bd66a866ac59511.
Status: completed engineering development; audited saved-output consistency. Three evaluation seeds per scenario, not a main inferential study.

## Finding and decision

The added aggregate and subgroup causal statistics did not change recorded treatment-policy loss relative to the conventional M0 monitor in any matched development comparison. This held across the three initial training/fitting realizations, three shifted-scenario onset choices and review caps 2/4/8. The positive result is conditional adaptation benefit: in the opposing-change scenario with onset4, the adaptive methods had lower mean loss than treat-all. However M0, M1 and FULL shared that benefit, so it is not an incremental causal-monitoring benefit.

Recommendation: preserve these development findings and do not automatically launch a larger copy of this grid. The engineering objectives are complete. A larger study would improve precision but is not presently motivated by an observed incremental signal effect or a newly established literature contribution. The existing result can support a narrowly scoped evaluation of redundancy/limits; whether to expand requires a specific additional scientific question and a separately frozen protocol. No generator, gate, initial fit or seed is changed to manufacture superiority.

## Exact scope and counts

Initial data/fitting seeds42/1042/2042; shifted onsets4/7/10; stream seeds420300–420302; five original scenarios; n1000 and12 windows. Stable streams were evaluated once at scoring-onset marker7. The resulting117 distinct fit/scenario/onset/stream configurations are dependent factor evaluations, not117 independent random replications. Each comparison has351 paired method-budget observations, comprising repeated caps, initial fits and onset views of the same three stream seeds.

Outputs:16848 period rows,1404 method-budget run rows,4212 benchmark period rows,468 summary rows and5967 paired development contrasts. Main endpoint is mean period-average post-onset oracle-relative net-benefit loss, with cumulative loss also saved. Different onsets have different remaining horizons; per-window averaging does not remove that opportunity difference. Units are simulated per-customer net-benefit opportunity loss, not total business profit.

## Monitoring signals versus decision outcomes

FULL minus M1 and M1 minus M0 were exactly zero in all351 saved paired observations, for both cumulative and per-window loss. This is observed equality, not population equivalence.

Compared with M0, M1 scores differed in279 period rows, but issued alerts, reviews, accepted-update flags, recorded loss and treatment rates did not differ. FULL scores differed in1872 period rows; issued alerts and reviews each differed in18 rows. Accepted-update flags, recorded loss and treatment rates still agreed. Repeated cap rows are not independent incidents. Customer-level action arrays are not saved, so this audit does not independently establish equality of each individual action.

The conventional M0 monitor detected covariate, response and opposing changes at the first shifted window in every evaluated stream. Assignment shifts were also detected in all evaluated streams, with at most one window of delay. Thus the stronger signal definitions again had little or no earlier window-level detection opportunity. The data do not show that subgroup monitoring is unnecessary in every other environment.

## All main comparison directions

The following counts describe mean differences within each initial-fit/scenario/onset/cap cell, averaging its three paired stream seeds. The117 cells are dependent; these are descriptive tallies, not a binomial significance analysis or an equally weighted population effect.

| Comparison (first minus second) | Lower loss | Equal within numerical tolerance | Higher loss |
| --- | ---: | ---: | ---: |
| FULL minus M1 | 0 | 117 | 0 |
| M1 minus M0 | 0 | 117 | 0 |
| M1 minus PERIODIC | 24 | 77 | 16 |
| M1 minus treat-all | 9 | 0 | 108 |
| M1 minus frozen initial policy | 33 | 84 | 0 |

The9 mean cells favoring M1 over treat-all were all opposing/onset4 (all3 initial fits ×3 caps). Within those cells every individual paired observation also favored the adaptive policy. Remaining cells favored treat-all on mean loss. Some onset7 individual observations favored adaptation, but no onset7 cell mean did. In stable/covariate/assignment scenarios, treat-all is oracle-optimal by construction because both true subgroup effects exceed cost10.

The M1–PERIODIC range contains gains, ties and losses. We must not describe all alert-triggered reviews as superior to calendars. Earlier change provides more opportunities for a helpful accepted update to affect subsequent decisions. This is an interpretation of the controlled timing factor and logged behavior, not evidence of a new timing algorithm.

## Calibration limits

Each fitted initial model received separate stable scales, thresholds and null assessment. The40 saved calibration maxima per monitor were checked against their recorded higher95th-percentile threshold. Independent held-out null results were0/20 for all monitors under initial seed42,2/20 under1042, and0/20 under2042. These are small engineering samples, and the repeated monitors/initial fits share null stream seeds. They are not a precise validation of a5% false-alert target, nor60 independent streams per monitor/model-population claim. No threshold was retuned from evaluation or held-out outcomes.

## Audit

All95 independent saved-output/provenance checks passed. Checked source/protocol/historical snapshot hashes, launch-to-manifest agreement, completion/configuration, exact factor/seed coverage, unique keys, full windows, stable-once accounting, period-to-run loss and event aggregation, post-window means, resource caps, every1404 review/alert schedule, recorded gate decisions, detection applicability/delay, all468 summary means, per-fit thresholds/null seeds, all benchmarks and all5967 paired contrasts.

The original program's8 saved checks also reported passed. These are consistency/provenance checks, not95 independent statistical tests or a fresh reproduction of all model fits. Individual action arrays, scale-stream observations and gate-observation gains were not reconstructed; mathematical/program tests and historical provenance checks provide separate engineering evidence. The user's35 Windows regression tests had passed before this run.

## Measured runtime and main-study feasibility

Total32.08 minutes (1925.084seconds). Recorded setup8.279seconds; calibration861.650seconds (14.36minutes); evaluation1044.673seconds (17.41minutes). Remaining time covers analysis/output overhead.

Illustration only: increasing evaluation from3 to100 seeds per scenario at the same factor grid multiplies evaluation configurations by33.33. Increasing per-fit scale/calibration/null counts from10/40/20 to100/1000/200 changes total stable streams from70 to1300 per fit (18.57×). Naive linear scaling gives about9.67hours evaluation plus4.45hours calibration, roughly14.1hours before additional overhead. This is not a runtime promise or selected main configuration. Repeated partial CSV writes, caching, machine load and different phase costs can break linear scaling; a full runner would need output-efficiency review. No main mode, main sample-size justification or main seed allocation is supplied by the development script.

## Next checkpoint

Preserve the archive and commit these audited findings. Development namespaces420xxx are now exposed and must not be used as untouched main streams. Keep the historical ablation, calendar, spacing and corrected simple-policy benchmark findings separate. Do not update the manuscript to claim causal superiority, equivalence, explanation benefit or publication acceptance. The next action is scientific synthesis of these results with the previous studies; a further experiment needs a specific question rather than an automatic larger rerun.
