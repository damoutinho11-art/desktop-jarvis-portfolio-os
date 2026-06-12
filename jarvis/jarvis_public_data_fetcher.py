"""Public data fetcher local cache control plane.

v4.57 introduces a public-source-only fetch boundary. The default path is
dry-run/no-network/no-write. Real fetching is available only through explicit
authorization and writes raw, unverified bytes into an ignored local cache.
"""

from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse


AUTHORIZATION_PHRASE = "AUTHORIZE_PUBLIC_DATA_FETCH_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE"

ALLOWED_UPDATE_FREQUENCIES = {"daily", "weekly", "manual"}
ALLOWED_SOURCE_TYPES = {
    "official_product_page",
    "official_document",
    "exchange_page",
    "issuer_page",
    "public_market_data_csv",
    "public_market_data_json",
    "public_reference_json",
    "public_reference_csv",
    "other_public_reference",
}
BLOCKED_QUERY_KEYS = {"api_key", "token", "secret", "password", "auth", "credential"}
BROKER_OR_AUTH_HINTS = ("broker", "trading", "oauth", "login", "account", "session")

UNSAFE_SAFETY_CONTROLS = (
    "registry_mutation",
    "registry_file_written",
    "candidate_registry_write",
    "candidate_intake_file_written",
    "persisted_candidate_packet",
    "executor_created",
    "approved_asset",
    "trusted_asset",
    "investable",
    "evidence_verification_started",
    "promoted_verified_evidence",
    "allocation_recommendation",
    "portfolio_construction",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "broker_api_used",
    "authenticated_api_used",
    "credentials_used",
    "private_file_ingested",
    "private_account_data_ingested",
    "automatic_evidence_extraction",
)


@dataclass(frozen=True)
class PublicDataSourceValidation:
    source_id: str
    source_type: str
    source_url: str
    update_frequency: str
    valid: bool
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class PublicDataUpdatePlanItem:
    source_id: str
    candidate_id: str
    display_name: str
    source_type: str
    source_url: str
    update_frequency: str
    planned_action: str
    raw_unverified_data_only: bool


@dataclass(frozen=True)
class PublicDataFetcherEvaluation:
    title: str
    version: str
    overall_status: str
    fetcher_mode: str
    dry_run_only: bool
    execute_fetch: bool
    write_local_cache: bool
    authorization_phrase_valid: bool
    update_frequency: str
    output_directory: str
    source_count: int
    source_validations: tuple[PublicDataSourceValidation, ...]
    update_plan: tuple[PublicDataUpdatePlanItem, ...]
    fetched_files: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    raw_unverified_data: bool = True
    evidence_verified: bool = False
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
    authenticated_api_used: bool = False
    credentials_used: bool = False
    private_file_ingested: bool = False
    automatic_evidence_extraction: bool = False


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _sources_from_config_or_manifest(config: dict[str, Any], manifest: dict[str, Any] | None) -> list[dict[str, Any]]:
    if manifest is not None:
        sources = manifest.get("sources", [])
    else:
        sources = config.get("sources", [])
    return [source for source in sources if isinstance(source, dict)] if isinstance(sources, list) else []


def _safe_source_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return safe or "public_source"


