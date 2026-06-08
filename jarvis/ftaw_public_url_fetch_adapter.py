"""Controlled public URL fetch adapter for FTAW public evidence drafts.

Automated research. Manual trust.

Network access is disabled by default and can only be attempted when global and
per-source gates are explicitly enabled for safe public source types and URLs.
Fetched or fixture evidence is always draft-only and unverified.
"""

from __future__ import annotations

import json
import re
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.parse import urlparse

from .asset_registry import load_asset_registry
from .ftaw_draft_evidence_verification_queue import REQUIRED_FACT_FIELDS
from .ftaw_public_source_auto_draft import (
    PUBLIC_RESEARCH_EVIDENCE_TYPES,
    TARGET_ASSET_ID,
    extract_facts_from_text,
)


ALLOWED_PUBLIC_SOURCE_TYPES = {
    "provider_product_page",
    "provider_factsheet_pdf",
    "provider_kiid_pdf",
    "public_market_data_page",
    "provider_holdings_page",
    "public_index_page",
}
FORBIDDEN_SOURCE_TYPES = {
    "authenticated_broker",
    "personal_account_page",
    "trading_api",
    "credentialed_api",
    "broker_account",
}
BLOCKED_URL_PATTERNS = (
    "login",
    "account",
    "trade",
    "order",
    "portfolio",
    "api/trading",
    "session",
    "token",
)
MANUAL_EVIDENCE_TYPES = ("platform_availability", "tax_route")
SOURCE_QUALITY_BY_TYPE = {
    "provider_product_page": "provider_factsheet",
    "provider_factsheet_pdf": "provider_factsheet",
    "provider_kiid_pdf": "provider_factsheet",
    "public_market_data_page": "manual_research",
    "provider_holdings_page": "provider_factsheet",
    "public_index_page": "manual_research",
}


@dataclass(frozen=True)
class FTAWPublicURLFetchSource:
    source_id: str
    asset_id: str
    evidence_type: str
    source_type: str
    source_name: str
    url_reference: str
    enabled: bool
    allow_network_fetch: bool
    local_fixture_text: str | None
    extraction_rules: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class FTAWPublicURLFetchConfig:
    enable_network_fetch: bool
    sources: tuple[FTAWPublicURLFetchSource, ...]


@dataclass(frozen=True)
class FTAWPublicURLFetchResult:
    source_id: str
    asset_id: str
    evidence_type: str
    source_status: str
    mode: str
    draft_status: str | None
    draft_record: dict[str, object] | None
    extracted_facts: dict[str, object]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class FTAWPublicURLFetchPack:
    fetch_status: str
    global_network_fetch_enabled: bool
    processed_source_count: int
    local_fixture_count: int
    network_fetch_attempted_count: int
    network_fetch_blocked_count: int
    skipped_source_count: int
    draft_evidence_records: tuple[dict[str, object], ...]
    draft_records_by_evidence_type: dict[str, int]
    draft_ready_count: int
    needs_correction_count: int
    blocked_sources: tuple[str, ...]
    manual_evidence_skipped: tuple[str, ...]
    results: tuple[FTAWPublicURLFetchResult, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
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


def _parse_rules(value: Any) -> dict[str, tuple[str, ...]]:
    raw = _require_mapping(value, "extraction_rules")
    parsed: dict[str, tuple[str, ...]] = {}
    for fact_key, labels in raw.items():
        if not isinstance(labels, list) or not labels:
            raise ValueError(f"extraction_rules.{fact_key} must be a non-empty list.")
        parsed[str(fact_key)] = tuple(_require_text(label, f"extraction_rules.{fact_key}") for label in labels)
    return parsed


def _parse_source(raw: dict[str, Any]) -> FTAWPublicURLFetchSource:
    item = _require_mapping(raw, "public URL fetch source")
    return FTAWPublicURLFetchSource(
        source_id=_require_text(item.get("source_id"), "source_id"),
        asset_id=_require_text(item.get("asset_id"), "asset_id"),
        evidence_type=_require_text(item.get("evidence_type"), "evidence_type"),
        source_type=_require_text(item.get("source_type"), "source_type"),
        source_name=_require_text(item.get("source_name"), "source_name"),
        url_reference=_require_text(item.get("url_reference"), "url_reference"),
        enabled=_require_bool(item.get("enabled"), "enabled"),
        allow_network_fetch=_require_bool(item.get("allow_network_fetch"), "allow_network_fetch"),
        local_fixture_text=_optional_text(item.get("local_fixture_text"), "local_fixture_text"),
        extraction_rules=_parse_rules(item.get("extraction_rules", {})),
    )


def load_ftaw_public_url_fetch_config(path: str | Path) -> FTAWPublicURLFetchConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "FTAW public URL fetch config")
    sources = raw.get("sources")
    if not isinstance(sources, list):
        raise ValueError("sources must be a list.")
    return FTAWPublicURLFetchConfig(
        enable_network_fetch=_require_bool(raw.get("enable_network_fetch", False), "enable_network_fetch"),
        sources=tuple(_parse_source(source) for source in sources),
    )


