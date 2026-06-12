"""Markdown report for manual candidate intake review decisions."""

from __future__ import annotations

import argparse
from pathlib import Path

from .jarvis_manual_candidate_intake_review_decision import (
    ManualCandidateIntakeReviewDecisionPack,
    load_manual_candidate_intake_review_decision_pack,
)


DEFAULT_INPUT = Path("jarvis/data/jarvis_manual_candidate_intake_review_decision.example.json")


ROUTE = (
    "v4.50 manual watchlist entry -> v4.51 manual candidate intake bridge -> "
    "v4.52 manual candidate intake review decision -> future explicit dry-run candidate intake packet -> "
    "v4.49 candidate intake -> v4.27-v4.47 Phase 1 real evidence pipeline"
)


def _join_or_none(values: tuple[str, ...]) -> str:
    return ", ".join(values) if values else "none"


def build_manual_candidate_intake_review_decision_report(pack: ManualCandidateIntakeReviewDecisionPack) -> str:
    record = pack.decision_record
    lines = [
        f"# {pack.title}",
        "",
        f"version: {pack.version}",
        f"overall status: {pack.overall_status}",
        f"decision mode: {pack.decision_mode}",
        f"source bridge version: {pack.source_bridge_version or 'missing'}",
        f"source bridge status: {pack.source_bridge_status or 'missing'}",
        f"source preview candidate count: {pack.source_preview_candidate_count if pack.source_preview_candidate_count is not None else 'missing'}",
        f"dry-run only: {str(pack.dry_run_only).lower()}",
        f"write candidate intake file: {str(pack.write_candidate_intake_file).lower()}",
        f"registry mutation: {str(pack.registry_mutation).lower()}",
        f"candidate registry write: {str(pack.candidate_registry_write).lower()}",
        "no candidate intake file was written.",
        "This decision record is not approval, trust, investability, evidence collection, evidence verification, recommendation, writing, or execution.",
        "",
        "## Decision",
    ]
    if record is None:
        lines.append("- decision record: missing")
    else:
        lines.extend(
            [
                f"- decision id: {record.decision_id or 'missing'}",
                f"- reviewer: {record.reviewer or 'missing'}",
                f"- review timestamp: {record.review_timestamp or 'missing'}",
                f"- decision: {record.decision or 'missing'}",
                f"- decision scope: {record.decision_scope or 'missing'}",
                f"- reviewed candidate ids: {_join_or_none(record.reviewed_candidate_ids)}",
                f"- rationale: {record.rationale or 'missing'}",
                f"- required followups: {_join_or_none(record.required_followups)}",
                f"- manual review required: {str(record.manual_review_required).lower()}",
                f"- next allowed step: {record.next_allowed_step or 'missing'}",
                f"- safety acknowledgement: {record.safety_acknowledgement or 'missing'}",
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
            f"- registry mutation: {str(pack.registry_mutation).lower()}",
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
            "no candidate registry write",
            "no candidate intake file written",
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
            "ACCEPT_FOR_CANDIDATE_INTAKE_DRY_RUN records only a human decision for a future dry-run packet step; it is not approval, trust, investability, evidence collection, evidence verification, allocation, buy/sell, trade, registry mutation, candidate registry write, broker API use, credential use, private ingest, fetching/downloads, or executor authorization.",
        ]
    )
    return "\n".join(lines)


def build_report_from_path(path: str | Path = DEFAULT_INPUT) -> str:
    return build_manual_candidate_intake_review_decision_report(load_manual_candidate_intake_review_decision_pack(path))


def main() -> None:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. manual candidate intake review decision report.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT), help="Path to review decision JSON.")
    args = parser.parse_args()
    print(build_report_from_path(args.input))


if __name__ == "__main__":
    main()
