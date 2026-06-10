"""Readable report for FTAW registry update dry-run pack."""

from __future__ import annotations

from pathlib import Path

from .ftaw_registry_update_dry_run_pack import build_ftaw_registry_update_dry_run_pack_from_files


def build_ftaw_registry_update_dry_run_pack_report(
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
) -> str:
    pack = build_ftaw_registry_update_dry_run_pack_from_files(
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
    )
    lines = [
        "J.A.R.V.I.S. FTAW Registry Update Dry-Run Pack Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"registry update dry-run status: {pack.registry_update_dry_run_status}",
        f"human decision status: {pack.human_decision_status}",
        f"registry_update_dry_run_ready: {str(pack.registry_update_dry_run_ready).lower()}",
        f"dry-run plan created: {str(pack.dry_run_plan_created).lower()}",
        f"current approval_status: {pack.current_approval_status or 'none'}",
        f"proposed approval_status: {pack.proposed_approval_status or 'none'}",
        f"registry_update_mode: {pack.registry_update_mode or 'none'}",
        f"registry_mutation: {str(pack.registry_mutation).lower()}",
        f"approved_asset: {str(pack.approved_asset).lower()}",
        f"buy_signal: {str(pack.buy_signal).lower()}",
        "blocked reasons:",
    ]
    lines.extend(f"- {reason}" for reason in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    if pack.dry_run_plan is not None:
        lines.extend(
            [
                "dry-run plan:",
                f"- asset_id: {pack.dry_run_plan.asset_id}",
                f"- evidence coverage summary: {pack.dry_run_plan.evidence_coverage_summary}",
                f"- human approval review decision reference: {pack.dry_run_plan.human_approval_review_decision_reference}",
                "promotion dry-run references:",
            ]
        )
        lines.extend(f"- {reference}" for reference in pack.dry_run_plan.promotion_dry_run_references)
    else:
        lines.extend(["dry-run plan:", "- none", "promotion dry-run references:", "- none"])
    lines.extend(
        [
            "registry update dry-run is not registry mutation.",
            "registry update dry-run is not asset approval.",
            "registry update dry-run is not verified evidence promotion.",
            "registry update dry-run is not allocation advice.",
            "registry update dry-run is not a buy/sell request.",
            "registry update dry-run is not trade execution.",
            "no verified evidence promotion: true",
            "no approvals created: true",
            "no registry mutation: true",
            "no allocation recommendations: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW registry update dry-run pack report.")
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
    args = parser.parse_args()
    print(
        build_ftaw_registry_update_dry_run_pack_report(
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
        )
    )


if __name__ == "__main__":
    main()
