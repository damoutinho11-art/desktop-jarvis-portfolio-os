"""J.A.R.V.I.S. v7.3 live public market intelligence fetcher boundary.

This stage defines the safe boundary for future live public market/news/risk
fetching.

It does not perform live fetching.

Safety boundary:
- fetcher boundary only
- live fetching disabled by default
- no network calls attempted
- no buy request creation
- no broker/API connection
- no order placement
- no trade execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v7_2_public_market_intelligence_fixture_ingestion import (
    STATUS_READY as V7_2_STATUS_READY,
    audit_v7_2_public_market_intelligence_fixture_ingestion,
)


STATUS_READY = "JARVIS_V7_3_LIVE_PUBLIC_MARKET_INTELLIGENCE_FETCHER_BOUNDARY_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V7_3_LIVE_PUBLIC_MARKET_INTELLIGENCE_FETCHER_BOUNDARY_BLOCKED_SAFE"

NEXT_STAGE = "v7_4_live_public_market_intelligence_dry_run_planner"

BOUNDARY_STATUS_READY = "LIVE_PUBLIC_MARKET_INTELLIGENCE_FETCHER_BOUNDARY_READY"
BOUNDARY_STATUS_BLOCKED = "LIVE_PUBLIC_MARKET_INTELLIGENCE_FETCHER_BOUNDARY_BLOCKED"

METHOD_GET = "GET"

ALLOWED_ENDPOINT_CATEGORIES = {
    "PUBLIC_CRYPTO_MARKET_CONTEXT",
    "PUBLIC_ETF_MARKET_CONTEXT",
    "PUBLIC_NEWS_RISK_CONTEXT",
    "PUBLIC_VOLATILITY_CONTEXT",
}

ALLOWED_PROVIDER_TYPES = {
    "PUBLIC_MARKET_DATA_PROVIDER",
    "PUBLIC_NEWS_CONTEXT_PROVIDER",
    "PUBLIC_INDEX_CONTEXT_PROVIDER",
    "PUBLIC_CRYPTO_CONTEXT_PROVIDER",
}


@dataclass(frozen=True)
class LivePublicMarketFetchBoundaryRequest:
    request_id: str
    provider_name: str
    provider_type: str
    endpoint_category: str
    candidate_id: str
    method: str
    url_template: str
    request_purpose: str
    expected_adapter_record_type: str
    timeout_seconds: int
    max_records: int
    rate_limit_per_minute: int
    requires_api_key: bool
    live_fetch_enabled: bool
    network_call_attempted: bool
    stores_raw_response: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_boundary_only(self) -> bool:
        return (
            not self.live_fetch_enabled
            and not self.network_call_attempted
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "endpoint_category": self.endpoint_category,
            "candidate_id": self.candidate_id,
            "method": self.method,
            "url_template": self.url_template,
            "request_purpose": self.request_purpose,
            "expected_adapter_record_type": self.expected_adapter_record_type,
            "timeout_seconds": self.timeout_seconds,
            "max_records": self.max_records,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "requires_api_key": self.requires_api_key,
            "live_fetch_enabled": self.live_fetch_enabled,
            "network_call_attempted": self.network_call_attempted,
            "stores_raw_response": self.stores_raw_response,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_boundary_only": self.safe_boundary_only(),
        }


@dataclass(frozen=True)
class LivePublicMarketFetcherBoundaryResult:
    status: str
    boundary_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    fetch_boundary_request_count: int
    disabled_live_fetch_count: int
    network_call_attempt_count: int
    compatible_with_v7_2_fixture_ingestion: bool
    fetch_boundary_requests: tuple[LivePublicMarketFetchBoundaryRequest, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    live_fetch_boundary_ready: bool
    boundary_only: bool
    live_fetch_disabled_by_default: bool
    network_calls_deferred: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "boundary_status": self.boundary_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "fetch_boundary_request_count": self.fetch_boundary_request_count,
            "disabled_live_fetch_count": self.disabled_live_fetch_count,
            "network_call_attempt_count": self.network_call_attempt_count,
            "compatible_with_v7_2_fixture_ingestion": self.compatible_with_v7_2_fixture_ingestion,
            "fetch_boundary_requests": [request.to_dict() for request in self.fetch_boundary_requests],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "live_fetch_boundary_ready": self.live_fetch_boundary_ready,
            "boundary_only": self.boundary_only,
            "live_fetch_disabled_by_default": self.live_fetch_disabled_by_default,
            "network_calls_deferred": self.network_calls_deferred,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _request(
    request_id: str,
    provider_name: str,
    provider_type: str,
    endpoint_category: str,
    candidate_id: str,
    url_template: str,
    request_purpose: str,
    expected_adapter_record_type: str,
    max_records: int,
    requires_api_key: bool = False,
) -> LivePublicMarketFetchBoundaryRequest:
    return LivePublicMarketFetchBoundaryRequest(
        request_id=request_id,
        provider_name=provider_name,
        provider_type=provider_type,
        endpoint_category=endpoint_category,
        candidate_id=candidate_id,
        method=METHOD_GET,
        url_template=url_template,
        request_purpose=request_purpose,
        expected_adapter_record_type=expected_adapter_record_type,
        timeout_seconds=10,
        max_records=max_records,
        rate_limit_per_minute=20,
        requires_api_key=requires_api_key,
        live_fetch_enabled=False,
        network_call_attempted=False,
        stores_raw_response=False,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_example_live_public_market_fetch_boundary_requests() -> tuple[
    LivePublicMarketFetchBoundaryRequest, ...
]:
    return (
        _request(
            "btc_public_price_context_boundary",
            "public_crypto_market_context_provider",
            "PUBLIC_CRYPTO_CONTEXT_PROVIDER",
            "PUBLIC_CRYPTO_MARKET_CONTEXT",
            "btc_candidate",
            "https://example.invalid/crypto-market-context/{candidate_id}",
            "Future live BTC market context fetch boundary.",
            "PUBLIC_CRYPTO_MARKET_DATA",
            5,
        ),
        _request(
            "btc_public_volatility_context_boundary",
            "public_crypto_volatility_context_provider",
            "PUBLIC_CRYPTO_CONTEXT_PROVIDER",
            "PUBLIC_VOLATILITY_CONTEXT",
            "btc_candidate",
            "https://example.invalid/crypto-volatility-context/{candidate_id}",
            "Future live BTC volatility/risk context fetch boundary.",
            "PUBLIC_CRYPTO_MARKET_DATA",
            5,
        ),
        _request(
            "global_all_world_etf_context_boundary",
            "public_index_market_context_provider",
            "PUBLIC_INDEX_CONTEXT_PROVIDER",
            "PUBLIC_ETF_MARKET_CONTEXT",
            "global_all_world_etf_candidate",
            "https://example.invalid/etf-market-context/{candidate_id}",
            "Future live diversified ETF market context fetch boundary.",
            "PUBLIC_INDEX_PROVIDER",
            5,
        ),
        _request(
            "quality_factor_news_context_boundary",
            "public_news_risk_context_provider",
            "PUBLIC_NEWS_CONTEXT_PROVIDER",
            "PUBLIC_NEWS_RISK_CONTEXT",
            "quality_factor_etf_candidate",
            "https://example.invalid/news-risk-context/{candidate_id}",
            "Future live factor ETF news/risk context fetch boundary.",
            "PUBLIC_NEWS_CONTEXT",
            10,
        ),
    )


def audit_v7_3_live_public_market_intelligence_fetcher_boundary(
    fetch_requests: tuple[LivePublicMarketFetchBoundaryRequest, ...] | None | object = None,
) -> LivePublicMarketFetcherBoundaryResult:
    fixture_result = audit_v7_2_public_market_intelligence_fixture_ingestion()

    if fetch_requests is None:
        effective_requests = build_example_live_public_market_fetch_boundary_requests()
        invalid_override = False
    elif isinstance(fetch_requests, tuple):
        effective_requests = fetch_requests
        invalid_override = False
    else:
        effective_requests = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v7.3 defines the live public market-intelligence fetcher boundary only.",
        "No live network call is attempted in v7.3.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Fetch request override must be a tuple of LivePublicMarketFetchBoundaryRequest.")

    if fixture_result.status != V7_2_STATUS_READY or fixture_result.blockers:
        blockers.append("Source v7.2 public market intelligence fixture ingestion is blocked.")

    if not effective_requests:
        blockers.append("No live public market fetch boundary requests were produced.")

    request_ids: list[str] = []
    clean_requests: list[LivePublicMarketFetchBoundaryRequest] = []

    for index, request in enumerate(effective_requests):
        if not isinstance(request, LivePublicMarketFetchBoundaryRequest):
            blockers.append(f"Fetch request at index {index} must be a LivePublicMarketFetchBoundaryRequest.")
            continue

        clean_requests.append(request)
        request_ids.append(request.request_id)

        if not request.request_id.strip():
            blockers.append("Fetch boundary request ID is required.")
        if not request.provider_name.strip():
            blockers.append(f"{request.request_id}: provider name is required.")
        if request.provider_type not in ALLOWED_PROVIDER_TYPES:
            blockers.append(f"{request.request_id}: provider type is not allowed.")
        if request.endpoint_category not in ALLOWED_ENDPOINT_CATEGORIES:
            blockers.append(f"{request.request_id}: endpoint category is not allowed.")
        if not request.candidate_id.strip():
            blockers.append(f"{request.request_id}: candidate ID is required.")
        if request.method != METHOD_GET:
            blockers.append(f"{request.request_id}: only GET boundary requests are allowed.")
        if not request.url_template.startswith("https://"):
            blockers.append(f"{request.request_id}: URL template must be HTTPS.")
        if not request.request_purpose.strip():
            blockers.append(f"{request.request_id}: request purpose is required.")
        if not request.expected_adapter_record_type.strip():
            blockers.append(f"{request.request_id}: expected adapter record type is required.")
        if request.timeout_seconds <= 0 or request.timeout_seconds > 30:
            blockers.append(f"{request.request_id}: timeout must be between 1 and 30 seconds.")
        if request.max_records <= 0 or request.max_records > 50:
            blockers.append(f"{request.request_id}: max records must be between 1 and 50.")
        if request.rate_limit_per_minute <= 0 or request.rate_limit_per_minute > 60:
            blockers.append(f"{request.request_id}: rate limit must be between 1 and 60 per minute.")
        if request.live_fetch_enabled:
            blockers.append(f"{request.request_id}: live fetching must be disabled in v7.3.")
        if request.network_call_attempted:
            blockers.append(f"{request.request_id}: network calls are forbidden in v7.3.")
        if request.stores_raw_response:
            blockers.append(f"{request.request_id}: raw response storage is forbidden before live fetch dry-run.")
        if not request.safe_boundary_only():
            blockers.append(f"{request.request_id}: fetch request must remain boundary-only.")
        if request.creates_buy_request:
            blockers.append(f"{request.request_id}: buy request creation is forbidden.")
        if request.connects_broker:
            blockers.append(f"{request.request_id}: broker connection is forbidden.")
        if request.places_order:
            blockers.append(f"{request.request_id}: order placement is forbidden.")
        if request.executes_trade:
            blockers.append(f"{request.request_id}: trade execution is forbidden.")

    if len(request_ids) != len(set(request_ids)):
        blockers.append("Live public market fetch boundary request IDs must be unique.")

    clean_request_tuple = tuple(clean_requests)

    selected_candidate_requests = tuple(
        request
        for request in clean_request_tuple
        if request.candidate_id == fixture_result.selected_candidate_id
    )
    if not selected_candidate_requests:
        blockers.append("At least one fetch boundary request must cover the selected candidate.")

    disabled_live_fetch_count = sum(1 for request in clean_request_tuple if not request.live_fetch_enabled)
    network_call_attempt_count = sum(1 for request in clean_request_tuple if request.network_call_attempted)

    safety_flags = {
        "live_fetch_boundary_ready": False,
        "boundary_only": True,
        "live_fetch_disabled_by_default": disabled_live_fetch_count == len(clean_request_tuple),
        "network_calls_deferred": network_call_attempt_count == 0,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["boundary_only"]:
        blockers.append("v7.3 must remain boundary-only.")
    if not safety_flags["live_fetch_disabled_by_default"]:
        blockers.append("v7.3 must keep live fetching disabled by default.")
    if not safety_flags["network_calls_deferred"]:
        blockers.append("v7.3 must defer all network calls.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v7.3 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v7.3 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v7.3 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v7.3 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return LivePublicMarketFetcherBoundaryResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        boundary_status=BOUNDARY_STATUS_READY if ready else BOUNDARY_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=fixture_result.selected_candidate_id,
        selected_sleeve_id=fixture_result.selected_sleeve_id,
        fetch_boundary_request_count=len(clean_request_tuple),
        disabled_live_fetch_count=disabled_live_fetch_count,
        network_call_attempt_count=network_call_attempt_count,
        compatible_with_v7_2_fixture_ingestion=fixture_result.status == V7_2_STATUS_READY,
        fetch_boundary_requests=clean_request_tuple,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "live_fetch_boundary_ready": ready},
    )
