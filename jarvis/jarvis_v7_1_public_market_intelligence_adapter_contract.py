"""J.A.R.V.I.S. v7.1 public market intelligence adapter contract.

This stage defines the safe contract for future public market/news/risk inputs.

It does not fetch live data yet. It validates adapter-shaped public records and
converts them into v7.0-compatible autonomous market signals.

Safety boundary:
- adapter contract only
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
    AutonomousMarketSignal,
    SIGNAL_BLOCKING,
    SIGNAL_CAUTION,
    SIGNAL_NEUTRAL,
    SIGNAL_SUPPORTIVE,
    STATUS_READY as V7_0_STATUS_READY,
    audit_v7_0_autonomous_market_intelligence_expansion,
)


STATUS_READY = "JARVIS_V7_1_PUBLIC_MARKET_INTELLIGENCE_ADAPTER_CONTRACT_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V7_1_PUBLIC_MARKET_INTELLIGENCE_ADAPTER_CONTRACT_BLOCKED_SAFE"

NEXT_STAGE = "v7_2_public_market_intelligence_fixture_ingestion"

ADAPTER_STATUS_CONTRACT_READY = "PUBLIC_MARKET_INTELLIGENCE_ADAPTER_CONTRACT_READY"
ADAPTER_STATUS_BLOCKED = "PUBLIC_MARKET_INTELLIGENCE_ADAPTER_CONTRACT_BLOCKED"

ALLOWED_SEVERITIES = {
    SIGNAL_SUPPORTIVE,
    SIGNAL_CAUTION,
    SIGNAL_NEUTRAL,
    SIGNAL_BLOCKING,
}

ALLOWED_SOURCE_QUALITIES = {
    "PUBLIC_MARKET_DATA",
    "PUBLIC_NEWS_CONTEXT",
    "PUBLIC_INDEX_PROVIDER",
    "PUBLIC_CRYPTO_MARKET_DATA",
    "LOCAL_FIXTURE_PUBLIC_CONTRACT",
}


@dataclass(frozen=True)
class PublicMarketIntelligenceAdapterRecord:
    record_id: str
    adapter_name: str
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

    def safe_adapter_record_only(self) -> bool:
        return (
            not self.live_fetch_attempted
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_signal(self) -> AutonomousMarketSignal:
        return AutonomousMarketSignal(
            signal_id=f"public_adapter_{self.record_id}",
            candidate_id=self.candidate_id,
            signal_type=self.signal_type,
            signal_value=self.signal_value,
            severity=self.severity,
            confidence_score=self.confidence_score,
            summary=self.summary,
            freshness_status=self.freshness_status,
            source_label=f"{self.adapter_name}:{self.public_source_label}",
            supports_recommendation=self.supports_recommendation,
            blocks_recommendation=self.blocks_recommendation,
            creates_buy_request=False,
            connects_broker=False,
            places_order=False,
            executes_trade=False,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "adapter_name": self.adapter_name,
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
            "safe_adapter_record_only": self.safe_adapter_record_only(),
        }


@dataclass(frozen=True)
class PublicMarketIntelligenceAdapterContractResult:
    status: str
    adapter_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    adapter_record_count: int
    generated_signal_count: int
    compatible_with_v7_0: bool
    selected_candidate_supported: bool
    selected_candidate_blocked: bool
    public_adapter_records: tuple[PublicMarketIntelligenceAdapterRecord, ...]
    generated_signals: tuple[AutonomousMarketSignal, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    adapter_contract_ready: bool
    contract_only: bool
    live_fetch_deferred: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "adapter_status": self.adapter_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "adapter_record_count": self.adapter_record_count,
            "generated_signal_count": self.generated_signal_count,
            "compatible_with_v7_0": self.compatible_with_v7_0,
            "selected_candidate_supported": self.selected_candidate_supported,
            "selected_candidate_blocked": self.selected_candidate_blocked,
            "public_adapter_records": [record.to_dict() for record in self.public_adapter_records],
            "generated_signals": [signal.to_dict() for signal in self.generated_signals],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "adapter_contract_ready": self.adapter_contract_ready,
            "contract_only": self.contract_only,
            "live_fetch_deferred": self.live_fetch_deferred,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _record(
    record_id: str,
    candidate_id: str,
    signal_type: str,
    signal_value: str,
    severity: str,
    confidence_score: int,
    summary: str,
    source_quality: str,
    supports_recommendation: bool,
    blocks_recommendation: bool = False,
) -> PublicMarketIntelligenceAdapterRecord:
    return PublicMarketIntelligenceAdapterRecord(
        record_id=record_id,
        adapter_name="public_market_intelligence_contract_fixture",
        candidate_id=candidate_id,
        signal_type=signal_type,
        signal_value=signal_value,
        severity=severity,
        confidence_score=confidence_score,
        summary=summary,
        public_source_label="fixture_public_source",
        public_source_quality=source_quality,
        source_url="https://example.invalid/public-market-intelligence-contract",
        observed_at_utc="2026-06-15T00:00:00Z",
        freshness_status="CONTRACT_FIXTURE_NOT_LIVE_FETCHED",
        supports_recommendation=supports_recommendation,
        blocks_recommendation=blocks_recommendation,
        live_fetch_attempted=False,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_example_public_market_intelligence_adapter_records(
    selected_candidate_id: str,
) -> tuple[PublicMarketIntelligenceAdapterRecord, ...]:
    return (
        _record(
            "btc_public_market_context",
            "btc_candidate",
            "PUBLIC_CRYPTO_MARKET_CONTEXT",
            "BTC public market context fixture supports keeping BTC visible.",
            SIGNAL_SUPPORTIVE,
            91,
            "Public adapter contract can express supportive BTC context without fetching live data.",
            "PUBLIC_CRYPTO_MARKET_DATA",
            selected_candidate_id == "btc_candidate",
        ),
        _record(
            "btc_public_volatility_context",
            "btc_candidate",
            "PUBLIC_VOLATILITY_CONTEXT",
            "BTC volatility caution fixture is active.",
            SIGNAL_CAUTION,
            84,
            "Public adapter contract can express crypto caution without blocking the recommendation.",
            "PUBLIC_CRYPTO_MARKET_DATA",
            selected_candidate_id == "btc_candidate",
        ),
        _record(
            "global_all_world_public_context",
            "global_all_world_etf_candidate",
            "PUBLIC_CORE_ETF_CONTEXT",
            "Global all-world ETF remains core alternative context.",
            SIGNAL_SUPPORTIVE,
            87,
            "Public adapter contract can express diversified ETF support.",
            "PUBLIC_INDEX_PROVIDER",
            True,
        ),
        _record(
            "quality_factor_public_context",
            "quality_factor_etf_candidate",
            "PUBLIC_FACTOR_ETF_CONTEXT",
            "Quality factor ETF remains secondary context.",
            SIGNAL_NEUTRAL,
            70,
            "Public adapter contract can express secondary neutral context.",
            "PUBLIC_MARKET_DATA",
            False,
        ),
    )


def convert_adapter_records_to_signals(
    records: tuple[PublicMarketIntelligenceAdapterRecord, ...],
) -> tuple[AutonomousMarketSignal, ...]:
    return tuple(record.to_signal() for record in records)


def audit_v7_1_public_market_intelligence_adapter_contract(
    adapter_records: tuple[PublicMarketIntelligenceAdapterRecord, ...] | None | object = None,
) -> PublicMarketIntelligenceAdapterContractResult:
    v7_0_result = audit_v7_0_autonomous_market_intelligence_expansion()

    if adapter_records is None:
        effective_records = build_example_public_market_intelligence_adapter_records(
            v7_0_result.selected_candidate_id
        )
    elif isinstance(adapter_records, tuple):
        effective_records = adapter_records
    else:
        effective_records = ()
        invalid_override = True

    if adapter_records is None or isinstance(adapter_records, tuple):
        invalid_override = False

    blockers: list[str] = []
    warnings: list[str] = [
        "v7.1 defines a public market-intelligence adapter contract only.",
        "No live public fetch is performed in v7.1.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Adapter override must be a tuple of PublicMarketIntelligenceAdapterRecord.")

    if v7_0_result.status != V7_0_STATUS_READY or v7_0_result.blockers:
        blockers.append("Source v7.0 autonomous market intelligence expansion is blocked.")

    if not effective_records:
        blockers.append("No public market intelligence adapter records were produced.")

    record_ids: list[str] = []
    clean_records: list[PublicMarketIntelligenceAdapterRecord] = []
    for index, record in enumerate(effective_records):
        if not isinstance(record, PublicMarketIntelligenceAdapterRecord):
            blockers.append(f"Adapter record at index {index} must be a PublicMarketIntelligenceAdapterRecord.")
            continue

        clean_records.append(record)
        record_ids.append(record.record_id)

        if not record.record_id.strip():
            blockers.append("Adapter record ID is required.")
        if not record.adapter_name.strip():
            blockers.append(f"{record.record_id}: adapter name is required.")
        if not record.candidate_id.strip():
            blockers.append(f"{record.record_id}: candidate ID is required.")
        if not record.signal_type.strip():
            blockers.append(f"{record.record_id}: signal type is required.")
        if not record.summary.strip():
            blockers.append(f"{record.record_id}: summary is required.")
        if record.severity not in ALLOWED_SEVERITIES:
            blockers.append(f"{record.record_id}: severity is not allowed.")
        if record.public_source_quality not in ALLOWED_SOURCE_QUALITIES:
            blockers.append(f"{record.record_id}: public source quality is not allowed.")
        if record.confidence_score < 0 or record.confidence_score > 100:
            blockers.append(f"{record.record_id}: confidence score must be 0..100.")
        if not record.source_url.strip():
            blockers.append(f"{record.record_id}: source URL placeholder/reference is required.")
        if record.live_fetch_attempted:
            blockers.append(f"{record.record_id}: live fetching is forbidden in v7.1.")
        if not record.safe_adapter_record_only():
            blockers.append(f"{record.record_id}: adapter record must remain contract-only.")
        if record.creates_buy_request:
            blockers.append(f"{record.record_id}: buy request creation is forbidden.")
        if record.connects_broker:
            blockers.append(f"{record.record_id}: broker connection is forbidden.")
        if record.places_order:
            blockers.append(f"{record.record_id}: order placement is forbidden.")
        if record.executes_trade:
            blockers.append(f"{record.record_id}: trade execution is forbidden.")

    if len(record_ids) != len(set(record_ids)):
        blockers.append("Public market intelligence adapter record IDs must be unique.")

    clean_record_tuple = tuple(clean_records)
    generated_signals = convert_adapter_records_to_signals(clean_record_tuple)

    signal_ids = [signal.signal_id for signal in generated_signals]
    if len(signal_ids) != len(set(signal_ids)):
        blockers.append("Generated market signal IDs must be unique.")

    for signal in generated_signals:
        if not signal.safe_signal_only():
            blockers.append(f"{signal.signal_id}: generated signal must remain non-executable.")

    compatible_result = audit_v7_0_autonomous_market_intelligence_expansion(generated_signals)

    compatible_with_v7_0 = compatible_result.status == V7_0_STATUS_READY
    selected_supported = compatible_result.selected_candidate_supported
    selected_blocked = compatible_result.selected_candidate_blocked

    if not compatible_with_v7_0:
        blockers.append("Generated adapter signals are not compatible with v7.0 market intelligence.")
    if selected_blocked:
        blockers.append("Generated adapter signals block the selected weekly candidate.")

    safety_flags = {
        "adapter_contract_ready": False,
        "contract_only": True,
        "live_fetch_deferred": True,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["contract_only"]:
        blockers.append("v7.1 must remain contract-only.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v7.1 must defer live fetching.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v7.1 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v7.1 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v7.1 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v7.1 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return PublicMarketIntelligenceAdapterContractResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        adapter_status=ADAPTER_STATUS_CONTRACT_READY if ready else ADAPTER_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=v7_0_result.selected_candidate_id,
        selected_sleeve_id=v7_0_result.selected_sleeve_id,
        adapter_record_count=len(clean_record_tuple),
        generated_signal_count=len(generated_signals),
        compatible_with_v7_0=compatible_with_v7_0,
        selected_candidate_supported=selected_supported,
        selected_candidate_blocked=selected_blocked,
        public_adapter_records=clean_record_tuple,
        generated_signals=generated_signals,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "adapter_contract_ready": ready},
    )
