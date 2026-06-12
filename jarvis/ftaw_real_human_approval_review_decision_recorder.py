"""FTAW real human approval review decision recorder.

This read-only recorder consumes v4.44 real manual approval review gate output
and records a human approval review decision. It does not mutate registries,
approve assets, recommend allocations, create orders, trade, create an
executor, ingest private files, fetch sources, download sources, or extract
facts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .ftaw_real_manual_approval_review_gate import (
    FTAWRealManualApprovalReviewGatePack,
    build_ftaw_real_manual_approval_review_gate_from_files,
)


ALLOWED_REAL_HUMAN_APPROVAL_REVIEW_DECISIONS = (
    "approve_for_registry_update_dry_run",
    "reject",
    "needs_correction",
    "defer",
)


@dataclass(frozen=True)
class FTAWRealHumanApprovalReviewDecisionRecord:
    asset_id: str
    decision: str
    reviewed_by_user: bool
    user_asserted_manual_approval_review: bool
    user_asserted_no_registry_mutation: bool
    user_asserted_no_allocation_recommendation: bool
    user_asserted_no_buy_signal: bool
    user_asserted_no_trade: bool
    reviewer_notes: str
    decision_status: str
    decision_recorded: bool
    registry_update_dry_run_ready: bool
    approved_asset: bool = False
    approval_status_change: bool = False
    registry_mutation: bool = False
    allocation_recommendation: bool = False
    buy_signal: bool = False
    trade_executed: bool = False


@dataclass(frozen=True)
class FTAWRealHumanApprovalReviewDecisionRecorderPack:
    target_asset: str
    recorder_status: str
    upstream_v4_44_status: str
    decision: str
    decision_recorded: bool
    registry_update_dry_run_ready: bool
    decision_record: FTAWRealHumanApprovalReviewDecisionRecord | None
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    approved_asset: bool = False
    approval_status_change: bool = False
    registry_mutation: bool = False
    allocation_recommendation: bool = False
    buy_signal: bool = False
    trade_executed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    executor_created: bool = False
    evidence_verified: bool = False
    verified_evidence_promotion: bool = False
    private_file_auto_ingest: bool = False
    automatic_source_fetching: bool = False
    automatic_downloads: bool = False
    automatic_fact_extraction: bool = False


def _load_decision(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    decision = data.get("human_approval_review_decision", data)
    if decision is None:
        return {}
    if not isinstance(decision, dict):
        raise ValueError("human_approval_review_decision must be an object when present")
    return decision


def _build_record(gate: FTAWRealManualApprovalReviewGatePack, entry: dict) -> FTAWRealHumanApprovalReviewDecisionRecord:
    asset_id = str(entry.get("asset_id", ""))
    decision = str(entry.get("decision", ""))
    confirmations = (
        entry.get("reviewed_by_user") is True,
        entry.get("user_asserted_manual_approval_review") is True,
        entry.get("user_asserted_no_registry_mutation") is True,
        entry.get("user_asserted_no_allocation_recommendation") is True,
        entry.get("user_asserted_no_buy_signal") is True,
        entry.get("user_asserted_no_trade") is True,
    )

    if gate.approval_review_gate_status != "READY_FOR_REAL_HUMAN_APPROVAL_REVIEW" or not gate.approval_packet_created:
        status = "blocked_no_real_manual_approval_review_packet"
    elif asset_id != gate.target_asset:
        status = "blocked_asset_mismatch"
    elif decision not in ALLOWED_REAL_HUMAN_APPROVAL_REVIEW_DECISIONS:
        status = "blocked_invalid_human_approval_review_decision"
    elif not all(confirmations):
        status = "blocked_missing_user_confirmation"
    elif decision == "approve_for_registry_update_dry_run":
        status = "decision_recorded_for_registry_update_dry_run"
    elif decision == "reject":
        status = "decision_recorded_rejected"
    elif decision == "needs_correction":
        status = "decision_recorded_needs_correction"
    else:
        status = "decision_recorded_deferred"

    return FTAWRealHumanApprovalReviewDecisionRecord(
        asset_id=asset_id,
        decision=decision,
        reviewed_by_user=entry.get("reviewed_by_user") is True,
        user_asserted_manual_approval_review=entry.get("user_asserted_manual_approval_review") is True,
        user_asserted_no_registry_mutation=entry.get("user_asserted_no_registry_mutation") is True,
        user_asserted_no_allocation_recommendation=entry.get("user_asserted_no_allocation_recommendation") is True,
        user_asserted_no_buy_signal=entry.get("user_asserted_no_buy_signal") is True,
        user_asserted_no_trade=entry.get("user_asserted_no_trade") is True,
        reviewer_notes=str(entry.get("reviewer_notes", "")),
        decision_status=status,
        decision_recorded=status in {
            "decision_recorded_for_registry_update_dry_run",
            "decision_recorded_rejected",
            "decision_recorded_needs_correction",
            "decision_recorded_deferred",
        },
        registry_update_dry_run_ready=status == "decision_recorded_for_registry_update_dry_run",
        approved_asset=False,
        approval_status_change=False,
        registry_mutation=False,
        allocation_recommendation=False,
        buy_signal=False,
        trade_executed=False,
    )


def build_ftaw_real_human_approval_review_decision_recorder(
    gate: FTAWRealManualApprovalReviewGatePack,
    decision_entry: dict,
) -> FTAWRealHumanApprovalReviewDecisionRecorderPack:
    record = _build_record(gate, decision_entry) if decision_entry else None
    blocked: list[str] = []
    if gate.approval_review_gate_status != "READY_FOR_REAL_HUMAN_APPROVAL_REVIEW" or not gate.approval_packet_created:
        blocked.append(f"approval review gate status is {gate.approval_review_gate_status}.")
    if record is None:
        blocked.append("human approval review decision is missing.")
    elif record.decision_status.startswith("blocked_"):
        blocked.append(f"human approval review decision blocked: {record.decision_status}.")
    elif record.decision_status == "decision_recorded_rejected":
        blocked.append("human approval review decision is reject.")
    elif record.decision_status == "decision_recorded_needs_correction":
        blocked.append("human approval review decision needs correction.")
    elif record.decision_status == "decision_recorded_deferred":
        blocked.append("human approval review decision is deferred.")
    blocked.extend(gate.blocked_reasons)

    if gate.approval_review_gate_status == "BLOCKED_NO_REAL_CANDIDATE_READINESS_REVIEW" and record is None:
        status = "BLOCKED_NO_REAL_MANUAL_APPROVAL_REVIEW_PACKET"
        next_action = "Resolve v4.44 manual approval review gate readiness before recording a human decision."
    elif record is not None and record.decision_status == "decision_recorded_deferred":
        status = "REAL_HUMAN_APPROVAL_REVIEW_DEFERRED"
        next_action = "Human deferred approval review; no registry dry-run readiness was unlocked."
    elif record is not None and record.decision_status == "decision_recorded_for_registry_update_dry_run" and not blocked:
        status = "REAL_HUMAN_APPROVAL_REVIEW_DECISION_RECORDED_FOR_REGISTRY_DRY_RUN"
        next_action = "A future registry update dry-run may inspect this decision; no registry mutation occurred."
    else:
        status = "PARTIAL_REAL_HUMAN_APPROVAL_REVIEW_DECISION_RECORDED"
        next_action = "Resolve decision blockers before future registry update dry-run review."

    return FTAWRealHumanApprovalReviewDecisionRecorderPack(
        target_asset=gate.target_asset,
        recorder_status=status,
        upstream_v4_44_status=gate.approval_review_gate_status,
        decision=record.decision if record is not None else "none",
        decision_recorded=record.decision_recorded if record is not None else False,
        registry_update_dry_run_ready=record.registry_update_dry_run_ready if record is not None and not blocked else False,
        decision_record=record,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        approved_asset=False,
        approval_status_change=False,
        registry_mutation=False,
        allocation_recommendation=False,
        buy_signal=False,
        trade_executed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
        executor_created=False,
        evidence_verified=False,
        verified_evidence_promotion=False,
        private_file_auto_ingest=False,
        automatic_source_fetching=False,
        automatic_downloads=False,
        automatic_fact_extraction=False,
    )


def build_ftaw_real_human_approval_review_decision_recorder_from_files(
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
    registry_update_dry_run_config_path: str | Path,
    registry_update_apply_gate_config_path: str | Path,
    explicit_manual_apply_command_config_path: str | Path,
    execution_review_config_path: str | Path,
    full_pipeline_audit_config_path: str | Path,
    real_evidence_intake_readiness_config_path: str | Path,
    collection_checklist_config_path: str | Path,
    public_source_reference_plan_config_path: str | Path,
    manual_public_source_reference_entry_config_path: str | Path,
    manual_source_fact_entry_config_path: str | Path,
    identity_guard_bridge_config_path: str | Path,
    identity_guard_review_decision_config_path: str | Path,
    identity_guard_submission_dry_run_config_path: str | Path,
    identity_guard_submission_review_gate_config_path: str | Path,
    explicit_manual_identity_guard_submission_command_config_path: str | Path,
    identity_guard_submission_execution_review_config_path: str | Path,
    manual_identity_guard_result_recorder_config_path: str | Path,
    real_identity_guarded_verification_queue_dry_run_bridge_config_path: str | Path,
    real_manual_verification_decision_recorder_config_path: str | Path,
    real_verified_evidence_preview_bridge_config_path: str | Path,
    real_verified_evidence_promotion_dry_run_pack_config_path: str | Path,
    real_candidate_readiness_review_pack_config_path: str | Path,
    real_manual_approval_review_gate_config_path: str | Path,
    real_human_approval_review_decision_recorder_config_path: str | Path,
) -> FTAWRealHumanApprovalReviewDecisionRecorderPack:
    gate = build_ftaw_real_manual_approval_review_gate_from_files(
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
        human_decision_config_path,
        registry_update_dry_run_config_path,
        registry_update_apply_gate_config_path,
        explicit_manual_apply_command_config_path,
        execution_review_config_path,
        full_pipeline_audit_config_path,
        real_evidence_intake_readiness_config_path,
        collection_checklist_config_path,
        public_source_reference_plan_config_path,
        manual_public_source_reference_entry_config_path,
        manual_source_fact_entry_config_path,
        identity_guard_bridge_config_path,
        identity_guard_review_decision_config_path,
        identity_guard_submission_dry_run_config_path,
        identity_guard_submission_review_gate_config_path,
        explicit_manual_identity_guard_submission_command_config_path,
        identity_guard_submission_execution_review_config_path,
        manual_identity_guard_result_recorder_config_path,
        real_identity_guarded_verification_queue_dry_run_bridge_config_path,
        real_manual_verification_decision_recorder_config_path,
        real_verified_evidence_preview_bridge_config_path,
        real_verified_evidence_promotion_dry_run_pack_config_path,
        real_candidate_readiness_review_pack_config_path,
        real_manual_approval_review_gate_config_path,
    )
    return build_ftaw_real_human_approval_review_decision_recorder(
        gate,
        _load_decision(real_human_approval_review_decision_recorder_config_path),
    )
