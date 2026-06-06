"""Optional public source fetch adapter for draft evidence records."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .asset_registry import AssetRegistry, CandidateAsset, load_asset_registry


SUPPORTED_PUBLIC_SOURCE_TYPES = {
    "provider_product_page",
    "provider_factsheet_pdf",
    "provider_kiid_pdf",
    "public_platform_page",
    "public_market_data_page",
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
    "public_market_data_page": "manual_research",
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
    "price_currency",
    "market_price",
    "price_source",
    "as_of_market_date",
    "holdings_source",
    "country_exposure_source",
    "sector_exposure_source",
    "tax_route_summary",
    "tax_wrapper",
)
DEFAULT_TIMEOUT_SECONDS = 5
DEFAULT_MAX_BYTES = 200_000
REFERENCE_DATE = "2026-06-05"


@dataclass(frozen=True)
class PublicSourceFetchConfig:
    source_id: str
    asset_id: str
    evidence_type: str
    source_type: str
    source_name: str
    url_reference: str | None
    enabled: bool
    allow_network_fetch: bool
    local_fixture_content: str | None
    notes: str


@dataclass(frozen=True)
class PublicSourceFetchResult:
    source_id: str
    asset_id: str
    status: str
    mode: str
    draft_evidence_record: dict[str, object] | None
    extracted_facts: dict[str, object]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class PublicSourceFetchRunResult:
    results: tuple[PublicSourceFetchResult, ...]
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


def _optional_bool(value: Any, default: bool) -> bool:
    if value is None:
        return default
    if not isinstance(value, bool):
        raise ValueError("allow_network_fetch must be true or false.")
    return value


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{field} must be true or false.")
    return value


def parse_public_source_config(raw: dict[str, Any]) -> PublicSourceFetchConfig:
    item = _require_mapping(raw, "public source fetch config")
    return PublicSourceFetchConfig(
        source_id=_require_text(item.get("source_id"), "source_id"),
        asset_id=_require_text(item.get("asset_id"), "asset_id"),
        evidence_type=_require_text(item.get("evidence_type"), "evidence_type"),
        source_type=_require_text(item.get("source_type"), "source_type"),
        source_name=_require_text(item.get("source_name"), "source_name"),
        url_reference=_optional_text(item.get("url_reference"), "url_reference"),
        enabled=_require_bool(item.get("enabled"), "enabled"),
        allow_network_fetch=_optional_bool(item.get("allow_network_fetch"), False),
        local_fixture_content=_optional_text(item.get("local_fixture_content"), "local_fixture_content"),
        notes=_require_text(item.get("notes"), "notes"),
    )


def load_public_source_configs(path: str | Path) -> tuple[PublicSourceFetchConfig, ...]:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "public source fetch file")
    sources = raw.get("sources")
    if not isinstance(sources, list):
        raise ValueError("public source fetch file must contain a sources list.")
    return tuple(parse_public_source_config(source) for source in sources)


def _default_network_fetch(url: str, timeout_seconds: int, max_bytes: int) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "JARVIS-public-source-fetcher/3.3"})
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return response.read(max_bytes).decode("utf-8", errors="replace")


def _is_public_url(url: str | None) -> bool:
    return bool(url and (url.startswith("https://") or url.startswith("http://")))


def extract_public_source_facts(content: str) -> tuple[dict[str, object], tuple[str, ...]]:
    text = re.sub(r"<[^>]+>", "\n", content)
    facts: dict[str, object] = {}
    warnings: list[str] = []
    for key in FACT_KEYS:
        pattern = re.compile(rf"(?im)^\s*{re.escape(key)}\s*[:=]\s*(.+?)\s*$")
        match = pattern.search(text)
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


def _draft_record(config: PublicSourceFetchConfig, facts: dict[str, object], warnings: tuple[str, ...]) -> dict[str, object]:
    return {
        "evidence_id": f"draft_public_{config.source_id}",
        "asset_id": config.asset_id,
        "evidence_type": config.evidence_type,
        "source_quality": SOURCE_QUALITY_BY_TYPE[config.source_type],
        "source_name": config.source_name,
        "as_of": REFERENCE_DATE,
        "verified_by_user": False,
        "verification_notes": "Auto-fetched public evidence draft. User verification required.",
        "url_reference": config.url_reference,
        "extracted_facts": facts,
        "warnings": list(warnings),
    }


def fetch_public_source(
    config: PublicSourceFetchConfig,
    assets_by_id: dict[str, CandidateAsset],
    network_fetch: Callable[[str, int, int], str] | None = None,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    max_bytes: int = DEFAULT_MAX_BYTES,
) -> PublicSourceFetchResult:
    blockers: list[str] = []
    warnings: list[str] = []
    if config.source_type in FORBIDDEN_SOURCE_TYPES:
        blockers.append(f"{config.source_id}: forbidden source_type {config.source_type}.")
    elif config.source_type not in SUPPORTED_PUBLIC_SOURCE_TYPES:
        blockers.append(f"{config.source_id}: unsupported source_type {config.source_type}.")
    if config.asset_id not in assets_by_id:
        blockers.append(f"{config.source_id}: unknown asset_id {config.asset_id}.")
    if not config.enabled:
        blockers.append(f"{config.source_id}: source disabled; skipped.")
    if blockers:
        return PublicSourceFetchResult(config.source_id, config.asset_id, "BLOCKED", "blocked", None, {}, (), tuple(blockers))

    mode = "local_fixture"
    content = config.local_fixture_content or ""
    if not config.allow_network_fetch:
        if not config.local_fixture_content:
            warnings.append(f"{config.source_id}: network fetch disabled and no local_fixture_content supplied.")
    else:
        mode = "network_fetch"
        if not _is_public_url(config.url_reference):
            blockers.append(f"{config.source_id}: allow_network_fetch requires a public http or https URL.")
        else:
            try:
                fetcher = network_fetch or _default_network_fetch
                content = fetcher(config.url_reference or "", timeout_seconds, max_bytes)
            except (OSError, urllib.error.URLError, TimeoutError, ValueError) as exc:
                warnings.append(f"{config.source_id}: network fetch failed: {exc}.")
                content = config.local_fixture_content or ""
                mode = "network_warning"
        if blockers:
            return PublicSourceFetchResult(config.source_id, config.asset_id, "BLOCKED", mode, None, {}, tuple(warnings), tuple(blockers))

    facts, fact_warnings = extract_public_source_facts(content)
    warnings.extend(fact_warnings)
    draft = _draft_record(config, facts, tuple(dict.fromkeys(warnings)))
    status = "WARNING" if warnings else "DRAFT_EVIDENCE_CREATED"
    return PublicSourceFetchResult(
        source_id=config.source_id,
        asset_id=config.asset_id,
        status=status,
        mode=mode,
        draft_evidence_record=draft,
        extracted_facts=facts,
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=(),
    )


def run_public_source_fetcher(
    registry_path: str | Path | AssetRegistry,
    sources_path: str | Path,
    network_fetch: Callable[[str, int, int], str] | None = None,
) -> PublicSourceFetchRunResult:
    registry = load_asset_registry(registry_path) if not isinstance(registry_path, AssetRegistry) else registry_path
    assets_by_id = registry.by_id()
    results = tuple(
        fetch_public_source(config, assets_by_id, network_fetch=network_fetch)
        for config in load_public_source_configs(sources_path)
    )
    return PublicSourceFetchRunResult(results=results)
