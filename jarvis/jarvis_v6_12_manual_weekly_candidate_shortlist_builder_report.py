"""Report CLI for J.A.R.V.I.S. v6.12 manual weekly candidate shortlist builder."""

from __future__ import annotations

import argparse

from .jarvis_v6_12_manual_weekly_candidate_shortlist_builder import (
    ManualWeeklyCandidateShortlistResult,
    audit_v6_12_manual_weekly_candidate_shortlist_builder,
)


def build_v6_12_manual_weekly_candidate_shortlist_builder_report(
    result: ManualWeeklyCandidateShortlistResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.12 Manual Weekly Candidate Shortlist Builder",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"analyzed policy id: {result.analyzed_policy_id}",
        f"source planning context item count: {result.source_planning_context_item_count}",
        f"shortlist candidate count: {result.shortlist_candidate_count}",
        f"critical source count: {result.critical_source_count}",
        f"high source count: {result.high_source_count}",
        f"crypto shortlist count: {result.crypto_shortlist_count}",
        f"manual review required count: {result.manual_review_required_count}",
        f"investable cash EUR: {result.investable_cash_eur}",
        f"protected cash EUR: {result.protected_cash_eur}",
        "",
        "## Shortlist Candidates",
    ]

    for candidate in result.shortlist_candidates:
        lines.extend(
            [
                "",
                f"### {candidate.shortlist_id}",
                f"- rank: {candidate.rank}",
                f"- sleeve id: {candidate.sleeve_id}",
                f"- candidate id: {candidate.candidate_id}",
                f"- candidate role: {candidate.candidate_role}",
                f"- quality status: {candidate.quality_status}",
                f"- source context id: {candidate.source_context_id}",
                f"- source priority: {candidate.source_priority}",
                f"- source gap status: {candidate.source_gap_status}",
                f"- shortlist status: {candidate.shortlist_status}",
                f"- manual review required: {candidate.manual_review_required}",
                f"- shortlisted for manual review: {candidate.shortlisted_for_manual_review}",
                f"- final recommendation created: {candidate.final_recommendation_created}",
                f"- asset approved: {candidate.asset_approved}",
                f"- creates weekly buy ticket: {candidate.creates_weekly_buy_ticket}",
                f"- creates buy request: {candidate.creates_buy_request}",
                f"- connects broker: {candidate.connects_broker}",
                f"- executes trade: {candidate.executes_trade}",
                "",
                "#### Reason Codes",
            ]
        )
        lines.extend(f"- {reason}" for reason in candidate.reason_codes)

        lines.extend(["", "#### Constraints"])
        lines.extend(f"- {constraint}" for constraint in candidate.constraints)

    lines.extend(["", "## Warnings"])
    if result.warnings:
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("- none")

    lines.extend(["", "## Blockers"])
    if result.blockers:
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety",
            "",
            f"- manual weekly shortlist ready: {result.manual_weekly_shortlist_ready}",
            f"- shortlist only: {result.shortlist_only}",
            f"- final recommendation deferred: {result.final_recommendation_deferred}",
            f"- asset approval deferred: {result.asset_approval_deferred}",
            f"- weekly buy ticket deferred: {result.weekly_buy_ticket_deferred}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_12_manual_weekly_candidate_shortlist_builder() -> str:
    return build_v6_12_manual_weekly_candidate_shortlist_builder_report(
        audit_v6_12_manual_weekly_candidate_shortlist_builder()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.12 manual weekly candidate shortlist builder."
    )
    parser.parse_args()
    print(report_v6_12_manual_weekly_candidate_shortlist_builder())


if __name__ == "__main__":
    main()
