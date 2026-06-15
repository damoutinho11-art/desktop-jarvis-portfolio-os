"""J.A.R.V.I.S. v7.8 public provider configuration registry.

This stage declares safe public-data provider metadata for future public market
intelligence fetching.

It does not enable live fetching.

Safety boundary:
- provider configuration registry only
- providers disabled by default
- no network calls attempted
- no raw response storage
- no live adapter record emission
- no buy request creation
- no broker/API connection
- no order placement
- no trade execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v7_3_live_public_market_intelligence_fetcher_boundary import (
    ALLOWED_ENDPOINT_CATEGORIES,
    ALLOWED_PROVIDER_TYPES,
)
from .jarvis_v7_7_live_public_market_intelligence_enablement_preflight import (
    STATUS_READY as V7_7_STATUS_READY,
    audit_v7_7_live_public_market_intelligence_enablement_preflight,
)


STATUS_READY = "JARVIS_V7_8_PUBLIC_PROVIDER_CONFIGURATION_REGISTRY_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V7_8_PUBLIC_PROVIDER_CONFIGURATION_REGISTRY_BLOCKED_SAFE"

NEXT_STAGE = "v7_9_public_provider_skeleton_binding_audit"

REGISTRY_STATUS_READY = "PUBLIC_PROVIDER_CONFIGURATION_REGISTRY_READY"
REGISTRY_STATUS_BLOCKED = "PUBLIC_PROVIDER_CONFIGURATION_REGISTRY_BLOCKED"

AUTH_MODE_NONE = "NO_AUTH_REQUIRED"
AUTH_MODE_ENV_API_KEY = "ENV_API_KEY_REQUIRED"

ALLOWED_AUTH_MODES = {
    AUTH_MODE_NONE,
    AUTH_MODE_ENV_API_KEY,
}

RAW_STORAGE_POLICY_NONE = "NO_RAW_RESPONSE_STORAGE"
CACHE_POLICY_NORMALIZED_ONLY = "NORMALIZED_RECORD_CACHE_ONLY"

ALLOWED_RAW_STORAGE_POLICIES = {
    RAW_STORAGE_POLICY_NONE,
}

ALLOWED_CACHE_POLICIES = {
    CACHE_POLICY_NORMALIZED_ONLY,
}


@dataclass(frozen=True)
class PublicProviderConfiguration:
    provider_id: str
    provider_name: str
    provider_type: str
    endpoint_category: str
    base_url_reference: str
    auth_mode: str
    api_key_env_var: str
    timeout_seconds: int
    rate_limit_per_minute: int
    max_records_per_request: int
    raw_response_storage_policy: str
    cache_policy: str
    configuration_source: str
    covers_selected_candidate: bool
    usable_for_dry_run_plans: bool
    provider_enabled_by_default: bool
    live_fetch_enabled: bool
    network_call_allowed: bool
    raw_response_storage_allowed: bool
    emits_live_adapter_record: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_configuration_only(self) -> bool:
        return (
            self.usable_for_dry_run_plans
            and not self.provider_enabled_by_default
            and not self.live_fetch_enabled
            and not self.network_call_allowed
            and not self.raw_response_storage_allowed
            and not self.emits_live_adapter_record
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "endpoint_category": self.endpoint_category,
            "base_url_reference": self.base_url_reference,
            "auth_mode": self.auth_mode,
            "api_key_env_var": self.api_key_env_var,
            "timeout_seconds": self.timeout_seconds,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "max_records_per_request": self.max_records_per_request,
            "raw_response_storage_policy": self.raw_response_storage_policy,
            "cache_policy": self.cache_policy,
            "configuration_source": self.configuration_source,
            "covers_selected_candidate": self.covers_selected_candidate,
            "usable_for_dry_run_plans": self.usable_for_dry_run_plans,
            "provider_enabled_by_default": self.provider_enabled_by_default,
            "live_fetch_enabled": self.live_fetch_enabled,
            "network_call_allowed": self.network_call_allowed,
            "raw_response_storage_allowed": self.raw_response_storage_allowed,
            "emits_live_adapter_record": self.emits_live_adapter_record,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_configuration_only": self.safe_configuration_only(),
        }


@dataclass(frozen=True)
class PublicProviderConfigurationRegistryResult:
    status: str
    registry_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    provider_count: int
    selected_candidate_provider_count: int
    enabled_provider_count: int
    live_fetch_enabled_count: int
    network_call_allowed_count: int
    raw_response_storage_allowed_count: int
    live_adapter_record_emit_count: int
    no_auth_provider_count: int
    env_api_key_provider_count: int
    compatible_with_v7_7_enablement_preflight: bool
    providers: tuple[PublicProviderConfiguration, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    provider_registry_ready: bool
    registry_only: bool
    providers_disabled_by_default: bool
    live_fetch_deferred: bool
    network_calls_deferred: bool
    raw_response_storage_deferred: bool
    live_adapter_record_emission_deferred: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "registry_status": self.registry_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "provider_count": self.provider_count,
            "selected_candidate_provider_count": self.selected_candidate_provider_count,
            "enabled_provider_count": self.enabled_provider_count,
            "live_fetch_enabled_count": self.live_fetch_enabled_count,
            "network_call_allowed_count": self.network_call_allowed_count,
            "raw_response_storage_allowed_count": self.raw_response_storage_allowed_count,
            "live_adapter_record_emit_count": self.live_adapter_record_emit_count,
            "no_auth_provider_count": self.no_auth_provider_count,
            "env_api_key_provider_count": self.env_api_key_provider_count,
            "compatible_with_v7_7_enablement_preflight": self.compatible_with_v7_7_enablement_preflight,
            "providers": [provider.to_dict() for provider in self.providers],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "provider_registry_ready": self.provider_registry_ready,
            "registry_only": self.registry_only,
            "providers_disabled_by_default": self.providers_disabled_by_default,
            "live_fetch_deferred": self.live_fetch_deferred,
            "network_calls_deferred": self.network_calls_deferred,
            "raw_response_storage_deferred": self.raw_response_storage_deferred,
            "live_adapter_record_emission_deferred": self.live_adapter_record_emission_deferred,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _provider(
    provider_id: str,
    provider_name: str,
    provider_type: str,
    endpoint_category: str,
    base_url_reference: str,
    auth_mode: str,
    api_key_env_var: str,
    covers_selected_candidate: bool,
    rate_limit_per_minute: int,
    max_records_per_request: int,
) -> PublicProviderConfiguration:
    return PublicProviderConfiguration(
        provider_id=provider_id,
        provider_name=provider_name,
        provider_type=provider_type,
        endpoint_category=endpoint_category,
        base_url_reference=base_url_reference,
        auth_mode=auth_mode,
        api_key_env_var=api_key_env_var,
        timeout_seconds=10,
        rate_limit_per_minute=rate_limit_per_minute,
        max_records_per_request=max_records_per_request,
        raw_response_storage_policy=RAW_STORAGE_POLICY_NONE,
        cache_policy=CACHE_POLICY_NORMALIZED_ONLY,
        configuration_source="jarvis_v7_8_public_provider_configuration_registry",
        covers_selected_candidate=covers_selected_candidate,
        usable_for_dry_run_plans=True,
        provider_enabled_by_default=False,
        live_fetch_enabled=False,
        network_call_allowed=False,
        raw_response_storage_allowed=False,
        emits_live_adapter_record=False,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_example_public_provider_configurations() -> tuple[PublicProviderConfiguration, ...]:
    return (
        _provider(
            "coingecko_public_crypto_context_provider",
            "CoinGecko public crypto market context",
            "PUBLIC_CRYPTO_CONTEXT_PROVIDER",
            "PUBLIC_CRYPTO_MARKET_CONTEXT",
            "https://api.coingecko.com/api/v3",
            AUTH_MODE_NONE,
            "",
            True,
            20,
            25,
        ),
        _provider(
            "coingecko_public_crypto_volatility_context_provider",
            "CoinGecko public crypto volatility context",
            "PUBLIC_CRYPTO_CONTEXT_PROVIDER",
            "PUBLIC_VOLATILITY_CONTEXT",
            "https://api.coingecko.com/api/v3",
            AUTH_MODE_NONE,
            "",
            True,
            20,
            25,
        ),
        _provider(
            "stooq_public_index_market_context_provider",
            "Stooq public index and ETF market context",
            "PUBLIC_INDEX_CONTEXT_PROVIDER",
            "PUBLIC_ETF_MARKET_CONTEXT",
            "https://stooq.com/q/l/",
            AUTH_MODE_NONE,
            "",
            False,
            20,
            25,
        ),
        _provider(
            "public_news_risk_context_provider",
            "Public news risk context provider",
            "PUBLIC_NEWS_CONTEXT_PROVIDER",
            "PUBLIC_NEWS_RISK_CONTEXT",
            "https://example.invalid/public-news-risk-context",
            AUTH_MODE_ENV_API_KEY,
            "JARVIS_PUBLIC_NEWS_CONTEXT_API_KEY",
            False,
            10,
            10,
        ),
    )


def audit_v7_8_public_provider_configuration_registry(
    providers: tuple[PublicProviderConfiguration, ...] | None | object = None,
) -> PublicProviderConfigurationRegistryResult:
    preflight_result = audit_v7_7_live_public_market_intelligence_enablement_preflight()

    if providers is None:
        effective_providers = build_example_public_provider_configurations()
        invalid_override = False
    elif isinstance(providers, tuple):
        effective_providers = providers
        invalid_override = False
    else:
        effective_providers = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v7.8 declares public provider configuration metadata only.",
        "Providers remain disabled by default.",
        "No live public network call is attempted in v7.8.",
        "No raw public response payload is stored in v7.8.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Provider override must be a tuple of PublicProviderConfiguration.")

    if preflight_result.status != V7_7_STATUS_READY or preflight_result.blockers:
        blockers.append("Source v7.7 live public market intelligence enablement preflight is blocked.")

    if preflight_result.live_fetch_enablement_allowed:
        blockers.append("v7.8 requires live fetch enablement to remain disallowed.")

    if not effective_providers:
        blockers.append("No public provider configurations were produced.")

    provider_ids: list[str] = []
    clean_providers: list[PublicProviderConfiguration] = []

    for index, provider in enumerate(effective_providers):
        if not isinstance(provider, PublicProviderConfiguration):
            blockers.append(f"Provider at index {index} must be a PublicProviderConfiguration.")
            continue

        clean_providers.append(provider)
        provider_ids.append(provider.provider_id)

        if not provider.provider_id.strip():
            blockers.append("Provider ID is required.")
        if not provider.provider_name.strip():
            blockers.append(f"{provider.provider_id}: provider name is required.")
        if provider.provider_type not in ALLOWED_PROVIDER_TYPES:
            blockers.append(f"{provider.provider_id}: provider type is not allowed.")
        if provider.endpoint_category not in ALLOWED_ENDPOINT_CATEGORIES:
            blockers.append(f"{provider.provider_id}: endpoint category is not allowed.")
        if not provider.base_url_reference.startswith("https://"):
            blockers.append(f"{provider.provider_id}: base URL reference must be HTTPS.")
        if provider.auth_mode not in ALLOWED_AUTH_MODES:
            blockers.append(f"{provider.provider_id}: auth mode is not allowed.")
        if provider.auth_mode == AUTH_MODE_ENV_API_KEY and not provider.api_key_env_var.strip():
            blockers.append(f"{provider.provider_id}: API-key auth requires an environment variable name.")
        if provider.auth_mode == AUTH_MODE_NONE and provider.api_key_env_var.strip():
            blockers.append(f"{provider.provider_id}: no-auth providers must not declare API key env vars.")
        if provider.timeout_seconds <= 0 or provider.timeout_seconds > 30:
            blockers.append(f"{provider.provider_id}: timeout must be between 1 and 30 seconds.")
        if provider.rate_limit_per_minute <= 0 or provider.rate_limit_per_minute > 60:
            blockers.append(f"{provider.provider_id}: rate limit must be between 1 and 60 per minute.")
        if provider.max_records_per_request <= 0 or provider.max_records_per_request > 50:
            blockers.append(f"{provider.provider_id}: max records must be between 1 and 50.")
        if provider.raw_response_storage_policy not in ALLOWED_RAW_STORAGE_POLICIES:
            blockers.append(f"{provider.provider_id}: raw response storage policy is not allowed.")
        if provider.cache_policy not in ALLOWED_CACHE_POLICIES:
            blockers.append(f"{provider.provider_id}: cache policy is not allowed.")
        if not provider.configuration_source.strip():
            blockers.append(f"{provider.provider_id}: configuration source is required.")
        if not provider.usable_for_dry_run_plans:
            blockers.append(f"{provider.provider_id}: provider must be usable for dry-run plans.")
        if provider.provider_enabled_by_default:
            blockers.append(f"{provider.provider_id}: provider must be disabled by default.")
        if provider.live_fetch_enabled:
            blockers.append(f"{provider.provider_id}: live fetching is forbidden in v7.8.")
        if provider.network_call_allowed:
            blockers.append(f"{provider.provider_id}: network calls are forbidden in v7.8.")
        if provider.raw_response_storage_allowed:
            blockers.append(f"{provider.provider_id}: raw response storage is forbidden in v7.8.")
        if provider.emits_live_adapter_record:
            blockers.append(f"{provider.provider_id}: live adapter record emission is forbidden in v7.8.")
        if not provider.safe_configuration_only():
            blockers.append(f"{provider.provider_id}: provider configuration must remain registry-only.")
        if provider.creates_buy_request:
            blockers.append(f"{provider.provider_id}: buy request creation is forbidden.")
        if provider.connects_broker:
            blockers.append(f"{provider.provider_id}: broker connection is forbidden.")
        if provider.places_order:
            blockers.append(f"{provider.provider_id}: order placement is forbidden.")
        if provider.executes_trade:
            blockers.append(f"{provider.provider_id}: trade execution is forbidden.")

    if len(provider_ids) != len(set(provider_ids)):
        blockers.append("Public provider configuration IDs must be unique.")

    clean_provider_tuple = tuple(clean_providers)

    selected_candidate_provider_count = sum(
        1 for provider in clean_provider_tuple if provider.covers_selected_candidate
    )
    if selected_candidate_provider_count <= 0:
        blockers.append("At least one public provider configuration must cover the selected candidate.")

    covered_endpoint_categories = {
        provider.endpoint_category for provider in clean_provider_tuple
    }
    if "PUBLIC_CRYPTO_MARKET_CONTEXT" not in covered_endpoint_categories:
        blockers.append("Registry must include public crypto market context provider coverage.")
    if "PUBLIC_VOLATILITY_CONTEXT" not in covered_endpoint_categories:
        blockers.append("Registry must include public volatility context provider coverage.")
    if "PUBLIC_ETF_MARKET_CONTEXT" not in covered_endpoint_categories:
        blockers.append("Registry must include public ETF market context provider coverage.")
    if "PUBLIC_NEWS_RISK_CONTEXT" not in covered_endpoint_categories:
        blockers.append("Registry must include public news/risk context provider coverage.")

    enabled_provider_count = sum(1 for provider in clean_provider_tuple if provider.provider_enabled_by_default)
    live_fetch_enabled_count = sum(1 for provider in clean_provider_tuple if provider.live_fetch_enabled)
    network_call_allowed_count = sum(1 for provider in clean_provider_tuple if provider.network_call_allowed)
    raw_response_storage_allowed_count = sum(
        1 for provider in clean_provider_tuple if provider.raw_response_storage_allowed
    )
    live_adapter_record_emit_count = sum(
        1 for provider in clean_provider_tuple if provider.emits_live_adapter_record
    )
    no_auth_provider_count = sum(1 for provider in clean_provider_tuple if provider.auth_mode == AUTH_MODE_NONE)
    env_api_key_provider_count = sum(
        1 for provider in clean_provider_tuple if provider.auth_mode == AUTH_MODE_ENV_API_KEY
    )

    safety_flags = {
        "provider_registry_ready": False,
        "registry_only": True,
        "providers_disabled_by_default": enabled_provider_count == 0,
        "live_fetch_deferred": live_fetch_enabled_count == 0,
        "network_calls_deferred": network_call_allowed_count == 0,
        "raw_response_storage_deferred": raw_response_storage_allowed_count == 0,
        "live_adapter_record_emission_deferred": live_adapter_record_emit_count == 0,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["registry_only"]:
        blockers.append("v7.8 must remain registry-only.")
    if not safety_flags["providers_disabled_by_default"]:
        blockers.append("v7.8 must keep all providers disabled by default.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v7.8 must defer live fetching.")
    if not safety_flags["network_calls_deferred"]:
        blockers.append("v7.8 must defer network calls.")
    if not safety_flags["raw_response_storage_deferred"]:
        blockers.append("v7.8 must defer raw response storage.")
    if not safety_flags["live_adapter_record_emission_deferred"]:
        blockers.append("v7.8 must defer live adapter record emission.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v7.8 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v7.8 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v7.8 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v7.8 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return PublicProviderConfigurationRegistryResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        registry_status=REGISTRY_STATUS_READY if ready else REGISTRY_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=preflight_result.selected_candidate_id,
        selected_sleeve_id=preflight_result.selected_sleeve_id,
        provider_count=len(clean_provider_tuple),
        selected_candidate_provider_count=selected_candidate_provider_count,
        enabled_provider_count=enabled_provider_count,
        live_fetch_enabled_count=live_fetch_enabled_count,
        network_call_allowed_count=network_call_allowed_count,
        raw_response_storage_allowed_count=raw_response_storage_allowed_count,
        live_adapter_record_emit_count=live_adapter_record_emit_count,
        no_auth_provider_count=no_auth_provider_count,
        env_api_key_provider_count=env_api_key_provider_count,
        compatible_with_v7_7_enablement_preflight=preflight_result.status == V7_7_STATUS_READY,
        providers=clean_provider_tuple,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "provider_registry_ready": ready},
    )
