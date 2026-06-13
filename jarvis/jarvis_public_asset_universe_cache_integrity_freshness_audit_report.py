"""Markdown report for v4.65 public asset universe cache audit."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_public_asset_universe_cache_integrity_freshness_audit import (
    PublicAssetUniverseCacheAuditResult,
    load_public_asset_universe_cache_integrity_freshness_audit_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_asset_universe_cache_integrity_freshness_audit.example.json")


def build_public_asset_universe_cache_integrity_freshness_audit_report(
    result: PublicAssetUniverseCacheAuditResult,
) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"audit mode: {result.audit_mode or 'missing'}",
        "report only: true",
        "read only: true",
        "local cache only: true",
        "no network: true",
        "no fetching: true",
        "no writes: true",
        "",
        "## Coverage Summary",
        f"- coverage status: {result.coverage_status}",
        f"- expected source count: {result.coverage.expected_source_count}",
        f"- observed cache entry count: {result.coverage.observed_cache_entry_count}",
        f"- covered source count: {result.coverage.covered_source_count}",
        f"- missing source count: {result.coverage.missing_source_count}",
        f"- failed source count: {result.coverage.failed_source_count}",
        "",
        "## Freshness Summary",
        f"- fresh count: {result.fresh_count}",
        f"- stale count: {result.stale_count}",
        f"- missing count: {result.missing_count}",
        f"- manual review count: {result.manual_review_count}",
        "",
        "## Integrity Summary",
        f"- hash mismatch count: {result.hash_mismatch_count}",
        f"- unsafe metadata count: {result.unsafe_metadata_count}",
        f"- invalid path count: {result.invalid_path_count}",
        "",
        "## Per-Source Cache Audit Summary",
        "source | freshness | integrity | fetched_at | blockers",
        "--- | --- | --- | --- | ---",
    ]
    if result.per_source_results:
        for item in result.per_source_results:
            blockers = "; ".join(item.blockers) if item.blockers else "none"
            lines.append(
                f"{item.source_id} | {item.freshness_status} | {item.integrity_status} | {item.fetched_at or 'none'} | {blockers}"
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
            "- v4.65 audits cache integrity and freshness after v4.64.",
            "- it reads explicit input JSON and explicit file-backed paths only.",
            "",
            "## Where We Need To Go",
            "- fix stale, missing, failed, mismatched, or unsafe cache entries before normalization.",
            "- proceed to a public asset universe normalizer only after cache audit is stable.",
            "",
            "## Do Not Build Next",
            "- classifier inside v4.65",
            "- normalizer inside v4.65",
            "- evidence extraction",
            "- scheduler",
            "- investment screening",
            "- broker integration",
            "- registry mutation",
            "- executor",
            "",
            "## Redundancy Check",
            "- this is not a fetcher.",
            "- this is not a cache repair tool.",
            "- this is not a normalizer, classifier, screener, evidence verifier, approval layer, broker integration, or executor.",
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
            "no writes",
            "no cache mutation",
            "no cache repair",
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
            "no normalization",
            "no classification",
            "no screening",
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
            "This report does not claim fetching, API calls, scraping, writing, cache repair, cache mutation, scheduling, broker integration, Lightyear integration, LHV integration, crypto exchange integration, credential use, evidence verification, normalization, classification, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, candidate registry write, private ingest, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_public_asset_universe_cache_integrity_freshness_audit_report(
        load_public_asset_universe_cache_integrity_freshness_audit_result(path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the public asset universe cache integrity and freshness audit.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to cache audit JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
