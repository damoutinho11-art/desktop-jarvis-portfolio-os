"""Report CLI for J.A.R.V.I.S. v9.0 public market data enablement decision layer."""

from __future__ import annotations

import argparse

from .jarvis_v9_0_public_market_data_enablement_decision_layer import (
    PublicMarketDataEnablementDecisionLayerResult,
    audit_v9_0_public_market_data_enablement_decision_layer,
)


def build_v9_0_public_market_data_enablement_decision_layer_report(
    result: PublicMarketDataEnablementDecisionLayerResult,
) -> str:
    lines = [
        "# J.A.R.V.I.S. v9.0 Public Market Data Enablement Decision Layer",
        "",
        f"status: {result.status}",
        f"decision layer status: {result.decision_layer_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"decision count: {result.decision_count}",
        f"dry-run allowed decision count: {result.dry_run_allowed_decision_count}",
        f"live allowed decision count: {result.live_allowed_decision_count}",
        f"authorization required decision count: {result.authorization_required_decision_count}",
        f"live blocking decision count: {result.live_blocking_decision_count}",
        f"compatible with v7.10 readiness closeout: {result.compatible_with_v7_10_readiness_closeout}",
        f"compatible with v8.4 command center closeout: {result.compatible_with_v8_4_command_center_closeout}",
        "",
        "## Decisions",
    ]

    for decision in result.decisions:
        lines.extend(
            [
                "",
                f"### {decision.decision_id}",
                f"- title: {decision.title}",
                f"- decision: {decision.decision}",
                f"- reason: {decision.reason}",
                f"- evidence: {decision.evidence}",
                f"- allowed in dry-run: {decision.allowed_in_dry_run}",
                f"- live mode allowed: {decision.live_mode_allowed}",
                f"- requires explicit operator authorization: {decision.requires_explicit_operator_authorization}",
                f"- blocks live fetch: {decision.blocks_live_fetch}",
                f"- user visible: {decision.user_visible}",
                f"- creates buy request: {decision.creates_buy_request}",
                f"- connects broker: {decision.connects_broker}",
                f"- places order: {decision.places_order}",
                f"- executes trade: {decision.executes_trade}",
                f"- network call enabled: {decision.network_call_enabled}",
                f"- raw response storage enabled: {decision.raw_response_storage_enabled}",
                f"- live adapter record emission enabled: {decision.live_adapter_record_emission_enabled}",
            ]
        )

    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety",
            "",
            f"- enablement decision layer ready: {result.enablement_decision_layer_ready}",
            f"- source selection not repeated: {result.source_selection_not_repeated}",
            f"- dry-run planning allowed: {result.dry_run_planning_allowed}",
            f"- live mode blocked: {result.live_mode_blocked}",
            f"- explicit operator authorization required: {result.explicit_operator_authorization_required}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
            f"- network calls deferred: {result.network_calls_deferred}",
            f"- raw response storage deferred: {result.raw_response_storage_deferred}",
            f"- live adapter record emission deferred: {result.live_adapter_record_emission_deferred}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v9_0_public_market_data_enablement_decision_layer() -> str:
    return build_v9_0_public_market_data_enablement_decision_layer_report(
        audit_v9_0_public_market_data_enablement_decision_layer()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v9.0 public market data enablement decision layer."
    )
    parser.parse_args()
    print(report_v9_0_public_market_data_enablement_decision_layer())


if __name__ == "__main__":
    main()
