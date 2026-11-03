# Paper 1 method references and citation placement v1

Checked 3 November 2026 against the primary sources linked below. This supplements the draft bibliography; it is not a completed systematic review or novelty certification. Author/publisher metadata checks do not imply a complete full-text methodological audit.

## Method sources

1. Künzel, S. R., Sekhon, J. S., Bickel, P. J., & Yu, B. (2019). Metalearners for estimating heterogeneous treatment effects using machine learning. Proceedings of the National Academy of Sciences, 116(10), 4156–4165. https://doi.org/10.1073/pnas.1804597116
   Publisher full text: https://www.pnas.org/doi/10.1073/pnas.1804597116
   Placement: Section 3.2, introducing the T-learner. Cite this as established methodology, not a new estimator developed here.

2. Breiman, L. (2001). Random forests. Machine Learning, 45, 5–32. https://doi.org/10.1023/A:1010933404324
   Author manuscript: https://www.stat.berkeley.edu/users/breiman/randomforest2001.pdf
   Placement: Section 3.2, describing the random-forest outcome models. The author manuscript's pagination differs from the journal version. This reference does not specify this project's software defaults or establish their optimality.

3. Dudík, M., Langford, J., & Li, L. (2011). Doubly robust policy evaluation and learning. Proceedings of the 28th International Conference on Machine Learning.
   Official conference manuscript: https://icml.cc/2011/papers/554_icmlpaper.pdf
   Placement: Sections 3.2.1 and 3.4 for doubly robust evaluation background. The implemented binary-treatment pseudo-outcome and pointwise update gate must still be described explicitly. Do not attribute a sequential-safety guarantee for our gate to this paper. Page range omitted pending proceedings metadata verification.

## Completed related-work metadata

4. Shoush, M., & Dumas, M. (2022). Prescriptive process monitoring under resource constraints: A causal inference approach. In Process Mining Workshops (ICPM 2021), Lecture Notes in Business Information Processing, 433, 180–193. https://doi.org/10.1007/978-3-030-98581-3_14
   Publisher: https://link.springer.com/chapter/10.1007/978-3-030-98581-3_14
   This is intervention-resource allocation, not the same operational event as a model-review cap. Both concern resources; their distinction does not establish novelty alone.

## Remaining reference work

- Add primary citations for bootstrap reporting and the Wilson interval if these methods are retained in the final manuscript.
- Complete the closest-study comparison with other retraining-timing work; do not assume RCCDA exhausts that literature.
- Preserve CausalStream and OnlineCML as relevant but incompletely assessed sources. Full manuscripts remain unavailable in the existing audit; they cannot be omitted merely to remove overlap risk.
- Verify final metadata, access dates for software documentation and journal formatting before submission.
- These supporting files do not change any result, title approval status or scientific hypothesis.
