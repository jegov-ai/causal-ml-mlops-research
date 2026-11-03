# Project 1: focused novelty-audit addendum

Date: 1 November 2026. Status: evidence-based, provisional novelty assessment; not a preregistration or approval to expand experiments.

## Decision

The broad idea of combining causal treatment decisions, changing environments, monitoring/adaptation and decision-regret evaluation is already represented in published research. Project 1 should not claim to introduce these ingredients or their broad combination.

A narrower candidate contribution remains: an empirical attribution study asking whether adding causal monitoring signals changes cumulative treatment-policy opportunity loss when estimators, independently calibrated run-level false-alert targets, response controllers and review-budget caps are held common. The accessible sources inspected here do not establish that exact joint comparison. This is a bounded evidence finding, not proof that nobody has done it. Novelty risk remains unresolved, particularly for the two inaccessible manuscripts.

## Continuity and evidence standard

This addendum extends, rather than replaces, the existing 100-record corpus, nine-paper closest-literature audit, EVALUATION_PLAN_v3_ALIGNED.md and prospective extension protocol draft. The corpus is not represented as 100 full-text reviews. Seven previously selected papers received selective full-text inspection. CausalStream and OnlineCML still have NOT received full-manuscript review.

No existing code, decisions, outputs, seeds or negative results were changed. No new Project 1 experiments were launched. Existing equal or worse regret for richer monitors remains evidence against unconditional superiority. Earlier detection alone is not a policy-benefit result.

Deep Research was not exposed as an available tool in this session. This investigation used direct scholarly pages, accessible manuscripts, author documentation and repository source. Repository inspection was static; software demonstrations were not executed or independently reproduced.

## 1. CausalStream: access remains unresolved

El quammah et al., CausalStream: A General Architecture for Real-Time Causal Inference on Data Streams, Concurrency and Computation: Practice and Experience (2026), DOI 10.1002/cpe.70756.

Verified access: publisher abstract/metadata and a publisher-supplied first-page preview hosted on ResearchGate. The preview is page 1 of 17, not the full paper. The accessible description supports overlap in streaming causal inference and incremental doubly robust estimation.

Routes checked: publisher full-text, PDF and ePDF links; supplementary route; author/ORCID leads; ResearchGate; exact-title and DOI searches with preprint, manuscript, arXiv, Zenodo, OSF and GitHub terms. No accessible complete manuscript or supplement was located through these routes. An unsuccessful search is not evidence of nonexistence.

Unresolved: its complete monitoring signals, adaptation controllers, false-alert calibration, review budgets, regret endpoints and experimental comparisons. Do not label these absent. Its full experimental overlap remains a material novelty risk.

Sources: https://onlinelibrary.wiley.com/doi/abs/10.1002/cpe.70756 ; https://www.researchgate.net/publication/404992667_CausalStream_A_General_Architecture_for_Real-Time_Causal_Inference_on_Data_Streams

## 2. OnlineCML: more overlap verified through public software

Ahmed Tarek Hammad, OnlineCML: A Python Library for Online Causal Machine Learning (2026), SSRN abstract 6598878. Treat as a preprint; peer-reviewed publication status was not established.

The complete manuscript remained inaccessible: SSRN abstract/delivery routes failed; the author publication page led back to SSRN; ResearchGate offered no manuscript file. This does not establish that a manuscript cannot be obtained elsewhere.

Important additional evidence comes from the author's public documentation and repository:

- Example 08 implements ADWIN monitoring of causal pseudo-outcomes and reset-on-drift estimation, compared with static and forgetting-factor estimation. Its illustrative ATE changes from 3 to -1 at observation 1,000 in a 2,000-observation stream.
- Example 05 already demonstrates cumulative regret for epsilon-greedy, Thompson sampling and UCB in a stationary two-arm reward example. It also illustrates policy integration with causal estimation.
- Selected clinical and marketing examples include causal estimation, subgroup/uplift or diagnostic components. These are additional overlap, not evidence that every component was evaluated together.

The inspected examples did not establish a single experiment jointly comparing conventional versus causal monitors under the same estimator, independently matched false-alert calibration, common response gate and fixed review caps, with cumulative post-change treatment-policy loss as the endpoint. This statement is limited to inspected examples, not the inaccessible manuscript or entire ecosystem.

Reproducibility anchor: repository https://github.com/athammad/onlinecml , commit 0b5644eb076ef13da52898ad0b22a08db5ef4335 (23 April 2026). Selected notebook source inspected: examples 05, 06, 08, 09, 10 and 11; example 12 received keyword inventory only. No PDF/TEX/BIB manuscript was found in the checked working tree; all historical commits were not exhaustively searched.

Sources: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6598878 ; https://athsas.com/papers.html ; https://athammad.github.io/onlinecml/examples/08_concept_drift/ ; https://athammad.github.io/onlinecml/examples/05_policy_exploration/

## 3. Newly identified close published comparator

Berrevoets, Verboven and Verbeke (2022), Treatment effect optimisation in dynamic environments, Journal of Causal Inference 10:106–122. DOI 10.1515/jci-2020-0009. Accessible full manuscript; targeted inspection of Sections 4–6, especially 5.3.

This study evaluates uplifted contextual bandits against standard contextual bandits and uplift random forests under static, sudden and gradual change. Its random-forest baseline uses ADWIN to trigger data recollection and retraining. Decision performance is compared with oracle treatment choices across ten randomly generated environments.

