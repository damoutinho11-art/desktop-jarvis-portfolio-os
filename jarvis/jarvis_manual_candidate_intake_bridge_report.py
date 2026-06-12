"""Markdown report for the manual candidate intake bridge."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_manual_candidate_intake_bridge import ManualCandidateIntakeBridgePack, load_manual_candidate_intake_bridge_pack


DEFAULT_INPUT = Path("jarvis/data/jarvis_manual_candidate_intake_bridge.example.json")


def build_manual_candidate_intake_bridge_report(pack: ManualCandidateIntakeBridgePack) -> str:
    lines = [
        f"# {pack.title}",
        "",
        f"version: {pack.version}",
        f"overall status: {pack.overall_status}",
        f"bridge mode: {pack.bridge_mode}",
        f"source watchlist pack: {pack.source_watchlist_entry_pack or 'embedded entries'}",
        f"dry-run only: {str(pack.dry_run_only).lower()}",
        f"write candidate intake file: {str(pack.write_candidate_intake_file).lower()}",
        f"registry mutation: {str(pack.registry_mutation).lower()}",
        f"candidate registry write: {str(pack.candidate_registry_write).lower()}",
        "no candidate intake file was written.",
        "The preview is not approval, trust, investability, evidence verification, recommendation, writing, or automatic routing.",
        f"input entry count: {pack.input_entry_count}",
        f"preview candidate count: {pack.preview_candidate_count}",
        "",
        "## Route",
        "v4.50 manual watchlist entry -> v4.51 manual candidate intake bridge -> v4.49 candidate intake -> v4.27-v4.47 Phase 1 real evidence pipeline",
        "",
        "## Entries",
    ]
    for entry in pack.entries:
        lines.extend(
            [
                f"### {entry.watchlist_entry_id}",
                f"- candidate id: {entry.candidate_id}",
                f"- display name: {entry.display_name}",
                f"- asset type: {entry.asset_type}",
                f"- v4.50 status: {entry.entry_status}",
                f"- bridge status: {entry.bridge_entry_status}",
                f"- candidate preview created: {str(entry.candidate_preview_created).lower()}",
                f"- blocked reasons: {', '.join(entry.blocked_reasons) if entry.blocked_reasons else 'none'}",
                f"- warnings: {', '.join(entry.warnings) if entry.warnings else 'none'}",
            ]
        )
    lines.append("")
    lines.append("## Candidate Intake Packet Preview")
    if pack.candidate_intake_packet_preview is None:
        lines.append("- none")
    else:
        packet = pack.candidate_intake_packet_preview
        lines.append(f"- version: {packet['version']}")
        lines.append(f"- generated_from: {packet['generated_from']}")
        lines.append(f"- dry_run_only: {str(packet['dry_run_only']).lower()}")
        lines.append(f"- write_candidate_intake_file: {str(packet['write_candidate_intake_file']).lower()}")
        lines.append(f"- registry_mutation: {str(packet['registry_mutation']).lower()}")
        lines.append(f"- candidate_registry_write: {str(packet['candidate_registry_write']).lower()}")
        for candidate in packet["candidates"]:
            lines.append(
                f"- candidate: {candidate['candidate_id']} | {candidate['display_name']} | "
                f"{candidate['asset_type']} | {candidate['phase1_route']}"
            )
    lines.append("")
    lines.append("## Blocked Reasons")
    lines.extend(f"- {reason}" for reason in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.append("")
    lines.append("## Safety Statements")
    lines.extend(
        [
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no evidence collection started",
            "no evidence verification",
            "no verified evidence promotion",
            "no registry mutation",
            "no candidate registry write",
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
            "This report does not claim approval, trust, investability, verification, promotion, allocation, portfolio weight, buy/sell, trade, registry mutation, candidate registry write, broker API use, credential use, private ingest, fetching/downloads, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_manual_candidate_intake_bridge_report(load_manual_candidate_intake_bridge_pack(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. manual candidate intake bridge report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to bridge JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
