"""FTAW real verified evidence preview bridge.

This read-only bridge consumes v4.40 accepted manual verification decisions
and creates verified-evidence preview records for a later promotion dry-run
review. It does not verify evidence, promote evidence, approve assets, mutate
registries, recommend allocations, create orders, trade, create an executor,
ingest private files, fetch sources, download sources, or extract facts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_real_manual_identity_guard_review_decision_recorder import PUBLIC_EVIDENCE_TYPES
from .ftaw_real_manual_verification_decision_recorder import (
    FTAWRealManualVerificationDecisionRecorderPack,
    FTAWRealManualVerificationDecisionRecord,
    build_ftaw_real_manual_verification_decision_recorder_from_files,
)


@dataclass(frozen=True)
class FTAWRealVerifiedEvidencePreviewRecord:
    asset_id: str
    evidence_type: str
    source_reference_id: str
    manual_verification_decision: str
    manual_decision_status: str
    preview_status: str
    preview_reason: str
    verified_evidence_preview: bool
    evidence_verified: bool = False
    verified_by_user: bool = False
    verified_evidence_promoted: bool = False
    approved_asset: bool = False
    registry_mutation: bool = False
    allocation_recommendation: bool = False
    buy_signal: bool = False
    trade_executed: bool = False


@dataclass(frozen=True)
class FTAWRealVerifiedEvidencePreviewBridgePack:
    target_asset: str
    preview_bridge_status: str
    upstream_v4_40_status: str
    accepted_decision_count: int
    preview_record_count: int
    missing_preview_count: int
    manual_private_outstanding_count: int
    preview_records: tuple[FTAWRealVerifiedEvidencePreviewRecord, ...]
    manual_private_outstanding: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    evidence_verified: bool = False
    verified_evidence_promotion: bool = False
    approvals_created: bool = False
    registry_mutation: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    executor_created: bool = False
    private_file_auto_ingest: bool = False
    automatic_source_fetching: bool = False
    automatic_downloads: bool = False
    automatic_fact_extraction: bool = False


def _preview_from_decision(
    target_asset: str,
    record: FTAWRealManualVerificationDecisionRecord,
) -> FTAWRealVerifiedEvidencePreviewRecord:
    preview_ready = record.decision_status == "accepted_for_verified_evidence_preview_review"
    return FTAWRealVerifiedEvidencePreviewRecord(
        asset_id=target_asset,
        evidence_type=record.evidence_type,
        source_reference_id=record.source_reference_id,
        manual_verification_decision=record.manual_verification_decision,
        manual_decision_status=record.decision_status,
        preview_status="preview_ready" if preview_ready else f"excluded_{record.manual_verification_decision}",
        preview_reason="accepted manual verification decision can be reviewed by a future promotion dry-run layer"
        if preview_ready
        else "manual decision was not accepted for verified evidence preview",
        verified_evidence_preview=preview_ready,
        evidence_verified=False,
        verified_by_user=False,
        verified_evidence_promoted=False,
        approved_asset=False,
        registry_mutation=False,
        allocation_recommendation=False,
        buy_signal=False,
        trade_executed=False,
    )


def build_ftaw_real_verified_evidence_preview_bridge(
    manual_decisions: FTAWRealManualVerificationDecisionRecorderPack,
) -> FTAWRealVerifiedEvidencePreviewBridgePack:
    accepted_records = tuple(
        sorted(
            (
                record
                for record in manual_decisions.decision_records
                if record.decision_status == "accepted_for_verified_evidence_preview_review"
            ),
            key=lambda item: (item.evidence_type, item.source_reference_id),
        )
    )
    preview_records = tuple(_preview_from_decision(manual_decisions.target_asset, record) for record in accepted_records)
    accepted_types = {record.evidence_type for record in accepted_records}
    missing_types = tuple(evidence_type for evidence_type in PUBLIC_EVIDENCE_TYPES if evidence_type not in accepted_types)

    blocked: list[str] = []
    if manual_decisions.decision_recorder_status != "MANUAL_VERIFICATION_DECISIONS_RECORDED_FOR_VERIFIED_EVIDENCE_PREVIEW_REVIEW":
        blocked.append(f"manual verification decision recorder status is {manual_decisions.decision_recorder_status}.")
    blocked.extend(f"missing accepted manual verification preview decision for {evidence_type}" for evidence_type in missing_types)
    for record in manual_decisions.decision_records:
        if record.evidence_type in PUBLIC_EVIDENCE_TYPES and record.decision_status in {
            "manual_verification_rejected",
            "manual_verification_needs_correction",
        }:
            blocked.append(f"{record.evidence_type} decision excluded: {record.decision_status}.")
        elif record.decision_status.startswith("blocked_"):
            blocked.append(f"{record.evidence_type or 'unknown'} decision blocked: {record.decision_status}.")
    blocked.extend(manual_decisions.blocked_reasons)

    if manual_decisions.decision_recorder_status == "BLOCKED_NO_VERIFICATION_QUEUE_DRY_RUN" and not preview_records:
        status = "BLOCKED_NO_MANUAL_VERIFICATION_DECISIONS"
        next_action = "Resolve v4.40 manual verification decision readiness before creating preview records."
    elif blocked:
        status = "PARTIAL_VERIFIED_EVIDENCE_PREVIEW_READY"
        next_action = "Resolve missing, rejected, or needs-correction decisions before promotion dry-run review."
    else:
        status = "VERIFIED_EVIDENCE_PREVIEW_READY_FOR_PROMOTION_DRY_RUN_REVIEW"
        next_action = "A future promotion dry-run review may inspect these preview records; no evidence was verified."

    return FTAWRealVerifiedEvidencePreviewBridgePack(
        target_asset=manual_decisions.target_asset,
        preview_bridge_status=status,
        upstream_v4_40_status=manual_decisions.decision_recorder_status,
        accepted_decision_count=len(accepted_records),
        preview_record_count=len(preview_records),
        missing_preview_count=len(missing_types),
        manual_private_outstanding_count=manual_decisions.manual_private_outstanding_count,
        preview_records=preview_records,
        manual_private_outstanding=manual_decisions.manual_private_outstanding,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        evidence_verified=False,
        verified_evidence_promotion=False,
        approvals_created=False,
        registry_mutation=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
        executor_created=False,
        private_file_auto_ingest=False,
        automatic_source_fetching=False,
        automatic_downloads=False,
        automatic_fact_extraction=False,
    )


def build_ftaw_real_verified_evidence_preview_bridge_from_files(
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
) -> FTAWRealVerifiedEvidencePreviewBridgePack:
    Path(real_verified_evidence_preview_bridge_config_path).read_text(encoding="utf-8")
    manual_decisions = build_ftaw_real_manual_verification_decision_recorder_from_files(
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
    )
    return build_ftaw_real_verified_evidence_preview_bridge(manual_decisions)
