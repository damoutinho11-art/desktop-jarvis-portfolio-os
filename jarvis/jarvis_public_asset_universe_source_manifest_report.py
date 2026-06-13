"""Markdown report for v4.62 public asset universe source manifest schema."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_public_asset_universe_source_manifest import (
    PublicAssetUniverseSourceManifestResult,
    load_public_asset_universe_source_manifest_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_asset_universe_source_manifest.example.json")


def _bool_text(value: object) -> str:
    return str(value is True).lower()


def build_public_asset_universe_source_manifest_report(result: PublicAssetUniverseSourceManifestResult) -> str:
    cache_paths = result.local_cache_policy.get("planned_paths", [])
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.overall_status}",
        f"manifest mode: {result.manifest_mode or 'missing'}",
        f"report only: {_bool_text(result.report_only)}",
        f"no network: {_bool_text(result.no_network)}",
        f"no fetching: {_bool_text(result.no_fetching)}",
        f"no downloading: {_bool_text(result.no_downloading)}",
        f"no scraping: {_bool_text(result.no_scraping)}",
        f"no API calls: {_bool_text(result.no_api_calls)}",
        f"no writes: {_bool_text(result.no_writes)}",
        f"no cache creation: {_bool_text(result.no_cache_creation)}",
        f"no subprocess: {_bool_text(result.no_subprocess)}",
        f"no scheduler creation: {_bool_text(result.no_scheduler_creation)}",
        f"no broker integration: {_bool_text(result.no_broker_integration)}",
        "",
        "## Strategic Correction",
        "- no manual one-by-one asset entry as primary workflow.",
        "- public source manifest is required before universe fetch/cache.",
        "- v4.62 defines source metadata only; it does not fetch, download, scrape, call APIs, or write cache files.",
        "",
        "## Required Source Categories",
        "source category | supported universes | expected fields",
        "--- | --- | ---",
    ]
    if result.source_categories:
        for category in result.source_categories:
            lines.append(
                f"{category.source_category_id} | {', '.join(category.supported_asset_universes)} | {', '.join(category.expected_fields)}"
            )
    else:
        lines.append("none | none | none")
    lines.extend(["", "## Source Entries Summary", "source | category | universes | type | future fetch method", "--- | --- | --- | --- | ---"])
    if result.sources:
        for source in result.sources:
            lines.append(
                f"{source.source_id} | {source.source_category_id} | {', '.join(source.target_asset_universes)} | {source.source_type} | {source.allowed_future_fetch_method}"
            )
    else:
        lines.append("none | none | none | none | none")
    lines.extend(["", "## Covered Asset Universes"])
    lines.extend(f"- {universe}" for universe in result.covered_asset_universe_ids) if result.covered_asset_universe_ids else lines.append("- none")
    lines.extend(
        [
            "",
            "## Future Fetch Policy",
            f"- default_fetch_allowed: {str(result.future_fetch_policy.get('default_fetch_allowed')).lower()}",
            f"- future_fetch_allowed_only_with_explicit_authorization: {str(result.future_fetch_policy.get('future_fetch_allowed_only_with_explicit_authorization')).lower()}",
            f"- required authorization phrase: {result.future_fetch_policy.get('required_authorization_phrase', 'missing')}",
            f"- local_cache_only: {str(result.future_fetch_policy.get('local_cache_only')).lower()}",
            f"- fetched_data_unverified: {str(result.future_fetch_policy.get('fetched_data_unverified')).lower()}",
            f"- no_fetched_data_committed: {str(result.future_fetch_policy.get('no_fetched_data_committed')).lower()}",
            "",
            "## Local Cache Policy",
            "- v4.62 creates no cache.",
            "- future cache must remain ignored and uncommitted.",
            "- raw data remains unverified.",
            "- normalized data remains unapproved.",
        ]
    )
    for path in cache_paths if isinstance(cache_paths, list) else []:
        lines.append(f"- planned path only: {path}")
    lines.extend(["", "## Identifier Policy"])
    for key, value in sorted(result.identifier_policy.items()):
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## URL/Credential Safety Summary",
            "- source URLs must be http or https.",
            "- file, localhost, credential-looking query parameters, broker/private endpoints, Lightyear/LHV source entries, login/account/wallet/trading endpoints are blocked.",
            "- public_api_reference_only is a reference type only; v4.62 does not allow API calls.",
            "",
            "## Where We Are",
            "- v4.61 defined public asset universe discovery planning.",
            "- v4.62 defines the public source manifest schema before any fetch/cache stage.",
            "",
            "## Where We Need To Go",
            "- next efficient stage is v4.63 Public Asset Universe Fetch Dry-Run Planner.",
            "- future fetch requires explicit authorization and local-cache-only behavior.",
            "",
            "## Do Not Build Next",
        ]
    )
    lines.extend(f"- {item}" for item in result.redundant_next_steps_to_avoid) if result.redundant_next_steps_to_avoid else lines.append("- universe_fetcher_in_v4_62")
    lines.extend(
        [
            "",
            "## Redundancy Check",
            "- do not build another gate or manual one-candidate workflow as the main path.",
            "- do not build a scheduler, classifier, evidence extractor, broker integration, trading flow, or executor in v4.62.",
            "",
            "## Next Efficient Action",
            f"- {result.next_manual_action or 'missing'}",
            "",
            "## v5.0 Research OS Target",
            "- local-first public research OS, not a trading bot.",
            "- public universe discovery -> source manifest -> explicit local-cache fetch -> freshness -> normalization -> classification -> screening -> evidence packs -> human dashboard -> external manual action.",
            "",
            "## Blocked Reasons",
        ]
    )
    lines.extend(f"- {reason}" for reason in result.blocked_reasons) if result.blocked_reasons else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.extend(
        [
            "",
            "## Safety Statements",
            "no network calls",
            "no fetching",
            "no downloading",
            "no scraping",
            "no API calls",
            "no writes",
            "no cache creation",
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
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no registry mutation",
            "no registry file written",
            "no candidate registry write",
            "no candidate intake file written",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell signal",
            "no trade",
            "no executor",
            "final real-world purchases remain manual and external",
            "",
            "This report does not claim fetching, API calls, scraping, writing, cache creation, scheduling, broker integration, Lightyear integration, LHV integration, crypto exchange integration, credential use, evidence verification, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, candidate registry write, private ingest, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_public_asset_universe_source_manifest_report(
        load_public_asset_universe_source_manifest_result(path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the public asset universe source manifest report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to source manifest JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
