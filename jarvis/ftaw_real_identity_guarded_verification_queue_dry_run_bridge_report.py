"""Readable report for FTAW real identity-guarded verification queue dry-run bridge."""

from __future__ import annotations

from pathlib import Path

from .ftaw_real_identity_guarded_verification_queue_dry_run_bridge import (
    build_ftaw_real_identity_guarded_verification_queue_dry_run_bridge_from_files,
)


def build_ftaw_real_identity_guarded_verification_queue_dry_run_bridge_report(
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
) -> str:
    pack = build_ftaw_real_identity_guarded_verification_queue_dry_run_bridge_from_files(
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
    )
    lines = [
        "J.A.R.V.I.S. FTAW Real Identity-Guarded Verification Queue Dry-Run Bridge Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"queue dry-run bridge status: {pack.queue_dry_run_bridge_status}",
        f"upstream v4.38 status: {pack.upstream_v4_38_status}",
        f"required pass count: {pack.required_pass_count}",
        f"present pass count: {pack.present_pass_count}",
        f"missing/fail/needs-correction count: {pack.missing_fail_needs_correction_count}",
        f"dry-run preview item count: {pack.dry_run_preview_item_count}",
        f"manual/private outstanding count: {pack.manual_private_outstanding_count}",
        "preview item table:",
        "evidence_type | source_reference_id | manual_identity_guard_result | dry_run_queue_preview | real_queue_item_created | queue_eligibility_created | evidence_verified | verified_evidence_promoted | approved_asset | registry_mutation | buy_signal",
    ]
    if pack.preview_items:
        for item in pack.preview_items:
            lines.append(
                f"{item.evidence_type} | {item.source_reference_id} | {item.manual_identity_guard_result} | "
                f"{str(item.dry_run_queue_preview).lower()} | {str(item.real_queue_item_created).lower()} | "
                f"{str(item.queue_eligibility_created).lower()} | {str(item.evidence_verified).lower()} | "
                f"{str(item.verified_evidence_promoted).lower()} | {str(item.approved_asset).lower()} | "
                f"{str(item.registry_mutation).lower()} | {str(item.buy_signal).lower()}"
            )
    else:
        lines.append("none")
    lines.extend(["manual/private outstanding:", ", ".join(pack.manual_private_outstanding)])
    lines.append("blocked reasons:")
    lines.extend(f"- {item}" for item in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            f"next manual action: {pack.next_manual_action}",
            "verification queue dry-run preview is not queue eligibility.",
            "verification queue dry-run preview is not evidence verification.",
            "verification queue dry-run preview is not verified evidence promotion.",
            "verification queue dry-run preview is not asset approval.",
            "verification queue dry-run preview is not registry mutation.",
            "verification queue dry-run preview is not allocation advice.",
            "verification queue dry-run preview is not a buy/sell request.",
            "verification queue dry-run preview is not trade execution.",
            "no real queue item created: true",
            "no queue eligibility created: true",
            "no evidence verified: true",
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

    parser = argparse.ArgumentParser(description="Build FTAW real identity-guarded verification queue dry-run bridge report.")
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
    parser.add_argument(
        "real_identity_guarded_verification_queue_dry_run_bridge_config_path",
        nargs="?",
        default="jarvis/data/ftaw_real_identity_guarded_verification_queue_dry_run_bridge.example.json",
    )
    args = parser.parse_args()
    print(
        build_ftaw_real_identity_guarded_verification_queue_dry_run_bridge_report(
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
            args.explicit_manual_identity_guard_submission_command_config_path,
            args.identity_guard_submission_execution_review_config_path,
            args.manual_identity_guard_result_recorder_config_path,
            args.real_identity_guarded_verification_queue_dry_run_bridge_config_path,
        )
    )


if __name__ == "__main__":
    main()
