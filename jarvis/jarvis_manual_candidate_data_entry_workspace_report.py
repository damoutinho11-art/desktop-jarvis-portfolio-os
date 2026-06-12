"""Markdown report for the v4.56 manual candidate data entry workspace."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_manual_candidate_data_entry_workspace import (
    ManualCandidateDataEntryWorkspacePack,
    load_manual_candidate_data_entry_workspace_pack,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_manual_candidate_data_entry_workspace.example.json")


def _join(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def build_manual_candidate_data_entry_workspace_report(pack: ManualCandidateDataEntryWorkspacePack) -> str:
    local_path = pack.recommended_local_paths[0] if pack.recommended_local_paths else "missing"
    lines = [
        f"# {pack.title}",
        "",
        f"version: {pack.version}",
        f"overall status: {pack.overall_status}",
        f"workspace mode: {pack.workspace_mode or 'missing'}",
        f"template path: {pack.template_path or 'missing'}",
        f"template exists: {str(pack.template_exists).lower()}",
        f"recommended local private copy path: {local_path}",
        f"gitignore guardrail status: {pack.gitignore_guardrail_status}",
        f"missing gitignore patterns: {_join(pack.missing_gitignore_patterns)}",
        f"next action: {pack.next_action or 'missing'}",
        "",
        "No more candidate-intake gates are being added.",
        "v4.56 is a manual candidate data entry workspace, not a gate.",
        "",
        "## Route",
        "v4.56 manual candidate data entry workspace -> v4.50 manual watchlist entry -> v4.49 candidate intake -> v4.27-v4.47 Phase 1 real evidence/manual review pipeline",
        "",
        "## Private Data Warnings",
        "- do not commit local candidate watchlists",
        "- do not commit account data",
        "- do not commit credentials",
        "- do not commit broker data",
        "- do not commit private files/screenshots/PDFs",
        "- keep real candidate entries in ignored local/private files",
        "",
        "## Recommended Local Paths",
    ]
    lines.extend(f"- {path}" for path in pack.recommended_local_paths) if pack.recommended_local_paths else lines.append("- none")
    lines.extend(
        [
            "",
            "## Blocked Reasons",
        ]
    )
    lines.extend(f"- {reason}" for reason in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            "",
            "## Warnings",
        ]
    )
    lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
    lines.extend(
        [
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
            "MANUAL_CANDIDATE_DATA_ENTRY_WORKSPACE_READY_SAFE means templates/docs/guardrails are ready for manual local data entry only.",
            "It is not approval, trust, investability, evidence collection, evidence verification, verified evidence promotion, allocation, portfolio weight, buy/sell, trade, registry mutation, candidate registry write, candidate intake file write, packet persistence, broker API use, credential use, private ingest, fetching/downloads, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_manual_candidate_data_entry_workspace_report(load_manual_candidate_data_entry_workspace_pack(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. manual candidate data entry workspace report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to workspace JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