def _is_under_jarvis_local(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    local_root = (root / "jarvis" / "local").resolve()
    try:
        resolved.relative_to(local_root)
        return True
    except ValueError:
        return False


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_fetcher_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    if _text(config.get("update_frequency")) not in ALLOWED_UPDATE_FREQUENCIES:
        blocked.append("update_frequency must be daily, weekly, or manual.")
    safety = config.get("safety_controls", {})
    if not isinstance(safety, dict):
        blocked.append("safety_controls must be an object.")
        safety = {}
    for field in UNSAFE_SAFETY_CONTROLS:
        if _bool(safety.get(field)) or _bool(config.get(field)):
            blocked.append(f"{field} must be false.")
    return tuple(blocked)


def validate_source(source: dict[str, Any]) -> PublicDataSourceValidation:
    blocked: list[str] = []
    warnings: list[str] = []
    source_id = _text(source.get("source_id")) or "unknown_source"
    source_type = _text(source.get("source_type"))
    source_url = _text(source.get("source_url"))
    update_frequency = _text(source.get("update_frequency"))

    if not source_id or source_id == "unknown_source":
        blocked.append("source_id is required.")
    if source_type not in ALLOWED_SOURCE_TYPES:
        blocked.append("source_type must be an allowed public source type.")
    if update_frequency not in ALLOWED_UPDATE_FREQUENCIES:
        blocked.append("update_frequency must be daily, weekly, or manual.")
    if source.get("public_source_only") is not True:
        blocked.append("public_source_only must be true.")
    for field in ("requires_authentication", "requires_credentials", "broker_or_trading_api", "contains_private_data"):
        if _bool(source.get(field)):
            blocked.append(f"{field} must be false.")

    parsed = urlparse(source_url)
    if parsed.scheme not in {"http", "https"}:
        blocked.append("source_url must be http or https.")
    if parsed.scheme == "file":
        blocked.append("file:// sources are blocked.")
    lowered_url = source_url.lower()
    if "file://" in lowered_url or "\\local\\" in lowered_url or "/local/" in lowered_url or "private" in lowered_url:
        blocked.append("source_url must not reference local/private files.")
    query_keys = {key.lower() for key in parse_qs(parsed.query).keys()}
    for key in sorted(query_keys.intersection(BLOCKED_QUERY_KEYS)):
        blocked.append(f"credential-looking query parameter is blocked: {key}")
    if any(hint in lowered_url for hint in BROKER_OR_AUTH_HINTS):
        blocked.append("broker/authenticated-looking endpoint is blocked.")

    if update_frequency == "weekly":
        warnings.append("weekly update frequency is acceptable for slower metadata.")
    if update_frequency == "daily":
        warnings.append("daily update frequency is preferred for freshness.")

    return PublicDataSourceValidation(
        source_id=source_id,
        source_type=source_type,
        source_url=source_url,
        update_frequency=update_frequency,
        valid=not blocked,
        blocked_reasons=tuple(blocked),
        warnings=tuple(warnings),
    )


def validate_source_manifest(manifest: dict[str, Any]) -> tuple[PublicDataSourceValidation, ...]:
    return tuple(validate_source(source) for source in _sources_from_config_or_manifest({}, manifest))


def build_update_plan(config: dict[str, Any], manifest: dict[str, Any] | None = None) -> tuple[PublicDataUpdatePlanItem, ...]:
    sources = _sources_from_config_or_manifest(config, manifest)
    items = [
        PublicDataUpdatePlanItem(
            source_id=_text(source.get("source_id")) or "unknown_source",
            candidate_id=_text(source.get("candidate_id")),
            display_name=_text(source.get("display_name")),
            source_type=_text(source.get("source_type")),
            source_url=_text(source.get("source_url")),
            update_frequency=_text(source.get("update_frequency")),
            planned_action="dry_run_preview_public_fetch_to_local_cache",
            raw_unverified_data_only=True,
        )
        for source in sources
    ]
    return tuple(sorted(items, key=lambda item: item.source_id))


def evaluate_public_data_fetcher(
    config: dict[str, Any], manifest: dict[str, Any] | None = None, fetched_files: tuple[str, ...] = ()
) -> PublicDataFetcherEvaluation:
    config_blocked = list(validate_fetcher_config(config))
    validations = tuple(sorted((validate_source(source) for source in _sources_from_config_or_manifest(config, manifest)), key=lambda item: item.source_id))
    source_blocked = [f"{item.source_id}: {reason}" for item in validations for reason in item.blocked_reasons]
    warnings = [warning for item in validations for warning in item.warnings]
    dry_run_only = _bool(config.get("dry_run_only"))
    execute_fetch = _bool(config.get("execute_fetch"))
    write_local_cache = _bool(config.get("write_local_cache"))
    authorization_phrase_valid = _text(config.get("authorization_phrase")) == AUTHORIZATION_PHRASE

    blocked = config_blocked + source_blocked
    if execute_fetch and (dry_run_only or not write_local_cache or not authorization_phrase_valid):
        status = "PUBLIC_DATA_FETCHER_FETCH_READY_REQUIRES_EXPLICIT_AUTH_SAFE"
    elif fetched_files:
        status = "PUBLIC_DATA_FETCHER_FETCH_COMPLETED_LOCAL_CACHE_ONLY_SAFE"
    elif blocked:
        status = "PUBLIC_DATA_FETCHER_BLOCKED_SAFE"
    elif validations:
        status = "PUBLIC_DATA_FETCHER_PLAN_READY_SAFE"
    else:
        status = "PUBLIC_DATA_FETCHER_PARTIAL_SAFE"
        warnings.append("no public sources are configured.")

    return PublicDataFetcherEvaluation(
        title=_text(config.get("title")) or "J.A.R.V.I.S. Public Data Fetcher",
        version=_text(config.get("version")) or "v4.57",
        overall_status=status,
        fetcher_mode=_text(config.get("fetcher_mode")),
        dry_run_only=dry_run_only,
        execute_fetch=execute_fetch,
        write_local_cache=write_local_cache,
        authorization_phrase_valid=authorization_phrase_valid,
        update_frequency=_text(config.get("update_frequency")),
        output_directory=_text(config.get("output_directory")),
        source_count=len(validations),
        source_validations=validations,
        update_plan=build_update_plan(config, manifest),
        fetched_files=fetched_files,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
    )


def _default_fetch(url: str) -> bytes:
    with urllib.request.urlopen(url, timeout=30) as response:  # nosec - guarded public-only fetch path
        return response.read()


def fetch_public_sources(
    config: dict[str, Any],
    manifest: dict[str, Any],
    fetch_func: Callable[[str], bytes] | None = None,
    root: str | Path = ".",
) -> PublicDataFetcherEvaluation:
    root_path = Path(root)
    output_directory = root_path / _text(config.get("output_directory"))
    prelim = evaluate_public_data_fetcher(config, manifest)
    blocked = list(prelim.blocked_reasons)

    if not _bool(config.get("execute_fetch")):
        blocked.append("execute_fetch must be true for real fetch.")
    if _bool(config.get("dry_run_only")):
        blocked.append("dry_run_only must be false for real fetch.")
    if not _bool(config.get("write_local_cache")):
        blocked.append("write_local_cache must be true for real fetch.")
    if _text(config.get("authorization_phrase")) != AUTHORIZATION_PHRASE:
        blocked.append("exact authorization phrase is required for real fetch.")
    if not _is_under_jarvis_local(output_directory, root_path):
        blocked.append("output_directory must be under ignored jarvis/local.")
    if blocked:
        adjusted = dict(config)
        adjusted["execute_fetch"] = True
        result = evaluate_public_data_fetcher(adjusted, manifest)
        return PublicDataFetcherEvaluation(**{**result.__dict__, "blocked_reasons": tuple(dict.fromkeys(blocked))})

    fetch = fetch_func or _default_fetch
    output_directory.mkdir(parents=True, exist_ok=True)
    fetch_date = _text(config.get("fetch_date")) or "1970-01-01"
    fetched_files: list[str] = []
    sources = sorted(_sources_from_config_or_manifest(config, manifest), key=lambda source: _text(source.get("source_id")))
    for source in sources:
        source_id = _safe_source_id(_text(source.get("source_id")))
        suffix = ".raw"
        expected = _text(source.get("expected_content_type")).lower()
        if "json" in expected:
            suffix = ".json.raw"
        elif "csv" in expected:
            suffix = ".csv.raw"
        path = output_directory / f"{fetch_date}_{source_id}{suffix}"
        path.write_bytes(fetch(_text(source.get("source_url"))))
        fetched_files.append(str(path))

    return evaluate_public_data_fetcher(config, manifest, tuple(fetched_files))
