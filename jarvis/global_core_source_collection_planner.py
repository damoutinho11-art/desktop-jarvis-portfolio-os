"""Human source collection planner for global core ETF evidence.

This planner converts disabled source templates into manual collection tasks.
It does not fetch sources, verify evidence, approve assets, mutate registries,
recommend allocations, create orders, or trade.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .global_core_source_template_expander import (
    GlobalCoreSourceTemplate,
    build_global_core_source_template_expansion_from_files,
)


PUBLIC_EVIDENCE_TYPES = {
    "fund_metadata",
    "fee_metadata",
    "distribution_policy",
    "exposure_data",
}
PRIORITY_BY_EVIDENCE_TYPE = {
    "fund_metadata": 10,
    "fee_metadata": 11,
    "distribution_policy": 12,
    "exposure_data": 13,
    "market_data": 20,
    "platform_availability": 30,
    "tax_route": 40,
}
ACCEPTANCE_CRITERIA = {
    "fund_metadata": (
        "Capture source URL or document reference.",
        "Capture fund name, ticker, ISIN, provider, index, and replication method.",
        "Do not mark evidence verified until manually reviewed.",
    ),
    "fee_metadata": (
        "Capture fee/TER value and source date if visible.",
        "Capture whether source is factsheet, KIID, or provider page.",
        "Do not mark evidence verified until manually reviewed.",
    ),
    "distribution_policy": (
        "Capture accumulation/distribution policy and source reference.",
        "Confirm the policy applies to the exact candidate instrument.",
        "Do not mark evidence verified until manually reviewed.",
    ),
    "exposure_data": (
        "Capture holdings, country, and sector source references.",
        "Capture source as-of date if visible.",
        "Do not mark evidence verified until manually reviewed.",
    ),
    "market_data": (
        "Capture price, currency, source, and as_of date.",
        "Confirm the market data is for the exact candidate ticker or ISIN.",
        "Do not mark evidence verified until manually reviewed.",
    ),
    "platform_availability": (
        "Capture account-specific Lightyear screenshot or manual account note.",
        "Confirm no order was placed.",
        "Do not mark evidence verified until manually reviewed.",
    ),
    "tax_route": (
        "Capture manual tax/account route notes.",
        "Confirm route does not use emergency funds or trading automation.",
        "Do not mark evidence verified until manually reviewed.",
    ),
}


@dataclass(frozen=True)
class GlobalCoreSourceCollectionPlannerConfig:
    focus_candidate_ids: tuple[str, ...] = ()
    top_next_tasks_limit: int = 10
    auto_fetch_allowed_by_default: bool = False


@dataclass(frozen=True)
class SourceCollectionTask:
    collection_task_id: str
    asset_id: str
    evidence_type: str
    source_id: str
    source_type: str
    source_name: str
    url_reference: str
    collection_priority: int
    collection_mode: str
    collection_instructions: str
    fields_to_capture: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    manual_verification_required: bool
    auto_fetch_allowed: bool
    auto_verified: bool
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class GlobalCoreSourceCollectionPlan:
    collection_plan_status: str
    target_candidates: tuple[str, ...]
    already_reviewed_skipped: tuple[str, ...]
    tasks: tuple[SourceCollectionTask, ...]
    top_next_collection_tasks: tuple[SourceCollectionTask, ...]
    tasks_by_candidate: dict[str, int]
    tasks_by_collection_mode: dict[str, int]
    account_specific_manual_tasks_count: int
    manual_tax_review_tasks_count: int
    auto_fetch_allowed_count: int
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


def _text_tuple(value: Any, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list when provided.")
    result = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field} must contain non-empty text.")
        result.append(item.strip())
    return tuple(result)


def load_global_core_source_collection_planner_config(path: str | Path) -> GlobalCoreSourceCollectionPlannerConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "global core source collection planner config")
    limit = raw.get("top_next_tasks_limit", 10)
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("top_next_tasks_limit must be a positive integer.")
    auto_fetch_default = raw.get("auto_fetch_allowed_by_default", False)
    if not isinstance(auto_fetch_default, bool):
        raise ValueError("auto_fetch_allowed_by_default must be true or false.")
    return GlobalCoreSourceCollectionPlannerConfig(
        focus_candidate_ids=_text_tuple(raw.get("focus_candidate_ids"), "focus_candidate_ids"),
        top_next_tasks_limit=limit,
        auto_fetch_allowed_by_default=auto_fetch_default,
    )


def _collection_mode(evidence_type: str) -> str:
    if evidence_type == "platform_availability":
        return "account_specific_manual"
    if evidence_type == "tax_route":
        return "manual_tax_review"
    return "public_research"


def _instructions(template: GlobalCoreSourceTemplate, mode: str) -> str:
    if mode == "account_specific_manual":
        return (
            f"Collect account-specific evidence for {template.asset_id}: {template.source_guidance}. "
            "Do not place an order and do not enter credentials into J.A.R.V.I.S."
        )
    if mode == "manual_tax_review":
        return (
            f"Prepare a manual tax/account route note for {template.asset_id}: {template.source_guidance}. "
            "No recommendation or approval is created."
        )
    return (
        f"Collect public reference material for {template.asset_id}: {template.source_guidance}. "
        "No network fetch is performed by this planner."
    )


def _task_from_template(template: GlobalCoreSourceTemplate, auto_fetch_allowed: bool) -> SourceCollectionTask:
    mode = _collection_mode(template.evidence_type)
    blockers: list[str] = []
    warnings: list[str] = []
    if template.enabled:
        blockers.append(f"{template.source_id}: source template must remain disabled.")
    if template.allow_network_fetch:
        blockers.append(f"{template.source_id}: source template must not allow network fetch.")
    if template.auto_verified:
        blockers.append(f"{template.source_id}: source template must not be auto-verified.")
    if auto_fetch_allowed:
        blockers.append(f"{template.source_id}: auto_fetch_allowed must remain false by default.")
    return SourceCollectionTask(
        collection_task_id=f"collect_source_{template.source_id}",
        asset_id=template.asset_id,
        evidence_type=template.evidence_type,
        source_id=template.source_id,
        source_type=template.source_type,
        source_name=template.source_name,
        url_reference=template.url_reference,
        collection_priority=PRIORITY_BY_EVIDENCE_TYPE.get(template.evidence_type, 99),
        collection_mode=mode,
        collection_instructions=_instructions(template, mode),
        fields_to_capture=template.fields_to_verify,
        acceptance_criteria=ACCEPTANCE_CRITERIA[template.evidence_type],
        manual_verification_required=True,
        auto_fetch_allowed=auto_fetch_allowed,
        auto_verified=False,
        warnings=tuple(warnings),
        blockers=tuple(blockers),
    )


def _sort_key(task: SourceCollectionTask) -> tuple[str, int, str]:
    return (task.asset_id, task.collection_priority, task.evidence_type)


def build_global_core_source_collection_plan(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    config: GlobalCoreSourceCollectionPlannerConfig,
) -> GlobalCoreSourceCollectionPlan:
    expansion = build_global_core_source_template_expansion_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
    )
    focus = set(config.focus_candidate_ids)
    selected_templates = tuple(
        template for template in expansion.templates if not focus or template.asset_id in focus
    )
    tasks = tuple(
        sorted(
            (
                _task_from_template(template, config.auto_fetch_allowed_by_default)
                for template in selected_templates
            ),
            key=_sort_key,
        )
    )
    blockers = [*expansion.blockers]
    blockers.extend(blocker for task in tasks for blocker in task.blockers)
    warnings = [*expansion.warnings]
    warnings.extend(warning for task in tasks for warning in task.warnings)
    by_candidate: dict[str, int] = {}
    by_mode: dict[str, int] = {}
    for task in tasks:
        by_candidate[task.asset_id] = by_candidate.get(task.asset_id, 0) + 1
        by_mode[task.collection_mode] = by_mode.get(task.collection_mode, 0) + 1
    target_candidates = tuple(sorted(by_candidate))
    unique_blockers = tuple(dict.fromkeys(blockers))
    return GlobalCoreSourceCollectionPlan(
        collection_plan_status="READY" if tasks and not unique_blockers else "BLOCKED" if unique_blockers else "NO_TASKS",
        target_candidates=target_candidates,
        already_reviewed_skipped=expansion.already_reviewed_skipped,
        tasks=tasks,
        top_next_collection_tasks=tasks[: config.top_next_tasks_limit],
        tasks_by_candidate=dict(sorted(by_candidate.items())),
        tasks_by_collection_mode=dict(sorted(by_mode.items())),
        account_specific_manual_tasks_count=by_mode.get("account_specific_manual", 0),
        manual_tax_review_tasks_count=by_mode.get("manual_tax_review", 0),
        auto_fetch_allowed_count=sum(task.auto_fetch_allowed for task in tasks),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=unique_blockers,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_global_core_source_collection_plan_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    planner_config_path: str | Path,
) -> GlobalCoreSourceCollectionPlan:
    return build_global_core_source_collection_plan(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
        load_global_core_source_collection_planner_config(planner_config_path),
    )
