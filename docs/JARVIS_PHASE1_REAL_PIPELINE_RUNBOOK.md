# J.A.R.V.I.S. Phase 1 Real Pipeline Runbook

Phase 1 turns manually collected real evidence for the FTAW/VWCE pilot candidate into a fully audited dry-run readiness state. It is a backend gate chain only: automated research, manual trust, manual approval, no execution.

Phase 1 is complete as of v4.47. The system has no executor, writes no registry update, approves no asset automatically, promotes no verified evidence automatically, creates no allocation recommendation, creates no buy/sell request, and executes no trade.

## Stage List

- v4.27 Real Evidence Intake Readiness Bridge: decides whether the candidate is ready to plan real evidence intake.
- v4.28 Real Evidence Collection Checklist Pack: lists required public, private, and manual evidence collection tasks.
- v4.29 Real Public Source Reference Intake Plan: plans public source references without fetching or downloading them.
- v4.30 Manual Public Source Reference Entry Recorder: records manually entered public source references.
- v4.31 Manual Source Fact Entry Pack: records manually entered source facts.
- v4.32 Real Manual Source Fact Identity Guard Bridge: prepares manually entered facts for identity-guard review.
- v4.33 Manual Identity Guard Review Decision Recorder: records manual identity-review decisions.
- v4.34 Identity Guard Submission Dry-Run Pack: builds a dry-run packet for identity-guard submission.
- v4.35 Identity Guard Submission Review Gate: checks whether the dry-run packet is ready for explicit manual submission.
- v4.36 Explicit Manual Identity Guard Submission Command Contract: validates the human command contract for the identity-guard submission step.
- v4.37 Identity Guard Submission Execution Review Pack: performs final preflight review for identity-guard submission.
- v4.38 Manual Identity Guard Result Recorder: records manually asserted identity-guard pass/fail results.
- v4.39 Real Identity-Guarded Verification Queue Dry-Run Bridge: previews manual verification queue items.
- v4.40 Real Manual Verification Decision Recorder: records human verification decisions for queue preview items.
- v4.41 Real Verified Evidence Preview Bridge: creates preview records only for accepted manual decisions.
- v4.42 Real Verified Evidence Promotion Dry-Run Pack: plans promotion as dry-run only.
- v4.43 Real Candidate Readiness Review Pack: reviews whether dry-run evidence coverage is sufficient for manual approval review.
- v4.44 Real Manual Approval Review Gate: prepares a human approval review packet.
- v4.45 Real Human Approval Review Decision Recorder: records a human approval-review decision.
- v4.46 Real Registry Update Dry-Run Pack: plans a registry status update as dry-run only.
- v4.47 Final Real Pipeline Audit Report: audits the whole real pipeline and issues the final safe dry-run verdict.

## Running Reports

Run default reports from PowerShell:

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

Run the v4.48 command index:

```powershell
python -m jarvis.jarvis_phase1_command_index_report
python -m jarvis.jarvis_phase1_command_index_report --input jarvis\data\jarvis_phase1_command_index.example.json
```

## v4.47 Final Audit Statuses

- `FINAL_REAL_PIPELINE_BLOCKED_SAFE`: the pipeline is safely blocked before dry-run readiness.
- `FINAL_REAL_PIPELINE_PARTIAL_SAFE`: some stages passed, but at least one required stage is blocked or partial.
- `FINAL_REAL_PIPELINE_DRY_RUN_READY_SAFE`: all Phase 1 real-pipeline stages reached dry-run readiness with safety flags preserved.

## Safety Flag Interpretation

- `registry_mutation false`: no candidate registry was changed.
- `registry_file_written false`: no registry file was written.
- `approved_asset false`: no asset was approved.
- `allocation_recommendation false`: no allocation advice was produced.
- `buy_signal false`: no buy signal was produced.
- `trade_executed false`: no trade was executed.
- `executor_created false`: no executor exists in Phase 1.

## What This System Does Not Do

- No approval.
- No mutation.
- No allocation advice.
- No buy/sell request.
- No trade.
- No broker API.
- No credentials.
- No private file auto-ingest.
- No automatic source fetching, downloads, or extraction.

## Future Candidate Intake Placeholder

Future candidate intake/watchlist expansion belongs in a future v4.49 layer. Do not implement v4.49 here.

VWCE and FTAW were pilot/test anchors for proving the manual-trust pipeline. Future candidates must pass the same evidence, identity, manual verification, manual approval, dry-run, and final audit chain before becoming trusted. No asset becomes investable or trusted automatically.
