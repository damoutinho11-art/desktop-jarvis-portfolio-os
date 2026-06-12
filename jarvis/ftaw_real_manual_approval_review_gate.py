"""FTAW real manual approval review gate.

This read-only gate consumes v4.43 real candidate readiness and prepares a
human approval review packet. It does not approve assets, mutate registries,
recommend allocations, create orders, trade, create an executor, verify
evidence, promote evidence, ingest private files, fetch sources, download
sources, or extract facts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_real_manual_identity_guard_review_decision_recorder import PUBLIC_EVIDENCE_TYPES
from .ftaw_real_candidate_readiness_review_pack import (
    FTAWRealCandidateReadinessReviewItem,
    FTAWRealCandidateReadinessReviewPack,
    build_ftaw_real_candidate_readiness_review_pack_from_files,
)


@dataclass(frozen=True)
class FTAWRealManualApprovalReviewPacket:
    asset_id: str
    candidate_readiness_status: str
    readiness_item_count: int
    required_evidence_types: tuple[str, ...]
    missing_evidence_types: tuple[str, ...]
    readiness_references: tuple[str, ...]
    manual_private_outstanding: tuple[str, ...]
    approval_review_only: bool = True
    approved_asset: bool = False
    approval_status_change: bool = False
    registry_mutation: bool = False
    allocation_recommendation: bool = False
    buy_signal: bool = False
    trade_executed: bool = False


@dataclass(frozen=True)
class FTAWRealManualApprovalReviewGatePack:
    target_asset: str
    approval_review_gate_status: str
    upstream_v4_43_status: str
    readiness_item_count: int
    required_item_count: int
    missing_item_count: int
    approval_packet_created: bool
    manual_private_outstanding_count: int
    review_packet: FTAWRealManualApprovalReviewPacket | None
    readiness_items: tuple[FTAWRealCandidateReadinessReviewItem, ...]
    manual_private_outstanding: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    approvals_created: bool = False
    registry_mutation: bool = False
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


def _missing_types(readiness: FTAWRealCandidateReadinessReviewPack) -> tuple[str, ...]:
    present = {item.evidence_type for item in readiness.readiness_items}
    return tuple(evidence_type for evidence_type in PUBLIC_EVIDENCE_TYPES if evidence_type not in present)


def build_ftaw_real_manual_approval_review_gate(
    readiness: FTAWRealCandidateReadinessReviewPack,
) -> FTAWRealManualApprovalReviewGatePack:
    readiness_items = tuple(sorted(readiness.readiness_items, key=lambda item: (item.evidence_type, item.source_reference_id)))
    missing_types = _missing_types(readiness)
    blocked: list[str] = []
    if readiness.readiness_status != "REAL_CANDIDATE_READY_FOR_MANUAL_APPROVAL_REVIEW":
        blocked.append(f"real candidate readiness status is {readiness.readiness_status}.")
    if len(readiness_items) != len(PUBLIC_EVIDENCE_TYPES):
        blocked.append("readiness item coverage is incomplete.")
    blocked.extend(f"missing readiness item for {evidence_type}" for evidence_type in missing_types)
    blocked.extend(readiness.blocked_reasons)

    if readiness.readiness_status == "BLOCKED_NO_VERIFIED_EVIDENCE_PROMOTION_DRY_RUN" and not readiness_items:
        status = "BLOCKED_NO_REAL_CANDIDATE_READINESS_REVIEW"
        next_action = "Resolve v4.43 real candidate readiness before creating a manual approval review packet."
        packet = None
    elif blocked:
        status = "PARTIAL_REAL_MANUAL_APPROVAL_REVIEW_READY"
        next_action = "Resolve readiness blockers before future human approval review."
        packet = FTAWRealManualApprovalReviewPacket(
            asset_id=readiness.target_asset,
            candidate_readiness_status=readiness.readiness_status,
            readiness_item_count=len(readiness_items),
            required_evidence_types=PUBLIC_EVIDENCE_TYPES,
            missing_evidence_types=missing_types,
            readiness_references=tuple(f"{item.asset_id}:{item.evidence_type}:readiness_review" for item in readiness_items),
            manual_private_outstanding=readiness.manual_private_outstanding,
            approval_review_only=True,
            approved_asset=False,
            approval_status_change=False,
            registry_mutation=False,
            allocation_recommendation=False,
            buy_signal=False,
            trade_executed=False,
        )
    else:
        status = "READY_FOR_REAL_HUMAN_APPROVAL_REVIEW"
        next_action = "A human may review the approval packet; this is not approval."
        packet = FTAWRealManualApprovalReviewPacket(
            asset_id=readiness.target_asset,
            candidate_readiness_status=readiness.readiness_status,
            readiness_item_count=len(readiness_items),
            required_evidence_types=PUBLIC_EVIDENCE_TYPES,
            missing_evidence_types=(),
            readiness_references=tuple(f"{item.asset_id}:{item.evidence_type}:readiness_review" for item in readiness_items),
            manual_private_outstanding=readiness.manual_private_outstanding,
            approval_review_only=True,
            approved_asset=False,
            approval_status_change=False,
            registry_mutation=False,
            allocation_recommendation=False,
            buy_signal=False,
            trade_executed=False,
        )

    return FTAWRealManualApprovalReviewGatePack(
        target_asset=readiness.target_asset,
        approval_review_gate_status=status,
        upstream_v4_43_status=readiness.readiness_status,
        readiness_item_count=len(readiness_items),
        required_item_count=len(PUBLIC_EVIDENCE_TYPES),
        missing_item_count=len(missing_types),
        approval_packet_created=packet is not None,
        manual_private_outstanding_count=readiness.manual_private_outstanding_count,
        review_packet=packet,
        readiness_items=readiness_items,
        manual_private_outstanding=readiness.manual_private_outstanding,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        approvals_created=False,
        registry_mutation=False,
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


def build_ftaw_real_manual_approval_review_gate_from_files(
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
) -> FTAWRealManualApprovalReviewGatePack:
    Path(real_manual_approval_review_gate_config_path).read_text(encoding="utf-8")
    readiness = build_ftaw_real_candidate_readiness_review_pack_from_files(
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
    )
    return build_ftaw_real_manual_approval_review_gate(readiness)
