# Refreshed gate development findings — 8 November 2026

Run: refreshed_gate_development_v1_results/run_20261108_162422. Intended source commit before execution: d35425b (reported Windows commit; the runner does not store this Git identifier). Runtime 44.13 minutes. Status: completed, reconciled exploratory development on three exposed stream seeds. No independent confirmation or superiority claim.

## What changed
Only AIPW gate outcome predictions changed from frozen baseline models to candidate models trained on the current training partition. The gate observations remained separate from fitting, and the 1.96 multiplier, known propensity values, monitoring, review schedules, scenarios and seeds stayed unchanged. Each gate maintained its own policy trajectory. Historical files remain unchanged.

## Reconciliation
Recomputed all 1,404 paired outcome rows from 33,696 period records. The frozen arm reconciles with all original 16,848 period records. Both gate variants have identical monitoring scores, thresholds, alerts and review flags. All 10,620 diagnostic records match reviews and recorded acceptance decisions. Script/protocol/reference manifest hashes reconcile with the uploaded snapshots. All histories contain 12 windows; final-window missing next-window benefit is preserved. This is saved-output/provenance verification, not independent reproduction of all model fits or reconstruction of individual diagnostic actions.

## Full paired comparison
Negative refreshed-minus-frozen loss favors refreshed. Sign classification uses absolute tolerance 1e-10. These dependent repeated records are not independent replications.

| Monitor | Lower loss seed records | Tied | Higher loss | Total |
| --- | ---: | ---: | ---: | ---: |
| M0 | 29 | 307 | 15 | 351 |
| M1 | 29 | 307 | 15 | 351 |
| FULL | 29 | 307 | 15 | 351 |
| PERIODIC | 8 | 324 | 19 | 351 |

Averaging the three stream seeds within each initial-fit/scenario/onset/cap cell yields 117 dependent cells per monitor. M0, M1 and FULL each have 22 lower-loss, 83 tied and 12 higher-loss cell means. PERIODIC has 7 lower, 92 tied and 18 higher. These counts are neither significance tests nor population probabilities, and the number of winning cells is not itself a deployment objective.

## Conditional effects
For M1, response-shift mean differences were nonpositive in every initial-fit/onset/cap cell. Averaging across initial fits/caps within onset gives -0.166091, -0.033889 and -0.101667 mean-period loss units at onsets4/7/10. Opposing-shift results changed direction: +0.059048 at onset4, -0.276538 at onset7 and +0.160370 at onset10. These are descriptive dependent-cell averages with different remaining horizons, not pooled independent estimates.

One adverse case, initial fit1042, seed420302, opposing onset10, increased cumulative post-onset loss by 4.33 and mean-per-window loss by 1.443333 at each cap. The three cap records repeat the same underlying stream; they are not three independent failures. Full cell and paired tables retain every result.

## Accepted updates and next-window diagnostic
For each of M0/M1/FULL, frozen had 92 accepted review records, all helpful on the next window. Refreshed had 118 accepted records: 109 helpful and 9 harmful. These are 17 more helpful and 9 more harmful records in aggregate, not matched one-for-one incremental acceptance effects, because incumbents diverge across gates. The absence of harmful frozen records in this sample is not a safety guarantee.

PERIODIC frozen had 84 helpful,2 harmful and5 final-window accepted records. Refreshed had73 helpful,0 harmful and7 final-window accepted records. Missing future-window measurements do not count as zero or harmless. Candidate benefit compares fixed models on the next observed window, not a full counterfactual controller trajectory.

## Decision
The refreshed gate is a plausible modification with observed benefits and harms, not a validated system-wide improvement. Do not replace the frozen baseline or claim causal monitoring superiority: M0/M1/FULL period losses remain equal within each gate variant. This development comparison supplies evidence of a trade-off, not a novel estimator or certified research gap.

Preserve this complete comparison in the manuscript supplement. Any claim of improved performance needs a separately frozen validation protocol and untouched audited seeds, with an explicit decision-relevant endpoint and reporting of harmful accepted updates. Do not select only response/onset7 cells after seeing these results or tune additional variants until one wins. No further run is automatically scheduled by this record.
