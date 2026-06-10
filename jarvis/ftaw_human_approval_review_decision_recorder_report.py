"""Readable report for FTAW human approval review decisions."""

from __future__ import annotations

from pathlib import Path

from .ftaw_human_approval_review_decision_recorder import build_ftaw_human_approval_review_decision_pack_from_files


def build_ftaw_human_approval_review_decision_recorder_report(
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
) -> str:
    pack = build_ftaw_human_approval_review_decision_pack_from_files(
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
    )
    lines = [
        "J.A.R.V.I.S. FTAW Human Approval Review Decision Recorder Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"gate status: {pack.gate_status}",
        f"review packet created: {str(pack.review_packet_created).lower()}",
        f"human decision file used: {pack.human_decision_file_used}",
        f"human decision: {pack.human_decision or 'none'}",
        f"decision status: {pack.decision_status}",
        f"registry_update_dry_run_ready: {str(pack.registry_update_dry_run_ready).lower()}",
        f"rejected count: {pack.rejected_count}",
        f"needs_more_evidence count: {pack.needs_more_evidence_count}",
        f"pending decision count: {pack.pending_decision_count}",
        f"blocked reason count: {pack.blocked_reason_count}",
        "blocked reasons:",
    ]
    lines.extend(f"- {reason}" for reason in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            f"approved asset: {str(pack.approved_asset).lower()}",
            f"approval_status_change: {str(pack.approval_status_change).lower()}",
            "human approval review decision is not asset approval.",
            "human approval review decision is not registry mutation.",
            "human approval review decision is not verified evidence promotion.",
            "human approval review decision is not allocation advice.",
            "human approval review decision is not a buy/sell request.",
            "human approval review decision is not trade execution.",
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

    parser = argparse.ArgumentParser(description="Build FTAW human approval review decision recorder report.")
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
    args = parser.parse_args()
    print(
        build_ftaw_human_approval_review_decision_recorder_report(
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
        )
    )


if __name__ == "__main__":
    main()
