"""Report CLI for J.A.R.V.I.S. v10.1 unified operator runtime."""

from __future__ import annotations

import argparse

from .jarvis_v10_1_unified_operator_runtime import (
    UnifiedOperatorRuntimeResult,
    audit_v10_1_unified_operator_runtime,
)


def build_v10_1_unified_operator_runtime_report(result: UnifiedOperatorRuntimeResult) -> str:
    lines = [
        "# J.A.R.V.I.S. v10.1 Unified Operator Runtime",
        "",
        f"status: {result.status}",
        f"runtime status: {result.runtime_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"component count: {result.component_count}",
        f"ready component count: {result.ready_component_count}",
        f"blocked component count: {result.blocked_component_count}",
        f"warning count: {result.warning_count}",
        f"blocker count: {result.blocker_count}",
        "",
        "## Data Refresh",
        f"- data refresh status: {result.data_refresh_status}",
        f"- source manifest loaded: {result.data_source_manifest_loaded}",
        f"- autonomous refresh ready: {result.autonomous_refresh_ready}",
        f"- raw public data refreshed: {result.raw_public_data_refreshed}",
        f"- ready for downstream normalization: {result.ready_for_downstream_normalization}",
        f"- ready for downstream source quality gate: {result.ready_for_downstream_source_quality_gate}",
        f"- recommendation quality current data: {result.recommendation_quality_current_data}",
        "",
        "## Product Layers",
        f"- evidence pack status: {result.evidence_pack_status}",
        f"- recommendation status: {result.recommendation_status}",
        f"- recommendation dashboard status: {result.recommendation_dashboard_status}",
        f"- public market dashboard status: {result.public_market_dashboard_status}",
        f"- action brief status: {result.action_brief_status}",
        "",
        "## Components",
    ]

    for component in result.components:
        lines.extend(
            [
                "",
                f"### {component.component_id}",
                f"- title: {component.title}",
                f"- status: {component.status}",
                f"- ready: {component.ready}",
                f"- summary: {component.summary}",
                f"- user visible: {component.user_visible}",
                f"- creates buy request: {component.creates_buy_request}",
                f"- connects broker: {component.connects_broker}",
                f"- places order: {component.places_order}",
                f"- executes trade: {component.executes_trade}",
            ]
        )

    lines.extend(
        [
            "",
            "## Voice-Ready Summary",
            f"- voice summary ready: {result.voice_summary_ready}",
            f"- voice interface available: {result.voice_interface_available}",
            f"- summary: {result.voice_summary}",
            "",
            "## Warnings",
        ]
    )
    lines.extend(f"- {warning}" for warning in result.warnings) if result.warnings else lines.append("- none")

    lines.extend(["", "## Blockers"])
    lines.extend(f"- {blocker}" for blocker in result.blockers) if result.blockers else lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety",
            f"- unified operator runtime ready: {result.unified_operator_runtime_ready}",
            f"- one command runtime: {result.one_command_runtime}",
            f"- product mode runtime: {result.product_mode_runtime}",
            f"- data refresh integrated: {result.data_refresh_integrated}",
            f"- evidence pack integrated: {result.evidence_pack_integrated}",
            f"- recommendation integrated: {result.recommendation_integrated}",
            f"- dashboard integrated: {result.dashboard_integrated}",
            f"- action brief integrated: {result.action_brief_integrated}",
            f"- voice-ready summary integrated: {result.voice_ready_summary_integrated}",
            f"- UI shell not built yet: {result.ui_shell_not_built_yet}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
            f"- credentials forbidden: {result.credentials_forbidden}",
            f"- private account data ingestion forbidden: {result.private_account_data_ingestion_forbidden}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v10_1_unified_operator_runtime() -> str:
    return build_v10_1_unified_operator_runtime_report(audit_v10_1_unified_operator_runtime())


def main() -> None:
    parser = argparse.ArgumentParser(description="Report J.A.R.V.I.S. v10.1 unified operator runtime.")
    parser.parse_args()
    print(report_v10_1_unified_operator_runtime())


if __name__ == "__main__":
    main()
