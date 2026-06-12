"""Markdown report for the Phase 2 candidate-intake chain audit."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_phase2_candidate_intake_chain_audit import (
    Phase2CandidateIntakeChainAuditPack,
    load_phase2_candidate_intake_chain_audit_pack,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_phase2_candidate_intake_chain_audit.example.json")

ROUTE = (
    "v4.50 manual watchlist entry -> v4.51 manual candidate intake bridge -> "
    "v4.52 manual candidate intake review decision -> "
    "v4.53 explicit dry-run packet command contract -> "
    "v4.54 candidate intake packet dry-run builder -> "
    "v4.49 candidate intake -> v4.27-v4.47 Phase 1 real evidence pipeline"
)


def _join_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def build_phase2_candidate_intake_chain_audit_report(pack: Phase2CandidateIntakeChainAuditPack) -> str:
    lines = [
        f"# {pack.title}",
        "",
        f"version: {pack.version}",
        f"overall status: {pack.overall_status}",
        f"audit mode: {pack.audit_mode}",
        f"report only: {str(pack.report_only).lower()}",
        f"phase2 candidate-intake chain complete: {str(pack.phase2_candidate_intake_chain_complete).lower()}",
        f"chain coherence verdict: {str(pack.chain_coherent).lower()}",
        f"redundancy verdict: {pack.redundancy_verdict}",
        f"next action: {pack.next_action or 'missing'}",
        "",
        "## Phase 2 Candidate-Intake Chain Summary",
        "v4.49-v4.54 are enough for candidate-intake dry-run readiness.",
        "More candidate-intake gates are not currently justified.",
        "The correct next action is real manual candidate watchlist data entry using the v4.50 format.",
        "Future stages should only be created when they introduce a real new boundary, not repeated review layers.",
        "",
        "## Stages",
    ]
    for stage in pack.stages:
        lines.extend(
            [
                f"### {stage.stage_id} - {stage.stage_name}",
                f"- purpose: {stage.purpose}",
                f"- expected safe status: {stage.expected_safe_status}",
                f"- report command: `{stage.report_command}`",
                f"- writes files: {str(stage.writes_files).lower()}",
                f"- mutates registry: {str(stage.mutates_registry).lower()}",
                f"- creates executor: {str(stage.creates_executor).lower()}",
                f"- approves asset: {str(stage.approves_asset).lower()}",
                f"- trusts asset: {str(stage.trusts_asset).lower()}",
                f"- marks investable: {str(stage.marks_investable).lower()}",
                f"- starts evidence collection: {str(stage.starts_evidence_collection).lower()}",
                f"- verifies evidence: {str(stage.verifies_evidence).lower()}",
                f"- promotes verified evidence: {str(stage.promotes_verified_evidence).lower()}",
                f"- recommends allocation: {str(stage.recommends_allocation).lower()}",
                f"- creates buy or sell signal: {str(stage.creates_buy_or_sell_signal).lower()}",
                f"- executes trade: {str(stage.executes_trade).lower()}",
            ]
        )
    lines.extend(
        [
            "",
            "## Expected Statuses",
        ]
    )
    lines.extend(f"- {status}" for status in pack.expected_statuses) if pack.expected_statuses else lines.append("- none")
    lines.extend(
        [
            "",
            "## Route",
            ROUTE,
            "",
            "VWCE and FTAW were pilot anchors only.",
            "Any candidate must pass the same evidence and manual review chain.",
            "",
            "## Blocked Reasons",
        ]
    )
    lines.extend(f"- {reason}" for reason in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.extend(
        [
            "",
            "## Notes",
        ]
    )
    lines.extend(f"- {note}" for note in pack.notes) if pack.notes else lines.append("- none")
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
            "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_COMPLETE_SAFE is an audit verdict only; it is not approval, trust, investability, evidence collection, evidence verification, promotion, allocation, portfolio weight, buy/sell, trade, registry mutation, candidate registry write, candidate intake file write, packet persistence, broker API use, credential use, private ingest, fetching/downloads, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_phase2_candidate_intake_chain_audit_report(load_phase2_candidate_intake_chain_audit_pack(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. Phase 2 candidate-intake chain audit report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to audit JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
