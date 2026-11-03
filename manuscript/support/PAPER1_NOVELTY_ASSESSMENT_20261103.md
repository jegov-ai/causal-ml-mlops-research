# Paper 1 targeted novelty assessment — 3 November 2026

## Verdict and scope decision

This assessment is complete as a bounded assessment of the evidence inspected through this checkpoint. Verdict: an incremental controlled empirical extension is plausible and suitable for a scoped review draft; a verified original research gap, sufficient publication-level novelty and a first-of-its-kind claim are NOT established. Continue writing on that basis, without treating another positive experiment as a substitute for prior-art distinction.

The strongest candidate contribution is the isolated incremental decision value of subgroup-effect and group assignment-contrast signals under a common estimator, frozen calibration procedure, common held-out update gate and finite review caps, reporting opportunity-loss magnitudes and mechanisms linking alerts to reviews and accepted updates. Its significance is an empirical boundary in a specified benchmark, not a universal claim that richer monitoring is unnecessary. This design difference alone may be insufficient for a journal; the assessment does not guarantee otherwise.

## Established overlap and exact boundary

| Source | Evidence inspected | Established overlap | Bounded distinction and risk |
| --- | --- | --- | --- |
| Berrevoets, Verboven & Verbeke (2022), doi:10.1515/jci-2020-0009 | Primary manuscript, targeted Section 5.3 and Equation 9 | Causal treatment decisions under drift; ADWIN-triggered recollection/retraining; oracle-action disagreement; detection can fail to improve decisions | Our common adaptation procedure and magnitude-weighted policy loss differ. Neither decision-centric evaluation nor sensitivity harms are new general findings. |
| Feng et al. (2024), PMLR 236:587–608 | Primary full text, targeted Sections 4.1–4.4 | Average/subgroup causal predictive-performance monitoring, causal data-source choices, control limits and detection properties | Their PPV/NPV/calibration targets differ from our AIPW treatment-effect means and downstream gated-update loss. The average-versus-subgroup comparison itself is established. Our study has no performative logging feedback. |
| Piaseczny et al. (2025), RCCDA, doi:10.52202/085713-5183 | Official proceedings; primary Sections 3–4/Algorithm 1 | Resource-aware model updates under drift, prediction loss and budget control | Our measured target is treatment-policy opportunity loss; review and accepted-update events are separate. Their general budget formulation is not claimed incapable of finite horizons. No implemented RCCDA comparison here. |
| Shoush & Dumas (2022), doi:10.1007/978-3-030-98581-3_14 | Publisher text and earlier targeted audit | Causal intervention decisions with constrained resources and net gain | Intervention capacity differs from model-review capacity; resource-constrained causal decisions are established. |
| OnlineCML (2026), SSRN 6598878 and author examples 05/08 | Selected author documentation/source; full manuscript unavailable | Pseudo-outcome drift monitoring/reset; separate policy/regret examples | Exact joint overlap not established from inspected materials; MUST NOT label absent from the manuscript. |
| CausalStream (2026), doi:10.1002/cpe.70756 | Abstract and first-page preview from existing audit | Streaming causal inference and incremental doubly robust estimation | Full monitor/controller/resource/regret comparison remains unknown. |
| Dasari (2026), arXiv:2608.19488 | ArXiv search/abstract-level record; direct abstract/HTML/repository access attempts failed in this session | Retraining-policy evaluation with drift, budgets and latency is already explicitly studied | Full design not reviewed. No exact experimental absence claim. Generic trigger-versus-calendar timing is not our novelty. |

## What the completed evidence contributes

1. The 100-seed ablation finds exactly zero observed incremental regret differences despite some signal/event differences. This is a conditional empirical result, not equivalence.
2. A fresh 100-seed calendar comparison documents favorable timing results alongside occasional adverse subgroup-monitoring cases. Calendar selection and fixed onset materially constrain interpretation.
3. Complete operational accounting distinguishes monitoring, issued alerts, actual reviews and accepted updates. This is a reporting/attribution feature, not an invented algorithm.
4. The two-seed spacing check remains engineering development and is not promoted to inferential support.

## Claim allowed

“We evaluate the incremental policy value of subgroup-effect and assignment-contrast monitoring under common estimation and adaptation procedures. In the evaluated synthetic benchmark, additional signals produced no main-ablation regret improvement and occasionally worse outcomes in a separate seed set; selected review schedules changed downstream policy loss.”

## Claims rejected

First causal monitoring method; first subgroup causal monitor; first resource-aware adaptation; first regret-under-drift study; first discovery that detection does not guarantee improvement; universal superiority; causal-versus-conventional benefit from the recent extensions; proven explanation benefit; new real-world profitability evidence; assured journal novelty or acceptance.

## Search and access record

This extends the existing 100-record corpus and targeted nine-paper audit, not a restarted systematic review. Searches in two available web engines covered subgroup/treatment-effect monitoring, drift, policy regret, causal monitoring with review budgets, calibration and retraining-policy comparisons. Exact-title and primary DOI/proceedings retrieval supplemented searches. No retrieval count or PRISMA completeness claim is made. Targeted inspection is not full review of every source.

Primary links: https://proceedings.mlr.press/v236/feng24a.html ; https://proceedings.mlr.press/v236/feng24a/feng24a.pdf ; https://www.degruyterbrill.com/document/doi/10.1515/jci-2020-0009/pdf ; https://proceedings.neurips.cc/paper_files/paper/2025/hash/e3d1b6d954a204267fd334cbaf9cd4af-Abstract-Conference.html ; https://link.springer.com/chapter/10.1007/978-3-030-98581-3_14 ; https://athammad.github.io/onlinecml/examples/08_concept_drift/ ; https://arxiv.org/abs/2608.19488

## Residual uncertainty is a conclusion, not unfinished labeling

The assessment cannot eliminate unknown overlap from inaccessible manuscripts or guarantee literature completeness. This does not justify hiding those papers or endlessly adding experiments. The current disposition is: retain the narrowly scoped exploratory evaluation, disclose overlap and uncertainty, and obtain critical review of its importance. Broader or confirmatory claims require separately specified evidence. No new heavy experiment is authorized or launched by this document itself.
