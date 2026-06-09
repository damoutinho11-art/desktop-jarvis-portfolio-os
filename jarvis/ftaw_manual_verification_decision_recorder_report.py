"""Readable report for FTAW manual verification decisions."""

from __future__ import annotations

from pathlib import Path

from .ftaw_manual_verification_decision_recorder import build_ftaw_manual_verification_decision_pack_from_files


def build_ftaw_manual_verification_decision_recorder_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
) -> str:
    pack = build_ftaw_manual_verification_decision_pack_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
    )
    lines = [
        "J.A.R.V.I.S. FTAW Manual Verification Decision Recorder Report",
        "Automated structure. Manual trust.",
        f"decision pack status: {pack.decision_pack_status}",
        f"target asset: {pack.target_asset}",
        f"queue config used: {pack.queue_config_used}",
        f"decision file used: {pack.decision_file_used}",
        f"total queue items: {pack.total_queue_items}",
        f"eligible queue items: {pack.eligible_queue_items}",
        f"accepted_for_verified_evidence_preview count: {pack.accepted_for_verified_evidence_preview_count}",
        f"rejected count: {pack.rejected_count}",
        f"needs_correction count: {pack.needs_correction_count}",
        f"pending_manual_decision count: {pack.pending_manual_decision_count}",
        f"blocked_unknown_queue_item count: {pack.blocked_unknown_queue_item_count}",
        f"blocked_non_eligible_queue_item count: {pack.blocked_non_eligible_queue_item_count}",
        f"blocked_invalid_manual_decision count: {pack.blocked_invalid_manual_decision_count}",
        "manual decision is not asset approval.",
        "manual decision is not registry mutation.",
        "manual decision is not allocation advice.",
        "manual decision is not a buy/sell request.",
        "manual decision is not trade execution.",
        "decision items:",
    ]
    if pack.decision_results:
        for result in pack.decision_results:
            decision = result.manual_decision or "none"
            lines.append(
                f"- {result.queue_item_id} | evidence_type: {result.evidence_type} | "
                f"source: {result.source_name} | queue_status: {result.queue_status} | "
                f"manual_decision: {decision} | decision_status: {result.decision_status} | "
                f"reason: {result.reason}"
            )
    else:
        lines.append("- none")
    lines.append("preview-ready item ids:")
    lines.extend(f"- {item_id}" for item_id in pack.preview_ready_item_ids) if pack.preview_ready_item_ids else lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in pack.blockers) if pack.blockers else lines.append("- none")
    lines.extend(
        [
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

    parser = argparse.ArgumentParser(description="Build FTAW manual verification decision recorder report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("url_fetch_config_path", nargs="?", default="jarvis/data/ftaw_public_url_fetch_adapter.example.json")
    parser.add_argument("fact_intake_config_path", nargs="?", default="jarvis/data/ftaw_source_fact_intake.example.json")
    parser.add_argument("identity_guard_config_path", nargs="?", default="jarvis/data/ftaw_source_identity_guard.example.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/ftaw_identity_guarded_verification_queue.example.json")
    parser.add_argument("decision_config_path", nargs="?", default="jarvis/data/ftaw_manual_verification_decision_recorder.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_manual_verification_decision_recorder_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.url_fetch_config_path,
            args.fact_intake_config_path,
            args.identity_guard_config_path,
            args.queue_config_path,
            args.decision_config_path,
        )
    )


if __name__ == "__main__":
    main()
