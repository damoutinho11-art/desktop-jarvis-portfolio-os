"""Markdown report for v4.67 public asset universe classifier."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_public_asset_universe_classifier import (
    PublicAssetUniverseClassifierResult,
    load_public_asset_universe_classifier_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_asset_universe_classifier.example.json")


def build_public_asset_universe_classifier_report(result: PublicAssetUniverseClassifierResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"classifier mode: {result.classifier_mode or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Classification Summary",
        f"- normalized record count: {result.normalized_record_count}",
        f"- classified record count: {result.classified_record_count}",
        "",
        "## Evidence Readiness Bucket Summary",
        f"- READY_FOR_RESEARCH_QUEUE: {result.ready_for_research_queue_count}",
        f"- NEEDS_MORE_PUBLIC_DATA: {result.needs_more_public_data_count}",
        f"- NEEDS_MANUAL_SOURCE_REVIEW: {result.needs_manual_source_review_count}",
        f"- BLOCKED_BY_MISSING_FIELDS: {result.blocked_by_missing_fields_count}",
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
        "- classified output remains unverified and unapproved",
        "",
        "## Sample Classified Records",
        "asset_id | asset_class | instrument_type | readiness | approval_status",
        "--- | --- | --- | --- | ---",
    ]
    if result.classified_records:
        for record in result.classified_records[:10]:
            lines.append(
                f"{record['asset_id']} | {record['asset_class']} | {record['instrument_type']} | "
                f"{record['evidence_readiness_bucket']} | {record['approval_status']}"
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
            "- v4.67 classifies normalized public asset records structurally.",
            "- classified records remain unverified, unapproved, unscreened, unscored, and unrecommended.",
            "",
            "## Where We Need To Go",
            "- next efficient stage is v4.68 Public Asset Universe Research Priority Queue.",
            "- research priority must remain separate from classification and must not be investment advice.",
            "",
            "## Do Not Build Next",
            "- screening inside v4.67",
            "- research scoring inside v4.67",
            "- evidence extraction",
            "- scheduler",
            "- investment recommendation",
            "- broker integration",
            "- registry mutation",
            "- executor",
            "",
            "## Redundancy Check",
            "- this is not a fetcher.",
            "- this is not a normalizer.",
            "- this is not screening, scoring, evidence verification, recommendation, approval, allocation, trading, or execution.",
            "",
            "## Next Efficient Action",
            f"- {result.next_safe_action or 'missing'}",
            "",
            "## v5.0 Research OS Target",
            "- public universe discovery -> source manifest -> explicit local cache -> cache audit -> normalization -> classification -> research queue -> evidence packs -> human dashboard -> external manual action.",
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
            "no screening",
            "no research scoring",
            "no ranking",
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
            "This report does not claim fetching, API calls, scraping, evidence verification, screening, research scoring, recommendation, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, candidate registry write, private ingest, broker integration, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_public_asset_universe_classifier_report(load_public_asset_universe_classifier_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the public asset universe classifier report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to classifier JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
