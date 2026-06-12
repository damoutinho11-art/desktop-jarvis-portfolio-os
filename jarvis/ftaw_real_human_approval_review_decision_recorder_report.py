"""Readable report for FTAW real human approval review decision recorder."""

from __future__ import annotations

from pathlib import Path

from .ftaw_real_human_approval_review_decision_recorder import (
    build_ftaw_real_human_approval_review_decision_recorder_from_files,
)


def build_ftaw_real_human_approval_review_decision_recorder_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
    preview_bridge_config_path: str | Path,
    promotion_dry_run_config_path: str | Path,
    readiness_config_path: str | Path,
    approval_review_gate_config_path: str | Path,
    human_decision_config_path: str | Path,
    registry_update_dry_run_config_path: str | Path,
    registry_update_apply_gate_config_path: str | Path,
    explicit_manual_apply_command_config_path: str | Path,
    execution_review_config_path: str | Path,
    full_pipeline_audit_config_path: str | Path,
    real_evidence_intake_readiness_config_path: str | Path,
    collection_checklist_config_path: str | Path,
    public_source_reference_plan_config_path: str | Path,
    manual_public_source_reference_entry_config_path: str | Path,
    manual_source_fact_entry_config_path: str | Path,
    identity_guard_bridge_config_path: str | Path,
    identity_guard_review_decision_config_path: str | Path,
    identity_guard_submission_dry_run_config_path: str | Path,
    identity_guard_submission_review_gate_config_path: str | Path,
    explicit_manual_identity_guard_submission_command_config_path: str | Path,
    identity_guard_submission_execution_review_config_path: str | Path,
    manual_identity_guard_result_recorder_config_path: str | Path,
    real_identity_guarded_verification_queue_dry_run_bridge_config_path: str | Path,
    real_manual_verification_decision_recorder_config_path: str | Path,
    real_verified_evidence_preview_bridge_config_path: str | Path,
    real_verified_evidence_promotion_dry_run_pack_config_path: str | Path,
    real_candidate_readiness_review_pack_config_path: str | Path,
    real_manual_approval_review_gate_config_path: str | Path,
    real_human_approval_review_decision_recorder_config_path: str | Path,
) -> str:
    pack = build_ftaw_real_human_approval_review_decision_recorder_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
        approval_review_gate_config_path,
        human_decision_config_path,
        registry_update_dry_run_config_path,
        registry_update_apply_gate_config_path,
        explicit_manual_apply_command_config_path,
        execution_review_config_path,
        full_pipeline_audit_config_path,
        real_evidence_intake_readiness_config_path,
        collection_checklist_config_path,
        public_source_reference_plan_config_path,
        manual_public_source_reference_entry_config_path,
        manual_source_fact_entry_config_path,
        identity_guard_bridge_config_path,
        identity_guard_review_decision_config_path,
        identity_guard_submission_dry_run_config_path,
        identity_guard_submission_review_gate_config_path,
        explicit_manual_identity_guard_submission_command_config_path,
        identity_guard_submission_execution_review_config_path,
        manual_identity_guard_result_recorder_config_path,
        real_identity_guarded_verification_queue_dry_run_bridge_config_path,
        real_manual_verification_decision_recorder_config_path,
        real_verified_evidence_preview_bridge_config_path,
        real_verified_evidence_promotion_dry_run_pack_config_path,
        real_candidate_readiness_review_pack_config_path,
        real_manual_approval_review_gate_config_path,
        real_human_approval_review_decision_recorder_config_path,
    )
    record = pack.decision_record
    lines = [
        "J.A.R.V.I.S. FTAW Real Human Approval Review Decision Recorder Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"recorder status: {pack.recorder_status}",
        f"upstream v4.44 status: {pack.upstream_v4_44_status}",
        f"decision: {pack.decision}",
        f"decision recorded: {str(pack.decision_recorded).lower()}",
        f"registry dry-run ready: {str(pack.registry_update_dry_run_ready).lower()}",
        "decision table:",
        "asset_id | decision | decision_status | decision_recorded | registry_update_dry_run_ready | approved_asset | approval_status_change | registry_mutation | allocation_recommendation | buy_signal | trade_executed | reviewer_notes",
    ]
    if record is None:
        lines.append("none")
    else:
        lines.append(
            f"{record.asset_id} | {record.decision} | {record.decision_status} | "
            f"{str(record.decision_recorded).lower()} | {str(record.registry_update_dry_run_ready).lower()} | "
            f"{str(record.approved_asset).lower()} | {str(record.approval_status_change).lower()} | "
            f"{str(record.registry_mutation).lower()} | {str(record.allocation_recommendation).lower()} | "
            f"{str(record.buy_signal).lower()} | {str(record.trade_executed).lower()} | {record.reviewer_notes}"
        )
    lines.append("blocked reasons:")
    lines.extend(f"- {item}" for item in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            f"next manual action: {pack.next_manual_action}",
            "human approval review decision recording is not registry mutation.",
            "human approval review decision recording is not allocation advice.",
            "human approval review decision recording is not a buy/sell request.",
            "human approval review decision recording is not trade execution.",
            "no registry mutation: true",
            "no allocation recommendations: true",
            "no buy/sell requests: true",
            "no trades executed: true",
            "no executor created: true",
            "no evidence verified: true",
            "no verified evidence promotion: true",
            "no private file auto-ingest: true",
            "no automatic source fetching: true",
            "no automatic downloads: true",
            "no automatic fact extraction: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW real human approval review decision recorder report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("url_fetch_config_path", nargs="?", default="jarvis/data/ftaw_public_url_fetch_adapter.example.json")
    parser.add_argument("fact_intake_config_path", nargs="?", default="jarvis/data/ftaw_source_fact_intake.example.json")
    parser.add_argument("identity_guard_config_path", nargs="?", default="jarvis/data/ftaw_source_identity_guard.example.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/ftaw_identity_guarded_verification_queue.example.json")
    parser.add_argument("decision_config_path", nargs="?", default="jarvis/data/ftaw_manual_verification_decision_recorder.example.json")
    parser.add_argument("preview_bridge_config_path", nargs="?", default="jarvis/data/ftaw_verified_evidence_preview_bridge.example.json")
    parser.add_argument("promotion_dry_run_config_path", nargs="?", default="jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json")
    parser.add_argument("readiness_config_path", nargs="?", default="jarvis/data/ftaw_candidate_readiness_pack.example.json")
    parser.add_argument("approval_review_gate_config_path", nargs="?", default="jarvis/data/ftaw_manual_approval_review_gate.example.json")
    parser.add_argument("human_decision_config_path", nargs="?", default="jarvis/data/ftaw_human_approval_review_decision_recorder.example.json")
    parser.add_argument("registry_update_dry_run_config_path", nargs="?", default="jarvis/data/ftaw_registry_update_dry_run_pack.example.json")
    parser.add_argument("registry_update_apply_gate_config_path", nargs="?", default="jarvis/data/ftaw_registry_update_apply_gate.example.json")
    parser.add_argument("explicit_manual_apply_command_config_path", nargs="?", default="jarvis/data/ftaw_explicit_manual_apply_command_contract.example.json")
    parser.add_argument("execution_review_config_path", nargs="?", default="jarvis/data/ftaw_registry_apply_execution_review_pack.example.json")
    parser.add_argument("full_pipeline_audit_config_path", nargs="?", default="jarvis/data/ftaw_full_pipeline_audit_report.example.json")
    parser.add_argument("real_evidence_intake_readiness_config_path", nargs="?", default="jarvis/data/ftaw_real_evidence_intake_readiness_bridge.example.json")
    parser.add_argument("collection_checklist_config_path", nargs="?", default="jarvis/data/ftaw_real_evidence_collection_checklist_pack.example.json")
    parser.add_argument("public_source_reference_plan_config_path", nargs="?", default="jarvis/data/ftaw_real_public_source_reference_intake_plan.example.json")
    parser.add_argument("manual_public_source_reference_entry_config_path", nargs="?", default="jarvis/data/ftaw_manual_public_source_reference_entry_recorder.example.json")
    parser.add_argument("manual_source_fact_entry_config_path", nargs="?", default="jarvis/data/ftaw_manual_source_fact_entry_pack.example.json")
    parser.add_argument("identity_guard_bridge_config_path", nargs="?", default="jarvis/data/ftaw_real_manual_source_fact_identity_guard_bridge.example.json")
    parser.add_argument("identity_guard_review_decision_config_path", nargs="?", default="jarvis/data/ftaw_real_manual_identity_guard_review_decision_recorder.example.json")
    parser.add_argument("identity_guard_submission_dry_run_config_path", nargs="?", default="jarvis/data/ftaw_identity_guard_submission_dry_run_pack.example.json")
    parser.add_argument("identity_guard_submission_review_gate_config_path", nargs="?", default="jarvis/data/ftaw_identity_guard_submission_review_gate.example.json")
    parser.add_argument("explicit_manual_identity_guard_submission_command_config_path", nargs="?", default="jarvis/data/ftaw_explicit_manual_identity_guard_submission_command_contract.example.json")
    parser.add_argument("identity_guard_submission_execution_review_config_path", nargs="?", default="jarvis/data/ftaw_identity_guard_submission_execution_review_pack.example.json")
    parser.add_argument("manual_identity_guard_result_recorder_config_path", nargs="?", default="jarvis/data/ftaw_manual_identity_guard_result_recorder.example.json")
    parser.add_argument("real_identity_guarded_verification_queue_dry_run_bridge_config_path", nargs="?", default="jarvis/data/ftaw_real_identity_guarded_verification_queue_dry_run_bridge.example.json")
    parser.add_argument("real_manual_verification_decision_recorder_config_path", nargs="?", default="jarvis/data/ftaw_real_manual_verification_decision_recorder.example.json")
    parser.add_argument("real_verified_evidence_preview_bridge_config_path", nargs="?", default="jarvis/data/ftaw_real_verified_evidence_preview_bridge.example.json")
    parser.add_argument("real_verified_evidence_promotion_dry_run_pack_config_path", nargs="?", default="jarvis/data/ftaw_real_verified_evidence_promotion_dry_run_pack.example.json")
    parser.add_argument("real_candidate_readiness_review_pack_config_path", nargs="?", default="jarvis/data/ftaw_real_candidate_readiness_review_pack.example.json")
    parser.add_argument("real_manual_approval_review_gate_config_path", nargs="?", default="jarvis/data/ftaw_real_manual_approval_review_gate.example.json")
    parser.add_argument("real_human_approval_review_decision_recorder_config_path", nargs="?", default="jarvis/data/ftaw_real_human_approval_review_decision_recorder.example.json")
    args = parser.parse_args()
    print(build_ftaw_real_human_approval_review_decision_recorder_report(**vars(args)))


if __name__ == "__main__":
    main()
