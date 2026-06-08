"""FTAW public source auto-draft collector.

Automated research. Manual trust.

This module consumes local/static public source snippets and produces draft
VerifiedEvidenceIntakeRecord-compatible records. It never fetches by default
and never verifies evidence automatically.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .asset_registry import load_asset_registry
from .ftaw_draft_evidence_verification_queue import REQUIRED_FACT_FIELDS
from .ftaw_public_source_research_pack import PUBLIC_RESEARCH_EVIDENCE_TYPES


TARGET_ASSET_ID = "ftaw_global_core_candidate"
FORBIDDEN_SOURCE_TYPES = {
    "authenticated_broker",
    "personal_account_page",
    "trading_api",
    "credentialed_api",
}
ALLOWED_SOURCE_TYPES = {
    "provider_product_page",
    "provider_factsheet_pdf",
    "provider_kiid_pdf",
    "public_market_data_page",
    "manual_url_reference",
    "local_source_fixture",
}
SOURCE_QUALITY_BY_TYPE = {
    "provider_product_page": "provider_factsheet",
    "provider_factsheet_pdf": "provider_factsheet",
    "provider_kiid_pdf": "provider_factsheet",
    "public_market_data_page": "manual_research",
    "manual_url_reference": "manual_research",
    "local_source_fixture": "manual_research",
}
MANUAL_EVIDENCE_TYPES = ("platform_availability", "tax_route")


@dataclass(frozen=True)
class FTAWAutoDraftSourceRecord:
    source_id: str
    asset_id: str
    evidence_type: str
    source_type: str
    source_name: str
    url_reference: str
    local_text_content: str
    local_file_reference: str | None
    enabled: bool
    allow_network_fetch: bool
    extraction_rules: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class FTAWAutoDraftConfig:
    sources: tuple[FTAWAutoDraftSourceRecord, ...]


@dataclass(frozen=True)
class FTAWAutoDraftResult:
    source_id: str
    asset_id: str
    evidence_type: str
    source_status: str
    draft_status: str | None
    draft_record: dict[str, object] | None
    extracted_facts: dict[str, object]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class FTAWPublicSourceAutoDraftPack:
    auto_draft_status: str
    processed_source_count: int
    skipped_source_count: int
    blocked_source_count: int
    draft_evidence_records: tuple[dict[str, object], ...]
    draft_records_by_evidence_type: dict[str, int]
    draft_ready_count: int
    needs_correction_count: int
    manual_evidence_skipped: tuple[str, ...]
    network_fetch_enabled_count: int
    results: tuple[FTAWAutoDraftResult, ...]
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


def _parse_extraction_rules(value: Any) -> dict[str, tuple[str, ...]]:
    raw = _require_mapping(value, "extraction_rules")
    rules: dict[str, tuple[str, ...]] = {}
    for fact_key, keywords in raw.items():
        if not isinstance(keywords, list) or not keywords:
            raise ValueError(f"extraction_rules.{fact_key} must be a non-empty list.")
        rules[str(fact_key)] = tuple(_require_text(keyword, f"extraction_rules.{fact_key}") for keyword in keywords)
    return rules


def _parse_source(raw: dict[str, Any]) -> FTAWAutoDraftSourceRecord:
    item = _require_mapping(raw, "auto-draft source")
    return FTAWAutoDraftSourceRecord(
        source_id=_require_text(item.get("source_id"), "source_id"),
        asset_id=_require_text(item.get("asset_id"), "asset_id"),
        evidence_type=_require_text(item.get("evidence_type"), "evidence_type"),
        source_type=_require_text(item.get("source_type"), "source_type"),
        source_name=_require_text(item.get("source_name"), "source_name"),
        url_reference=_require_text(item.get("url_reference"), "url_reference"),
        local_text_content=str(item.get("local_text_content", "")),
        local_file_reference=_optional_text(item.get("local_file_reference"), "local_file_reference"),
        enabled=_require_bool(item.get("enabled"), "enabled"),
        allow_network_fetch=_require_bool(item.get("allow_network_fetch"), "allow_network_fetch"),
        extraction_rules=_parse_extraction_rules(item.get("extraction_rules", {})),
    )


def load_ftaw_public_source_auto_draft_config(path: str | Path) -> FTAWAutoDraftConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "FTAW public source auto-draft config")
    sources = raw.get("sources")
    if not isinstance(sources, list):
        raise ValueError("sources must be a list.")
    return FTAWAutoDraftConfig(sources=tuple(_parse_source(source) for source in sources))


def _extract_value(text: str, keywords: tuple[str, ...]) -> str | None:
    for keyword in keywords:
        pattern = re.compile(rf"(?im)^\s*{re.escape(keyword)}\s*[:=]\s*(.+?)\s*$")
        match = pattern.search(text)
        if match:
            return match.group(1).strip()
    return None


def extract_facts_from_text(text: str, extraction_rules: dict[str, tuple[str, ...]]) -> dict[str, object]:
    facts: dict[str, object] = {}
    for fact_key, keywords in extraction_rules.items():
        value = _extract_value(text, keywords)
        if value is not None:
            facts[fact_key] = value
    return facts


def _missing_required(evidence_type: str, facts: dict[str, object]) -> tuple[str, ...]:
    return tuple(
        field
        for field in REQUIRED_FACT_FIELDS.get(evidence_type, ())
        if field not in facts or _is_placeholder(facts[field])
    )


def _is_placeholder(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        return not stripped or stripped.startswith("<") or stripped.endswith("_to_capture>")
    return False


def _draft_record(source: FTAWAutoDraftSourceRecord, facts: dict[str, object], warnings: tuple[str, ...]) -> dict[str, object]:
    return {
        "evidence_id": f"auto_draft_{source.source_id}",
        "asset_id": source.asset_id,
        "evidence_type": source.evidence_type,
        "source_quality": SOURCE_QUALITY_BY_TYPE.get(source.source_type, "manual_research"),
        "source_name": source.source_name,
        "as_of": "<YYYY-MM-DD>",
        "verified_by_user": False,
        "verification_notes": "Auto-drafted public source evidence. Manual verification required.",
        "file_reference": source.local_file_reference,
        "url_reference": source.url_reference,
        "extracted_facts": facts,
        "warnings": list(warnings),
    }


def process_auto_draft_source(source: FTAWAutoDraftSourceRecord) -> FTAWAutoDraftResult:
    warnings: list[str] = []
    blockers: list[str] = []
    if source.asset_id != TARGET_ASSET_ID:
        return FTAWAutoDraftResult(source.source_id, source.asset_id, source.evidence_type, "skipped", None, None, {}, (), ())
    if not source.enabled:
        return FTAWAutoDraftResult(source.source_id, source.asset_id, source.evidence_type, "skipped", None, None, {}, (), ())
    if source.evidence_type in MANUAL_EVIDENCE_TYPES:
        warnings.append(f"{source.evidence_type}: manual evidence type skipped by public auto-draft collector.")
        return FTAWAutoDraftResult(source.source_id, source.asset_id, source.evidence_type, "skipped", None, None, {}, tuple(warnings), ())
    if source.evidence_type not in PUBLIC_RESEARCH_EVIDENCE_TYPES:
        blockers.append(f"{source.source_id}: unsupported evidence_type {source.evidence_type}.")
        return FTAWAutoDraftResult(source.source_id, source.asset_id, source.evidence_type, "blocked", None, None, {}, tuple(warnings), tuple(blockers))
    if source.source_type in FORBIDDEN_SOURCE_TYPES:
        blockers.append(f"{source.source_id}: forbidden source_type {source.source_type}.")
        return FTAWAutoDraftResult(source.source_id, source.asset_id, source.evidence_type, "blocked", None, None, {}, tuple(warnings), tuple(blockers))
    if source.source_type not in ALLOWED_SOURCE_TYPES:
        blockers.append(f"{source.source_id}: unsupported source_type {source.source_type}.")
        return FTAWAutoDraftResult(source.source_id, source.asset_id, source.evidence_type, "blocked", None, None, {}, tuple(warnings), tuple(blockers))
    if source.allow_network_fetch:
        warnings.append(f"{source.source_id}: network fetch flag is enabled, but no network fetch is performed by this collector.")
    facts = extract_facts_from_text(source.local_text_content, source.extraction_rules)
    missing = _missing_required(source.evidence_type, facts)
    warnings.append("draft_public_source_requires_manual_verification")
    if not source.local_text_content.strip():
        blockers.append(f"{source.source_id}: local_text_content is empty.")
    blockers.extend(f"{source.source_id}: missing required fact {field}." for field in missing)
    status = "needs_correction" if blockers else "draft_ready_for_manual_verification"
    return FTAWAutoDraftResult(
        source_id=source.source_id,
        asset_id=source.asset_id,
        evidence_type=source.evidence_type,
        source_status="processed",
        draft_status=status,
        draft_record=_draft_record(source, facts, tuple(warnings)),
        extracted_facts=facts,
        warnings=tuple(warnings),
        blockers=tuple(blockers),
    )


def build_ftaw_public_source_auto_draft_pack(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    public_research_config_path: str | Path,
    verification_config_path: str | Path,
    auto_draft_config: FTAWAutoDraftConfig,
) -> FTAWPublicSourceAutoDraftPack:
    registry = load_asset_registry(source_registry_path)
    if TARGET_ASSET_ID not in registry.by_id():
        raise ValueError(f"{TARGET_ASSET_ID} not found in registry.")
    # Paths are intentionally loaded/validated by existence only for this focused layer.
    Path(public_research_config_path).read_text(encoding="utf-8")
    Path(verification_config_path).read_text(encoding="utf-8")
    if reviewed_registry_copy_path is not None and str(reviewed_registry_copy_path).lower() not in {"", "none", "null", "-"}:
        Path(reviewed_registry_copy_path).read_text(encoding="utf-8")

    results = tuple(process_auto_draft_source(source) for source in auto_draft_config.sources)
    records = tuple(result.draft_record for result in results if result.draft_record is not None)
    by_type: dict[str, int] = {}
    for record in records:
        evidence_type = str(record["evidence_type"])
        by_type[evidence_type] = by_type.get(evidence_type, 0) + 1
    warnings = tuple(dict.fromkeys(warning for result in results for warning in result.warnings))
    blockers = tuple(dict.fromkeys(blocker for result in results for blocker in result.blockers))
    draft_ready_count = sum(result.draft_status == "draft_ready_for_manual_verification" for result in results)
    needs_correction_count = sum(result.draft_status == "needs_correction" for result in results)
    status = "READY_WITH_CORRECTIONS" if needs_correction_count else "READY" if records else "NO_DRAFTS"
    if any(result.source_status == "blocked" for result in results):
        status = "BLOCKED"
    return FTAWPublicSourceAutoDraftPack(
        auto_draft_status=status,
        processed_source_count=sum(result.source_status == "processed" for result in results),
        skipped_source_count=sum(result.source_status == "skipped" for result in results),
        blocked_source_count=sum(result.source_status == "blocked" for result in results),
        draft_evidence_records=records,
        draft_records_by_evidence_type=dict(sorted(by_type.items())),
        draft_ready_count=draft_ready_count,
        needs_correction_count=needs_correction_count,
        manual_evidence_skipped=tuple(sorted({result.evidence_type for result in results if result.evidence_type in MANUAL_EVIDENCE_TYPES and result.source_status == "skipped"})),
        network_fetch_enabled_count=sum(source.allow_network_fetch for source in auto_draft_config.sources),
        results=results,
        warnings=warnings,
        blockers=blockers,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_public_source_auto_draft_pack_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    public_research_config_path: str | Path,
    verification_config_path: str | Path,
    auto_draft_config_path: str | Path,
) -> FTAWPublicSourceAutoDraftPack:
    return build_ftaw_public_source_auto_draft_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        public_research_config_path,
        verification_config_path,
        load_ftaw_public_source_auto_draft_config(auto_draft_config_path),
    )
