"""Markdown report for v5.1 public source fixture wiring."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_v5_1_public_source_fixture_wiring import (
    V51PublicSourceFixtureWiringResult,
    load_v5_1_public_source_fixture_wiring_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_v5_1_public_source_fixture_wiring.example.json")


def build_v5_1_public_source_fixture_wiring_report(result: V51PublicSourceFixtureWiringResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"fixture wiring mode: {result.fixture_wiring_mode or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Fixture Summary",
        f"- fixture count: {result.fixture_count}",
        f"- ready fixture count: {result.ready_fixture_count}",
        f"- missing fixture count: {result.missing_fixture_count}",
        f"- stale fixture count: {result.stale_fixture_count}",
        f"- manual refresh required count: {result.manual_refresh_required_count}",
        f"- invalid path count: {result.invalid_path_count}",
        f"- unsupported format count: {result.unsupported_format_count}",
        f"- unsafe fixture count: {result.unsafe_fixture_count}",
        f"- duplicate fixture id count: {result.duplicate_fixture_id_count}",
        "fixture id | category | format | status | path | mapped | blockers | warnings",
        "--- | --- | --- | --- | --- | --- | --- | ---",
    ]
    if result.fixture_rows:
        for row in result.fixture_rows:
            lines.append(
                f"{row['fixture_id']} | {row['source_category_id']} | {row['fixture_format']} | {row['fixture_status']} | "
                f"{row['expected_local_path']} | {row['mapped_to_pipeline']} | {row['blocker_count']} | {row['warning_count']}"
            )
    else:
        lines.append("none | none | none | none | none | false | 0 | 0")
    lines.extend(
        [
            "",
            "## Supported Format Summary",
            "- csv",
            "- json",
            "- txt",
            "- md",
            "- html_saved_public_page",
            "- pdf_public_document_reference_only",
            "- unknown",
            "",
            "## Pipeline Mapping Summary",
            f"- mapped to pipeline count: {result.mapped_to_pipeline_count}",
            f"- blocked mapping count: {result.blocked_mapping_count}",
            "fixture id | category | mapped | pipeline stages | blocked reason",
            "--- | --- | --- | --- | ---",
        ]
    )
    if result.pipeline_mapping_rows:
        for row in result.pipeline_mapping_rows:
            lines.append(
                f"{row['fixture_id']} | {row['source_category_id']} | {row['mapped']} | "
                f"{', '.join(row['pipeline_stages']) if row['pipeline_stages'] else 'none'} | {row['blocked_reason'] or 'none'}"
            )
    else:
        lines.append("none | none | false | none | none")
    lines.extend(
        [
            "",
            "## Operator Runbook Steps",
        ]
    )
    if result.operator_runbook_steps:
        lines.extend(f"{index}. {step}" for index, step in enumerate(result.operator_runbook_steps, start=1))
    else:
        lines.append("1. Review fixture wiring configuration before preparing local public source fixtures.")
    lines.extend(
        [
            "",
            "## Blockers / Warnings",
            "- blockers: " + (", ".join(result.blockers) if result.blockers else "none"),
            "- warnings: " + (", ".join(result.warnings) if result.warnings else "none"),
            "",
            "## Next Safe Operator Action",
            f"- {result.next_safe_action or 'missing'}",
            "",
            "## Do Not Build Next",
        ]
    )
    lines.extend(f"- {item}" for item in result.do_not_build_next)
    lines.extend(
        [
            "",
            "## Where We Are",
            "- v5.0 is sealed.",
            "- v5.1 wires local public-source fixture preparation for operator-managed files.",
            "- fixture presence is not evidence verification.",
            "",
            "## Where We Need To Go",
            "- prepare local public-source fixture metadata and run fixture import dry-runs before any downstream use.",
            "- suggested next phase is v5.2 Explicit-Authorization Public Fetch Adapter Stub or v5.2 Real Fixture Import Dry-Run.",
            "",
            "## Post-v5.0 Phase Statement",
            "- v5.1 is an operational runbook layer after the MVP seal.",
            "- it does not change the v5.0 verdict or add live fetching.",
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
            "no source parsing as verified evidence",
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
            "This report does not claim fetching, scraping, evidence verification, recommendation, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, broker integration, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_v5_1_public_source_fixture_wiring_report(load_v5_1_public_source_fixture_wiring_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the v5.1 public source fixture wiring report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to v5.1 fixture wiring JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
