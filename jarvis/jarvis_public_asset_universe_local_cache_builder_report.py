"""Markdown report for v4.64 public asset universe local cache builder."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_public_asset_universe_local_cache_builder import (
    PublicAssetUniverseLocalCacheBuilderResult,
    load_public_asset_universe_local_cache_builder_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_asset_universe_local_cache_builder.example.json")


def _bool_text(value: object) -> str:
    return str(value is True).lower()


def build_public_asset_universe_local_cache_builder_report(
    result: PublicAssetUniverseLocalCacheBuilderResult,
) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"builder mode: {result.builder_mode or 'missing'}",
        f"report only: {_bool_text(result.report_only)}",
        f"default no fetch: {_bool_text(result.default_no_fetch)}",
        f"default no write: {_bool_text(result.default_no_write)}",
        f"authorization status: {result.authorization_status}",
        "",
        "## Default-Off Summary",
        "- default no network calls",
        "- default no fetching",
        "- default no downloading",
        "- default no writes",
        "- authorized path is local-cache-only and writes raw unverified public data only.",
        "",
        "## Source Plan Summary",
        f"- source count: {result.source_count}",
        f"- fetched count: {result.fetched_count}",
        f"- skipped count: {result.skipped_count}",
        f"- blocked count: {result.blocked_count}",
        f"- failed count: {result.failed_count}",
        "",
        "## Source Plans",
        "source | status | method | raw cache path | metadata path",
        "--- | --- | --- | --- | ---",
    ]
    if result.source_plans:
        for plan in result.source_plans:
            lines.append(
                f"{plan.source_id} | {plan.eligibility_status} | {plan.allowed_future_fetch_method} | {plan.raw_cache_path} | {plan.metadata_path}"
            )
    else:
        lines.append("none | none | none | none | none")
    lines.extend(["", "## Planned vs Written Path Summary", "### Written Raw Cache Paths"])
    lines.extend(f"- {path}" for path in result.written_raw_cache_paths) if result.written_raw_cache_paths else lines.append("- none")
    lines.extend(["", "### Written Metadata Paths"])
    lines.extend(f"- {path}" for path in result.written_metadata_paths) if result.written_metadata_paths else lines.append("- none")
    lines.extend(["", "## Skipped / Manual Reference Sources"])
    lines.extend(f"- {source}" for source in result.skipped_sources) if result.skipped_sources else lines.append("- none")
    lines.extend(["", "## Blocked Sources"])
    lines.extend(f"- {source}" for source in result.blocked_sources) if result.blocked_sources else lines.append("- none")
    lines.extend(["", "## Failed Sources"])
    lines.extend(f"- {source}" for source in result.failed_sources) if result.failed_sources else lines.append("- none")
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")
    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")
    lines.extend(
        [
            "",
            "## Where We Are",
            "- v4.64 is the first controlled local-cache builder for public asset universe sources.",
            "- evaluation/report mode is still no-fetch and no-write.",
            "",
            "## Where We Need To Go",
            "- use only exact explicit authorization before any local-cache build.",
            "- keep cached raw public data ignored and uncommitted.",
            "",
            "## Do Not Build Next",
            "- classifier inside v4.64",
            "- evidence extraction",
            "- scheduler",
            "- investment screening",
            "- broker integration",
            "- registry mutation",
            "- executor",
            "",
            "## Redundancy Check",
            "- this is not a source manifest.",
            "- this is not an evidence verifier.",
            "- this is not an approval, allocation, trading, or execution layer.",
            "",
            "## Next Efficient Action",
            "- v4.65 Public Asset Universe Cache Freshness + Integrity Audit, or Public Asset Universe Normalizer after the cache builder is stable.",
            "",
            "## v5.0 Research OS Target",
            "- public universe discovery -> source manifest -> fetch dry-run -> explicit local cache -> freshness -> normalization -> classification -> screening -> evidence packs -> human dashboard -> external manual action.",
            "",
            "## Safety Statements",
            "default no network calls",
            "default no fetching",
            "default no downloading",
            "default no writes",
            "authorized path local-cache-only",
            "no scraping",
            "no API calls without explicit authorization",
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
            "no candidate registry write",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell signal",
            "no trade",
            "no executor",
            "final real-world purchases remain manual and external",
            "",
            "This report does not execute fetching or writing. It does not claim evidence verification, approval, trust, investability, allocation, portfolio construction, buy/sell signal, trade, registry mutation, candidate write, broker integration, credential use, private ingest, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_public_asset_universe_local_cache_builder_report(
        load_public_asset_universe_local_cache_builder_result(path)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the public asset universe local cache builder report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to local cache builder JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
