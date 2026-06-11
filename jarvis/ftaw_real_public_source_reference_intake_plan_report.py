"""Readable report for FTAW real public source reference intake plan."""

from __future__ import annotations

from pathlib import Path

from .ftaw_real_public_source_reference_intake_plan import build_ftaw_real_public_source_reference_intake_plan_from_files


def build_ftaw_real_public_source_reference_intake_plan_report(
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
) -> str:
    plan = build_ftaw_real_public_source_reference_intake_plan_from_files(
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
    )
    lines = [
        "J.A.R.V.I.S. FTAW Real Public Source Reference Intake Plan Report",
        "Automated structure. Manual trust.",
        f"target asset: {plan.target_asset}",
        f"public source reference plan status: {plan.public_source_reference_plan_status}",
        f"upstream checklist status: {plan.upstream_checklist_status}",
        f"source reference slot count: {plan.source_reference_slot_count}",
        f"public official slot count: {plan.public_official_slot_count}",
        f"public market slot count: {plan.public_market_slot_count}",
        f"private manual slot count: {plan.private_manual_slot_count}",
        f"manual confirmation slot count: {plan.manual_confirmation_slot_count}",
        f"auto_fetch_allowed count: {plan.auto_fetch_allowed_count}",
        f"auto_download_allowed count: {plan.auto_download_allowed_count}",
        f"auto_verify_allowed count: {plan.auto_verify_allowed_count}",
        "per-slot table:",
        "evidence_type | source_category | public_or_private | commit_safety | manual_url_required | auto_fetch_allowed | auto_download_allowed | auto_verify_allowed | collected | verified | manual action",
    ]
    for slot in plan.source_reference_slots:
        lines.append(
            f"{slot.evidence_type} | {slot.source_category} | {slot.expected_public_or_private} | "
            f"{slot.expected_commit_safety} | {str(slot.manual_url_required).lower()} | "
            f"{str(slot.auto_fetch_allowed).lower()} | {str(slot.auto_download_allowed).lower()} | "
            f"{str(slot.auto_verify_allowed).lower()} | {str(slot.collected).lower()} | "
            f"{str(slot.verified).lower()} | {slot.manual_action}"
        )
    lines.append("blocked reasons:")
    lines.extend(f"- {item}" for item in plan.blocked_reasons) if plan.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            f"next manual action: {plan.next_manual_action}",
            f"source fact intake records created: {str(plan.source_fact_intake_records_created).lower()}",
            f"identity guard pass records created: {str(plan.identity_guard_pass_records_created).lower()}",
            f"queue eligibility created: {str(plan.queue_eligibility_created).lower()}",
            f"approved_asset: {str(plan.approved_asset).lower()}",
            f"registry_mutation: {str(plan.registry_mutation).lower()}",
            f"verified_evidence_promotion: {str(plan.verified_evidence_promotion).lower()}",
            f"automatic_source_fetching: {str(plan.automatic_source_fetching).lower()}",
            f"automatic_downloads: {str(plan.automatic_downloads).lower()}",
            "public source reference plan is not evidence collection.",
            "public source reference plan is not evidence verification.",
            "public source reference plan is not asset approval.",
            "public source reference plan is not registry mutation.",
            "public source reference plan is not allocation advice.",
            "public source reference plan is not a buy/sell request.",
            "public source reference plan is not trade execution.",
            "public source reference plan does not fetch or download sources automatically.",
            "private evidence must not be committed.",
            "no evidence collected: true",
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
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW real public source reference intake plan report.")
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
    args = parser.parse_args()
    print(
        build_ftaw_real_public_source_reference_intake_plan_report(
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
        )
    )


if __name__ == "__main__":
    main()
