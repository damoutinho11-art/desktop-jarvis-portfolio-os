"""FTAW real candidate readiness review pack.

This read-only pack consumes v4.42 verified-evidence promotion dry-run items
and determines whether the real-evidence candidate is ready for a future
manual approval review. It does not promote verified evidence, mark evidence
verified, approve assets, mutate registries, recommend allocations, create
orders, trade, create an executor, ingest private files, fetch sources,
download sources, or extract facts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_real_manual_identity_guard_review_decision_recorder import PUBLIC_EVIDENCE_TYPES
from .ftaw_real_verified_evidence_promotion_dry_run_pack import (
    FTAWRealVerifiedEvidencePromotionDryRunItem,
    FTAWRealVerifiedEvidencePromotionDryRunPack,
    build_ftaw_real_verified_evidence_promotion_dry_run_pack_from_files,
)


@dataclass(frozen=True)
class FTAWRealCandidateReadinessReviewItem:
    asset_id: str
    evidence_type: str
    source_reference_id: str
    readiness_item_status: str
    promotion_dry_run: bool
    evidence_verified: bool = False
    verified_evidence_promoted: bool = False
    approved_asset: bool = False
    registry_mutation: bool = False
    allocation_recommendation: bool = False
    buy_signal: bool = False
    trade_executed: bool = False


@dataclass(frozen=True)
class FTAWRealCandidateReadinessReviewPack:
    target_asset: str
    readiness_status: str
    upstream_v4_42_status: str
    planned_item_count: int
    required_item_count: int
    missing_item_count: int
    manual_private_outstanding_count: int
    readiness_items: tuple[FTAWRealCandidateReadinessReviewItem, ...]
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


def _readiness_item_from_planned_item(
    item: FTAWRealVerifiedEvidencePromotionDryRunItem,
) -> FTAWRealCandidateReadinessReviewItem:
    return FTAWRealCandidateReadinessReviewItem(
        asset_id=item.asset_id,
        evidence_type=item.evidence_type,
        source_reference_id=item.source_reference_id,
        readiness_item_status="ready_for_manual_approval_review_readiness",
        promotion_dry_run=item.promotion_dry_run,
        evidence_verified=False,
        verified_evidence_promoted=False,
        approved_asset=False,
        registry_mutation=False,
        allocation_recommendation=False,
        buy_signal=False,
        trade_executed=False,
    )


def build_ftaw_real_candidate_readiness_review_pack(
    promotion_dry_run: FTAWRealVerifiedEvidencePromotionDryRunPack,
) -> FTAWRealCandidateReadinessReviewPack:
    planned_items = tuple(
        sorted(
            (
                item
                for item in promotion_dry_run.planned_items
                if item.promotion_dry_run and item.planned_promotion_status == "planned_for_promotion_dry_run"
            ),
            key=lambda item: (item.evidence_type, item.source_reference_id),
        )
    )
    readiness_items = tuple(_readiness_item_from_planned_item(item) for item in planned_items)
    planned_types = {item.evidence_type for item in readiness_items}
    missing_types = tuple(evidence_type for evidence_type in PUBLIC_EVIDENCE_TYPES if evidence_type not in planned_types)

    blocked: list[str] = []
    if promotion_dry_run.promotion_dry_run_status != "VERIFIED_EVIDENCE_PROMOTION_DRY_RUN_READY_FOR_CANDIDATE_READINESS_REVIEW":
        blocked.append(f"verified evidence promotion dry-run status is {promotion_dry_run.promotion_dry_run_status}.")
    blocked.extend(f"missing planned promotion dry-run item for {evidence_type}" for evidence_type in missing_types)
    blocked.extend(promotion_dry_run.blocked_reasons)

    if promotion_dry_run.promotion_dry_run_status == "BLOCKED_NO_VERIFIED_EVIDENCE_PREVIEW" and not readiness_items:
        status = "BLOCKED_NO_VERIFIED_EVIDENCE_PROMOTION_DRY_RUN"
        next_action = "Resolve v4.42 promotion dry-run readiness before candidate readiness review."
    elif blocked:
        status = "PARTIAL_REAL_CANDIDATE_READINESS_REVIEW_READY"
        next_action = "Resolve missing dry-run evidence items before future manual approval review."
    else:
        status = "REAL_CANDIDATE_READY_FOR_MANUAL_APPROVAL_REVIEW"
        next_action = "A future manual approval review may inspect this readiness pack; no asset was approved."

    return FTAWRealCandidateReadinessReviewPack(
        target_asset=promotion_dry_run.target_asset,
        readiness_status=status,
        upstream_v4_42_status=promotion_dry_run.promotion_dry_run_status,
        planned_item_count=len(readiness_items),
        required_item_count=len(PUBLIC_EVIDENCE_TYPES),
        missing_item_count=len(missing_types),
        manual_private_outstanding_count=promotion_dry_run.manual_private_outstanding_count,
        readiness_items=readiness_items,
        manual_private_outstanding=promotion_dry_run.manual_private_outstanding,
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


def build_ftaw_real_candidate_readiness_review_pack_from_files(
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
) -> FTAWRealCandidateReadinessReviewPack:
    Path(real_candidate_readiness_review_pack_config_path).read_text(encoding="utf-8")
    promotion_dry_run = build_ftaw_real_verified_evidence_promotion_dry_run_pack_from_files(
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
    )
    return build_ftaw_real_candidate_readiness_review_pack(promotion_dry_run)