def is_safe_public_url(url: str) -> tuple[bool, tuple[str, ...]]:
    blockers: list[str] = []
    parsed = urlparse(url)
    if parsed.scheme != "https":
        blockers.append("URL scheme must be https.")
    lowered = url.lower()
    for pattern in BLOCKED_URL_PATTERNS:
        if pattern in lowered:
            blockers.append(f"URL contains blocked pattern {pattern}.")
    return (not blockers, tuple(blockers))


def _is_placeholder(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        return not stripped or stripped.startswith("<") or stripped.endswith("_to_capture>")
    return False


def _missing_required(evidence_type: str, facts: dict[str, object]) -> tuple[str, ...]:
    return tuple(
        field
        for field in REQUIRED_FACT_FIELDS.get(evidence_type, ())
        if field not in facts or _is_placeholder(facts[field])
    )


def _default_fetch(url: str, timeout_seconds: int = 10, max_bytes: int = 200_000) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "JARVIS-public-evidence-draft/4.10"})
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return response.read(max_bytes).decode("utf-8", errors="replace")


def _draft_record(source: FTAWPublicURLFetchSource, facts: dict[str, object], warnings: tuple[str, ...]) -> dict[str, object]:
    return {
        "evidence_id": f"url_fetch_draft_{source.source_id}",
        "asset_id": source.asset_id,
        "evidence_type": source.evidence_type,
        "source_quality": SOURCE_QUALITY_BY_TYPE.get(source.source_type, "manual_research"),
        "source_name": source.source_name,
        "as_of": "<YYYY-MM-DD>",
        "verified_by_user": False,
        "verification_notes": "Auto-fetched public evidence draft. Manual verification required.",
        "file_reference": None,
        "url_reference": source.url_reference,
        "extracted_facts": facts,
        "warnings": list(warnings),
    }


def process_url_fetch_source(
    source: FTAWPublicURLFetchSource,
    enable_network_fetch: bool,
    fetcher: Callable[[str], str] | None = None,
) -> FTAWPublicURLFetchResult:
    warnings: list[str] = []
    blockers: list[str] = []
    if source.asset_id != TARGET_ASSET_ID:
        return FTAWPublicURLFetchResult(source.source_id, source.asset_id, source.evidence_type, "skipped", "not_target_asset", None, None, {}, (), ())
    if not source.enabled:
        return FTAWPublicURLFetchResult(source.source_id, source.asset_id, source.evidence_type, "skipped", "disabled", None, None, {}, (), ())
    if source.evidence_type in MANUAL_EVIDENCE_TYPES:
        warnings.append(f"{source.evidence_type}: manual evidence type skipped by public URL fetch adapter.")
        return FTAWPublicURLFetchResult(source.source_id, source.asset_id, source.evidence_type, "skipped", "manual_evidence", None, None, {}, tuple(warnings), ())
    if source.evidence_type not in PUBLIC_RESEARCH_EVIDENCE_TYPES:
        blockers.append(f"{source.source_id}: unsupported evidence_type {source.evidence_type}.")
        return FTAWPublicURLFetchResult(source.source_id, source.asset_id, source.evidence_type, "blocked", "blocked", None, None, {}, tuple(warnings), tuple(blockers))
    if source.source_type in FORBIDDEN_SOURCE_TYPES:
        blockers.append(f"{source.source_id}: forbidden source_type {source.source_type}.")
        return FTAWPublicURLFetchResult(source.source_id, source.asset_id, source.evidence_type, "blocked", "blocked", None, None, {}, tuple(warnings), tuple(blockers))
    if source.source_type not in ALLOWED_PUBLIC_SOURCE_TYPES:
        blockers.append(f"{source.source_id}: unsupported source_type {source.source_type}.")
        return FTAWPublicURLFetchResult(source.source_id, source.asset_id, source.evidence_type, "blocked", "blocked", None, None, {}, tuple(warnings), tuple(blockers))

    fetched_text = source.local_fixture_text
    mode = "local_fixture" if fetched_text is not None else "network_fetch"
    if fetched_text is None:
        safe, url_blockers = is_safe_public_url(source.url_reference)
        blockers.extend(f"{source.source_id}: {blocker}" for blocker in url_blockers)
        if not enable_network_fetch:
            blockers.append(f"{source.source_id}: global network fetch is disabled.")
        if not source.allow_network_fetch:
            blockers.append(f"{source.source_id}: source allow_network_fetch is false.")
        if blockers:
            return FTAWPublicURLFetchResult(source.source_id, source.asset_id, source.evidence_type, "blocked", "network_blocked", None, None, {}, tuple(warnings), tuple(blockers))
        if not safe:
            return FTAWPublicURLFetchResult(source.source_id, source.asset_id, source.evidence_type, "blocked", "network_blocked", None, None, {}, tuple(warnings), tuple(blockers))
        fetched_text = (fetcher or _default_fetch)(source.url_reference)

    facts = extract_facts_from_text(fetched_text, source.extraction_rules)
    missing = _missing_required(source.evidence_type, facts)
    warnings.append("draft_public_source_requires_manual_verification")
    blockers.extend(f"{source.source_id}: missing required fact {field}." for field in missing)
    status = "needs_correction" if blockers else "draft_ready_for_manual_verification"
    return FTAWPublicURLFetchResult(
        source_id=source.source_id,
        asset_id=source.asset_id,
        evidence_type=source.evidence_type,
        source_status="processed",
        mode=mode,
        draft_status=status,
        draft_record=_draft_record(source, facts, tuple(warnings)),
        extracted_facts=facts,
        warnings=tuple(warnings),
        blockers=tuple(blockers),
    )


