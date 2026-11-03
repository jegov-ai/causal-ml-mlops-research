# Paper 1 supporting results tables

Prepared 3 November 2026. These tables transcribe completed saved outputs; no experiment was rerun. Full-precision source files remain authoritative. Tables round to six decimal places. Pointwise bootstrap intervals are exploratory and unadjusted for multiplicity. NA indicates an unavailable or inapplicable quantity; stable-run detection and PERIODIC detection are not meaningful.

## Ablation: all 60 method/scenario/cap summaries

Harmful-treatment rate is the fraction of all customers receiving treatment despite negative true net benefit; it is not conditional on receiving treatment.

| scenario | review_budget | method | seeds | mean_postchange_regret | mean_prechange_regret | mean_reviews | mean_alerts | mean_accepted_updates | mean_harmful_treatment_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assignment | 2 | M1 | 100 | 5.747150 | 5.722500 | 2.000000 | 2.000000 | 0.020000 | 0.000000 |
| assignment | 2 | M2-A | 100 | 5.747150 | 5.722500 | 2.000000 | 2.000000 | 0.020000 | 0.000000 |
| assignment | 2 | M2-B | 100 | 5.747150 | 5.722500 | 2.000000 | 2.000000 | 0.020000 | 0.000000 |
| assignment | 2 | M2-FULL | 100 | 5.747150 | 5.722500 | 2.000000 | 2.000000 | 0.020000 | 0.000000 |
| assignment | 4 | M1 | 100 | 5.735300 | 5.722500 | 4.000000 | 2.000000 | 0.060000 | 0.000000 |
| assignment | 4 | M2-A | 100 | 5.735300 | 5.722500 | 4.000000 | 2.000000 | 0.060000 | 0.000000 |
| assignment | 4 | M2-B | 100 | 5.735300 | 5.722500 | 4.000000 | 2.000000 | 0.060000 | 0.000000 |
| assignment | 4 | M2-FULL | 100 | 5.735300 | 5.722500 | 4.000000 | 2.000000 | 0.060000 | 0.000000 |
| assignment | 8 | M1 | 100 | 5.735300 | 5.722500 | 6.020000 | 2.000000 | 0.080000 | 0.000000 |
| assignment | 8 | M2-A | 100 | 5.735300 | 5.722500 | 6.020000 | 2.000000 | 0.080000 | 0.000000 |
| assignment | 8 | M2-B | 100 | 5.735300 | 5.722500 | 6.040000 | 2.000000 | 0.080000 | 0.000000 |
| assignment | 8 | M2-FULL | 100 | 5.735300 | 5.722500 | 6.040000 | 2.000000 | 0.080000 | 0.000000 |
| covariate | 2 | M1 | 100 | 3.130400 | 5.722500 | 2.000000 | 2.000000 | 0.060000 | 0.000000 |
| covariate | 2 | M2-A | 100 | 3.130400 | 5.722500 | 2.000000 | 2.000000 | 0.060000 | 0.000000 |
| covariate | 2 | M2-B | 100 | 3.130400 | 5.722500 | 2.000000 | 2.000000 | 0.060000 | 0.000000 |
| covariate | 2 | M2-FULL | 100 | 3.130400 | 5.722500 | 2.000000 | 2.000000 | 0.060000 | 0.000000 |
| covariate | 4 | M1 | 100 | 3.110850 | 5.722500 | 4.000000 | 2.000000 | 0.140000 | 0.000000 |
| covariate | 4 | M2-A | 100 | 3.110850 | 5.722500 | 4.000000 | 2.000000 | 0.140000 | 0.000000 |
| covariate | 4 | M2-B | 100 | 3.110850 | 5.722500 | 4.000000 | 2.000000 | 0.140000 | 0.000000 |
| covariate | 4 | M2-FULL | 100 | 3.110850 | 5.722500 | 4.000000 | 2.000000 | 0.140000 | 0.000000 |
| covariate | 8 | M1 | 100 | 3.109250 | 5.722500 | 6.040000 | 2.000000 | 0.190000 | 0.000000 |
| covariate | 8 | M2-A | 100 | 3.109250 | 5.722500 | 6.040000 | 2.000000 | 0.190000 | 0.000000 |
| covariate | 8 | M2-B | 100 | 3.109250 | 5.722500 | 6.040000 | 2.000000 | 0.190000 | 0.000000 |
| covariate | 8 | M2-FULL | 100 | 3.109250 | 5.722500 | 6.040000 | 2.000000 | 0.190000 | 0.000000 |
| opposing | 2 | M1 | 100 | 12.904090 | 5.722500 | 2.000000 | 2.000000 | 0.980000 | 0.179177 |
| opposing | 2 | M2-A | 100 | 12.904090 | 5.722500 | 2.000000 | 2.000000 | 0.980000 | 0.179177 |
| opposing | 2 | M2-B | 100 | 12.904090 | 5.722500 | 2.000000 | 2.000000 | 0.980000 | 0.179177 |
| opposing | 2 | M2-FULL | 100 | 12.904090 | 5.722500 | 2.000000 | 2.000000 | 0.980000 | 0.179177 |
| opposing | 4 | M1 | 100 | 12.256387 | 5.722500 | 4.000000 | 2.000000 | 1.080000 | 0.174183 |
| opposing | 4 | M2-A | 100 | 12.256387 | 5.722500 | 4.000000 | 2.000000 | 1.080000 | 0.174183 |
| opposing | 4 | M2-B | 100 | 12.256387 | 5.722500 | 4.000000 | 2.000000 | 1.080000 | 0.174183 |
| opposing | 4 | M2-FULL | 100 | 12.256387 | 5.722500 | 4.000000 | 2.000000 | 1.080000 | 0.174183 |
| opposing | 8 | M1 | 100 | 11.789998 | 5.722500 | 6.040000 | 2.000000 | 1.120000 | 0.171548 |
| opposing | 8 | M2-A | 100 | 11.789998 | 5.722500 | 6.040000 | 2.000000 | 1.120000 | 0.171548 |
| opposing | 8 | M2-B | 100 | 11.789998 | 5.722500 | 6.040000 | 2.000000 | 1.120000 | 0.171548 |
| opposing | 8 | M2-FULL | 100 | 11.789998 | 5.722500 | 6.040000 | 2.000000 | 1.120000 | 0.171548 |
| response | 2 | M1 | 100 | 15.784550 | 5.722500 | 2.000000 | 2.000000 | 0.090000 | 0.336922 |
| response | 2 | M2-A | 100 | 15.784550 | 5.722500 | 2.000000 | 2.000000 | 0.090000 | 0.336922 |
| response | 2 | M2-B | 100 | 15.784550 | 5.722500 | 2.000000 | 2.000000 | 0.090000 | 0.336922 |
| response | 2 | M2-FULL | 100 | 15.784550 | 5.722500 | 2.000000 | 2.000000 | 0.090000 | 0.336922 |
| response | 4 | M1 | 100 | 15.573800 | 5.722500 | 4.000000 | 2.000000 | 0.170000 | 0.329693 |
| response | 4 | M2-A | 100 | 15.573800 | 5.722500 | 4.000000 | 2.000000 | 0.170000 | 0.329693 |
| response | 4 | M2-B | 100 | 15.573800 | 5.722500 | 4.000000 | 2.000000 | 0.170000 | 0.329693 |
| response | 4 | M2-FULL | 100 | 15.573800 | 5.722500 | 4.000000 | 2.000000 | 0.170000 | 0.329693 |
| response | 8 | M1 | 100 | 15.526250 | 5.722500 | 6.040000 | 2.000000 | 0.260000 | 0.327805 |
| response | 8 | M2-A | 100 | 15.526250 | 5.722500 | 6.040000 | 2.000000 | 0.260000 | 0.327805 |
| response | 8 | M2-B | 100 | 15.526250 | 5.722500 | 6.040000 | 2.000000 | 0.260000 | 0.327805 |
| response | 8 | M2-FULL | 100 | 15.526250 | 5.722500 | 6.040000 | 2.000000 | 0.260000 | 0.327805 |
| stable | 2 | M1 | 100 | 5.746850 | 5.722500 | 0.060000 | 0.030000 | 0.000000 | 0.000000 |
| stable | 2 | M2-A | 100 | 5.746850 | 5.722500 | 0.060000 | 0.030000 | 0.000000 | 0.000000 |
| stable | 2 | M2-B | 100 | 5.746850 | 5.722500 | 0.060000 | 0.030000 | 0.000000 | 0.000000 |
| stable | 2 | M2-FULL | 100 | 5.746850 | 5.722500 | 0.060000 | 0.030000 | 0.000000 | 0.000000 |
| stable | 4 | M1 | 100 | 5.746850 | 5.722500 | 0.110000 | 0.030000 | 0.000000 | 0.000000 |
| stable | 4 | M2-A | 100 | 5.746850 | 5.722500 | 0.110000 | 0.030000 | 0.000000 | 0.000000 |
| stable | 4 | M2-B | 100 | 5.746850 | 5.722500 | 0.110000 | 0.030000 | 0.000000 | 0.000000 |
| stable | 4 | M2-FULL | 100 | 5.746850 | 5.722500 | 0.110000 | 0.030000 | 0.000000 | 0.000000 |
| stable | 8 | M1 | 100 | 5.746850 | 5.722500 | 0.190000 | 0.030000 | 0.000000 | 0.000000 |
| stable | 8 | M2-A | 100 | 5.746850 | 5.722500 | 0.190000 | 0.030000 | 0.000000 | 0.000000 |
| stable | 8 | M2-B | 100 | 5.746850 | 5.722500 | 0.190000 | 0.030000 | 0.000000 | 0.000000 |
| stable | 8 | M2-FULL | 100 | 5.746850 | 5.722500 | 0.190000 | 0.030000 | 0.000000 | 0.000000 |

