"""Report CLI for J.A.R.V.I.S. v8.2 weekly recommendation evidence pack integration."""

from __future__ import annotations

import argparse

from .jarvis_v8_2_weekly_recommendation_evidence_pack_integration import (
    WeeklyRecommendationEvidencePackIntegrationResult,
    audit_v8_2_weekly_recommendation_evidence_pack_integration,
)


def build_v8_2_weekly_recommendation_evidence_pack_integration_report(
    result: WeeklyRecommendationEvidencePackIntegrationResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v8.2 Weekly Recommendation Evidence Pack Integration",
        "",
        f"status: {result.status}",
        f"pack status: {result.pack_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"section count: {result.section_count}",
        f"included section count: {result.included_section_count}",
        f"ready section count: {result.ready_section_count}",
        f"watch section count: {result.watch_section_count}",
        f"blocked section count: {result.blocked_section_count}",
        f"ready for pack section count: {result.ready_for_pack_section_count}",
        f"user-visible section count: {result.user_visible_section_count}",
        f"live fetch enabled section count: {result.live_fetch_enabled_section_count}",
        f"network call enabled section count: {result.network_call_enabled_section_count}",
        f"raw response storage enabled section count: {result.raw_response_storage_enabled_section_count}",
        f"live adapter record emission enabled section count: {result.live_adapter_record_emission_enabled_section_count}",
        f"compatible with v8.1 research cycle panel: {result.compatible_with_v8_1_research_cycle_panel}",
        "",
        "## Evidence Pack Sections",
    ]

    for section in result.sections:
        lines.extend(
            [
                "",
                f"### {section.section_id}",
                f"- title: {section.title}",
                f"- source item id: {section.source_item_id}",
                f"- category: {section.category}",
                f"- state: {section.state}",
                f"- freshness: {section.freshness}",
                f"- evidence summary: {section.evidence_summary}",
                f"- evidence detail: {section.evidence_detail}",
                f"- recommendation relevance: {section.recommendation_relevance}",
                f"- status reason: {section.status_reason}",
                f"- included in weekly pack: {section.included_in_weekly_pack}",
                f"- ready for pack: {section.ready_for_pack}",
                f"- watch only: {section.watch_only}",
                f"- user visible: {section.user_visible}",
                f"- final user action required: {section.final_user_action_required}",
                f"- live fetch enabled: {section.live_fetch_enabled}",
                f"- network call enabled: {section.network_call_enabled}",
                f"- raw response storage enabled: {section.raw_response_storage_enabled}",
                f"- live adapter record emission enabled: {section.live_adapter_record_emission_enabled}",
                f"- creates buy request: {section.creates_buy_request}",
                f"- connects broker: {section.connects_broker}",
                f"- places order: {section.places_order}",
                f"- executes trade: {section.executes_trade}",
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
            f"- evidence pack integration ready: {result.evidence_pack_integration_ready}",
            f"- product integration stage: {result.product_integration_stage}",
            f"- research review integrated: {result.research_review_integrated}",
            f"- selected candidate integrated: {result.selected_candidate_integrated}",
            f"- public intelligence integrated: {result.public_intelligence_integrated}",
            f"- freshness watch integrated: {result.freshness_watch_integrated}",
            f"- execution boundary integrated: {result.execution_boundary_integrated}",
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


def report_v8_2_weekly_recommendation_evidence_pack_integration() -> str:
    return build_v8_2_weekly_recommendation_evidence_pack_integration_report(
        audit_v8_2_weekly_recommendation_evidence_pack_integration()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v8.2 weekly recommendation evidence pack integration."
    )
    parser.parse_args()
    print(report_v8_2_weekly_recommendation_evidence_pack_integration())


if __name__ == "__main__":
    main()
