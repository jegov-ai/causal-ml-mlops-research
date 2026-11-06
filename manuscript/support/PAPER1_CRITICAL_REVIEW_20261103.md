# Critical review of Paper 1 review draft v6

Date: 3 November 2026. Review of existing manuscript/code/saved runs, not a new simulation. Historical protocols, outputs and manuscripts remain unchanged.

## Decision

V6 is an internal review draft, not submission-ready. A material reporting omission must be corrected: saved treat-all, treat-none and frozen-model benchmarks were not integrated into the main results. All five calendar-study arms are now compared against all three benchmarks in 225 post-hoc contrasts, covering all five scenarios and three caps. No favorable subset was selected. These contrasts were NOT added to the prospective primary analysis retroactively.

## Major finding 1: the simple treat-all benchmark changes the interpretation

In the calendar study's 100 paired seeds per scenario, treat-all had lower mean cumulative postchange loss than M1 and PERIODIC in all 15 scenario/cap cells for each method. Stable, covariate and assignment scenarios have true treatment effects 40/15 and cost 10, so treat-all is the oracle policy in these scenarios and has exactly zero regret by construction. This does not mean a deployer knows the oracle; it identifies a structural feature of this generator and a necessary practical comparator.

In response and opposing scenarios, treat-all incurs positive loss by treating younger customers with effect 5 below cost 10. Nevertheless its mean loss is 10.659150, below all M1 and PERIODIC mean losses in the calendar experiment. M1's advantage over the selected calendar must therefore not be presented as evidence of an overall best policy. Paired intervals below are descriptive post-hoc intervals, not confirmatory tests or proof of uniform seed-wise dominance.

## M1 versus treat-all: all scenario/cap cells

Positive means M1 had greater loss. Intervals use 5,000 paired bootstrap resamples, RNG 20261103. They are unadjusted across the new 225 contrasts and concern this fixed fitted initial model and simulator.

| scenario | review_budget | mean_policy_regret | mean_benchmark_regret | mean_difference | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- |
| assignment | 2 | 5.681050 | 0.000000 | 5.681050 | 5.636250 | 5.720800 |
| assignment | 4 | 5.669700 | 0.000000 | 5.669700 | 5.618393 | 5.713002 |
| assignment | 8 | 5.655900 | 0.000000 | 5.655900 | 5.599299 | 5.705802 |
| covariate | 2 | 3.085450 | 0.000000 | 3.085450 | 3.051900 | 3.114951 |
| covariate | 4 | 3.052200 | 0.000000 | 3.052200 | 3.004398 | 3.097753 |
| covariate | 8 | 3.050050 | 0.000000 | 3.050050 | 3.000749 | 3.095603 |
| opposing | 2 | 11.504052 | 10.659150 | 0.844902 | 0.087266 | 1.748127 |
| opposing | 4 | 11.345019 | 10.659150 | 0.685869 | 0.063262 | 1.436992 |
| opposing | 8 | 11.047568 | 10.659150 | 0.388418 | -0.053436 | 0.896606 |
| response | 2 | 15.489650 | 10.659150 | 4.830500 | 4.407586 | 5.219211 |
| response | 4 | 15.258100 | 10.659150 | 4.598950 | 4.165300 | 4.990012 |
| response | 8 | 15.193450 | 10.659150 | 4.534300 | 4.097723 | 4.929954 |
| stable | 2 | 5.711900 | 0.000000 | 5.711900 | 5.683349 | 5.741650 |
| stable | 4 | 5.712000 | 0.000000 | 5.712000 | 5.684099 | 5.742203 |
| stable | 8 | 5.712000 | 0.000000 | 5.712000 | 5.684199 | 5.741851 |

## Major finding 2: detection ceiling limits what the null ablation can establish

M1 detected the opposing change in window 7 on all 100 calendar-study seeds at every cap. The earlier ablation similarly recorded immediate detection for covariate, response and opposing changes. These streams do not provide an earlier window-level detection opportunity for extra subgroup signals. Thus zero incremental regret is a benchmark boundary, not evidence that subgroup monitoring fails in environments where aggregate/conventional signals are less responsive. Preserve the opposing scenario's conventional outcome-distribution signals; do not remove them after observing results to manufacture a subgroup win.

## Major finding 3: a review is often not an accepted update

In the response scenario, M1 had at least one accepted update in 16%, 24% and 32% of calendar-study streams at caps 2, 4 and 8. Detection alone did not imply adaptation. This may reflect the candidate learner, finite gate data and conservative pointwise rule; saved acceptance rates cannot isolate which cause dominates. Do not claim a proven bottleneck mechanism without a controlled follow-up.

## Major finding 4: fixed onset and calendars restrict timing conclusions

At caps 2 and 4, the selected calendar's first postchange reviews were windows 8 and 9, later than onset 7. Timing advantages are conditional on that allocation. No onset sensitivity or alternative-calendar study has been performed. These are limitations if the paper stays narrowly exploratory, and evidence requirements if claiming general timing robustness.

## Manuscript corrections required before external submission

- Add the three saved policy benchmarks to methods/results and point to all 225 new post-hoc contrasts.
- State explicitly in abstract/discussion that observed alert-versus-calendar gains did not beat treat-all on mean loss in this calendar study.
- Explain the oracle treat-all structure in the three non-response-shift scenarios and the window-level detection ceiling.
- Report accepted-update rates alongside detection and review counts; avoid attributing null differences solely to the monitors.
- Keep calibration differences, actual workload, fixed initial model, unavailable-paper risk and unadjusted exploratory intervals explicit.
- Replace project-management phrases in the scientific body with a clean scope statement when making a journal-formatted version. Do not erase the external provenance/novelty records.

## Exact replacement discussion paragraph

“The comparison with fixed review calendars does not establish superiority over simple treatment policies. In the saved calendar-study streams, treating every customer had lower mean postchange opportunity loss than both M1 and PERIODIC at every evaluated cap and scenario. In stable, covariate and assignment scenarios, both subgroup effects exceeded the assumed cost, making treat-all the oracle action by construction. Under response and opposing changes, treat-all incurred positive regret but still had lower mean loss than the evaluated adaptive arms. Consequently, the observed benefit of alert-timed reviews is a relative improvement over the selected calendars within this benchmark, rather than evidence of a best-performing treatment strategy. These benchmark comparisons were added post hoc and are reported as descriptive diagnostics.”

## Next scientific action

Correct the benchmark reporting before making submission or contribution-sufficiency claims. The current evidence can support a carefully bounded exploratory evaluation. If stronger claims are required, specify an untouched sensitivity study that varies shift onset and initial model independently; no settings or new seeds are selected in this review. A new test is not required merely to report the current result honestly.

This review did not rerun candidate fits or Windows unit tests. The new computation aggregates existing saved benchmark rows and produces paired diagnostic contrasts. Full-precision CSV is authoritative; displayed means are rounded.
