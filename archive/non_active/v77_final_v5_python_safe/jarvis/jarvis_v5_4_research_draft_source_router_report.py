"""Markdown report for v5.4 research draft source router."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_v5_4_research_draft_source_router import (
    V54ResearchDraftSourceRouterResult,
    load_v5_4_research_draft_source_router_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_v5_4_research_draft_source_router.example.json")


def build_v5_4_research_draft_source_router_report(result: V54ResearchDraftSourceRouterResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"research draft source router mode: {result.research_draft_source_router_mode or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Review Row Summary",
        f"- review row count: {result.review_row_count}",
        f"- unsafe count: {result.unsafe_count}",
        f"- unsupported format count: {result.unsupported_format_count}",
        f"- unsupported category count: {result.unsupported_category_count}",
        f"- duplicate review id count: {result.duplicate_review_id_count}",
        f"- duplicate fixture id count: {result.duplicate_fixture_id_count}",
        f"- private or credential risk count: {result.private_or_credential_risk_count}",
        f"- forbidden flag count: {result.forbidden_flag_count}",
        f"- missing fixture count: {result.missing_fixture_count}",
        f"- stale fixture count: {result.stale_fixture_count}",
        f"- manual refresh required count: {result.manual_refresh_required_count}",
        "",
        "## Source Route Summary",
        f"- source route count: {result.source_route_count}",
        f"- routed reference count: {result.routed_reference_count}",
        f"- pending operator review count: {result.pending_operator_review_count}",
        f"- deferred route count: {result.deferred_route_count}",
        f"- blocked route count: {result.blocked_route_count}",
        "route id | review id | fixture id | source reference type | priority | decision | allowed downstream use",
        "--- | --- | --- | --- | --- | --- | ---",
    ]
    if result.route_rows:
        for row in result.route_rows:
            lines.append(
                f"{row['route_id']} | {row['review_id']} | {row['fixture_id']} | {row['source_reference_type']} | "
                f"{row['route_priority']} | {row['route_decision']} | {', '.join(row['allowed_downstream_use'])}"
            )
    else:
        lines.append("none | none | none | none | none | none | none")
    lines.extend(
        [
            "",
            "## Routing Decision Summary",
            f"- route_to_research_draft_reference_only: {result.routed_reference_count}",
            f"- pending operator review: {result.pending_operator_review_count}",
            f"- deferred: {result.deferred_route_count}",
            f"- blocked: {result.blocked_route_count}",
            "- routed references are unverified source references only.",
            "- routing is not evidence verification, source truth verification, approval, recommendation, allocation, buy/sell, or trade.",
            "",
            "## Route Priority Summary",
            f"- high priority count: {result.high_priority_count}",
            f"- medium priority count: {result.medium_priority_count}",
            f"- low priority count: {result.low_priority_count}",
            "",
            "## Blocked Downstream Use Summary",
            "- evidence_verification",
            "- source_truth_verification",
            "- approval",
            "- trust",
            "- investability",
            "- registry_mutation",
            "- recommendation",
            "- allocation",
            "- trade",
            "- executor",
            "",
            "## Blockers / Warnings",
            "- blockers: " + (", ".join(result.blockers) if result.blockers else "none"),
            "- warnings: " + (", ".join(result.warnings) if result.warnings else "none"),
            "",
            "## Operator Runbook Steps",
        ]
    )
    if result.operator_runbook_steps:
        lines.extend(f"{index}. {step}" for index, step in enumerate(result.operator_runbook_steps, start=1))
    else:
        lines.append("1. Review source routes before any research packet draft assembly.")
    lines.extend(
        [
            "",
            "## Output / Write Authorization Summary",
            "- report wrote files: false",
            f"- ready to write with explicit authorization: {str(result.status == 'V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_READY_TO_WRITE_SAFE').lower()}",
            "- required phrase: AUTHORIZE_V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE",
            "- optional write root: jarvis/local/public_source_fixtures/v5_4_research_draft_source_router",
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
            "- v5.1 wired public fixture preparation.",
            "- v5.2 dry-ran local public fixture import.",
            "- v5.3 created the operator fixture review queue.",
            "- v5.4 routes accepted/queued review metadata into research-draft source references only.",
            "",
            "## Where We Need To Go",
            "- review source routes manually before any packet draft assembly.",
            "- next efficient phase is v5.5 Public Research Packet Draft Assembler, still without evidence verification or fetching.",
            "",
            "## Anti-Redundancy Statement",
            "- v5.1 answers what fixtures should exist and where.",
            "- v5.2 answers whether local fixture metadata can be import-previewed safely.",
            "- v5.3 answers what the operator accepted, deferred, or rejected.",
            "- v5.4 answers which accepted metadata can become unverified research-draft source references.",
            "- this layer does not repeat fixture wiring, import dry-run inspection, or operator queue review.",
            "",
            "## Post-v5.3 Phase Statement",
            "- v5.4 is a metadata-only routing layer after operator fixture review.",
            "- it does not add fetching, evidence verification, source truth verification, approval, recommendation, or execution.",
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
            "no external file read",
            "no OCR",
            "no PDF parsing",
            "no HTML scraping",
            "no source parsing as verified evidence",
            "no evidence extraction",
            "no evidence verification",
            "no source truth verification",
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
            "This report does not claim fetching, scraping, external file read, OCR, PDF parsing, HTML scraping, evidence verification, source truth verification, recommendation, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, broker integration, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_v5_4_research_draft_source_router_report(load_v5_4_research_draft_source_router_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the v5.4 research draft source router report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to v5.4 research draft source router JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
