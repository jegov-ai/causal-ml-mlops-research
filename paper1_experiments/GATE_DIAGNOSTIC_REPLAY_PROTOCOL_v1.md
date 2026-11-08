# Retrospective gate diagnostic replay v1
Prepared 8 November 2026 after inspection of existing findings.

Question: At recorded review events, did candidate policies have lower oracle loss than incumbents on the held-out gate sample and on the next saved-seed window? How did this relate to acceptance?

This is a post-hoc diagnostic replay of the exposed development run run_20261106_102857_143041, not independent replication or a prospectively tested discovery. No new seed set, scenario, calibration or deployment controller is introduced. Default limit 1 is an engineering reproducibility check. A full replay covers all 117 configurations without selecting favorable settings.

Frozen source hashes must match the archived snapshots, and Python/library versions must match the reference manifest. Use the archived per-fit centers, scales, thresholds and background. Refit only the same initial/candidate models using the original seeds. Inject a read-only callback before the unchanged acceptance decision. Compare every original period field with the reference; categorical events must match, floating values have rtol=atol=1e-12. Stop on mismatch and preserve partial diagnostics. Partial output is not a successful replay.

Positive true_gate_benefit means incumbent oracle regret minus candidate oracle regret on the held-out gate sample. Positive next_window_benefit uses the same two fixed models on the next generated window. Truth is used only for offline diagnostics and never enters monitoring, fitting or acceptance. Candidate and incumbent predictions are compared before any accepted replacement. Final-window reviews have no next-window measurement and retain a missing value, not zero.

Next-window benefit is a finite-sample offline diagnostic, not population value, a new deployment policy, or the total effect of changing the gate over a future adaptive trajectory. Do not infer all-horizon regret saved by simply summing overlapping one-window candidate gains. Candidate quality on unreviewed windows is not evaluated; this replay alone cannot identify the optimal review schedule or fully decompose all lost opportunities.

Retain accepted helpful/harmful/tied candidates and rejected helpful/harmful/tied candidates using a disclosed numerical tolerance. Report all conditions and dependent repeated event counts. No p-values or equivalence claims are planned. Engineering replay outcomes must not be pooled with fresh independent evidence. The script performs no literature novelty certification.

Local checks passed: syntax; benefit sign/zero; equality pass and mismatch rejection; unique callback insertion with original function recovered exactly after removing the callback. Full numerical replay is not locally verified because the saved Windows software environment differs. First reproduce one configuration on the original Windows environment before executing all 117. No runtime guarantee is supplied.
