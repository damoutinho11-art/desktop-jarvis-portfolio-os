"""Readable report for FTAW real evidence intake readiness bridge."""

from __future__ import annotations

from pathlib import Path

from .ftaw_real_evidence_intake_readiness_bridge import build_ftaw_real_evidence_intake_readiness_bridge_from_files


def build_ftaw_real_evidence_intake_readiness_bridge_report(
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
) -> str:
    pack = build_ftaw_real_evidence_intake_readiness_bridge_from_files(
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
    )
    lines = [
        "J.A.R.V.I.S. FTAW Real Evidence Intake Readiness Bridge Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"real evidence intake readiness status: {pack.real_evidence_intake_readiness_status}",
        f"upstream audit status: {pack.upstream_audit_status}",
        f"final preflight ready: {str(pack.final_preflight_ready).lower()}",
        f"required real evidence types count: {pack.required_real_evidence_types_count}",
        "required real evidence types:",
    ]
    lines.extend(f"- {item}" for item in pack.required_real_evidence_types)
    lines.append("recommended source categories:")
    lines.extend(f"- {item}" for item in pack.recommended_source_categories)
    lines.append("private/manual evidence requirements:")
    lines.extend(f"- {item}" for item in pack.private_manual_evidence_requirements)
    lines.append("account-specific evidence requirements:")
    lines.extend(f"- {item}" for item in pack.account_specific_evidence_requirements)
    lines.append("manual-only evidence types:")
    lines.extend(f"- {item}" for item in pack.manual_only_evidence_types)
    lines.append("blocked reasons:")
    lines.extend(f"- {item}" for item in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            f"next manual action: {pack.next_manual_action}",
            f"real evidence collected: {str(pack.real_evidence_collected).lower()}",
            f"evidence verified: {str(pack.evidence_verified).lower()}",
            f"real evidence queue eligibility created: {str(pack.real_evidence_queue_eligibility_created).lower()}",
            f"approved_asset: {str(pack.approved_asset).lower()}",
            f"registry_mutation: {str(pack.registry_mutation).lower()}",
            f"verified_evidence_promotion: {str(pack.verified_evidence_promotion).lower()}",
            f"executor_created: {str(pack.executor_created).lower()}",
            "real evidence intake readiness is not asset approval.",
            "real evidence intake readiness is not verified evidence promotion.",
            "real evidence intake readiness is not registry mutation.",
            "real evidence intake readiness is not allocation advice.",
            "real evidence intake readiness is not a buy/sell request.",
            "real evidence intake readiness is not trade execution.",
            "real evidence intake planning does not ingest private files automatically.",
            "no verified evidence promotion: true",
            "no approvals created: true",
            "no registry mutation: true",
            "no allocation recommendations: true",
            "no buy/sell requests: true",
            "no trades executed: true",
            "no executor created: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW real evidence intake readiness bridge report.")
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
    args = parser.parse_args()
    print(
        build_ftaw_real_evidence_intake_readiness_bridge_report(
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
        )
    )


if __name__ == "__main__":
    main()
