"""Markdown report for the candidate intake packet dry-run builder."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_candidate_intake_packet_dry_run_builder import (
    CandidateIntakePacketDryRunBuilderPack,
    load_candidate_intake_packet_dry_run_builder_pack,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_candidate_intake_packet_dry_run_builder.example.json")

ROUTE = (
    "v4.50 manual watchlist entry -> v4.51 manual candidate intake bridge -> "
    "v4.52 manual candidate intake review decision -> "
    "v4.53 explicit candidate intake dry-run packet command contract -> "
    "v4.54 candidate intake packet dry-run builder -> "
    "future explicit manual candidate intake packet acceptance/review -> "
    "v4.49 candidate intake -> v4.27-v4.47 Phase 1 real evidence pipeline"
)


def _join_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def build_candidate_intake_packet_dry_run_builder_report(pack: CandidateIntakePacketDryRunBuilderPack) -> str:
    lines = [
        f"# {pack.title}",
        "",
        f"version: {pack.version}",
        f"overall status: {pack.overall_status}",
        f"builder mode: {pack.builder_mode}",
        f"source command contract version: {pack.source_command_contract_version or 'missing'}",
        f"source command contract status: {pack.source_command_contract_status or 'missing'}",
        f"source command id: {pack.source_command_id or 'missing'}",
        f"explicit command phrase status: {str(pack.explicit_command_phrase_present).lower()}",
        f"command candidate ids in scope: {_join_or_none(pack.command_candidate_ids_in_scope)}",
        f"source preview candidate count: {pack.source_preview_candidate_count}",
        f"built packet preview candidate count: {pack.built_preview_candidate_count}",
        "no packet file was persisted.",
        "no candidate intake file was written.",
        "This dry-run builder is not approval, trust, investability, evidence collection, evidence verification, recommendation, writing, or execution.",
        "",
        "## Candidate Packet Preview Summary",
    ]
    for result in pack.candidate_results:
        lines.extend(
            [
                f"### {result.candidate_id}",
                f"- packet preview created: {str(result.candidate_preview_created).lower()}",
                f"- blocked reasons: {_join_or_none(result.blocked_reasons)}",
                f"- warnings: {_join_or_none(result.warnings)}",
            ]
        )
        if result.packet_candidate is not None:
            candidate = result.packet_candidate
            lines.extend(
                [
                    f"- display name: {candidate['display_name']}",
                    f"- asset type: {candidate['asset_type']}",
                    f"- symbol or identifier: {candidate['symbol_or_identifier']}",
                    f"- phase1 route: {candidate['phase1_route']}",
                    f"- required evidence categories: {', '.join(candidate['required_evidence_categories'])}",
                ]
            )
    lines.extend(
        [
            "",
            "## Packet Preview",
        ]
    )
    if pack.candidate_intake_packet_preview is None:
        lines.append("- none")
    else:
        packet = pack.candidate_intake_packet_preview
        lines.extend(
            [
                f"- version: {packet['version']}",
                f"- generated_from: {packet['generated_from']}",
                f"- dry_run_only: {str(packet['dry_run_only']).lower()}",
                f"- write_candidate_intake_file: {str(packet['write_candidate_intake_file']).lower()}",
                f"- persist_packet_file: {str(packet['persist_packet_file']).lower()}",
                f"- registry_mutation: {str(packet['registry_mutation']).lower()}",
                f"- registry_file_written: {str(packet['registry_file_written']).lower()}",
                f"- candidate_registry_write: {str(packet['candidate_registry_write']).lower()}",
                f"- candidate_count: {packet['candidate_count']}",
            ]
        )
    lines.extend(
        [
            "",
            "## Route",
            ROUTE,
            "",
            "## Blocked Reasons",
        ]
    )
    lines.extend(f"- {reason}" for reason in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            "",
            "## Dry-Run / No-Write / No-Mutation Summary",
            f"- dry-run only: {str(pack.dry_run_only).lower()}",
            f"- write candidate intake file: {str(pack.write_candidate_intake_file).lower()}",
            f"- persist packet file: {str(pack.persist_packet_file).lower()}",
            f"- registry mutation: {str(pack.registry_mutation).lower()}",
            f"- registry file written: {str(pack.registry_file_written).lower()}",
            f"- candidate registry write: {str(pack.candidate_registry_write).lower()}",
            f"- evidence collection started: {str(pack.evidence_collection_started).lower()}",
            f"- evidence verification started: {str(pack.evidence_verification_started).lower()}",
            "",
            "## Safety Statements",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no evidence collection started",
            "no evidence verification",
            "no verified evidence promotion",
            "no registry mutation",
            "no registry file written",
            "no candidate registry write",
            "no candidate intake file written",
            "no packet file persisted",
            "no allocation recommendation",
            "no portfolio weight",
            "no buy/sell request",
            "no trade",
            "no executor",
            "no broker/authenticated API",
            "no credentials",
            "no private file ingest",
            "no automatic fetching/downloads/extraction",
            "",
            "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_READY_SAFE means only that a packet preview was built in memory/report output; it is not approval, trust, investability, evidence collection, evidence verification, allocation, buy/sell, trade, registry mutation, candidate registry write, candidate intake file write, packet persistence, broker API use, credential use, private ingest, fetching/downloads, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_candidate_intake_packet_dry_run_builder_report(load_candidate_intake_packet_dry_run_builder_pack(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. candidate intake packet dry-run builder report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to builder JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
