"""Public asset universe cache integrity and freshness audit.

v4.65 is read-only. It audits explicit cache entries only; it does not scan
directories, fetch, write, repair, normalize, classify, verify evidence, approve,
allocate, trade, or create an executor.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


ALLOWED_CACHE_ROOT = Path("jarvis/local/public_asset_universe")
SUPPORTED_FREQUENCIES = {"daily", "weekly", "monthly", "manual"}

VALID_NEXT_MANUAL_ACTIONS = {
    "review_cache_audit",
    "repair_cache_by_rerunning_authorized_fetch",
    "proceed_to_public_asset_universe_normalizer",
    "fix_cache_metadata",
    "no_manual_asset_entry_required",
}

BLOCKED_NEXT_MANUAL_ACTIONS = {
    "execute_fetch_now",
    "normalize_now",
    "classify_now",
    "evidence_verification",
    "approval",
    "registry_mutation",
    "allocation_recommendation",
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
    "cache_mutation",
    "cache_repair",
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
    "normalization",
    "classification",
    "screening",
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
    "local_cache_only",
    "raw_data_unverified",
    "read_only_audit_only",
)

UNSAFE_METADATA_FIELDS = (
    "evidence_verified",
    "verified_evidence_promotion",
    "approved_asset",
    "trusted_asset",
    "investable",
    "allocation_recommendation",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "registry_mutation",
    "candidate_registry_write",
    "executor_created",
)

REQUIRED_SAFE_TRUE_METADATA_FIELDS = (
    "raw_unverified",
    "discovery_not_verification",
    "classification_not_approval",
    "screening_not_investment_advice",
)


@dataclass(frozen=True)
class CacheEntryAuditResult:
    source_id: str
    raw_cache_path: str
    metadata_path: str
    freshness_status: str
    integrity_status: str
    fetched_at: str
    expected_update_frequency: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class CacheCoverageResult:
    coverage_status: str
    expected_source_count: int
    observed_cache_entry_count: int
    covered_source_count: int
    missing_source_count: int
    failed_source_count: int
    stale_source_count: int
    fresh_source_count: int
    manual_review_source_count: int
    unsafe_metadata_count: int
    hash_mismatch_count: int
    missing_source_ids: tuple[str, ...]


@dataclass(frozen=True)
class PublicAssetUniverseCacheAuditResult:
    title: str
    version: str
    status: str
    audit_mode: str
    source_count: int
    cache_entry_count: int
    fresh_count: int
    stale_count: int
    missing_count: int
    failed_count: int
    hash_mismatch_count: int
    unsafe_metadata_count: int
    invalid_path_count: int
    manual_review_count: int
    coverage_status: str
    coverage: CacheCoverageResult
    per_source_results: tuple[CacheEntryAuditResult, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    next_safe_action: str
    no_network_called: bool = True
    no_fetch_executed: bool = True
    no_cache_written: bool = True
    no_evidence_verification: bool = True
    no_approval: bool = True
    no_allocation: bool = True
    no_trade: bool = True
    no_executor: bool = True
    local_cache_only: bool = True
    raw_data_unverified: bool = True


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


def parse_date_or_datetime(value: Any) -> date | None:
    text = _text(value)
    if not text:
        return None
    normalized = text.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        try:
            return date.fromisoformat(text)
        except ValueError:
            return None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _cache_root(config_or_root: dict[str, Any] | str | Path | None) -> Path:
    if isinstance(config_or_root, dict):
        return Path(_text(config_or_root.get("cache_root")) or ALLOWED_CACHE_ROOT)
    if config_or_root:
        return Path(config_or_root)
    return ALLOWED_CACHE_ROOT


def _path_blockers(path: str | Path, cache_root: str | Path | None = None) -> tuple[str, ...]:
    text = _text(path)
    if not text:
        return ("cache path is required.",)
    normalized = text.replace("\\", "/")
    if normalized.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("cache path must not target docs, templates, or jarvis/data.",)
    root = _cache_root(cache_root).resolve()
    candidate = Path(path).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return ("cache path must stay under the configured cache_root.",)
    lowered = normalized.lower()
    if ("private" in lowered or "account" in lowered) and "public_asset_universe" not in lowered:
        return ("cache path must not target private/account data.",)
    return ()


def validate_expected_source_plan(plan: dict[str, Any], cache_root: str | Path | None = None) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in (
        "source_id",
        "source_name",
        "source_category_id",
        "expected_update_frequency",
        "raw_cache_path",
        "metadata_path",
        "eligibility_status",
        "required_authorization_phrase",
    ):
        if not _text(plan.get(field)):
            blocked.append(f"{field} is required.")
    for field in (
        "public_only",
        "raw_data_unverified",
        "discovery_not_verification",
        "classification_not_approval",
        "screening_not_investment_advice",
    ):
        if plan.get(field) is not True:
            blocked.append(f"{field} must be true.")
    if not _list(plan.get("target_asset_universes")):
        blocked.append("target_asset_universes must not be empty.")
    if not _list(plan.get("expected_fields")):
        blocked.append("expected_fields must not be empty.")
    if _text(plan.get("expected_update_frequency")) not in SUPPORTED_FREQUENCIES:
        blocked.append("expected_update_frequency is unsupported.")
    blocked.extend(f"raw_cache_path: {reason}" for reason in _path_blockers(plan.get("raw_cache_path", ""), cache_root))
    blocked.extend(f"metadata_path: {reason}" for reason in _path_blockers(plan.get("metadata_path", ""), cache_root))
    return tuple(dict.fromkeys(blocked))


def validate_cache_entry(entry: dict[str, Any], cache_root: str | Path | None = None) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in ("source_id", "raw_cache_path", "metadata_path", "expected_update_frequency", "fetch_status"):
        if not _text(entry.get(field)):
            blocked.append(f"{field} is required.")
    if entry.get("file_backed") not in {True, False}:
        blocked.append("file_backed must be true or false.")
    blocked.extend(f"raw_cache_path: {reason}" for reason in _path_blockers(entry.get("raw_cache_path", ""), cache_root))
    blocked.extend(f"metadata_path: {reason}" for reason in _path_blockers(entry.get("metadata_path", ""), cache_root))
    if _text(entry.get("expected_update_frequency")) not in SUPPORTED_FREQUENCIES:
        blocked.append("expected_update_frequency is unsupported.")
    for field in REQUIRED_SAFE_TRUE_METADATA_FIELDS:
        if entry.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in UNSAFE_METADATA_FIELDS:
        value = entry.get(field)
        if value is True or (field == "portfolio_weight" and value not in {False, 0, 0.0, None}):
            blocked.append(f"{field} must be false.")
    return tuple(dict.fromkeys(blocked))


def compute_freshness_status(
    fetched_at: Any,
    current_date: Any,
    expected_update_frequency: str,
    fetch_status: str,
) -> str:
    if fetch_status not in {"fetched_local_cache_only", "ok", "manual_reference"}:
        return "CACHE_FAILED_FETCH_SAFE"
    frequency = _text(expected_update_frequency)
    if frequency == "manual":
        return "CACHE_MANUAL_REVIEW_REQUIRED_SAFE"
    fetched = parse_date_or_datetime(fetched_at)
    current = parse_date_or_datetime(current_date)
    if fetched is None or current is None:
        return "CACHE_BLOCKED_SAFE"
    days = (current - fetched).days
    thresholds = {"daily": 1, "weekly": 7, "monthly": 31}
    if frequency not in thresholds:
        return "CACHE_BLOCKED_SAFE"
    return "CACHE_FRESH_SAFE" if days <= thresholds[frequency] else "CACHE_STALE_SAFE"


def _metadata_unsafe_reasons(metadata: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in REQUIRED_SAFE_TRUE_METADATA_FIELDS:
        if metadata.get(field) is not True:
            blocked.append(f"metadata.{field} must be true.")
    for field in UNSAFE_METADATA_FIELDS:
        value = metadata.get(field)
        if value is True or (field == "portfolio_weight" and value not in {False, 0, 0.0, None}):
            blocked.append(f"metadata.{field} must be false.")
    return tuple(blocked)


def _entry_raw_bytes_and_metadata(entry: dict[str, Any], cache_root: str | Path | None) -> tuple[bytes | None, dict[str, Any] | None, tuple[str, ...]]:
    blocked: list[str] = []
    if entry.get("file_backed") is True:
        raw_path = Path(_text(entry.get("raw_cache_path")))
        metadata_path = Path(_text(entry.get("metadata_path")))
        raw_blockers = _path_blockers(raw_path, cache_root)
        metadata_blockers = _path_blockers(metadata_path, cache_root)
        if raw_blockers or metadata_blockers:
            return None, None, tuple(raw_blockers + metadata_blockers)
        raw_bytes = raw_path.read_bytes() if raw_path.exists() else None
        metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.exists() else None
        return raw_bytes, metadata, ()
    raw_content = entry.get("raw_content_inline")
    raw_bytes = raw_content.encode("utf-8") if isinstance(raw_content, str) else None
    metadata_inline = entry.get("metadata_inline")
    metadata = metadata_inline if isinstance(metadata_inline, dict) else None
    return raw_bytes, metadata, tuple(blocked)


def compute_integrity_status(
    entry: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    raw_bytes: bytes | None = None,
    cache_root: str | Path | None = None,
) -> str:
    if entry.get("fetch_status") not in {"fetched_local_cache_only", "ok", "manual_reference"}:
        return "CACHE_INTEGRITY_FAILED_FETCH_SAFE"
    if _path_blockers(entry.get("raw_cache_path", ""), cache_root) or _path_blockers(entry.get("metadata_path", ""), cache_root):
        return "CACHE_INTEGRITY_INVALID_PATH_SAFE"
    if entry.get("observed_raw_exists") is False or raw_bytes is None:
        return "CACHE_INTEGRITY_MISSING_RAW_SAFE"
    if entry.get("observed_metadata_exists") is False or metadata is None:
        return "CACHE_INTEGRITY_MISSING_METADATA_SAFE"
    if _metadata_unsafe_reasons(metadata):
        return "CACHE_INTEGRITY_UNSAFE_METADATA_SAFE"
    if _text(metadata.get("source_id")) != _text(entry.get("source_id")):
        return "CACHE_INTEGRITY_UNSAFE_METADATA_SAFE"
    observed_hash = sha256_bytes(raw_bytes)
    expected_hash = _text(metadata.get("content_sha256") or entry.get("expected_raw_sha256_from_metadata"))
    if observed_hash != expected_hash:
        return "CACHE_INTEGRITY_HASH_MISMATCH_SAFE"
    expected_length = metadata.get("content_length", entry.get("content_length"))
    if expected_length is not None and int(expected_length) != len(raw_bytes):
        return "CACHE_INTEGRITY_HASH_MISMATCH_SAFE"
    return "CACHE_INTEGRITY_OK_SAFE"


def evaluate_cache_entry(entry: dict[str, Any], current_date: Any, cache_root: str | Path | None = None) -> CacheEntryAuditResult:
    validation = list(validate_cache_entry(entry, cache_root))
    raw_bytes, metadata, read_blockers = _entry_raw_bytes_and_metadata(entry, cache_root)
    validation.extend(read_blockers)
    integrity = compute_integrity_status(entry, metadata=metadata, raw_bytes=raw_bytes, cache_root=cache_root)
    freshness = compute_freshness_status(
        entry.get("fetched_at") or (metadata or {}).get("fetched_at"),
        current_date,
        entry.get("expected_update_frequency"),
        entry.get("fetch_status"),
    )
    blockers = tuple(dict.fromkeys(validation))
    return CacheEntryAuditResult(
        source_id=_text(entry.get("source_id")),
        raw_cache_path=_text(entry.get("raw_cache_path")),
        metadata_path=_text(entry.get("metadata_path")),
        freshness_status=freshness,
        integrity_status=integrity,
        fetched_at=_text(entry.get("fetched_at") or (metadata or {}).get("fetched_at")),
        expected_update_frequency=_text(entry.get("expected_update_frequency")),
        blockers=blockers,
        warnings=(),
    )


def evaluate_cache_coverage(
    expected_source_plans: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    cache_entry_results: tuple[CacheEntryAuditResult, ...],
) -> CacheCoverageResult:
    expected_ids = {_text(plan.get("source_id")) for plan in expected_source_plans if isinstance(plan, dict)}
    observed_ids = {result.source_id for result in cache_entry_results}
    missing_ids = tuple(sorted(expected_ids - observed_ids))
    failed_count = sum(1 for result in cache_entry_results if result.freshness_status == "CACHE_FAILED_FETCH_SAFE" or result.integrity_status == "CACHE_INTEGRITY_FAILED_FETCH_SAFE")
    stale_count = sum(1 for result in cache_entry_results if result.freshness_status == "CACHE_STALE_SAFE")
    fresh_count = sum(1 for result in cache_entry_results if result.freshness_status == "CACHE_FRESH_SAFE")
    manual_count = sum(1 for result in cache_entry_results if result.freshness_status == "CACHE_MANUAL_REVIEW_REQUIRED_SAFE")
    unsafe_count = sum(1 for result in cache_entry_results if result.integrity_status == "CACHE_INTEGRITY_UNSAFE_METADATA_SAFE")
    mismatch_count = sum(1 for result in cache_entry_results if result.integrity_status == "CACHE_INTEGRITY_HASH_MISMATCH_SAFE")
    if unsafe_count:
        coverage_status = "CACHE_COVERAGE_BLOCKED_SAFE"
    elif len(missing_ids) == len(expected_ids) and expected_ids:
        coverage_status = "CACHE_COVERAGE_MISSING_SAFE"
    elif missing_ids or failed_count or stale_count or mismatch_count:
        coverage_status = "CACHE_COVERAGE_PARTIAL_SAFE"
    else:
        coverage_status = "CACHE_COVERAGE_COMPLETE_SAFE"
    return CacheCoverageResult(
        coverage_status=coverage_status,
        expected_source_count=len(expected_ids),
        observed_cache_entry_count=len(cache_entry_results),
        covered_source_count=len(expected_ids & observed_ids),
        missing_source_count=len(missing_ids),
        failed_source_count=failed_count,
        stale_source_count=stale_count,
        fresh_source_count=fresh_count,
        manual_review_source_count=manual_count,
        unsafe_metadata_count=unsafe_count,
        hash_mismatch_count=mismatch_count,
        missing_source_ids=missing_ids,
    )


def validate_cache_audit_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in (
        "report_only",
        "read_only",
        "local_cache_only",
        "no_network",
        "no_fetching",
        "no_downloading",
        "no_scraping",
        "no_api_calls",
        "no_writes",
        "no_cache_mutation",
        "no_cache_repair",
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
        if _bool(safety.get(field)):
            blocked.append(f"safety_controls.{field} must be false.")
    for field in TRUE_REQUIRED_SAFETY_FIELDS:
        if safety.get(field) is not True:
            blocked.append(f"safety_controls.{field} must be true.")
    next_action = _text(config.get("next_manual_action"))
    if next_action not in VALID_NEXT_MANUAL_ACTIONS:
        blocked.append("next_manual_action must be valid.")
    if next_action in BLOCKED_NEXT_MANUAL_ACTIONS:
        blocked.append(f"next_manual_action must not be {next_action}.")
    cache_root = _cache_root(config)
    plans = config.get("expected_source_plans", [])
    entries = config.get("cache_entries", [])
    if not isinstance(plans, list):
        blocked.append("expected_source_plans must be a list.")
        plans = []
    if not isinstance(entries, list):
        blocked.append("cache_entries must be a list.")
        entries = []
    for plan in plans:
        if isinstance(plan, dict):
            blocked.extend(f"{_text(plan.get('source_id'))}: {reason}" for reason in validate_expected_source_plan(plan, cache_root))
    for entry in entries:
        if isinstance(entry, dict):
            blocked.extend(f"{_text(entry.get('source_id'))}: {reason}" for reason in validate_cache_entry(entry, cache_root))
    return tuple(dict.fromkeys(blocked))


def evaluate_public_asset_universe_cache_integrity_freshness_audit(config: dict[str, Any]) -> PublicAssetUniverseCacheAuditResult:
    cache_root = _cache_root(config)
    current_date = config.get("current_date")
    plans = config.get("expected_source_plans", []) if isinstance(config.get("expected_source_plans"), list) else []
    entries = config.get("cache_entries", []) if isinstance(config.get("cache_entries"), list) else []
    per_source = tuple(
        sorted(
            (evaluate_cache_entry(entry, current_date, cache_root) for entry in entries if isinstance(entry, dict)),
            key=lambda item: item.source_id,
        )
    )
    coverage = evaluate_cache_coverage(plans, per_source)
    config_blockers = list(validate_cache_audit_config(config))
    entry_blockers = [f"{result.source_id}: {reason}" for result in per_source for reason in result.blockers]
    blockers = tuple(dict.fromkeys(config_blockers + entry_blockers))
    fresh_count = coverage.fresh_source_count
    stale_count = coverage.stale_source_count
    failed_count = coverage.failed_source_count
    hash_mismatch_count = coverage.hash_mismatch_count
    unsafe_metadata_count = coverage.unsafe_metadata_count
    manual_count = coverage.manual_review_source_count
    invalid_path_count = sum(1 for result in per_source if result.integrity_status == "CACHE_INTEGRITY_INVALID_PATH_SAFE")
    missing_count = coverage.missing_source_count + sum(
        1 for result in per_source if result.integrity_status in {"CACHE_INTEGRITY_MISSING_RAW_SAFE", "CACHE_INTEGRITY_MISSING_METADATA_SAFE"}
    )
    integrity_issue_count = sum(
        1
        for result in per_source
        if result.integrity_status
        in {
            "CACHE_INTEGRITY_HASH_MISMATCH_SAFE",
            "CACHE_INTEGRITY_MISSING_RAW_SAFE",
            "CACHE_INTEGRITY_MISSING_METADATA_SAFE",
            "CACHE_INTEGRITY_FAILED_FETCH_SAFE",
        }
    )
    if blockers or unsafe_metadata_count or invalid_path_count:
        status = "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_BLOCKED_SAFE"
    elif integrity_issue_count:
        status = "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_INTEGRITY_ISSUES_SAFE"
    elif stale_count or missing_count:
        status = "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_STALE_OR_MISSING_SAFE"
    elif coverage.coverage_status != "CACHE_COVERAGE_COMPLETE_SAFE":
        status = "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_PARTIAL_SAFE"
    else:
        status = "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_READY_SAFE"
    warnings = []
    if any(result.freshness_status == "CACHE_BLOCKED_SAFE" for result in per_source):
        warnings.append("one or more sources have unsupported freshness data.")
    return PublicAssetUniverseCacheAuditResult(
        title=_text(config.get("title")) or "J.A.R.V.I.S. Public Asset Universe Cache Integrity + Freshness Audit",
        version=_text(config.get("version")) or "v4.65",
        status=status,
        audit_mode=_text(config.get("audit_mode")),
        source_count=len(plans),
        cache_entry_count=len(per_source),
        fresh_count=fresh_count,
        stale_count=stale_count,
        missing_count=missing_count,
        failed_count=failed_count,
        hash_mismatch_count=hash_mismatch_count,
        unsafe_metadata_count=unsafe_metadata_count,
        invalid_path_count=invalid_path_count,
        manual_review_count=manual_count,
        coverage_status=coverage.coverage_status,
        coverage=coverage,
        per_source_results=per_source,
        blockers=blockers,
        warnings=tuple(warnings),
        next_safe_action=_text(config.get("next_manual_action")),
    )


def render_cache_integrity_freshness_summary(result: PublicAssetUniverseCacheAuditResult) -> str:
    return (
        f"status={result.status}; coverage={result.coverage_status}; sources={result.source_count}; "
        f"entries={result.cache_entry_count}; fresh={result.fresh_count}; stale={result.stale_count}; "
        f"missing={result.missing_count}; failed={result.failed_count}; hash_mismatch={result.hash_mismatch_count}"
    )


def load_public_asset_universe_cache_integrity_freshness_audit_result(path: str | Path) -> PublicAssetUniverseCacheAuditResult:
    return evaluate_public_asset_universe_cache_integrity_freshness_audit(load_json(path))