Its Equation 9 calls the probability of disagreement with the oracle action regret. Project 1 instead accumulates the magnitude of foregone net treatment benefit. The estimands differ: a small and a large harmful mistake count equally in disagreement probability but differently in opportunity loss.

The published comparison changes learning/collection strategies across methods. The inspected design does not establish the Project 1 joint isolation of monitoring signals under a common estimator/controller and independently matched false-alert target plus review caps. This is a potential distinction, not evidence of a novel algorithm. Its findings also warn that detection speed alone may not overcome data-collection and adaptation delays.

Primary manuscript: https://www.degruyterbrill.com/document/doi/10.1515/jci-2020-0009/pdf ; author code link: https://github.com/vub-dl/u-cmab

## 4. Budgeted causal intervention is also established

Shoush and Dumas, Prescriptive Process Monitoring Under Resource Constraints: A Causal Inference Approach (online March 2022; ICPM 2021 workshops), DOI 10.1007/978-3-030-98581-3_14, uses predictive risk and causal intervention effects to allocate scarce intervention resources and compares net gain with a predictive baseline. Therefore, causal monitoring/action under resource limits is not a new general idea.

Its intervention capacity is conceptually different from Project 1's model-review budget. Later related work addresses intervention timing, uncertainty and resource allocation. These provide relevant neighboring literature, rather than proof of the exact distribution-shift benchmark.

Primary sources: https://link.springer.com/chapter/10.1007/978-3-030-98581-3_14 ; https://arxiv.org/pdf/2206.07745 ; https://arxiv.org/pdf/2307.06564

## Exact-design evidence matrix

“Not established” means not demonstrated by inspected evidence; it must not be read as “absent from the literature.”

| Design element | Existing evidence | Assessment for Project 1 |
| --- | --- | --- |
| Streaming causal effect estimation | CausalStream description; OnlineCML software | Established ingredient |
| Causal drift detector with estimator reset | OnlineCML example 08 | Established capability |
| Causal treatment selection under drift with oracle decision evaluation | Berrevoets et al. Section 5.3 | Published; broad novelty claim ruled out |
| Drift-triggered causal-model retraining | Berrevoets et al. ADWIN baseline; OnlineCML reset example | Established capability |
| Cumulative regret demonstration | OnlineCML example 05; wider bandit literature | Established endpoint family; definitions must be distinguished |
| Causal interventions under resource constraints | Shoush and Dumas | Published; intervention capacity differs from review capacity |
| Conventional/ATE/subgroup signals compared with one fixed estimator and response gate | Exact joint comparison not established here | Candidate evaluation contribution |
| Independent run-level null calibration plus common review caps and downstream opportunity loss | Exact joint comparison not established here | Candidate controlled comparison; unresolved manuscript risk |
| Opposing subgroup changes with population-stable ATE as one diagnostic case | Not established as unique by this audit | Useful test case; do not claim scenario invention |
| Explainability improves policy decisions | Existing Project 1 results do not establish this | Unsupported; retain null/negative findings |

## What Project 1 actually isolates—and its limitations

The implemented study uses a T-learner, common candidate-update/gating logic, controlled covariate/assignment/response shifts, and budget caps of 2, 4 and 8 reviews. Regret sums period-average oracle-relative net-treatment opportunity loss; it is not total monetary profit. Logged treatment assignment is exogenous, labels are immediate, and current-period evidence changes the next period's policy. It is not a full interactive deployment-feedback evaluation.

M2 adds both subgroup causal estimates AND an assignment-rate contrast. Any improvement cannot presently be attributed solely to subgroup causal monitoring. The preserved extension draft's subgroup-only/assignment-only ablations address this confounding. They are attribution checks, not automatically a novel method.

Identical caps do not imply identical realized reviews or equal compute. Report realized reviews, accepted changes and timing. The response gate uses repeated pointwise intervals, without an established sequential-safety guarantee. Initial alert timing can determine review timing and exhaust capacity before later change. These are candidate explanations to test, not post-hoc proof of mechanism.

## Defensible contribution wording

“We evaluate whether adding causal effect monitoring signals improves cumulative treatment-policy performance over conventional monitoring in controlled distribution-shift experiments. To separate monitoring from adaptation differences, we hold estimators and response controllers common, independently calibrate false-alert targets, and vary prespecified review-budget caps. We report beneficial, null and harmful effects, including cases where earlier detection does not improve decisions.”

Label this a proposed empirical evaluation contribution. Do not use “first,” “unique,” “100% novel,” or claim that prior methods lack regret, adaptation or resource constraints. Do not claim the inaccessible papers have no overlap.

## Immediate next steps before expansion

1. Seek the two complete manuscripts through institutional library access or author copies. No author messages were sent. Record version/date and inspect methods, experiments and supplements against the matrix.
2. Use the 2022 dynamic-treatment study and OnlineCML examples as explicit comparators in the supervisor-facing gap discussion. Ask whether a controlled monitoring-attribution benchmark is a sufficient contribution for the intended venue or degree.
3. Retain the existing negative results as motivating evidence: richer signals need not deliver better actions under the same response constraints. Freeze a primary scenario, budget, contrast and effect-size interpretation before new inferential experiments; the existing extension draft remains a draft.
4. If manuscripts remain unavailable, publish the access limitation and qualify the novelty claim. Do not replace missing evidence with assumptions. A useful reproducible negative-result benchmark may still be defensible, but its originality and scope need supervisor assessment.

Bottom-line status: broad novelty is contradicted by accessible prior work; the exact controlled attribution comparison remains a plausible but unverified gap. Full-text uncertainty for CausalStream and OnlineCML remains open.
