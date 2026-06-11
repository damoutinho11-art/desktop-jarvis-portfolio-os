"""Readable report for FTAW manual source fact entry pack."""

from __future__ import annotations

from pathlib import Path

from .ftaw_manual_source_fact_entry_pack import build_ftaw_manual_source_fact_entry_pack_from_files


def build_ftaw_manual_source_fact_entry_pack_report(
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
) -> str:
    pack = build_ftaw_manual_source_fact_entry_pack_from_files(
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
    )
    lines = [
        "J.A.R.V.I.S. FTAW Manual Source Fact Entry Pack Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"source fact entry status: {pack.source_fact_entry_status}",
        f"upstream manual public source reference recorder status: {pack.upstream_manual_public_source_reference_recorder_status}",
        f"public references recorded count: {pack.public_references_recorded_count}",
        f"manual source fact entries provided count: {pack.manual_source_fact_entries_provided_count}",
        f"accepted source fact record count: {pack.accepted_source_fact_record_count}",
        f"required public fact record count: {pack.required_public_fact_record_count}",
        f"missing public fact record count: {pack.missing_public_fact_record_count}",
        f"missing required field count: {pack.missing_required_field_count}",
        f"rejected entry count: {pack.rejected_entry_count}",
        f"manual/private outstanding count: {pack.manual_private_outstanding_count}",
        "accepted source fact records:",
        "evidence_type | source_reference_id | required fields present | required fields missing | manual_entry | auto_extracted | fetched | downloaded | parsed | verified | identity_guard_pass_created | queue_eligibility_created | manual action",
    ]
    if pack.accepted_source_fact_records:
        for record in pack.accepted_source_fact_records:
            lines.append(
                f"{record.evidence_type} | {record.source_reference_id} | {', '.join(record.required_fields_present) or 'none'} | "
                f"{', '.join(record.required_fields_missing) or 'none'} | {str(record.manual_entry).lower()} | "
                f"{str(record.auto_extracted).lower()} | {str(record.fetched).lower()} | {str(record.downloaded).lower()} | "
                f"{str(record.parsed).lower()} | {str(record.verified).lower()} | "
                f"{str(record.identity_guard_pass_created).lower()} | {str(record.queue_eligibility_created).lower()} | "
                f"{record.manual_action}"
            )
    else:
        lines.append("none")
    lines.extend(["rejected entry table:", "evidence_type | source_reference_id | reason"])
    if pack.rejected_entries:
        for entry in pack.rejected_entries:
            lines.append(f"{entry.evidence_type} | {entry.source_reference_id} | {entry.reason}")
    else:
        lines.append("none")
    lines.extend(["manual/private outstanding table:", "evidence_type | reason | next manual action"])
    for item in pack.manual_private_outstanding:
        lines.append(f"{item.evidence_type} | {item.reason} | {item.next_manual_action}")
    lines.append("blocked reasons:")
    lines.extend(f"- {item}" for item in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            f"next manual action: {pack.next_manual_action}",
            f"automatic_fact_extraction: {str(pack.automatic_fact_extraction).lower()}",
            f"evidence_verified: {str(pack.evidence_verified).lower()}",
            f"identity_guard_pass_records_created: {str(pack.identity_guard_pass_records_created).lower()}",
            f"queue_eligibility_created: {str(pack.queue_eligibility_created).lower()}",
            f"approved_asset: {str(pack.approved_asset).lower()}",
            f"registry_mutation: {str(pack.registry_mutation).lower()}",
            "manual source fact entry is not automatic extraction.",
            "manual source fact entry is not evidence verification.",
            "manual source fact entry is not identity guard approval.",
            "manual source fact entry is not queue eligibility.",
            "manual source fact entry is not asset approval.",
            "manual source fact entry is not registry mutation.",
            "manual source fact entry is not allocation advice.",
            "manual source fact entry is not a buy/sell request.",
            "manual source fact entry is not trade execution.",
            "source references are not fetched or downloaded automatically.",
            "private evidence must not be committed.",
            "no automatic source fetching: true",
            "no automatic downloads: true",
            "no automatic fact extraction: true",
            "no evidence verified: true",
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
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW manual source fact entry report.")
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
    args = parser.parse_args()
    print(
        build_ftaw_manual_source_fact_entry_pack_report(
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
        )
    )


if __name__ == "__main__":
    main()
