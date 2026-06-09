"""Source identity guard for FTAW fact intake.

Core law: Do not trust facts unless they belong to the exact asset.

The guard is read-only. Passing identity does not verify evidence, approve an
asset, mutate registries, recommend allocations, create orders, or trade.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from .asset_registry import load_asset_registry
from .ftaw_public_source_research_pack import PUBLIC_RESEARCH_EVIDENCE_TYPES
from .ftaw_source_fact_intake import (
    MANUAL_EVIDENCE_TYPES,
    TARGET_ASSET_ID,
    FTAWSourceFactIntakeConfig,
    FTAWSourceFactRecord,
    load_ftaw_source_fact_intake_config,
)


IDENTITY_FIELDS = (
    "name",
    "ticker",
    "isin_or_symbol",
    "provider",
    "index_tracked",
)
EXPECTED_FIELD_BY_FACT = {
    "name": "expected_name",
    "ticker": "expected_ticker",
    "isin_or_symbol": "expected_isin_or_symbol",
    "provider": "expected_provider",
    "index_tracked": "expected_index_tracked",
}


@dataclass(frozen=True)
class FTAWSourceIdentityGuardConfig:
    asset_id: str
    expected_name: str | None
    expected_ticker: str | None
    expected_isin_or_symbol: str | None
    expected_provider: str | None
    expected_index_tracked: str | None
    allowed_source_names: tuple[str, ...]
    allowed_url_domains: tuple[str, ...]


@dataclass(frozen=True)
class FTAWSourceIdentityGuardResult:
    asset_id: str
    identity_guard_status: str
    checked_fields: tuple[str, ...]
    matched_fields: tuple[str, ...]
    missing_identity_fields: tuple[str, ...]
    placeholder_identity_fields: tuple[str, ...]
    mismatched_fields: tuple[str, ...]
    skipped_evidence_types: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    identity_guard_passed: bool
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    return value


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text when provided.")
    return value.strip()


def _text_tuple(value: Any, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list.")
    result = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field} must contain non-empty text.")
        result.append(item.strip())
    return tuple(result)


def load_ftaw_source_identity_guard_config(path: str | Path) -> FTAWSourceIdentityGuardConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "FTAW source identity guard config")
    asset_id = _optional_text(raw.get("asset_id", TARGET_ASSET_ID), "asset_id") or TARGET_ASSET_ID
    return FTAWSourceIdentityGuardConfig(
        asset_id=asset_id,
        expected_name=_optional_text(raw.get("expected_name"), "expected_name"),
        expected_ticker=_optional_text(raw.get("expected_ticker"), "expected_ticker"),
        expected_isin_or_symbol=_optional_text(raw.get("expected_isin_or_symbol"), "expected_isin_or_symbol"),
        expected_provider=_optional_text(raw.get("expected_provider"), "expected_provider"),
        expected_index_tracked=_optional_text(raw.get("expected_index_tracked"), "expected_index_tracked"),
        allowed_source_names=_text_tuple(raw.get("allowed_source_names", []), "allowed_source_names"),
        allowed_url_domains=_text_tuple(raw.get("allowed_url_domains", []), "allowed_url_domains"),
    )


def _is_placeholder(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        return not stripped or stripped.startswith("<") or stripped.endswith("_to_capture>")
    return False


def _norm(value: object) -> str:
    return " ".join(str(value).strip().lower().split())


def _domain(url_reference: str) -> str:
    parsed = urlparse(url_reference)
    return parsed.netloc.lower()


def _target_records(config: FTAWSourceFactIntakeConfig) -> tuple[FTAWSourceFactRecord, ...]:
    return tuple(record for record in config.records if record.asset_id == TARGET_ASSET_ID)


def build_ftaw_source_identity_guard(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    fact_intake: FTAWSourceFactIntakeConfig,
    guard_config: FTAWSourceIdentityGuardConfig,
) -> FTAWSourceIdentityGuardResult:
    registry = load_asset_registry(source_registry_path)
    if TARGET_ASSET_ID not in registry.by_id():
        raise ValueError(f"{TARGET_ASSET_ID} not found in registry.")
    if reviewed_registry_copy_path is not None and str(reviewed_registry_copy_path).lower() not in {"", "none", "null", "-"}:
        Path(reviewed_registry_copy_path).read_text(encoding="utf-8")

    blockers: list[str] = []
    warnings: list[str] = []
    checked: list[str] = []
    matched: list[str] = []
    missing: list[str] = []
    placeholders: list[str] = []
    mismatched: list[str] = []
    skipped: set[str] = set()

    if guard_config.asset_id != TARGET_ASSET_ID:
        blockers.append(f"asset_id mismatch: expected guard target {TARGET_ASSET_ID}, got {guard_config.asset_id}.")

    expected_by_fact = {
        "name": guard_config.expected_name,
        "ticker": guard_config.expected_ticker,
        "isin_or_symbol": guard_config.expected_isin_or_symbol,
        "provider": guard_config.expected_provider,
        "index_tracked": guard_config.expected_index_tracked,
    }
    for fact_key, expected in expected_by_fact.items():
        expected_field = EXPECTED_FIELD_BY_FACT[fact_key]
        if expected is None:
            missing.append(expected_field)
        elif _is_placeholder(expected):
            placeholders.append(expected_field)

    if not guard_config.allowed_source_names:
        missing.append("allowed_source_names")
    if any(_is_placeholder(name) for name in guard_config.allowed_source_names):
        placeholders.append("allowed_source_names")
    if any(_is_placeholder(domain) for domain in guard_config.allowed_url_domains):
        placeholders.append("allowed_url_domains")

    records = _target_records(fact_intake)
    fund_records = [record for record in records if record.evidence_type == "fund_metadata"]
    for record in records:
        if record.evidence_type in MANUAL_EVIDENCE_TYPES:
            skipped.add(record.evidence_type)
        elif record.evidence_type not in PUBLIC_RESEARCH_EVIDENCE_TYPES:
            skipped.add(record.evidence_type)

    if not fund_records:
        missing.append("fund_metadata")
    for record in fund_records:
        usable_source_names = tuple(name for name in guard_config.allowed_source_names if not _is_placeholder(name))
        usable_domains = tuple(domain for domain in guard_config.allowed_url_domains if not _is_placeholder(domain))
        if usable_source_names and record.source_name not in usable_source_names:
            mismatched.append("source_name")
            blockers.append(f"source_name mismatch: {record.source_name} is not allowed.")
        if usable_domains:
            domain = _domain(record.url_reference)
            if domain not in usable_domains:
                mismatched.append("url_domain")
                blockers.append(f"URL domain mismatch: {domain or '<missing>'} is not allowed.")
        for fact_key in IDENTITY_FIELDS:
            checked.append(fact_key)
            expected = expected_by_fact[fact_key]
            actual = record.extracted_facts.get(fact_key)
            if _is_placeholder(actual):
                placeholders.append(fact_key)
                continue
            if expected is None or _is_placeholder(expected):
                continue
            if _norm(actual) == _norm(expected):
                matched.append(fact_key)
            else:
                mismatched.append(fact_key)
                blockers.append(f"{fact_key} mismatch: expected {expected}, got {actual}.")

    unique_missing = tuple(sorted(dict.fromkeys(missing)))
    unique_placeholders = tuple(sorted(dict.fromkeys(placeholders)))
    unique_mismatched = tuple(sorted(dict.fromkeys(mismatched)))
    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_checked = tuple(sorted(dict.fromkeys(checked)))
    unique_matched = tuple(sorted(dict.fromkeys(matched)))
    if unique_blockers:
        status = "BLOCKED"
    elif unique_missing or unique_placeholders or set(unique_matched) != set(IDENTITY_FIELDS):
        status = "needs_identity_confirmation"
    else:
        status = "identity_guard_passed"
    return FTAWSourceIdentityGuardResult(
        asset_id=TARGET_ASSET_ID,
        identity_guard_status=status,
        checked_fields=unique_checked,
        matched_fields=unique_matched,
        missing_identity_fields=unique_missing,
        placeholder_identity_fields=unique_placeholders,
        mismatched_fields=unique_mismatched,
        skipped_evidence_types=tuple(sorted(skipped)),
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        identity_guard_passed=status == "identity_guard_passed",
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_source_identity_guard_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    fact_intake_config_path: str | Path,
    guard_config_path: str | Path,
) -> FTAWSourceIdentityGuardResult:
    return build_ftaw_source_identity_guard(
        source_registry_path,
        reviewed_registry_copy_path,
        load_ftaw_source_fact_intake_config(fact_intake_config_path),
        load_ftaw_source_identity_guard_config(guard_config_path),
    )