## Ablation: all 72 paired contrasts

Negative differences favor the first named arm. Zero observed differences and [0,0] intervals do not establish population equivalence.

| scenario | review_budget | comparison | seeds | mean_loss_difference | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- |
| covariate | 2 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 2 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 2 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 2 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 2 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 2 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 4 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 4 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 4 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 4 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 4 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 4 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 8 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 8 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 8 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 8 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 8 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 8 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 2 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 2 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 2 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 2 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 2 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 2 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 4 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 4 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 4 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 4 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 4 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 4 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 8 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 8 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 8 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 8 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 8 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 8 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 2 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 2 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 2 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 2 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 2 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 2 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 4 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 4 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 4 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 4 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 4 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 4 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 8 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 8 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 8 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 8 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 8 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 8 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 2 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 2 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 2 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 2 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 2 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 2 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 4 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 4 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 4 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 4 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 4 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 4 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 8 | M2-A minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 8 | M2-B minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 8 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 8 | M2-FULL minus M2-A | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 8 | M2-FULL minus M2-B | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 8 | descriptive interaction | 100 | 0.000000 | 0.000000 | 0.000000 |

## Ablation: shifted-stream detection

Each cell contains 100 seeds. Delay is conditional on recorded detection, measured in windows from onset 7; zero denotes window-end detection in the first changed window.

