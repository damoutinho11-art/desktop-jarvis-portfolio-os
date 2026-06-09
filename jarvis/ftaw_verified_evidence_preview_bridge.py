"""Preview bridge from FTAW manual decisions to verified evidence previews.

This is a preview layer only. It does not write to the verified evidence store,
promote evidence, approve assets, mutate registries, recommend allocations,
create orders, or trade.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_identity_guarded_verification_queue import (
    FTAWIdentityGuardedVerificationQueue,
    FTAWIdentityGuardedVerificationQueueItem,
    build_ftaw_identity_guarded_verification_queue_from_files,
)
from .ftaw_manual_verification_decision_recorder import (
    FTAWManualVerificationDecisionPack,
    build_ftaw_manual_verification_decision_pack,
    load_ftaw_manual_verification_decision_config,
)


@dataclass(frozen=True)
class FTAWVerifiedEvidencePreviewRecord:
    asset_id: str
    evidence_type: str
    source_name: str
    source_quality: str
    extracted_facts: dict[str, object]
    manual_decision_id: str
    queue_item_reference: str
    manual_decision: str | None
    preview_status: str
    reason: str
    verified_by_user: bool = False
    verified_evidence_preview: bool = False
    no_verified_evidence_promotion: bool = True
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


@dataclass(frozen=True)
class FTAWVerifiedEvidencePreviewBridgePack:
    preview_bridge_status: str
    target_asset: str
    total_queue_items: int
    eligible_queue_items: int
    decision_records_count: int
    preview_ready_count: int
    excluded_rejected_count: int
    excluded_needs_correction_count: int
    pending_manual_decision_count: int
    blocked_invalid_manual_decision_count: int
    blocked_unknown_queue_item_count: int
    blocked_non_eligible_queue_item_count: int
    preview_records: tuple[FTAWVerifiedEvidencePreviewRecord, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    no_verified_evidence_promotion: bool = True
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _queue_item_id(item: FTAWIdentityGuardedVerificationQueueItem) -> str:
    return f"{item.asset_id}:{item.evidence_type}"


def _asset_id_from_queue_item_id(queue_item_id: str) -> str:
    return queue_item_id.split(":", 1)[0] if ":" in queue_item_id else "unknown"


def _record_for_result(result, item: FTAWIdentityGuardedVerificationQueueItem | None) -> FTAWVerifiedEvidencePreviewRecord:
    status_by_decision = {
        "accepted_for_verified_evidence_preview": "preview_ready",
        "rejected": "excluded_rejected",
        "needs_correction": "excluded_needs_correction",
        "pending_manual_decision": "pending_manual_decision",
        "blocked_invalid_manual_decision": "blocked_invalid_manual_decision",
        "blocked_unknown_queue_item": "blocked_unknown_queue_item",
        "blocked_non_eligible_queue_item": "blocked_non_eligible_queue_item",
    }
    preview_status = status_by_decision.get(result.decision_status, result.decision_status)
    source_name = item.source_name if item is not None else result.source_name
    source_quality = item.source_quality if item is not None else "unknown"
    facts = dict(getattr(item, "extracted_facts", {})) if item is not None else {}
    asset_id = item.asset_id if item is not None else _asset_id_from_queue_item_id(result.queue_item_id)
    evidence_type = item.evidence_type if item is not None else result.evidence_type
    return FTAWVerifiedEvidencePreviewRecord(
        asset_id=asset_id,
        evidence_type=evidence_type,
        source_name=source_name,
        source_quality=source_quality,
        extracted_facts=facts,
        manual_decision_id=result.queue_item_id,
        queue_item_reference=result.queue_item_id,
        manual_decision=result.manual_decision,
        preview_status=preview_status,
        reason=result.reason,
        verified_by_user=False,
        verified_evidence_preview=preview_status == "preview_ready",
        no_verified_evidence_promotion=True,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_verified_evidence_preview_bridge(
    queue: FTAWIdentityGuardedVerificationQueue,
    decisions: FTAWManualVerificationDecisionPack,
) -> FTAWVerifiedEvidencePreviewBridgePack:
    items_by_id = {_queue_item_id(item): item for item in queue.items}
    preview_records = tuple(_record_for_result(result, items_by_id.get(result.queue_item_id)) for result in decisions.decision_results)
    preview_ready = sum(record.preview_status == "preview_ready" for record in preview_records)
    rejected = sum(record.preview_status == "excluded_rejected" for record in preview_records)
    correction = sum(record.preview_status == "excluded_needs_correction" for record in preview_records)
    pending = sum(record.preview_status == "pending_manual_decision" for record in preview_records)
    invalid = sum(record.preview_status == "blocked_invalid_manual_decision" for record in preview_records)
    unknown = sum(record.preview_status == "blocked_unknown_queue_item" for record in preview_records)
    non_eligible = sum(record.preview_status == "blocked_non_eligible_queue_item" for record in preview_records)
    if invalid or unknown or non_eligible:
        status = "BLOCKED"
    elif pending:
        status = "PENDING_MANUAL_DECISION"
    elif preview_ready:
        status = "PREVIEW_READY"
    elif preview_records:
        status = "NO_PREVIEW_READY_RECORDS"
    else:
        status = "NO_DECISIONS"
    return FTAWVerifiedEvidencePreviewBridgePack(
        preview_bridge_status=status,
        target_asset=queue.target_asset_id,
        total_queue_items=queue.total_input_items,
        eligible_queue_items=queue.eligible_for_manual_verification_count,
        decision_records_count=len(decisions.decision_results),
        preview_ready_count=preview_ready,
        excluded_rejected_count=rejected,
        excluded_needs_correction_count=correction,
        pending_manual_decision_count=pending,
        blocked_invalid_manual_decision_count=invalid,
        blocked_unknown_queue_item_count=unknown,
        blocked_non_eligible_queue_item_count=non_eligible,
        preview_records=preview_records,
        warnings=decisions.warnings,
        blockers=decisions.blockers,
        no_verified_evidence_promotion=True,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_verified_evidence_preview_bridge_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
    bridge_config_path: str | Path,
) -> FTAWVerifiedEvidencePreviewBridgePack:
    Path(bridge_config_path).read_text(encoding="utf-8")
    queue = build_ftaw_identity_guarded_verification_queue_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
    )
    decisions = build_ftaw_manual_verification_decision_pack(
        queue,
        load_ftaw_manual_verification_decision_config(decision_config_path),
        queue_config_path,
        decision_config_path,
    )
    return build_ftaw_verified_evidence_preview_bridge(queue, decisions)
