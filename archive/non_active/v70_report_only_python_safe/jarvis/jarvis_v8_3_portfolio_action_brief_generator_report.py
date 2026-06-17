"""Report CLI for J.A.R.V.I.S. v8.3 portfolio action brief generator."""

from __future__ import annotations

import argparse

from .jarvis_v8_3_portfolio_action_brief_generator import (
    PortfolioActionBriefGeneratorResult,
    audit_v8_3_portfolio_action_brief_generator,
)


def build_v8_3_portfolio_action_brief_generator_report(
    result: PortfolioActionBriefGeneratorResult,
) -> str:
    brief = result.brief

    lines = [
        "# J.A.R.V.I.S. v8.3 Portfolio Action Brief Generator",
        "",
        f"status: {result.status}",
        f"brief status: {result.brief_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"evidence section count: {result.evidence_section_count}",
        f"ready evidence section count: {result.ready_evidence_section_count}",
        f"watch evidence section count: {result.watch_evidence_section_count}",
        f"blocked evidence section count: {result.blocked_evidence_section_count}",
        f"compatible with v8.2 evidence pack: {result.compatible_with_v8_2_evidence_pack}",
        "",
        "## Portfolio Action Brief",
        "",
        f"- brief id: {brief.brief_id}",
        f"- brief type: {brief.brief_type}",
        f"- headline: {brief.headline}",
        f"- preparation reason: {brief.preparation_reason}",
        f"- evidence summary: {brief.evidence_summary}",
        f"- watch summary: {brief.watch_summary}",
        f"- blocked summary: {brief.blocked_summary}",
        f"- final manual action: {brief.final_manual_action}",
        f"- operator instruction: {brief.operator_instruction}",
        f"- user visible: {brief.user_visible}",
        f"- creates buy request: {brief.creates_buy_request}",
        f"- connects broker: {brief.connects_broker}",
        f"- places order: {brief.places_order}",
        f"- executes trade: {brief.executes_trade}",
        f"- live fetch enabled: {brief.live_fetch_enabled}",
        f"- network call enabled: {brief.network_call_enabled}",
        f"- raw response storage enabled: {brief.raw_response_storage_enabled}",
        f"- live adapter record emission enabled: {brief.live_adapter_record_emission_enabled}",
        "",
        "## Blockers",
    ]

    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety",
            "",
            f"- action brief ready: {result.action_brief_ready}",
            f"- product brief stage: {result.product_brief_stage}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
            f"- live fetch deferred: {result.live_fetch_deferred}",
            f"- network calls deferred: {result.network_calls_deferred}",
            f"- raw response storage deferred: {result.raw_response_storage_deferred}",
            f"- live adapter record emission deferred: {result.live_adapter_record_emission_deferred}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v8_3_portfolio_action_brief_generator() -> str:
    return build_v8_3_portfolio_action_brief_generator_report(
        audit_v8_3_portfolio_action_brief_generator()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Report J.A.R.V.I.S. v8.3 portfolio action brief generator.")
    parser.parse_args()
    print(report_v8_3_portfolio_action_brief_generator())


if __name__ == "__main__":
    main()
