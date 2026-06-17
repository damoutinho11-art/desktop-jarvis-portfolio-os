"""Report CLI for J.A.R.V.I.S. v8.1 autonomous research cycle status panel."""

from __future__ import annotations

import argparse

from .jarvis_v8_1_autonomous_research_cycle_status_panel import (
    AutonomousResearchCycleStatusPanelResult,
    audit_v8_1_autonomous_research_cycle_status_panel,
)


def build_v8_1_autonomous_research_cycle_status_panel_report(
    result: AutonomousResearchCycleStatusPanelResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v8.1 Autonomous Research Cycle Status Panel",
        "",
        f"status: {result.status}",
        f"panel status: {result.panel_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"item count: {result.item_count}",
        f"reviewed item count: {result.reviewed_item_count}",
        f"ready item count: {result.ready_item_count}",
        f"watch item count: {result.watch_item_count}",
        f"stale item count: {result.stale_item_count}",
        f"blocked item count: {result.blocked_item_count}",
        f"recommendation pack ready item count: {result.recommendation_pack_ready_item_count}",
        f"user-visible item count: {result.user_visible_item_count}",
        f"live fetch enabled item count: {result.live_fetch_enabled_item_count}",
        f"network call enabled item count: {result.network_call_enabled_item_count}",
        f"raw response storage enabled item count: {result.raw_response_storage_enabled_item_count}",
        f"live adapter record emission enabled item count: {result.live_adapter_record_emission_enabled_item_count}",
        f"compatible with v8.0 operator dashboard: {result.compatible_with_v8_0_operator_dashboard}",
        "",
        "## Research Cycle Status Items",
    ]

    for item in result.items:
        lines.extend(
            [
                "",
                f"### {item.item_id}",
                f"- title: {item.title}",
                f"- category: {item.category}",
                f"- state: {item.state}",
                f"- freshness: {item.freshness}",
                f"- priority: {item.priority}",
                f"- reviewed by J.A.R.V.I.S.: {item.reviewed_by_jarvis}",
                f"- ready for recommendation pack: {item.ready_for_recommendation_pack}",
                f"- blocked reason: {item.blocked_reason}",
                f"- watch focus: {item.watch_focus}",
                f"- evidence: {item.evidence}",
                f"- operator summary: {item.operator_summary}",
                f"- user visible: {item.user_visible}",
                f"- live fetch enabled: {item.live_fetch_enabled}",
                f"- network call enabled: {item.network_call_enabled}",
                f"- raw response storage enabled: {item.raw_response_storage_enabled}",
                f"- live adapter record emission enabled: {item.live_adapter_record_emission_enabled}",
                f"- creates buy request: {item.creates_buy_request}",
                f"- connects broker: {item.connects_broker}",
                f"- places order: {item.places_order}",
                f"- executes trade: {item.executes_trade}",
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
            f"- research cycle panel ready: {result.research_cycle_panel_ready}",
            f"- product visibility stage: {result.product_visibility_stage}",
            f"- public intelligence review visible: {result.public_intelligence_review_visible}",
            f"- candidate coverage visible: {result.candidate_coverage_visible}",
            f"- freshness status visible: {result.freshness_status_visible}",
            f"- recommendation pack readiness visible: {result.recommendation_pack_readiness_visible}",
            f"- next watch focus visible: {result.next_watch_focus_visible}",
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


def report_v8_1_autonomous_research_cycle_status_panel() -> str:
    return build_v8_1_autonomous_research_cycle_status_panel_report(
        audit_v8_1_autonomous_research_cycle_status_panel()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v8.1 autonomous research cycle status panel."
    )
    parser.parse_args()
    print(report_v8_1_autonomous_research_cycle_status_panel())


if __name__ == "__main__":
    main()
