"""Public data freshness monitor.

v4.58 is read-only/report-only. It evaluates local cache metadata for public
data freshness. It performs no network calls, fetching, downloading, parsing as
evidence, evidence extraction, verification, approval, registry mutation,
recommendation, trade, or executor work.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


ALLOWED_UPDATE_FREQUENCIES = {"daily", "weekly", "manual"}
BLOCKED_QUERY_KEYS = {"api_key", "token", "secret", "password", "auth", "credential"}

UNSAFE_TRUE_FIELDS = (
    "execute_fetch",
    "parse_evidence",
    "verify_evidence",
    "promote_verified_evidence",
    "approved_asset",
    "trusted_asset",
    "investable",
    "allocation_recommendation",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "registry_mutation",
    "registry_file_written",
    "candidate_registry_write",
    "candidate_intake_file_written",
    "persisted_packet_file",
    "executor_created",
    "broker_api_used",
    "credentials_used",
    "automatic_source_fetching",
    "automatic_download",
    "private_file_ingested",
    "evidence_collection_started",
    "evidence_verification_started",
    "fetched_data_committed",
)


@dataclass(frozen=True)
class CacheEntryValidation:
    source_id: str
    cache_path: str
    valid: bool
    blocked_reasons: tuple[str, ...]


@dataclass(frozen=True)
class SourceFreshnessResult:
    source_id: str
    candidate_id: str
    update_frequency: str
    latest_fetched_at: str
    freshness_status: str
    next_safe_action: str
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class PublicDataFreshnessMonitorResult:
    title: str
    version: str
    overall_status: str
    monitor_mode: str
    report_only: bool
    no_network: bool
    execute_fetch: bool
    current_date: str
    source_count: int
    cache_entry_count: int
    fresh_count: int
    stale_count: int
    missing_count: int
    manual_policy_count: int
    failed_count: int
    source_results: tuple[SourceFreshnessResult, ...]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    no_fetching: bool = True
    no_downloading: bool = True
    evidence_extraction: bool = False
    evidence_verification: bool = False
    verified_evidence_promotion: bool = False
    registry_mutation: bool = False
    registry_file_written: bool = False
    candidate_registry_write: bool = False
    candidate_intake_file_written: bool = False
    allocation_recommendation: bool = False
    portfolio_weight: bool = False
    buy_signal: bool = False
    sell_signal: bool = False
    trade_executed: bool = False
    executor_created: bool = False
    broker_api_used: bool = False
    credentials_used: bool = False
    private_file_ingested: bool = False


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_date_or_datetime(value: Any) -> date | None:
    text = _text(value)
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None


def validate_monitor_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    if config.get("report_only") is not True:
        blocked.append("report_only must be true.")
    if config.get("no_network") is not True:
        blocked.append("no_network must be true.")
    for field in UNSAFE_TRUE_FIELDS:
        if _bool(config.get(field)):
            blocked.append(f"{field} must be false.")
    safety = config.get("safety_controls", {})
    if isinstance(safety, dict):
        for field in UNSAFE_TRUE_FIELDS:
            if _bool(safety.get(field)):
                blocked.append(f"safety_controls.{field} must be false.")
        if safety.get("no_network") is not True:
            blocked.append("safety_controls.no_network must be true.")
        if safety.get("report_only") is not True:
            blocked.append("safety_controls.report_only must be true.")
    else:
        blocked.append("safety_controls must be an object.")
    if parse_date_or_datetime(config.get("current_date")) is None:
        blocked.append("current_date must be an ISO date.")
    return tuple(blocked)


def validate_source(source: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    update_frequency = _text(source.get("update_frequency"))
    if update_frequency not in ALLOWED_UPDATE_FREQUENCIES:
        blocked.append("update_frequency must be daily, weekly, or manual.")
    if source.get("public_source_only") is not True:
        blocked.append("public_source_only must be true.")
    for field in ("requires_authentication", "requires_credentials", "broker_or_trading_api", "contains_private_data"):
        if _bool(source.get(field)):
            blocked.append(f"{field} must be false.")
    source_url = _text(source.get("source_url"))
    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"}:
        blocked.append("source_url must be http or https.")
    query_keys = {key.lower() for key in parse_qs(parsed.query).keys()}
    for key in sorted(query_keys.intersection(BLOCKED_QUERY_KEYS)):
        blocked.append(f"credential-looking query parameter is blocked: {key}")
    return tuple(blocked)


def validate_cache_entry(entry: dict[str, Any]) -> CacheEntryValidation:
    blocked: list[str] = []
    source_id = _text(entry.get("source_id")) or "unknown_source"
    cache_path = _text(entry.get("cache_path"))
    normalized = cache_path.replace("\\", "/").lower()
    if not normalized.startswith("jarvis/local/"):
        blocked.append("cache_path must be under jarvis/local.")
    for disallowed in ("jarvis/data/", "docs/", "templates/"):
        if normalized.startswith(disallowed):
            blocked.append(f"cache_path must not be under {disallowed.rstrip('/')}.")
    if entry.get("raw_unverified") is not True:
        blocked.append("raw_unverified must be true.")
    if entry.get("local_cache_only") is not True:
        blocked.append("local_cache_only must be true.")
    if entry.get("committed_to_git") is not False:
        blocked.append("committed_to_git must be false.")
    if parse_date_or_datetime(entry.get("fetched_at")) is None:
        blocked.append("fetched_at must be an ISO date.")
    return CacheEntryValidation(source_id=source_id, cache_path=cache_path, valid=not blocked, blocked_reasons=tuple(blocked))


def _latest_entry(entries: list[dict[str, Any]]) -> dict[str, Any] | None:
    dated = [(parse_date_or_datetime(entry.get("fetched_at")), entry) for entry in entries]
    dated = [(fetched_at, entry) for fetched_at, entry in dated if fetched_at is not None]
    if not dated:
        return None
    return sorted(dated, key=lambda item: item[0], reverse=True)[0][1]


def evaluate_source_freshness(
    source: dict[str, Any], cache_entries: list[dict[str, Any]], current_date: date
) -> SourceFreshnessResult:
    source_id = _text(source.get("source_id")) or "unknown_source"
    blocked = list(validate_source(source))
    matching_entries = [entry for entry in cache_entries if _text(entry.get("source_id")) == source_id]
    cache_validations = [validate_cache_entry(entry) for entry in matching_entries]
    for validation in cache_validations:
        if not validation.valid:
            blocked.extend(validation.blocked_reasons)
    if blocked:
        return SourceFreshnessResult(
            source_id=source_id,
            candidate_id=_text(source.get("candidate_id")),
            update_frequency=_text(source.get("update_frequency")),
            latest_fetched_at="none",
            freshness_status="SOURCE_BLOCKED_SAFE",
            next_safe_action="fix_manifest_or_cache_metadata",
            blocked_reasons=tuple(dict.fromkeys(blocked)),
            warnings=(),
        )
    frequency = _text(source.get("update_frequency"))
    latest = _latest_entry(matching_entries)
    if frequency == "manual":
        return SourceFreshnessResult(
            source_id=source_id,
            candidate_id=_text(source.get("candidate_id")),
            update_frequency=frequency,
            latest_fetched_at=_text(latest.get("fetched_at")) if latest else "none",
            freshness_status="SOURCE_MANUAL_POLICY_SAFE",
            next_safe_action="manually_review_manual_frequency_source",
            blocked_reasons=(),
            warnings=("manual source requires human refresh policy.",),
        )
    if latest is None:
        return SourceFreshnessResult(
            source_id=source_id,
            candidate_id=_text(source.get("candidate_id")),
            update_frequency=frequency,
            latest_fetched_at="none",
            freshness_status="SOURCE_MISSING_SAFE",
            next_safe_action="run_v4_57_explicit_public_fetch_local_cache_only",
            blocked_reasons=(),
            warnings=(),
        )
    if _text(latest.get("fetch_status")).lower() != "success":
        return SourceFreshnessResult(
            source_id=source_id,
            candidate_id=_text(source.get("candidate_id")),
            update_frequency=frequency,
            latest_fetched_at=_text(latest.get("fetched_at")),
            freshness_status="SOURCE_FETCH_FAILED_SAFE",
            next_safe_action="run_v4_57_explicit_public_fetch_local_cache_only",
            blocked_reasons=(),
            warnings=(),
        )
    fetched_at = parse_date_or_datetime(latest.get("fetched_at"))
    age_days = (current_date - fetched_at).days if fetched_at is not None else 999999
    limit = 1 if frequency == "daily" else 7
    if age_days <= limit:
        status = "SOURCE_FRESH_SAFE"
        action = "no_action_required_for_fresh_sources"
    else:
        status = "SOURCE_STALE_SAFE"
        action = "run_v4_57_explicit_public_fetch_local_cache_only"
    return SourceFreshnessResult(
        source_id=source_id,
        candidate_id=_text(source.get("candidate_id")),
        update_frequency=frequency,
        latest_fetched_at=_text(latest.get("fetched_at")),
        freshness_status=status,
        next_safe_action=action,
        blocked_reasons=(),
        warnings=(),
    )


def evaluate_public_data_freshness(config: dict[str, Any]) -> PublicDataFreshnessMonitorResult:
    config_blocked = list(validate_monitor_config(config))
    current_date = parse_date_or_datetime(config.get("current_date")) or date(1970, 1, 1)
    sources = [source for source in config.get("sources", []) if isinstance(source, dict)] if isinstance(config.get("sources"), list) else []
    cache_entries = [entry for entry in config.get("local_cache_index", []) if isinstance(entry, dict)] if isinstance(config.get("local_cache_index"), list) else []
    source_results = tuple(sorted((evaluate_source_freshness(source, cache_entries, current_date) for source in sources), key=lambda item: item.source_id))
    blocked = config_blocked + [f"{result.source_id}: {reason}" for result in source_results for reason in result.blocked_reasons]
    warnings = [warning for result in source_results for warning in result.warnings]
    fresh_count = sum(result.freshness_status == "SOURCE_FRESH_SAFE" for result in source_results)
    stale_count = sum(result.freshness_status == "SOURCE_STALE_SAFE" for result in source_results)
    missing_count = sum(result.freshness_status == "SOURCE_MISSING_SAFE" for result in source_results)
    manual_count = sum(result.freshness_status == "SOURCE_MANUAL_POLICY_SAFE" for result in source_results)
    failed_count = sum(result.freshness_status == "SOURCE_FETCH_FAILED_SAFE" for result in source_results)

    if blocked:
        status = "PUBLIC_DATA_FRESHNESS_MONITOR_BLOCKED_SAFE"
    elif not source_results:
        status = "PUBLIC_DATA_FRESHNESS_MONITOR_PARTIAL_SAFE"
        warnings.append("no sources configured for freshness monitoring.")
    elif stale_count or missing_count or failed_count:
        status = "PUBLIC_DATA_FRESHNESS_MONITOR_STALE_OR_MISSING_SAFE"
    else:
        status = "PUBLIC_DATA_FRESHNESS_MONITOR_ALL_FRESH_SAFE"

    return PublicDataFreshnessMonitorResult(
        title=_text(config.get("title")) or "J.A.R.V.I.S. Public Data Freshness Monitor",
        version=_text(config.get("version")) or "v4.58",
        overall_status=status,
        monitor_mode=_text(config.get("monitor_mode")),
        report_only=_bool(config.get("report_only")),
        no_network=_bool(config.get("no_network")),
        execute_fetch=_bool(config.get("execute_fetch")),
        current_date=_text(config.get("current_date")),
        source_count=len(source_results),
        cache_entry_count=len(cache_entries),
        fresh_count=fresh_count,
        stale_count=stale_count,
        missing_count=missing_count,
        manual_policy_count=manual_count,
        failed_count=failed_count,
        source_results=source_results,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def render_freshness_summary(result: PublicDataFreshnessMonitorResult) -> str:
    return (
        f"status={result.overall_status}; fresh={result.fresh_count}; stale={result.stale_count}; "
        f"missing={result.missing_count}; manual={result.manual_policy_count}; failed={result.failed_count}"
    )


def load_public_data_freshness_monitor_result(path: str | Path) -> PublicDataFreshnessMonitorResult:
    return evaluate_public_data_freshness(load_json(path))
