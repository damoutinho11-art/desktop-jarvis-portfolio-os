"""FTAW identity guard submission execution review pack.

This read-only final preflight reviews the explicit manual identity guard
submission command contract from v4.36. It never runs identity guard, creates
pass records, creates queue eligibility, verifies evidence, approves assets,
mutates registries, promotes evidence, recommends allocations, creates orders,
trades, or creates an executor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_explicit_manual_identity_guard_submission_command_contract import (
    EXPECTED_COMMAND_TYPE,
    FTAWExplicitManualIdentityGuardSubmissionCommandContractPack,
    build_ftaw_explicit_manual_identity_guard_submission_command_contract_from_files,
)


@dataclass(frozen=True)
class FTAWIdentityGuardSubmissionExecutionReviewPack:
    target_asset: str
    execution_review_status: str
    upstream_v4_36_status: str
    dry_run_status: str
    review_gate_status: str
    command_type: str | None
    asset_match: bool
    command_type_match: bool
    all_confirmations_true: bool
    packet_item_count: int
    required_packet_item_count: int
    manual_private_outstanding_count: int
    final_preflight_ready: bool
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    evidence_verified: bool = False
    identity_guard_executed: bool = False
    identity_guard_pass_records_created: bool = False
    queue_eligibility_created: bool = False
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


def build_ftaw_identity_guard_submission_execution_review_pack(
    contract: FTAWExplicitManualIdentityGuardSubmissionCommandContractPack,
) -> FTAWIdentityGuardSubmissionExecutionReviewPack:
    blocked: list[str] = []
    dry_run_status = "IDENTITY_GUARD_SUBMISSION_DRY_RUN_READY" if contract.packet_item_count == 5 else "INCOMPLETE"
    review_gate_status = contract.upstream_v4_35_gate_status
    command_type_match = contract.command_type == EXPECTED_COMMAND_TYPE
    all_confirmations_true = contract.missing_confirmation_count == 0 and all(check.ready for check in contract.confirmation_checklist)

    if contract.contract_status != "READY_FOR_MANUAL_IDENTITY_GUARD_SUBMISSION_EXECUTION_REVIEW":
        blocked.append(f"identity guard submission command contract status is {contract.contract_status}.")
    if dry_run_status != "IDENTITY_GUARD_SUBMISSION_DRY_RUN_READY":
        blocked.append("v4.34 dry-run packet is not ready with five public packet items.")
    if review_gate_status != "READY_FOR_EXPLICIT_MANUAL_IDENTITY_GUARD_SUBMISSION_COMMAND":
        blocked.append(f"v4.35 review gate status is {review_gate_status}.")
    if not command_type_match:
        blocked.append(f"command_type must be {EXPECTED_COMMAND_TYPE}.")
    if not contract.command_target_match:
        blocked.append("command target asset id must match target asset.")
    if not all_confirmations_true:
        blocked.append("all explicit manual command confirmations must be present and true.")

    blocked.extend(contract.blocked_reasons)

    if contract.contract_status == "BLOCKED_NO_IDENTITY_GUARD_SUBMISSION_REVIEW_GATE":
        status = "BLOCKED_NO_IDENTITY_GUARD_SUBMISSION_COMMAND_CONTRACT"
        next_action = "Resolve the v4.36 command contract before final preflight review."
    elif blocked:
        status = "PARTIAL_IDENTITY_GUARD_SUBMISSION_EXECUTION_REVIEW_READY"
        next_action = "Resolve execution-review blockers before any future manual identity guard submission step."
    else:
        status = "READY_FOR_FINAL_MANUAL_IDENTITY_GUARD_SUBMISSION_PREFLIGHT"
        next_action = "A future final manual preflight may inspect this packet; identity guard was not executed."

    return FTAWIdentityGuardSubmissionExecutionReviewPack(
        target_asset=contract.target_asset,
        execution_review_status=status,
        upstream_v4_36_status=contract.contract_status,
        dry_run_status=dry_run_status,
        review_gate_status=review_gate_status,
        command_type=contract.command_type,
        asset_match=contract.command_target_match,
        command_type_match=command_type_match,
        all_confirmations_true=all_confirmations_true,
        packet_item_count=contract.packet_item_count,
        required_packet_item_count=5,
        manual_private_outstanding_count=contract.manual_private_outstanding_count,
        final_preflight_ready=status == "READY_FOR_FINAL_MANUAL_IDENTITY_GUARD_SUBMISSION_PREFLIGHT",
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        evidence_verified=False,
        identity_guard_executed=False,
        identity_guard_pass_records_created=False,
        queue_eligibility_created=False,
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


def build_ftaw_identity_guard_submission_execution_review_pack_from_files(
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
) -> FTAWIdentityGuardSubmissionExecutionReviewPack:
    Path(identity_guard_submission_execution_review_config_path).read_text(encoding="utf-8")
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
    return build_ftaw_identity_guard_submission_execution_review_pack(contract)
