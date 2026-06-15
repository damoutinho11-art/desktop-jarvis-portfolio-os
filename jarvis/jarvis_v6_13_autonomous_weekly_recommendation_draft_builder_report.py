"""Report CLI for J.A.R.V.I.S. v6.13 autonomous weekly recommendation draft builder."""

from __future__ import annotations

import argparse

from .jarvis_v6_13_autonomous_weekly_recommendation_draft_builder import (
    AutonomousWeeklyRecommendationDraftResult,
    audit_v6_13_autonomous_weekly_recommendation_draft_builder,
)


def build_v6_13_autonomous_weekly_recommendation_draft_builder_report(
    result: AutonomousWeeklyRecommendationDraftResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.13 Autonomous Weekly Recommendation Draft Builder",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"analyzed policy id: {result.analyzed_policy_id}",
        f"shortlist candidate count: {result.shortlist_candidate_count}",
        f"recommendation count: {result.recommendation_count}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"investable cash EUR: {result.investable_cash_eur}",
        f"protected cash EUR: {result.protected_cash_eur}",
        "",
        "## Recommendation Draft",
    ]

    if result.recommendation is None:
        lines.append("- none")
    else:
        rec = result.recommendation
        lines.extend(
            [
                f"- recommendation id: {rec.recommendation_id}",
                f"- recommendation status: {rec.recommendation_status}",
                f"- decision: {rec.decision}",
                f"- selected shortlist id: {rec.selected_shortlist_id}",
                f"- selected candidate id: {rec.selected_candidate_id}",
                f"- selected sleeve id: {rec.selected_sleeve_id}",
                f"- selected rank: {rec.selected_rank}",
                f"- confidence score: {rec.confidence_score}",
                f"- suggested manual amount logic: {rec.suggested_manual_amount_logic}",
                f"- primary reason: {rec.primary_reason}",
                f"- final user action required: {rec.final_user_action_required}",
                f"- creates buy request: {rec.creates_buy_request}",
                f"- connects broker: {rec.connects_broker}",
                f"- places order: {rec.places_order}",
                f"- executes trade: {rec.executes_trade}",
                "",
                "### Supporting Reasons",
            ]
        )
        lines.extend(f"- {reason}" for reason in rec.supporting_reasons)

        lines.extend(["", "### Rejection Reasons For Other Candidates"])
        if rec.rejection_reasons_for_others:
            lines.extend(f"- {reason}" for reason in rec.rejection_reasons_for_others)
        else:
            lines.append("- none")

        lines.extend(["", "### Risk Warnings"])
        lines.extend(f"- {warning}" for warning in rec.risk_warnings)

        lines.extend(["", "### Manual Buy Instructions"])
        lines.extend(f"- {instruction}" for instruction in rec.manual_buy_instructions)

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
            f"- autonomous recommendation ready: {result.autonomous_recommendation_ready}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_13_autonomous_weekly_recommendation_draft_builder() -> str:
    return build_v6_13_autonomous_weekly_recommendation_draft_builder_report(
        audit_v6_13_autonomous_weekly_recommendation_draft_builder()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.13 autonomous weekly recommendation draft builder."
    )
    parser.parse_args()
    print(report_v6_13_autonomous_weekly_recommendation_draft_builder())


if __name__ == "__main__":
    main()