| scenario | review_budget | method | detected | mean_delay_detected |
| --- | --- | --- | --- | --- |
| assignment | 2 | M1 | 100.000000 | 0.020000 |
| assignment | 2 | M2-A | 100.000000 | 0.020000 |
| assignment | 2 | M2-B | 100.000000 | 0.000000 |
| assignment | 2 | M2-FULL | 100.000000 | 0.000000 |
| assignment | 4 | M1 | 100.000000 | 0.020000 |
| assignment | 4 | M2-A | 100.000000 | 0.020000 |
| assignment | 4 | M2-B | 100.000000 | 0.000000 |
| assignment | 4 | M2-FULL | 100.000000 | 0.000000 |
| assignment | 8 | M1 | 100.000000 | 0.020000 |
| assignment | 8 | M2-A | 100.000000 | 0.020000 |
| assignment | 8 | M2-B | 100.000000 | 0.000000 |
| assignment | 8 | M2-FULL | 100.000000 | 0.000000 |
| covariate | 2 | M1 | 100.000000 | 0.000000 |
| covariate | 2 | M2-A | 100.000000 | 0.000000 |
| covariate | 2 | M2-B | 100.000000 | 0.000000 |
| covariate | 2 | M2-FULL | 100.000000 | 0.000000 |
| covariate | 4 | M1 | 100.000000 | 0.000000 |
| covariate | 4 | M2-A | 100.000000 | 0.000000 |
| covariate | 4 | M2-B | 100.000000 | 0.000000 |
| covariate | 4 | M2-FULL | 100.000000 | 0.000000 |
| covariate | 8 | M1 | 100.000000 | 0.000000 |
| covariate | 8 | M2-A | 100.000000 | 0.000000 |
| covariate | 8 | M2-B | 100.000000 | 0.000000 |
| covariate | 8 | M2-FULL | 100.000000 | 0.000000 |
| opposing | 2 | M1 | 100.000000 | 0.000000 |
| opposing | 2 | M2-A | 100.000000 | 0.000000 |
| opposing | 2 | M2-B | 100.000000 | 0.000000 |
| opposing | 2 | M2-FULL | 100.000000 | 0.000000 |
| opposing | 4 | M1 | 100.000000 | 0.000000 |
| opposing | 4 | M2-A | 100.000000 | 0.000000 |
| opposing | 4 | M2-B | 100.000000 | 0.000000 |
| opposing | 4 | M2-FULL | 100.000000 | 0.000000 |
| opposing | 8 | M1 | 100.000000 | 0.000000 |
| opposing | 8 | M2-A | 100.000000 | 0.000000 |
| opposing | 8 | M2-B | 100.000000 | 0.000000 |
| opposing | 8 | M2-FULL | 100.000000 | 0.000000 |
| response | 2 | M1 | 100.000000 | 0.000000 |
| response | 2 | M2-A | 100.000000 | 0.000000 |
| response | 2 | M2-B | 100.000000 | 0.000000 |
| response | 2 | M2-FULL | 100.000000 | 0.000000 |
| response | 4 | M1 | 100.000000 | 0.000000 |
| response | 4 | M2-A | 100.000000 | 0.000000 |
| response | 4 | M2-B | 100.000000 | 0.000000 |
| response | 4 | M2-FULL | 100.000000 | 0.000000 |
| response | 8 | M1 | 100.000000 | 0.000000 |
| response | 8 | M2-A | 100.000000 | 0.000000 |
| response | 8 | M2-B | 100.000000 | 0.000000 |
| response | 8 | M2-FULL | 100.000000 | 0.000000 |

