"""Focused source collection pack for the FTAW global core candidate.

The pack converts manual collection tasks into ready-to-fill verified evidence
intake templates. It does not fetch, verify, approve, mutate, recommend, or
trade.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .global_core_source_collection_planner import (
    SourceCollectionTask,
    build_global_core_source_collection_plan_from_files,
)


DEFAULT_TARGET_ASSET_ID = "ftaw_global_core_candidate"


@dataclass(frozen=True)
class FTAWSourceCollectionPackConfig:
    target_asset_id: str = DEFAULT_TARGET_ASSET_ID


@dataclass(frozen=True)
class FTAWSourceCollectionItem:
    collection_task_id: str
    asset_id: str
    evidence_type: str
    collection_mode: str
    source_type: str
    source_name: str
    url_reference: str
    fields_to_capture: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    ready_to_fill_intake_template: dict[str, object]
    manual_verification_required: bool
    auto_fetch_allowed: bool
    auto_verified: bool


@dataclass(frozen=True)
class FTAWSourceCollectionPack:
    pack_status: str
    target_asset_id: str
    collection_items: tuple[FTAWSourceCollectionItem, ...]
    items_by_evidence_type: dict[str, int]
    public_research_tasks_count: int
    account_specific_manual_tasks_count: int
    manual_tax_review_tasks_count: int
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


def load_ftaw_source_collection_pack_config(path: str | Path) -> FTAWSourceCollectionPackConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "FTAW source collection pack config")
    return FTAWSourceCollectionPackConfig(
        target_asset_id=_require_text(raw.get("target_asset_id", DEFAULT_TARGET_ASSET_ID), "target_asset_id")
    )


def _placeholder_facts(fields: tuple[str, ...]) -> dict[str, object]:
    return {field: f"<{field}_to_capture>" for field in fields}


def _intake_template(task: SourceCollectionTask) -> dict[str, object]:
    return {
        "evidence_id": f"<verified_evidence_id_for_{task.asset_id}_{task.evidence_type}>",
        "asset_id": task.asset_id,
        "evidence_type": task.evidence_type,
        "source_quality": "<source_quality_to_select>",
        "source_name": task.source_name or "<source_name_to_fill>",
        "as_of": "<YYYY-MM-DD>",
        "verified_by_user": False,
        "verification_notes": "<manual_verification_notes_to_fill>",
        "file_reference": None,
        "url_reference": task.url_reference or "<url_reference_to_fill>",
        "extracted_facts": _placeholder_facts(task.fields_to_capture),
        "warnings": [],
    }


def _item_from_task(task: SourceCollectionTask) -> FTAWSourceCollectionItem:
    return FTAWSourceCollectionItem(
        collection_task_id=task.collection_task_id,
        asset_id=task.asset_id,
        evidence_type=task.evidence_type,
        collection_mode=task.collection_mode,
        source_type=task.source_type,
        source_name=task.source_name,
        url_reference=task.url_reference,
        fields_to_capture=task.fields_to_capture,
        acceptance_criteria=task.acceptance_criteria,
        ready_to_fill_intake_template=_intake_template(task),
        manual_verification_required=True,
        auto_fetch_allowed=False,
        auto_verified=False,
    )


def _validate_item(item: FTAWSourceCollectionItem) -> tuple[str, ...]:
    blockers: list[str] = []
    template = item.ready_to_fill_intake_template
    if template.get("verified_by_user") is not False:
        blockers.append(f"{item.collection_task_id}: intake template must have verified_by_user=false.")
    if item.manual_verification_required is not True:
        blockers.append(f"{item.collection_task_id}: manual_verification_required must be true.")
    if item.auto_fetch_allowed:
        blockers.append(f"{item.collection_task_id}: auto_fetch_allowed must be false.")
    if item.auto_verified:
        blockers.append(f"{item.collection_task_id}: auto_verified must be false.")
    if item.evidence_type == "platform_availability" and item.collection_mode != "account_specific_manual":
        blockers.append(f"{item.collection_task_id}: platform availability must use account_specific_manual.")
    if item.evidence_type == "tax_route" and item.collection_mode != "manual_tax_review":
        blockers.append(f"{item.collection_task_id}: tax route must use manual_tax_review.")
    if item.evidence_type == "market_data":
        fields = {field.lower() for field in item.fields_to_capture}
        if not {"price", "currency", "source"}.issubset(fields):
            blockers.append(f"{item.collection_task_id}: market data must capture price, currency, and source.")
        if not any(field in fields for field in ("as_of_date", "market_date")):
            blockers.append(f"{item.collection_task_id}: market data must capture an as_of date or market date.")
    return tuple(blockers)


def build_ftaw_source_collection_pack(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    planner_config_path: str | Path,
    config: FTAWSourceCollectionPackConfig,
) -> FTAWSourceCollectionPack:
    plan = build_global_core_source_collection_plan_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
        planner_config_path,
    )
    tasks = tuple(task for task in plan.tasks if task.asset_id == config.target_asset_id)
    items = tuple(_item_from_task(task) for task in tasks)
    blockers = [*plan.blockers]
    warnings = [*plan.warnings]
    blockers.extend(blocker for item in items for blocker in _validate_item(item))
    if len(items) != 7:
        blockers.append(f"{config.target_asset_id}: expected exactly 7 collection items.")
    by_type: dict[str, int] = {}
    by_mode: dict[str, int] = {}
    for item in items:
        by_type[item.evidence_type] = by_type.get(item.evidence_type, 0) + 1
        by_mode[item.collection_mode] = by_mode.get(item.collection_mode, 0) + 1
    unique_blockers = tuple(dict.fromkeys(blockers))
    return FTAWSourceCollectionPack(
        pack_status="READY" if items and not unique_blockers else "BLOCKED" if unique_blockers else "NO_ITEMS",
        target_asset_id=config.target_asset_id,
        collection_items=items,
        items_by_evidence_type=dict(sorted(by_type.items())),
        public_research_tasks_count=by_mode.get("public_research", 0),
        account_specific_manual_tasks_count=by_mode.get("account_specific_manual", 0),
        manual_tax_review_tasks_count=by_mode.get("manual_tax_review", 0),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=unique_blockers,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_source_collection_pack_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    planner_config_path: str | Path,
    pack_config_path: str | Path,
) -> FTAWSourceCollectionPack:
    return build_ftaw_source_collection_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
        planner_config_path,
        load_ftaw_source_collection_pack_config(pack_config_path),
    )
