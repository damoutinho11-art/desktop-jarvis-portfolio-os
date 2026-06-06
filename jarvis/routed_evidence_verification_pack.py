"""Focused verification pack for routed public draft evidence."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .asset_registry import AssetRegistry, load_asset_registry
from .evidence_verification_queue import (
    EvidenceVerificationDecision,
    EvidenceVerificationDecisionResult,
    EvidenceVerificationTask,
    apply_verification_decision,
)
from .public_draft_evidence_router import (
    build_public_draft_evidence_router_pack,
    routed_records_to_verification_tasks,
)


SOURCE_QUALITY_PRIORITY = {
    "fund_metadata": ("provider_factsheet",),
    "fee_metadata": ("provider_factsheet",),
    "distribution_policy": ("provider_factsheet",),
    "exposure_data": ("provider_factsheet",),
    "platform_availability": ("platform_screenshot",),
    "market_data": ("verified_api_snapshot", "manual_research"),
    "tax_route": ("manual_research",),
}
SOURCE_NAME_PRIORITY = {
    "fund_metadata": ("product", "factsheet"),
    "fee_metadata": ("factsheet", "product"),
    "distribution_policy": ("product", "factsheet"),
    "platform_availability": ("platform",),
    "market_data": ("market",),
    "exposure_data": ("exposure",),
    "tax_route": ("tax route", "tax"),
}


@dataclass(frozen=True)
class VerificationDecisionOverride:
    evidence_type: str
    decision: str
    decided_at: str
    decided_by: str
    notes: str


@dataclass(frozen=True)
class RoutedEvidenceVerificationConfig:
    target_asset_id: str
    required_evidence_types: tuple[str, ...]
    decision_overrides: tuple[VerificationDecisionOverride, ...]


@dataclass(frozen=True)
class RoutedEvidenceVerificationPack:
    verification_pack_status: str
    target_asset_id: str
    required_evidence_types: tuple[str, ...]
    pending_tasks: tuple[EvidenceVerificationTask, ...]
    missing_evidence_types: tuple[str, ...]
    selected_source_by_evidence_type: dict[str, str]
    decision_results: tuple[EvidenceVerificationDecisionResult, ...]
    accepted_previews: tuple[dict[str, object], ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
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


def _require_text_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list.")
    return tuple(_require_text(item, field) for item in value)


def _parse_decision_override(raw: dict[str, Any]) -> VerificationDecisionOverride:
    item = _require_mapping(raw, "decision override")
    return VerificationDecisionOverride(
        evidence_type=_require_text(item.get("evidence_type"), "evidence_type"),
        decision=_require_text(item.get("decision"), "decision"),
        decided_at=_require_text(item.get("decided_at"), "decided_at"),
        decided_by=_require_text(item.get("decided_by"), "decided_by"),
        notes=_require_text(item.get("notes"), "notes"),
    )


def load_routed_evidence_verification_config(path: str | Path) -> RoutedEvidenceVerificationConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "routed evidence verification pack config")
    overrides = raw.get("decision_overrides", [])
    if not isinstance(overrides, list):
        raise ValueError("decision_overrides must be a list when provided.")
    return RoutedEvidenceVerificationConfig(
        target_asset_id=_require_text(raw.get("target_asset_id", "vwce_global_core_candidate"), "target_asset_id"),
        required_evidence_types=_require_text_list(raw.get("required_evidence_types"), "required_evidence_types"),
        decision_overrides=tuple(_parse_decision_override(override) for override in overrides),
    )


def _quality_rank(evidence_type: str, source_quality: str) -> int:
    preferred = SOURCE_QUALITY_PRIORITY.get(evidence_type, ())
    if source_quality in preferred:
        return preferred.index(source_quality)
    return len(preferred) + 1


def _source_name_rank(evidence_type: str, source_name: str) -> int:
    preferred = SOURCE_NAME_PRIORITY.get(evidence_type, ())
    normalized = source_name.lower()
    for index, token in enumerate(preferred):
        if token in normalized:
            return index
    return len(preferred) + 1


def select_best_routed_record(records: tuple[dict[str, object], ...] | list[dict[str, object]], evidence_type: str) -> dict[str, object] | None:
    candidates = [record for record in records if record.get("evidence_type") == evidence_type]
    if not candidates:
        return None
    return sorted(
        candidates,
        key=lambda record: (
            _quality_rank(evidence_type, str(record.get("source_quality", ""))),
            _source_name_rank(evidence_type, str(record.get("source_name", ""))),
            str(record.get("evidence_id", "")),
        ),
    )[0]


def _decision_for_task(task: EvidenceVerificationTask, override: VerificationDecisionOverride) -> EvidenceVerificationDecision:
    return EvidenceVerificationDecision(
        task_id=task.task_id,
        decision=override.decision,
        decided_at=override.decided_at,
        decided_by=override.decided_by,
        notes=override.notes,
    )


def build_routed_evidence_verification_pack(
    registry_path: str | Path | AssetRegistry,
    public_sources_path: str | Path,
    config: RoutedEvidenceVerificationConfig,
) -> RoutedEvidenceVerificationPack:
    registry = load_asset_registry(registry_path) if not isinstance(registry_path, AssetRegistry) else registry_path
    blockers: list[str] = []
    if config.target_asset_id not in registry.by_id():
        blockers.append(f"{config.target_asset_id}: target asset not found in registry.")

    router_pack = build_public_draft_evidence_router_pack(registry, public_sources_path)
    routed_records = [
        record
        for route in router_pack.route_results
        for record in route.routed_evidence_records
        if record.get("asset_id") == config.target_asset_id
    ]

    selected_records: list[dict[str, object]] = []
    missing: list[str] = []
    selected_sources: dict[str, str] = {}
    for evidence_type in config.required_evidence_types:
        record = select_best_routed_record(routed_records, evidence_type)
        if record is None:
            missing.append(evidence_type)
            continue
        selected_records.append(record)
        selected_sources[evidence_type] = str(record.get("source_name", "unknown source"))

    tasks = routed_records_to_verification_tasks(selected_records)
    tasks_by_type = {task.evidence_type: task for task in tasks}
    decision_results: list[EvidenceVerificationDecisionResult] = []
    accepted_previews: list[dict[str, object]] = []
    for override in config.decision_overrides:
        task = tasks_by_type.get(override.evidence_type)
        if task is None:
            blockers.append(f"{override.evidence_type}: no pending task exists for decision override.")
            continue
        result = apply_verification_decision(task, _decision_for_task(task, override))
        decision_results.append(result)
        if result.verified_evidence_preview is not None:
            accepted_previews.append(result.verified_evidence_preview)
        blockers.extend(result.blockers)

    warnings = tuple(
        dict.fromkeys(
            [warning for task in tasks for warning in task.warnings]
            + [warning for result in decision_results for warning in result.warnings]
        )
    )
    status = "BLOCKED" if blockers else "INCOMPLETE" if missing else "PENDING_MANUAL_VERIFICATION"
    return RoutedEvidenceVerificationPack(
        verification_pack_status=status,
        target_asset_id=config.target_asset_id,
        required_evidence_types=config.required_evidence_types,
        pending_tasks=tasks,
        missing_evidence_types=tuple(missing),
        selected_source_by_evidence_type=dict(sorted(selected_sources.items())),
        decision_results=tuple(decision_results),
        accepted_previews=tuple(accepted_previews),
        warnings=warnings,
        blockers=tuple(dict.fromkeys(blockers)),
        approvals_created=False,
        registry_mutation_allowed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_routed_evidence_verification_pack_from_files(
    registry_path: str | Path,
    public_sources_path: str | Path,
    config_path: str | Path,
) -> RoutedEvidenceVerificationPack:
    return build_routed_evidence_verification_pack(
        registry_path,
        public_sources_path,
        load_routed_evidence_verification_config(config_path),
    )


def write_accepted_previews(pack: RoutedEvidenceVerificationPack, path: str | Path) -> Path:
    if not pack.accepted_previews:
        raise ValueError("no accepted previews available to write.")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"records": list(pack.accepted_previews)}, indent=2, sort_keys=True), encoding="utf-8")
    return target
