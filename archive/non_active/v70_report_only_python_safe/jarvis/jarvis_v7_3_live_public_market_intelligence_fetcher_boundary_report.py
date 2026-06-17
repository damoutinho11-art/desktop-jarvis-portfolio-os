"""Report CLI for J.A.R.V.I.S. v7.3 live public market intelligence fetcher boundary."""

from __future__ import annotations

import argparse

from .jarvis_v7_3_live_public_market_intelligence_fetcher_boundary import (
    LivePublicMarketFetcherBoundaryResult,
    audit_v7_3_live_public_market_intelligence_fetcher_boundary,
)


def build_v7_3_live_public_market_intelligence_fetcher_boundary_report(
    result: LivePublicMarketFetcherBoundaryResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v7.3 Live Public Market Intelligence Fetcher Boundary",
        "",
        f"status: {result.status}",
        f"boundary status: {result.boundary_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"fetch boundary request count: {result.fetch_boundary_request_count}",
        f"disabled live fetch count: {result.disabled_live_fetch_count}",
        f"network call attempt count: {result.network_call_attempt_count}",
        f"compatible with v7.2 fixture ingestion: {result.compatible_with_v7_2_fixture_ingestion}",
        "",
        "## Fetch Boundary Requests",
    ]

    for request in result.fetch_boundary_requests:
        lines.extend(
            [
                "",
                f"### {request.request_id}",
                f"- provider name: {request.provider_name}",
                f"- provider type: {request.provider_type}",
                f"- endpoint category: {request.endpoint_category}",
                f"- candidate id: {request.candidate_id}",
                f"- method: {request.method}",
                f"- url template: {request.url_template}",
                f"- request purpose: {request.request_purpose}",
                f"- expected adapter record type: {request.expected_adapter_record_type}",
                f"- timeout seconds: {request.timeout_seconds}",
                f"- max records: {request.max_records}",
                f"- rate limit per minute: {request.rate_limit_per_minute}",
                f"- requires api key: {request.requires_api_key}",
                f"- live fetch enabled: {request.live_fetch_enabled}",
                f"- network call attempted: {request.network_call_attempted}",
                f"- stores raw response: {request.stores_raw_response}",
                f"- creates buy request: {request.creates_buy_request}",
                f"- connects broker: {request.connects_broker}",
                f"- places order: {request.places_order}",
                f"- executes trade: {request.executes_trade}",
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
            f"- live fetch boundary ready: {result.live_fetch_boundary_ready}",
            f"- boundary only: {result.boundary_only}",
            f"- live fetch disabled by default: {result.live_fetch_disabled_by_default}",
            f"- network calls deferred: {result.network_calls_deferred}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v7_3_live_public_market_intelligence_fetcher_boundary() -> str:
    return build_v7_3_live_public_market_intelligence_fetcher_boundary_report(
        audit_v7_3_live_public_market_intelligence_fetcher_boundary()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v7.3 live public market intelligence fetcher boundary."
    )
    parser.parse_args()
    print(report_v7_3_live_public_market_intelligence_fetcher_boundary())


if __name__ == "__main__":
    main()
