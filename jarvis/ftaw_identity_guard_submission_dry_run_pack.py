"""FTAW identity guard submission dry-run pack.

This read-only dry-run packages accepted manual identity-guard review decisions
for a future submission review. It does not run identity guard, create pass
records, create queue eligibility, verify evidence, approve assets, mutate
registries, promote evidence, recommend allocations, create orders, trade, or
create an executor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_real_manual_identity_guard_review_decision_recorder import (
    PUBLIC_EVIDENCE_TYPES,
    FTAWManualIdentityGuardReviewDecisionRecorderPack,
    build_ftaw_real_manual_identity_guard_review_decision_recorder_from_files,
)


@dataclass(frozen=True)
class FTAWIdentityGuardSubmissionDryRunItem:
    evidence_type: str
    source_reference_id: str
    reviewer_decision: str
    included_in_dry_run_packet: bool
    identity_guard_executed: bool = False
    identity_guard_pass_created: bool = False
    queue_eligibility_created: bool = False
    evidence_verified: bool = False
    approved_asset: bool = False
    buy_signal: bool = False


@dataclass(frozen=True)
class FTAWIdentityGuardSubmissionDryRunPack:
    target_asset: str
    dry_run_status: str
    upstream_v4_33_status: str
    accepted_decision_count: int
    required_public_decision_count: int
    missing_decision_count: int
    dry_run_packet_item_count: int
    manual_private_outstanding_count: int
    packet_items: tuple[FTAWIdentityGuardSubmissionDryRunItem, ...]
    manual_private_outstanding: tuple
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    evidence_verified: bool = False
    identity_guard_executed: bool = False
    identity_guard_pass_records_created: bool = False
    queue_eligibility_created: bool = False
    verified_evidence_promotion: bool = False
    approved_asset: bool = False
    registry_mutation: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    executor_created: bool = False
    private_file_auto_ingest: bool = False
    automatic_source_fetching: bool = False
    automatic_downloads: bool = False
    automatic_fact_extraction: bool = False


def build_ftaw_identity_guard_submission_dry_run_pack(
    decision_pack: FTAWManualIdentityGuardReviewDecisionRecorderPack,
) -> FTAWIdentityGuardSubmissionDryRunPack:
    accepted = tuple(
        sorted(
            (
                record
                for record in decision_pack.decision_records
                if record.reviewer_decision == "accept_for_identity_guard_review" and record.evidence_type in PUBLIC_EVIDENCE_TYPES
            ),
            key=lambda record: (record.evidence_type, record.source_reference_id),
        )
    )
    present_types = {record.evidence_type for record in accepted}
    missing_types = tuple(evidence_type for evidence_type in PUBLIC_EVIDENCE_TYPES if evidence_type not in present_types)
    blocked = list(decision_pack.blocked_reasons)
    blocked.extend(f"missing accepted identity guard decision for {evidence_type}" for evidence_type in missing_types)
    packet_items = tuple(
        FTAWIdentityGuardSubmissionDryRunItem(
            evidence_type=record.evidence_type,
            source_reference_id=record.source_reference_id,
            reviewer_decision=record.reviewer_decision,
            included_in_dry_run_packet=True,
            identity_guard_executed=False,
            identity_guard_pass_created=False,
            queue_eligibility_created=False,
            evidence_verified=False,
            approved_asset=False,
            buy_signal=False,
        )
        for record in accepted
    )

    if len(accepted) == 0:
        status = "BLOCKED_NO_MANUAL_IDENTITY_GUARD_DECISIONS"
        next_action = "Record accepted manual identity guard review decisions before creating a dry-run packet."
    elif missing_types or decision_pack.recorder_status != "MANUAL_IDENTITY_GUARD_DECISIONS_RECORDED_FOR_DRY_RUN_SUBMISSION_REVIEW":
        status = "PARTIAL_IDENTITY_GUARD_SUBMISSION_DRY_RUN_READY"
        next_action = "Resolve missing or blocked accepted decisions before full dry-run submission readiness."
    else:
        status = "IDENTITY_GUARD_SUBMISSION_DRY_RUN_READY"
        next_action = "Proceed later to a manual identity guard submission review; do not execute identity guard automatically."

    return FTAWIdentityGuardSubmissionDryRunPack(
        target_asset=decision_pack.target_asset,
        dry_run_status=status,
        upstream_v4_33_status=decision_pack.recorder_status,
        accepted_decision_count=len(accepted),
        required_public_decision_count=len(PUBLIC_EVIDENCE_TYPES),
        missing_decision_count=len(missing_types),
        dry_run_packet_item_count=len(packet_items),
        manual_private_outstanding_count=decision_pack.manual_private_outstanding_count,
        packet_items=packet_items,
        manual_private_outstanding=decision_pack.manual_private_outstanding,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        evidence_verified=False,
        identity_guard_executed=False,
        identity_guard_pass_records_created=False,
        queue_eligibility_created=False,
        verified_evidence_promotion=False,
        approved_asset=False,
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


def build_ftaw_identity_guard_submission_dry_run_pack_from_files(
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
) -> FTAWIdentityGuardSubmissionDryRunPack:
    Path(identity_guard_submission_dry_run_config_path).read_text(encoding="utf-8")
    decision_pack = build_ftaw_real_manual_identity_guard_review_decision_recorder_from_files(
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
    )
    return build_ftaw_identity_guard_submission_dry_run_pack(decision_pack)
