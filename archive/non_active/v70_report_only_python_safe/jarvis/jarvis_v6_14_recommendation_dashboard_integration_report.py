"""Report CLI for J.A.R.V.I.S. v6.14 recommendation dashboard integration."""

from __future__ import annotations

import argparse

from .jarvis_v6_14_recommendation_dashboard_integration import (
    RecommendationDashboardIntegrationResult,
    audit_v6_14_recommendation_dashboard_integration,
)


def build_v6_14_recommendation_dashboard_integration_report(
    result: RecommendationDashboardIntegrationResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.14 Recommendation Dashboard Integration",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"analyzed policy id: {result.analyzed_policy_id}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"dashboard card count: {result.dashboard_card_count}",
        f"visible recommendation card count: {result.visible_recommendation_card_count}",
        f"safety card count: {result.safety_card_count}",
        f"manual action card count: {result.manual_action_card_count}",
        "",
        "## Dashboard Payload",
    ]

    if result.dashboard_payload is None:
        lines.append("- none")
    else:
        payload = result.dashboard_payload
        lines.extend(
            [
                f"- dashboard id: {payload.dashboard_id}",
                f"- dashboard status: {payload.dashboard_status}",
                f"- headline: {payload.headline}",
                f"- recommendation status: {payload.recommendation_status}",
                f"- recommendation decision: {payload.recommendation_decision}",
                f"- confidence score: {payload.confidence_score}",
                f"- creates buy request: {payload.creates_buy_request}",
                f"- connects broker: {payload.connects_broker}",
                f"- places order: {payload.places_order}",
                f"- executes trade: {payload.executes_trade}",
                "",
                "## Dashboard Cards",
            ]
        )

        for card in payload.cards:
            lines.extend(
                [
                    "",
                    f"### {card.card_id}",
                    f"- title: {card.title}",
                    f"- status: {card.status}",
                    f"- severity: {card.severity}",
                    f"- summary: {card.summary}",
                    f"- action label: {card.action_label}",
                    f"- user action required: {card.user_action_required}",
                    f"- creates buy request: {card.creates_buy_request}",
                    f"- connects broker: {card.connects_broker}",
                    f"- places order: {card.places_order}",
                    f"- executes trade: {card.executes_trade}",
                    "",
                    "#### Details",
                ]
            )
            lines.extend(f"- {detail}" for detail in card.details)

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
            f"- dashboard integration ready: {result.dashboard_integration_ready}",
            f"- dashboard only: {result.dashboard_only}",
            f"- autonomous recommendation displayed: {result.autonomous_recommendation_displayed}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_14_recommendation_dashboard_integration() -> str:
    return build_v6_14_recommendation_dashboard_integration_report(
        audit_v6_14_recommendation_dashboard_integration()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.14 recommendation dashboard integration."
    )
    parser.parse_args()
    print(report_v6_14_recommendation_dashboard_integration())


if __name__ == "__main__":
    main()
