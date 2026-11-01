# Signal ablation: development protocol v1

Prepared 1 November 2026. Exploratory engineering phase, before any new ablation runs.

Extends the existing prospective extension draft's Extension A. Extension B (periodic review) is deferred from this two-day task. Neither novelty nor specific supervisor approval is claimed. Historical plans, scripts and outputs remain intact.

Four arms: M1; M2-A = M1 plus young/older AIPW effects; M2-B = M1 plus group assignment-rate contrast; M2-FULL = both. M1 already contains the overall assignment rate and other conventional statistics. This ablation removes only the EXTRA group contrast, not all assignment information. Explanation statistics remain offline diagnostics and never enter these four scores.

Inherited generator, estimator, scenarios, shift window 7, cost 10, gate, next-window updates, two-alert cap and review caps 2/4/8 are unchanged. Every arm has independently calibrated thresholds on shared stable calibration streams, targeting approximately 5% run-level any-alert probability. Separate held-out stable streams evaluate achieved rates. Pilot calibration is deliberately small and not an inferential calibration guarantee.

## Development seed allocation (half-open ranges)

This versions the draft's engineering allocation: development scale/calibration/null streams now also occupy reserved space below 310000. Main proposed ranges 310000 onward remain untouched by smoke/pilot modes.

| Purpose | Smoke | Development pilot |
| --- | --- | --- |
| Evaluation | 300000:300001 | 300001:300004 |
| Scale | 300010:300013 | 301000:301010 |
| Calibration | 300020:300025 | 302000:302040 |
| Held-out null | 300030:300033 | 303000:303020 |
| Customers/window | 200 | 1000 |

These ranges have no apparent collision in inspected tracked code and the initial JSON/script search, but prior saved CSV records still require audit BEFORE executing smoke/pilot. A mocked unit test uses 300009; it is development-only. Baseline seeds and explanation anchors stay historical fixed constants. No result on development seeds is new untouched-main evidence. Do not repeat a run and count it as independent replication.

Primary measured outcome is cumulative period-average oracle-relative regret across windows 7–12. Report all scenarios and budgets, paired differences M2-A minus M1, M2-B minus M1, M2-FULL minus M1; incremental FULL contrasts; and descriptive factorial interaction FULL minus A minus B plus M1. No primary scenario/budget or confirmatory hypothesis is selected. Stable arm regret is retained in summary, while change-detection contrast intervals concern shifted scenarios. All intervals are descriptive, unadjusted, and tiny-development-pilot intervals are not research conclusions.

Report actual reviews, alerts, accepted updates, detection/misses and harmful exposure. Equal caps do not imply equal workload. Explanation diagnostics are retained for comparability, so runtime includes their overhead. Any interaction interpretation is conditional on these operational variants, calibration and controller; do not claim a general causal mechanism.

Study mode is not enabled. Before main evaluation: audit recorded seeds and untracked code, measure pilot wall time, assess feasible replication and uncertainty, record final scope/settings, review code diff and commit the prospective protocol. Do not reduce calibration or select favorable scenarios after inspecting results. Negative outcomes remain valid. CausalStream and OnlineCML full-manuscript overlap remains unresolved.
