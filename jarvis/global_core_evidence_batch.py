"""Evidence collection batch for remaining global core ETF candidates.

The batch prepares manual verification tasks only. It does not verify evidence,
approve assets, mutate registries, create allocation recommendations, or create
buy/sell requests.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .asset_registry import load_asset_registry
from .multi_candidate_review_queue import (
    CandidateReviewQueueItem,
    build_multi_candidate_review_queue_from_files,
)


DEFAULT_TARGET_CANDIDATES = (
    "ftaw_global_core_candidate",
    "spyi_imie_global_core_candidate",
    "ssac_iusq_global_core_candidate",
    "webn_global_core_candidate",
)
GLOBAL_CORE_EVIDENCE_TYPES = (
    "fund_metadata",
    "fee_metadata",
    "distribution_policy",
    "platform_availability",
    "tax_route",
    "exposure_data",
    "market_data",
)
SOURCE_GUIDANCE = {
    "fund_metadata": "provider product page or provider factsheet",
    "fee_metadata": "provider factsheet or KIID",
    "distribution_policy": "provider product page/factsheet",
    "platform_availability": "account-specific Lightyear screenshot or account-specific manual note",
    "tax_route": "manual tax/account route note",
    "exposure_data": "provider holdings/country/sector page or factsheet",
    "market_data": "public market data page with price/currency/date/source",
}
SUGGESTED_SOURCE_TYPE = {
    "fund_metadata": "provider_product_page",
    "fee_metadata": "provider_factsheet_pdf",
    "distribution_policy": "provider_product_page",
    "platform_availability": "manual_url_reference",
    "tax_route": "manual_url_reference",
    "exposure_data": "provider_factsheet_pdf",
    "market_data": "public_market_data_page",
}
FIELDS_TO_VERIFY = {
    "fund_metadata": ("name", "ticker", "isin_or_symbol", "provider", "index_tracked", "replication_method"),
    "fee_metadata": ("ter_or_fee", "fee_source", "as_of_date"),
    "distribution_policy": ("distribution_policy", "accumulating_or_distributing", "as_of_date"),
    "platform_availability": ("platform_name", "instrument_visible", "account_specific_checked", "order_not_placed"),
    "tax_route": ("account_route", "tax_considerations", "manual_review_notes"),
    "exposure_data": ("top_holdings_source", "country_exposure_source", "sector_exposure_source", "as_of_date"),
    "market_data": ("price", "currency", "market_date", "source"),
}


@dataclass(frozen=True)
class GlobalCoreEvidenceBatchConfig:
    target_candidate_ids: tuple[str, ...]
    evidence_types: tuple[str, ...]
    create_source_config_templates: bool = True


@dataclass(frozen=True)
class EvidenceCollectionTask:
    task_id: str
    asset_id: str
    evidence_type: str
    priority: int
    suggested_source_type: str
    source_guidance: str
    fields_to_verify: tuple[str, ...]
    manual_verification_required: bool
    auto_verified: bool


@dataclass(frozen=True)
class GlobalCoreEvidenceBatch:
    batch_status: str
    target_candidates: tuple[str, ...]
    already_reviewed_skipped: tuple[str, ...]
    tasks: tuple[EvidenceCollectionTask, ...]
    source_config_templates: tuple[dict[str, object], ...]
    tasks_by_evidence_type: dict[str, int]
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


def _require_text_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list.")
    values = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field} must contain non-empty text.")
        values.append(item.strip())
    return tuple(values)


def load_global_core_evidence_batch_config(path: str | Path) -> GlobalCoreEvidenceBatchConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "global core evidence batch config")
    target_ids = raw.get("target_candidate_ids", list(DEFAULT_TARGET_CANDIDATES))
    evidence_types = raw.get("evidence_types", list(GLOBAL_CORE_EVIDENCE_TYPES))
    create_templates = raw.get("create_source_config_templates", True)
    if not isinstance(create_templates, bool):
        raise ValueError("create_source_config_templates must be true or false.")
    parsed_evidence_types = _require_text_list(evidence_types, "evidence_types")
    unsupported = [item for item in parsed_evidence_types if item not in GLOBAL_CORE_EVIDENCE_TYPES]
    if unsupported:
        raise ValueError("unsupported global core evidence type: " + ", ".join(unsupported))
    return GlobalCoreEvidenceBatchConfig(
        target_candidate_ids=_require_text_list(target_ids, "target_candidate_ids"),
        evidence_types=parsed_evidence_types,
        create_source_config_templates=create_templates,
    )


def _task_id(asset_id: str, evidence_type: str) -> str:
    return f"collect_{asset_id}_{evidence_type}"


def _source_template(asset_id: str, evidence_type: str) -> dict[str, object]:
    return {
        "source_id": f"draft_{asset_id}_{evidence_type}",
        "asset_id": asset_id,
        "evidence_type": evidence_type,
        "source_type": SUGGESTED_SOURCE_TYPE[evidence_type],
        "source_name": f"{asset_id} {evidence_type} manual source template",
        "url_reference": None,
        "enabled": False,
        "allow_network_fetch": False,
        "local_fixture_content": None,
        "notes": "Template only. User must provide and verify real evidence; no network fetch is allowed by default.",
    }


def _queue_items_by_id(items: tuple[CandidateReviewQueueItem, ...]) -> dict[str, CandidateReviewQueueItem]:
    return {item.asset_id: item for item in items}


def build_global_core_evidence_batch(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    config: GlobalCoreEvidenceBatchConfig,
) -> GlobalCoreEvidenceBatch:
    registry = load_asset_registry(source_registry_path)
    registry_by_id = registry.by_id()
    queue = build_multi_candidate_review_queue_from_files(source_registry_path, reviewed_registry_copy_path, queue_config_path)
    queue_by_id = _queue_items_by_id(queue.items)
    tasks: list[EvidenceCollectionTask] = []
    templates: list[dict[str, object]] = []
    warnings: list[str] = []
    blockers: list[str] = []
    target_candidates: list[str] = []
    skipped: list[str] = []

    for asset_id in config.target_candidate_ids:
        asset = registry_by_id.get(asset_id)
        item = queue_by_id.get(asset_id)
        if asset is None:
            blockers.append(f"{asset_id}: target candidate missing from registry.")
            continue
        if item is None:
            blockers.append(f"{asset_id}: target candidate missing from review queue.")
            continue
        if asset.sleeve != "global_core" or asset.asset_type != "ETF":
            blockers.append(f"{asset_id}: target must be a global_core ETF candidate.")
            continue
        if item.review_queue_status == "already_reviewed":
            skipped.append(asset_id)
            continue
        if item.review_queue_status == "blocked":
            warnings.append(f"{asset_id}: candidate is blocked in the review queue.")
        target_candidates.append(asset_id)
        for priority, evidence_type in enumerate(config.evidence_types, start=1):
            tasks.append(
                EvidenceCollectionTask(
                    task_id=_task_id(asset_id, evidence_type),
                    asset_id=asset_id,
                    evidence_type=evidence_type,
                    priority=priority,
                    suggested_source_type=SUGGESTED_SOURCE_TYPE[evidence_type],
                    source_guidance=SOURCE_GUIDANCE[evidence_type],
                    fields_to_verify=FIELDS_TO_VERIFY[evidence_type],
                    manual_verification_required=True,
                    auto_verified=False,
                )
            )
            if config.create_source_config_templates:
                templates.append(_source_template(asset_id, evidence_type))

    for item in queue.reviewed_candidates:
        if item.sleeve == "global_core" and item.asset_id not in skipped and item.asset_id in DEFAULT_TARGET_CANDIDATES + ("vwce_global_core_candidate",):
            skipped.append(item.asset_id)

    by_type: dict[str, int] = {}
    for task in tasks:
        by_type[task.evidence_type] = by_type.get(task.evidence_type, 0) + 1
    return GlobalCoreEvidenceBatch(
        batch_status="READY" if tasks and not blockers else "BLOCKED" if blockers else "NO_TARGETS",
        target_candidates=tuple(target_candidates),
        already_reviewed_skipped=tuple(sorted(dict.fromkeys(skipped))),
        tasks=tuple(tasks),
        source_config_templates=tuple(templates),
        tasks_by_evidence_type=dict(sorted(by_type.items())),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_global_core_evidence_batch_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
) -> GlobalCoreEvidenceBatch:
    return build_global_core_evidence_batch(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        load_global_core_evidence_batch_config(batch_config_path),
    )
