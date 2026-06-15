"""Report CLI for J.A.R.V.I.S. v7.5 response normalizer contract."""

from __future__ import annotations

import argparse

from .jarvis_v7_5_live_public_market_intelligence_response_normalizer_contract import (
    PublicMarketResponseNormalizerContractResult,
    audit_v7_5_live_public_market_intelligence_response_normalizer_contract,
)


def build_v7_5_live_public_market_intelligence_response_normalizer_contract_report(
    result: PublicMarketResponseNormalizerContractResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v7.5 Live Public Market Intelligence Response Normalizer Contract",
        "",
        f"status: {result.status}",
        f"normalizer status: {result.normalizer_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"normalization input count: {result.normalization_input_count}",
        f"normalized adapter record count: {result.normalized_adapter_record_count}",
        f"selected candidate normalized record count: {result.selected_candidate_normalized_record_count}",
        f"raw response payload count: {result.raw_response_payload_count}",
        f"raw response storage count: {result.raw_response_storage_count}",
        f"network call attempt count: {result.network_call_attempt_count}",
        f"live fetch attempt count: {result.live_fetch_attempt_count}",
        f"compatible with v7.4 dry-run planner: {result.compatible_with_v7_4_dry_run_planner}",
        f"compatible with v7.1 adapter contract: {result.compatible_with_v7_1_adapter_contract}",
        f"selected candidate supported: {result.selected_candidate_supported}",
        f"selected candidate blocked: {result.selected_candidate_blocked}",
        "",
        "## Normalization Inputs",
    ]

    for item in result.normalization_inputs:
        lines.extend(
            [
                "",
                f"### {item.normalization_input_id}",
                f"- source plan id: {item.source_plan_id}",
                f"- source request id: {item.source_request_id}",
                f"- candidate id: {item.candidate_id}",
                f"- provider name: {item.provider_name}",
                f"- endpoint category: {item.endpoint_category}",
                f"- response kind: {item.response_kind}",
                f"- normalized signal type: {item.normalized_signal_type}",
                f"- normalized signal value: {item.normalized_signal_value}",
                f"- severity: {item.severity}",
                f"- confidence score: {item.confidence_score}",
                f"- public source quality: {item.public_source_quality}",
                f"- source url reference: {item.source_url_reference}",
                f"- freshness status: {item.freshness_status}",
                f"- supports recommendation: {item.supports_recommendation}",
                f"- blocks recommendation: {item.blocks_recommendation}",
                f"- raw response payload present: {item.raw_response_payload_present}",
                f"- raw response stored: {item.raw_response_stored}",
                f"- live fetch attempted: {item.live_fetch_attempted}",
                f"- network call attempted: {item.network_call_attempted}",
                f"- creates buy request: {item.creates_buy_request}",
                f"- connects broker: {item.connects_broker}",
                f"- places order: {item.places_order}",
                f"- executes trade: {item.executes_trade}",
                f"- normalized summary: {item.normalized_summary}",
            ]
        )

    lines.extend(["", "## Normalized Adapter Records"])
    for record in result.normalized_adapter_records:
        lines.extend(
            [
                "",
                f"### {record.record_id}",
                f"- adapter name: {record.adapter_name}",
                f"- candidate id: {record.candidate_id}",
                f"- signal type: {record.signal_type}",
                f"- severity: {record.severity}",
                f"- confidence score: {record.confidence_score}",
                f"- freshness status: {record.freshness_status}",
                f"- live fetch attempted: {record.live_fetch_attempted}",
                f"- creates buy request: {record.creates_buy_request}",
                f"- connects broker: {record.connects_broker}",
                f"- places order: {record.places_order}",
                f"- executes trade: {record.executes_trade}",
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
            f"- response normalizer contract ready: {result.response_normalizer_contract_ready}",
            f"- contract only: {result.contract_only}",
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


def report_v7_5_live_public_market_intelligence_response_normalizer_contract() -> str:
    return build_v7_5_live_public_market_intelligence_response_normalizer_contract_report(
        audit_v7_5_live_public_market_intelligence_response_normalizer_contract()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v7.5 response normalizer contract."
    )
    parser.parse_args()
    print(report_v7_5_live_public_market_intelligence_response_normalizer_contract())


if __name__ == "__main__":
    main()
