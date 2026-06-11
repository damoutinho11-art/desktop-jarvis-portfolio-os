"""Readable report for FTAW manual public source reference entry recorder."""

from __future__ import annotations

from pathlib import Path

from .ftaw_manual_public_source_reference_entry_recorder import (
    build_ftaw_manual_public_source_reference_entry_recorder_from_files,
)


def build_ftaw_manual_public_source_reference_entry_recorder_report(
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
) -> str:
    pack = build_ftaw_manual_public_source_reference_entry_recorder_from_files(
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
    )
    lines = [
        "J.A.R.V.I.S. FTAW Manual Public Source Reference Entry Recorder Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"recorder status: {pack.recorder_status}",
        f"upstream public source reference plan status: {pack.upstream_public_source_reference_plan_status}",
        f"manual public reference entries provided count: {pack.manual_public_reference_entries_provided_count}",
        f"public references recorded count: {pack.public_references_recorded_count}",
        f"required public reference count: {pack.required_public_reference_count}",
        f"missing public reference count: {pack.missing_public_reference_count}",
        f"manual/private outstanding count: {pack.manual_private_outstanding_count}",
        f"skipped/rejected entry count: {pack.skipped_rejected_entry_count}",
        "recorded public reference table:",
        "evidence_type | source_reference_id | source_category | manual_reference | manual_entry | fetched | downloaded | parsed | facts_extracted | collected | verified | manual action",
    ]
    if pack.recorded_references:
        for record in pack.recorded_references:
            lines.append(
                f"{record.evidence_type} | {record.source_reference_id} | {record.source_category} | "
                f"{record.manual_reference} | {str(record.manual_entry).lower()} | {str(record.fetched).lower()} | "
                f"{str(record.downloaded).lower()} | {str(record.parsed).lower()} | "
                f"{str(record.facts_extracted).lower()} | {str(record.collected).lower()} | "
                f"{str(record.verified).lower()} | {record.manual_action}"
            )
    else:
        lines.append("none")
    lines.extend(["manual/private outstanding table:", "evidence_type | reason | next manual action"])
    for item in pack.manual_private_outstanding:
        lines.append(f"{item.evidence_type} | {item.reason} | {item.next_manual_action}")
    lines.append("blocked reasons:")
    lines.extend(f"- {item}" for item in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.append("rejected reasons:")
    lines.extend(f"- {item}" for item in pack.rejected_reasons) if pack.rejected_reasons else lines.append("- none")
    lines.extend(
        [
            f"next manual action: {pack.next_manual_action}",
            f"source fact intake records created: {str(pack.source_fact_intake_records_created).lower()}",
            f"identity guard pass records created: {str(pack.identity_guard_pass_records_created).lower()}",
            f"queue eligibility created: {str(pack.queue_eligibility_created).lower()}",
            f"approved_asset: {str(pack.approved_asset).lower()}",
            f"registry_mutation: {str(pack.registry_mutation).lower()}",
            f"verified_evidence_promotion: {str(pack.verified_evidence_promotion).lower()}",
            f"automatic_source_fetching: {str(pack.automatic_source_fetching).lower()}",
            f"automatic_downloads: {str(pack.automatic_downloads).lower()}",
            "manual source reference entry is not evidence collection.",
            "manual source reference entry is not evidence verification.",
            "manual source reference entry is not source fact extraction.",
            "manual source reference entry is not asset approval.",
            "manual source reference entry is not registry mutation.",
            "manual source reference entry is not allocation advice.",
            "manual source reference entry is not a buy/sell request.",
            "manual source reference entry is not trade execution.",
            "source references are not fetched or downloaded automatically.",
            "private evidence must not be committed.",
            "no evidence collected: true",
            "no evidence verified: true",
            "no source facts extracted: true",
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
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW manual public source reference entry recorder report.")
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
    args = parser.parse_args()
    print(
        build_ftaw_manual_public_source_reference_entry_recorder_report(
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
        )
    )


if __name__ == "__main__":
    main()
