"""Report CLI for J.A.R.V.I.S. v8.0 public market intelligence operator dashboard."""

from __future__ import annotations

import argparse

from .jarvis_v8_0_public_market_intelligence_operator_dashboard import (
    PublicMarketIntelligenceOperatorDashboardResult,
    audit_v8_0_public_market_intelligence_operator_dashboard,
)


def build_v8_0_public_market_intelligence_operator_dashboard_report(
    result: PublicMarketIntelligenceOperatorDashboardResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v8.0 Public Market Intelligence Operator Dashboard",
        "",
        f"status: {result.status}",
        f"dashboard status: {result.dashboard_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"card count: {result.card_count}",
        f"ready card count: {result.ready_card_count}",
        f"disabled card count: {result.disabled_card_count}",
        f"blocked card count: {result.blocked_card_count}",
        f"user-visible card count: {result.user_visible_card_count}",
        f"live fetch enabled card count: {result.live_fetch_enabled_card_count}",
        f"network call enabled card count: {result.network_call_enabled_card_count}",
        f"raw response storage enabled card count: {result.raw_response_storage_enabled_card_count}",
        f"live adapter record emission enabled card count: {result.live_adapter_record_emission_enabled_card_count}",
        f"compatible with v7.10 readiness closeout: {result.compatible_with_v7_10_readiness_closeout}",
        "",
        "## Dashboard Cards",
    ]

    for card in result.cards:
        lines.extend(
            [
                "",
                f"### {card.card_id}",
                f"- title: {card.title}",
                f"- category: {card.category}",
                f"- state: {card.state}",
                f"- priority: {card.priority}",
                f"- summary: {card.summary}",
                f"- evidence: {card.evidence}",
                f"- next operator action: {card.next_operator_action}",
                f"- user visible: {card.user_visible}",
                f"- blocks live fetch: {card.blocks_live_fetch}",
                f"- live fetch enabled: {card.live_fetch_enabled}",
                f"- network call enabled: {card.network_call_enabled}",
                f"- raw response storage enabled: {card.raw_response_storage_enabled}",
                f"- live adapter record emission enabled: {card.live_adapter_record_emission_enabled}",
                f"- creates buy request: {card.creates_buy_request}",
                f"- connects broker: {card.connects_broker}",
                f"- places order: {card.places_order}",
                f"- executes trade: {card.executes_trade}",
            ]
        )

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
            f"- operator dashboard ready: {result.operator_dashboard_ready}",
            f"- dashboard visibility only: {result.dashboard_visibility_only}",
            f"- v7 chain closeout visible: {result.v7_chain_closeout_visible}",
            f"- selected candidate visible: {result.selected_candidate_visible}",
            f"- provider readiness visible: {result.provider_readiness_visible}",
            f"- disabled live fetch visible: {result.disabled_live_fetch_visible}",
            f"- execution safety visible: {result.execution_safety_visible}",
            f"- live fetch deferred: {result.live_fetch_deferred}",
            f"- network calls deferred: {result.network_calls_deferred}",
            f"- raw response storage deferred: {result.raw_response_storage_deferred}",
            f"- live adapter record emission deferred: {result.live_adapter_record_emission_deferred}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v8_0_public_market_intelligence_operator_dashboard() -> str:
    return build_v8_0_public_market_intelligence_operator_dashboard_report(
        audit_v8_0_public_market_intelligence_operator_dashboard()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v8.0 public market intelligence operator dashboard."
    )
    parser.parse_args()
    print(report_v8_0_public_market_intelligence_operator_dashboard())


if __name__ == "__main__":
    main()
