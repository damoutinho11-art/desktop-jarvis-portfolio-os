"""Markdown report for v4.63 public asset universe fetch dry-run planner."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_public_asset_universe_fetch_dry_run_planner import (
    PublicAssetUniverseFetchDryRunResult,
    load_public_asset_universe_fetch_dry_run_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_asset_universe_fetch_dry_run_planner.example.json")


def _bool_text(value: object) -> str:
    return str(value is True).lower()


def build_public_asset_universe_fetch_dry_run_report(result: PublicAssetUniverseFetchDryRunResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"planner mode: {result.planner_mode or 'missing'}",
        f"report only: {_bool_text(result.report_only)}",
        f"dry-run only: {_bool_text(result.dry_run_only)}",
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
        "- public fetch dry-run planner comes before any universe cache builder.",
        "- v4.63 produces plans only; it does not fetch, download, scrape, call APIs, or write cache files.",
        "",
        "## Authorization Policy",
        f"- default_fetch_allowed: {str(result.authorization_policy.get('default_fetch_allowed')).lower()}",
        f"- future_fetch_allowed_only_with_explicit_authorization: {str(result.authorization_policy.get('future_fetch_allowed_only_with_explicit_authorization')).lower()}",
        f"- required authorization phrase: {result.required_authorization_phrase}",
        f"- authorization_phrase_present: {str(result.authorization_policy.get('authorization_phrase_present')).lower()}",
        f"- authorization_phrase_valid: {str(result.authorization_policy.get('authorization_phrase_valid')).lower()}",
        f"- even if authorized this stage still does not fetch: {str(result.authorization_policy.get('even_if_authorized_this_stage_still_does_not_fetch')).lower()}",
        "",
        "## Source Eligibility Summary",
        f"- source count: {result.source_count}",
        f"- eligible count: {result.eligible_count}",
        f"- manual reference only count: {result.manual_reference_only_count}",
        f"- blocked count: {result.blocked_count}",
        f"- no fetch executed: {str(result.no_fetch_executed).lower()}",
        f"- no cache written: {str(result.no_cache_written).lower()}",
        f"- no network called: {str(result.no_network_called).lower()}",
        "",
        "## Per-Source Dry-Run Plan Summary",
        "source | status | method | raw cache path | blockers",
        "--- | --- | --- | --- | ---",
    ]
    if result.source_plans:
        for plan in result.source_plans:
            blockers = "; ".join(plan.blockers) if plan.blockers else "none"
            lines.append(
                f"{plan.source_id} | {plan.eligibility_status} | {plan.allowed_future_fetch_method} | {plan.raw_cache_path} | {blockers}"
            )
    else:
        lines.append("none | none | none | none | none")
    lines.extend(["", "## Fetch Order"])
    lines.extend(f"- {source_id}" for source_id in result.fetch_order) if result.fetch_order else lines.append("- none")
    lines.extend(["", "## Planned Local Cache Paths", "### Raw Cache Paths"])
    lines.extend(f"- {path}" for path in result.planned_raw_cache_paths) if result.planned_raw_cache_paths else lines.append("- none")
    lines.extend(["", "### Metadata Paths"])
    lines.extend(f"- {path}" for path in result.planned_metadata_paths) if result.planned_metadata_paths else lines.append("- none")
    lines.extend(["", "### Fetch Plan Paths"])
    lines.extend(f"- {path}" for path in result.planned_fetch_plan_paths) if result.planned_fetch_plan_paths else lines.append("- none")
    lines.extend(["", "## Freshness Policy"])
    if result.freshness_policy:
        for key, value in sorted(result.freshness_policy.items()):
            lines.append(f"- {key}: {value}")
    else:
        lines.append("- none")
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.extend(
        [
            "",
            "## Where We Are",
            "- v4.61 defined public asset universe discovery planning.",
            "- v4.62 defined allowed public source manifest metadata.",
            "- v4.63 defines deterministic fetch dry-run plans before any cache builder.",
            "",
            "## Where We Need To Go",
            "- next efficient stage is v4.64 Public Asset Universe Local Cache Builder.",
            "- v4.64 may write ignored local cache only if separately implemented and explicitly authorized.",
            "",
            "## Do Not Build Next",
            "- actual fetcher in v4.63",
            "- scheduler",
            "- classifier",
            "- evidence extraction",
            "- broker integration",
            "- trading/executor",
            "",
            "## Redundancy Check",
            "- this is not another source manifest schema.",
            "- this is not a cache builder.",
            "- this is not a scheduler, classifier, evidence extractor, broker integration, or executor.",
            "",
            "## Next Efficient Action",
            f"- {result.next_safe_action or 'missing'}",
            "",
            "## v5.0 Research OS Target",
            "- local-first public research OS, not a trading bot.",
            "- public universe discovery -> source manifest -> fetch dry-run -> explicit local cache -> freshness -> normalization -> classification -> screening -> evidence packs -> human dashboard -> external manual action.",
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
    return build_public_asset_universe_fetch_dry_run_report(
        load_public_asset_universe_fetch_dry_run_result(path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the public asset universe fetch dry-run report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to fetch dry-run planner JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