## Calendar comparison: all 75 method/scenario/cap summaries

Harmful-treatment rate is the fraction of all customers receiving treatment despite negative true net benefit; it is not conditional on receiving treatment.

| scenario | review_budget | method | seeds | mean_postchange_regret | mean_prechange_regret | mean_reviews | mean_alerts | mean_accepted_updates | mean_harmful_treatment_rate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| assignment | 2 | M1 | 100 | 5.681050 | 5.721600 | 2.000000 | 2.000000 | 0.050000 | 0.000000 |
| assignment | 2 | M2-A | 100 | 5.681050 | 5.721600 | 2.000000 | 2.000000 | 0.050000 | 0.000000 |
| assignment | 2 | M2-B | 100 | 5.681050 | 5.721600 | 2.000000 | 2.000000 | 0.050000 | 0.000000 |
| assignment | 2 | M2-FULL | 100 | 5.681050 | 5.721600 | 2.000000 | 2.000000 | 0.050000 | 0.000000 |
| assignment | 2 | PERIODIC | 100 | 5.682700 | 5.719600 | 2.000000 | 0.000000 | 0.030000 | 0.000000 |
| assignment | 4 | M1 | 100 | 5.669700 | 5.720800 | 4.000000 | 2.000000 | 0.080000 | 0.000000 |
| assignment | 4 | M2-A | 100 | 5.669700 | 5.720800 | 4.000000 | 2.000000 | 0.080000 | 0.000000 |
| assignment | 4 | M2-B | 100 | 5.669700 | 5.720800 | 4.000000 | 2.000000 | 0.080000 | 0.000000 |
| assignment | 4 | M2-FULL | 100 | 5.669700 | 5.720800 | 4.000000 | 2.000000 | 0.080000 | 0.000000 |
| assignment | 4 | PERIODIC | 100 | 5.657850 | 5.706600 | 4.000000 | 0.000000 | 0.070000 | 0.000000 |
| assignment | 8 | M1 | 100 | 5.655900 | 5.720800 | 6.000000 | 2.000000 | 0.130000 | 0.000000 |
| assignment | 8 | M2-A | 100 | 5.655900 | 5.720800 | 6.040000 | 2.000000 | 0.130000 | 0.000000 |
| assignment | 8 | M2-B | 100 | 5.655900 | 5.720800 | 6.020000 | 2.000000 | 0.130000 | 0.000000 |
| assignment | 8 | M2-FULL | 100 | 5.655900 | 5.720800 | 6.060000 | 2.000000 | 0.130000 | 0.000000 |
| assignment | 8 | PERIODIC | 100 | 5.621800 | 5.690950 | 8.000000 | 0.000000 | 0.140000 | 0.000000 |
| covariate | 2 | M1 | 100 | 3.085450 | 5.721600 | 2.000000 | 2.000000 | 0.080000 | 0.000000 |
| covariate | 2 | M2-A | 100 | 3.093300 | 5.721600 | 2.000000 | 2.000000 | 0.070000 | 0.000000 |
| covariate | 2 | M2-B | 100 | 3.085450 | 5.721600 | 2.000000 | 2.000000 | 0.080000 | 0.000000 |
| covariate | 2 | M2-FULL | 100 | 3.093300 | 5.721600 | 2.000000 | 2.000000 | 0.070000 | 0.000000 |
| covariate | 2 | PERIODIC | 100 | 3.084450 | 5.719600 | 2.000000 | 0.000000 | 0.050000 | 0.000000 |
| covariate | 4 | M1 | 100 | 3.052200 | 5.720800 | 4.000000 | 2.000000 | 0.190000 | 0.000000 |
| covariate | 4 | M2-A | 100 | 3.052200 | 5.720800 | 4.000000 | 2.000000 | 0.190000 | 0.000000 |
| covariate | 4 | M2-B | 100 | 3.052200 | 5.720800 | 4.000000 | 2.000000 | 0.190000 | 0.000000 |
| covariate | 4 | M2-FULL | 100 | 3.052200 | 5.720800 | 4.000000 | 2.000000 | 0.190000 | 0.000000 |
| covariate | 4 | PERIODIC | 100 | 3.050850 | 5.706600 | 4.000000 | 0.000000 | 0.150000 | 0.000000 |
| covariate | 8 | M1 | 100 | 3.050050 | 5.720800 | 6.020000 | 2.000000 | 0.270000 | 0.000000 |
| covariate | 8 | M2-A | 100 | 3.050050 | 5.720800 | 6.060000 | 2.000000 | 0.270000 | 0.000000 |
| covariate | 8 | M2-B | 100 | 3.050050 | 5.720800 | 6.020000 | 2.000000 | 0.270000 | 0.000000 |
| covariate | 8 | M2-FULL | 100 | 3.050050 | 5.720800 | 6.060000 | 2.000000 | 0.270000 | 0.000000 |
| covariate | 8 | PERIODIC | 100 | 3.055850 | 5.690950 | 8.000000 | 0.000000 | 0.250000 | 0.000000 |
| opposing | 2 | M1 | 100 | 11.504052 | 5.721600 | 2.000000 | 2.000000 | 1.010000 | 0.172670 |
| opposing | 2 | M2-A | 100 | 12.010685 | 5.721600 | 2.000000 | 2.000000 | 0.990000 | 0.176292 |
| opposing | 2 | M2-B | 100 | 11.504052 | 5.721600 | 2.000000 | 2.000000 | 1.010000 | 0.172670 |
| opposing | 2 | M2-FULL | 100 | 12.010685 | 5.721600 | 2.000000 | 2.000000 | 0.990000 | 0.176292 |
| opposing | 2 | PERIODIC | 100 | 19.119119 | 5.719600 | 2.000000 | 0.000000 | 0.870000 | 0.227223 |
| opposing | 4 | M1 | 100 | 11.345019 | 5.720800 | 4.000000 | 2.000000 | 1.060000 | 0.171837 |
| opposing | 4 | M2-A | 100 | 11.345019 | 5.720800 | 4.000000 | 2.000000 | 1.060000 | 0.171837 |
| opposing | 4 | M2-B | 100 | 11.345019 | 5.720800 | 4.000000 | 2.000000 | 1.060000 | 0.171837 |
| opposing | 4 | M2-FULL | 100 | 11.345019 | 5.720800 | 4.000000 | 2.000000 | 1.060000 | 0.171837 |
| opposing | 4 | PERIODIC | 100 | 24.649376 | 5.706600 | 4.000000 | 0.000000 | 1.060000 | 0.262622 |
| opposing | 8 | M1 | 100 | 11.047568 | 5.720800 | 6.020000 | 2.000000 | 1.120000 | 0.169470 |
| opposing | 8 | M2-A | 100 | 11.047568 | 5.720800 | 6.060000 | 2.000000 | 1.120000 | 0.169470 |
| opposing | 8 | M2-B | 100 | 11.047568 | 5.720800 | 6.020000 | 2.000000 | 1.120000 | 0.169470 |
| opposing | 8 | M2-FULL | 100 | 11.047568 | 5.720800 | 6.060000 | 2.000000 | 1.120000 | 0.169470 |
| opposing | 8 | PERIODIC | 100 | 11.881339 | 5.690950 | 8.000000 | 0.000000 | 1.140000 | 0.176883 |
| response | 2 | M1 | 100 | 15.489650 | 5.721600 | 2.000000 | 2.000000 | 0.170000 | 0.326575 |
| response | 2 | M2-A | 100 | 15.489650 | 5.721600 | 2.000000 | 2.000000 | 0.170000 | 0.326575 |
| response | 2 | M2-B | 100 | 15.489650 | 5.721600 | 2.000000 | 2.000000 | 0.170000 | 0.326575 |
| response | 2 | M2-FULL | 100 | 15.489650 | 5.721600 | 2.000000 | 2.000000 | 0.170000 | 0.326575 |
| response | 2 | PERIODIC | 100 | 16.082900 | 5.719600 | 2.000000 | 0.000000 | 0.060000 | 0.347008 |
| response | 4 | M1 | 100 | 15.258100 | 5.720800 | 4.000000 | 2.000000 | 0.260000 | 0.318952 |
| response | 4 | M2-A | 100 | 15.258100 | 5.720800 | 4.000000 | 2.000000 | 0.260000 | 0.318952 |
| response | 4 | M2-B | 100 | 15.258100 | 5.720800 | 4.000000 | 2.000000 | 0.260000 | 0.318952 |
| response | 4 | M2-FULL | 100 | 15.258100 | 5.720800 | 4.000000 | 2.000000 | 0.260000 | 0.318952 |
| response | 4 | PERIODIC | 100 | 16.093100 | 5.706600 | 4.000000 | 0.000000 | 0.120000 | 0.348417 |
| response | 8 | M1 | 100 | 15.193450 | 5.720800 | 6.020000 | 2.000000 | 0.360000 | 0.316240 |
| response | 8 | M2-A | 100 | 15.193450 | 5.720800 | 6.060000 | 2.000000 | 0.360000 | 0.316240 |
| response | 8 | M2-B | 100 | 15.193450 | 5.720800 | 6.020000 | 2.000000 | 0.360000 | 0.316240 |
| response | 8 | M2-FULL | 100 | 15.193450 | 5.720800 | 6.060000 | 2.000000 | 0.360000 | 0.316240 |
| response | 8 | PERIODIC | 100 | 15.371450 | 5.690950 | 8.000000 | 0.000000 | 0.310000 | 0.324458 |
| stable | 2 | M1 | 100 | 5.711900 | 5.721600 | 0.040000 | 0.020000 | 0.010000 | 0.000000 |
| stable | 2 | M2-A | 100 | 5.711900 | 5.721600 | 0.080000 | 0.050000 | 0.010000 | 0.000000 |
| stable | 2 | M2-B | 100 | 5.711900 | 5.721600 | 0.040000 | 0.020000 | 0.010000 | 0.000000 |
| stable | 2 | M2-FULL | 100 | 5.711900 | 5.721600 | 0.080000 | 0.050000 | 0.010000 | 0.000000 |
| stable | 2 | PERIODIC | 100 | 5.688600 | 5.719600 | 2.000000 | 0.000000 | 0.020000 | 0.000000 |
| stable | 4 | M1 | 100 | 5.712000 | 5.720800 | 0.080000 | 0.020000 | 0.020000 | 0.000000 |
| stable | 4 | M2-A | 100 | 5.712000 | 5.720800 | 0.160000 | 0.050000 | 0.020000 | 0.000000 |
| stable | 4 | M2-B | 100 | 5.712000 | 5.720800 | 0.080000 | 0.020000 | 0.020000 | 0.000000 |
| stable | 4 | M2-FULL | 100 | 5.712000 | 5.720800 | 0.160000 | 0.050000 | 0.020000 | 0.000000 |
| stable | 4 | PERIODIC | 100 | 5.650300 | 5.706600 | 4.000000 | 0.000000 | 0.090000 | 0.000000 |
| stable | 8 | M1 | 100 | 5.712000 | 5.720800 | 0.130000 | 0.020000 | 0.020000 | 0.000000 |
| stable | 8 | M2-A | 100 | 5.715600 | 5.720800 | 0.300000 | 0.050000 | 0.030000 | 0.000000 |
| stable | 8 | M2-B | 100 | 5.712000 | 5.720800 | 0.130000 | 0.020000 | 0.020000 | 0.000000 |
| stable | 8 | M2-FULL | 100 | 5.715600 | 5.720800 | 0.300000 | 0.050000 | 0.030000 | 0.000000 |
| stable | 8 | PERIODIC | 100 | 5.620700 | 5.690950 | 8.000000 | 0.000000 | 0.180000 | 0.000000 |

