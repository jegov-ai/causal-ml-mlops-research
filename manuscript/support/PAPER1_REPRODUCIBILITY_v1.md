# Paper 1 reproducibility record v1

Prepared 3 November 2026 from the saved run manifests and previously inspected source. This is documentation of completed runs, not independent reproduction of all model fits. Do not rerun exposed seeds and count them as fresh evidence.

## Run identities

| Item | Signal ablation | Fixed-calendar comparison |
| --- | --- | --- |
| Run | run_20261102_012152 | run_20261102_054710 |
| Project output directory | paper1_experiments/monitoring_signal_ablation_v1_study | paper1_experiments/monitoring_schedule_comparison_v1_results |
| Source commit | 4fd595ac5dc65899c5a2273ac4c56fb7e92810fe | 94f8e62aab67204dc9e92414fc8ac90d444198f8 |
| Script SHA-256 | 47a5d523ea995b6a7697759f0217c3e7342513b4585de476f44e2adcaede000f | ebcf8962e8776f5c850e4d0cc20f7885513cdc1a2c5ba017e6f0a04a8dae768c |
| Recorded protocol SHA-256 | 6d800d0e4b35cb9668ad68f32fe21bdcfde780b3c46b78339dd6aae6ed6860b1 | 784e5a744ce1b2d9694602632abfac8ba8cbf1ec3d79eeb663a513935fbd8e97 |
| Evaluation seeds, inclusive | 340000–340099 | 350000–350099 |
| Runtime, seconds | 9754.178976 | 7145.938112 |

The ablation protocol snapshot uses different line endings from its frozen hash: the previously audited match requires normalization of CRLF to LF. Preserve originals; this is not a substantive protocol change. Shared candidate fits and explanation calculations are cached across arms, so joint runtime is not separate per-arm operational compute.

## Environment as recorded by the run manifests

Python 3.12.10, Windows 10 build 19045; NumPy 2.5.4, pandas 3.1.0 and scikit-learn 1.9.1. These are manifest-recorded versions, not a newly reconstructed environment. Exact source and version checks were used before the calendar comparison. No refreshed package installation was performed for this documentation.

## Fixed allocation

The initial 1,000-customer dataset used seed 42 and an 80/20 train/test split with random state 42. The 800-row initial training subset fitted the shared T-learner. Each arm-specific forest used 100 trees, min_samples_leaf=5, random_state=42 and n_jobs=1; remaining estimator settings followed the recorded scikit-learn version's defaults.

Stable scale seeds: 310000–310099 (100 streams); stable calibration: 320000–320999 (1,000 streams); independent held-out stable assessment: 330000–330199 (200 streams). Each has 12 windows of 1,000 observations. For each evaluation stream/window, random generation uses SeedSequence([seed, period]). Candidate splitting and fitting use seed+period. The same seed across scenarios provides pairing, not independent scenario replications.

All scenarios, caps 2/4/8 and methods were retained. Labels were immediate and logging exogenous. Current-window outcomes could change only next-window actions. Ground truth remained offline scoring information. One frozen initial model, one shift onset (window 7) and a 12-window horizon limit generalization.

The 16-row explanation background comprised eight original training rows per age group, sampled with random states 123 and 456. The 64 anchors came from stable make_window(70000,1,64). These fixed diagnostic objects were reused; they are not new independent replications. Shapley statistics do not enter the four ablation scores.

The review-spacing engineering check used development seeds 360100–360101, recorded separately in run_20261103_072712. Its 1,440 period rows and 120 run rows are not pooled into the main studies.

## Analysis units and reporting

The simulation unit for each scenario is the seed-wise stream. Repeated methods, budgets and windows are dependent evaluations. Regret sums window-average lost net benefit over windows 7–12; it is not a customer-total profit estimate. The supplied support tables recompute summary means from saved run rows and preserve every saved contrast. They do not reconstruct individual customer actions or calibration maxima.

The gate uses a pointwise mean-minus-1.96-SE rule, not a sequential confidence guarantee. Stable detection is not applicable; PERIODIC does not have an alert-calibration or detection endpoint. Equal caps do not mean equal actual reviews or compute. The 100-seed count is pragmatic; no formal power or equivalence claim is made.
