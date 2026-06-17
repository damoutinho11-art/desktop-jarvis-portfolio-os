"""Report CLI for J.A.R.V.I.S. v7.0 autonomous market intelligence expansion."""

from __future__ import annotations

import argparse

from .jarvis_v7_0_autonomous_market_intelligence_expansion import (
    AutonomousMarketIntelligenceExpansionResult,
    audit_v7_0_autonomous_market_intelligence_expansion,
)


def build_v7_0_autonomous_market_intelligence_expansion_report(
    result: AutonomousMarketIntelligenceExpansionResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v7.0 Autonomous Market Intelligence Expansion",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"candidate card count: {result.candidate_card_count}",
        f"total signal count: {result.total_signal_count}",
        f"selected candidate market state: {result.selected_candidate_market_state}",
        f"selected candidate market score: {result.selected_candidate_market_score}",
        f"selected candidate supported: {result.selected_candidate_supported}",
        f"selected candidate blocked: {result.selected_candidate_blocked}",
        "",
        "## Candidate Market Intelligence Cards",
    ]

    for card in result.candidate_cards:
        lines.extend(
            [
                "",
                f"### {card.candidate_id}",
                f"- sleeve id: {card.sleeve_id}",
                f"- selected by weekly recommendation: {card.selected_by_weekly_recommendation}",
                f"- market state: {card.market_state}",
                f"- market intelligence score: {card.market_intelligence_score}",
                f"- signal count: {card.signal_count}",
                f"- supportive signal count: {card.supportive_signal_count}",
                f"- caution signal count: {card.caution_signal_count}",
                f"- blocking signal count: {card.blocking_signal_count}",
                f"- intelligence summary: {card.intelligence_summary}",
                f"- creates buy request: {card.creates_buy_request}",
                f"- connects broker: {card.connects_broker}",
                f"- places order: {card.places_order}",
                f"- executes trade: {card.executes_trade}",
                "",
                "#### Signals",
            ]
        )
        for signal in card.signals:
            lines.extend(
                [
                    f"- {signal.signal_id}: {signal.severity} | {signal.signal_type} | {signal.summary}",
                    f"  - confidence score: {signal.confidence_score}",
                    f"  - freshness status: {signal.freshness_status}",
                    f"  - source label: {signal.source_label}",
                    f"  - supports recommendation: {signal.supports_recommendation}",
                    f"  - blocks recommendation: {signal.blocks_recommendation}",
                    f"  - creates buy request: {signal.creates_buy_request}",
                    f"  - connects broker: {signal.connects_broker}",
                    f"  - places order: {signal.places_order}",
                    f"  - executes trade: {signal.executes_trade}",
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
            f"- autonomous market intelligence ready: {result.autonomous_market_intelligence_ready}",
            f"- market intelligence only: {result.market_intelligence_only}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v7_0_autonomous_market_intelligence_expansion() -> str:
    return build_v7_0_autonomous_market_intelligence_expansion_report(
        audit_v7_0_autonomous_market_intelligence_expansion()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v7.0 autonomous market intelligence expansion."
    )
    parser.parse_args()
    print(report_v7_0_autonomous_market_intelligence_expansion())


if __name__ == "__main__":
    main()
