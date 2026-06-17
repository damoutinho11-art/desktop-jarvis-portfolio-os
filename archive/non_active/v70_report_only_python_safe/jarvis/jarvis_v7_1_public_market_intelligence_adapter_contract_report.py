"""Report CLI for J.A.R.V.I.S. v7.1 public market intelligence adapter contract."""

from __future__ import annotations

import argparse

from .jarvis_v7_1_public_market_intelligence_adapter_contract import (
    PublicMarketIntelligenceAdapterContractResult,
    audit_v7_1_public_market_intelligence_adapter_contract,
)


def build_v7_1_public_market_intelligence_adapter_contract_report(
    result: PublicMarketIntelligenceAdapterContractResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v7.1 Public Market Intelligence Adapter Contract",
        "",
        f"status: {result.status}",
        f"adapter status: {result.adapter_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"adapter record count: {result.adapter_record_count}",
        f"generated signal count: {result.generated_signal_count}",
        f"compatible with v7.0: {result.compatible_with_v7_0}",
        f"selected candidate supported: {result.selected_candidate_supported}",
        f"selected candidate blocked: {result.selected_candidate_blocked}",
        "",
        "## Public Adapter Records",
    ]

    for record in result.public_adapter_records:
        lines.extend(
            [
                "",
                f"### {record.record_id}",
                f"- adapter name: {record.adapter_name}",
                f"- candidate id: {record.candidate_id}",
                f"- signal type: {record.signal_type}",
                f"- signal value: {record.signal_value}",
                f"- severity: {record.severity}",
                f"- confidence score: {record.confidence_score}",
                f"- public source label: {record.public_source_label}",
                f"- public source quality: {record.public_source_quality}",
                f"- source url: {record.source_url}",
                f"- observed at UTC: {record.observed_at_utc}",
                f"- freshness status: {record.freshness_status}",
                f"- supports recommendation: {record.supports_recommendation}",
                f"- blocks recommendation: {record.blocks_recommendation}",
                f"- live fetch attempted: {record.live_fetch_attempted}",
                f"- creates buy request: {record.creates_buy_request}",
                f"- connects broker: {record.connects_broker}",
                f"- places order: {record.places_order}",
                f"- executes trade: {record.executes_trade}",
                f"- summary: {record.summary}",
            ]
        )

    lines.extend(["", "## Generated Signals"])
    for signal in result.generated_signals:
        lines.extend(
            [
                "",
                f"### {signal.signal_id}",
                f"- candidate id: {signal.candidate_id}",
                f"- signal type: {signal.signal_type}",
                f"- severity: {signal.severity}",
                f"- confidence score: {signal.confidence_score}",
                f"- freshness status: {signal.freshness_status}",
                f"- source label: {signal.source_label}",
                f"- supports recommendation: {signal.supports_recommendation}",
                f"- blocks recommendation: {signal.blocks_recommendation}",
                f"- creates buy request: {signal.creates_buy_request}",
                f"- connects broker: {signal.connects_broker}",
                f"- places order: {signal.places_order}",
                f"- executes trade: {signal.executes_trade}",
                f"- summary: {signal.summary}",
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
            f"- adapter contract ready: {result.adapter_contract_ready}",
            f"- contract only: {result.contract_only}",
            f"- live fetch deferred: {result.live_fetch_deferred}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v7_1_public_market_intelligence_adapter_contract() -> str:
    return build_v7_1_public_market_intelligence_adapter_contract_report(
        audit_v7_1_public_market_intelligence_adapter_contract()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v7.1 public market intelligence adapter contract."
    )
    parser.parse_args()
    print(report_v7_1_public_market_intelligence_adapter_contract())


if __name__ == "__main__":
    main()
