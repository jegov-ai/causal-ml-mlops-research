# Paper 1: Introduction and Abstract — Draft v1

Working title: Evaluation of Causal Machine Learning Integration into MLOps Pipelines for Explainable and Robust Decision Making.

Status: Exploratory manuscript draft for supervisor review. The working title is broader than the evidence presented here. Final title alignment, citation verification and novelty assessment remain pending.

## Abstract

Monitoring a changing environment does not necessarily improve the decisions made by a machine-learning system. Additional signals may identify change without producing a useful model update, particularly when review opportunities are limited. This study evaluates the incremental decision value of causal monitoring signals and the timing of model reviews in a controlled synthetic treatment-policy benchmark.

Two prospectively specified exploratory experiments used 12 windows of 1,000 customers, five distributional scenarios and review caps of 2, 4 and 8. Each experiment evaluated 100 paired seeds per scenario, conditional on one initial random-forest T-learner. The first separated subgroup treatment-effect signals and a between-group treatment-assignment-rate contrast from a baseline combining conventional statistics with aggregate causal-effect monitoring. The second compared these monitoring variants with selected fixed review calendars. Candidate estimators and held-out AIPW update-acceptance gates were common across arms. Accepted updates affected the following window.

The main ablation produced exactly zero observed paired regret differences between the additional-signal variants and the baseline. In the fresh calendar comparison, additional subgroup signals again provided no improvement and occasionally increased loss. Alert-triggered baseline reviews produced lower mean loss than the selected calendars under treatment-response and opposing subgroup-effect changes, while stable conditions favored calendar reviews. These comparisons depended on review timing and did not establish universal controller superiority.

The findings show that monitoring differences and decision benefits must be evaluated separately. Conclusions remain conditional on the generator, initial model, calibration, update gate, fixed shift onset and chosen calendars. Novelty remains provisional.

Keywords: causal machine learning; MLOps; distribution shift; treatment-policy regret; model monitoring; review budgets.

## 1. Introduction

A machine-learning model used to support treatment or product decisions may encounter changes in customer characteristics, treatment assignment or treatment response. In a discount-allocation setting, these changes raise distinct questions. A change in the customer population may affect the distribution of predictions, whereas a change in treatment response may alter whether offering the discount is beneficial. Monitoring these quantities can inform model review, but detecting a change does not itself determine whether a replacement model should be deployed.

This distinction motivates the present evaluation. A monitoring signal affects decisions through a sequence of operational steps: an alert initiates a review, a candidate model is trained, an acceptance rule compares candidate and incumbent policies, and an accepted update changes subsequent decisions. Additional monitoring information may have little incremental value if an existing monitor already triggers a timely review or if the available candidate does not pass the update gate. Conversely, an early alert may consume limited review opportunities before a later change.

Our project implements a synthetic causal-ML monitoring benchmark in which a T-learner estimates heterogeneous treatment effects and recommends treatment when the estimated effect exceeds an assumed cost. The benchmark separates logged treatment assignment from policy recommendations and reserves known synthetic effects for offline evaluation. This permits calculation of oracle-relative treatment-policy opportunity loss while keeping synthetic truth outside the monitoring and adaptation rules.

Existing research already addresses treatment decisions in dynamic environments, causal estimation on streams, monitoring-triggered adaptation and resource-constrained interventions. For example, Berrevoets et al. (2022) evaluated treatment-effect optimisation under changing conditions. OnlineCML's inspected public examples demonstrate causal pseudo-outcome monitoring and estimator reset. These precedents rule out a broad claim that combining causal estimation, drift monitoring and regret evaluation is itself new. The narrower question is whether a controlled comparison can clarify the incremental value of monitoring signals and review timing under common adaptation procedures.

We examine two supporting research questions. First, does adding subgroup treatment-effect monitoring, a between-group assignment-rate contrast, or both reduce cumulative treatment-policy regret beyond a baseline that already includes conventional statistics and aggregate causal-effect monitoring? Second, how does alert-triggered review timing compare with prospectively specified fixed calendars when candidate estimation, update acceptance and maximum review caps are shared?

The first experiment compared four monitoring variants. M1 combined conventional statistics with an aggregate AIPW treatment-effect statistic. M2-A added subgroup treatment-effect statistics, M2-B added a between-group assignment-rate contrast, and M2-FULL added both. The second experiment retained these variants and introduced fixed-calendar reviews. Each experiment evaluated five scenarios and three review caps using 100 paired seeds per scenario.

The principal measured outcome was cumulative period-average oracle-relative net-benefit regret over the latter six windows. Alerts, reviews, accepted updates, harmful-treatment rates and detection timing provided complementary operational evidence. Alert thresholds targeted a common stable-stream any-alert probability, with independent held-out assessment. Equal intended calibration targets were distinguished from equal achieved false-alert rates, and common review caps were distinguished from equal realized workload.

The completed results did not show an incremental regret benefit from the additional monitoring signals. The main ablation yielded identical observed regret across variants, while the fresh calendar comparison included occasional adverse subgroup-monitoring outcomes. Alert-triggered M1 reviews reduced loss relative to the selected calendars under treatment-effect changes, but calendar reviews performed better in stable settings. A separate small review-spacing development check also demonstrated that delaying reviews could postpone a useful update. These findings are retained together rather than selecting only favorable comparisons.

The intended contribution is a reproducible, controlled empirical evaluation of how monitoring information and review opportunities translate into downstream policy performance. It is not a new treatment-effect estimator or drift detector. The experiments do not isolate the overall benefit of causal information over a purely conventional monitor because M1 already contains aggregate causal information. They also do not establish an explanation-stability benefit; explanation quantities remain offline diagnostics in these extensions.

The contribution and its limits require further assessment against the closest literature. In particular, the complete CausalStream and OnlineCML manuscripts were unavailable during the audit, and full overlap remains unresolved. The study is therefore presented as exploratory evidence with a provisional research-gap assessment, subject to supervisor review and final manuscript scope alignment.

## Citation completion note

The final manuscript must replace provisional author references with source-verified citations and a complete bibliography. Claims about unavailable manuscripts must remain restricted to the abstracts, previews and software materials actually inspected. No first-of-its-kind or guaranteed-publication claim is made.