## Calendar comparison: all 75 paired contrasts

Negative differences favor the first named arm. Zero observed differences and [0,0] intervals do not establish population equivalence.

| scenario | review_budget | comparison | seeds | mean_difference | ci_low | ci_high |
| --- | --- | --- | --- | --- | --- | --- |
| stable | 2 | M1 minus PERIODIC | 100 | 0.023300 | 0.000000 | 0.057356 |
| stable | 2 | M2-A minus PERIODIC | 100 | 0.023300 | 0.000000 | 0.058450 |
| stable | 2 | M2-B minus PERIODIC | 100 | 0.023300 | 0.000000 | 0.058450 |
| stable | 2 | M2-FULL minus PERIODIC | 100 | 0.023300 | 0.000000 | 0.058450 |
| stable | 2 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| stable | 4 | M1 minus PERIODIC | 100 | 0.061700 | 0.002499 | 0.134601 |
| stable | 4 | M2-A minus PERIODIC | 100 | 0.061700 | 0.002645 | 0.134764 |
| stable | 4 | M2-B minus PERIODIC | 100 | 0.061700 | 0.002650 | 0.136151 |
| stable | 4 | M2-FULL minus PERIODIC | 100 | 0.061700 | 0.004049 | 0.137100 |
| stable | 4 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| stable | 8 | M1 minus PERIODIC | 100 | 0.091300 | 0.023447 | 0.171054 |
| stable | 8 | M2-A minus PERIODIC | 100 | 0.094900 | 0.028050 | 0.170777 |
| stable | 8 | M2-B minus PERIODIC | 100 | 0.091300 | 0.024649 | 0.169964 |
| stable | 8 | M2-FULL minus PERIODIC | 100 | 0.094900 | 0.024547 | 0.173459 |
| stable | 8 | M2-FULL minus M1 | 100 | 0.003600 | 0.000000 | 0.010800 |
| covariate | 2 | M1 minus PERIODIC | 100 | 0.001000 | -0.015350 | 0.014350 |
| covariate | 2 | M2-A minus PERIODIC | 100 | 0.008850 | -0.010205 | 0.030901 |
| covariate | 2 | M2-B minus PERIODIC | 100 | 0.001000 | -0.014100 | 0.014200 |
| covariate | 2 | M2-FULL minus PERIODIC | 100 | 0.008850 | -0.010700 | 0.031552 |
| covariate | 2 | M2-FULL minus M1 | 100 | 0.007850 | 0.000000 | 0.023550 |
| covariate | 4 | M1 minus PERIODIC | 100 | 0.001350 | -0.029151 | 0.032551 |
| covariate | 4 | M2-A minus PERIODIC | 100 | 0.001350 | -0.030703 | 0.032151 |
| covariate | 4 | M2-B minus PERIODIC | 100 | 0.001350 | -0.030000 | 0.032501 |
| covariate | 4 | M2-FULL minus PERIODIC | 100 | 0.001350 | -0.029850 | 0.032600 |
| covariate | 4 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| covariate | 8 | M1 minus PERIODIC | 100 | -0.005800 | -0.036952 | 0.024755 |
| covariate | 8 | M2-A minus PERIODIC | 100 | -0.005800 | -0.036751 | 0.025002 |
| covariate | 8 | M2-B minus PERIODIC | 100 | -0.005800 | -0.037250 | 0.024251 |
| covariate | 8 | M2-FULL minus PERIODIC | 100 | -0.005800 | -0.037151 | 0.024751 |
| covariate | 8 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 2 | M1 minus PERIODIC | 100 | -0.001650 | -0.033601 | 0.024400 |
| assignment | 2 | M2-A minus PERIODIC | 100 | -0.001650 | -0.034959 | 0.023450 |
| assignment | 2 | M2-B minus PERIODIC | 100 | -0.001650 | -0.033300 | 0.023050 |
| assignment | 2 | M2-FULL minus PERIODIC | 100 | -0.001650 | -0.032650 | 0.023050 |
| assignment | 2 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 4 | M1 minus PERIODIC | 100 | 0.011850 | -0.052651 | 0.083010 |
| assignment | 4 | M2-A minus PERIODIC | 100 | 0.011850 | -0.053555 | 0.079301 |
| assignment | 4 | M2-B minus PERIODIC | 100 | 0.011850 | -0.050551 | 0.081960 |
| assignment | 4 | M2-FULL minus PERIODIC | 100 | 0.011850 | -0.052011 | 0.080351 |
| assignment | 4 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| assignment | 8 | M1 minus PERIODIC | 100 | 0.034100 | -0.032100 | 0.106451 |
| assignment | 8 | M2-A minus PERIODIC | 100 | 0.034100 | -0.036505 | 0.107801 |
| assignment | 8 | M2-B minus PERIODIC | 100 | 0.034100 | -0.033351 | 0.110754 |
| assignment | 8 | M2-FULL minus PERIODIC | 100 | 0.034100 | -0.033750 | 0.105701 |
| assignment | 8 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 2 | M1 minus PERIODIC | 100 | -0.593250 | -0.970900 | -0.266716 |
| response | 2 | M2-A minus PERIODIC | 100 | -0.593250 | -0.965714 | -0.255600 |
| response | 2 | M2-B minus PERIODIC | 100 | -0.593250 | -0.985224 | -0.262345 |
| response | 2 | M2-FULL minus PERIODIC | 100 | -0.593250 | -0.986066 | -0.262860 |
| response | 2 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 4 | M1 minus PERIODIC | 100 | -0.835000 | -1.266564 | -0.444599 |
| response | 4 | M2-A minus PERIODIC | 100 | -0.835000 | -1.254557 | -0.448879 |
| response | 4 | M2-B minus PERIODIC | 100 | -0.835000 | -1.267322 | -0.457424 |
| response | 4 | M2-FULL minus PERIODIC | 100 | -0.835000 | -1.265724 | -0.443594 |
| response | 4 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| response | 8 | M1 minus PERIODIC | 100 | -0.178000 | -0.378659 | -0.011350 |
| response | 8 | M2-A minus PERIODIC | 100 | -0.178000 | -0.377154 | -0.008589 |
| response | 8 | M2-B minus PERIODIC | 100 | -0.178000 | -0.379754 | -0.008349 |
| response | 8 | M2-FULL minus PERIODIC | 100 | -0.178000 | -0.381175 | -0.003194 |
| response | 8 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 2 | M1 minus PERIODIC | 100 | -7.615068 | -9.355841 | -5.954485 |
| opposing | 2 | M2-A minus PERIODIC | 100 | -7.108434 | -8.882606 | -5.372553 |
| opposing | 2 | M2-B minus PERIODIC | 100 | -7.615068 | -9.298010 | -6.003771 |
| opposing | 2 | M2-FULL minus PERIODIC | 100 | -7.108434 | -8.905231 | -5.346106 |
| opposing | 2 | M2-FULL minus M1 | 100 | 0.506634 | 0.000000 | 1.288168 |
| opposing | 4 | M1 minus PERIODIC | 100 | -13.304356 | -14.865089 | -11.743961 |
| opposing | 4 | M2-A minus PERIODIC | 100 | -13.304356 | -14.893306 | -11.822178 |
| opposing | 4 | M2-B minus PERIODIC | 100 | -13.304356 | -14.925420 | -11.740074 |
| opposing | 4 | M2-FULL minus PERIODIC | 100 | -13.304356 | -14.855358 | -11.727266 |
| opposing | 4 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |
| opposing | 8 | M1 minus PERIODIC | 100 | -0.833771 | -1.306201 | -0.418000 |
| opposing | 8 | M2-A minus PERIODIC | 100 | -0.833771 | -1.315063 | -0.408058 |
| opposing | 8 | M2-B minus PERIODIC | 100 | -0.833771 | -1.313517 | -0.415968 |
| opposing | 8 | M2-FULL minus PERIODIC | 100 | -0.833771 | -1.336653 | -0.421857 |
| opposing | 8 | M2-FULL minus M1 | 100 | 0.000000 | 0.000000 | 0.000000 |

