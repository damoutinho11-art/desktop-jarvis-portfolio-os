"""FTAW real identity-guarded verification queue dry-run bridge.

This read-only bridge converts v4.38 manual identity guard pass results into a
verification queue preview for later manual verification. It does not create
real queue items, create queue eligibility, verify evidence, promote evidence,
approve assets, mutate registries, recommend allocations, create orders, trade,
or create an executor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_manual_identity_guard_result_recorder import (
    FTAWManualIdentityGuardResultRecorderPack,
    build_ftaw_manual_identity_guard_result_recorder_from_files,
)
from .ftaw_real_manual_identity_guard_review_decision_recorder import PUBLIC_EVIDENCE_TYPES


@dataclass(frozen=True)
class FTAWRealIdentityGuardedVerificationQueueDryRunPreviewItem:
    evidence_type: str
    source_reference_id: str
    manual_identity_guard_result: str
    dry_run_queue_preview: bool
    real_queue_item_created: bool = False
    queue_eligibility_created: bool = False
    evidence_verified: bool = False
    verified_evidence_promoted: bool = False
    approved_asset: bool = False
    registry_mutation: bool = False
    buy_signal: bool = False


@dataclass(frozen=True)
class FTAWRealIdentityGuardedVerificationQueueDryRunBridgePack:
    target_asset: str
    queue_dry_run_bridge_status: str
    upstream_v4_38_status: str
    required_pass_count: int
    present_pass_count: int
    missing_fail_needs_correction_count: int
    dry_run_preview_item_count: int
    manual_private_outstanding_count: int
    preview_items: tuple[FTAWRealIdentityGuardedVerificationQueueDryRunPreviewItem, ...]
    manual_private_outstanding: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    real_queue_item_created: bool = False
    queue_eligibility_created: bool = False
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


def build_ftaw_real_identity_guarded_verification_queue_dry_run_bridge(
    result_pack: FTAWManualIdentityGuardResultRecorderPack,
) -> FTAWRealIdentityGuardedVerificationQueueDryRunBridgePack:
    pass_records = tuple(
        sorted(
            (
                record
                for record in result_pack.result_records
                if record.result_status == "manual_identity_guard_pass_recorded" and record.evidence_type in PUBLIC_EVIDENCE_TYPES
            ),
            key=lambda record: (record.evidence_type, record.source_reference_id),
        )
    )
    pass_types = {record.evidence_type for record in pass_records}
    missing_types = tuple(evidence_type for evidence_type in PUBLIC_EVIDENCE_TYPES if evidence_type not in pass_types)
    preview_items = tuple(
        FTAWRealIdentityGuardedVerificationQueueDryRunPreviewItem(
            evidence_type=record.evidence_type,
            source_reference_id=record.source_reference_id,
            manual_identity_guard_result="pass",
            dry_run_queue_preview=True,
            real_queue_item_created=False,
            queue_eligibility_created=False,
            evidence_verified=False,
            verified_evidence_promoted=False,
            approved_asset=False,
            registry_mutation=False,
            buy_signal=False,
        )
        for record in pass_records
    )

    blocked: list[str] = []
    if result_pack.result_recorder_status != "MANUAL_IDENTITY_GUARD_RESULTS_RECORDED_FOR_QUEUE_DRY_RUN_REVIEW":
        blocked.append(f"manual identity guard result recorder status is {result_pack.result_recorder_status}.")
    blocked.extend(f"missing manual identity guard pass result for {evidence_type}" for evidence_type in missing_types)
    blocked.extend(result_pack.blocked_reasons)

    missing_fail_needs_correction_count = max(0, len(PUBLIC_EVIDENCE_TYPES) - len(pass_types))
    if len(pass_records) == 0:
        status = "BLOCKED_NO_MANUAL_IDENTITY_GUARD_RESULTS"
        next_action = "Record manual identity guard pass results before creating a queue dry-run preview."
    elif blocked:
        status = "PARTIAL_VERIFICATION_QUEUE_DRY_RUN_READY"
        next_action = "Resolve missing, failed, or needs-correction manual identity guard results before full queue dry-run readiness."
    else:
        status = "VERIFICATION_QUEUE_DRY_RUN_READY_FOR_MANUAL_REVIEW"
        next_action = "A future manual verification queue review may inspect this dry-run preview; no real queue item was created."

    return FTAWRealIdentityGuardedVerificationQueueDryRunBridgePack(
        target_asset=result_pack.target_asset,
        queue_dry_run_bridge_status=status,
        upstream_v4_38_status=result_pack.result_recorder_status,
        required_pass_count=len(PUBLIC_EVIDENCE_TYPES),
        present_pass_count=len(pass_types),
        missing_fail_needs_correction_count=missing_fail_needs_correction_count,
        dry_run_preview_item_count=len(preview_items),
        manual_private_outstanding_count=result_pack.manual_private_outstanding_count,
        preview_items=preview_items,
        manual_private_outstanding=result_pack.manual_private_outstanding,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        real_queue_item_created=False,
        queue_eligibility_created=False,
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


def build_ftaw_real_identity_guarded_verification_queue_dry_run_bridge_from_files(
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
) -> FTAWRealIdentityGuardedVerificationQueueDryRunBridgePack:
    Path(real_identity_guarded_verification_queue_dry_run_bridge_config_path).read_text(encoding="utf-8")
    result_pack = build_ftaw_manual_identity_guard_result_recorder_from_files(
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
    )
    return build_ftaw_real_identity_guarded_verification_queue_dry_run_bridge(result_pack)
