"""Draft-only public source research pack for the FTAW candidate.

The pack turns FTAW public research collection items into unverified draft
evidence records. It does not fetch, verify, approve, mutate, recommend, or
trade.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ftaw_source_collection_pack import (
    FTAWSourceCollectionItem,
    build_ftaw_source_collection_pack_from_files,
)


DEFAULT_TARGET_ASSET_ID = "ftaw_global_core_candidate"
PUBLIC_RESEARCH_EVIDENCE_TYPES = (
    "fund_metadata",
    "fee_metadata",
    "distribution_policy",
    "exposure_data",
    "market_data",
)
SKIPPED_MANUAL_EVIDENCE_TYPES = ("platform_availability", "tax_route")


@dataclass(frozen=True)
class FTAWPublicSourceResearchConfig:
    target_asset_id: str = DEFAULT_TARGET_ASSET_ID
    source_quality_by_evidence_type: dict[str, str] | None = None
    local_static_fixture_facts: dict[str, dict[str, object]] | None = None


@dataclass(frozen=True)
class FTAWPublicSourceResearchPack:
    pack_status: str
    target_asset_id: str
    public_research_tasks_count: int
    draft_evidence_records: tuple[dict[str, object], ...]
    skipped_manual_evidence_types: tuple[str, ...]
    draft_records_by_evidence_type: dict[str, int]
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


def _optional_string_map(value: Any, field: str) -> dict[str, str]:
    if value is None:
        return {}
    raw = _require_mapping(value, field)
    parsed: dict[str, str] = {}
    for key, item in raw.items():
        parsed[str(key)] = _require_text(item, f"{field}.{key}")
    return parsed


def _optional_facts_map(value: Any) -> dict[str, dict[str, object]]:
    if value is None:
        return {}
    raw = _require_mapping(value, "local_static_fixture_facts")
    parsed: dict[str, dict[str, object]] = {}
    for evidence_type, facts in raw.items():
        parsed[str(evidence_type)] = dict(_require_mapping(facts, f"local_static_fixture_facts.{evidence_type}"))
    return parsed


def load_ftaw_public_source_research_config(path: str | Path) -> FTAWPublicSourceResearchConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "FTAW public source research config")
    return FTAWPublicSourceResearchConfig(
        target_asset_id=_require_text(raw.get("target_asset_id", DEFAULT_TARGET_ASSET_ID), "target_asset_id"),
        source_quality_by_evidence_type=_optional_string_map(raw.get("source_quality_by_evidence_type"), "source_quality_by_evidence_type"),
        local_static_fixture_facts=_optional_facts_map(raw.get("local_static_fixture_facts")),
    )


def _placeholder_facts(item: FTAWSourceCollectionItem) -> dict[str, object]:
    return {field: f"<{field}_to_capture>" for field in item.fields_to_capture}


def _draft_record(
    item: FTAWSourceCollectionItem,
    config: FTAWPublicSourceResearchConfig,
) -> tuple[dict[str, object], tuple[str, ...]]:
    source_quality_by_type = config.source_quality_by_evidence_type or {}
    fixture_facts = (config.local_static_fixture_facts or {}).get(item.evidence_type)
    warnings: list[str] = []
    facts = _placeholder_facts(item)
    if fixture_facts:
        facts.update(fixture_facts)
        warnings.append(
            f"{item.evidence_type}: local/static fixture facts are draft only and require user verification."
        )
    return (
        {
            "evidence_id": f"draft_ftaw_public_{item.evidence_type}",
            "asset_id": config.target_asset_id,
            "evidence_type": item.evidence_type,
            "source_quality": source_quality_by_type.get(item.evidence_type, "<source_quality_to_select>"),
            "source_name": item.source_name or "<source_name_to_fill>",
            "as_of": "<YYYY-MM-DD>",
            "verified_by_user": False,
            "verification_notes": "<manual_review_required_before_verified_evidence>",
            "file_reference": None,
            "url_reference": item.url_reference or "<url_reference_to_fill>",
            "extracted_facts": facts,
            "warnings": list(warnings),
        },
        tuple(warnings),
    )


def build_ftaw_public_source_research_pack(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    planner_config_path: str | Path,
    source_collection_pack_config_path: str | Path,
    config: FTAWPublicSourceResearchConfig,
) -> FTAWPublicSourceResearchPack:
    source_pack = build_ftaw_source_collection_pack_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
        planner_config_path,
        source_collection_pack_config_path,
    )
    blockers = [*source_pack.blockers]
    warnings = [*source_pack.warnings]
    public_items = tuple(
        item
        for item in source_pack.collection_items
        if item.asset_id == config.target_asset_id and item.collection_mode == "public_research"
    )
    skipped_manual = tuple(
        sorted(
            item.evidence_type
            for item in source_pack.collection_items
            if item.asset_id == config.target_asset_id and item.collection_mode != "public_research"
        )
    )
    records: list[dict[str, object]] = []
    for item in public_items:
        record, record_warnings = _draft_record(item, config)
        records.append(record)
        warnings.extend(record_warnings)
        if record.get("verified_by_user") is not False:
            blockers.append(f"{item.evidence_type}: draft record must have verified_by_user=false.")
    if tuple(sorted(record["evidence_type"] for record in records)) != tuple(sorted(PUBLIC_RESEARCH_EVIDENCE_TYPES)):
        blockers.append(f"{config.target_asset_id}: expected exactly the five public research evidence records.")
    if any(evidence_type in {record["evidence_type"] for record in records} for evidence_type in SKIPPED_MANUAL_EVIDENCE_TYPES):
        blockers.append(f"{config.target_asset_id}: manual evidence types must not produce draft public records.")
    by_type: dict[str, int] = {}
    for record in records:
        evidence_type = str(record["evidence_type"])
        by_type[evidence_type] = by_type.get(evidence_type, 0) + 1
    unique_blockers = tuple(dict.fromkeys(blockers))
    return FTAWPublicSourceResearchPack(
        pack_status="READY" if records and not unique_blockers else "BLOCKED" if unique_blockers else "NO_RECORDS",
        target_asset_id=config.target_asset_id,
        public_research_tasks_count=len(public_items),
        draft_evidence_records=tuple(records),
        skipped_manual_evidence_types=skipped_manual,
        draft_records_by_evidence_type=dict(sorted(by_type.items())),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=unique_blockers,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_public_source_research_pack_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    planner_config_path: str | Path,
    source_collection_pack_config_path: str | Path,
    public_research_config_path: str | Path,
) -> FTAWPublicSourceResearchPack:
    return build_ftaw_public_source_research_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
        planner_config_path,
        source_collection_pack_config_path,
        load_ftaw_public_source_research_config(public_research_config_path),
    )
