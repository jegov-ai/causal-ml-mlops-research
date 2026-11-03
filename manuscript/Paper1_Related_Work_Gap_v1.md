# Paper 1: Related Work and Research Gap — Draft v1

Status: Working manuscript section based on the existing focused literature audit. Novelty remains provisional. This section does not represent a new systematic review or full-text assessment of all 100 corpus records.

## 1. Causal decision making in changing environments

Existing research already investigates causal treatment decisions under changing conditions. Berrevoets, Verboven and Verbeke (2022) evaluated treatment-effect optimisation in dynamic environments using uplifted contextual bandits, conventional contextual bandits and uplift random forests. Their experiments included static, sudden-change and gradual-change settings. An ADWIN-based random-forest comparator triggered data recollection and retraining following detected change.

This work establishes that treatment decisions under drift, monitoring-triggered adaptation and oracle-based decision evaluation are not new general contributions of the present study.

An important distinction concerns the outcome definition. Berrevoets et al. defined regret using disagreement with an oracle treatment choice. Our evaluation measures the magnitude of foregone net treatment benefit. These quantities address related but different questions: action disagreement records whether a decision differs, whereas opportunity loss also accounts for the consequence of that difference.

The inspected prior comparison also varied learning and data-collection strategies. Our extensions instead compare monitoring additions and review timing while retaining common candidate estimators and update-acceptance rules. This is an experimental distinction, not evidence of a new causal estimator or proof of novelty.

## 2. Streaming causal estimation and adaptation

CausalStream describes an architecture for real-time causal inference on data streams, including incremental doubly robust estimation. Its accessible abstract and first-page preview establish relevant overlap with streaming causal estimation. However, its complete manuscript was unavailable during our audit. Its full monitoring design, adaptation rules and experimental comparisons therefore remain unresolved.

OnlineCML provides additional relevant evidence through public author documentation and software examples. An inspected example applies ADWIN to causal pseudo-outcomes and resets estimation following detected drift, comparing this approach with static and forgetting-factor alternatives. Another example demonstrates cumulative regret for exploration policies in a stationary two-arm setting.

These examples show that causal drift monitoring, estimator adaptation and regret demonstrations already exist. They must not be presented as capabilities introduced by our project.

The inspected examples did not establish the exact joint comparison used in our extensions: additional monitoring signals evaluated under common estimators, a common update gate, independently assessed run-level false-alert targets and finite review caps, with downstream treatment-policy opportunity loss as an outcome. This statement is restricted to the inspected evidence. The complete OnlineCML manuscript remained unavailable, so its full overlap cannot be excluded.

## 3. Resource-constrained causal intervention

Shoush and Dumas investigated prescriptive process monitoring under resource constraints using causal inference. Their work combines predictive information and estimated intervention effects to allocate scarce intervention resources.

Consequently, combining causal information with resource constraints is not a new general idea. Our review caps concern opportunities to evaluate and potentially update a model. They differ from limits on the number of interventions delivered to individual cases. This distinction clarifies the evaluation setting but does not independently establish originality.

## 4. Candidate gap and study positioning

The candidate gap concerns the incremental decision value of monitoring information when adaptation procedures are held common.

A richer monitoring signal can change an alert without changing a treatment decision. Its downstream value depends on whether a review occurs, whether the candidate policy passes the acceptance gate and whether sufficient future decision opportunities remain. Finite review caps can also make early alerts costly by consuming capacity before later changes.

Our study examines these relationships through two completed exploratory comparisons:

1. A signal ablation separating subgroup treatment-effect statistics from a between-group treatment-assignment-rate contrast.
2. A comparison of alert-triggered consecutive reviews with prospectively specified fixed review calendars.

The experiments share initial models, candidate-learning procedures, update gates and simulated streams within each comparison. Independently held-out stable streams assess the achieved alert rates of the monitoring rules. Common calibration targets are distinguished from exactly equal achieved false-alert rates, and equal review caps are distinguished from equal realized workload.

The potential contribution is therefore a controlled empirical evaluation of monitoring information and adaptation timing. Signal ablation, periodic review and causal monitoring are not individually claimed as inventions.

## 5. Research questions aligned with the completed extensions

RQ1: Under the specified synthetic shifts and common adaptation procedures, does adding subgroup treatment-effect monitoring, a between-group assignment-rate contrast, or both reduce cumulative treatment-policy regret beyond M1?

RQ2: Under the same candidate estimator, acceptance gate and maximum review caps, how does alert-triggered review timing compare with the selected fixed review calendars?

M1 includes conventional statistics and aggregate causal-effect monitoring. These questions concern additions to that baseline and the timing of reviews. They do not independently answer whether causal-aware monitoring outperforms a purely conventional M0 monitor.

Explanation diagnostics were recorded separately. The completed extensions do not establish that explanation monitoring improves policy decisions or explanation stability.

## 6. Interpretation of the completed evidence

The main signal ablation found no observed incremental regret reduction from the additional signals. The fresh schedule-comparison experiment also identified occasional adverse outcomes from richer monitoring.

Alert-triggered M1 reviews produced lower mean loss than the selected calendars in treatment-effect-shift scenarios. Other settings favored the calendar or showed small differences. The findings remain conditional on the chosen schedules, fixed shift onset, estimator, gate and simulation horizon.

A subsequent two-seed review-spacing check was engineering development rather than a main evaluation. It showed that preserving later review opportunities can also delay helpful adaptation. It is retained as supporting development evidence, without an inferential superiority claim.

These beneficial, null and adverse results define the reported findings. They do not justify changing scenarios or selecting seeds to obtain a favorable outcome.

## 7. Remaining novelty uncertainties

The existing corpus contains 100 records; it must not be described as 100 completed full-text reviews. Nine particularly relevant papers were previously selected, of which seven received selective full-text inspection. The complete CausalStream and OnlineCML manuscripts remained unavailable.

The exact controlled comparison remains a plausible evaluation contribution rather than a verified absence in prior research. Before submission, the literature assessment must also reconcile closely related work on resource-aware model updating and retraining timing, including RCCDA and other relevant recent studies.

No claim of being the first, uniquely novel or universally superior is supported. Supervisor assessment and a source-verified comparison with the closest studies remain necessary to judge whether the contribution is sufficient for the intended manuscript and venue.

## Working reference records

These records identify sources used in the existing audit. Complete bibliographic metadata and publication status must be verified before submission.

- Berrevoets, J., Verboven, S., and Verbeke, W. (2022). Treatment effect optimisation in dynamic environments. Journal of Causal Inference, 10, 106–122. https://doi.org/10.1515/jci-2020-0009

- El quammah et al. (2026). CausalStream: A General Architecture for Real-Time Causal Inference on Data Streams. Concurrency and Computation: Practice and Experience. https://doi.org/10.1002/cpe.70756
  Evidence inspected: abstract and first-page preview; complete manuscript unavailable.

- Hammad, A. T. (2026). OnlineCML: A Python Library for Online Causal Machine Learning. SSRN record 6598878. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6598878
  Evidence inspected: available descriptions, selected author documentation and repository examples; complete manuscript unavailable. Peer-reviewed publication status not established.

- OnlineCML author documentation:
  https://athammad.github.io/onlinecml/examples/08_concept_drift/
  https://athammad.github.io/onlinecml/examples/05_policy_exploration/
  Repository inspection anchor: commit 0b5644eb076ef13da52898ad0b22a08db5ef4335.

- Shoush and Dumas. Prescriptive Process Monitoring Under Resource Constraints: A Causal Inference Approach. https://doi.org/10.1007/978-3-030-98581-3_14