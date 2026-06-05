"""Promotion pack for accepted evidence verification decisions."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .asset_registry import AssetRegistry, load_asset_registry
from .evidence_provenance import EvidenceProvenanceRecord, classify_evidence_readiness
from .evidence_verification_queue import (
    EvidenceVerificationDecision,
    EvidenceVerificationTask,
    apply_verification_decision,
    build_evidence_verification_queue,
)


@dataclass(frozen=True)
class EvidencePromotionDecisionInput:
    task_id: str
    decision: str
    decided_at: str
    decided_by: str
    notes: str


@dataclass(frozen=True)
class EvidencePromotionPack:
    promotion_pack_status: str
    total_tasks: int
    accepted_count: int
    rejected_count: int
    needs_correction_count: int
    verified_evidence_preview_count: int
    verified_evidence_previews: tuple[dict[str, object], ...]
    provenance_gate_results: tuple[dict[str, object], ...]
    assets_ready_for_real_status_review: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
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


def parse_promotion_decision(raw: dict[str, Any]) -> EvidencePromotionDecisionInput:
    item = _require_mapping(raw, "promotion decision")
    return EvidencePromotionDecisionInput(
        task_id=_require_text(item.get("task_id"), "task_id"),
        decision=_require_text(item.get("decision"), "decision"),
        decided_at=_require_text(item.get("decided_at"), "decided_at"),
        decided_by=_require_text(item.get("decided_by"), "decided_by"),
        notes=_require_text(item.get("notes"), "notes"),
    )


def load_promotion_decisions(path: str | Path) -> tuple[EvidencePromotionDecisionInput, ...]:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "verified evidence promotion")
    decisions = raw.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("verified evidence promotion file must contain a decisions list.")
    return tuple(parse_promotion_decision(decision) for decision in decisions)


def _decision_to_queue_decision(decision: EvidencePromotionDecisionInput) -> EvidenceVerificationDecision:
    return EvidenceVerificationDecision(
        task_id=decision.task_id,
        decision=decision.decision,
        decided_at=decision.decided_at,
        decided_by=decision.decided_by,
        notes=decision.notes,
    )


def _preview_to_provenance(preview: dict[str, object]) -> EvidenceProvenanceRecord:
    evidence_type = str(preview["evidence_type"])
    if evidence_type in {"protocol_metadata", "fee_metadata"}:
        evidence_type = "fund_metadata"
    if evidence_type == "distribution_policy":
        evidence_type = "tax_route"
    return EvidenceProvenanceRecord(
        asset_id=str(preview["asset_id"]),
        evidence_type=evidence_type,
        source_quality=str(preview["source_quality"]),
        source_name=str(preview["source_name"]),
        as_of=str(preview["as_of"]),
        verified_by_user=bool(preview["verified_by_user"]),
        notes=str(preview["verification_notes"]),
    )


def build_verified_evidence_promotion_pack(
    registry_path: str | Path | AssetRegistry,
    sources_path: str | Path,
    decisions: tuple[EvidencePromotionDecisionInput, ...] | list[EvidencePromotionDecisionInput],
) -> EvidencePromotionPack:
    registry = load_asset_registry(registry_path) if not isinstance(registry_path, AssetRegistry) else registry_path
    queue = build_evidence_verification_queue(registry, sources_path)
    tasks_by_id: dict[str, EvidenceVerificationTask] = {task.task_id: task for task in queue.tasks}
    blockers: list[str] = []
    warnings: list[str] = list(queue.warnings)
    previews: list[dict[str, object]] = []
    accepted = rejected = needs_correction = 0
    for decision in decisions:
        task = tasks_by_id.get(decision.task_id)
        if task is None:
            blockers.append(f"{decision.task_id}: no matching verification task.")
            continue
        result = apply_verification_decision(task, _decision_to_queue_decision(decision))
        blockers.extend(result.blockers)
        warnings.extend(result.warnings)
        if decision.decision == "accept" and result.verified_evidence_preview is not None:
            accepted += 1
            previews.append(result.verified_evidence_preview)
        elif decision.decision == "reject":
            rejected += 1
        elif decision.decision == "needs_correction":
            needs_correction += 1

    provenance_records = tuple(_preview_to_provenance(preview) for preview in previews)
    gates_by_id = classify_evidence_readiness(provenance_records, registry.by_id())
    gate_results = tuple(gates_by_id[asset.asset_id] for asset in registry.assets)
    ready_assets = tuple(result.asset_id for result in gate_results if result.real_status_promotion_allowed)
    blockers.extend(blocker for result in gate_results for blocker in result.blockers)
    warnings.extend(warning for result in gate_results for warning in result.warnings)
    return EvidencePromotionPack(
        promotion_pack_status="READY_FOR_STATUS_REVIEW" if ready_assets else "INCOMPLETE",
        total_tasks=len(queue.tasks),
        accepted_count=accepted,
        rejected_count=rejected,
        needs_correction_count=needs_correction,
        verified_evidence_preview_count=len(previews),
        verified_evidence_previews=tuple(previews),
        provenance_gate_results=tuple(result.to_dict() for result in gate_results),
        assets_ready_for_real_status_review=ready_assets,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
        approvals_created=False,
        registry_mutation_allowed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_verified_evidence_promotion_pack_from_files(
    registry_path: str | Path,
    sources_path: str | Path,
    decisions_path: str | Path,
) -> EvidencePromotionPack:
    return build_verified_evidence_promotion_pack(registry_path, sources_path, load_promotion_decisions(decisions_path))


def write_verified_evidence_previews(pack: EvidencePromotionPack, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"records": list(pack.verified_evidence_previews)}, indent=2, sort_keys=True), encoding="utf-8")
    return target
