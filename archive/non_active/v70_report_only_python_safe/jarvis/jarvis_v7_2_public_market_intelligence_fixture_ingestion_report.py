"""Report CLI for J.A.R.V.I.S. v7.2 public market intelligence fixture ingestion."""

from __future__ import annotations

import argparse

from .jarvis_v7_2_public_market_intelligence_fixture_ingestion import (
    PublicMarketIntelligenceFixtureIngestionResult,
    audit_v7_2_public_market_intelligence_fixture_ingestion,
)


def build_v7_2_public_market_intelligence_fixture_ingestion_report(
    result: PublicMarketIntelligenceFixtureIngestionResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v7.2 Public Market Intelligence Fixture Ingestion",
        "",
        f"status: {result.status}",
        f"ingestion status: {result.ingestion_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"fixture dataset id: {result.fixture_dataset_id}",
        f"fixture row count: {result.fixture_row_count}",
        f"ingested record count: {result.ingested_record_count}",
        f"generated signal count: {result.generated_signal_count}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"compatible with v7.1 contract: {result.compatible_with_v7_1_contract}",
        f"selected candidate supported: {result.selected_candidate_supported}",
        f"selected candidate blocked: {result.selected_candidate_blocked}",
        "",
        "## Fixture Rows",
    ]

    for row in result.fixture_rows:
        lines.extend(
            [
                "",
                f"### {row.fixture_row_id}",
                f"- fixture dataset id: {row.fixture_dataset_id}",
                f"- candidate id: {row.candidate_id}",
                f"- signal type: {row.signal_type}",
                f"- signal value: {row.signal_value}",
                f"- severity: {row.severity}",
                f"- confidence score: {row.confidence_score}",
                f"- public source label: {row.public_source_label}",
                f"- public source quality: {row.public_source_quality}",
                f"- source url: {row.source_url}",
                f"- observed at UTC: {row.observed_at_utc}",
                f"- freshness status: {row.freshness_status}",
                f"- supports recommendation: {row.supports_recommendation}",
                f"- blocks recommendation: {row.blocks_recommendation}",
                f"- live fetch attempted: {row.live_fetch_attempted}",
                f"- creates buy request: {row.creates_buy_request}",
                f"- connects broker: {row.connects_broker}",
                f"- places order: {row.places_order}",
                f"- executes trade: {row.executes_trade}",
                f"- summary: {row.summary}",
            ]
        )

    lines.extend(["", "## Ingested Adapter Records"])
    for record in result.ingested_adapter_records:
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
            f"- fixture ingestion ready: {result.fixture_ingestion_ready}",
            f"- fixture ingestion only: {result.fixture_ingestion_only}",
            f"- live fetch deferred: {result.live_fetch_deferred}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v7_2_public_market_intelligence_fixture_ingestion() -> str:
    return build_v7_2_public_market_intelligence_fixture_ingestion_report(
        audit_v7_2_public_market_intelligence_fixture_ingestion()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v7.2 public market intelligence fixture ingestion."
    )
    parser.parse_args()
    print(report_v7_2_public_market_intelligence_fixture_ingestion())


if __name__ == "__main__":
    main()
