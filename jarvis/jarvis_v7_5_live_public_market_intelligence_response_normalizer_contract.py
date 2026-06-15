"""J.A.R.V.I.S. v7.5 live public market intelligence response normalizer contract.

This stage defines how future public market/news/risk responses would be
normalized into v7.1-compatible public market intelligence adapter records.

It does not perform live fetching.

Safety boundary:
- response normalizer contract only
- no network calls attempted
- no raw response storage
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
from .jarvis_v7_4_live_public_market_intelligence_dry_run_planner import (
    STATUS_READY as V7_4_STATUS_READY,
    audit_v7_4_live_public_market_intelligence_dry_run_planner,
)


STATUS_READY = "JARVIS_V7_5_LIVE_PUBLIC_MARKET_INTELLIGENCE_RESPONSE_NORMALIZER_CONTRACT_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V7_5_LIVE_PUBLIC_MARKET_INTELLIGENCE_RESPONSE_NORMALIZER_CONTRACT_BLOCKED_SAFE"

NEXT_STAGE = "v7_6_disabled_live_public_market_fetch_adapter_skeleton"

NORMALIZER_STATUS_READY = "LIVE_PUBLIC_MARKET_INTELLIGENCE_RESPONSE_NORMALIZER_CONTRACT_READY"
NORMALIZER_STATUS_BLOCKED = "LIVE_PUBLIC_MARKET_INTELLIGENCE_RESPONSE_NORMALIZER_CONTRACT_BLOCKED"

ALLOWED_RESPONSE_KINDS = {
    "PUBLIC_PRICE_CONTEXT_RESPONSE",
    "PUBLIC_VOLATILITY_CONTEXT_RESPONSE",
    "PUBLIC_NEWS_RISK_CONTEXT_RESPONSE",
    "PUBLIC_INDEX_CONTEXT_RESPONSE",
}


@dataclass(frozen=True)
class PublicMarketResponseNormalizationInput:
    normalization_input_id: str
    source_plan_id: str
    source_request_id: str
    candidate_id: str
    provider_name: str
    endpoint_category: str
    response_kind: str
    normalized_signal_type: str
    normalized_signal_value: str
    severity: str
    confidence_score: int
    normalized_summary: str
    public_source_label: str
    public_source_quality: str
    source_url_reference: str
    observed_at_utc: str
    freshness_status: str
    supports_recommendation: bool
    blocks_recommendation: bool
    raw_response_payload_present: bool
    raw_response_stored: bool
    live_fetch_attempted: bool
    network_call_attempted: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_normalization_input_only(self) -> bool:
        return (
            not self.raw_response_payload_present
            and not self.raw_response_stored
            and not self.live_fetch_attempted
            and not self.network_call_attempted
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_adapter_record(self) -> PublicMarketIntelligenceAdapterRecord:
        return PublicMarketIntelligenceAdapterRecord(
            record_id=f"normalized_{self.normalization_input_id}",
            adapter_name="jarvis_v7_5_response_normalizer_contract",
            candidate_id=self.candidate_id,
            signal_type=self.normalized_signal_type,
            signal_value=self.normalized_signal_value,
            severity=self.severity,
            confidence_score=self.confidence_score,
            summary=self.normalized_summary,
            public_source_label=self.public_source_label,
            public_source_quality=self.public_source_quality,
            source_url=self.source_url_reference,
            observed_at_utc=self.observed_at_utc,
            freshness_status=self.freshness_status,
            supports_recommendation=self.supports_recommendation,
            blocks_recommendation=self.blocks_recommendation,
            live_fetch_attempted=False,
            creates_buy_request=False,
            connects_broker=False,
            places_order=False,
            executes_trade=False,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "normalization_input_id": self.normalization_input_id,
            "source_plan_id": self.source_plan_id,
            "source_request_id": self.source_request_id,
            "candidate_id": self.candidate_id,
            "provider_name": self.provider_name,
            "endpoint_category": self.endpoint_category,
            "response_kind": self.response_kind,
            "normalized_signal_type": self.normalized_signal_type,
            "normalized_signal_value": self.normalized_signal_value,
            "severity": self.severity,
            "confidence_score": self.confidence_score,
            "normalized_summary": self.normalized_summary,
            "public_source_label": self.public_source_label,
            "public_source_quality": self.public_source_quality,
            "source_url_reference": self.source_url_reference,
            "observed_at_utc": self.observed_at_utc,
            "freshness_status": self.freshness_status,
            "supports_recommendation": self.supports_recommendation,
            "blocks_recommendation": self.blocks_recommendation,
            "raw_response_payload_present": self.raw_response_payload_present,
            "raw_response_stored": self.raw_response_stored,
            "live_fetch_attempted": self.live_fetch_attempted,
            "network_call_attempted": self.network_call_attempted,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_normalization_input_only": self.safe_normalization_input_only(),
        }


@dataclass(frozen=True)
class PublicMarketResponseNormalizerContractResult:
    status: str
    normalizer_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    normalization_input_count: int
    normalized_adapter_record_count: int
    selected_candidate_normalized_record_count: int
    raw_response_payload_count: int
    raw_response_storage_count: int
    network_call_attempt_count: int
    live_fetch_attempt_count: int
    compatible_with_v7_4_dry_run_planner: bool
    compatible_with_v7_1_adapter_contract: bool
    selected_candidate_supported: bool
    selected_candidate_blocked: bool
    normalization_inputs: tuple[PublicMarketResponseNormalizationInput, ...]
    normalized_adapter_records: tuple[PublicMarketIntelligenceAdapterRecord, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    response_normalizer_contract_ready: bool
    contract_only: bool
    live_fetch_deferred: bool
    network_calls_deferred: bool
    raw_response_storage_deferred: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "normalizer_status": self.normalizer_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "normalization_input_count": self.normalization_input_count,
            "normalized_adapter_record_count": self.normalized_adapter_record_count,
            "selected_candidate_normalized_record_count": self.selected_candidate_normalized_record_count,
            "raw_response_payload_count": self.raw_response_payload_count,
            "raw_response_storage_count": self.raw_response_storage_count,
            "network_call_attempt_count": self.network_call_attempt_count,
            "live_fetch_attempt_count": self.live_fetch_attempt_count,
            "compatible_with_v7_4_dry_run_planner": self.compatible_with_v7_4_dry_run_planner,
            "compatible_with_v7_1_adapter_contract": self.compatible_with_v7_1_adapter_contract,
            "selected_candidate_supported": self.selected_candidate_supported,
            "selected_candidate_blocked": self.selected_candidate_blocked,
            "normalization_inputs": [item.to_dict() for item in self.normalization_inputs],
            "normalized_adapter_records": [record.to_dict() for record in self.normalized_adapter_records],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "response_normalizer_contract_ready": self.response_normalizer_contract_ready,
            "contract_only": self.contract_only,
            "live_fetch_deferred": self.live_fetch_deferred,
            "network_calls_deferred": self.network_calls_deferred,
            "raw_response_storage_deferred": self.raw_response_storage_deferred,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _normalization_input(
    normalization_input_id: str,
    source_plan_id: str,
    source_request_id: str,
    candidate_id: str,
    provider_name: str,
    endpoint_category: str,
    response_kind: str,
    normalized_signal_type: str,
    normalized_signal_value: str,
    severity: str,
    confidence_score: int,
    normalized_summary: str,
    public_source_quality: str,
    supports_recommendation: bool,
    blocks_recommendation: bool = False,
) -> PublicMarketResponseNormalizationInput:
    return PublicMarketResponseNormalizationInput(
        normalization_input_id=normalization_input_id,
        source_plan_id=source_plan_id,
        source_request_id=source_request_id,
        candidate_id=candidate_id,
        provider_name=provider_name,
        endpoint_category=endpoint_category,
        response_kind=response_kind,
        normalized_signal_type=normalized_signal_type,
        normalized_signal_value=normalized_signal_value,
        severity=severity,
        confidence_score=confidence_score,
        normalized_summary=normalized_summary,
        public_source_label="v7_5_normalized_public_context_fixture",
        public_source_quality=public_source_quality,
        source_url_reference="https://example.invalid/v7-5-response-normalizer-contract",
        observed_at_utc="2026-06-15T00:00:00Z",
        freshness_status="NORMALIZER_CONTRACT_NOT_LIVE_FETCHED",
        supports_recommendation=supports_recommendation,
        blocks_recommendation=blocks_recommendation,
        raw_response_payload_present=False,
        raw_response_stored=False,
        live_fetch_attempted=False,
        network_call_attempted=False,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_example_response_normalization_inputs() -> tuple[
    PublicMarketResponseNormalizationInput, ...
]:
    return (
        _normalization_input(
            "btc_price_context_normalization",
            "dry_run_btc_public_price_context_boundary",
            "btc_public_price_context_boundary",
            "btc_candidate",
            "public_crypto_market_context_provider",
            "PUBLIC_CRYPTO_MARKET_CONTEXT",
            "PUBLIC_PRICE_CONTEXT_RESPONSE",
            "NORMALIZED_PUBLIC_CRYPTO_MARKET_CONTEXT",
            "BTC normalized public price context remains supportive.",
            SIGNAL_SUPPORTIVE,
            91,
            "Normalizer contract can express supportive BTC market context without raw response storage.",
            "PUBLIC_CRYPTO_MARKET_DATA",
            True,
        ),
        _normalization_input(
            "btc_volatility_context_normalization",
            "dry_run_btc_public_volatility_context_boundary",
            "btc_public_volatility_context_boundary",
            "btc_candidate",
            "public_crypto_volatility_context_provider",
            "PUBLIC_VOLATILITY_CONTEXT",
            "PUBLIC_VOLATILITY_CONTEXT_RESPONSE",
            "NORMALIZED_PUBLIC_CRYPTO_VOLATILITY_CONTEXT",
            "BTC normalized volatility context remains cautionary.",
            SIGNAL_CAUTION,
            83,
            "Normalizer contract preserves crypto volatility caution without blocking the selected candidate.",
            "PUBLIC_CRYPTO_MARKET_DATA",
            True,
        ),
        _normalization_input(
            "global_all_world_context_normalization",
            "dry_run_global_all_world_etf_context_boundary",
            "global_all_world_etf_context_boundary",
            "global_all_world_etf_candidate",
            "public_index_market_context_provider",
            "PUBLIC_ETF_MARKET_CONTEXT",
            "PUBLIC_INDEX_CONTEXT_RESPONSE",
            "NORMALIZED_PUBLIC_CORE_ETF_CONTEXT",
            "Global all-world ETF normalized context remains supportive.",
            SIGNAL_SUPPORTIVE,
            88,
            "Normalizer contract keeps diversified ETF context available as a safe adapter record.",
            "PUBLIC_INDEX_PROVIDER",
            True,
        ),
        _normalization_input(
            "quality_factor_news_context_normalization",
            "dry_run_quality_factor_news_context_boundary",
            "quality_factor_news_context_boundary",
            "quality_factor_etf_candidate",
            "public_news_risk_context_provider",
            "PUBLIC_NEWS_RISK_CONTEXT",
            "PUBLIC_NEWS_RISK_CONTEXT_RESPONSE",
            "NORMALIZED_PUBLIC_NEWS_RISK_CONTEXT",
            "Quality factor ETF normalized news/risk context remains neutral.",
            SIGNAL_NEUTRAL,
            70,
            "Normalizer contract keeps secondary news/risk context available without forcing a recommendation.",
            "PUBLIC_NEWS_CONTEXT",
            False,
        ),
    )


def normalize_response_inputs_to_adapter_records(
    normalization_inputs: tuple[PublicMarketResponseNormalizationInput, ...],
) -> tuple[PublicMarketIntelligenceAdapterRecord, ...]:
    return tuple(item.to_adapter_record() for item in normalization_inputs)


def audit_v7_5_live_public_market_intelligence_response_normalizer_contract(
    normalization_inputs: tuple[PublicMarketResponseNormalizationInput, ...] | None | object = None,
) -> PublicMarketResponseNormalizerContractResult:
    dry_run_result = audit_v7_4_live_public_market_intelligence_dry_run_planner()

    if normalization_inputs is None:
        effective_inputs = build_example_response_normalization_inputs()
        invalid_override = False
    elif isinstance(normalization_inputs, tuple):
        effective_inputs = normalization_inputs
        invalid_override = False
    else:
        effective_inputs = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v7.5 defines the response normalizer contract only.",
        "No live public network call is attempted in v7.5.",
        "Raw public response payloads are not stored in v7.5.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Normalization input override must be a tuple of PublicMarketResponseNormalizationInput.")

    if dry_run_result.status != V7_4_STATUS_READY or dry_run_result.blockers:
        blockers.append("Source v7.4 live public market intelligence dry-run planner is blocked.")

    if not effective_inputs:
        blockers.append("No public market response normalization inputs were produced.")

    input_ids: list[str] = []
    source_plan_ids: list[str] = []
    clean_inputs: list[PublicMarketResponseNormalizationInput] = []

    for index, item in enumerate(effective_inputs):
        if not isinstance(item, PublicMarketResponseNormalizationInput):
            blockers.append(f"Normalization input at index {index} must be a PublicMarketResponseNormalizationInput.")
            continue

        clean_inputs.append(item)
        input_ids.append(item.normalization_input_id)
        source_plan_ids.append(item.source_plan_id)

        if not item.normalization_input_id.strip():
            blockers.append("Normalization input ID is required.")
        if not item.source_plan_id.strip():
            blockers.append(f"{item.normalization_input_id}: source plan ID is required.")
        if not item.source_request_id.strip():
            blockers.append(f"{item.normalization_input_id}: source request ID is required.")
        if not item.candidate_id.strip():
            blockers.append(f"{item.normalization_input_id}: candidate ID is required.")
        if not item.provider_name.strip():
            blockers.append(f"{item.normalization_input_id}: provider name is required.")
        if not item.endpoint_category.strip():
            blockers.append(f"{item.normalization_input_id}: endpoint category is required.")
        if item.response_kind not in ALLOWED_RESPONSE_KINDS:
            blockers.append(f"{item.normalization_input_id}: response kind is not allowed.")
        if not item.normalized_signal_type.strip():
            blockers.append(f"{item.normalization_input_id}: normalized signal type is required.")
        if not item.normalized_signal_value.strip():
            blockers.append(f"{item.normalization_input_id}: normalized signal value is required.")
        if item.severity not in ALLOWED_SEVERITIES:
            blockers.append(f"{item.normalization_input_id}: severity is not allowed.")
        if item.public_source_quality not in ALLOWED_SOURCE_QUALITIES:
            blockers.append(f"{item.normalization_input_id}: public source quality is not allowed.")
        if item.confidence_score < 0 or item.confidence_score > 100:
            blockers.append(f"{item.normalization_input_id}: confidence score must be 0..100.")
        if not item.normalized_summary.strip():
            blockers.append(f"{item.normalization_input_id}: normalized summary is required.")
        if not item.source_url_reference.startswith("https://"):
            blockers.append(f"{item.normalization_input_id}: source URL reference must be HTTPS.")
        if item.raw_response_payload_present:
            blockers.append(f"{item.normalization_input_id}: raw response payload must not be present in v7.5.")
        if item.raw_response_stored:
            blockers.append(f"{item.normalization_input_id}: raw response storage is forbidden in v7.5.")
        if item.live_fetch_attempted:
            blockers.append(f"{item.normalization_input_id}: live fetching is forbidden in v7.5.")
        if item.network_call_attempted:
            blockers.append(f"{item.normalization_input_id}: network calls are forbidden in v7.5.")
        if not item.safe_normalization_input_only():
            blockers.append(f"{item.normalization_input_id}: normalization input must remain contract-only.")
        if item.creates_buy_request:
            blockers.append(f"{item.normalization_input_id}: buy request creation is forbidden.")
        if item.connects_broker:
            blockers.append(f"{item.normalization_input_id}: broker connection is forbidden.")
        if item.places_order:
            blockers.append(f"{item.normalization_input_id}: order placement is forbidden.")
        if item.executes_trade:
            blockers.append(f"{item.normalization_input_id}: trade execution is forbidden.")

    if len(input_ids) != len(set(input_ids)):
        blockers.append("Public market response normalization input IDs must be unique.")

    expected_plan_ids = {plan.plan_id for plan in dry_run_result.dry_run_fetch_plans}
    unexpected_plan_ids = sorted(set(source_plan_ids) - expected_plan_ids)
    if unexpected_plan_ids:
        blockers.append("Normalization inputs must reference v7.4 dry-run plan IDs.")

    clean_input_tuple = tuple(clean_inputs)
    normalized_records = normalize_response_inputs_to_adapter_records(clean_input_tuple)

    adapter_result = audit_v7_1_public_market_intelligence_adapter_contract(normalized_records)

    compatible_with_v7_1 = adapter_result.status == V7_1_STATUS_READY
    selected_supported = adapter_result.selected_candidate_supported
    selected_blocked = adapter_result.selected_candidate_blocked

    if not compatible_with_v7_1:
        blockers.append("Normalized response records are not compatible with the v7.1 adapter contract.")
    if selected_blocked:
        blockers.append("Normalized response records block the selected weekly candidate.")

    selected_candidate_record_count = sum(
        1 for record in normalized_records if record.candidate_id == dry_run_result.selected_candidate_id
    )
    if selected_candidate_record_count <= 0:
        blockers.append("At least one normalized adapter record must cover the selected candidate.")

    raw_response_payload_count = sum(1 for item in clean_input_tuple if item.raw_response_payload_present)
    raw_response_storage_count = sum(1 for item in clean_input_tuple if item.raw_response_stored)
    network_call_attempt_count = sum(1 for item in clean_input_tuple if item.network_call_attempted)
    live_fetch_attempt_count = sum(1 for item in clean_input_tuple if item.live_fetch_attempted)

    safety_flags = {
        "response_normalizer_contract_ready": False,
        "contract_only": True,
        "live_fetch_deferred": live_fetch_attempt_count == 0,
        "network_calls_deferred": network_call_attempt_count == 0,
        "raw_response_storage_deferred": raw_response_storage_count == 0 and raw_response_payload_count == 0,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["contract_only"]:
        blockers.append("v7.5 must remain contract-only.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v7.5 must defer live fetching.")
    if not safety_flags["network_calls_deferred"]:
        blockers.append("v7.5 must defer network calls.")
    if not safety_flags["raw_response_storage_deferred"]:
        blockers.append("v7.5 must defer raw response storage.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v7.5 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v7.5 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v7.5 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v7.5 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return PublicMarketResponseNormalizerContractResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        normalizer_status=NORMALIZER_STATUS_READY if ready else NORMALIZER_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=dry_run_result.selected_candidate_id,
        selected_sleeve_id=dry_run_result.selected_sleeve_id,
        normalization_input_count=len(clean_input_tuple),
        normalized_adapter_record_count=len(normalized_records),
        selected_candidate_normalized_record_count=selected_candidate_record_count,
        raw_response_payload_count=raw_response_payload_count,
        raw_response_storage_count=raw_response_storage_count,
        network_call_attempt_count=network_call_attempt_count,
        live_fetch_attempt_count=live_fetch_attempt_count,
        compatible_with_v7_4_dry_run_planner=dry_run_result.status == V7_4_STATUS_READY,
        compatible_with_v7_1_adapter_contract=compatible_with_v7_1,
        selected_candidate_supported=selected_supported,
        selected_candidate_blocked=selected_blocked,
        normalization_inputs=clean_input_tuple,
        normalized_adapter_records=normalized_records,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "response_normalizer_contract_ready": ready},
    )
