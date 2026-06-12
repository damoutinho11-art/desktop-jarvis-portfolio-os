"""FTAW final real pipeline audit report.

This read-only audit summarizes the real-evidence FTAW control chain from
real evidence intake readiness through registry update dry-run planning. It
does not mutate registries, approve assets, verify evidence, promote evidence,
recommend allocations, create orders, trade, create an executor, ingest private
files, fetch sources, download sources, or extract facts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_explicit_manual_identity_guard_submission_command_contract import (
    build_ftaw_explicit_manual_identity_guard_submission_command_contract_from_files,
)
from .ftaw_identity_guard_submission_dry_run_pack import build_ftaw_identity_guard_submission_dry_run_pack_from_files
from .ftaw_identity_guard_submission_execution_review_pack import (
    build_ftaw_identity_guard_submission_execution_review_pack_from_files,
)
from .ftaw_identity_guard_submission_review_gate import build_ftaw_identity_guard_submission_review_gate_from_files
from .ftaw_manual_identity_guard_result_recorder import build_ftaw_manual_identity_guard_result_recorder_from_files
from .ftaw_manual_public_source_reference_entry_recorder import (
    build_ftaw_manual_public_source_reference_entry_recorder_from_files,
)
from .ftaw_manual_source_fact_entry_pack import build_ftaw_manual_source_fact_entry_pack_from_files
from .ftaw_real_candidate_readiness_review_pack import build_ftaw_real_candidate_readiness_review_pack_from_files
from .ftaw_real_evidence_collection_checklist_pack import (
    build_ftaw_real_evidence_collection_checklist_pack_from_files,
)
from .ftaw_real_evidence_intake_readiness_bridge import build_ftaw_real_evidence_intake_readiness_bridge_from_files
from .ftaw_real_human_approval_review_decision_recorder import (
    build_ftaw_real_human_approval_review_decision_recorder_from_files,
)
from .ftaw_real_identity_guarded_verification_queue_dry_run_bridge import (
    build_ftaw_real_identity_guarded_verification_queue_dry_run_bridge_from_files,
)
from .ftaw_real_manual_approval_review_gate import build_ftaw_real_manual_approval_review_gate_from_files
from .ftaw_real_manual_identity_guard_review_decision_recorder import (
    build_ftaw_real_manual_identity_guard_review_decision_recorder_from_files,
)
from .ftaw_real_manual_source_fact_identity_guard_bridge import (
    build_ftaw_real_manual_source_fact_identity_guard_bridge_from_files,
)
from .ftaw_real_manual_verification_decision_recorder import (
    build_ftaw_real_manual_verification_decision_recorder_from_files,
)
from .ftaw_real_public_source_reference_intake_plan import build_ftaw_real_public_source_reference_intake_plan_from_files
from .ftaw_real_registry_update_dry_run_pack import build_ftaw_real_registry_update_dry_run_pack_from_files
from .ftaw_real_verified_evidence_preview_bridge import build_ftaw_real_verified_evidence_preview_bridge_from_files
from .ftaw_real_verified_evidence_promotion_dry_run_pack import (
    build_ftaw_real_verified_evidence_promotion_dry_run_pack_from_files,
)


@dataclass(frozen=True)
class FTAWFinalRealPipelineAuditStage:
    stage_name: str
    status: str
    ready: bool
    blocked_reasons_count: int
    summary: str


@dataclass(frozen=True)
class FTAWFinalRealPipelineAuditPack:
    target_asset: str
    final_audit_status: str
    earliest_blocked_stage: str | None
    stage_count: int
    passed_stage_count: int
    blocked_stage_count: int
    warning_count: int
    final_dry_run_readiness: bool
    registry_dry_run_status: str
    proposed_dry_run_status: str | None
    stages: tuple[FTAWFinalRealPipelineAuditStage, ...]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    next_manual_action: str
    registry_dry_run_ready: bool
    registry_mutation: bool = False
    registry_file_written: bool = False
    approved_asset: bool = False
    approvals_created: bool = False
    evidence_verified_automatically: bool = False
    verified_evidence_promotion_executed: bool = False
    allocation_recommendation: bool = False
    allocation_recommendation_created: bool = False
    buy_signal: bool = False
    buy_sell_requests_created: bool = False
    trade_executed: bool = False
    trades_executed: bool = False
    executor_created: bool = False
    private_file_auto_ingest: bool = False
    automatic_source_fetching: bool = False
    automatic_downloads: bool = False
    automatic_fact_extraction: bool = False


READY_STATUSES = {
    "READY_FOR_REAL_EVIDENCE_INTAKE_PLANNING",
    "REAL_EVIDENCE_COLLECTION_PLAN_READY",
    "PUBLIC_SOURCE_REFERENCE_PLAN_READY",
    "PUBLIC_SOURCE_REFERENCES_RECORDED_FOR_MANUAL_FACT_ENTRY",
    "PUBLIC_SOURCE_FACTS_RECORDED_FOR_IDENTITY_GUARD_REVIEW",
    "MANUAL_SOURCE_FACTS_ENTERED_FOR_IDENTITY_REVIEW",
    "READY_FOR_MANUAL_IDENTITY_GUARD_REVIEW",
    "MANUAL_IDENTITY_GUARD_DECISIONS_RECORDED_FOR_DRY_RUN_SUBMISSION_REVIEW",
    "IDENTITY_GUARD_SUBMISSION_DRY_RUN_READY",
    "READY_FOR_EXPLICIT_MANUAL_IDENTITY_GUARD_SUBMISSION_COMMAND",
    "READY_FOR_MANUAL_IDENTITY_GUARD_SUBMISSION_EXECUTION_REVIEW",
    "READY_FOR_FINAL_MANUAL_IDENTITY_GUARD_SUBMISSION_PREFLIGHT",
    "MANUAL_IDENTITY_GUARD_RESULTS_RECORDED_FOR_QUEUE_DRY_RUN_REVIEW",
    "VERIFICATION_QUEUE_DRY_RUN_READY_FOR_MANUAL_REVIEW",
    "MANUAL_VERIFICATION_DECISIONS_RECORDED_FOR_VERIFIED_EVIDENCE_PREVIEW_REVIEW",
    "VERIFIED_EVIDENCE_PREVIEW_READY_FOR_PROMOTION_DRY_RUN_REVIEW",
    "VERIFIED_EVIDENCE_PROMOTION_DRY_RUN_READY_FOR_CANDIDATE_READINESS_REVIEW",
    "REAL_CANDIDATE_READY_FOR_MANUAL_APPROVAL_REVIEW",
    "READY_FOR_REAL_HUMAN_APPROVAL_REVIEW",
    "REAL_HUMAN_APPROVAL_REVIEW_DECISION_RECORDED_FOR_REGISTRY_DRY_RUN",
    "REAL_REGISTRY_UPDATE_DRY_RUN_READY_FOR_FINAL_AUDIT",
}


def _blocked_count(pack: object) -> int:
    return len(getattr(pack, "blocked_reasons", ()) or ())


def _stage(name: str, status: str, pack: object, summary: str = "read-only safety flags preserved") -> FTAWFinalRealPipelineAuditStage:
    return FTAWFinalRealPipelineAuditStage(
        stage_name=name,
        status=status,
        ready=status in READY_STATUSES,
        blocked_reasons_count=_blocked_count(pack),
        summary=summary,
    )


def _first_blocked(stages: tuple[FTAWFinalRealPipelineAuditStage, ...]) -> str | None:
    for stage in stages:
        if not stage.ready:
            return stage.stage_name
    return None


def _status(final_ready: bool, passed_stage_count: int) -> str:
    if final_ready:
        return "FINAL_REAL_PIPELINE_DRY_RUN_READY_SAFE"
    if passed_stage_count:
        return "FINAL_REAL_PIPELINE_PARTIAL_SAFE"
    return "FINAL_REAL_PIPELINE_BLOCKED_SAFE"


def build_ftaw_final_real_pipeline_audit_pack(
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
    real_registry_update_dry_run_pack_config_path: str | Path,
    final_real_pipeline_audit_config_path: str | Path,
) -> FTAWFinalRealPipelineAuditPack:
    Path(final_real_pipeline_audit_config_path).read_text(encoding="utf-8")

    intake = build_ftaw_real_evidence_intake_readiness_bridge_from_files(
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
    )
    checklist = build_ftaw_real_evidence_collection_checklist_pack_from_files(
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
    )
    plan = build_ftaw_real_public_source_reference_intake_plan_from_files(
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
    )
    recorder = build_ftaw_manual_public_source_reference_entry_recorder_from_files(
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
    )
    facts = build_ftaw_manual_source_fact_entry_pack_from_files(
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
    )
    bridge = build_ftaw_real_manual_source_fact_identity_guard_bridge_from_files(
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
    )
    review = build_ftaw_real_manual_identity_guard_review_decision_recorder_from_files(
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
    submission = build_ftaw_identity_guard_submission_dry_run_pack_from_files(
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
    )
    review_gate = build_ftaw_identity_guard_submission_review_gate_from_files(
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
    )
    contract = build_ftaw_explicit_manual_identity_guard_submission_command_contract_from_files(
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
    )
    execution = build_ftaw_identity_guard_submission_execution_review_pack_from_files(
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
    )
    result = build_ftaw_manual_identity_guard_result_recorder_from_files(
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
    queue_dry_run = build_ftaw_real_identity_guarded_verification_queue_dry_run_bridge_from_files(
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
    )
    manual_verification = build_ftaw_real_manual_verification_decision_recorder_from_files(
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
    preview = build_ftaw_real_verified_evidence_preview_bridge_from_files(
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
    )
    promotion = build_ftaw_real_verified_evidence_promotion_dry_run_pack_from_files(
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
    approval = build_ftaw_real_manual_approval_review_gate_from_files(
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
    human = build_ftaw_real_human_approval_review_decision_recorder_from_files(
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
        real_human_approval_review_decision_recorder_config_path,
    )
    registry = build_ftaw_real_registry_update_dry_run_pack_from_files(
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
        real_human_approval_review_decision_recorder_config_path,
        real_registry_update_dry_run_pack_config_path,
    )

    stages = (
        _stage("v4.27 real evidence intake readiness", intake.real_evidence_intake_readiness_status, intake),
        _stage("v4.28 collection checklist", checklist.checklist_status, checklist),
        _stage("v4.29 public source reference plan", plan.public_source_reference_plan_status, plan),
        _stage("v4.30 manual public reference recorder", recorder.recorder_status, recorder),
        _stage("v4.31 manual source fact entry", facts.source_fact_entry_status, facts),
        _stage("v4.32 identity guard bridge", bridge.bridge_status, bridge),
        _stage("v4.33 manual identity review decision recorder", review.recorder_status, review),
        _stage("v4.34 identity submission dry-run", submission.dry_run_status, submission),
        _stage("v4.35 identity submission review gate", review_gate.gate_status, review_gate),
        _stage("v4.36 explicit manual command contract", contract.contract_status, contract),
        _stage("v4.37 execution review preflight", execution.execution_review_status, execution),
        _stage("v4.38 manual identity result recorder", result.result_recorder_status, result),
        _stage("v4.39 verification queue dry-run bridge", queue_dry_run.queue_dry_run_bridge_status, queue_dry_run),
        _stage("v4.40 real manual verification decision recorder", manual_verification.decision_recorder_status, manual_verification),
        _stage("v4.41 verified evidence preview bridge", preview.preview_bridge_status, preview),
        _stage("v4.42 verified evidence promotion dry-run", promotion.promotion_dry_run_status, promotion),
        _stage("v4.43 real candidate readiness review", readiness.readiness_status, readiness),
        _stage("v4.44 real manual approval review gate", approval.approval_review_gate_status, approval),
        _stage("v4.45 real human approval decision recorder", human.recorder_status, human),
        _stage("v4.46 real registry update dry-run", registry.dry_run_status, registry),
    )
    passed = sum(1 for stage in stages if stage.ready)
    blocked_reasons = tuple(dict.fromkeys(reason for pack in (
        intake,
        checklist,
        plan,
        recorder,
        facts,
        bridge,
        review,
        submission,
        review_gate,
        contract,
        execution,
        result,
        queue_dry_run,
        manual_verification,
        preview,
        promotion,
        readiness,
        approval,
        human,
        registry,
    ) for reason in (getattr(pack, "blocked_reasons", ()) or ())))
    warnings = (
        "final audit is read-only and creates no executor.",
        "complete dry-run readiness is not asset approval.",
        "registry update dry-run remains a dry-run only.",
    )
    final_ready = (
        registry.dry_run_status == "REAL_REGISTRY_UPDATE_DRY_RUN_READY_FOR_FINAL_AUDIT"
        and registry.dry_run
        and not registry.registry_mutation
        and not registry.registry_file_written
        and not registry.approved_asset
        and not registry.allocation_recommendation
        and not registry.buy_signal
        and not registry.trade_executed
    )
    return FTAWFinalRealPipelineAuditPack(
        target_asset=registry.target_asset,
        final_audit_status=_status(final_ready, passed),
        earliest_blocked_stage=_first_blocked(stages),
        stage_count=len(stages),
        passed_stage_count=passed,
        blocked_stage_count=len(stages) - passed,
        warning_count=len(warnings),
        final_dry_run_readiness=final_ready,
        registry_dry_run_status=registry.dry_run_status,
        proposed_dry_run_status=registry.proposed_dry_run_status,
        stages=stages,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        next_manual_action=(
            "Backend gate chain phase 1 complete; a future executor would still require separate implementation."
            if final_ready
            else "Resolve the earliest blocked stage before treating the real pipeline as dry-run ready."
        ),
        registry_dry_run_ready=registry.dry_run,
        registry_mutation=False,
        registry_file_written=False,
        approved_asset=False,
        approvals_created=False,
        evidence_verified_automatically=False,
        verified_evidence_promotion_executed=False,
        allocation_recommendation=False,
        allocation_recommendation_created=False,
        buy_signal=False,
        buy_sell_requests_created=False,
        trade_executed=False,
        trades_executed=False,
        executor_created=False,
        private_file_auto_ingest=False,
        automatic_source_fetching=False,
        automatic_downloads=False,
        automatic_fact_extraction=False,
    )


def build_ftaw_final_real_pipeline_audit_report(*args: object, **kwargs: object) -> str:
    pack = build_ftaw_final_real_pipeline_audit_pack(*args, **kwargs)
    lines = [
        "J.A.R.V.I.S. FTAW Final Real Pipeline Audit Report",
        "Automated structure. Manual trust.",
        f"target asset: {pack.target_asset}",
        f"final audit status: {pack.final_audit_status}",
        f"earliest blocked stage: {pack.earliest_blocked_stage or 'none'}",
        f"stage count: {pack.stage_count}",
        f"passed stage count: {pack.passed_stage_count}",
        f"blocked stage count: {pack.blocked_stage_count}",
        f"warning count: {pack.warning_count}",
        f"final dry-run readiness: {str(pack.final_dry_run_readiness).lower()}",
        f"registry dry-run status: {pack.registry_dry_run_status}",
        f"proposed dry-run status: {pack.proposed_dry_run_status or 'none'}",
        "stage table:",
        "stage | status | ready | blocked reasons count | summary",
    ]
    lines.extend(
        f"{stage.stage_name} | {stage.status} | {str(stage.ready).lower()} | "
        f"{stage.blocked_reasons_count} | {stage.summary}"
        for stage in pack.stages
    )
    lines.append("blocked reasons:")
    lines.extend(f"- {reason}" for reason in pack.blocked_reasons) if pack.blocked_reasons else lines.append("- none")
    lines.append("warnings:")
    lines.extend(f"- {warning}" for warning in pack.warnings)
    lines.extend(
        [
            f"next manual action: {pack.next_manual_action}",
            "backend gate chain phase 1 complete only when complete audit is safe.",
            "no executor exists.",
            "no mutation performed.",
            "no buy/sell/trade performed.",
            "no registry mutation: true",
            "no registry file written: true",
            "no approvals created: true",
            "approved asset false: true",
            "no evidence verified automatically: true",
            "no verified evidence promotion executed: true",
            "no allocation recommendations: true",
            "no buy/sell requests: true",
            "no trades executed: true",
            "no executor created: true",
            "no private file auto-ingest: true",
            "no automatic source fetching: true",
            "no automatic downloads: true",
            "no automatic fact extraction: true",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build FTAW final real pipeline audit report.")
    parser.add_argument("source_registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    parser.add_argument("reviewed_registry_copy_path", nargs="?", default="jarvis/data/private/candidate_assets.v2.reviewed.local.json")
    parser.add_argument("url_fetch_config_path", nargs="?", default="jarvis/data/ftaw_public_url_fetch_adapter.example.json")
    parser.add_argument("fact_intake_config_path", nargs="?", default="jarvis/data/ftaw_source_fact_intake.example.json")
    parser.add_argument("identity_guard_config_path", nargs="?", default="jarvis/data/ftaw_source_identity_guard.example.json")
    parser.add_argument("queue_config_path", nargs="?", default="jarvis/data/ftaw_identity_guarded_verification_queue.example.json")
    parser.add_argument("decision_config_path", nargs="?", default="jarvis/data/ftaw_manual_verification_decision_recorder.example.json")
    parser.add_argument("preview_bridge_config_path", nargs="?", default="jarvis/data/ftaw_verified_evidence_preview_bridge.example.json")
    parser.add_argument("promotion_dry_run_config_path", nargs="?", default="jarvis/data/ftaw_verified_evidence_promotion_dry_run.example.json")
    parser.add_argument("readiness_config_path", nargs="?", default="jarvis/data/ftaw_candidate_readiness_pack.example.json")
    parser.add_argument("approval_review_gate_config_path", nargs="?", default="jarvis/data/ftaw_manual_approval_review_gate.example.json")
    parser.add_argument("human_decision_config_path", nargs="?", default="jarvis/data/ftaw_human_approval_review_decision_recorder.example.json")
    parser.add_argument("registry_update_dry_run_config_path", nargs="?", default="jarvis/data/ftaw_registry_update_dry_run_pack.example.json")
    parser.add_argument("registry_update_apply_gate_config_path", nargs="?", default="jarvis/data/ftaw_registry_update_apply_gate.example.json")
    parser.add_argument("explicit_manual_apply_command_config_path", nargs="?", default="jarvis/data/ftaw_explicit_manual_apply_command_contract.example.json")
    parser.add_argument("execution_review_config_path", nargs="?", default="jarvis/data/ftaw_registry_apply_execution_review_pack.example.json")
    parser.add_argument("full_pipeline_audit_config_path", nargs="?", default="jarvis/data/ftaw_full_pipeline_audit_report.example.json")
    parser.add_argument("real_evidence_intake_readiness_config_path", nargs="?", default="jarvis/data/ftaw_real_evidence_intake_readiness_bridge.example.json")
    parser.add_argument("collection_checklist_config_path", nargs="?", default="jarvis/data/ftaw_real_evidence_collection_checklist_pack.example.json")
    parser.add_argument("public_source_reference_plan_config_path", nargs="?", default="jarvis/data/ftaw_real_public_source_reference_intake_plan.example.json")
    parser.add_argument("manual_public_source_reference_entry_config_path", nargs="?", default="jarvis/data/ftaw_manual_public_source_reference_entry_recorder.example.json")
    parser.add_argument("manual_source_fact_entry_config_path", nargs="?", default="jarvis/data/ftaw_manual_source_fact_entry_pack.example.json")
    parser.add_argument("identity_guard_bridge_config_path", nargs="?", default="jarvis/data/ftaw_real_manual_source_fact_identity_guard_bridge.example.json")
    parser.add_argument("identity_guard_review_decision_config_path", nargs="?", default="jarvis/data/ftaw_real_manual_identity_guard_review_decision_recorder.example.json")
    parser.add_argument("identity_guard_submission_dry_run_config_path", nargs="?", default="jarvis/data/ftaw_identity_guard_submission_dry_run_pack.example.json")
    parser.add_argument("identity_guard_submission_review_gate_config_path", nargs="?", default="jarvis/data/ftaw_identity_guard_submission_review_gate.example.json")
    parser.add_argument("explicit_manual_identity_guard_submission_command_config_path", nargs="?", default="jarvis/data/ftaw_explicit_manual_identity_guard_submission_command_contract.example.json")
    parser.add_argument("identity_guard_submission_execution_review_config_path", nargs="?", default="jarvis/data/ftaw_identity_guard_submission_execution_review_pack.example.json")
    parser.add_argument("manual_identity_guard_result_recorder_config_path", nargs="?", default="jarvis/data/ftaw_manual_identity_guard_result_recorder.example.json")
    parser.add_argument("real_identity_guarded_verification_queue_dry_run_bridge_config_path", nargs="?", default="jarvis/data/ftaw_real_identity_guarded_verification_queue_dry_run_bridge.example.json")
    parser.add_argument("real_manual_verification_decision_recorder_config_path", nargs="?", default="jarvis/data/ftaw_real_manual_verification_decision_recorder.example.json")
    parser.add_argument("real_verified_evidence_preview_bridge_config_path", nargs="?", default="jarvis/data/ftaw_real_verified_evidence_preview_bridge.example.json")
    parser.add_argument("real_verified_evidence_promotion_dry_run_pack_config_path", nargs="?", default="jarvis/data/ftaw_real_verified_evidence_promotion_dry_run_pack.example.json")
    parser.add_argument("real_candidate_readiness_review_pack_config_path", nargs="?", default="jarvis/data/ftaw_real_candidate_readiness_review_pack.example.json")
    parser.add_argument("real_manual_approval_review_gate_config_path", nargs="?", default="jarvis/data/ftaw_real_manual_approval_review_gate.example.json")
    parser.add_argument("real_human_approval_review_decision_recorder_config_path", nargs="?", default="jarvis/data/ftaw_real_human_approval_review_decision_recorder.example.json")
    parser.add_argument("real_registry_update_dry_run_pack_config_path", nargs="?", default="jarvis/data/ftaw_real_registry_update_dry_run_pack.example.json")
    parser.add_argument("final_real_pipeline_audit_config_path", nargs="?", default="jarvis/data/ftaw_final_real_pipeline_audit_report.example.json")
    args = parser.parse_args()
    print(build_ftaw_final_real_pipeline_audit_report(**vars(args)))


if __name__ == "__main__":
    main()
