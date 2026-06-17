"""Report CLI for J.A.R.V.I.S. v8.4 operator command center closeout."""

from __future__ import annotations

import argparse

from .jarvis_v8_4_operator_command_center_closeout import (
    OperatorCommandCenterCloseoutResult,
    audit_v8_4_operator_command_center_closeout,
)


def build_v8_4_operator_command_center_closeout_report(
    result: OperatorCommandCenterCloseoutResult,
) -> str:
    lines = [
        "# J.A.R.V.I.S. v8.4 Operator Command Center Closeout",
        "",
        f"status: {result.status}",
        f"closeout status: {result.closeout_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"capability count: {result.capability_count}",
        f"ready capability count: {result.ready_capability_count}",
        f"user-visible capability count: {result.user_visible_capability_count}",
        f"unsafe capability count: {result.unsafe_capability_count}",
        "",
        "## Capabilities",
    ]

    for capability in result.capabilities:
        lines.extend(
            [
                "",
                f"### {capability.capability_id}",
                f"- stage: {capability.stage}",
                f"- title: {capability.title}",
                f"- product value: {capability.product_value}",
                f"- evidence: {capability.evidence}",
                f"- ready: {capability.ready}",
                f"- user visible: {capability.user_visible}",
                f"- creates buy request: {capability.creates_buy_request}",
                f"- connects broker: {capability.connects_broker}",
                f"- places order: {capability.places_order}",
                f"- executes trade: {capability.executes_trade}",
                f"- live fetch enabled: {capability.live_fetch_enabled}",
                f"- network call enabled: {capability.network_call_enabled}",
                f"- raw response storage enabled: {capability.raw_response_storage_enabled}",
                f"- live adapter record emission enabled: {capability.live_adapter_record_emission_enabled}",
            ]
        )

    lines.extend(["", "## Warnings"])
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "## Closeout Safety",
            "",
            f"- v8.0 ready: {result.v8_0_ready}",
            f"- v8.1 ready: {result.v8_1_ready}",
            f"- v8.2 ready: {result.v8_2_ready}",
            f"- v8.3 ready: {result.v8_3_ready}",
            f"- v8 product layer complete: {result.v8_product_layer_complete}",
            f"- dashboard visibility complete: {result.dashboard_visibility_complete}",
            f"- research cycle visibility complete: {result.research_cycle_visibility_complete}",
            f"- evidence pack integration complete: {result.evidence_pack_integration_complete}",
            f"- action brief generation complete: {result.action_brief_generation_complete}",
            f"- product value not redundant: {result.product_value_not_redundant}",
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


def report_v8_4_operator_command_center_closeout() -> str:
    return build_v8_4_operator_command_center_closeout_report(
        audit_v8_4_operator_command_center_closeout()
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Report J.A.R.V.I.S. v8.4 operator command center closeout.")
    parser.parse_args()
    print(report_v8_4_operator_command_center_closeout())


if __name__ == "__main__":
    main()
