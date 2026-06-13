"""Public asset universe fetch dry-run planner.

v4.63 turns a public source manifest into deterministic future-fetch plans.
It is dry-run/report-only: no network calls, fetching, downloads, scraping, API
calls, writes, cache creation, subprocesses, schedulers, browser automation,
broker integration, private ingest, evidence verification, approvals, allocation,
trading, or executor behavior.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .jarvis_public_asset_universe_source_manifest import (
    ALLOWED_FUTURE_FETCH_METHODS,
    ALLOWED_SOURCE_TYPES,
    REQUIRED_AUTHORIZATION_PHRASE,
    validate_source_entry,
)


AUTO_FETCH_METHODS = {
    "explicit_http_get_local_cache_only",
    "explicit_public_file_download_local_cache_only",
    "explicit_public_json_fetch_local_cache_only",
    "explicit_public_csv_fetch_local_cache_only",
}

MANUAL_REFERENCE_METHOD = "manual_download_reference_only"

FETCH_ORDER_PRIORITY = {
    "exchange_or_market_reference_sources": 0,
    "identifier_mapping_sources": 1,
    "exchange_listing_sources": 2,
    "etf_listing_sources": 2,
    "equity_listing_sources": 2,
    "fund_or_etp_listing_sources": 2,
    "issuer_or_provider_sources": 3,
    "fund_provider_sources": 3,
    "regulator_or_filings_sources": 4,
    "public_market_data_sources": 5,
    "crypto_public_reference_sources": 6,
}

VALID_NEXT_MANUAL_ACTIONS = {
    "review_fetch_dry_run_plan",
    "prepare_explicit_public_universe_fetch_local_cache_only",
    "fix_blocked_manifest_sources",
    "no_manual_asset_entry_required",
}

BLOCKED_NEXT_MANUAL_ACTIONS = {
    "execute_fetch_now",
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
    "dry_run_planner_only",
    "source_manifest_required",
)


@dataclass(frozen=True)
class SourceFetchDryRunPlan:
    source_id: str
    source_name: str
    source_category_id: str
    target_asset_universes: tuple[str, ...]
    source_type: str
    source_url: str
    allowed_future_fetch_method: str
    eligible_for_future_fetch: bool
    eligibility_status: str
    blockers: tuple[str, ...]
    required_authorization_phrase: str
    raw_cache_path: str
    metadata_path: str
    fetch_plan_path: str
    expected_fields: tuple[str, ...]
    required_fields_for_future_fetch: tuple[str, ...]
    expected_update_frequency: str
    freshness_requirement: str
    safety_notes: tuple[str, ...]


@dataclass(frozen=True)
class PublicAssetUniverseFetchDryRunResult:
    title: str
    version: str
    status: str
    planner_mode: str
    report_only: bool
    dry_run_only: bool
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
    source_plans: tuple[SourceFetchDryRunPlan, ...]
    source_count: int
    eligible_count: int
    manual_reference_only_count: int
    blocked_count: int
    planned_raw_cache_paths: tuple[str, ...]
    planned_metadata_paths: tuple[str, ...]
    planned_fetch_plan_paths: tuple[str, ...]
    required_authorization_phrase: str
    fetch_order: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    next_safe_action: str
    no_fetch_executed: bool
    no_cache_written: bool
    no_network_called: bool
    authorization_policy: dict[str, Any]
    planned_cache_policy: dict[str, Any]
    freshness_policy: dict[str, Any]
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
    dry_run_planner_only: bool = True
    source_manifest_required: bool = True


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


def validate_authorization_policy(policy: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    expected = {
        "default_fetch_allowed": False,
        "future_fetch_allowed_only_with_explicit_authorization": True,
        "authorization_phrase_present": False,
        "authorization_phrase_valid": False,
        "even_if_authorized_this_stage_still_does_not_fetch": True,
        "local_cache_only": True,
        "fetched_data_unverified": True,
        "no_fetched_data_committed": True,
        "no_evidence_verification": True,
        "no_approval": True,
        "no_allocation": True,
        "no_trade": True,
        "no_executor": True,
    }
    for field, value in expected.items():
        if policy.get(field) is not value:
            blocked.append(f"authorization_policy.{field} must be {str(value).lower()}.")
    if policy.get("required_authorization_phrase") != REQUIRED_AUTHORIZATION_PHRASE:
        blocked.append("authorization_policy.required_authorization_phrase must match the strict phrase.")
    return tuple(blocked)


def validate_planned_cache_policy(policy: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    expected = {
        "planned_cache_paths_only": True,
        "local_cache_only": True,
        "cache_paths_ignored_uncommitted_required": True,
        "raw_data_unverified": True,
        "normalized_data_not_created": True,
        "no_cache_written": True,
        "no_fetched_data_committed": True,
    }
    for field, value in expected.items():
        if policy.get(field) is not value:
            blocked.append(f"planned_cache_policy.{field} must be {str(value).lower()}.")
    planned_paths = _list(policy.get("planned_paths"))
    if not planned_paths:
        blocked.append("planned_cache_policy.planned_paths must not be empty.")
    for path in planned_paths:
        if not path.replace("\\", "/").startswith("jarvis/local/public_asset_universe/"):
            blocked.append("planned_cache_policy planned paths must be under jarvis/local/public_asset_universe.")
    return tuple(blocked)


def validate_source_for_fetch_plan(source: dict[str, Any]) -> tuple[str, ...]:
    blocked = list(validate_source_entry(source).blocked_reasons)
    fetch_method = _text(source.get("allowed_future_fetch_method"))
    if fetch_method not in AUTO_FETCH_METHODS and fetch_method != MANUAL_REFERENCE_METHOD:
        blocked.append("allowed_future_fetch_method is not supported by the dry-run planner.")
    return tuple(blocked)


def _planned_extension(source: dict[str, Any]) -> str:
    if _text(source.get("allowed_future_fetch_method")) == "explicit_public_csv_fetch_local_cache_only":
        return "csv"
    if _text(source.get("source_type")) == "public_csv":
        return "csv"
    return "json"


def _cache_base(policy: dict[str, Any], key: str, fallback: str) -> str:
    value = _text(policy.get(key))
    return value if value else fallback


def _join_planned_path(base: str, filename: str) -> str:
    return base.rstrip("\\/") + "\\" + filename


def build_source_fetch_dry_run_plan(source: dict[str, Any], planned_cache_policy: dict[str, Any]) -> SourceFetchDryRunPlan:
    source_id = _text(source.get("source_id"))
    blockers = list(validate_source_for_fetch_plan(source))
    fetch_method = _text(source.get("allowed_future_fetch_method"))
    if blockers:
        status = "FETCH_DRY_RUN_BLOCKED_SAFE"
        eligible = False
    elif fetch_method == MANUAL_REFERENCE_METHOD:
        status = "FETCH_DRY_RUN_MANUAL_REFERENCE_ONLY_SAFE"
        eligible = False
    else:
        status = "FETCH_DRY_RUN_ELIGIBLE_SAFE"
        eligible = True
    extension = _planned_extension(source)
    raw_base = _cache_base(planned_cache_policy, "raw_cache_base_path", "jarvis\\local\\public_asset_universe\\raw\\")
    metadata_base = _cache_base(planned_cache_policy, "metadata_base_path", "jarvis\\local\\public_asset_universe\\metadata\\")
    fetch_plan_base = _cache_base(planned_cache_policy, "fetch_plan_base_path", "jarvis\\local\\public_asset_universe\\fetch_plans\\")
    return SourceFetchDryRunPlan(
        source_id=source_id,
        source_name=_text(source.get("source_name")),
        source_category_id=_text(source.get("source_category_id")),
        target_asset_universes=_list(source.get("target_asset_universes")),
        source_type=_text(source.get("source_type")),
        source_url=_text(source.get("source_url")),
        allowed_future_fetch_method=fetch_method,
        eligible_for_future_fetch=eligible,
        eligibility_status=status,
        blockers=tuple(dict.fromkeys(blockers)),
        required_authorization_phrase=REQUIRED_AUTHORIZATION_PHRASE,
        raw_cache_path=_join_planned_path(raw_base, f"{source_id}.raw.{extension}"),
        metadata_path=_join_planned_path(metadata_base, f"{source_id}.metadata.json"),
        fetch_plan_path=_join_planned_path(fetch_plan_base, f"{source_id}.fetch_plan.json"),
        expected_fields=_list(source.get("expected_fields")),
        required_fields_for_future_fetch=_list(source.get("required_fields_for_future_fetch")),
        expected_update_frequency=_text(source.get("expected_update_frequency")),
        freshness_requirement=_text(source.get("freshness_requirement")) or _text(source.get("expected_update_frequency")),
        safety_notes=_list(source.get("safety_notes")),
    )


def compute_fetch_order(source_plans: tuple[SourceFetchDryRunPlan, ...]) -> tuple[str, ...]:
    ordered = sorted(
        source_plans,
        key=lambda plan: (
            FETCH_ORDER_PRIORITY.get(plan.source_category_id, 99),
            plan.source_category_id,
            plan.source_id,
        ),
    )
    return tuple(plan.source_id for plan in ordered)


def validate_fetch_dry_run_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in (
        "report_only",
        "dry_run_only",
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
    if not isinstance(config.get("source_manifest"), dict):
        blocked.append("source_manifest must be present.")
    for field, validator in (
        ("authorization_policy", validate_authorization_policy),
        ("planned_cache_policy", validate_planned_cache_policy),
    ):
        policy = config.get(field, {})
        if not isinstance(policy, dict):
            blocked.append(f"{field} must be an object.")
            policy = {}
        blocked.extend(validator(policy))
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
    next_action = _text(config.get("next_manual_action"))
    if next_action not in VALID_NEXT_MANUAL_ACTIONS:
        blocked.append("next_manual_action must be an allowed fetch dry-run action.")
    if next_action in BLOCKED_NEXT_MANUAL_ACTIONS:
        blocked.append(f"next_manual_action must not be {next_action}.")
    return tuple(blocked)


def evaluate_public_asset_universe_fetch_dry_run(config: dict[str, Any]) -> PublicAssetUniverseFetchDryRunResult:
    manifest = config.get("source_manifest", {}) if isinstance(config.get("source_manifest"), dict) else {}
    planned_cache_policy = config.get("planned_cache_policy", {}) if isinstance(config.get("planned_cache_policy"), dict) else {}
    source_plans = tuple(
        build_source_fetch_dry_run_plan(source, planned_cache_policy)
        for source in manifest.get("sources", [])
        if isinstance(source, dict)
    )
    config_blockers = list(validate_fetch_dry_run_config(config))
    source_blockers = [f"{plan.source_id}: {reason}" for plan in source_plans for reason in plan.blockers]
    blockers = tuple(dict.fromkeys(config_blockers + source_blockers))
    eligible_count = sum(1 for plan in source_plans if plan.eligibility_status == "FETCH_DRY_RUN_ELIGIBLE_SAFE")
    manual_count = sum(1 for plan in source_plans if plan.eligibility_status == "FETCH_DRY_RUN_MANUAL_REFERENCE_ONLY_SAFE")
    blocked_count = sum(1 for plan in source_plans if plan.eligibility_status == "FETCH_DRY_RUN_BLOCKED_SAFE")
    if config_blockers or not source_plans or (source_plans and blocked_count == len(source_plans)):
        status = "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_BLOCKED_SAFE"
    elif source_blockers:
        status = "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_PARTIAL_SAFE"
    else:
        status = "PUBLIC_ASSET_UNIVERSE_FETCH_DRY_RUN_READY_SAFE"
    safety = config.get("safety_controls", {}) if isinstance(config.get("safety_controls"), dict) else {}
    return PublicAssetUniverseFetchDryRunResult(
        title=_text(config.get("title")) or "J.A.R.V.I.S. Public Asset Universe Fetch Dry-Run Planner",
        version=_text(config.get("version")) or "v4.63",
        status=status,
        planner_mode=_text(config.get("planner_mode")),
        report_only=_bool(config.get("report_only")),
        dry_run_only=_bool(config.get("dry_run_only")),
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
        source_plans=source_plans,
        source_count=len(source_plans),
        eligible_count=eligible_count,
        manual_reference_only_count=manual_count,
        blocked_count=blocked_count,
        planned_raw_cache_paths=tuple(plan.raw_cache_path for plan in source_plans),
        planned_metadata_paths=tuple(plan.metadata_path for plan in source_plans),
        planned_fetch_plan_paths=tuple(plan.fetch_plan_path for plan in source_plans),
        required_authorization_phrase=REQUIRED_AUTHORIZATION_PHRASE,
        fetch_order=compute_fetch_order(source_plans),
        blockers=blockers,
        warnings=(),
        next_safe_action=_text(config.get("next_manual_action")),
        no_fetch_executed=True,
        no_cache_written=True,
        no_network_called=True,
        authorization_policy=config.get("authorization_policy", {}) if isinstance(config.get("authorization_policy"), dict) else {},
        planned_cache_policy=planned_cache_policy,
        freshness_policy=config.get("freshness_policy", {}) if isinstance(config.get("freshness_policy"), dict) else {},
        **{field: _bool(safety.get(field)) for field in FALSE_REQUIRED_SAFETY_FIELDS},
        **{field: _bool(safety.get(field)) for field in TRUE_REQUIRED_SAFETY_FIELDS},
    )


def render_fetch_dry_run_summary(result: PublicAssetUniverseFetchDryRunResult) -> str:
    return (
        f"status={result.status}; sources={result.source_count}; eligible={result.eligible_count}; "
        f"manual={result.manual_reference_only_count}; blocked={result.blocked_count}; next={result.next_safe_action}"
    )


def load_public_asset_universe_fetch_dry_run_result(path: str | Path) -> PublicAssetUniverseFetchDryRunResult:
    return evaluate_public_asset_universe_fetch_dry_run(load_json(path))
