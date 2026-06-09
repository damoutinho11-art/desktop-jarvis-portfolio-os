"""Readable report for FTAW identity-guarded verification queue."""

from __future__ import annotations

from pathlib import Path

from .ftaw_identity_guarded_verification_queue import build_ftaw_identity_guarded_verification_queue_from_files


def build_ftaw_identity_guarded_verification_queue_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
) -> str:
    queue = build_ftaw_identity_guarded_verification_queue_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
    )
    lines = [
        "J.A.R.V.I.S. FTAW Identity-Guarded Verification Queue Report",
        "Automated structure. Manual trust.",
        f"queue status: {queue.queue_status}",
        f"target asset: {queue.target_asset_id}",
        f"identity guard status: {queue.identity_guard_status}",
        f"identity guard passed: {str(queue.identity_guard_passed).lower()}",
        f"total input evidence/source-fact items: {queue.total_input_items}",
        f"queued count: {queue.queued_count}",
        f"eligible_for_manual_verification count: {queue.eligible_for_manual_verification_count}",
        f"needs_source_facts count: {queue.needs_source_facts_count}",
        f"needs_identity_confirmation count: {queue.needs_identity_confirmation_count}",
        f"blocked_source_identity_mismatch count: {queue.blocked_source_identity_mismatch_count}",
        f"manual_only_skipped count: {queue.manual_only_skipped_count}",
        "eligible_for_manual_verification is not approval.",
        "eligible_for_manual_verification is not verified evidence.",
        "eligible_for_manual_verification is not a buy signal.",
        "queue items:",
    ]
    if queue.items:
        for item in queue.items:
            source = item.source_name or "none"
            lines.append(f"- {item.evidence_type} | source: {source} | status: {item.queue_status} | reason: {item.reason}")
    else:
        lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in queue.warnings) if queue.warnings else lines.append("- none")
    lines.append("blockers:")
    lines.extend(f"- {blocker}" for blocker in queue.blockers) if queue.blockers else lines.append("- none")
    lines.extend(
        [
            "manual verification required: true",
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

    parser = argparse.ArgumentParser(description="Build FTAW identity-guarded verification queue report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("url_fetch_config_path", nargs="?", default="jarvis/data/ftaw_public_url_fetch_adapter.example.json")
    parser.add_argument("fact_intake_config_path", nargs="?", default="jarvis/data/ftaw_source_fact_intake.example.json")
    parser.add_argument("identity_guard_config_path", nargs="?", default="jarvis/data/ftaw_source_identity_guard.example.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/ftaw_identity_guarded_verification_queue.example.json")
    args = parser.parse_args()
    print(
        build_ftaw_identity_guarded_verification_queue_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.url_fetch_config_path,
            args.fact_intake_config_path,
            args.identity_guard_config_path,
            args.queue_config_path,
        )
    )


if __name__ == "__main__":
    main()