def build_ftaw_public_url_fetch_pack(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    auto_draft_config_path: str | Path,
    fetch_config: FTAWPublicURLFetchConfig,
    fetcher: Callable[[str], str] | None = None,
) -> FTAWPublicURLFetchPack:
    registry = load_asset_registry(source_registry_path)
    if TARGET_ASSET_ID not in registry.by_id():
        raise ValueError(f"{TARGET_ASSET_ID} not found in registry.")
    Path(auto_draft_config_path).read_text(encoding="utf-8")
    if reviewed_registry_copy_path is not None and str(reviewed_registry_copy_path).lower() not in {"", "none", "null", "-"}:
        Path(reviewed_registry_copy_path).read_text(encoding="utf-8")

    results = tuple(process_url_fetch_source(source, fetch_config.enable_network_fetch, fetcher) for source in fetch_config.sources)
    records = tuple(result.draft_record for result in results if result.draft_record is not None)
    by_type: dict[str, int] = {}
    for record in records:
        evidence_type = str(record["evidence_type"])
        by_type[evidence_type] = by_type.get(evidence_type, 0) + 1
    warnings = tuple(dict.fromkeys(warning for result in results for warning in result.warnings))
    blockers = tuple(dict.fromkeys(blocker for result in results for blocker in result.blockers))
    draft_ready = sum(result.draft_status == "draft_ready_for_manual_verification" for result in results)
    needs_correction = sum(result.draft_status == "needs_correction" for result in results)
    network_blocked = sum(result.mode == "network_blocked" for result in results)
    blocked_count = sum(result.source_status == "blocked" for result in results)
    status = "BLOCKED" if blocked_count else "READY_WITH_CORRECTIONS" if needs_correction else "READY" if records else "NO_DRAFTS"
    return FTAWPublicURLFetchPack(
        fetch_status=status,
        global_network_fetch_enabled=fetch_config.enable_network_fetch,
        processed_source_count=sum(result.source_status == "processed" for result in results),
        local_fixture_count=sum(result.mode == "local_fixture" for result in results),
        network_fetch_attempted_count=sum(result.mode == "network_fetch" for result in results),
        network_fetch_blocked_count=network_blocked,
        skipped_source_count=sum(result.source_status == "skipped" for result in results),
        draft_evidence_records=records,
        draft_records_by_evidence_type=dict(sorted(by_type.items())),
        draft_ready_count=draft_ready,
        needs_correction_count=needs_correction,
        blocked_sources=tuple(result.source_id for result in results if result.source_status == "blocked"),
        manual_evidence_skipped=tuple(sorted({result.evidence_type for result in results if result.mode == "manual_evidence"})),
        results=results,
        warnings=warnings,
        blockers=blockers,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_public_url_fetch_pack_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    auto_draft_config_path: str | Path,
    fetch_config_path: str | Path,
) -> FTAWPublicURLFetchPack:
    return build_ftaw_public_url_fetch_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        auto_draft_config_path,
        load_ftaw_public_url_fetch_config(fetch_config_path),
    )
