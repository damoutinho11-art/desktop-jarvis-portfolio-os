"""Manual decision recorder for FTAW identity-guarded queue items.

This layer records human-authored decisions about queue items that are already
eligible for manual verification. It does not create verified evidence, approve
assets, mutate registries, recommend allocations, create orders, or trade.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ftaw_identity_guarded_verification_queue import (
    FTAWIdentityGuardedVerificationQueue,
    FTAWIdentityGuardedVerificationQueueItem,
    build_ftaw_identity_guarded_verification_queue_from_files,
)


ALLOWED_MANUAL_DECISIONS = {
    "accept_for_verified_evidence_preview",
    "reject",
    "needs_correction",
}


@dataclass(frozen=True)
class FTAWManualVerificationDecision:
    queue_item_id: str
    manual_decision: str
    reviewer_notes: str


@dataclass(frozen=True)
class FTAWManualVerificationDecisionConfig:
    decisions: tuple[FTAWManualVerificationDecision, ...]


@dataclass(frozen=True)
class FTAWManualVerificationDecisionResult:
    queue_item_id: str
    evidence_type: str
    source_name: str
    queue_status: str
    manual_decision: str | None
    decision_status: str
    reason: str
    verified_by_user: bool = False


@dataclass(frozen=True)
class FTAWManualVerificationDecisionPack:
    decision_pack_status: str
    target_asset: str
    queue_config_used: str
    decision_file_used: str
    total_queue_items: int
    eligible_queue_items: int
    accepted_for_verified_evidence_preview_count: int
    rejected_count: int
    needs_correction_count: int
    pending_manual_decision_count: int
    blocked_unknown_queue_item_count: int
    blocked_non_eligible_queue_item_count: int
    blocked_invalid_manual_decision_count: int
    preview_ready_item_ids: tuple[str, ...]
    decision_results: tuple[FTAWManualVerificationDecisionResult, ...]
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


def _queue_item_id(item: FTAWIdentityGuardedVerificationQueueItem) -> str:
    return f"{item.asset_id}:{item.evidence_type}"


def _parse_decision(raw: Any) -> FTAWManualVerificationDecision:
    item = _require_mapping(raw, "manual decision")
    return FTAWManualVerificationDecision(
        queue_item_id=_require_text(item.get("queue_item_id"), "queue_item_id"),
        manual_decision=_require_text(item.get("manual_decision"), "manual_decision"),
        reviewer_notes=_require_text(item.get("reviewer_notes", "Manual decision recorded."), "reviewer_notes"),
    )


def load_ftaw_manual_verification_decision_config(path: str | Path) -> FTAWManualVerificationDecisionConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "FTAW manual verification decision config")
    decisions = raw.get("decisions")
    if not isinstance(decisions, list):
        raise ValueError("decisions must be a list.")
    return FTAWManualVerificationDecisionConfig(decisions=tuple(_parse_decision(item) for item in decisions))


def build_ftaw_manual_verification_decision_pack(
    queue: FTAWIdentityGuardedVerificationQueue,
    decision_config: FTAWManualVerificationDecisionConfig,
    queue_config_used: str | Path,
    decision_file_used: str | Path,
) -> FTAWManualVerificationDecisionPack:
    items_by_id = {_queue_item_id(item): item for item in queue.items}
    decisions_by_id = {decision.queue_item_id: decision for decision in decision_config.decisions}
    results: list[FTAWManualVerificationDecisionResult] = []
    blockers: list[str] = []
    warnings: list[str] = []
    preview_ready: list[str] = []

    for decision in decision_config.decisions:
        item = items_by_id.get(decision.queue_item_id)
        if item is None:
            blockers.append(f"{decision.queue_item_id}: unknown queue item.")
            results.append(
                FTAWManualVerificationDecisionResult(
                    queue_item_id=decision.queue_item_id,
                    evidence_type="unknown",
                    source_name="unknown",
                    queue_status="unknown",
                    manual_decision=decision.manual_decision,
                    decision_status="blocked_unknown_queue_item",
                    reason="Decision references an unknown queue item.",
                    verified_by_user=False,
                )
            )
            continue
        if decision.manual_decision not in ALLOWED_MANUAL_DECISIONS:
            blockers.append(f"{decision.queue_item_id}: invalid manual decision {decision.manual_decision}.")
            results.append(
                FTAWManualVerificationDecisionResult(
                    queue_item_id=decision.queue_item_id,
                    evidence_type=item.evidence_type,
                    source_name=item.source_name,
                    queue_status=item.queue_status,
                    manual_decision=decision.manual_decision,
                    decision_status="blocked_invalid_manual_decision",
                    reason="Manual decision is not in the allowed list.",
                    verified_by_user=False,
                )
            )
            continue
        if item.queue_status != "eligible_for_manual_verification":
            blockers.append(f"{decision.queue_item_id}: queue item is not eligible for manual verification.")
            results.append(
                FTAWManualVerificationDecisionResult(
                    queue_item_id=decision.queue_item_id,
                    evidence_type=item.evidence_type,
                    source_name=item.source_name,
                    queue_status=item.queue_status,
                    manual_decision=decision.manual_decision,
                    decision_status="blocked_non_eligible_queue_item",
                    reason="Decision references a non-eligible queue item.",
                    verified_by_user=False,
                )
            )
            continue
        if decision.manual_decision == "accept_for_verified_evidence_preview":
            preview_ready.append(decision.queue_item_id)
            status = "accepted_for_verified_evidence_preview"
            reason = "Manual accept recorded for a future verified evidence preview layer only."
        elif decision.manual_decision == "reject":
            status = "rejected"
            reason = "Manual reject recorded; source facts remain unchanged."
        else:
            status = "needs_correction"
            reason = "Manual needs-correction recorded; item remains out of preview-ready items."
        results.append(
            FTAWManualVerificationDecisionResult(
                queue_item_id=decision.queue_item_id,
                evidence_type=item.evidence_type,
                source_name=item.source_name,
                queue_status=item.queue_status,
                manual_decision=decision.manual_decision,
                decision_status=status,
                reason=reason,
                verified_by_user=False,
            )
        )

    for item_id, item in sorted(items_by_id.items()):
        if item.queue_status == "eligible_for_manual_verification" and item_id not in decisions_by_id:
            warnings.append(f"{item_id}: eligible queue item is pending a manual decision.")
            results.append(
                FTAWManualVerificationDecisionResult(
                    queue_item_id=item_id,
                    evidence_type=item.evidence_type,
                    source_name=item.source_name,
                    queue_status=item.queue_status,
                    manual_decision=None,
                    decision_status="pending_manual_decision",
                    reason="Eligible queue item has no human-authored decision.",
                    verified_by_user=False,
                )
            )

    accepted_count = sum(result.decision_status == "accepted_for_verified_evidence_preview" for result in results)
    rejected_count = sum(result.decision_status == "rejected" for result in results)
    correction_count = sum(result.decision_status == "needs_correction" for result in results)
    pending_count = sum(result.decision_status == "pending_manual_decision" for result in results)
    unknown_count = sum(result.decision_status == "blocked_unknown_queue_item" for result in results)
    non_eligible_count = sum(result.decision_status == "blocked_non_eligible_queue_item" for result in results)
    invalid_count = sum(result.decision_status == "blocked_invalid_manual_decision" for result in results)
    if unknown_count or non_eligible_count or invalid_count:
        status = "BLOCKED"
    elif pending_count:
        status = "PENDING_MANUAL_DECISION"
    elif accepted_count or rejected_count or correction_count:
        status = "DECISIONS_RECORDED"
    else:
        status = "NO_DECISIONS"
    return FTAWManualVerificationDecisionPack(
        decision_pack_status=status,
        target_asset=queue.target_asset_id,
        queue_config_used=str(queue_config_used),
        decision_file_used=str(decision_file_used),
        total_queue_items=queue.total_input_items,
        eligible_queue_items=queue.eligible_for_manual_verification_count,
        accepted_for_verified_evidence_preview_count=accepted_count,
        rejected_count=rejected_count,
        needs_correction_count=correction_count,
        pending_manual_decision_count=pending_count,
        blocked_unknown_queue_item_count=unknown_count,
        blocked_non_eligible_queue_item_count=non_eligible_count,
        blocked_invalid_manual_decision_count=invalid_count,
        preview_ready_item_ids=tuple(preview_ready),
        decision_results=tuple(results),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_manual_verification_decision_pack_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
) -> FTAWManualVerificationDecisionPack:
    queue = build_ftaw_identity_guarded_verification_queue_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
    )
    return build_ftaw_manual_verification_decision_pack(
        queue,
        load_ftaw_manual_verification_decision_config(decision_config_path),
        queue_config_path,
        decision_config_path,
    )
