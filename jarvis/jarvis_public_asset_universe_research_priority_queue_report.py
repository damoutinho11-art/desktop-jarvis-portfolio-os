"""Markdown report for v4.68 public asset universe research priority queue."""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from .jarvis_public_asset_universe_research_priority_queue import (
    PublicAssetUniverseResearchPriorityQueueResult,
    load_public_asset_universe_research_priority_queue_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_asset_universe_research_priority_queue.example.json")


def build_public_asset_universe_research_priority_queue_report(result: PublicAssetUniverseResearchPriorityQueueResult) -> str:
    next_steps = Counter(item["suggested_next_research_step"] for item in result.queue_items)
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"queue mode: {result.queue_mode or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Queue Summary",
        f"- classified record count: {result.classified_record_count}",
        f"- queue item count: {result.queue_item_count}",
        "",
        "## Priority Bucket Summary",
        f"- RESEARCH_QUEUE_HIGH_READY: {result.high_ready_count}",
        f"- RESEARCH_QUEUE_MEDIUM_READY: {result.medium_ready_count}",
        f"- RESEARCH_QUEUE_LOW_READY: {result.low_ready_count}",
        f"- RESEARCH_QUEUE_NEEDS_MORE_PUBLIC_DATA: {result.needs_more_public_data_count}",
        f"- RESEARCH_QUEUE_NEEDS_MANUAL_SOURCE_REVIEW: {result.needs_manual_source_review_count}",
        f"- RESEARCH_QUEUE_BLOCKED_SAFE: {result.blocked_safe_count}",
        "",
        "## Suggested Next Research Step Summary",
    ]
    if next_steps:
        for step in sorted(next_steps):
            lines.append(f"- {step}: {next_steps[step]}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Skipped / Blocked Record Summary",
            f"- skipped record count: {result.skipped_record_count}",
            f"- blocked record count: {result.blocked_record_count}",
            "- skipped records: " + (", ".join(result.skipped_records) if result.skipped_records else "none"),
            "- blocked records: " + (", ".join(result.blocked_records) if result.blocked_records else "none"),
            "",
            "## Duplicate Asset ID Summary",
            f"- duplicate asset id count: {result.duplicate_asset_id_count}",
            "",
            "## Output / Write Authorization Summary",
            "- default write allowed: false",
            "- report writes files: false",
            "- optional write requires exact authorization phrase",
            "- queue output remains unverified and unapproved",
            "",
            "## Sample Queue Items",
            "queue_id | asset_id | priority | next step | approval_status",
            "--- | --- | --- | --- | ---",
        ]
    )
    if result.queue_items:
        for item in result.queue_items[:10]:
            lines.append(
                f"{item['queue_id']} | {item['asset_id']} | {item['research_priority_bucket']} | "
                f"{item['suggested_next_research_step']} | {item['approval_status']}"
            )
    else:
        lines.append("none | none | none | none | none")
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.extend(
        [
            "",
            "## Where We Are",
            "- v4.68 builds a research workflow priority queue from classified public asset records.",
            "- queue priority is workflow readiness only, not investment merit.",
            "",
            "## Where We Need To Go",
            "- next efficient stage is v4.69 Public Evidence Pack Draft Generator.",
            "- evidence pack drafting must remain separate from evidence verification and recommendation.",
            "",
            "## Do Not Build Next",
            "- investment screening inside v4.68",
            "- research scoring based on returns inside v4.68",
            "- recommendation",
            "- evidence extraction",
            "- scheduler",
            "- broker integration",
            "- registry mutation",
            "- executor",
            "",
            "## Redundancy Check",
            "- this is not classification.",
            "- this is not screening, scoring, evidence verification, recommendation, approval, allocation, trading, or execution.",
            "",
            "## Next Efficient Action",
            f"- {result.next_safe_action or 'missing'}",
            "",
            "## v5.0 Research OS Target",
            "- public universe discovery -> source manifest -> local cache -> cache audit -> normalization -> classification -> research queue -> evidence packs -> human dashboard -> external manual action.",
            "",
            "## Safety Statements",
            "no network calls",
            "no fetching",
            "no downloading",
            "no scraping",
            "no API calls",
            "no browser automation",
            "no subprocess execution",
            "no scheduler creation",
            "no broker integration",
            "no Lightyear integration",
            "no LHV integration",
            "no crypto exchange integration",
            "no credentials",
            "no private/account data ingest",
            "no evidence extraction",
            "no evidence verification",
            "no verified evidence promotion",
            "no investment screening",
            "no research scoring based on expected returns",
            "no ranking by investment merit",
            "no recommendation",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no registry mutation",
            "no candidate registry write",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell signal",
            "no trade",
            "no executor",
            "final real-world purchases remain manual and external",
            "",
            "This report does not claim evidence verification, recommendation, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, candidate registry write, private ingest, broker integration, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_public_asset_universe_research_priority_queue_report(load_public_asset_universe_research_priority_queue_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the public asset universe research priority queue report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to research priority queue JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
