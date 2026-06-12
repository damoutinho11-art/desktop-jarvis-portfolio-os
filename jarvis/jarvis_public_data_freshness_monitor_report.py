"""Markdown report for the v4.58 public data freshness monitor."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_public_data_freshness_monitor import (
    PublicDataFreshnessMonitorResult,
    load_public_data_freshness_monitor_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_data_freshness_monitor.example.json")


def build_public_data_freshness_monitor_report(result: PublicDataFreshnessMonitorResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.overall_status}",
        f"monitor mode: {result.monitor_mode or 'missing'}",
        f"report only: {str(result.report_only).lower()}",
        f"no network: {str(result.no_network).lower()}",
        f"execute fetch: {str(result.execute_fetch).lower()}",
        f"current_date: {result.current_date}",
        f"source count: {result.source_count}",
        f"cache entry count: {result.cache_entry_count}",
        f"fresh count: {result.fresh_count}",
        f"stale count: {result.stale_count}",
        f"missing count: {result.missing_count}",
        f"manual policy count: {result.manual_policy_count}",
        f"failed count: {result.failed_count}",
        "",
        "This monitor is report-only: no network calls, no fetching, and no downloading occurred.",
        "Freshness is not verification.",
        "Raw cached data remains unverified until a separate manual evidence review pipeline.",
        "No evidence extraction occurred.",
        "Daily sources are fresh within 1 calendar day of current_date.",
        "Weekly sources are fresh within 7 calendar days of current_date.",
        "Manual sources require human policy/review and are not stale automatically.",
        "",
        "## Sources",
        "source_id | candidate_id | update_frequency | latest_fetched_at | freshness_status | next_safe_action",
        "--- | --- | --- | --- | --- | ---",
    ]
    for item in result.source_results:
        lines.append(
            f"{item.source_id} | {item.candidate_id or 'none'} | {item.update_frequency} | "
            f"{item.latest_fetched_at} | {item.freshness_status} | {item.next_safe_action}"
        )
    if not result.source_results:
        lines.append("none | none | none | none | none | fix_manifest_or_cache_metadata")
    lines.extend(["", "## Blocked Reasons"])
    lines.extend(f"- {reason}" for reason in result.blocked_reasons) if result.blocked_reasons else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.extend(
        [
            "",
            "## Route",
            "v4.56 manual candidate data entry workspace -> v4.57 public data fetcher local cache control plane -> v4.58 public data freshness monitor -> future manual source review/fact entry only if separately requested -> v4.27-v4.47 evidence/manual review pipeline",
            "",
            "## Safety Statements",
            "no fetching",
            "no downloading",
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
            "no buy/sell request",
            "no trade",
            "no executor",
            "no broker/authenticated API",
            "no credentials",
            "no private file ingest",
            "no automatic private data ingest",
            "no fetched data committed",
            "",
            "This report does not claim evidence verification, approval, trust, investability, allocation, buy/sell, trade, registry mutation, candidate registry write, broker API use, credential use, private ingest, automatic evidence extraction, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_public_data_freshness_monitor_report(load_public_data_freshness_monitor_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. public data freshness monitor report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to freshness monitor JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
