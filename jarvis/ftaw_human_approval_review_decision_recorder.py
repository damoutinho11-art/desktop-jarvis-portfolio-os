"""Human approval review decision recorder for FTAW review packets.

This layer records a human decision after the manual approval review gate is
ready. It does not approve assets, promote evidence, mutate registries,
recommend allocations, create orders, or trade.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ftaw_manual_approval_review_gate import (
    FTAWManualApprovalReviewGatePack,
    build_ftaw_manual_approval_review_gate_from_files,
)


ALLOWED_HUMAN_APPROVAL_REVIEW_DECISIONS = {
    "approved_for_registry_update_dry_run",
    "rejected",
    "needs_more_evidence",
}


@dataclass(frozen=True)
class FTAWHumanApprovalReviewDecision:
    review_packet_id: str
    asset_id: str
    human_decision: str
    reviewer_notes: str


@dataclass(frozen=True)
class FTAWHumanApprovalReviewDecisionConfig:
    decision: FTAWHumanApprovalReviewDecision | None


@dataclass(frozen=True)
class FTAWHumanApprovalReviewDecisionPack:
    decision_recorder_status: str
    target_asset: str
    gate_status: str
    review_packet_created: bool
    human_decision_file_used: str
    human_decision: str | None
    decision_status: str
    registry_update_dry_run_ready: bool
    rejected_count: int
    needs_more_evidence_count: int
    pending_decision_count: int
    blocked_reason_count: int
    blocked_reasons: tuple[str, ...]
    review_packet_id: str | None
    approved_asset: bool = False
    approval_status_change: bool = False
    no_verified_evidence_promotion: bool = True
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


def _review_packet_id(asset_id: str) -> str:
    return f"{asset_id}:manual_approval_review"


def _parse_decision(value: Any) -> FTAWHumanApprovalReviewDecision:
    raw = _require_mapping(value, "human approval review decision")
    return FTAWHumanApprovalReviewDecision(
        review_packet_id=_require_text(raw.get("review_packet_id"), "review_packet_id"),
        asset_id=_require_text(raw.get("asset_id"), "asset_id"),
        human_decision=_require_text(raw.get("human_decision"), "human_decision"),
        reviewer_notes=_require_text(raw.get("reviewer_notes", "Human approval review decision recorded."), "reviewer_notes"),
    )


def load_ftaw_human_approval_review_decision_config(path: str | Path) -> FTAWHumanApprovalReviewDecisionConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "FTAW human approval review decision config")
    decision = raw.get("decision")
    if decision is None:
        return FTAWHumanApprovalReviewDecisionConfig(decision=None)
    return FTAWHumanApprovalReviewDecisionConfig(decision=_parse_decision(decision))


def build_ftaw_human_approval_review_decision_pack(
    gate: FTAWManualApprovalReviewGatePack,
    decision_config: FTAWHumanApprovalReviewDecisionConfig,
    decision_file_used: str | Path,
) -> FTAWHumanApprovalReviewDecisionPack:
    expected_packet_id = _review_packet_id(gate.target_asset)
    decision = decision_config.decision
    blocked: list[str] = []

    if gate.approval_review_gate_status != "READY_FOR_HUMAN_APPROVAL_REVIEW":
        blocked.append(f"approval review gate status is {gate.approval_review_gate_status}.")
        return FTAWHumanApprovalReviewDecisionPack(
            decision_recorder_status="BLOCKED",
            target_asset=gate.target_asset,
            gate_status=gate.approval_review_gate_status,
            review_packet_created=gate.review_packet_created,
            human_decision_file_used=str(decision_file_used),
            human_decision=decision.human_decision if decision else None,
            decision_status="blocked_gate_not_ready",
            registry_update_dry_run_ready=False,
            rejected_count=0,
            needs_more_evidence_count=0,
            pending_decision_count=0,
            blocked_reason_count=1,
            blocked_reasons=tuple(blocked),
            review_packet_id=expected_packet_id if gate.review_packet_created else None,
        )
    if not gate.review_packet_created or gate.review_packet is None:
        blocked.append("review packet was not created.")
        return FTAWHumanApprovalReviewDecisionPack(
            decision_recorder_status="BLOCKED",
            target_asset=gate.target_asset,
            gate_status=gate.approval_review_gate_status,
            review_packet_created=gate.review_packet_created,
            human_decision_file_used=str(decision_file_used),
            human_decision=decision.human_decision if decision else None,
            decision_status="blocked_no_review_packet",
            registry_update_dry_run_ready=False,
            rejected_count=0,
            needs_more_evidence_count=0,
            pending_decision_count=0,
            blocked_reason_count=1,
            blocked_reasons=tuple(blocked),
            review_packet_id=None,
        )
    if decision is None:
        return FTAWHumanApprovalReviewDecisionPack(
            decision_recorder_status="PENDING_HUMAN_DECISION",
            target_asset=gate.target_asset,
            gate_status=gate.approval_review_gate_status,
            review_packet_created=gate.review_packet_created,
            human_decision_file_used=str(decision_file_used),
            human_decision=None,
            decision_status="pending_human_approval_review_decision",
            registry_update_dry_run_ready=False,
            rejected_count=0,
            needs_more_evidence_count=0,
            pending_decision_count=1,
            blocked_reason_count=0,
            blocked_reasons=(),
            review_packet_id=expected_packet_id,
        )
    if decision.review_packet_id != expected_packet_id:
        blocked.append(f"{decision.review_packet_id}: unknown review packet.")
        return FTAWHumanApprovalReviewDecisionPack(
            decision_recorder_status="BLOCKED",
            target_asset=gate.target_asset,
            gate_status=gate.approval_review_gate_status,
            review_packet_created=gate.review_packet_created,
            human_decision_file_used=str(decision_file_used),
            human_decision=decision.human_decision,
            decision_status="blocked_unknown_review_packet",
            registry_update_dry_run_ready=False,
            rejected_count=0,
            needs_more_evidence_count=0,
            pending_decision_count=0,
            blocked_reason_count=1,
            blocked_reasons=tuple(blocked),
            review_packet_id=expected_packet_id,
        )
    if decision.asset_id != gate.review_packet.asset_id:
        blocked.append(f"decision asset {decision.asset_id} does not match review packet asset {gate.review_packet.asset_id}.")
        return FTAWHumanApprovalReviewDecisionPack(
            decision_recorder_status="BLOCKED",
            target_asset=gate.target_asset,
            gate_status=gate.approval_review_gate_status,
            review_packet_created=gate.review_packet_created,
            human_decision_file_used=str(decision_file_used),
            human_decision=decision.human_decision,
            decision_status="blocked_asset_mismatch",
            registry_update_dry_run_ready=False,
            rejected_count=0,
            needs_more_evidence_count=0,
            pending_decision_count=0,
            blocked_reason_count=1,
            blocked_reasons=tuple(blocked),
            review_packet_id=expected_packet_id,
        )
    if decision.human_decision not in ALLOWED_HUMAN_APPROVAL_REVIEW_DECISIONS:
        blocked.append(f"{decision.human_decision}: invalid human approval review decision.")
        return FTAWHumanApprovalReviewDecisionPack(
            decision_recorder_status="BLOCKED",
            target_asset=gate.target_asset,
            gate_status=gate.approval_review_gate_status,
            review_packet_created=gate.review_packet_created,
            human_decision_file_used=str(decision_file_used),
            human_decision=decision.human_decision,
            decision_status="blocked_invalid_human_decision",
            registry_update_dry_run_ready=False,
            rejected_count=0,
            needs_more_evidence_count=0,
            pending_decision_count=0,
            blocked_reason_count=1,
            blocked_reasons=tuple(blocked),
            review_packet_id=expected_packet_id,
        )

    if decision.human_decision == "approved_for_registry_update_dry_run":
        status = "decision_recorded_for_registry_update_dry_run"
        dry_run_ready = True
        rejected_count = 0
        needs_more_evidence_count = 0
    elif decision.human_decision == "rejected":
        status = "decision_recorded_rejected"
        dry_run_ready = False
        rejected_count = 1
        needs_more_evidence_count = 0
    else:
        status = "decision_recorded_needs_more_evidence"
        dry_run_ready = False
        rejected_count = 0
        needs_more_evidence_count = 1

    return FTAWHumanApprovalReviewDecisionPack(
        decision_recorder_status="DECISION_RECORDED",
        target_asset=gate.target_asset,
        gate_status=gate.approval_review_gate_status,
        review_packet_created=gate.review_packet_created,
        human_decision_file_used=str(decision_file_used),
        human_decision=decision.human_decision,
        decision_status=status,
        registry_update_dry_run_ready=dry_run_ready,
        rejected_count=rejected_count,
        needs_more_evidence_count=needs_more_evidence_count,
        pending_decision_count=0,
        blocked_reason_count=0,
        blocked_reasons=(),
        review_packet_id=expected_packet_id,
        approved_asset=False,
        approval_status_change=False,
        no_verified_evidence_promotion=True,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_human_approval_review_decision_pack_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
    preview_bridge_config_path: str | Path,
    promotion_dry_run_config_path: str | Path,
    readiness_config_path: str | Path,
    approval_review_gate_config_path: str | Path,
    human_decision_config_path: str | Path,
) -> FTAWHumanApprovalReviewDecisionPack:
    gate = build_ftaw_manual_approval_review_gate_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
        approval_review_gate_config_path,
    )
    return build_ftaw_human_approval_review_decision_pack(
        gate,
        load_ftaw_human_approval_review_decision_config(human_decision_config_path),
        human_decision_config_path,
    )
