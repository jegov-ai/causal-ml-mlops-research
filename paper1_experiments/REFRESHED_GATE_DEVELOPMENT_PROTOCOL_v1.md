# Refreshed gate outcome models: development comparison v1
Prepared 8 November 2026, after inspecting retrospective diagnostic results.

## Question and status
Does replacing frozen initial outcome predictions with current candidate outcome predictions inside the AIPW update gate change treatment-policy loss and harmful accepted updates? This is exploratory development on the already exposed sensitivity streams. It is not independent confirmation, a new doubly robust method, or a validated improvement. Preserve all historical results.

## Single change
Frozen: net_pseudo = aipw_effect(gate, baseline) - COST.
Refreshed: net_pseudo = aipw_effect(gate, candidate) - COST.
The candidate was fitted on the current 70% training partition; gate outcomes remain in the separate 30% partition. Do not fit the candidate on gate outcomes. Use the same known logging propensities and the same candidate to score both candidate and incumbent policies on the gate sample. The acceptance rule remains mean gain minus 1.96 standard errors greater than zero. No tuning of the multiplier, cost or synthetic effects is allowed in this comparison.

Outcome-model accuracy can affect doubly robust evaluation variance; the statistical background is Dudik, Langford and Li (2011), https://icml.cc/2011/papers/554_icmlpaper.pdf. This reference does not guarantee lower variance from the candidate model, valid finite-sample coverage under the implemented stratified split, sequential safety, or downstream improvement. These remain empirical limitations.

## Fixed conditions and pairing
Use all 117 configurations from development run run_20261106_102857_143041: initial data/fitting seeds42/1042/2042; stream seeds420300/420301/420302; four shifted scenarios at onsets4/7/10 and stable once at marker7; 12 windows,1000 customers/window; M0/M1/FULL/PERIODIC; caps2/4/8; same fixed calendars. Reuse archived per-fit calibration/background without retuning. Both gate variants start from identical initial models and retain separate incumbent trajectories. Candidate fits and partitions have identical seed rules across variants. Changes affect next-window actions only. Monitoring remains frozen and must reproduce identical scores, alerts and review opportunities across gates. The method does not change the schedule to gain an advantage.

## Execution and checks
Default limit1 is an engineering smoke check, not evidence of effectiveness. A full development comparison uses limit117 and reports all cells. No automatic full run, resume or seed substitution is supported. Preserve failed/partial runs. Require exact archived source bytes and matching Python/library versions. The original gate must reproduce every original period field with rtol=atol=1e-12; changed gate monitoring/review fields must match. Both variants retain exact acceptance from positive recorded gate lower bound. Stop on any mismatch. Output a new directory, runner/protocol snapshots, source/protocol/reference hashes and completion status. Existing source files and original outputs are not overwritten.

## Reporting
Report paired refreshed-minus-frozen cumulative loss and mean-per-window loss across the available post-onset horizon, by initial fit/scenario/onset/monitor/cap, keeping three stream seeds paired. Negative favors refreshed. Stable uses windows7-12. Preserve all beneficial/null/adverse outcomes. No selected primary winning cell, inferential p-values or equivalence claims. Dependent repeated cells are not independent replications.

Report accepted updates and offline true gate/next-window benefits, including harmful accepted updates and beneficial rejected candidates. Final-window next-window benefit is missing, never zero. Benefits are finite-sample diagnostics with models held fixed, not sums of realizable future savings. Compare actual full controller trajectories using regret, rather than inferring total benefit from callback events.

Any later validation requires a frozen design, fresh audited seed allocations, adequate replication and a separate protocol before evaluation. This development run cannot establish novelty or deployment readiness. A tie or worse outcome is a reportable result, not justification for post-hoc scenario changes.
