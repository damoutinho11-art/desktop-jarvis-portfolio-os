"""Report CLI for J.A.R.V.I.S. v7.6 disabled live fetch adapter skeleton."""

from __future__ import annotations

import argparse

from .jarvis_v7_6_disabled_live_public_market_fetch_adapter_skeleton import (
    DisabledLivePublicMarketFetchAdapterSkeletonResult,
    audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton,
)


def build_v7_6_disabled_live_public_market_fetch_adapter_skeleton_report(
    result: DisabledLivePublicMarketFetchAdapterSkeletonResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v7.6 Disabled Live Public Market Fetch Adapter Skeleton",
        "",
        f"status: {result.status}",
        f"skeleton status: {result.skeleton_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"skeleton count: {result.skeleton_count}",
        f"selected candidate skeleton count: {result.selected_candidate_skeleton_count}",
        f"enabled adapter count: {result.enabled_adapter_count}",
        f"live fetch enabled count: {result.live_fetch_enabled_count}",
        f"network call allowed count: {result.network_call_allowed_count}",
        f"network call attempt count: {result.network_call_attempt_count}",
        f"raw response storage allowed count: {result.raw_response_storage_allowed_count}",
        f"raw response storage count: {result.raw_response_storage_count}",
        f"live adapter record emit count: {result.live_adapter_record_emit_count}",
        f"compatible with v7.3 fetch boundary: {result.compatible_with_v7_3_fetch_boundary}",
        f"compatible with v7.4 dry-run planner: {result.compatible_with_v7_4_dry_run_planner}",
        f"compatible with v7.5 response normalizer: {result.compatible_with_v7_5_response_normalizer}",
        "",
        "## Disabled Adapter Skeletons",
    ]

    for skeleton in result.adapter_skeletons:
        lines.extend(
            [
                "",
                f"### {skeleton.skeleton_id}",
                f"- candidate id: {skeleton.candidate_id}",
                f"- provider name: {skeleton.provider_name}",
                f"- endpoint category: {skeleton.endpoint_category}",
                f"- linked boundary request id: {skeleton.linked_boundary_request_id}",
                f"- linked dry-run plan id: {skeleton.linked_dry_run_plan_id}",
                f"- linked normalization input id: {skeleton.linked_normalization_input_id}",
                f"- boundary available: {skeleton.boundary_available}",
                f"- dry-run plan available: {skeleton.dry_run_plan_available}",
                f"- normalizer contract available: {skeleton.normalizer_contract_available}",
                f"- adapter enabled: {skeleton.adapter_enabled}",
                f"- live fetch enabled: {skeleton.live_fetch_enabled}",
                f"- network call allowed: {skeleton.network_call_allowed}",
                f"- network call attempted: {skeleton.network_call_attempted}",
                f"- raw response storage allowed: {skeleton.raw_response_storage_allowed}",
                f"- raw response stored: {skeleton.raw_response_stored}",
                f"- emits live adapter record: {skeleton.emits_live_adapter_record}",
                f"- creates buy request: {skeleton.creates_buy_request}",
                f"- connects broker: {skeleton.connects_broker}",
                f"- places order: {skeleton.places_order}",
                f"- executes trade: {skeleton.executes_trade}",
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
            f"- disabled adapter skeleton ready: {result.disabled_adapter_skeleton_ready}",
            f"- skeleton only: {result.skeleton_only}",
            f"- adapter disabled by default: {result.adapter_disabled_by_default}",
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


def report_v7_6_disabled_live_public_market_fetch_adapter_skeleton() -> str:
    return build_v7_6_disabled_live_public_market_fetch_adapter_skeleton_report(
        audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v7.6 disabled live fetch adapter skeleton."
    )
    parser.parse_args()
    print(report_v7_6_disabled_live_public_market_fetch_adapter_skeleton())


if __name__ == "__main__":
    main()
