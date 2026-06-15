"""J.A.R.V.I.S. v7.2 public market intelligence fixture ingestion.

This stage ingests fixture-shaped public market/news/risk rows through the v7.1
public market intelligence adapter contract.

Safety boundary:
- fixture ingestion only
- no live fetching
- no buy request creation
- no broker/API connection
- no order placement
- no trade execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v7_0_autonomous_market_intelligence_expansion import (
    SIGNAL_BLOCKING,
    SIGNAL_CAUTION,
    SIGNAL_NEUTRAL,
    SIGNAL_SUPPORTIVE,
)
from .jarvis_v7_1_public_market_intelligence_adapter_contract import (
    ALLOWED_SEVERITIES,
    ALLOWED_SOURCE_QUALITIES,
    PublicMarketIntelligenceAdapterRecord,
    STATUS_READY as V7_1_STATUS_READY,
    audit_v7_1_public_market_intelligence_adapter_contract,
)


STATUS_READY = "JARVIS_V7_2_PUBLIC_MARKET_INTELLIGENCE_FIXTURE_INGESTION_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V7_2_PUBLIC_MARKET_INTELLIGENCE_FIXTURE_INGESTION_BLOCKED_SAFE"

NEXT_STAGE = "v7_3_live_public_market_intelligence_fetcher_boundary"

INGESTION_STATUS_READY = "PUBLIC_MARKET_INTELLIGENCE_FIXTURE_INGESTED"
INGESTION_STATUS_BLOCKED = "PUBLIC_MARKET_INTELLIGENCE_FIXTURE_INGESTION_BLOCKED"

FIXTURE_DATASET_ID = "jarvis_v7_2_public_market_intelligence_fixture"


@dataclass(frozen=True)
class PublicMarketIntelligenceFixtureRow:
    fixture_row_id: str
    fixture_dataset_id: str
    candidate_id: str
    signal_type: str
    signal_value: str
    severity: str
    confidence_score: int
    summary: str
    public_source_label: str
    public_source_quality: str
    source_url: str
    observed_at_utc: str
    freshness_status: str
    supports_recommendation: bool
    blocks_recommendation: bool
    live_fetch_attempted: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_fixture_row_only(self) -> bool:
        return (
            not self.live_fetch_attempted
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_adapter_record(self) -> PublicMarketIntelligenceAdapterRecord:
        return PublicMarketIntelligenceAdapterRecord(
            record_id=self.fixture_row_id,
            adapter_name="jarvis_v7_2_fixture_ingestion_adapter",
            candidate_id=self.candidate_id,
            signal_type=self.signal_type,
            signal_value=self.signal_value,
            severity=self.severity,
            confidence_score=self.confidence_score,
            summary=self.summary,
            public_source_label=self.public_source_label,
            public_source_quality=self.public_source_quality,
            source_url=self.source_url,
            observed_at_utc=self.observed_at_utc,
            freshness_status=self.freshness_status,
            supports_recommendation=self.supports_recommendation,
            blocks_recommendation=self.blocks_recommendation,
            live_fetch_attempted=self.live_fetch_attempted,
            creates_buy_request=self.creates_buy_request,
            connects_broker=self.connects_broker,
            places_order=self.places_order,
            executes_trade=self.executes_trade,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "fixture_row_id": self.fixture_row_id,
            "fixture_dataset_id": self.fixture_dataset_id,
            "candidate_id": self.candidate_id,
            "signal_type": self.signal_type,
            "signal_value": self.signal_value,
            "severity": self.severity,
            "confidence_score": self.confidence_score,
            "summary": self.summary,
            "public_source_label": self.public_source_label,
            "public_source_quality": self.public_source_quality,
            "source_url": self.source_url,
            "observed_at_utc": self.observed_at_utc,
            "freshness_status": self.freshness_status,
            "supports_recommendation": self.supports_recommendation,
            "blocks_recommendation": self.blocks_recommendation,
            "live_fetch_attempted": self.live_fetch_attempted,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_fixture_row_only": self.safe_fixture_row_only(),
        }


@dataclass(frozen=True)
class PublicMarketIntelligenceFixtureIngestionResult:
    status: str
    ingestion_status: str
    recommended_next_stage: str
    fixture_dataset_id: str
    fixture_row_count: int
    ingested_record_count: int
    generated_signal_count: int
    selected_candidate_id: str
    selected_sleeve_id: str
    compatible_with_v7_1_contract: bool
    selected_candidate_supported: bool
    selected_candidate_blocked: bool
    fixture_rows: tuple[PublicMarketIntelligenceFixtureRow, ...]
    ingested_adapter_records: tuple[PublicMarketIntelligenceAdapterRecord, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    fixture_ingestion_ready: bool
    fixture_ingestion_only: bool
    live_fetch_deferred: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "ingestion_status": self.ingestion_status,
            "recommended_next_stage": self.recommended_next_stage,
            "fixture_dataset_id": self.fixture_dataset_id,
            "fixture_row_count": self.fixture_row_count,
            "ingested_record_count": self.ingested_record_count,
            "generated_signal_count": self.generated_signal_count,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "compatible_with_v7_1_contract": self.compatible_with_v7_1_contract,
            "selected_candidate_supported": self.selected_candidate_supported,
            "selected_candidate_blocked": self.selected_candidate_blocked,
            "fixture_rows": [row.to_dict() for row in self.fixture_rows],
            "ingested_adapter_records": [record.to_dict() for record in self.ingested_adapter_records],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "fixture_ingestion_ready": self.fixture_ingestion_ready,
            "fixture_ingestion_only": self.fixture_ingestion_only,
            "live_fetch_deferred": self.live_fetch_deferred,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _fixture_row(
    fixture_row_id: str,
    candidate_id: str,
    signal_type: str,
    signal_value: str,
    severity: str,
    confidence_score: int,
    summary: str,
    public_source_quality: str,
    supports_recommendation: bool,
    blocks_recommendation: bool = False,
) -> PublicMarketIntelligenceFixtureRow:
    return PublicMarketIntelligenceFixtureRow(
        fixture_row_id=fixture_row_id,
        fixture_dataset_id=FIXTURE_DATASET_ID,
        candidate_id=candidate_id,
        signal_type=signal_type,
        signal_value=signal_value,
        severity=severity,
        confidence_score=confidence_score,
        summary=summary,
        public_source_label="v7_2_fixture_public_source",
        public_source_quality=public_source_quality,
        source_url="https://example.invalid/v7-2-public-market-intelligence-fixture",
        observed_at_utc="2026-06-15T00:00:00Z",
        freshness_status="FIXTURE_READY_NO_LIVE_FETCH",
        supports_recommendation=supports_recommendation,
        blocks_recommendation=blocks_recommendation,
        live_fetch_attempted=False,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_example_public_market_intelligence_fixture_rows() -> tuple[
    PublicMarketIntelligenceFixtureRow, ...
]:
    return (
        _fixture_row(
            "v7_2_btc_fixture_support",
            "btc_candidate",
            "PUBLIC_CRYPTO_MARKET_CONTEXT_FIXTURE",
            "BTC fixture context supports visibility after policy-underweight signal.",
            SIGNAL_SUPPORTIVE,
            92,
            "Fixture ingestion proves BTC supportive public context can enter the v7 adapter contract.",
            "PUBLIC_CRYPTO_MARKET_DATA",
            True,
        ),
        _fixture_row(
            "v7_2_btc_fixture_caution",
            "btc_candidate",
            "PUBLIC_CRYPTO_VOLATILITY_FIXTURE",
            "BTC fixture volatility caution remains active.",
            SIGNAL_CAUTION,
            84,
            "Fixture ingestion preserves crypto volatility caution without blocking the selected candidate.",
            "PUBLIC_CRYPTO_MARKET_DATA",
            True,
        ),
        _fixture_row(
            "v7_2_global_core_fixture_support",
            "global_all_world_etf_candidate",
            "PUBLIC_CORE_ETF_CONTEXT_FIXTURE",
            "Global all-world ETF fixture remains core alternative context.",
            SIGNAL_SUPPORTIVE,
            88,
            "Fixture ingestion keeps diversified ETF context available as a non-executable signal.",
            "PUBLIC_INDEX_PROVIDER",
            True,
        ),
        _fixture_row(
            "v7_2_quality_factor_fixture_neutral",
            "quality_factor_etf_candidate",
            "PUBLIC_FACTOR_ETF_CONTEXT_FIXTURE",
            "Quality factor ETF fixture remains neutral secondary context.",
            SIGNAL_NEUTRAL,
            70,
            "Fixture ingestion keeps secondary factor context available without forcing a recommendation.",
            "PUBLIC_MARKET_DATA",
            False,
        ),
    )


def ingest_fixture_rows_as_adapter_records(
    fixture_rows: tuple[PublicMarketIntelligenceFixtureRow, ...],
) -> tuple[PublicMarketIntelligenceAdapterRecord, ...]:
    return tuple(row.to_adapter_record() for row in fixture_rows)


def audit_v7_2_public_market_intelligence_fixture_ingestion(
    fixture_rows: tuple[PublicMarketIntelligenceFixtureRow, ...] | None | object = None,
) -> PublicMarketIntelligenceFixtureIngestionResult:
    if fixture_rows is None:
        effective_rows = build_example_public_market_intelligence_fixture_rows()
        invalid_override = False
    elif isinstance(fixture_rows, tuple):
        effective_rows = fixture_rows
        invalid_override = False
    else:
        effective_rows = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v7.2 ingests public market-intelligence fixtures only.",
        "No live public fetch is performed in v7.2.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Fixture override must be a tuple of PublicMarketIntelligenceFixtureRow.")

    if not effective_rows:
        blockers.append("No public market intelligence fixture rows were produced.")

    row_ids: list[str] = []
    clean_rows: list[PublicMarketIntelligenceFixtureRow] = []

    for index, row in enumerate(effective_rows):
        if not isinstance(row, PublicMarketIntelligenceFixtureRow):
            blockers.append(f"Fixture row at index {index} must be a PublicMarketIntelligenceFixtureRow.")
            continue

        clean_rows.append(row)
        row_ids.append(row.fixture_row_id)

        if not row.fixture_row_id.strip():
            blockers.append("Fixture row ID is required.")
        if row.fixture_dataset_id != FIXTURE_DATASET_ID:
            blockers.append(f"{row.fixture_row_id}: fixture dataset ID is invalid.")
        if not row.candidate_id.strip():
            blockers.append(f"{row.fixture_row_id}: candidate ID is required.")
        if not row.signal_type.strip():
            blockers.append(f"{row.fixture_row_id}: signal type is required.")
        if not row.summary.strip():
            blockers.append(f"{row.fixture_row_id}: summary is required.")
        if row.severity not in ALLOWED_SEVERITIES:
            blockers.append(f"{row.fixture_row_id}: severity is not allowed.")
        if row.public_source_quality not in ALLOWED_SOURCE_QUALITIES:
            blockers.append(f"{row.fixture_row_id}: public source quality is not allowed.")
        if row.confidence_score < 0 or row.confidence_score > 100:
            blockers.append(f"{row.fixture_row_id}: confidence score must be 0..100.")
        if not row.source_url.strip():
            blockers.append(f"{row.fixture_row_id}: source URL placeholder/reference is required.")
        if row.live_fetch_attempted:
            blockers.append(f"{row.fixture_row_id}: live fetching is forbidden in v7.2.")
        if not row.safe_fixture_row_only():
            blockers.append(f"{row.fixture_row_id}: fixture row must remain fixture-ingestion-only.")
        if row.creates_buy_request:
            blockers.append(f"{row.fixture_row_id}: buy request creation is forbidden.")
        if row.connects_broker:
            blockers.append(f"{row.fixture_row_id}: broker connection is forbidden.")
        if row.places_order:
            blockers.append(f"{row.fixture_row_id}: order placement is forbidden.")
        if row.executes_trade:
            blockers.append(f"{row.fixture_row_id}: trade execution is forbidden.")

    if len(row_ids) != len(set(row_ids)):
        blockers.append("Public market intelligence fixture row IDs must be unique.")

    clean_row_tuple = tuple(clean_rows)
    ingested_records = ingest_fixture_rows_as_adapter_records(clean_row_tuple)

    adapter_result = audit_v7_1_public_market_intelligence_adapter_contract(ingested_records)

    compatible_with_v7_1 = adapter_result.status == V7_1_STATUS_READY
    selected_candidate_supported = adapter_result.selected_candidate_supported
    selected_candidate_blocked = adapter_result.selected_candidate_blocked

    if not compatible_with_v7_1:
        blockers.append("Ingested fixture records are not compatible with the v7.1 adapter contract.")
    if selected_candidate_blocked:
        blockers.append("Ingested fixture records block the selected weekly candidate.")

    safety_flags = {
        "fixture_ingestion_ready": False,
        "fixture_ingestion_only": True,
        "live_fetch_deferred": True,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["fixture_ingestion_only"]:
        blockers.append("v7.2 must remain fixture-ingestion-only.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v7.2 must defer live fetching.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v7.2 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v7.2 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v7.2 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v7.2 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return PublicMarketIntelligenceFixtureIngestionResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        ingestion_status=INGESTION_STATUS_READY if ready else INGESTION_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        fixture_dataset_id=FIXTURE_DATASET_ID,
        fixture_row_count=len(clean_row_tuple),
        ingested_record_count=len(ingested_records),
        generated_signal_count=adapter_result.generated_signal_count,
        selected_candidate_id=adapter_result.selected_candidate_id,
        selected_sleeve_id=adapter_result.selected_sleeve_id,
        compatible_with_v7_1_contract=compatible_with_v7_1,
        selected_candidate_supported=selected_candidate_supported,
        selected_candidate_blocked=selected_candidate_blocked,
        fixture_rows=clean_row_tuple,
        ingested_adapter_records=ingested_records,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "fixture_ingestion_ready": ready},
    )
