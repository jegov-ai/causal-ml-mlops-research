# Retrospective gate diagnostic findings — 8 November 2026

Reference: model_onset_sensitivity_v1_development/run_20261106_102857_143041.
Replay: gate_diagnostic_replay_v1_results/run_20261108_143830. Runtime 22.27 minutes.
Status: completed retrospective diagnostic analysis of exposed development seeds, not independent or confirmatory evidence.

## Reconciliation
All 16,848 reproduced period rows reconcile with the original across all original columns at rtol=atol=1e-12 (categorical event indicators unchanged). All 5,310 diagnostic rows uniquely match original review events; recorded gate means, lower bounds and acceptance flags agree. Missing next-window benefit occurs exactly at period 12. This verifies saved-output consistency; individual diagnostic benefit values cannot be independently reconstructed because per-customer actions were not saved.

## Definition
Positive benefit is incumbent oracle regret minus candidate oracle regret on the same observations. Helpful/harmful/tied use absolute tolerance 1e-10. Gate-sample benefit and next-window benefit are different diagnostics. The next-window comparison holds both models fixed and does not simulate an alternative future controller trajectory.

## M1 results
There were 1,224 reviews, 92 accepted and 1,132 rejected. Of the rejected reviews, 111 occurred in window 12 and had no next-window endpoint. Among the remaining 1,021 rejected review records, 551 candidates were helpful on the next window, 466 harmful and 4 tied. All 92 accepted review records were helpful on their next window in this replay.

In response-shift records, 265 rejected candidates were helpful on the next window and 7 harmful; 27 rejected final-window reviews were unevaluable. Seven updates were accepted and helpful. These aggregate repeated review records across onsets, initial fits and caps are not independent opportunities or distinct deployments. Helpful rejected candidate gains must not be summed as achievable all-horizon savings.

## Other arms and adverse evidence
M0 has exactly the same aggregate classification counts as M1. FULL has 554 helpful, 466 harmful and 4 tied rejected next-window comparisons, with 108 rejected final-window reviews. It also has 92 helpful accepted comparisons. These facts do not show a causal-monitoring advantage.

PERIODIC has 84 helpful and 2 harmful accepted next-window review records, plus 5 final-window accepted reviews with no next-window endpoint. Its 1,547 rejected records include 552 helpful, 750 harmful, 16 tied and 229 unavailable next-window comparisons.

The 2 harmful accepted PERIODIC records are the same initial fit 42, stream seed 420302, covariate scenario/onset10, review window9, repeated at caps4/8. Candidate benefit was +0.05 on the gate sample but -0.065 on the next window. They are not two independent failure incidents. This directly illustrates why same-window acceptance evidence need not describe next-window utility under a shift.

## Interpretation
The gate rejected both helpful and harmful candidates. That supports investigating its selectivity; it does not justify removing or weakening it. In the response scenario, detection was timely and useful candidates were sometimes present at reviews but rejected. This is descriptive evidence of a downstream acceptance constraint in these recorded cases, not a complete causal decomposition or proof of population conservatism. Candidate quality and finite-sample gate noise remain relevant, and the next-window observations are finite samples.

The diagnostic adds an explanation of the existing null outcomes; it does not establish a new detector, a superior controller or publication-level originality. Existing main, calendar, adverse and benchmark findings remain unchanged. No new simulation policy is authorized by these results.
