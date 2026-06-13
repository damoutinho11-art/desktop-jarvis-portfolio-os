"""Markdown report for v4.70 public research operator dashboard."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_public_research_operator_dashboard import (
    PublicResearchOperatorDashboardResult,
    load_public_research_operator_dashboard_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_public_research_operator_dashboard.example.json")


def build_public_research_operator_dashboard_report(result: PublicResearchOperatorDashboardResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"dashboard mode: {result.dashboard_mode or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Public Universe Pipeline Stage Table",
        "stage id | stage name | version | status | readiness | item count | blockers | warnings | safety",
        "--- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    if result.stage_rows:
        for row in result.stage_rows:
            lines.append(
                f"{row['stage_id']} | {row['stage_name']} | {row['version']} | {row['status']} | "
                f"{row['readiness']} | {row['item_count']} | {row['blocker_count']} | {row['warning_count']} | {row['safety_confirmed']}"
            )
    else:
        lines.append("none | none | none | none | none | 0 | 0 | 0 | false")
    lines.extend(
        [
            "",
            "## Public Research Counts",
            f"- normalized record count: {result.normalized_record_count}",
            f"- classified record count: {result.classified_record_count}",
            f"- research queue item count: {result.research_queue_item_count}",
            f"- draft pack count: {result.draft_pack_count}",
            "",
            "## Queue / Draft Pack Summary",
            f"- high ready research count: {result.high_ready_research_count}",
            f"- medium ready research count: {result.medium_ready_research_count}",
            f"- needs more public data count: {result.needs_more_public_data_count}",
            f"- needs manual source review count: {result.needs_manual_source_review_count}",
            f"- blocked safe count: {result.blocked_safe_count}",
            "",
            "## Blockers / Warnings",
            f"- blocker count: {result.blocker_count}",
            f"- warning count: {result.warning_count}",
            "- blockers: " + (", ".join(result.blockers) if result.blockers else "none"),
            "- warnings: " + (", ".join(result.warnings) if result.warnings else "none"),
            "",
            "## Pipeline Readiness Label",
            f"- {result.pipeline_readiness_label}",
            "",
            "## v5 MVP Readiness Label",
            f"- {result.v5_mvp_readiness_label}",
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
            "- v4.70 integrates v4.61-v4.69 public-universe research stages into one operator view.",
            "- this is a research-operations dashboard, not a broker or portfolio dashboard.",
            "",
            "## Where We Need To Go",
            "- next efficient stage is v4.71 End-to-End Public Universe Workflow Audit.",
            "- v5.0 remains a local-first public research OS MVP, not a trading bot.",
            "",
            "## Redundancy Check",
            "- this is not a fetcher.",
            "- this is not a cache writer.",
            "- this is not evidence extraction, evidence verification, recommendation, approval, allocation, trading, or execution.",
            "",
            "## Remaining Timeline To v5.0",
            "- v4.71 end-to-end public universe workflow audit",
            "- v5.0 local-first public research OS MVP audit",
            "",
            "## Dashboard Sections",
        ]
    )
    lines.extend(f"- {section}" for section in result.dashboard_sections)
    lines.extend(
        [
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
            "This report does not claim evidence extraction, evidence verification, recommendation, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, candidate registry write, private ingest, broker integration, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_public_research_operator_dashboard_report(load_public_research_operator_dashboard_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the public research operator dashboard report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to public research operator dashboard JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
