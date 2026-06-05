"""Offline-safe public source evidence fetcher for draft evidence records."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .asset_registry import AssetRegistry, CandidateAsset, load_asset_registry


ALLOWED_SOURCE_TYPES = {
    "provider_product_page",
    "provider_factsheet_pdf",
    "provider_kiid_pdf",
    "public_platform_page",
    "public_crypto_market_api",
    "public_fx_api",
    "manual_url_reference",
    "local_source_fixture",
}
FORBIDDEN_SOURCE_TYPES = {
    "authenticated_broker_session",
    "personal_account_page",
    "credentialed_api",
    "trading_api",
}
SOURCE_QUALITY_BY_TYPE = {
    "provider_product_page": "provider_factsheet",
    "provider_factsheet_pdf": "provider_factsheet",
    "provider_kiid_pdf": "provider_factsheet",
    "public_platform_page": "platform_screenshot",
    "public_crypto_market_api": "verified_api_snapshot",
    "public_fx_api": "verified_api_snapshot",
    "manual_url_reference": "manual_research",
    "local_source_fixture": "manual_research",
}
FACT_KEYS = (
    "isin",
    "ticker",
    "fund_name",
    "provider",
    "benchmark",
    "distribution_policy",
    "ter_or_fee",
    "currency",
    "domicile",
    "replication_method",
    "platform_name",
    "availability_status",
)


@dataclass(frozen=True)
class SourceEvidenceConfig:
    source_id: str
    asset_id: str
    evidence_type: str
    source_type: str
    source_name: str
    url_reference: str | None
    local_fixture_path: str | None
    enabled: bool
    notes: str
    static_content: str | None = None


@dataclass(frozen=True)
class SourceEvidenceFetchResult:
    source_id: str
    asset_id: str
    status: str
    draft_evidence_record: dict[str, object] | None
    extracted_facts: dict[str, object]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class SourceEvidenceRunResult:
    results: tuple[SourceEvidenceFetchResult, ...]
    approvals_created: bool = False
    registry_mutation_allowed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")
    return value.strip()


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _require_text(value, field)


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be true or false.")
    return value


def parse_source_config(raw: dict[str, Any]) -> SourceEvidenceConfig:
    item = _require_mapping(raw, "source evidence config")
    return SourceEvidenceConfig(
        source_id=_require_text(item.get("source_id"), "source_id"),
        asset_id=_require_text(item.get("asset_id"), "asset_id"),
        evidence_type=_require_text(item.get("evidence_type"), "evidence_type"),
        source_type=_require_text(item.get("source_type"), "source_type"),
        source_name=_require_text(item.get("source_name"), "source_name"),
        url_reference=_optional_text(item.get("url_reference"), "url_reference"),
        local_fixture_path=_optional_text(item.get("local_fixture_path"), "local_fixture_path"),
        enabled=_require_bool(item.get("enabled"), "enabled"),
        notes=_require_text(item.get("notes"), "notes"),
        static_content=_optional_text(item.get("static_content"), "static_content"),
    )


def load_source_evidence_configs(path: str | Path) -> tuple[SourceEvidenceConfig, ...]:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "source evidence sources")
    sources = raw.get("sources")
    if not isinstance(sources, list):
        raise ValueError("source evidence sources must contain a sources list.")
    return tuple(parse_source_config(source) for source in sources)


def _load_static_or_local_content(config: SourceEvidenceConfig) -> tuple[str, tuple[str, ...]]:
    warnings: list[str] = []
    if config.static_content:
        return config.static_content, tuple(warnings)
    if config.local_fixture_path:
        path = Path(config.local_fixture_path)
        if path.exists():
            return path.read_text(encoding="utf-8"), tuple(warnings)
        warnings.append(f"{config.source_id}: local_fixture_path not found; no content parsed.")
    else:
        warnings.append(f"{config.source_id}: no static_content or local_fixture_path supplied.")
    return "", tuple(warnings)


def extract_simple_facts(content: str) -> tuple[dict[str, object], tuple[str, ...]]:
    facts: dict[str, object] = {}
    warnings: list[str] = []
    for key in FACT_KEYS:
        pattern = re.compile(rf"(?im)^\s*{re.escape(key)}\s*[:=]\s*(.+?)\s*$")
        match = pattern.search(content)
        if match:
            value: object = match.group(1).strip()
            if key == "ter_or_fee":
                try:
                    value = float(str(value).replace("%", "").strip())
                except ValueError:
                    warnings.append("ter_or_fee could not be parsed as a number.")
            facts[key] = value
    for key in ("ticker", "currency", "provider", "platform_name", "availability_status"):
        if key not in facts:
            warnings.append(f"missing extracted fact: {key}.")
    return facts, tuple(warnings)


def _draft_record(config: SourceEvidenceConfig, facts: dict[str, object], warnings: tuple[str, ...]) -> dict[str, object]:
    return {
        "evidence_id": f"draft_{config.source_id}",
        "asset_id": config.asset_id,
        "evidence_type": config.evidence_type,
        "source_quality": SOURCE_QUALITY_BY_TYPE[config.source_type],
        "source_name": config.source_name,
        "as_of": "2026-06-05",
        "verified_by_user": False,
        "verification_notes": "Auto-prepared draft evidence. User verification required.",
        "file_reference": config.local_fixture_path,
        "url_reference": config.url_reference,
        "extracted_facts": facts,
        "warnings": list(warnings),
    }


def fetch_source_evidence(
    config: SourceEvidenceConfig,
    assets_by_id: dict[str, CandidateAsset],
) -> SourceEvidenceFetchResult:
    blockers: list[str] = []
    warnings: list[str] = []
    if config.source_type in FORBIDDEN_SOURCE_TYPES:
        blockers.append(f"{config.source_id}: forbidden source_type {config.source_type}.")
    elif config.source_type not in ALLOWED_SOURCE_TYPES:
        blockers.append(f"{config.source_id}: unsupported source_type {config.source_type}.")
    if config.asset_id not in assets_by_id:
        blockers.append(f"{config.source_id}: unknown asset_id {config.asset_id}.")
    if not config.enabled:
        blockers.append(f"{config.source_id}: source disabled; skipped.")
    if blockers:
        return SourceEvidenceFetchResult(
            source_id=config.source_id,
            asset_id=config.asset_id,
            status="BLOCKED",
            draft_evidence_record=None,
            extracted_facts={},
            warnings=tuple(warnings),
            blockers=tuple(blockers),
        )

    content, content_warnings = _load_static_or_local_content(config)
    warnings.extend(content_warnings)
    facts, fact_warnings = extract_simple_facts(content)
    warnings.extend(fact_warnings)
    draft = _draft_record(config, facts, tuple(warnings))
    status = "WARNING" if warnings else "DRAFT_EVIDENCE_CREATED"
    return SourceEvidenceFetchResult(
        source_id=config.source_id,
        asset_id=config.asset_id,
        status=status,
        draft_evidence_record=draft,
        extracted_facts=facts,
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=(),
    )


def run_source_evidence_fetcher(
    registry_path: str | Path | AssetRegistry,
    sources_path: str | Path,
) -> SourceEvidenceRunResult:
    registry = load_asset_registry(registry_path) if not isinstance(registry_path, AssetRegistry) else registry_path
    assets_by_id = registry.by_id()
    results = tuple(fetch_source_evidence(config, assets_by_id) for config in load_source_evidence_configs(sources_path))
    return SourceEvidenceRunResult(results=results)
