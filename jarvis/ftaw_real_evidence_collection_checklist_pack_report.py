"""Readable report for FTAW real evidence collection checklist pack."""

from __future__ import annotations

from pathlib import Path

from .ftaw_real_evidence_collection_checklist_pack import build_ftaw_real_evidence_collection_checklist_pack_from_files


def build_ftaw_real_evidence_collection_checklist_pack_report(
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
) -> str:
    pack = build_ftaw_real_evidence_collection_checklist_pack_from_files(
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
    )
    lines = [
        "J.A.R.V.I.S. FTAW Real Evidence Collection Checklist Pack Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"checklist status: {pack.checklist_status}",
        f"upstream real evidence intake readiness status: {pack.upstream_real_evidence_intake_readiness_status}",
        f"required evidence type count: {pack.required_evidence_type_count}",
        f"checklist item count: {pack.checklist_item_count}",
        f"public official item count: {pack.public_official_item_count}",
        f"private/manual item count: {pack.private_manual_item_count}",
        f"commit-safe public reference count: {pack.commit_safe_public_reference_count}",
        f"do-not-commit private evidence count: {pack.do_not_commit_private_evidence_count}",
        f"manual-only item count: {pack.manual_only_item_count}",
        "per-item table:",
        "evidence_type | source_category | public_or_private | commit_safety | required fields | manual action",
    ]
    for item in pack.checklist_items:
        lines.append(
            f"{item.evidence_type} | {item.source_category} | {item.public_or_private} | "
            f"{item.commit_safety} | {', '.join(item.required_source_fact_fields)} | "
            f"{item.manual_collection_instructions}"
        )
    lines.append("blocked reasons:")
    lines.extend(f"- {item}" for item in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            f"next manual action: {pack.next_manual_action}",
            f"evidence collected: {str(pack.evidence_collected).lower()}",
            f"evidence verified: {str(pack.evidence_verified).lower()}",
            f"queue eligibility created: {str(pack.queue_eligibility_created).lower()}",
            f"approved_asset: {str(pack.approved_asset).lower()}",
            f"registry_mutation: {str(pack.registry_mutation).lower()}",
            f"verified_evidence_promotion: {str(pack.verified_evidence_promotion).lower()}",
            f"private_file_auto_ingest: {str(pack.private_file_auto_ingest).lower()}",
            "collection checklist is not evidence verification.",
            "collection checklist is not asset approval.",
            "collection checklist is not registry mutation.",
            "collection checklist is not allocation advice.",
            "collection checklist is not a buy/sell request.",
            "collection checklist is not trade execution.",
            "private evidence must not be committed.",
            "no private file is auto-ingested.",
            "no evidence verified: true",
            "no verified evidence promotion: true",
            "no approvals created: true",
            "no registry mutation: true",
            "no allocation recommendations: true",
            "no buy/sell requests: true",
            "no trades executed: true",
            "no executor created: true",
            "no private file auto-ingest: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW real evidence collection checklist report.")
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
    args = parser.parse_args()
    print(
        build_ftaw_real_evidence_collection_checklist_pack_report(
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
        )
    )


if __name__ == "__main__":
    main()
