# Paper 1 reproducibility guide

Prepared 8 November 2026. Author: Jegan Govinda (Jegov).

Paper: Evaluating Causal-Aware Monitoring in MLOps: Decision Robustness Under Distribution Shift and Operational Constraints.

Repository: https://github.com/jegov-ai/causal-ml-mlops-research
Branch: project1-inspection-repairs
Archive-preservation commit: 931f7dd. This identifies the code and six archives before this guide was added; it is not a DOI or an independent replication certificate.
Current manuscript at that checkpoint: manuscript/Paper1_Integrated_Development_Findings_20261108.md.

## Archive map

All paths below are under reproducibility/archives/. The original experiments and later development analyses must remain separate.

| Archive | Run | Evidence and purpose |
| --- | --- | --- |
| Project1_Ablation_Study_012152.zip | run_20261102_012152 | Prospectively specified exploratory main ablation; 100 paired evaluation stream seeds, five scenarios, caps2/4/8; M1/A/B/FULL. Additional signals produced exactly zero observed incremental regret differences. |
| Project1_Schedule_Study_054710.zip | run_20261102_054710 | Separate prospective exploratory calendar comparison; 100 fresh paired seeds, M1/A/B/FULL/PERIODIC. Selected-calendar gains and adverse subgroup cases retained. |
| Project1_Review_Spacing_072712.zip | run_20261103_072712 | Two-seed engineering development check. Not main inferential evidence. |
| Project1_Sensitivity_Development_102857.zip | run_20261106_102857_143041 | Three exposed stream seeds paired across initial data/fitting seeds42/1042/2042 and onsets4/7/10; stable evaluated once. 117 dependent configurations, not117 independent replications. Includes M0/M1/FULL/PERIODIC. |
| Project1_Gate_Diagnostics_143830.zip | run_20261108_143830 | Retrospective replay of all117 sensitivity configurations; original period outputs reproduced, added offline candidate/incumbent benefit diagnostics. Not fresh independent evidence. |
| Project1_Refreshed_Gate_162422.zip | run_20261108_162422 | Exploratory frozen-versus-refreshed gate comparison on the same exposed development streams. Mixed outcomes and harmful accepted updates retained. Not validated replacement or causal-monitoring superiority. |

The development smoke runs and earlier historical studies are not duplicated in this six-archive set. This set supports the current manuscript's listed evaluations, not a claim that every historical Project1 run has been archived here. Preserve the broader repository history and findings.

## Verify archive integrity

archive_checksums.csv records SHA256 values for the six archive files. The copied files were checked against their Downloads originals and their ZIP contents passed Python zipfile.testzip() before commit. Checksums identify bytes; they do not validate scientific conclusions.

From the project root in Windows Command Prompt:

```cmd
.venv\Scripts\python.exe -c "from pathlib import Path; import csv,hashlib,zipfile; rows=list(csv.DictReader(Path('reproducibility/archive_checksums.csv').open(encoding='utf-8-sig'))); assert len(rows)==6; exec('for row in rows:\n p=Path(\"reproducibility/archives\")/row[\"File\"]\n assert hashlib.sha256(p.read_bytes()).hexdigest().lower()==row[\"Hash\"].lower(),p.name\n with zipfile.ZipFile(p) as z: assert z.testzip() is None,p.name\n print(\"VERIFIED:\",p.name)')"
```

This command requires a Python environment; it does not install dependencies or run simulations. Other operating systems can verify the same hashes using their usual SHA256 tools.

Extract each archive into a separate new directory and retain its internal structure. Do not overwrite original run directories or execute archived code merely to inspect output. Original Windows ZIP members may use Windows path separators; cross-platform extraction must handle them deliberately. The index identifies run names without assuming every archive uses identical internal layout.

## Code, protocols and analysis records

