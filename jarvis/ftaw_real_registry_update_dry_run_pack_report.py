"""Readable report for FTAW real registry update dry-run pack."""

from __future__ import annotations

from pathlib import Path

from .ftaw_real_registry_update_dry_run_pack import build_ftaw_real_registry_update_dry_run_pack_from_files


def build_ftaw_real_registry_update_dry_run_pack_report(
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
    real_registry_update_dry_run_pack_config_path: str | Path,
) -> str:
    pack = build_ftaw_real_registry_update_dry_run_pack_from_files(
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
        real_registry_update_dry_run_pack_config_path,
    )
    plan = pack.dry_run_plan
    lines = [
        "J.A.R.V.I.S. FTAW Real Registry Update Dry-Run Pack Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"dry-run status: {pack.dry_run_status}",
        f"upstream v4.45 status: {pack.upstream_v4_45_status}",
        f"current status: {pack.current_status or 'none'}",
        f"proposed dry-run status: {pack.proposed_dry_run_status or 'none'}",
        f"dry-run plan created: {str(pack.dry_run_plan_created).lower()}",
        f"registry mutation: {str(pack.registry_mutation).lower()}",
        f"registry file written: {str(pack.registry_file_written).lower()}",
        "dry-run plan:",
        "asset_id | current_status | proposed_dry_run_status | dry_run | registry_mutation | registry_file_written | current_status_unchanged | approved_asset | allocation_recommendation | buy_signal | trade_executed",
    ]
    if plan is None:
        lines.append("none")
    else:
        lines.append(
            f"{plan.asset_id} | {plan.current_status} | {plan.proposed_dry_run_status} | "
            f"{str(plan.dry_run).lower()} | {str(plan.registry_mutation).lower()} | "
            f"{str(plan.registry_file_written).lower()} | {str(plan.current_status_unchanged).lower()} | "
            f"{str(plan.approved_asset).lower()} | {str(plan.allocation_recommendation).lower()} | "
            f"{str(plan.buy_signal).lower()} | {str(plan.trade_executed).lower()}"
        )
    lines.append("blocked reasons:")
    lines.extend(f"- {item}" for item in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            f"next manual action: {pack.next_manual_action}",
            "registry update dry-run is not registry mutation.",
            "registry update dry-run is not asset approval.",
            "registry update dry-run is not allocation advice.",
            "registry update dry-run is not a buy/sell request.",
            "registry update dry-run is not trade execution.",
            "no registry mutation: true",
            "no registry file written: true",
            "no approvals created: true",
            "approved asset false: true",
            "no allocation recommendations: true",
            "no buy/sell requests: true",
            "no trades executed: true",
            "no executor created: true",
            "no private file auto-ingest: true",
            "no automatic source fetching: true",
            "no automatic downloads: true",
            "no automatic fact extraction: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW real registry update dry-run pack report.")
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
    parser.add_argument("real_registry_update_dry_run_pack_config_path", nargs="?", default="jarvis/data/ftaw_real_registry_update_dry_run_pack.example.json")
    args = parser.parse_args()
    print(build_ftaw_real_registry_update_dry_run_pack_report(**vars(args)))


if __name__ == "__main__":
    main()
