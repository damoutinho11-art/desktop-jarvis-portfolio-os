"""Public asset universe local cache builder.

v4.64 is default-off. Evaluation is read-only and never fetches or writes.
Only execute_authorized_local_cache_build may call a fetcher and write raw
unverified public data plus metadata, and only after the exact authorization
phrase is present.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from urllib.request import Request, urlopen

from .jarvis_public_asset_universe_source_manifest import (
    ALLOWED_SOURCE_TYPES,
    REQUIRED_AUTHORIZATION_PHRASE,
    validate_source_entry,
)


ALLOWED_FETCH_METHODS = {
    "explicit_http_get_local_cache_only",
    "explicit_public_file_download_local_cache_only",
    "explicit_public_json_fetch_local_cache_only",
    "explicit_public_csv_fetch_local_cache_only",
}
MANUAL_REFERENCE_METHOD = "manual_download_reference_only"
ALLOWED_ELIGIBILITY_STATUSES = {
    "FETCH_DRY_RUN_ELIGIBLE_SAFE",
    "FETCH_DRY_RUN_MANUAL_REFERENCE_ONLY_SAFE",
}
ALLOWED_WRITE_ROOT = Path("jarvis/local/public_asset_universe")

FALSE_REQUIRED_SAFETY_FIELDS = (
    "scraping",
    "api_calls_without_explicit_authorization",
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

AUTHORIZATION_DEPENDENT_SAFETY_FIELDS = (
    "network_calls",
    "fetching",
    "downloading",
    "writes",
    "cache_creation",
)

TRUE_REQUIRED_SAFETY_FIELDS = (
    "public_data_only",
    "manual_trust_required",
    "manual_approval_required",
    "no_execution_invariant",
    "final_purchase_external_manual_only",
    "local_cache_only",
    "raw_data_unverified",
    "explicit_authorization_required",
)


@dataclass(frozen=True)
class SourceFetchBuildPlan:
    source_id: str
    source_name: str
    source_category_id: str
    target_asset_universes: tuple[str, ...]
    source_type: str
    source_url: str
    allowed_future_fetch_method: str
    eligibility_status: str
    eligible_for_future_fetch: bool
    required_authorization_phrase: str
    raw_cache_path: str
    metadata_path: str
    fetch_plan_path: str
    expected_fields: tuple[str, ...]
    expected_update_frequency: str
    raw_data_unverified: bool
    discovery_not_verification: bool
    classification_not_approval: bool
    screening_not_investment_advice: bool
    public_only: bool
    authentication_required: bool
    credentials_allowed: bool
    broker_api_allowed: bool
    private_data_allowed: bool
    trading_access_allowed: bool
    safety_notes: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class PublicAssetUniverseLocalCacheBuilderResult:
    status: str
    authorization_status: str
    title: str
    version: str
    builder_mode: str
    report_only: bool
    default_no_fetch: bool
    default_no_write: bool
    source_plans: tuple[SourceFetchBuildPlan, ...]
    source_count: int
    fetched_count: int
    skipped_count: int
    blocked_count: int
    failed_count: int
    written_raw_cache_paths: tuple[str, ...]
    written_metadata_paths: tuple[str, ...]
    skipped_sources: tuple[str, ...]
    blocked_sources: tuple[str, ...]
    failed_sources: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    no_evidence_verification: bool
    no_approval: bool
    no_allocation: bool
    no_trade: bool
    no_executor: bool
    local_cache_only: bool
    fetched_data_unverified: bool
    fetch_executed: bool
    writes_performed: bool


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


def validate_authorization_policy(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    if config.get("explicit_authorization_required") is not True:
        blocked.append("explicit_authorization_required must be true.")
    if config.get("authorization_phrase_required") != REQUIRED_AUTHORIZATION_PHRASE:
        blocked.append("authorization_phrase_required must match the strict phrase.")
    if config.get("authorization_phrase") != REQUIRED_AUTHORIZATION_PHRASE:
        blocked.append("authorization_phrase must exactly match the strict phrase.")
    if config.get("authorization_phrase_valid") is not True:
        blocked.append("authorization_phrase_valid must be true.")
    return tuple(blocked)


def _authorization_valid(config: dict[str, Any]) -> bool:
    return (
        config.get("explicit_authorization_required") is True
        and config.get("authorization_phrase_required") == REQUIRED_AUTHORIZATION_PHRASE
        and config.get("authorization_phrase") == REQUIRED_AUTHORIZATION_PHRASE
        and config.get("authorization_phrase_valid") is True
    )


def validate_cache_path(path: str | Path, allowed_root: str | Path = ALLOWED_WRITE_ROOT) -> tuple[str, ...]:
    blocked: list[str] = []
    raw = _text(path).replace("\\", "/")
    if not raw:
        return ("cache path is required.",)
    forbidden_roots = ("jarvis/data/", "docs/", "templates/")
    if any(raw.startswith(prefix) for prefix in forbidden_roots):
        blocked.append("cache path must not target jarvis/data, docs, or templates.")
    allowed = Path(allowed_root).resolve()
    candidate = Path(path).resolve()
    try:
        candidate.relative_to(allowed)
    except ValueError:
        blocked.append("cache path must stay under the allowed local cache root.")
    return tuple(blocked)


def validate_cache_policy(policy: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    if policy.get("allowed_write_root") != "jarvis\\local\\public_asset_universe\\":
        blocked.append("cache_policy.allowed_write_root must be jarvis\\local\\public_asset_universe\\.")
    for field in ("local_cache_only", "cache_paths_ignored_uncommitted_required", "raw_data_unverified"):
        if policy.get(field) is not True:
            blocked.append(f"cache_policy.{field} must be true.")
    planned_paths = _list(policy.get("planned_paths"))
    if not planned_paths:
        blocked.append("cache_policy.planned_paths must not be empty.")
    for planned in planned_paths:
        if not planned.replace("\\", "/").startswith("jarvis/local/public_asset_universe/"):
            blocked.append("cache_policy planned paths must stay under jarvis/local/public_asset_universe.")
    return tuple(blocked)


def _default_extension(plan: dict[str, Any]) -> str:
    if _text(plan.get("allowed_future_fetch_method")) == "explicit_public_csv_fetch_local_cache_only":
        return "csv"
    if _text(plan.get("source_type")) == "public_csv":
        return "csv"
    return "json"


def _expected_path(plan: dict[str, Any], kind: str) -> str:
    source_id = _text(plan.get("source_id"))
    if kind == "raw":
        return f"jarvis\\local\\public_asset_universe\\raw\\{source_id}.raw.{_default_extension(plan)}"
    if kind == "metadata":
        return f"jarvis\\local\\public_asset_universe\\metadata\\{source_id}.metadata.json"
    return f"jarvis\\local\\public_asset_universe\\fetch_plans\\{source_id}.fetch_plan.json"


def validate_source_fetch_plan(plan: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in (
        "source_id",
        "source_name",
        "source_category_id",
        "source_type",
        "source_url",
        "allowed_future_fetch_method",
        "eligibility_status",
        "raw_cache_path",
        "metadata_path",
        "fetch_plan_path",
    ):
        if not _text(plan.get(field)):
            blocked.append(f"{field} is required.")
    if plan.get("eligibility_status") not in ALLOWED_ELIGIBILITY_STATUSES:
        blocked.append("eligibility_status must be an allowed dry-run status.")
    method = _text(plan.get("allowed_future_fetch_method"))
    if method not in ALLOWED_FETCH_METHODS and method != MANUAL_REFERENCE_METHOD:
        blocked.append("allowed_future_fetch_method is not supported by the local cache builder.")
    if _text(plan.get("source_type")) not in ALLOWED_SOURCE_TYPES:
        blocked.append("source_type must be an allowed public source type.")
    for field in (
        "raw_data_unverified",
        "discovery_not_verification",
        "classification_not_approval",
        "screening_not_investment_advice",
        "public_only",
    ):
        if plan.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in (
        "authentication_required",
        "credentials_allowed",
        "broker_api_allowed",
        "private_data_allowed",
        "trading_access_allowed",
    ):
        if plan.get(field) is not False:
            blocked.append(f"{field} must be false.")
    if not _list(plan.get("target_asset_universes")):
        blocked.append("target_asset_universes must not be empty.")
    if not _list(plan.get("expected_fields")):
        blocked.append("expected_fields must not be empty.")
    if not _list(plan.get("safety_notes")):
        blocked.append("safety_notes must not be empty.")
    source_like = dict(plan)
    source_like.setdefault("future_fetch_requires_explicit_authorization", True)
    source_like.setdefault("required_fields_for_future_fetch", ["source_url"])
    source_like.setdefault("future_fetch_output_scope", "raw_unverified_public_source")
    source_like.setdefault("future_cache_path_hint", "jarvis\\local\\public_asset_universe\\raw\\")
    blocked.extend(validate_source_entry(source_like).blocked_reasons)
    for field in ("raw_cache_path", "metadata_path", "fetch_plan_path"):
        path = _text(plan.get(field))
        if not path.replace("\\", "/").startswith("jarvis/local/public_asset_universe/"):
            blocked.append(f"{field} must stay under jarvis/local/public_asset_universe.")
        if path.replace("\\", "/").startswith(("jarvis/data/", "docs/", "templates/")):
            blocked.append(f"{field} must not target jarvis/data, docs, or templates.")
    return tuple(dict.fromkeys(blocked))


def _source_plan(plan: dict[str, Any]) -> SourceFetchBuildPlan:
    return SourceFetchBuildPlan(
        source_id=_text(plan.get("source_id")),
        source_name=_text(plan.get("source_name")),
        source_category_id=_text(plan.get("source_category_id")),
        target_asset_universes=_list(plan.get("target_asset_universes")),
        source_type=_text(plan.get("source_type")),
        source_url=_text(plan.get("source_url")),
        allowed_future_fetch_method=_text(plan.get("allowed_future_fetch_method")),
        eligibility_status=_text(plan.get("eligibility_status")),
        eligible_for_future_fetch=_bool(plan.get("eligible_for_future_fetch")),
        required_authorization_phrase=_text(plan.get("required_authorization_phrase")),
        raw_cache_path=_text(plan.get("raw_cache_path")) or _expected_path(plan, "raw"),
        metadata_path=_text(plan.get("metadata_path")) or _expected_path(plan, "metadata"),
        fetch_plan_path=_text(plan.get("fetch_plan_path")) or _expected_path(plan, "fetch_plan"),
        expected_fields=_list(plan.get("expected_fields")),
        expected_update_frequency=_text(plan.get("expected_update_frequency")),
        raw_data_unverified=_bool(plan.get("raw_data_unverified")),
        discovery_not_verification=_bool(plan.get("discovery_not_verification")),
        classification_not_approval=_bool(plan.get("classification_not_approval")),
        screening_not_investment_advice=_bool(plan.get("screening_not_investment_advice")),
        public_only=_bool(plan.get("public_only")),
        authentication_required=_bool(plan.get("authentication_required")),
        credentials_allowed=_bool(plan.get("credentials_allowed")),
        broker_api_allowed=_bool(plan.get("broker_api_allowed")),
        private_data_allowed=_bool(plan.get("private_data_allowed")),
        trading_access_allowed=_bool(plan.get("trading_access_allowed")),
        safety_notes=_list(plan.get("safety_notes")),
        blockers=validate_source_fetch_plan(plan),
    )


def validate_local_cache_builder_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in ("default_no_fetch", "default_no_write", "explicit_authorization_required", "no_scraping", "no_browser_automation", "no_broker_integration", "no_private_data_ingest"):
        if config.get(field) is not True:
            blocked.append(f"{field} must be true.")
    safety = config.get("safety_controls", {})
    if not isinstance(safety, dict):
        safety = {}
        blocked.append("safety_controls must be an object.")
    authorized = _authorization_valid(config)
    for field in FALSE_REQUIRED_SAFETY_FIELDS:
        if _bool(safety.get(field)):
            blocked.append(f"safety_controls.{field} must be false.")
    for field in TRUE_REQUIRED_SAFETY_FIELDS:
        if safety.get(field) is not True:
            blocked.append(f"safety_controls.{field} must be true.")
    for field in AUTHORIZATION_DEPENDENT_SAFETY_FIELDS:
        if _bool(safety.get(field)) and not authorized:
            blocked.append(f"safety_controls.{field} may be true only with exact authorization.")
    if authorized:
        for field in ("local_cache_only", "raw_data_unverified", "explicit_authorization_required"):
            if safety.get(field) is not True:
                blocked.append(f"safety_controls.{field} must remain true when authorized.")
    else:
        blocked.extend(validate_authorization_policy(config))
    for field in ("cache_policy", "write_policy", "fetch_policy", "metadata_policy"):
        if not isinstance(config.get(field), dict):
            blocked.append(f"{field} must be an object.")
    if isinstance(config.get("cache_policy"), dict):
        blocked.extend(validate_cache_policy(config["cache_policy"]))
    plans = config.get("source_fetch_plans", [])
    if not isinstance(plans, list):
        return tuple(dict.fromkeys(blocked + ["source_fetch_plans must be a list."]))
    for plan in plans:
        if isinstance(plan, dict):
            blocked.extend(f"{_text(plan.get('source_id'))}: {reason}" for reason in validate_source_fetch_plan(plan))
        else:
            blocked.append("source_fetch_plans entries must be objects.")
    return tuple(dict.fromkeys(blocked))


def _fetch_bytes_with_urllib(source_url: str) -> bytes:
    request = Request(source_url, headers={"User-Agent": "JARVIS-local-cache-builder/4.64"})
    with urlopen(request, timeout=30) as response:  # nosec - explicit authorized path only.
        return response.read()


def build_metadata_record(
    source_plan: SourceFetchBuildPlan,
    raw_bytes: bytes,
    raw_cache_path: str | Path,
    metadata_path: str | Path,
    fetched_at: str,
    fetch_method: str,
) -> dict[str, Any]:
    return {
        "source_id": source_plan.source_id,
        "source_name": source_plan.source_name,
        "source_url": source_plan.source_url,
        "source_category_id": source_plan.source_category_id,
        "fetched_at": fetched_at,
        "fetch_method": fetch_method,
        "raw_cache_path": str(raw_cache_path),
        "metadata_path": str(metadata_path),
        "content_length": len(raw_bytes),
        "content_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "fetch_status": "fetched_local_cache_only",
        "raw_unverified": True,
        "discovery_not_verification": True,
        "classification_not_approval": True,
        "screening_not_investment_advice": True,
        "evidence_verified": False,
        "verified_evidence_promotion": False,
        "approved_asset": False,
        "trusted_asset": False,
        "investable": False,
        "allocation_recommendation": False,
        "portfolio_weight": False,
        "buy_signal": False,
        "sell_signal": False,
        "trade_executed": False,
        "registry_mutation": False,
        "candidate_registry_write": False,
        "executor_created": False,
    }


def write_raw_cache(raw_bytes: bytes, raw_cache_path: str | Path) -> None:
    path = Path(raw_cache_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw_bytes)


def write_metadata(metadata: dict[str, Any], metadata_path: str | Path) -> None:
    path = Path(metadata_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _resolve_under_root(planned_path: str, cache_root: str | Path) -> Path:
    normalized = planned_path.replace("\\", "/")
    marker = "jarvis/local/public_asset_universe/"
    suffix = normalized.split(marker, 1)[1] if normalized.startswith(marker) else Path(normalized).name
    return Path(cache_root) / suffix


def evaluate_public_asset_universe_local_cache_builder(config: dict[str, Any]) -> PublicAssetUniverseLocalCacheBuilderResult:
    source_plans = tuple(_source_plan(plan) for plan in config.get("source_fetch_plans", []) if isinstance(plan, dict))
    blockers = validate_local_cache_builder_config(config)
    authorized = _authorization_valid(config)
    blocked_sources = tuple(plan.source_id for plan in source_plans if plan.blockers)
    manual_sources = tuple(plan.source_id for plan in source_plans if plan.eligibility_status == "FETCH_DRY_RUN_MANUAL_REFERENCE_ONLY_SAFE" and not plan.blockers)
    if not authorized:
        status = "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_UNAUTHORIZED_SAFE"
        authorization_status = "unauthorized"
    elif blockers:
        status = "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_BLOCKED_SAFE"
        authorization_status = "authorized_with_blockers"
    else:
        status = "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_READY_TO_FETCH_SAFE"
        authorization_status = "authorized"
    return PublicAssetUniverseLocalCacheBuilderResult(
        status=status,
        authorization_status=authorization_status,
        title=_text(config.get("title")) or "J.A.R.V.I.S. Public Asset Universe Local Cache Builder",
        version=_text(config.get("version")) or "v4.64",
        builder_mode=_text(config.get("builder_mode")),
        report_only=_bool(config.get("report_only")),
        default_no_fetch=_bool(config.get("default_no_fetch")),
        default_no_write=_bool(config.get("default_no_write")),
        source_plans=source_plans,
        source_count=len(source_plans),
        fetched_count=0,
        skipped_count=len(manual_sources),
        blocked_count=len(blocked_sources),
        failed_count=0,
        written_raw_cache_paths=(),
        written_metadata_paths=(),
        skipped_sources=manual_sources,
        blocked_sources=blocked_sources,
        failed_sources=(),
        warnings=("evaluation only; no fetch or write executed",),
        blockers=blockers,
        no_evidence_verification=True,
        no_approval=True,
        no_allocation=True,
        no_trade=True,
        no_executor=True,
        local_cache_only=True,
        fetched_data_unverified=True,
        fetch_executed=False,
        writes_performed=False,
    )


def execute_authorized_local_cache_build(
    config: dict[str, Any],
    fetcher: Callable[[str], bytes] | None = None,
    now: datetime | None = None,
    cache_root_override: str | Path | None = None,
) -> PublicAssetUniverseLocalCacheBuilderResult:
    evaluated = evaluate_public_asset_universe_local_cache_builder(config)
    if evaluated.status != "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_READY_TO_FETCH_SAFE":
        return evaluated
    fetcher = fetcher or _fetch_bytes_with_urllib
    fetched_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    cache_root = Path(cache_root_override) if cache_root_override is not None else ALLOWED_WRITE_ROOT
    written_raw: list[str] = []
    written_metadata: list[str] = []
    skipped: list[str] = []
    failed: list[str] = []
    blocked: list[str] = []
    for plan in evaluated.source_plans:
        if plan.eligibility_status == "FETCH_DRY_RUN_MANUAL_REFERENCE_ONLY_SAFE":
            skipped.append(plan.source_id)
            continue
        if plan.blockers or not plan.eligible_for_future_fetch:
            blocked.append(plan.source_id)
            continue
        raw_path = _resolve_under_root(plan.raw_cache_path, cache_root)
        metadata_path = _resolve_under_root(plan.metadata_path, cache_root)
        raw_blockers = validate_cache_path(raw_path, cache_root)
        metadata_blockers = validate_cache_path(metadata_path, cache_root)
        if raw_blockers or metadata_blockers:
            blocked.append(plan.source_id)
            continue
        try:
            raw_bytes = fetcher(plan.source_url)
            if isinstance(raw_bytes, str):
                raw_bytes = raw_bytes.encode("utf-8")
            metadata = build_metadata_record(
                plan,
                raw_bytes,
                raw_path,
                metadata_path,
                fetched_at,
                plan.allowed_future_fetch_method,
            )
            write_raw_cache(raw_bytes, raw_path)
            write_metadata(metadata, metadata_path)
            written_raw.append(str(raw_path))
            written_metadata.append(str(metadata_path))
        except Exception as exc:  # pragma: no cover - exercised by tests without relying on exact exception type.
            failed.append(f"{plan.source_id}: {exc}")
    if failed or blocked or skipped:
        status = "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_PARTIAL_LOCAL_CACHE_SAFE"
    else:
        status = "PUBLIC_ASSET_UNIVERSE_LOCAL_CACHE_BUILDER_EXECUTED_LOCAL_CACHE_SAFE"
    return PublicAssetUniverseLocalCacheBuilderResult(
        **{
            **evaluated.__dict__,
            "status": status,
            "authorization_status": "authorized",
            "fetched_count": len(written_raw),
            "skipped_count": len(skipped),
            "blocked_count": len(blocked),
            "failed_count": len(failed),
            "written_raw_cache_paths": tuple(written_raw),
            "written_metadata_paths": tuple(written_metadata),
            "skipped_sources": tuple(skipped),
            "blocked_sources": tuple(blocked),
            "failed_sources": tuple(failed),
            "warnings": ("authorized local-cache-only write performed; raw data remains unverified",),
            "blockers": (),
            "fetch_executed": bool(written_raw or failed),
            "writes_performed": bool(written_raw),
        }
    )


def render_local_cache_builder_summary(result: PublicAssetUniverseLocalCacheBuilderResult) -> str:
    return (
        f"status={result.status}; authorization={result.authorization_status}; sources={result.source_count}; "
        f"fetched={result.fetched_count}; skipped={result.skipped_count}; blocked={result.blocked_count}; failed={result.failed_count}"
    )


def load_public_asset_universe_local_cache_builder_result(path: str | Path) -> PublicAssetUniverseLocalCacheBuilderResult:
    return evaluate_public_asset_universe_local_cache_builder(load_json(path))
