"""Markdown report for J.A.R.V.I.S. candidate intake."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_candidate_intake import CandidateIntakePack, load_candidate_intake


DEFAULT_INPUT = Path("jarvis/data/jarvis_candidate_intake.example.json")


def build_candidate_intake_report(pack: CandidateIntakePack) -> str:
    lines = [
        f"# {pack.title}",
        "",
        f"version: {pack.version}",
        f"overall status: {pack.overall_status}",
        f"candidate count: {pack.candidate_count}",
        "",
        "Candidate intake is record-only and routes candidates toward the existing v4.27-v4.47 Phase 1 evidence pipeline.",
        "READY_FOR_PHASE1_EVIDENCE_PIPELINE means ready to begin manual evidence routing only; it is not approval, trust, investability, verification, or recommendation.",
        "",
        "## Candidates",
    ]
    for candidate in pack.candidates:
        lines.extend(
            [
                f"### {candidate.candidate_id}",
                f"- display name: {candidate.display_name}",
                f"- status: {candidate.intake_status}",
                f"- asset type: {candidate.asset_type}",
                f"- symbol or identifier: {candidate.symbol_or_identifier}",
                f"- issuer or provider: {candidate.issuer_or_provider or 'manual review required'}",
                f"- evidence checklist categories: {', '.join(candidate.evidence_checklist_categories)}",
                f"- route summary: {' -> '.join(candidate.route_summary)}",
                f"- blocked reasons: {', '.join(candidate.blocked_reasons) if candidate.blocked_reasons else 'none'}",
                f"- warnings: {', '.join(candidate.warnings) if candidate.warnings else 'none'}",
            ]
        )

    lines.extend(["", "## Phase 1 Route"])
    lines.extend(f"- {stage}" for stage in pack.phase1_route)
    lines.append("")
    lines.append("## Blocked Reasons")
    lines.extend(f"- {reason}" for reason in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.append("")
    lines.append("## Warnings")
    lines.extend(f"- {warning}" for warning in pack.warnings) if pack.warnings else lines.append("- none")
    lines.extend(
        [
            "",
            "## Safety Statements",
            "no approval",
            "no trusted asset",
            "no investable asset",
            "no evidence verification",
            "no registry mutation",
            "no registry file written",
            "no allocation recommendation",
            "no buy/sell request",
            "no buy signal",
            "no sell signal",
            "no trade",
            "no trade executed",
            "no executor",
            "no broker/authenticated API",
            "no credentials",
            "no private file auto-ingest",
            "no automatic fetching/downloads/extraction",
            "",
            "This report does not claim approval, trust, investability, allocation, buy/sell, trade, registry mutation, or execution authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_candidate_intake_report(load_candidate_intake(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. candidate intake report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to candidate intake JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