## Calendar comparison: shifted-stream detection

Each cell contains 100 seeds. Delay is conditional on recorded detection, measured in windows from onset 7; zero denotes window-end detection in the first changed window.

| scenario | review_budget | method | detected | mean_delay_detected |
| --- | --- | --- | --- | --- |
| assignment | 2 | M1 | 100.000000 | 0.020000 |
| assignment | 2 | M2-A | 100.000000 | 0.020000 |
| assignment | 2 | M2-B | 100.000000 | 0.000000 |
| assignment | 2 | M2-FULL | 100.000000 | 0.000000 |
| assignment | 4 | M1 | 100.000000 | 0.020000 |
| assignment | 4 | M2-A | 100.000000 | 0.020000 |
| assignment | 4 | M2-B | 100.000000 | 0.000000 |
| assignment | 4 | M2-FULL | 100.000000 | 0.000000 |
| assignment | 8 | M1 | 100.000000 | 0.020000 |
| assignment | 8 | M2-A | 100.000000 | 0.020000 |
| assignment | 8 | M2-B | 100.000000 | 0.000000 |
| assignment | 8 | M2-FULL | 100.000000 | 0.000000 |
| covariate | 2 | M1 | 100.000000 | 0.000000 |
| covariate | 2 | M2-A | 100.000000 | 0.000000 |
| covariate | 2 | M2-B | 100.000000 | 0.000000 |
| covariate | 2 | M2-FULL | 100.000000 | 0.000000 |
| covariate | 4 | M1 | 100.000000 | 0.000000 |
| covariate | 4 | M2-A | 100.000000 | 0.000000 |
| covariate | 4 | M2-B | 100.000000 | 0.000000 |
| covariate | 4 | M2-FULL | 100.000000 | 0.000000 |
| covariate | 8 | M1 | 100.000000 | 0.000000 |
| covariate | 8 | M2-A | 100.000000 | 0.000000 |
| covariate | 8 | M2-B | 100.000000 | 0.000000 |
| covariate | 8 | M2-FULL | 100.000000 | 0.000000 |
| opposing | 2 | M1 | 100.000000 | 0.000000 |
| opposing | 2 | M2-A | 100.000000 | 0.000000 |
| opposing | 2 | M2-B | 100.000000 | 0.000000 |
| opposing | 2 | M2-FULL | 100.000000 | 0.000000 |
| opposing | 4 | M1 | 100.000000 | 0.000000 |
| opposing | 4 | M2-A | 100.000000 | 0.000000 |
| opposing | 4 | M2-B | 100.000000 | 0.000000 |
| opposing | 4 | M2-FULL | 100.000000 | 0.000000 |
| opposing | 8 | M1 | 100.000000 | 0.000000 |
| opposing | 8 | M2-A | 100.000000 | 0.000000 |
| opposing | 8 | M2-B | 100.000000 | 0.000000 |
| opposing | 8 | M2-FULL | 100.000000 | 0.000000 |
| response | 2 | M1 | 100.000000 | 0.000000 |
| response | 2 | M2-A | 100.000000 | 0.000000 |
| response | 2 | M2-B | 100.000000 | 0.000000 |
| response | 2 | M2-FULL | 100.000000 | 0.000000 |
| response | 4 | M1 | 100.000000 | 0.000000 |
| response | 4 | M2-A | 100.000000 | 0.000000 |
| response | 4 | M2-B | 100.000000 | 0.000000 |
| response | 4 | M2-FULL | 100.000000 | 0.000000 |
| response | 8 | M1 | 100.000000 | 0.000000 |
| response | 8 | M2-A | 100.000000 | 0.000000 |
| response | 8 | M2-B | 100.000000 | 0.000000 |
| response | 8 | M2-FULL | 100.000000 | 0.000000 |

## Independent stable-run alert assessment

These 200 held-out streams per monitor were assessed once for the ablation calibration. The calendar comparison reused the thresholds, so this is not a second independent null assessment.

| method | sum | count | mean | wilson_low | wilson_high |
| --- | --- | --- | --- | --- | --- |
| M1 | 5 | 200 | 0.025000 | 0.010725 | 0.057179 |
| M2-A | 7 | 200 | 0.035000 | 0.017055 | 0.070471 |
| M2-B | 5 | 200 | 0.025000 | 0.010725 | 0.057179 |
| M2-FULL | 7 | 200 | 0.035000 | 0.017055 | 0.070471 |
