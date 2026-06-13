"""Public asset universe source manifest schema evaluator.

v4.62 validates allowed public source metadata for future universe discovery.
It is import-safe and read-only: no network, fetching, downloading, scraping,
API calls, writes, cache creation, subprocesses, schedulers, browser automation,
broker integration, private ingest, evidence verification, approvals, or trades.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlparse


REQUIRED_SOURCE_CATEGORIES = (
    "exchange_listing_sources",
    "issuer_or_provider_sources",
    "regulator_or_filings_sources",
    "fund_provider_sources",
    "public_market_data_sources",
    "crypto_public_reference_sources",
    "identifier_mapping_sources",
    "etf_listing_sources",
    "equity_listing_sources",
    "fund_or_etp_listing_sources",
    "exchange_or_market_reference_sources",
)

REQUIRED_ASSET_UNIVERSES = (
    "etf_universe",
    "equity_universe",
    "fund_or_etp_universe",
    "crypto_asset_universe",
    "exchange_or_market_reference_universe",
)

ALLOWED_SOURCE_TYPES = {
    "static_file_url",
    "public_web_page",
    "public_csv",
    "public_json",
    "public_api_reference_only",
    "official_public_download_page",
    "public_index_page",
}

ALLOWED_FUTURE_FETCH_METHODS = {
    "manual_download_reference_only",
    "explicit_http_get_local_cache_only",
    "explicit_public_file_download_local_cache_only",
    "explicit_public_json_fetch_local_cache_only",
    "explicit_public_csv_fetch_local_cache_only",
}

FORBIDDEN_SOURCE_OR_FETCH_TYPES = {
    "broker_api",
    "authenticated_api",
    "paid_api",
    "credentialed_api",
    "account_api",
    "trading_api",
    "wallet_api",
    "exchange_private_api",
    "browser_automation",
    "scraping_login_page",
    "private_file",
    "local_account_export",
}

CREDENTIAL_QUERY_KEYS = {
    "api_key",
    "apikey",
    "token",
    "secret",
    "password",
    "passwd",
    "auth",
    "credential",
    "bearer",
    "session",
    "access_key",
    "private_key",
}

PRIVATE_ENDPOINT_KEYWORDS = (
    "lightyear",
    "lhv",
    "coinbase/private",
    "binance/private",
    "kraken/private",
    "trading",
    "order",
    "account",
    "portfolio",
    "balance",
    "wallet",
    "login",
    "oauth",
)

REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_PUBLIC_ASSET_UNIVERSE_FETCH_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE"

VALID_NEXT_MANUAL_ACTIONS = {
    "review_public_source_manifest",
    "prepare_public_universe_fetch_dry_run_planner",
    "configure_local_public_universe_source_manifest",
    "no_manual_asset_entry_required",
}

BLOCKED_NEXT_MANUAL_ACTIONS = {
    "manually_enter_every_asset",
    "another_gate",
    "another_review_layer",
    "broker_integration",
    "credential_setup",
    "evidence_verification",
    "approval",
    "registry_mutation",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_execution",
    "executor_creation",
}

FALSE_REQUIRED_SAFETY_FIELDS = (
    "network_calls",
    "fetching",
    "downloading",
    "scraping",
    "api_calls",
    "writes",
    "cache_creation",
    "subprocess_execution",
    "scheduler_creation",
    "browser_automation",
    "broker_integration",
    "lightyear_integration",
    "lhv_integration",
    "crypto_exchange_integration",
    "credentials_used",
    "private_file_ingested",
    "automatic_private_data_ingest",
    "account_data_ingested",
    "source_parsing_as_evidence",
    "evidence_extraction",
    "evidence_verification",
    "verified_evidence_promotion",
    "registry_mutation",
    "registry_file_written",
    "candidate_registry_write",
    "candidate_intake_file_written",
    "approved_asset",
    "trusted_asset",
    "investable",
    "allocation_recommendation",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "executor_created",
)

TRUE_REQUIRED_SAFETY_FIELDS = (
    "public_data_only",
    "manual_trust_required",
    "manual_approval_required",
    "no_execution_invariant",
    "final_purchase_external_manual_only",
    "source_manifest_only",
)


@dataclass(frozen=True)
class SourceManifestCategory:
    source_category_id: str
    source_category_name: str
    supported_asset_universes: tuple[str, ...]
    expected_update_frequency: str
    expected_fields: tuple[str, ...]
    blocked_reasons: tuple[str, ...]


@dataclass(frozen=True)
class SourceManifestEntry:
    source_id: str
    source_name: str
    source_category_id: str
    target_asset_universes: tuple[str, ...]
    source_type: str
    source_url: str
    allowed_future_fetch_method: str
    blocked_reasons: tuple[str, ...]


@dataclass(frozen=True)
class PublicAssetUniverseSourceManifestResult:
    title: str
    version: str
    overall_status: str
    manifest_mode: str
    report_only: bool
    no_network: bool
    no_fetching: bool
    no_downloading: bool
    no_scraping: bool
    no_api_calls: bool
    no_writes: bool
    no_cache_creation: bool
    no_subprocess: bool
    no_scheduler_creation: bool
    no_broker_integration: bool
    no_private_data_ingest: bool
    source_manifest_id: str
    source_manifest_name: str
    intended_route: tuple[str, ...]
    source_categories: tuple[SourceManifestCategory, ...]
    sources: tuple[SourceManifestEntry, ...]
    required_source_category_ids: tuple[str, ...]
    required_asset_universe_ids: tuple[str, ...]
    covered_asset_universe_ids: tuple[str, ...]
    update_frequency_policy: dict[str, Any]
    future_fetch_policy: dict[str, Any]
    local_cache_policy: dict[str, Any]
    identifier_policy: dict[str, Any]
    next_manual_action: str
    redundant_next_steps_to_avoid: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    network_calls: bool = False
    fetching: bool = False
    downloading: bool = False
    scraping: bool = False
    api_calls: bool = False
    writes: bool = False
    cache_creation: bool = False
    subprocess_execution: bool = False
    scheduler_creation: bool = False
    browser_automation: bool = False
    broker_integration: bool = False
    lightyear_integration: bool = False
    lhv_integration: bool = False
    crypto_exchange_integration: bool = False
    credentials_used: bool = False
    private_file_ingested: bool = False
    automatic_private_data_ingest: bool = False
    account_data_ingested: bool = False
    source_parsing_as_evidence: bool = False
    evidence_extraction: bool = False
    evidence_verification: bool = False
    verified_evidence_promotion: bool = False
    registry_mutation: bool = False
    registry_file_written: bool = False
    candidate_registry_write: bool = False
    candidate_intake_file_written: bool = False
    approved_asset: bool = False
    trusted_asset: bool = False
    investable: bool = False
    allocation_recommendation: bool = False
    portfolio_weight: bool = False
    buy_signal: bool = False
    sell_signal: bool = False
    trade_executed: bool = False
    executor_created: bool = False
    public_data_only: bool = True
    manual_trust_required: bool = True
    manual_approval_required: bool = True
    no_execution_invariant: bool = True
    final_purchase_external_manual_only: bool = True
    source_manifest_only: bool = True


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _list(value: Any) -> tuple[str, ...]:
    if isinstance(value, list):
        return tuple(_text(item) for item in value if _text(item))
    text = _text(value)
    return (text,) if text else ()


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _validate_source_url(source_url: str, source_type: str, source_name: str) -> tuple[str, ...]:
    blocked: list[str] = []
    if not source_url:
        if source_type != "manual_download_reference_only":
            blocked.append("source_url is required.")
        return tuple(blocked)
    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"}:
        blocked.append("source_url must be http or https.")
    hostname = (parsed.hostname or "").lower()
    if hostname in {"localhost", "127.0.0.1"}:
        blocked.append("source_url must not target localhost or 127.0.0.1.")
    lowered = f"{source_url} {source_name}".lower()
    for keyword in PRIVATE_ENDPOINT_KEYWORDS:
        if keyword in lowered:
            blocked.append(f"source must not reference private/broker/trading keyword: {keyword}.")
    query_keys = {key.lower() for key, _value in parse_qsl(parsed.query, keep_blank_values=True)}
    for key in sorted(query_keys & CREDENTIAL_QUERY_KEYS):
        blocked.append(f"source_url must not contain credential-looking query key: {key}.")
    return tuple(blocked)


def validate_source_category(category: dict[str, Any]) -> SourceManifestCategory:
    blocked: list[str] = []
    for field in ("source_category_id", "source_category_name", "intended_use", "expected_update_frequency", "future_cache_path_hint"):
        if not _text(category.get(field)):
            blocked.append(f"{field} is required.")
    for field in ("public_only", "future_fetch_allowed_only_with_explicit_authorization"):
        if category.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in ("authentication_required", "credentials_allowed", "broker_api_allowed", "private_data_allowed", "trading_access_allowed"):
        if category.get(field) is not False:
            blocked.append(f"{field} must be false.")
    if not _list(category.get("supported_asset_universes")):
        blocked.append("supported_asset_universes must not be empty.")
    if not _list(category.get("expected_fields")):
        blocked.append("expected_fields must not be empty.")
    if not _list(category.get("safety_notes")):
        blocked.append("safety_notes must not be empty.")
    return SourceManifestCategory(
        source_category_id=_text(category.get("source_category_id")),
        source_category_name=_text(category.get("source_category_name")),
        supported_asset_universes=_list(category.get("supported_asset_universes")),
        expected_update_frequency=_text(category.get("expected_update_frequency")),
        expected_fields=_list(category.get("expected_fields")),
        blocked_reasons=tuple(blocked),
    )


def validate_source_entry(source: dict[str, Any], known_category_ids: set[str] | None = None) -> SourceManifestEntry:
    blocked: list[str] = []
    known_category_ids = known_category_ids or set()
    for field in (
        "source_id",
        "source_name",
        "source_category_id",
        "source_type",
        "expected_update_frequency",
        "future_fetch_output_scope",
        "future_cache_path_hint",
    ):
        if not _text(source.get(field)):
            blocked.append(f"{field} is required.")
    category_id = _text(source.get("source_category_id"))
    if known_category_ids and category_id not in known_category_ids:
        blocked.append("source_category_id must reference a known category.")
    source_type = _text(source.get("source_type"))
    if source_type not in ALLOWED_SOURCE_TYPES:
        blocked.append("source_type must be an allowed public source type.")
    if source_type in FORBIDDEN_SOURCE_OR_FETCH_TYPES:
        blocked.append("source_type must not be a forbidden source type.")
    fetch_method = _text(source.get("allowed_future_fetch_method"))
    if fetch_method not in ALLOWED_FUTURE_FETCH_METHODS:
        blocked.append("allowed_future_fetch_method must be an allowed future local-cache method.")
    if fetch_method in FORBIDDEN_SOURCE_OR_FETCH_TYPES:
        blocked.append("allowed_future_fetch_method must not be forbidden.")
    for field in (
        "public_only",
        "future_fetch_requires_explicit_authorization",
        "raw_data_unverified",
        "discovery_not_verification",
        "classification_not_approval",
        "screening_not_investment_advice",
    ):
        if source.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in ("authentication_required", "credentials_allowed", "broker_api_allowed", "private_data_allowed", "trading_access_allowed"):
        if source.get(field) is not False:
            blocked.append(f"{field} must be false.")
    if not _list(source.get("target_asset_universes")):
        blocked.append("target_asset_universes must not be empty.")
    if not _list(source.get("expected_fields")):
        blocked.append("expected_fields must not be empty.")
    if not _list(source.get("required_fields_for_future_fetch")):
        blocked.append("required_fields_for_future_fetch must not be empty.")
    if not _list(source.get("safety_notes")):
        blocked.append("safety_notes must not be empty.")
    blocked.extend(_validate_source_url(_text(source.get("source_url")), source_type, _text(source.get("source_name"))))
    return SourceManifestEntry(
        source_id=_text(source.get("source_id")),
        source_name=_text(source.get("source_name")),
        source_category_id=category_id,
        target_asset_universes=_list(source.get("target_asset_universes")),
        source_type=source_type,
        source_url=_text(source.get("source_url")),
        allowed_future_fetch_method=fetch_method,
        blocked_reasons=tuple(blocked),
    )


def validate_future_fetch_policy(policy: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    expected = {
        "default_fetch_allowed": False,
        "future_fetch_allowed_only_with_explicit_authorization": True,
        "local_cache_only": True,
        "fetched_data_unverified": True,
        "no_fetched_data_committed": True,
        "no_registry_mutation": True,
        "no_candidate_registry_write": True,
        "no_evidence_verification": True,
        "no_approval": True,
        "no_allocation": True,
        "no_trade": True,
        "no_executor": True,
    }
    for field, value in expected.items():
        if policy.get(field) is not value:
            blocked.append(f"future_fetch_policy.{field} must be {str(value).lower()}.")
    if policy.get("required_authorization_phrase") != REQUIRED_AUTHORIZATION_PHRASE:
        blocked.append("future_fetch_policy.required_authorization_phrase must match the strict phrase.")
    return tuple(blocked)


def validate_local_cache_policy(policy: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    if policy.get("cache_writes_performed_in_v4_62") is not False:
        blocked.append("local_cache_policy.cache_writes_performed_in_v4_62 must be false.")
    required_true = (
        "future_cache_must_remain_ignored_uncommitted",
        "raw_data_remains_unverified",
        "normalized_data_remains_unapproved",
        "no_fetched_data_committed",
        "future_cache_builder_requires_explicit_authorization",
        "future_cache_builder_local_cache_only",
    )
    for field in required_true:
        if policy.get(field) is not True:
            blocked.append(f"local_cache_policy.{field} must be true.")
    planned_paths = _list(policy.get("planned_paths"))
    if not planned_paths:
        blocked.append("local_cache_policy.planned_paths must not be empty.")
    for path in planned_paths:
        if not path.replace("\\", "/").startswith("jarvis/local/public_asset_universe/"):
            blocked.append("local_cache_policy planned paths must be under jarvis/local/public_asset_universe.")
    return tuple(blocked)


def validate_identifier_policy(policy: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in ("source_reference_id_required", "asset_id_required_later", "symbol_or_identifier_required_later"):
        if policy.get(field) is not True:
            blocked.append(f"identifier_policy.{field} must be true.")
    for field in (
        "account_identifiers_allowed",
        "broker_specific_private_identifiers_allowed",
        "portfolio_identifiers_allowed",
        "user_holdings_identifiers_allowed",
    ):
        if policy.get(field) is not False:
            blocked.append(f"identifier_policy.{field} must be false.")
    if not _list(policy.get("public_identifier_preference")):
        blocked.append("identifier_policy.public_identifier_preference must not be empty.")
    return tuple(blocked)


def validate_source_manifest_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in (
        "report_only",
        "no_network",
        "no_fetching",
        "no_downloading",
        "no_scraping",
        "no_api_calls",
        "no_writes",
        "no_cache_creation",
        "no_subprocess",
        "no_scheduler_creation",
        "no_broker_integration",
        "no_private_data_ingest",
    ):
        if config.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in ("source_manifest_id", "source_manifest_name"):
        if not _text(config.get(field)):
            blocked.append(f"{field} is required.")
    safety = config.get("safety_controls", {})
    if not isinstance(safety, dict):
        blocked.append("safety_controls must be an object.")
        safety = {}
    for field in FALSE_REQUIRED_SAFETY_FIELDS:
        if _bool(config.get(field)) or _bool(safety.get(field)):
            blocked.append(f"{field} must be false.")
    for field in TRUE_REQUIRED_SAFETY_FIELDS:
        if safety.get(field) is not True:
            blocked.append(f"{field} must be true.")
    categories = config.get("source_categories", [])
    if not isinstance(categories, list):
        blocked.append("source_categories must be a list.")
        categories = []
    category_ids = {_text(item.get("source_category_id")) for item in categories if isinstance(item, dict)}
    for category_id in REQUIRED_SOURCE_CATEGORIES:
        if category_id not in category_ids:
            blocked.append(f"required source category missing: {category_id}")
    required_category_ids = set(_list(config.get("required_source_category_ids")))
    for category_id in REQUIRED_SOURCE_CATEGORIES:
        if category_id not in required_category_ids:
            blocked.append(f"required_source_category_ids missing: {category_id}")
    required_universes = set(_list(config.get("required_asset_universe_ids")))
    for universe_id in REQUIRED_ASSET_UNIVERSES:
        if universe_id not in required_universes:
            blocked.append(f"required_asset_universe_ids missing: {universe_id}")
    sources = config.get("sources", [])
    if not isinstance(sources, list):
        blocked.append("sources must be a list.")
        sources = []
    covered = {universe for item in sources if isinstance(item, dict) for universe in _list(item.get("target_asset_universes"))}
    for universe_id in REQUIRED_ASSET_UNIVERSES:
        if universe_id not in covered:
            blocked.append(f"source entries do not cover required universe: {universe_id}")
    next_action = _text(config.get("next_manual_action"))
    if next_action not in VALID_NEXT_MANUAL_ACTIONS:
        blocked.append("next_manual_action must be an allowed source-manifest action.")
    if next_action in BLOCKED_NEXT_MANUAL_ACTIONS:
        blocked.append(f"next_manual_action must not be {next_action}.")
    for field, validator in (
        ("future_fetch_policy", validate_future_fetch_policy),
        ("local_cache_policy", validate_local_cache_policy),
        ("identifier_policy", validate_identifier_policy),
    ):
        policy = config.get(field, {})
        if not isinstance(policy, dict):
            blocked.append(f"{field} must be an object.")
            policy = {}
        blocked.extend(validator(policy))
    return tuple(blocked)


def evaluate_public_asset_universe_source_manifest(config: dict[str, Any]) -> PublicAssetUniverseSourceManifestResult:
    categories = tuple(
        validate_source_category(item)
        for item in config.get("source_categories", [])
        if isinstance(item, dict)
    )
    known_category_ids = {item.source_category_id for item in categories}
    sources = tuple(
        validate_source_entry(item, known_category_ids=known_category_ids)
        for item in config.get("sources", [])
        if isinstance(item, dict)
    )
    blocked = list(validate_source_manifest_config(config))
    blocked.extend(f"{item.source_category_id}: {reason}" for item in categories for reason in item.blocked_reasons)
    blocked.extend(f"{item.source_id}: {reason}" for item in sources for reason in item.blocked_reasons)
    warnings: list[str] = []
    if blocked:
        status = "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_BLOCKED_SAFE"
    elif len(sources) < len(REQUIRED_ASSET_UNIVERSES):
        status = "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_PARTIAL_SAFE"
    else:
        status = "PUBLIC_ASSET_UNIVERSE_SOURCE_MANIFEST_READY_SAFE"
    safety = config.get("safety_controls", {}) if isinstance(config.get("safety_controls"), dict) else {}
    covered = tuple(sorted({universe for source in sources for universe in source.target_asset_universes}))
    return PublicAssetUniverseSourceManifestResult(
        title=_text(config.get("title")) or "J.A.R.V.I.S. Public Asset Universe Source Manifest",
        version=_text(config.get("version")) or "v4.62",
        overall_status=status,
        manifest_mode=_text(config.get("manifest_mode")),
        report_only=_bool(config.get("report_only")),
        no_network=_bool(config.get("no_network")),
        no_fetching=_bool(config.get("no_fetching")),
        no_downloading=_bool(config.get("no_downloading")),
        no_scraping=_bool(config.get("no_scraping")),
        no_api_calls=_bool(config.get("no_api_calls")),
        no_writes=_bool(config.get("no_writes")),
        no_cache_creation=_bool(config.get("no_cache_creation")),
        no_subprocess=_bool(config.get("no_subprocess")),
        no_scheduler_creation=_bool(config.get("no_scheduler_creation")),
        no_broker_integration=_bool(config.get("no_broker_integration")),
        no_private_data_ingest=_bool(config.get("no_private_data_ingest")),
        source_manifest_id=_text(config.get("source_manifest_id")),
        source_manifest_name=_text(config.get("source_manifest_name")),
        intended_route=_list(config.get("intended_route")),
        source_categories=categories,
        sources=sources,
        required_source_category_ids=_list(config.get("required_source_category_ids")),
        required_asset_universe_ids=_list(config.get("required_asset_universe_ids")),
        covered_asset_universe_ids=covered,
        update_frequency_policy=config.get("update_frequency_policy", {}) if isinstance(config.get("update_frequency_policy"), dict) else {},
        future_fetch_policy=config.get("future_fetch_policy", {}) if isinstance(config.get("future_fetch_policy"), dict) else {},
        local_cache_policy=config.get("local_cache_policy", {}) if isinstance(config.get("local_cache_policy"), dict) else {},
        identifier_policy=config.get("identifier_policy", {}) if isinstance(config.get("identifier_policy"), dict) else {},
        next_manual_action=_text(config.get("next_manual_action")),
        redundant_next_steps_to_avoid=_list(config.get("redundant_next_steps_to_avoid")),
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warnings=tuple(warnings),
        **{field: _bool(safety.get(field)) for field in FALSE_REQUIRED_SAFETY_FIELDS},
        **{field: _bool(safety.get(field)) for field in TRUE_REQUIRED_SAFETY_FIELDS},
    )


def render_source_manifest_summary(result: PublicAssetUniverseSourceManifestResult) -> str:
    return (
        f"status={result.overall_status}; categories={len(result.source_categories)}; "
        f"sources={len(result.sources)}; covered={len(result.covered_asset_universe_ids)}; next={result.next_manual_action}"
    )


def load_public_asset_universe_source_manifest_result(path: str | Path) -> PublicAssetUniverseSourceManifestResult:
    return evaluate_public_asset_universe_source_manifest(load_json(path))
