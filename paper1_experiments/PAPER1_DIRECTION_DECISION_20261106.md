# Paper 1: direction decision and bounded extension plan

Date: 6 November 2026 (Malaysia). Status: research decision and development specification; not an executable frozen main-study protocol. Prepared after inspecting existing results. No new experiment has been run.

## Decision

REFOCUS WITHIN PROJECT 1. Retain the completed signal-ablation question as the empirical foundation, but make the next work a controlled sensitivity evaluation of its limits. Retain all historical code, protocols, positive/null/adverse results and the corrected benchmark reporting. Do not restart the project or submit the current draft as a general superiority study.

Do not adopt “when to retrain” or “adaptation versus static policies” alone as a new novelty claim. Those questions have substantial prior work. The broad alternative proposed earlier does not by itself improve the originality argument.

Preferred Paper 1 title remains: Evaluating Causal-Aware Monitoring in MLOps: Decision Robustness Under Distribution Shift and Operational Constraints. No new title version is required. Paper 2 remains separate and provisional; this decision does not start Paper 2 experiments.

## Exact question

Under common treatment-effect estimation and update-acceptance procedures, how do initial-model variation and shift timing affect the incremental treatment-policy value of aggregate and subgroup causal monitoring relative to conventional monitoring, scheduled updating and simple fixed policies?

The historical extensions answer only parts of this question. Any new M0 comparison and sensitivity results must be labelled a new prospective extension, not retroactively part of the old ablation.

## Why this is the appropriate next evaluation

The existing studies condition on one initial fitted T-learner and one shift onset. M1 already detects response/opposing/covariate changes in the first changed window in the main ablation, leaving no earlier window-level opportunity for extra signals. Fixed calendar dates are evaluated relative to the same onset. In addition, treat-all is oracle-optimal by construction when both subgroup effects exceed cost, and had lower mean loss than M1/PERIODIC even in the response/opposing calendar-study cells.

These facts do not invalidate the saved results. They restrict interpretation and identify the variables that must be assessed before stronger generalization. No scenario or threshold will be changed to make a monitor win.

Recomputed existing calendar-study means (same 100 seeds per scenario):

| Scenario | Frozen initial policy | Treat-all | M1, cap 2 | M1, cap 4 | M1, cap 8 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Stable | 5.709250 | 0.000000 | 5.711900 | 5.712000 | 5.712000 |
| Covariate | 3.109800 | 0.000000 | 3.085450 | 3.052200 | 3.050050 |
| Assignment | 5.709250 | 0.000000 | 5.681050 | 5.669700 | 5.655900 |
| Response | 16.342500 | 10.659150 | 15.489650 | 15.258100 | 15.193450 |
| Opposing | 38.173434 | 10.659150 | 11.504052 | 11.345019 | 11.047568 |

Loss is summed period-average net-benefit opportunity loss over windows 7–12. This table documents old output, not prospective extension results.

## Literature boundary checked for this decision

- Feng et al. (2024), Designing monitoring strategies for deployed machine learning algorithms: navigating performativity through a causal lens, PMLR 236:587–608. Average and subgroup causal monitoring are established; their PPV/NPV/calibration targets differ from our treatment-effect means. Primary text was selectively inspected in the earlier audit. https://proceedings.mlr.press/v236/feng24a.html
- Piaseczny et al. (2025), RCCDA, NeurIPS 38, doi:10.52202/085713-5183. Resource-aware update timing under drift is established. Our review events and policy-loss endpoint are a narrower evaluation distinction. https://proceedings.neurips.cc/paper_files/paper/2025/hash/e3d1b6d954a204267fd334cbaf9cd4af-Abstract-Conference.html
- Regol, Schwinn, Sprague, Coates and Markovich (2025), When to retrain a machine learning model, ICML/PMLR 267:51369–51404. The official abstract describes a retraining decision formulation and uncertainty-based forecasting, with classification experiments on seven datasets and cost-tradeoff robustness. This check was abstract/metadata-level; the attempted alternate PDF route returned 404. No full-text exclusion claim is made. https://proceedings.mlr.press/v267/regol25a.html
- Berrevoets et al. (2022), doi:10.1515/jci-2020-0009. Prior targeted full-text inspection already established causal treatment decisions under drift, monitoring-triggered retraining and decision-based regret. This remains a close comparator.
- CausalStream and OnlineCML complete-manuscript overlap remains unresolved. Dasari's arXiv:2608.19488 retraining-policy preprint is also access-limited in this session. Keep all three in the evidence record; unsuccessful access does not justify claiming their design elements absent.

Bounded assessment: pursue a controlled sensitivity/replication-and-extension contribution. No verified first-of-its-kind or publication-sufficiency conclusion follows from this search. A sensitivity grid improves evidential strength only if it delivers interpretable information; more runs do not create novelty by themselves.

## Limited development plan

Purpose: verify implementation, pairing, calibration and attainable compute for the sensitivity design. Development outcomes are permanently exposed; they are not the later inferential study.

### Factors

