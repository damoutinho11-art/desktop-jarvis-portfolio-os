"""Markdown report for v4.66 public asset universe normalizer."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_public_asset_universe_normalizer import (
    PublicAssetUniverseNormalizerResult,
    load_public_asset_universe_normalizer_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_asset_universe_normalizer.example.json")


def build_public_asset_universe_normalizer_report(result: PublicAssetUniverseNormalizerResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"normalizer mode: {result.normalizer_mode or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Normalized Record Summary",
        f"- source count: {result.source_count}",
        f"- raw record count: {result.raw_record_count}",
        f"- normalized record count: {result.normalized_record_count}",
        "",
        "## Skipped / Blocked Input Summary",
        f"- skipped input count: {result.skipped_input_count}",
        f"- blocked input count: {result.blocked_input_count}",
        "- skipped inputs: " + (", ".join(result.skipped_inputs) if result.skipped_inputs else "none"),
        "- blocked inputs: " + (", ".join(result.blocked_inputs) if result.blocked_inputs else "none"),
        "",
        "## Duplicate Asset ID Summary",
        f"- duplicate asset id count: {result.duplicate_asset_id_count}",
        "",
        "## Output / Write Authorization Summary",
        "- default write allowed: false",
        "- report writes files: false",
        "- optional write requires exact authorization phrase",
        "- normalized output remains unverified and unapproved",
        "",
        "## Sample Normalized Records",
        "asset_id | type | symbol | status",
        "--- | --- | --- | ---",
    ]
    if result.normalized_records:
        for record in result.normalized_records[:10]:
            lines.append(
                f"{record['asset_id']} | {record['asset_type']} | {record['symbol_or_identifier']} | {record['approval_status']}"
            )
    else:
        lines.append("none | none | none | none")
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.extend(
        [
            "",
            "## Where We Are",
            "- v4.66 normalizes audited public cache data into structural public asset records.",
            "- normalized records remain unverified, unapproved, unclassified, and unscreened.",
            "",
            "## Where We Need To Go",
            "- next efficient stage is v4.67 Public Asset Universe Classifier.",
            "- classification must remain separate from normalization.",
            "",
            "## Do Not Build Next",
            "- classifier inside v4.66",
            "- screening inside v4.66",
            "- evidence extraction",
            "- scheduler",
            "- investment recommendation",
            "- broker integration",
            "- registry mutation",
            "- executor",
            "",
            "## Redundancy Check",
            "- this is not a fetcher.",
            "- this is not a cache audit.",
            "- this is not classification, screening, evidence verification, approval, allocation, trading, or execution.",
            "",
            "## Next Efficient Action",
            f"- {result.next_safe_action or 'missing'}",
            "",
            "## v5.0 Research OS Target",
            "- public universe discovery -> source manifest -> explicit local cache -> cache audit -> normalization -> classification -> screening -> evidence packs -> human dashboard -> external manual action.",
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
            "no classification",
            "no screening",
            "no research scoring",
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
            "This report does not claim fetching, API calls, scraping, evidence verification, classification, screening, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, candidate registry write, private ingest, broker integration, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_public_asset_universe_normalizer_report(load_public_asset_universe_normalizer_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the public asset universe normalizer report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to normalizer JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