| Evaluation | Main source | Protocol/analysis location |
| --- | --- | --- |
| Main ablation | paper1_experiments/monitoring_signal_ablation_v1.py | SIGNAL_ABLATION_MAIN_PROTOCOL_v1.md; SIGNAL_ABLATION_MAIN_FINDINGS_20261102.md |
| Calendar comparison | paper1_experiments/monitoring_schedule_comparison_v1.py | SCHEDULE_COMPARISON_PROTOCOL_v1.md; SCHEDULE_COMPARISON_FINDINGS_20261102.md |
| Spacing development | paper1_experiments/monitoring_review_spacing_v1.py | REVIEW_SPACING_DEVELOPMENT_PROTOCOL_v1.md |
| Model/onset development | paper1_experiments/model_onset_sensitivity_v1.py | MODEL_ONSET_SENSITIVITY_DEVELOPMENT_PROTOCOL_v1.md; MODEL_ONSET_SENSITIVITY_DEVELOPMENT_FINDINGS_20261108.md |
| Gate replay | paper1_experiments/gate_diagnostic_replay_v1.py | GATE_DIAGNOSTIC_REPLAY_PROTOCOL_v1.md; GATE_DIAGNOSTIC_FINDINGS_20261108.md |
| Refreshed gate | paper1_experiments/refreshed_gate_development_v1.py | REFRESHED_GATE_DEVELOPMENT_PROTOCOL_v1.md; REFRESHED_GATE_DEVELOPMENT_FINDINGS_20261108.md |

Unqualified protocol/findings filenames in this table are in paper1_experiments/. Historical source snapshots and recorded hashes are authoritative for their own runs; later code should not silently replace them.

Supplementary numerical tables and records:
- manuscript/support/PAPER1_SUPPORTING_TABLES_v1.md: main-study summaries and paired contrasts.
- manuscript/support/POSTHOC_SAVED_BENCHMARK_CONTRASTS_20261103.csv:225 post-hoc policy-benchmark contrasts. These were not prospective primary analyses.
- manuscript/support/SENSITIVITY_CELL_MEAN_CONTRASTS_20261108.csv and SENSITIVITY_AUDIT_CHECKS_20261108.json: model/onset development records.
- manuscript/support/gate_diagnostics_20261108/: gate replay classification tables and audit record.
- manuscript/support/refreshed_gate_20261108/: all paired differences, cell means and accepted-update diagnostics.

## Reproduction levels and limitations

1. Archive integrity: file hashes and ZIP integrity checked before preservation.
2. Output consistency: main/sensitivity/replay/comparison audits reconcile saved keys, aggregation, event schedules, acceptance flags and reported contrasts as documented in their findings. These checks do not independently reconstruct every original random-forest fit or customer action.
3. Numerical replay: all117 sensitivity development configurations were replayed on the original Windows environment, with every original period field reconciled at absolute/relative tolerance1e-12. Refreshed comparison also reproduces frozen results and matches monitoring/review opportunities. This is same-environment reproduction on exposed seeds.
4. Independent execution from a clean checkout: not yet demonstrated. Do not claim that this guide proves environment portability or a one-command end-to-end reproduction.

The recorded Windows environment includes Python3.12.10, NumPy2.5.4, pandas3.1.0 and scikit-learn1.9.1. Consult each run's own manifest/checkpoint; these reported versions are not an independently tested installation recipe. No complete new environment lockfile is supplied by this guide.

Some historical audit scripts use local analysis paths. In particular, manuscript/support/gate_diagnostics_20261108/audit_gate_diagnostics.py is an analysis record with path assumptions, not a turnkey clean-checkout CLI. The refreshed audit has --run and --reference arguments but its independent re-execution on a new machine has not been demonstrated. Adjusting paths for reproduction must be documented rather than presented as already verified.

Evaluation runners include collision/provenance guards and are not generally safe to rerun blindly into existing directories. Reusing published seeds is reproduction, not independent evidence. Preserve partial runs and diagnose failures before retrying.

## Scientific boundaries

Main studies condition on one initial fit and onset7. Later development uses three stream seeds and dependent factor evaluations; do not pool these as independent replications. Gate diagnostics compare fixed candidate/incumbent policies on gate or next-window observations; summing diagnostic gains does not give attainable all-horizon improvement. Synthetic truth is reserved for offline evaluation. No deployed-policy feedback, real-world deployment validation, sequential-safety guarantee or profitability claim is established.

The original gate remains the baseline. Refreshed-gate benefits and harms are both retained. Current code/results do not establish a new causal estimator, universal superiority, population equivalence or assured publication novelty.

## Before external submission

Confirm that the intended journal permits the chosen public code/data location, finalize a stable version/release reference, and test clean-checkout instructions if claiming independent reproducibility. A persistent DOI-backed deposit can supplement GitHub but has not been created by this guide. Authorship, affiliation, licensing, funding and AI-use disclosures require explicit finalization; no license or approval is inferred here.
