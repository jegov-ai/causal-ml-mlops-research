# Paper 1: evidence synthesis and contribution statement

Date: 8 November 2026. Last confirmed pushed findings commit: 0d428e1. The preferred Paper 1 title is retained. No new experiment was run to prepare this synthesis.

## Contribution statement

We evaluate the incremental decision value of aggregate and subgroup causal monitoring under common treatment-effect estimation, review rules and held-out update acceptance. Across the completed main ablation, added signals yielded no observed incremental regret reduction. A separate calendar comparison documented occasional adverse subgroup-monitoring outcomes. A small development sensitivity check found equal recorded loss for conventional and causal-statistic monitors while revealing that adaptation's advantage over fixed policies depended on onset and the available horizon. We report these conditional results alongside simple-policy benchmarks and resource accounting.

## Evidence levels that must remain distinct

| Evidence | What it establishes in the observed data | Boundary |
| --- | --- | --- |
| 100-seed main ablation | Zero observed paired incremental loss from added subgroup/assignment signals | One initial fit and onset7; no M0; not equivalence |
| Separate 100-seed calendar comparison | Gains against selected calendars under effect shifts; rare adverse subgroup outcomes | Fixed dates/onset; M1 already causal; no universal calendar inferiority |
| Post-hoc saved-policy benchmark analysis | Treat-all lower mean loss than M1/PERIODIC in every calendar-study cell | Post-hoc descriptive analysis, not a new prospective hypothesis |
| Two-seed spacing development | Spacing can delay a useful accepted update | Engineering check only |
| Three-stream-seed model/onset development | M0/M1/FULL loss equality; conditional early-onset adaptation benefit | Dependent factor cells, small calibration/null counts, not a main study |

## What readers can learn

Different signals, alerts and review dates need not change recorded treatment-policy loss. Review/update opportunities can yield conditional benefit even when richer monitoring statistics add no benefit. A comparison against selected calendars is incomplete without simple fixed-policy benchmarks. These are empirical boundaries in the implemented benchmark, not first discoveries of generic monitoring/adaptation limitations.

## Claims retained and rejected

Retain: a controlled comparative evaluation and transparent reporting of beneficial, null and adverse outcomes. Reject: new estimator/detector, universal superiority, population equivalence, proven explanation-stability benefit, production safety or profitability, and guaranteed publication. Prior work already covers broad causal monitoring, adaptive treatment decisions and resource-aware updating. The targeted novelty assessment records the bounded potential distinction and access uncertainty; the synthesis does not certify journal sufficiency.

## Decision at this checkpoint

Complete the scientific synthesis of the current exploratory work. Do not automatically start a larger identical grid or alter the generator to obtain a favorable causal-monitoring result. A further study requires an explicitly useful question and a separately specified protocol. A larger study could be justified by precision/replication aims, but not merely by desire for a positive result. No new simulation is scheduled here.

## Manuscript changes

The attached synthesis manuscript integrates sensitivity methods/results, revises the abstract/discussion/conclusion and corrects the old statement that no onset/model variation had been performed. It preserves the distinction between earlier main studies and small development checks, the adverse cases and the simple-policy benchmark correction. Earlier drafts remain intact. It is a review manuscript, not a submission or acceptance claim.

## Remaining work before submission

Critical assessment of whether the scoped empirical contribution is sufficient for the intended venue; final bibliographic/style checks and unavailable-manuscript access if possible; journal-specific formatting, authorship/affiliation and applicable AI-use disclosure; supervisor review. None requires inventing a favorable result. User understanding of the design and ability to explain its limitations are also essential.
