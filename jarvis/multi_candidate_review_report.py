"""Readable report for the multi-candidate review queue."""

from __future__ import annotations

from pathlib import Path

from .multi_candidate_review_queue import build_multi_candidate_review_queue_from_files


def build_multi_candidate_review_report(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    config_path: str | Path,
) -> str:
    queue = build_multi_candidate_review_queue_from_files(source_registry_path, reviewed_registry_copy_path, config_path)
    lines = [
        "J.A.R.V.I.S. Multi-Candidate Review Queue Report",
        "Read-only evidence queue. No approvals, allocations, orders, or registry mutation.",
        f"queue status: {queue.queue_status}",
        f"total candidates: {queue.summary.total_candidates}",
        f"already reviewed count: {queue.summary.already_reviewed_count}",
        f"ready for review count: {queue.summary.ready_for_review_count}",
        f"blocked count: {queue.summary.blocked_count}",
        f"needs evidence count: {queue.summary.needs_evidence_count}",
        f"needs freshness check count: {queue.summary.needs_freshness_check_count}",
        "top next evidence candidates:",
    ]
    if queue.top_next_evidence_candidates:
        lines.extend(
            (
                f"- {item.asset_id} ({item.sleeve}, {item.review_queue_status}, "
                f"evidence {item.evidence_completeness_score:.1f}%): {item.next_manual_action}"
            )
            for item in queue.top_next_evidence_candidates
        )
    else:
        lines.append("- none")
    lines.append("reviewed candidates:")
    if queue.reviewed_candidates:
        lines.extend(
            f"- {item.asset_id}: {item.current_status} -> {item.reviewed_status_if_private_copy or item.current_status}"
            for item in queue.reviewed_candidates
        )
    else:
        lines.append("- none")
    lines.append("blockers summary:")
    lines.extend(f"- {blocker}" for blocker in queue.blockers) if queue.blockers else lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in queue.warnings) if queue.warnings else lines.append("- none")
    lines.append("queue items:")
    for item in queue.items:
        lines.append(
            f"- {item.asset_id}: {item.review_queue_status}; current={item.current_status}; "
            f"private={item.reviewed_status_if_private_copy}; missing={', '.join(item.missing_evidence_types) or 'none'}; "
            f"stale={', '.join(item.stale_evidence_types) or 'none'}"
        )
    lines.extend(
        [
            f"no approved_investable: {str(queue.summary.approved_investable_count == 0).lower()}",
            "no allocation recommendation: true",
            "no buy/sell requests: true",
            "no trades executed: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build a multi-candidate review queue report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("config_path", nargs="?", default="jarvis/data/multi_candidate_review_queue.example.json")
    args = parser.parse_args()
    print(
        build_multi_candidate_review_report(
            args.source_registry_path,
            args.reviewed_registry_copy_path,
            args.config_path,
        )
    )


if __name__ == "__main__":
    main()
