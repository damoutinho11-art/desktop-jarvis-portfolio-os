# J.A.R.V.I.S. Command Index

This command index is a quick reference for running the Phase 1 real-evidence FTAW pipeline reports and checks from PowerShell.

Phase 1 backend gate chain is complete. J.A.R.V.I.S. has no executor and performs no registry mutation, approval, evidence promotion, allocation recommendation, buy/sell request, or trade.

## Phase 1 Stages

- v4.27: FTAW Real Evidence Intake Readiness Bridge
- v4.28: FTAW Real Evidence Collection Checklist Pack
- v4.29: FTAW Real Public Source Reference Intake Plan
- v4.30: FTAW Manual Public Source Reference Entry Recorder
- v4.31: FTAW Manual Source Fact Entry Pack
- v4.32: FTAW Real Manual Source Fact Identity Guard Bridge
- v4.33: FTAW Manual Identity Guard Review Decision Recorder
- v4.34: FTAW Identity Guard Submission Dry-Run Pack
- v4.35: FTAW Identity Guard Submission Review Gate
- v4.36: FTAW Explicit Manual Identity Guard Submission Command Contract
- v4.37: FTAW Identity Guard Submission Execution Review Pack
- v4.38: FTAW Manual Identity Guard Result Recorder
- v4.39: FTAW Real Identity-Guarded Verification Queue Dry-Run Bridge
- v4.40: FTAW Real Manual Verification Decision Recorder
- v4.41: FTAW Real Verified Evidence Preview Bridge
- v4.42: FTAW Real Verified Evidence Promotion Dry-Run Pack
- v4.43: FTAW Real Candidate Readiness Review Pack
- v4.44: FTAW Real Manual Approval Review Gate
- v4.45: FTAW Real Human Approval Review Decision Recorder
- v4.46: FTAW Real Registry Update Dry-Run Pack
- v4.47: FTAW Final Real Pipeline Audit Report

## Verification Commands

Run these from the repo root:

```powershell
python -m py_compile jarvis\jarvis_phase1_command_index_report.py jarvis\tests\test_jarvis_phase1_command_index_report.py
python -m unittest jarvis.tests.test_jarvis_phase1_command_index_report -v
python -m unittest discover jarvis/tests
```

## v4.48 Command Index Reports

```powershell
python -m jarvis.jarvis_phase1_command_index_report
python -m jarvis.jarvis_phase1_command_index_report --input jarvis\data\jarvis_phase1_command_index.example.json
```

## Phase 1 Report Entry Points

Default report commands:

```powershell
python -m jarvis.ftaw_real_evidence_intake_readiness_bridge_report
python -m jarvis.ftaw_real_evidence_collection_checklist_pack_report
python -m jarvis.ftaw_real_public_source_reference_intake_plan_report
python -m jarvis.ftaw_manual_public_source_reference_entry_recorder_report
python -m jarvis.ftaw_manual_source_fact_entry_pack_report
python -m jarvis.ftaw_real_manual_source_fact_identity_guard_bridge_report
python -m jarvis.ftaw_real_manual_identity_guard_review_decision_recorder_report
python -m jarvis.ftaw_identity_guard_submission_dry_run_pack_report
python -m jarvis.ftaw_identity_guard_submission_review_gate_report
python -m jarvis.ftaw_explicit_manual_identity_guard_submission_command_contract_report
python -m jarvis.ftaw_identity_guard_submission_execution_review_pack_report
python -m jarvis.ftaw_manual_identity_guard_result_recorder_report
python -m jarvis.ftaw_real_identity_guarded_verification_queue_dry_run_bridge_report
python -m jarvis.ftaw_real_manual_verification_decision_recorder_report
python -m jarvis.ftaw_real_verified_evidence_preview_bridge_report
python -m jarvis.ftaw_real_verified_evidence_promotion_dry_run_pack_report
python -m jarvis.ftaw_real_candidate_readiness_review_pack_report
python -m jarvis.ftaw_real_manual_approval_review_gate_report
python -m jarvis.ftaw_real_human_approval_review_decision_recorder_report
python -m jarvis.ftaw_real_registry_update_dry_run_pack_report
python -m jarvis.ftaw_final_real_pipeline_audit_report
```

