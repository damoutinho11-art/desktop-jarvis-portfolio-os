"""Readable report for FTAW identity guard submission review gate."""

from __future__ import annotations

from pathlib import Path

from .ftaw_identity_guard_submission_review_gate import build_ftaw_identity_guard_submission_review_gate_from_files


def build_ftaw_identity_guard_submission_review_gate_report(
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
) -> str:
    pack = build_ftaw_identity_guard_submission_review_gate_from_files(
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
    )
    lines = [
        "J.A.R.V.I.S. FTAW Identity Guard Submission Review Gate Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"gate status: {pack.gate_status}",
        f"upstream v4.34 status: {pack.upstream_v4_34_status}",
        f"required packet item count: {pack.required_packet_item_count}",
        f"present packet item count: {pack.present_packet_item_count}",
        f"missing packet item count: {pack.missing_packet_item_count}",
        f"manual/private outstanding count: {pack.manual_private_outstanding_count}",
        "readiness checks table:",
        "evidence_type | present | source_reference_id | ready | reason | identity_guard_executed | identity_guard_pass_created | queue_eligibility_created | evidence_verified | approved_asset | buy_signal",
    ]
    for check in pack.readiness_checks:
        lines.append(
            f"{check.evidence_type} | {str(check.present).lower()} | {check.source_reference_id or 'none'} | "
            f"{str(check.ready).lower()} | {check.reason} | {str(check.identity_guard_executed).lower()} | "
            f"{str(check.identity_guard_pass_created).lower()} | {str(check.queue_eligibility_created).lower()} | "
            f"{str(check.evidence_verified).lower()} | {str(check.approved_asset).lower()} | {str(check.buy_signal).lower()}"
        )
    lines.extend(["manual/private outstanding table:", "evidence_type | reason | next manual action"])
    for item in pack.manual_private_outstanding:
        lines.append(f"{item.evidence_type} | {item.reason} | {item.next_manual_action}")
    lines.append("blocked reasons:")
    lines.extend(f"- {item}" for item in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            f"next manual action: {pack.next_manual_action}",
            "identity guard submission review gate is not identity confirmation.",
            "identity guard submission review gate is not evidence verification.",
            "identity guard submission review gate is not queue eligibility.",
            "identity guard submission review gate is not asset approval.",
            "identity guard submission review gate is not registry mutation.",
            "identity guard submission review gate is not allocation advice.",
            "identity guard submission review gate is not a buy/sell request.",
            "identity guard submission review gate is not trade execution.",
            "no evidence verified: true",
            "no identity guard executed: true",
            "no identity guard pass created: true",
            "no queue eligibility created: true",
            "no verified evidence promotion: true",
            "no approvals created: true",
            "no registry mutation: true",
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

    parser = argparse.ArgumentParser(description="Build FTAW identity guard submission review gate report.")
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
    args = parser.parse_args()
    print(
        build_ftaw_identity_guard_submission_review_gate_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.url_fetch_config_path,
            args.fact_intake_config_path,
            args.identity_guard_config_path,
            args.queue_config_path,
            args.decision_config_path,
            args.preview_bridge_config_path,
            args.promotion_dry_run_config_path,
            args.readiness_config_path,
            args.approval_review_gate_config_path,
            args.human_decision_config_path,
            args.registry_update_dry_run_config_path,
            args.registry_update_apply_gate_config_path,
            args.explicit_manual_apply_command_config_path,
            args.execution_review_config_path,
            args.full_pipeline_audit_config_path,
            args.real_evidence_intake_readiness_config_path,
            args.collection_checklist_config_path,
            args.public_source_reference_plan_config_path,
            args.manual_public_source_reference_entry_config_path,
            args.manual_source_fact_entry_config_path,
            args.identity_guard_bridge_config_path,
            args.identity_guard_review_decision_config_path,
            args.identity_guard_submission_dry_run_config_path,
            args.identity_guard_submission_review_gate_config_path,
        )
    )


if __name__ == "__main__":
    main()
