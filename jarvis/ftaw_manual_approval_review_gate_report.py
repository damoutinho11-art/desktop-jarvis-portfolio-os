"""Readable report for FTAW manual approval review gate."""

from __future__ import annotations

from pathlib import Path

from .ftaw_manual_approval_review_gate import build_ftaw_manual_approval_review_gate_from_files


def build_ftaw_manual_approval_review_gate_report(
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
) -> str:
    pack = build_ftaw_manual_approval_review_gate_from_files(
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
    )
    lines = [
        "J.A.R.V.I.S. FTAW Manual Approval Review Gate Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"approval review gate status: {pack.approval_review_gate_status}",
        f"candidate readiness status: {pack.candidate_readiness_status}",
        f"ready for manual approval review: {str(pack.ready_for_manual_approval_review).lower()}",
        f"required evidence types count: {pack.required_evidence_types_count}",
        f"planned promotion evidence types count: {pack.planned_promotion_evidence_types_count}",
        f"missing evidence types count: {pack.missing_evidence_types_count}",
        "missing evidence types:",
    ]
    lines.extend(f"- {item}" for item in pack.missing_evidence_types) if pack.missing_evidence_types else lines.append("- none")
    lines.append("blocked reasons:")
    lines.extend(f"- {item}" for item in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            f"review packet created: {str(pack.review_packet_created).lower()}",
            f"next manual action: {pack.next_manual_action}",
        ]
    )
    if pack.review_packet is not None:
        lines.extend(
            [
                "review packet:",
                f"- asset_id: {pack.review_packet.asset_id}",
                f"- evidence coverage summary: {pack.review_packet.evidence_coverage_summary}",
                f"- approval_review_only: {str(pack.review_packet.approval_review_only).lower()}",
                f"- approved: {str(pack.review_packet.approved).lower()}",
                f"- approval_status_change: {str(pack.review_packet.approval_status_change).lower()}",
                f"- buy_signal: {str(pack.review_packet.buy_signal).lower()}",
                "dry-run promotion references:",
            ]
        )
        lines.extend(f"- {item}" for item in pack.review_packet.dry_run_promotion_references)
    else:
        lines.extend(["review packet:", "- none", "dry-run promotion references:", "- none"])
    lines.extend(
        [
            "approval review packet is not asset approval.",
            "approval review packet is not verified evidence promotion.",
            "approval review packet is not registry mutation.",
            "approval review packet is not allocation advice.",
            "approval review packet is not a buy/sell request.",
            "approval review packet is not trade execution.",
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

    parser = argparse.ArgumentParser(description="Build FTAW manual approval review gate report.")
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
    args = parser.parse_args()
    print(
        build_ftaw_manual_approval_review_gate_report(
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
        )
    )


if __name__ == "__main__":
    main()
