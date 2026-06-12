"""Markdown report for the explicit candidate intake dry-run command contract."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_candidate_intake_dry_run_command_contract import (
    CandidateIntakeDryRunCommandContractPack,
    load_candidate_intake_dry_run_command_contract_pack,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_candidate_intake_dry_run_command_contract.example.json")

ROUTE = (
    "v4.50 manual watchlist entry -> v4.51 manual candidate intake bridge -> "
    "v4.52 manual candidate intake review decision -> "
    "v4.53 explicit candidate intake dry-run packet command contract -> "
    "future candidate intake packet dry-run builder -> "
    "v4.49 candidate intake -> v4.27-v4.47 Phase 1 real evidence pipeline"
)


def _join_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def build_candidate_intake_dry_run_command_contract_report(pack: CandidateIntakeDryRunCommandContractPack) -> str:
    contract = pack.command_contract
    lines = [
        f"# {pack.title}",
        "",
        f"version: {pack.version}",
        f"overall status: {pack.overall_status}",
        f"command contract mode: {pack.command_contract_mode}",
        f"source review decision version: {pack.source_review_decision_version or 'missing'}",
        f"source review decision status: {pack.source_review_decision_status or 'missing'}",
        f"source decision id: {pack.source_decision_id or 'missing'}",
        f"source decision: {pack.source_decision or 'missing'}",
        f"reviewed candidate ids: {_join_or_none(pack.reviewed_candidate_ids)}",
        f"dry-run only: {str(pack.dry_run_only).lower()}",
        f"write candidate intake file: {str(pack.write_candidate_intake_file).lower()}",
        f"create candidate intake packet: {str(pack.create_candidate_intake_packet).lower()}",
        f"registry mutation: {str(pack.registry_mutation).lower()}",
        f"registry file written: {str(pack.registry_file_written).lower()}",
        f"candidate registry write: {str(pack.candidate_registry_write).lower()}",
        "no candidate intake packet was created.",
        "no candidate intake file was written.",
        "This command contract is not approval, trust, investability, evidence collection, evidence verification, recommendation, writing, or execution.",
        "",
        "## Command Contract",
    ]
    if contract is None:
        lines.append("- command contract: missing")
    else:
        lines.extend(
            [
                f"- command id: {contract.command_id or 'missing'}",
                f"- commander: {contract.commander or 'missing'}",
                f"- command timestamp: {contract.command_timestamp or 'missing'}",
                f"- explicit command phrase status: {str(contract.exact_phrase_present).lower()}",
                f"- command scope: {contract.command_scope or 'missing'}",
                f"- candidate ids in scope: {_join_or_none(contract.candidate_ids_in_scope)}",
                f"- next allowed step: {contract.next_allowed_step or 'missing'}",
                f"- manual review required: {str(contract.manual_review_required).lower()}",
                f"- safety acknowledgement: {contract.safety_acknowledgement or 'missing'}",
                f"- contract notes: {contract.contract_notes or 'none'}",
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
            f"- create candidate intake packet: {str(pack.create_candidate_intake_packet).lower()}",
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
            "no candidate intake packet created",
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
            "READY_FOR_PACKET_DRY_RUN_SAFE validates only an explicit manual contract for a future dry-run packet builder; it is not approval, trust, investability, evidence collection, evidence verification, allocation, buy/sell, trade, registry mutation, candidate registry write, candidate intake file write, packet creation, broker API use, credential use, private ingest, fetching/downloads, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_candidate_intake_dry_run_command_contract_report(load_candidate_intake_dry_run_command_contract_pack(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. candidate intake dry-run command contract report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to command contract JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