- Preserve the five generator scenarios: stable, covariate, assignment, response and opposing. Preserve baseline and postshift effect magnitudes, spending/noise distributions, known randomized logging propensities and assumed cost 10.
- Preserve 12 windows of 1,000 customers. Shift onsets: 4, 7 and 10, changing only the onset parameter. Stable streams have no actual change.
- Three initial training-dataset realizations, generated using the original mechanism and the same 800/200 allocation and forest settings. This varies training-data realization as well as fitting randomness and must be described that way. Historical seed 42 can be an anchor; all exact allocations require a source/history/CSV audit before freezing. Do not choose initial fits by their observed policy performance.
- Score decisions before current labels; accepted models affect only the next window. Preserve the common 70/30 candidate/gate split and baseline-nuisance AIPW gate. No oracle in eligibility or updates.

### Arms and baselines

Adaptive arms: M0 conventional-only, M1 conventional plus aggregate AIPW, M2-FULL adding subgroup effects and assignment contrast, and the existing fixed-calendar controller. Preserve caps 2/4/8 and two-issued-alert cap where applicable. Fixed calendars remain the historical dates; they must not be shifted to follow the known simulator onset. Report the onset/calendar alignment.

Fixed benchmarks: treat-all, treat-none and the corresponding frozen initial T-learner. These are recorded on exactly the same windows and customers. Do not select the best benchmark using evaluation truth and call it deployable. Subgroup-only and assignment-only historical ablations remain in the paper; they are not silently replaced by a claim that FULL isolates subgroup effects.

Re-estimate centers/scales and each monitor's threshold separately for each initial fitted model, with independent stable scale/calibration/null streams. Historical thresholds cannot automatically transfer to another initial model. Calibration uses the same 12-window horizon and common intended any-alert target. Do not retune from null/evaluation outcomes. Pair future evaluation streams across models/arms/onsets where the generator supports common random inputs, documenting exactly what is shared.

### Development size and output

Three stream seeds per scenario, three initial fits and three onsets yield 135 initial-fit/onset/scenario/stream configurations before arms/caps. Stable streams reused across nominal onsets are the same data, not additional independent evidence. They should be computed once per initial fit/stream where possible and marked as repeated scoring views. Development calibration sizes must be set explicitly in the implementation protocol and are not research-quality calibration merely because code completes.

Record separate setup/calibration/evaluation wall times. Extrapolate main-study runtime from measured phases and their allocation counts. Do not quote the old study's total runtime as a guaranteed new runtime. No main evaluation starts until the main counts, ranges, calibration allocation, estimands, reporting rules and source hashes are frozen.

### Outcomes and comparisons to freeze before main evaluation

Primary decision quantity: mean per-customer oracle-relative net-benefit loss across available post-onset windows, with its cumulative counterpart and complete trajectories reported alongside. This makes unequal post-onset horizons visible. Historical windows-7–12 results retain their original estimand and are not pooled with this extension.

Key paired contrast: M2-FULL minus M1 within every prespecified factor cell. Supporting contrasts: M1 minus M0; each adaptive arm minus each fixed benchmark and the calendar controller. Report every cell and contrast. All extension analyses remain exploratory unless a separately justified confirmatory plan is explicitly frozen.

Initial-fit and stream dependence must be respected. Report each initial fit separately and summarize across the predeclared fits without treating arms, caps, windows or repeated onset views as independent samples. Three initial fits are a small sensitivity assessment, not broad population inference over learned models. Any resampling scheme must be specified in code/protocol before outcomes.

Record alerts, reviews, accepted updates, unused capacity, harm, detection/missed runs and delays. Common caps are not equal actual resources. Gate intervals remain pointwise with no sequential-safety claim. Zero differences remain possible and will be reported.

### Engineering acceptance and stop rules

Before launch: preserve historical source; parameterize onset and initial data generation in a new module; audit all proposed development/calibration/main seed namespaces against source, history and saved outputs; commit the intended files. No exact future seed range is certified unused in this note.

Required checks: unchanged historical configuration reproduces frozen behavior; shifting onset changes only declared trajectories; monitoring baseline/calibration correspond to the initial fit; all arms share evaluation windows; review/alert caps and next-window timing hold; simple benchmarks match analytic oracle behavior in stable settings; truth changes do not affect fitting/monitoring/controller; no accidental pseudo-replication of stable streams.

Run the bounded development set only after these checks. Stop on engineering inconsistency. Do not drop settings or extend the pilot because results favor a desired arm. After development, freeze the main protocol regardless of direction of effects, or explicitly reject an infeasible design with the reason recorded.

## Practical next action

Implement the new parameterized sensitivity module and tests against the frozen source, without altering the original scripts. Do not start main evaluation yet. First obtain current source/tests via the connected repository or a targeted source archive; the current local attachment is the frozen ablation source, not proof of the latest Windows tree.

## Completion of this decision

The keep-or-refocus decision is made: refocus the next evaluation within Project 1. The current corrected manuscript is retained as the record of completed studies. This note specifies a bounded development direction; new code, seed verification, pilot runtime and a frozen main protocol remain concrete implementation work. It is not a claim those steps have occurred.
