"""Report CLI for J.A.R.V.I.S. v7.4 live public market intelligence dry-run planner."""

from __future__ import annotations

import argparse

from .jarvis_v7_4_live_public_market_intelligence_dry_run_planner import (
    LivePublicMarketDryRunPlannerResult,
    audit_v7_4_live_public_market_intelligence_dry_run_planner,
)


def build_v7_4_live_public_market_intelligence_dry_run_planner_report(
    result: LivePublicMarketDryRunPlannerResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v7.4 Live Public Market Intelligence Dry-Run Planner",
        "",
        f"status: {result.status}",
        f"dry-run status: {result.dry_run_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"dry-run plan count: {result.dry_run_plan_count}",
        f"selected candidate plan count: {result.selected_candidate_plan_count}",
        f"planned network call count: {result.planned_network_call_count}",
        f"planned live fetch count: {result.planned_live_fetch_count}",
        f"raw response storage plan count: {result.raw_response_storage_plan_count}",
        f"compatible with v7.3 fetch boundary: {result.compatible_with_v7_3_fetch_boundary}",
        "",
        "## Dry-Run Fetch Plans",
    ]

    for plan in result.dry_run_fetch_plans:
        lines.extend(
            [
                "",
                f"### {plan.plan_id}",
                f"- source request id: {plan.source_request_id}",
                f"- candidate id: {plan.candidate_id}",
                f"- provider name: {plan.provider_name}",
                f"- provider type: {plan.provider_type}",
                f"- endpoint category: {plan.endpoint_category}",
                f"- planned method: {plan.planned_method}",
                f"- planned url: {plan.planned_url}",
                f"- planned reason: {plan.planned_reason}",
                f"- expected adapter record type: {plan.expected_adapter_record_type}",
                f"- timeout seconds: {plan.timeout_seconds}",
                f"- max records: {plan.max_records}",
                f"- rate limit per minute: {plan.rate_limit_per_minute}",
                f"- requires api key: {plan.requires_api_key}",
                f"- dry-run only: {plan.dry_run_only}",
                f"- live fetch allowed: {plan.live_fetch_allowed}",
                f"- network call allowed: {plan.network_call_allowed}",
                f"- raw response storage allowed: {plan.raw_response_storage_allowed}",
                f"- creates buy request: {plan.creates_buy_request}",
                f"- connects broker: {plan.connects_broker}",
                f"- places order: {plan.places_order}",
                f"- executes trade: {plan.executes_trade}",
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
            f"- dry-run planner ready: {result.dry_run_planner_ready}",
            f"- dry-run only: {result.dry_run_only}",
            f"- live fetch deferred: {result.live_fetch_deferred}",
            f"- network calls deferred: {result.network_calls_deferred}",
            f"- raw response storage deferred: {result.raw_response_storage_deferred}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v7_4_live_public_market_intelligence_dry_run_planner() -> str:
    return build_v7_4_live_public_market_intelligence_dry_run_planner_report(
        audit_v7_4_live_public_market_intelligence_dry_run_planner()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v7.4 live public market intelligence dry-run planner."
    )
    parser.parse_args()
    print(report_v7_4_live_public_market_intelligence_dry_run_planner())


if __name__ == "__main__":
    main()