v4.47 final audit reports:

```powershell
python -m jarvis.ftaw_final_real_pipeline_audit_report
python -m jarvis.ftaw_final_real_pipeline_audit_report jarvis\data\candidate_assets.v2.example.json None jarvis\data\ftaw_public_url_fetch_adapter.example.json jarvis\data\ftaw_source_fact_intake.example.json jarvis\data\ftaw_source_identity_guard.example.json jarvis\data\ftaw_identity_guarded_verification_queue.synthetic_complete.example.json jarvis\data\ftaw_manual_verification_decision_recorder.synthetic_complete.example.json jarvis\data\ftaw_verified_evidence_preview_bridge.synthetic_complete.example.json jarvis\data\ftaw_verified_evidence_promotion_dry_run.synthetic_complete.example.json jarvis\data\ftaw_candidate_readiness_pack.synthetic_complete.example.json jarvis\data\ftaw_manual_approval_review_gate.synthetic_complete.example.json jarvis\data\ftaw_human_approval_review_decision_recorder.synthetic_complete.example.json jarvis\data\ftaw_registry_update_dry_run_pack.synthetic_complete.example.json jarvis\data\ftaw_registry_update_apply_gate.synthetic_complete.example.json jarvis\data\ftaw_explicit_manual_apply_command_contract.synthetic_complete.example.json jarvis\data\ftaw_registry_apply_execution_review_pack.synthetic_complete.example.json jarvis\data\ftaw_full_pipeline_audit_report.synthetic_complete.example.json jarvis\data\ftaw_real_evidence_intake_readiness_bridge.synthetic_complete.example.json jarvis\data\ftaw_real_evidence_collection_checklist_pack.synthetic_complete.example.json jarvis\data\ftaw_real_public_source_reference_intake_plan.synthetic_complete.example.json jarvis\data\ftaw_manual_public_source_reference_entry_recorder.synthetic_complete.example.json jarvis\data\ftaw_manual_source_fact_entry_pack.synthetic_complete.example.json jarvis\data\ftaw_real_manual_source_fact_identity_guard_bridge.synthetic_complete.example.json jarvis\data\ftaw_real_manual_identity_guard_review_decision_recorder.synthetic_complete.example.json jarvis\data\ftaw_identity_guard_submission_dry_run_pack.synthetic_complete.example.json jarvis\data\ftaw_identity_guard_submission_review_gate.synthetic_complete.example.json jarvis\data\ftaw_explicit_manual_identity_guard_submission_command_contract.synthetic_complete.example.json jarvis\data\ftaw_identity_guard_submission_execution_review_pack.synthetic_complete.example.json jarvis\data\ftaw_manual_identity_guard_result_recorder.synthetic_complete.example.json jarvis\data\ftaw_real_identity_guarded_verification_queue_dry_run_bridge.synthetic_complete.example.json jarvis\data\ftaw_real_manual_verification_decision_recorder.synthetic_complete.example.json jarvis\data\ftaw_real_verified_evidence_preview_bridge.synthetic_complete.example.json jarvis\data\ftaw_real_verified_evidence_promotion_dry_run_pack.synthetic_complete.example.json jarvis\data\ftaw_real_candidate_readiness_review_pack.synthetic_complete.example.json jarvis\data\ftaw_real_manual_approval_review_gate.synthetic_complete.example.json jarvis\data\ftaw_real_human_approval_review_decision_recorder.synthetic_partial.example.json jarvis\data\ftaw_real_registry_update_dry_run_pack.synthetic_partial.example.json jarvis\data\ftaw_final_real_pipeline_audit_report.synthetic_partial.example.json
python -m jarvis.ftaw_final_real_pipeline_audit_report jarvis\data\candidate_assets.v2.example.json None jarvis\data\ftaw_public_url_fetch_adapter.example.json jarvis\data\ftaw_source_fact_intake.example.json jarvis\data\ftaw_source_identity_guard.example.json jarvis\data\ftaw_identity_guarded_verification_queue.synthetic_complete.example.json jarvis\data\ftaw_manual_verification_decision_recorder.synthetic_complete.example.json jarvis\data\ftaw_verified_evidence_preview_bridge.synthetic_complete.example.json jarvis\data\ftaw_verified_evidence_promotion_dry_run.synthetic_complete.example.json jarvis\data\ftaw_candidate_readiness_pack.synthetic_complete.example.json jarvis\data\ftaw_manual_approval_review_gate.synthetic_complete.example.json jarvis\data\ftaw_human_approval_review_decision_recorder.synthetic_complete.example.json jarvis\data\ftaw_registry_update_dry_run_pack.synthetic_complete.example.json jarvis\data\ftaw_registry_update_apply_gate.synthetic_complete.example.json jarvis\data\ftaw_explicit_manual_apply_command_contract.synthetic_complete.example.json jarvis\data\ftaw_registry_apply_execution_review_pack.synthetic_complete.example.json jarvis\data\ftaw_full_pipeline_audit_report.synthetic_complete.example.json jarvis\data\ftaw_real_evidence_intake_readiness_bridge.synthetic_complete.example.json jarvis\data\ftaw_real_evidence_collection_checklist_pack.synthetic_complete.example.json jarvis\data\ftaw_real_public_source_reference_intake_plan.synthetic_complete.example.json jarvis\data\ftaw_manual_public_source_reference_entry_recorder.synthetic_complete.example.json jarvis\data\ftaw_manual_source_fact_entry_pack.synthetic_complete.example.json jarvis\data\ftaw_real_manual_source_fact_identity_guard_bridge.synthetic_complete.example.json jarvis\data\ftaw_real_manual_identity_guard_review_decision_recorder.synthetic_complete.example.json jarvis\data\ftaw_identity_guard_submission_dry_run_pack.synthetic_complete.example.json jarvis\data\ftaw_identity_guard_submission_review_gate.synthetic_complete.example.json jarvis\data\ftaw_explicit_manual_identity_guard_submission_command_contract.synthetic_complete.example.json jarvis\data\ftaw_identity_guard_submission_execution_review_pack.synthetic_complete.example.json jarvis\data\ftaw_manual_identity_guard_result_recorder.synthetic_complete.example.json jarvis\data\ftaw_real_identity_guarded_verification_queue_dry_run_bridge.synthetic_complete.example.json jarvis\data\ftaw_real_manual_verification_decision_recorder.synthetic_complete.example.json jarvis\data\ftaw_real_verified_evidence_preview_bridge.synthetic_complete.example.json jarvis\data\ftaw_real_verified_evidence_promotion_dry_run_pack.synthetic_complete.example.json jarvis\data\ftaw_real_candidate_readiness_review_pack.synthetic_complete.example.json jarvis\data\ftaw_real_manual_approval_review_gate.synthetic_complete.example.json jarvis\data\ftaw_real_human_approval_review_decision_recorder.synthetic_complete.example.json jarvis\data\ftaw_real_registry_update_dry_run_pack.synthetic_complete.example.json jarvis\data\ftaw_final_real_pipeline_audit_report.synthetic_complete.example.json
```

The default command produces a blocked-safe report. The synthetic complete command produces `FINAL_REAL_PIPELINE_DRY_RUN_READY_SAFE` and still performs no mutation or execution.

## Cleanup And Git Checks

```powershell
Get-ChildItem -Path jarvis -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force
Get-ChildItem -Path jarvis -Recurse -File -Include *.pyc | Remove-Item -Force
git status --short
git log --oneline -6
```
