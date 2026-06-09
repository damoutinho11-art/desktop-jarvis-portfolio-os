"""Readable report for FTAW verified evidence preview bridge."""

from __future__ import annotations

from pathlib import Path

from .ftaw_verified_evidence_preview_bridge import build_ftaw_verified_evidence_preview_bridge_from_files


def build_ftaw_verified_evidence_preview_bridge_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
    bridge_config_path: str | Path,
) -> str:
    pack = build_ftaw_verified_evidence_preview_bridge_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        bridge_config_path,
    )
    lines = [
        "J.A.R.V.I.S. FTAW Verified Evidence Preview Bridge Report",
        "Automated structure. Manual trust.",
        f"status: {pack.preview_bridge_status}",
        f"target asset: {pack.target_asset}",
        f"total queue items: {pack.total_queue_items}",
        f"eligible queue items: {pack.eligible_queue_items}",
        f"decision records count: {pack.decision_records_count}",
        f"preview_ready count: {pack.preview_ready_count}",
        f"excluded_rejected count: {pack.excluded_rejected_count}",
        f"excluded_needs_correction count: {pack.excluded_needs_correction_count}",
        f"pending_manual_decision count: {pack.pending_manual_decision_count}",
        f"blocked_invalid_manual_decision count: {pack.blocked_invalid_manual_decision_count}",
        f"blocked_unknown_queue_item count: {pack.blocked_unknown_queue_item_count}",
        f"blocked_non_eligible_queue_item count: {pack.blocked_non_eligible_queue_item_count}",
        "verified evidence preview is not verified evidence promotion.",
        "verified evidence preview is not asset approval.",
        "verified evidence preview is not registry mutation.",
        "verified evidence preview is not allocation advice.",
        "verified evidence preview is not a buy/sell request.",
        "verified evidence preview is not trade execution.",
        "preview items:",
    ]
    if pack.preview_records:
        for record in pack.preview_records:
            decision = record.manual_decision or "none"
            lines.append(
                f"- {record.asset_id} | evidence_type: {record.evidence_type} | "
                f"source: {record.source_name} | manual_decision: {decision} | "
                f"preview_status: {record.preview_status} | reason: {record.reason}"
            )
    else:
        lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in pack.blockers) if pack.blockers else lines.append("- none")
    lines.extend(
        [
            "no verified evidence promotion: true",
            "no approvals created: true",
            "no registry mutation: true",
            "no allocation recommendation: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW verified evidence preview bridge report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("url_fetch_config_path", nargs="?", default="jarvis/data/ftaw_public_url_fetch_adapter.example.json")
    parser.add_argument("fact_intake_config_path", nargs="?", default="jarvis/data/ftaw_source_fact_intake.example.json")
    parser.add_argument("identity_guard_config_path", nargs="?", default="jarvis/data/ftaw_source_identity_guard.example.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/ftaw_identity_guarded_verification_queue.example.json")
    parser.add_argument("decision_config_path", nargs="?", default="jarvis/data/ftaw_manual_verification_decision_recorder.example.json")
    parser.add_argument("bridge_config_path", nargs="?", default="jarvis/data/ftaw_verified_evidence_preview_bridge.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_verified_evidence_preview_bridge_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.url_fetch_config_path,
            args.fact_intake_config_path,
            args.identity_guard_config_path,
            args.queue_config_path,
            args.decision_config_path,
            args.bridge_config_path,
        )
    )


if __name__ == "__main__":
    main()
