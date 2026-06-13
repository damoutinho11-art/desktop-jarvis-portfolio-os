"""Public asset universe normalizer.

v4.66 structurally normalizes safe audited public cache records. It is not
classification, screening, evidence extraction, evidence verification, approval,
allocation, trading, registry mutation, or execution.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_PUBLIC_ASSET_UNIVERSE_NORMALIZE_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE"
ALLOWED_CACHE_ROOT = Path("jarvis/local/public_asset_universe")
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/public_asset_universe/normalized")
SAFE_CACHE_AUDIT_STATUSES = {
    "PUBLIC_ASSET_UNIVERSE_CACHE_AUDIT_READY_SAFE",
    "CACHE_INTEGRITY_OK_SAFE",
    "CACHE_FRESH_SAFE",
    "CACHE_MANUAL_REVIEW_REQUIRED_SAFE",
}
ALLOWED_FRESHNESS = {"CACHE_FRESH_SAFE", "CACHE_MANUAL_REVIEW_REQUIRED_SAFE"}
ALLOWED_ASSET_TYPES = {"ETF", "EQUITY", "FUND_OR_ETP", "CRYPTO_ASSET", "MARKET_REFERENCE", "UNKNOWN_PUBLIC_ASSET"}
VALID_NEXT_MANUAL_ACTIONS = {
    "review_normalized_public_asset_universe",
    "proceed_to_public_asset_universe_classifier",
    "fix_raw_cache_or_metadata",
    "rerun_cache_audit",
    "no_manual_asset_entry_required",
}
BLOCKED_NEXT_MANUAL_ACTIONS = {
    "classify_now",
    "screen_now",
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
    "writes_without_explicit_authorization",
    "cache_mutation_without_explicit_authorization",
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
    "classification",
    "screening",
    "research_scoring",
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
    "normalized_data_unverified",
    "normalization_only",
)
UNSAFE_FIELDS = (
    "evidence_verified",
    "approved_asset",
    "trusted_asset",
    "investable",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "registry_mutation",
    "executor_created",
)


@dataclass(frozen=True)
class PublicAssetUniverseNormalizerResult:
    title: str
    version: str
    status: str
    normalizer_mode: str
    source_count: int
    raw_record_count: int
    normalized_record_count: int
    skipped_input_count: int
    blocked_input_count: int
    invalid_record_count: int
    duplicate_asset_id_count: int
    normalized_records: tuple[dict[str, Any], ...]
    skipped_inputs: tuple[str, ...]
    blocked_inputs: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    next_safe_action: str
    no_network_called: bool = True
    no_fetch_executed: bool = True
    no_cache_mutated: bool = True
    no_evidence_verification: bool = True
    no_classification: bool = True
    no_screening: bool = True
    no_approval: bool = True
    no_allocation: bool = True
    no_trade: bool = True
    no_executor: bool = True
    local_cache_only: bool = True
    normalized_data_unverified: bool = True


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
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        try:
            return date.fromisoformat(text)
        except ValueError:
            return None


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalize_string(value: Any) -> str:
    return re.sub(r"\s+", " ", _text(value)).strip()


def normalize_symbol(value: Any) -> str:
    return normalize_string(value).upper().replace(" ", "")


def normalize_asset_type(value: Any) -> str:
    text = normalize_string(value).upper().replace("-", "_").replace(" ", "_")
    aliases = {
        "ETF": "ETF",
        "EXCHANGE_TRADED_FUND": "ETF",
        "EQUITY": "EQUITY",
        "STOCK": "EQUITY",
        "SHARE": "EQUITY",
        "FUND": "FUND_OR_ETP",
        "ETP": "FUND_OR_ETP",
        "FUND_OR_ETP": "FUND_OR_ETP",
        "CRYPTO": "CRYPTO_ASSET",
        "CRYPTO_ASSET": "CRYPTO_ASSET",
        "MARKET": "MARKET_REFERENCE",
        "MARKET_REFERENCE": "MARKET_REFERENCE",
    }
    return aliases.get(text, "UNKNOWN_PUBLIC_ASSET")


def normalize_currency(value: Any) -> str:
    text = normalize_symbol(value)
    return text if len(text) == 3 and text.isalpha() else "UNKNOWN"


def normalize_region(value: Any) -> str:
    text = normalize_string(value)
    return text if text else "UNKNOWN"


def build_asset_id(record: dict[str, Any]) -> str:
    asset_type = normalize_asset_type(record.get("asset_type"))
    symbol = normalize_symbol(record.get("symbol_or_identifier") or record.get("symbol") or record.get("ticker"))
    venue = normalize_symbol(record.get("exchange_or_venue") or record.get("exchange") or record.get("market_or_region"))
    raw = "_".join(part for part in (asset_type, symbol or "UNKNOWN", venue or "PUBLIC") if part)
    return re.sub(r"[^A-Z0-9_]+", "_", raw).strip("_").lower()


def _path_blockers(path: str | Path, root: str | Path) -> tuple[str, ...]:
    text = _text(path)
    if not text:
        return ("path is required.",)
    normalized = text.replace("\\", "/")
    if normalized.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("path must not target docs, templates, or jarvis/data.",)
    root_path = Path(root).resolve()
    candidate = Path(path).resolve()
    try:
        candidate.relative_to(root_path)
    except ValueError:
        return ("path must stay under the configured root.",)
    return ()


def _authorization_valid(config: dict[str, Any]) -> bool:
    policy = config.get("authorization_policy", {})
    if not isinstance(policy, dict):
        return False
    return (
        policy.get("explicit_authorization_required") is True
        and policy.get("required_authorization_phrase") == REQUIRED_AUTHORIZATION_PHRASE
        and policy.get("authorization_phrase") == REQUIRED_AUTHORIZATION_PHRASE
        and policy.get("authorization_phrase_valid") is True
        and policy.get("default_write_allowed") is False
        and policy.get("write_allowed_only_with_explicit_authorization") is True
    )


def validate_normalizer_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in (
        "report_only",
        "default_no_write",
        "read_only_by_default",
        "local_cache_only",
        "no_network",
        "no_fetching",
        "no_downloading",
        "no_scraping",
        "no_api_calls",
        "no_browser_automation",
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
    action = _text(config.get("next_manual_action"))
    if action not in VALID_NEXT_MANUAL_ACTIONS:
        blocked.append("next_manual_action must be valid.")
    if action in BLOCKED_NEXT_MANUAL_ACTIONS:
        blocked.append(f"next_manual_action must not be {action}.")
    policy = config.get("authorization_policy", {})
    if not isinstance(policy, dict):
        blocked.append("authorization_policy must be an object.")
    else:
        expected = {
            "explicit_authorization_required": True,
            "default_write_allowed": False,
            "write_allowed_only_with_explicit_authorization": True,
            "local_cache_only": True,
            "normalized_data_unverified": True,
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
            blocked.append("authorization_policy.required_authorization_phrase must match.")
    if not isinstance(config.get("raw_inputs", []), list):
        blocked.append("raw_inputs must be a list.")
    return tuple(dict.fromkeys(blocked))


def validate_raw_input(raw_input: dict[str, Any], cache_root: str | Path | None = None) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in ("source_id", "source_name", "source_category_id", "cache_audit_status", "integrity_status", "freshness_status", "input_mode", "parser_hint", "expected_asset_type"):
        if not _text(raw_input.get(field)):
            blocked.append(f"{field} is required.")
    if raw_input.get("integrity_status") != "CACHE_INTEGRITY_OK_SAFE":
        blocked.append("integrity_status must be CACHE_INTEGRITY_OK_SAFE.")
    if raw_input.get("freshness_status") not in ALLOWED_FRESHNESS:
        blocked.append("freshness_status must be fresh or manual-review safe.")
    if raw_input.get("cache_audit_status") not in SAFE_CACHE_AUDIT_STATUSES:
        blocked.append("cache_audit_status must be safe.")
    if raw_input.get("raw_unverified") is not True:
        blocked.append("raw_unverified must be true.")
    for field in UNSAFE_FIELDS:
        if raw_input.get(field) is True:
            blocked.append(f"{field} must be false.")
    if raw_input.get("portfolio_weight") not in {None, False, 0, 0.0}:
        blocked.append("portfolio_weight must be false or zero.")
    if raw_input.get("input_mode") == "file_backed":
        root = cache_root or "jarvis\\local\\public_asset_universe\\"
        blocked.extend(f"raw_cache_path: {reason}" for reason in _path_blockers(raw_input.get("raw_cache_path", ""), root))
        blocked.extend(f"metadata_path: {reason}" for reason in _path_blockers(raw_input.get("metadata_path", ""), root))
    elif raw_input.get("input_mode") == "inline":
        if not isinstance(raw_input.get("raw_records_inline"), list):
            blocked.append("raw_records_inline must be a list for inline input.")
    else:
        blocked.append("input_mode must be inline or file_backed.")
    return tuple(dict.fromkeys(blocked))


def _load_raw_records(raw_input: dict[str, Any], cache_root: str | Path | None) -> list[dict[str, Any]]:
    if raw_input.get("input_mode") == "inline":
        return [record for record in raw_input.get("raw_records_inline", []) if isinstance(record, dict)]
    root = cache_root or "jarvis\\local\\public_asset_universe\\"
    if _path_blockers(raw_input.get("raw_cache_path", ""), root) or _path_blockers(raw_input.get("metadata_path", ""), root):
        return []
    raw_path = Path(raw_input["raw_cache_path"])
    text = raw_path.read_text(encoding="utf-8")
    if raw_path.suffix.lower() == ".json":
        data = json.loads(text)
        if isinstance(data, list):
            return [record for record in data if isinstance(record, dict)]
        if isinstance(data, dict):
            records = data.get("records", [data])
            return [record for record in records if isinstance(record, dict)]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return []
    headers = [part.strip() for part in lines[0].split(",")]
    return [dict(zip(headers, [part.strip() for part in line.split(",")])) for line in lines[1:]]


def normalize_raw_record(raw_record: dict[str, Any], source_context: dict[str, Any], current_date: Any) -> dict[str, Any]:
    asset_type = normalize_asset_type(raw_record.get("asset_type") or source_context.get("expected_asset_type"))
    symbol = normalize_symbol(raw_record.get("symbol_or_identifier") or raw_record.get("symbol") or raw_record.get("ticker") or raw_record.get("identifier"))
    display_name = normalize_string(raw_record.get("display_name") or raw_record.get("name") or symbol or "UNKNOWN")
    exchange = normalize_string(raw_record.get("exchange_or_venue") or raw_record.get("exchange") or raw_record.get("venue"))
    region = normalize_region(raw_record.get("market_or_region") or raw_record.get("region") or raw_record.get("market"))
    normalized_at = _text(current_date)
    base = {
        "asset_type": asset_type,
        "symbol_or_identifier": symbol,
        "exchange_or_venue": exchange,
        "market_or_region": region,
    }
    asset_id = normalize_string(raw_record.get("asset_id")) or build_asset_id({**raw_record, **base})
    return {
        "asset_id": asset_id,
        "display_name": display_name,
        "asset_type": asset_type,
        "symbol_or_identifier": symbol,
        "issuer_or_provider": normalize_string(raw_record.get("issuer_or_provider") or raw_record.get("issuer") or raw_record.get("provider")),
        "exchange_or_venue": exchange,
        "market_or_region": region,
        "currency": normalize_currency(raw_record.get("currency")),
        "isin_or_figi_or_other_public_identifier": normalize_string(raw_record.get("isin_or_figi_or_other_public_identifier") or raw_record.get("isin") or raw_record.get("figi") or raw_record.get("identifier")),
        "source_id": _text(source_context.get("source_id")),
        "source_category_id": _text(source_context.get("source_category_id")),
        "source_reference_ids": tuple(sorted(set(_list(raw_record.get("source_reference_ids")) + (_text(source_context.get("source_id")),)))),
        "discovery_source": normalize_string(source_context.get("source_name")),
        "discovered_at": _text(raw_record.get("discovered_at") or source_context.get("fetched_at") or current_date),
        "last_refreshed_at": _text(raw_record.get("last_refreshed_at") or source_context.get("fetched_at") or current_date),
        "normalized_at": normalized_at,
        "data_freshness_status": _text(source_context.get("freshness_status")),
        "raw_unverified": True,
        "normalized_public_data_only": True,
        "evidence_status": "UNVERIFIED_PUBLIC_DATA",
        "approval_status": "NOT_APPROVED",
        "investability_status": "NOT_INVESTABLE",
        "execution_status": "NO_EXECUTION",
        "classification_status": "NOT_CLASSIFIED",
        "screening_status": "NOT_SCREENED",
        "evidence_pack_status": "NOT_GENERATED",
        "manual_review_required": True,
        "manual_approval_required": True,
        "safety_notes": tuple(sorted(set(_list(source_context.get("safety_notes")) + ("Normalized public data remains unverified and unapproved.",)))),
    }


def validate_normalized_record(record: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    required = (
        "asset_id",
        "display_name",
        "asset_type",
        "symbol_or_identifier",
        "source_id",
        "source_category_id",
        "evidence_status",
        "approval_status",
        "investability_status",
        "execution_status",
        "classification_status",
        "screening_status",
        "evidence_pack_status",
    )
    for field in required:
        if not _text(record.get(field)):
            blocked.append(f"{field} is required.")
    if record.get("asset_type") not in ALLOWED_ASSET_TYPES:
        blocked.append("asset_type is not allowed.")
    expected = {
        "evidence_status": "UNVERIFIED_PUBLIC_DATA",
        "approval_status": "NOT_APPROVED",
        "investability_status": "NOT_INVESTABLE",
        "execution_status": "NO_EXECUTION",
        "classification_status": "NOT_CLASSIFIED",
        "screening_status": "NOT_SCREENED",
        "evidence_pack_status": "NOT_GENERATED",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            blocked.append(f"{field} must be {value}.")
    for field in ("raw_unverified", "normalized_public_data_only", "manual_review_required", "manual_approval_required"):
        if record.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in ("approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "candidate_registry_write", "executor_created"):
        if record.get(field) is True:
            blocked.append(f"{field} must not be true.")
    if record.get("portfolio_weight") not in {None, False, 0, 0.0}:
        blocked.append("portfolio_weight must not be nonzero.")
    return tuple(blocked)


def normalize_raw_inputs(config: dict[str, Any]) -> tuple[tuple[dict[str, Any], ...], tuple[str, ...], tuple[str, ...]]:
    records: list[dict[str, Any]] = []
    skipped: list[str] = []
    blocked: list[str] = []
    cache_root = config.get("cache_root") or "jarvis\\local\\public_asset_universe\\"
    for raw_input in config.get("raw_inputs", []):
        if not isinstance(raw_input, dict):
            blocked.append("raw input must be an object")
            continue
        reasons = validate_raw_input(raw_input, cache_root)
        if reasons:
            if raw_input.get("integrity_status") != "CACHE_INTEGRITY_OK_SAFE" or raw_input.get("freshness_status") not in ALLOWED_FRESHNESS:
                skipped.append(_text(raw_input.get("source_id")) or "unknown")
            else:
                blocked.append(f"{_text(raw_input.get('source_id'))}: {'; '.join(reasons)}")
            continue
        for raw_record in _load_raw_records(raw_input, cache_root):
            records.append(normalize_raw_record(raw_record, raw_input, config.get("current_date")))
    return tuple(records), tuple(skipped), tuple(blocked)


def evaluate_public_asset_universe_normalizer(config: dict[str, Any]) -> PublicAssetUniverseNormalizerResult:
    config_blockers = list(validate_normalizer_config(config))
    normalized_records, skipped_inputs, blocked_inputs = normalize_raw_inputs(config)
    record_blockers = [f"{record.get('asset_id')}: {reason}" for record in normalized_records for reason in validate_normalized_record(record)]
    ids = [record["asset_id"] for record in normalized_records if "asset_id" in record]
    duplicate_count = len(ids) - len(set(ids))
    if duplicate_count:
        record_blockers.append("duplicate asset_id detected.")
    blockers = tuple(dict.fromkeys(config_blockers + list(blocked_inputs) + record_blockers))
    authorized = _authorization_valid(config)
    if blockers:
        status = "PUBLIC_ASSET_UNIVERSE_NORMALIZER_BLOCKED_SAFE"
    elif skipped_inputs:
        status = "PUBLIC_ASSET_UNIVERSE_NORMALIZER_PARTIAL_SAFE"
    elif authorized:
        status = "PUBLIC_ASSET_UNIVERSE_NORMALIZER_READY_TO_WRITE_SAFE"
    else:
        status = "PUBLIC_ASSET_UNIVERSE_NORMALIZER_READY_SAFE"
    return PublicAssetUniverseNormalizerResult(
        title=_text(config.get("title")) or "J.A.R.V.I.S. Public Asset Universe Normalizer",
        version=_text(config.get("version")) or "v4.66",
        status=status,
        normalizer_mode=_text(config.get("normalizer_mode")),
        source_count=len(config.get("raw_inputs", [])) if isinstance(config.get("raw_inputs"), list) else 0,
        raw_record_count=sum(len(item.get("raw_records_inline", [])) for item in config.get("raw_inputs", []) if isinstance(item, dict) and isinstance(item.get("raw_records_inline"), list)),
        normalized_record_count=len(normalized_records),
        skipped_input_count=len(skipped_inputs),
        blocked_input_count=len(blocked_inputs),
        invalid_record_count=len(record_blockers),
        duplicate_asset_id_count=duplicate_count,
        normalized_records=tuple(sorted(normalized_records, key=lambda record: record["asset_id"])),
        skipped_inputs=skipped_inputs,
        blocked_inputs=tuple(blocked_inputs),
        warnings=(),
        blockers=blockers,
        next_safe_action=_text(config.get("next_manual_action")),
    )


def _output_root_blockers(path: str | Path) -> tuple[str, ...]:
    text = _text(path)
    if not text:
        return ("normalized output root is required.",)
    normalized = text.replace("\\", "/").rstrip("/")
    blocked_roots = {"docs", "templates", "jarvis/data", "."}
    if normalized in blocked_roots or normalized.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("normalized output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def execute_authorized_normalized_cache_write(
    config: dict[str, Any],
    normalized_records: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "PUBLIC_ASSET_UNIVERSE_NORMALIZER_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None:
        blockers.extend(_path_blockers(output_root, ALLOWED_OUTPUT_ROOT))
    for record in normalized_records:
        blockers.extend(f"{record.get('asset_id', 'unknown')}: {reason}" for reason in validate_normalized_record(record))
    if blockers:
        return {"status": "PUBLIC_ASSET_UNIVERSE_NORMALIZER_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    normalized_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = {
        "normalized_at": normalized_at,
        "normalized_data_unverified": True,
        "records": list(normalized_records),
    }
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digest = sha256_bytes(raw_bytes)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "public_asset_universe.normalized.json"
    metadata_path = output_root / "public_asset_universe.normalized.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "normalized_at": normalized_at,
        "record_count": len(normalized_records),
        "content_sha256": digest,
        "normalized_data_unverified": True,
        "evidence_verified": False,
        "approved_asset": False,
        "trusted_asset": False,
        "investable": False,
        "allocation_recommendation": False,
        "buy_signal": False,
        "sell_signal": False,
        "trade_executed": False,
        "registry_mutation": False,
        "executor_created": False,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "status": "PUBLIC_ASSET_UNIVERSE_NORMALIZER_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_public_asset_universe_normalizer_summary(result: PublicAssetUniverseNormalizerResult) -> str:
    return (
        f"status={result.status}; sources={result.source_count}; raw_records={result.raw_record_count}; "
        f"normalized={result.normalized_record_count}; skipped={result.skipped_input_count}; "
        f"blocked={result.blocked_input_count}; duplicates={result.duplicate_asset_id_count}"
    )


def load_public_asset_universe_normalizer_result(path: str | Path) -> PublicAssetUniverseNormalizerResult:
    return evaluate_public_asset_universe_normalizer(load_json(path))
