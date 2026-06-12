"""Public asset universe discovery plan evaluator.

v4.61 is a plan/schema/report layer only. It defines the future public asset
universe discovery direction without fetching, downloading, scraping, writing,
parsing sources as evidence, approving assets, recommending allocation, trading,
or integrating with brokers.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_TARGET_UNIVERSES = (
    "etf_universe",
    "equity_universe",
    "fund_or_etp_universe",
    "crypto_asset_universe",
    "exchange_or_market_reference_universe",
)

REQUIRED_SOURCE_CATEGORIES = (
    "exchange_listing_sources",
    "issuer_or_provider_sources",
    "regulator_or_filings_sources",
    "fund_provider_sources",
    "public_market_data_sources",
    "crypto_public_reference_sources",
    "identifier_mapping_sources",
)

REQUIRED_FUTURE_STAGES = (
    "v4.62",
    "v4.63",
    "v4.64",
    "v4.65",
    "v4.66",
    "v4.67",
    "v4.68",
    "v5.0",
)

VALID_NEXT_MANUAL_ACTIONS = {
    "define_public_source_manifest",
    "review_discovery_plan",
    "prepare_public_universe_source_manifest",
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
)

FORBIDDEN_SCREENING_OUTPUTS = {
    "BUY",
    "SELL",
    "HOLD",
    "HOLD_RECOMMENDATION",
    "APPROVED",
    "TRUSTED",
    "INVESTABLE",
    "ALLOCATION",
    "PORTFOLIO_WEIGHT",
    "TRADE",
}

REQUIRED_DEFAULT_STATUS_FIELDS = {
    "evidence_status": "UNVERIFIED_PUBLIC_DATA",
    "approval_status": "NOT_APPROVED",
    "investability_status": "NOT_INVESTABLE",
    "execution_status": "NO_EXECUTION",
}


@dataclass(frozen=True)
class TargetUniversePlan:
    universe_id: str
    universe_name: str
    asset_class: str
    required_fields: tuple[str, ...]
    source_categories: tuple[str, ...]
    blocked_reasons: tuple[str, ...]


@dataclass(frozen=True)
class SourceCategoryPlan:
    source_category_id: str
    source_category_name: str
    intended_use: str
    expected_update_frequency: str
    expected_fields: tuple[str, ...]
    blocked_reasons: tuple[str, ...]


@dataclass(frozen=True)
class FutureStagePlan:
    stage_id: str
    stage_name: str
    real_new_boundary: bool
    purpose: str
    why_not_redundant: str
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class PublicAssetUniverseDiscoveryPlanResult:
    title: str
    version: str
    overall_status: str
    plan_mode: str
    report_only: bool
    no_network: bool
    no_fetching: bool
    no_downloading: bool
    no_writes: bool
    no_cache_creation: bool
    no_subprocess: bool
    no_scheduler_creation: bool
    no_broker_integration: bool
    no_private_data_ingest: bool
    target_asset_universes: tuple[TargetUniversePlan, ...]
    public_source_categories: tuple[SourceCategoryPlan, ...]
    required_universe_fields: dict[str, tuple[str, ...]]
    freshness_policy: dict[str, Any]
    local_cache_plan: dict[str, Any]
    classification_plan: dict[str, Any]
    screening_plan: dict[str, Any]
    evidence_readiness_route: tuple[str, ...]
    human_action_boundary: dict[str, Any]
    future_build_sequence: tuple[FutureStagePlan, ...]
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


def validate_target_universe(universe: dict[str, Any]) -> TargetUniversePlan:
    blocked: list[str] = []
    for field in (
        "universe_id",
        "universe_name",
        "asset_class",
        "scope_description",
        "freshness_requirement",
        "evidence_pipeline_route",
    ):
        if not _text(universe.get(field)):
            blocked.append(f"{field} is required.")
    for field in ("public_only", "source_manifest_required", "local_cache_required_later", "automated_discovery_goal"):
        if universe.get(field) is not True:
            blocked.append(f"{field} must be true.")
    if universe.get("manual_entry_primary_path") is not False:
        blocked.append("manual_entry_primary_path must be false.")
    required_fields = _list(universe.get("required_fields"))
    if not required_fields:
        blocked.append("required_fields must not be empty.")
    for field, expected in REQUIRED_DEFAULT_STATUS_FIELDS.items():
        defaults = universe.get("default_status_values", {})
        if not isinstance(defaults, dict) or defaults.get(field) != expected:
            blocked.append(f"{field} must default to {expected}.")
        if field not in required_fields:
            blocked.append(f"{field} must be a required field.")
    for field in ("source_categories", "classification_tags", "safety_notes"):
        if not _list(universe.get(field)):
            blocked.append(f"{field} must not be empty.")
    return TargetUniversePlan(
        universe_id=_text(universe.get("universe_id")),
        universe_name=_text(universe.get("universe_name")),
        asset_class=_text(universe.get("asset_class")),
        required_fields=required_fields,
        source_categories=_list(universe.get("source_categories")),
        blocked_reasons=tuple(blocked),
    )


def validate_source_category(source_category: dict[str, Any]) -> SourceCategoryPlan:
    blocked: list[str] = []
    for field in ("source_category_id", "source_category_name", "intended_use", "expected_update_frequency"):
        if not _text(source_category.get(field)):
            blocked.append(f"{field} is required.")
    for field in ("public_only", "future_manifest_required", "future_fetch_allowed_only_with_explicit_authorization"):
        if source_category.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in ("authentication_required", "credentials_allowed", "broker_api_allowed", "private_data_allowed"):
        if source_category.get(field) is not False:
            blocked.append(f"{field} must be false.")
    if not _list(source_category.get("expected_fields")):
        blocked.append("expected_fields must not be empty.")
    return SourceCategoryPlan(
        source_category_id=_text(source_category.get("source_category_id")),
        source_category_name=_text(source_category.get("source_category_name")),
        intended_use=_text(source_category.get("intended_use")),
        expected_update_frequency=_text(source_category.get("expected_update_frequency")),
        expected_fields=_list(source_category.get("expected_fields")),
        blocked_reasons=tuple(blocked),
    )


def validate_future_stage(stage: dict[str, Any]) -> FutureStagePlan:
    blocked: list[str] = []
    warnings: list[str] = []
    for field in ("stage_id", "stage_name", "purpose", "why_not_redundant"):
        if not _text(stage.get(field)):
            blocked.append(f"{field} is required.")
    if stage.get("real_new_boundary") is not True:
        warnings.append("real_new_boundary false: possibly redundant.")
    if not _list(stage.get("must_not_do")):
        blocked.append("must_not_do must not be empty.")
    return FutureStagePlan(
        stage_id=_text(stage.get("stage_id")),
        stage_name=_text(stage.get("stage_name")),
        real_new_boundary=_bool(stage.get("real_new_boundary")),
        purpose=_text(stage.get("purpose")),
        why_not_redundant=_text(stage.get("why_not_redundant")),
        blocked_reasons=tuple(blocked),
        warnings=tuple(warnings),
    )


def _validate_human_action_boundary(boundary: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    required_true = (
        "user_may_manually_buy_externally",
        "jarvis_may_prepare_research_dashboard",
        "jarvis_may_prepare_evidence_pack_later",
    )
    required_false = (
        "jarvis_may_execute_trade",
        "jarvis_may_login_to_broker",
        "jarvis_may_store_credentials",
        "jarvis_may_call_broker_api",
        "jarvis_may_recommend_allocation",
        "jarvis_may_emit_buy_sell_signal",
    )
    for field in required_true:
        if boundary.get(field) is not True:
            blocked.append(f"human_action_boundary.{field} must be true.")
    for field in required_false:
        if boundary.get(field) is not False:
            blocked.append(f"human_action_boundary.{field} must be false.")
    return tuple(blocked)


def validate_discovery_plan_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in (
        "report_only",
        "no_network",
        "no_fetching",
        "no_downloading",
        "no_writes",
        "no_cache_creation",
        "no_subprocess",
        "no_scheduler_creation",
        "no_broker_integration",
        "no_private_data_ingest",
    ):
        if config.get(field) is not True:
            blocked.append(f"{field} must be true.")
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
    universes = config.get("target_asset_universes", [])
    if not isinstance(universes, list):
        blocked.append("target_asset_universes must be a list.")
        universes = []
    universe_ids = {_text(item.get("universe_id")) for item in universes if isinstance(item, dict)}
    for universe_id in REQUIRED_TARGET_UNIVERSES:
        if universe_id not in universe_ids:
            blocked.append(f"required target universe missing: {universe_id}")
    categories = config.get("public_source_categories", [])
    if not isinstance(categories, list):
        blocked.append("public_source_categories must be a list.")
        categories = []
    category_ids = {_text(item.get("source_category_id")) for item in categories if isinstance(item, dict)}
    for category_id in REQUIRED_SOURCE_CATEGORIES:
        if category_id not in category_ids:
            blocked.append(f"required source category missing: {category_id}")
    stage_ids = {_text(item.get("stage_id")) for item in config.get("future_build_sequence", []) if isinstance(item, dict)}
    for stage_id in REQUIRED_FUTURE_STAGES:
        if stage_id not in stage_ids:
            blocked.append(f"required future stage missing: {stage_id}")
    next_action = _text(config.get("next_manual_action"))
    if next_action not in VALID_NEXT_MANUAL_ACTIONS:
        blocked.append("next_manual_action must be an allowed discovery-plan action.")
    if next_action in BLOCKED_NEXT_MANUAL_ACTIONS:
        blocked.append(f"next_manual_action must not be {next_action}.")
    boundary = config.get("human_action_boundary", {})
    if not isinstance(boundary, dict):
        blocked.append("human_action_boundary must be an object.")
        boundary = {}
    blocked.extend(_validate_human_action_boundary(boundary))
    outputs = set(_list(config.get("screening_plan", {}).get("allowed_outputs") if isinstance(config.get("screening_plan"), dict) else ()))
    if outputs & FORBIDDEN_SCREENING_OUTPUTS:
        blocked.append("screening_plan allowed_outputs must not include recommendation or execution outputs.")
    return tuple(blocked)


def evaluate_public_asset_universe_discovery_plan(config: dict[str, Any]) -> PublicAssetUniverseDiscoveryPlanResult:
    universes = tuple(
        validate_target_universe(item)
        for item in config.get("target_asset_universes", [])
        if isinstance(item, dict)
    )
    categories = tuple(
        validate_source_category(item)
        for item in config.get("public_source_categories", [])
        if isinstance(item, dict)
    )
    stages = tuple(
        validate_future_stage(item)
        for item in config.get("future_build_sequence", [])
        if isinstance(item, dict)
    )
    blocked = list(validate_discovery_plan_config(config))
    blocked.extend(f"{item.universe_id}: {reason}" for item in universes for reason in item.blocked_reasons)
    blocked.extend(f"{item.source_category_id}: {reason}" for item in categories for reason in item.blocked_reasons)
    blocked.extend(f"{item.stage_id}: {reason}" for item in stages for reason in item.blocked_reasons)
    warnings = [f"{item.stage_id}: {warning}" for item in stages for warning in item.warnings]
    if blocked:
        status = "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_BLOCKED_SAFE"
    elif warnings or len(universes) < len(REQUIRED_TARGET_UNIVERSES) or len(categories) < len(REQUIRED_SOURCE_CATEGORIES):
        status = "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_PARTIAL_SAFE"
    else:
        status = "PUBLIC_ASSET_UNIVERSE_DISCOVERY_PLAN_READY_SAFE"
    safety = config.get("safety_controls", {}) if isinstance(config.get("safety_controls"), dict) else {}
    raw_required_fields = config.get("required_universe_fields", {})
    required_fields = {
        _text(key): _list(value)
        for key, value in raw_required_fields.items()
    } if isinstance(raw_required_fields, dict) else {}
    return PublicAssetUniverseDiscoveryPlanResult(
        title=_text(config.get("title")) or "J.A.R.V.I.S. Public Asset Universe Discovery Plan",
        version=_text(config.get("version")) or "v4.61",
        overall_status=status,
        plan_mode=_text(config.get("plan_mode")),
        report_only=_bool(config.get("report_only")),
        no_network=_bool(config.get("no_network")),
        no_fetching=_bool(config.get("no_fetching")),
        no_downloading=_bool(config.get("no_downloading")),
        no_writes=_bool(config.get("no_writes")),
        no_cache_creation=_bool(config.get("no_cache_creation")),
        no_subprocess=_bool(config.get("no_subprocess")),
        no_scheduler_creation=_bool(config.get("no_scheduler_creation")),
        no_broker_integration=_bool(config.get("no_broker_integration")),
        no_private_data_ingest=_bool(config.get("no_private_data_ingest")),
        target_asset_universes=universes,
        public_source_categories=categories,
        required_universe_fields=required_fields,
        freshness_policy=config.get("freshness_policy", {}) if isinstance(config.get("freshness_policy"), dict) else {},
        local_cache_plan=config.get("local_cache_plan", {}) if isinstance(config.get("local_cache_plan"), dict) else {},
        classification_plan=config.get("classification_plan", {}) if isinstance(config.get("classification_plan"), dict) else {},
        screening_plan=config.get("screening_plan", {}) if isinstance(config.get("screening_plan"), dict) else {},
        evidence_readiness_route=_list(config.get("evidence_readiness_route")),
        human_action_boundary=config.get("human_action_boundary", {}) if isinstance(config.get("human_action_boundary"), dict) else {},
        future_build_sequence=stages,
        next_manual_action=_text(config.get("next_manual_action")),
        redundant_next_steps_to_avoid=_list(config.get("redundant_next_steps_to_avoid")),
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warnings=tuple(warnings),
        **{field: _bool(safety.get(field)) for field in FALSE_REQUIRED_SAFETY_FIELDS},
        **{field: _bool(safety.get(field)) for field in TRUE_REQUIRED_SAFETY_FIELDS},
    )


def render_discovery_plan_summary(result: PublicAssetUniverseDiscoveryPlanResult) -> str:
    return (
        f"status={result.overall_status}; universes={len(result.target_asset_universes)}; "
        f"sources={len(result.public_source_categories)}; next={result.next_manual_action}"
    )


def load_public_asset_universe_discovery_plan_result(path: str | Path) -> PublicAssetUniverseDiscoveryPlanResult:
    return evaluate_public_asset_universe_discovery_plan(load_json(path))
