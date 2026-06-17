"""Markdown report for v5.5 public research packet draft assembler."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_v5_5_public_research_packet_draft_assembler import (
    V55PublicResearchPacketDraftAssemblerResult,
    load_v5_5_public_research_packet_draft_assembler_result,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_v5_5_public_research_packet_draft_assembler.example.json")


def build_v5_5_public_research_packet_draft_assembler_report(result: V55PublicResearchPacketDraftAssemblerResult) -> str:
    lines = [
        f"# {result.title}",
        "",
        f"version: {result.version}",
        f"overall status: {result.status}",
        f"public research packet draft assembler mode: {result.public_research_packet_draft_assembler_mode or 'missing'}",
        "read-only/default-no-write/no-network/no-fetch/no-broker summary: true",
        "",
        "## Route Row Summary",
        f"- route row count: {result.route_row_count}",
        f"- invalid route row count: {result.invalid_route_row_count}",
        f"- duplicate route id count: {result.duplicate_route_id_count}",
        f"- duplicate source reference count: {result.duplicate_source_reference_count}",
        f"- private or credential risk count: {result.private_or_credential_risk_count}",
        f"- forbidden flag count: {result.forbidden_flag_count}",
        f"- unsupported source reference type count: {result.unsupported_source_reference_type_count}",
        f"- route not ready count: {result.route_not_ready_count}",
        f"- deferred route count: {result.deferred_route_count}",
        f"- blocked route count: {result.blocked_route_count}",
        "",
        "## Packet Draft Summary",
        f"- packet group count: {result.packet_group_count}",
        f"- packet draft count: {result.packet_draft_count}",
        f"- source reference count: {result.source_reference_count}",
        f"- ready packet count: {result.ready_packet_count}",
        f"- deferred packet count: {result.deferred_packet_count}",
        f"- blocked packet count: {result.blocked_packet_count}",
        "packet id | group | draft type | priority | source references | allowed downstream use",
        "--- | --- | --- | --- | --- | ---",
    ]
    if result.packet_rows:
        for row in result.packet_rows:
            lines.append(
                f"{row['packet_id']} | {row['packet_group_key']} | {row['packet_draft_type']} | "
                f"{row['packet_priority']} | {row['source_reference_count']} | {', '.join(row['allowed_downstream_use'])}"
            )
    else:
        lines.append("none | none | none | none | none | none")
    lines.extend(
        [
            "",
            "## Packet Assembly Decision Summary",
            f"- public_research_packet_draft: {result.ready_packet_count}",
            f"- deferred packet drafts: {result.deferred_packet_count}",
            f"- blocked packet drafts: {result.blocked_packet_count}",
            "- packet drafts are unverified source-reference groupings only.",
            "- packet assembly is not evidence extraction, evidence verification, source truth verification, approval, recommendation, allocation, buy/sell, or trade.",
            "",
            "## Packet Priority Summary",
            f"- high priority count: {result.high_priority_count}",
            f"- medium priority count: {result.medium_priority_count}",
            f"- low priority count: {result.low_priority_count}",
            "",
            "## Blocked Downstream Use Summary",
            "- evidence_extraction",
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
        lines.append("1. Review packet drafts before any human review queue.")
    lines.extend(
        [
            "",
            "## Output / Write Authorization Summary",
            "- report wrote files: false",
            f"- ready to write with explicit authorization: {str(result.status == 'V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_READY_TO_WRITE_SAFE').lower()}",
            "- required phrase: AUTHORIZE_V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE",
            "- optional write root: jarvis/local/public_source_fixtures/v5_5_public_research_packet_drafts",
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
            "- v5.4 routed accepted review metadata into research-draft source references only.",
            "- v5.5 assembles unverified packet drafts from route-row metadata only.",
            "",
            "## Where We Need To Go",
            "- review public research packet drafts manually before any human review queue.",
            "- next efficient phase is v5.6 Public Research Packet Human Review Queue, still without evidence verification or fetching.",
            "",
            "## Anti-Redundancy Statement",
            "- v5.4 answers which accepted metadata can become unverified research-draft source references.",
            "- v5.5 answers how those references can be grouped into unverified packet drafts.",
            "- this layer does not repeat source routing, fixture wiring, import dry-run inspection, or operator queue review.",
            "",
            "## Post-v5.4 Phase Statement",
            "- v5.5 is a metadata-only packet draft assembly layer after source routing.",
            "- it does not add fetching, evidence extraction, evidence verification, source truth verification, approval, recommendation, or execution.",
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
            "This report does not claim fetching, scraping, external file read, OCR, PDF parsing, HTML scraping, evidence extraction, evidence verification, source truth verification, recommendation, approval, trust, investability, allocation, buy/sell signal, trade, registry mutation, broker integration, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_v5_5_public_research_packet_draft_assembler_report(load_v5_5_public_research_packet_draft_assembler_result(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the v5.5 public research packet draft assembler report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to v5.5 public research packet draft assembler JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
