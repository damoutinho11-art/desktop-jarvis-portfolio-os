"""FTAW explicit manual identity guard submission command contract.

This read-only contract validates a human-authored command against the v4.35
identity guard submission review gate. It does not run identity guard, create
pass records, create queue eligibility, verify evidence, approve assets, mutate
registries, promote evidence, recommend allocations, create orders, trade, or
create an executor.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .ftaw_identity_guard_submission_review_gate import (
    FTAWIdentityGuardSubmissionReviewGatePack,
    build_ftaw_identity_guard_submission_review_gate_from_files,
)


EXPECTED_COMMAND_TYPE = "submit_identity_guard_dry_run_packet_for_manual_review"
REQUIRED_CONFIRMATIONS = (
    "user_confirmed_manual_identity_submission_review",
    "user_confirmed_no_auto_execution",
    "user_confirmed_no_evidence_verification",
    "user_confirmed_no_queue_eligibility",
    "user_confirmed_no_approval",
    "user_confirmed_no_registry_mutation",
    "user_confirmed_no_buy_signal",
    "user_confirmed_no_trade",
)


@dataclass(frozen=True)
class FTAWManualIdentityGuardSubmissionConfirmationCheck:
    confirmation_name: str
    present: bool
    value: bool
    ready: bool
    reason: str


@dataclass(frozen=True)
class FTAWExplicitManualIdentityGuardSubmissionCommandContractPack:
    target_asset: str
    contract_status: str
    upstream_v4_35_gate_status: str
    command_type: str | None
    command_target_asset_id: str | None
    command_target_match: bool
    confirmation_checklist: tuple[FTAWManualIdentityGuardSubmissionConfirmationCheck, ...]
    packet_item_count: int
    missing_confirmation_count: int
    manual_private_outstanding_count: int
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


def _load_command(path: str | Path) -> dict:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    command = data.get("manual_identity_guard_submission_command")
    if command is None:
        return {}
    if not isinstance(command, dict):
        raise ValueError("manual_identity_guard_submission_command must be an object when present")
    return command


def _build_confirmation_checks(command: dict) -> tuple[FTAWManualIdentityGuardSubmissionConfirmationCheck, ...]:
    checks = []
    for name in REQUIRED_CONFIRMATIONS:
        present = name in command
        value = command.get(name) is True
        checks.append(
            FTAWManualIdentityGuardSubmissionConfirmationCheck(
                confirmation_name=name,
                present=present,
                value=value,
                ready=present and value,
                reason="confirmed"
                if present and value
                else f"{name} must be present and true",
            )
        )
    return tuple(checks)


def build_ftaw_explicit_manual_identity_guard_submission_command_contract(
    gate: FTAWIdentityGuardSubmissionReviewGatePack,
    command: dict,
) -> FTAWExplicitManualIdentityGuardSubmissionCommandContractPack:
    blocked: list[str] = []
    command_type = command.get("command_type")
    command_target_asset_id = command.get("command_target_asset_id")
    command_target_match = command_target_asset_id == gate.target_asset
    confirmation_checks = _build_confirmation_checks(command)
    missing_confirmation_count = sum(1 for check in confirmation_checks if not check.ready)

    gate_not_ready = gate.gate_status != "READY_FOR_EXPLICIT_MANUAL_IDENTITY_GUARD_SUBMISSION_COMMAND"

    if gate_not_ready:
        blocked.append(f"identity guard submission review gate status is {gate.gate_status}.")

    if not command:
        blocked.append("explicit manual identity guard submission command is missing.")
    else:
        if command_type != EXPECTED_COMMAND_TYPE:
            blocked.append(f"command_type must be {EXPECTED_COMMAND_TYPE}.")
        if not command_target_match:
            blocked.append("command target asset id must match gate target asset.")
        for check in confirmation_checks:
            if not check.ready:
                blocked.append(check.reason)

    if gate.present_packet_item_count != 5:
        blocked.append("v4.35 gate must contain five public packet items.")

    blocked.extend(gate.blocked_reasons)

    if gate_not_ready and not command:
        status = "BLOCKED_NO_IDENTITY_GUARD_SUBMISSION_REVIEW_GATE"
        next_action = "Resolve the v4.35 identity guard submission review gate before validating a manual command."
    elif not command:
        status = "BLOCKED_NO_EXPLICIT_MANUAL_COMMAND"
        next_action = "Provide an explicit manual identity guard submission command with all confirmations."
    elif blocked:
        status = "PARTIAL_MANUAL_IDENTITY_GUARD_SUBMISSION_COMMAND_RECORDED"
        next_action = "Resolve command blockers before execution review can be considered."
    else:
        status = "READY_FOR_MANUAL_IDENTITY_GUARD_SUBMISSION_EXECUTION_REVIEW"
        next_action = "A later execution review may inspect this command; identity guard was not executed."

    return FTAWExplicitManualIdentityGuardSubmissionCommandContractPack(
        target_asset=gate.target_asset,
        contract_status=status,
        upstream_v4_35_gate_status=gate.gate_status,
        command_type=command_type,
        command_target_asset_id=command_target_asset_id,
        command_target_match=command_target_match,
        confirmation_checklist=confirmation_checks,
        packet_item_count=gate.present_packet_item_count,
        missing_confirmation_count=missing_confirmation_count,
        manual_private_outstanding_count=gate.manual_private_outstanding_count,
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


def build_ftaw_explicit_manual_identity_guard_submission_command_contract_from_files(
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
) -> FTAWExplicitManualIdentityGuardSubmissionCommandContractPack:
    gate = build_ftaw_identity_guard_submission_review_gate_from_files(
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
    command = _load_command(explicit_manual_identity_guard_submission_command_config_path)
    return build_ftaw_explicit_manual_identity_guard_submission_command_contract(gate, command)
