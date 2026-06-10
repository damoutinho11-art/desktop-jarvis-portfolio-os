"""FTAW registry apply execution-review pack.

This final preflight layer verifies that the explicit manual apply command
contract and upstream apply gate still agree. It does not execute an apply,
write registry files, approve assets, promote evidence, recommend allocations,
create orders, or trade.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_explicit_manual_apply_command_contract import (
    COMMAND_TYPE,
    FTAWExplicitManualApplyCommandContractPack,
    build_ftaw_explicit_manual_apply_command_contract_from_files,
)
from .ftaw_registry_update_apply_gate import (
    FTAWRegistryUpdateApplyGatePack,
    build_ftaw_registry_update_apply_gate_from_files,
)


@dataclass(frozen=True)
class FTAWRegistryApplyExecutionReviewPack:
    execution_review_status: str
    target_asset: str
    contract_validation_status: str
    apply_gate_status: str
    dry_run_status: str
    command_type: str | None
    asset_id_match: bool
    current_status_match: bool
    proposed_status_match: bool
    dry_run_fingerprint_match: bool
    human_confirmation_phrase_match: bool
    safety_confirmations_complete: bool
    replay_protection_fields_present: bool
    explicit_manual_apply_required: bool
    apply_executed: bool
    registry_file_written: bool
    registry_mutation: bool
    approved_asset: bool
    buy_signal: bool
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    no_verified_evidence_promotion: bool = True
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def build_ftaw_registry_apply_execution_review_pack(
    contract: FTAWExplicitManualApplyCommandContractPack,
    apply_gate: FTAWRegistryUpdateApplyGatePack,
) -> FTAWRegistryApplyExecutionReviewPack:
    blocked: list[str] = []
    if contract.contract_validation_status != "READY_FOR_MANUAL_REGISTRY_APPLY_EXECUTION_REVIEW":
        blocked.append(f"contract validation status is {contract.contract_validation_status}.")
    if apply_gate.apply_gate_status != "READY_FOR_EXPLICIT_MANUAL_REGISTRY_APPLY":
        blocked.append(f"apply gate status is {apply_gate.apply_gate_status}.")
    if not apply_gate.explicit_manual_apply_required:
        blocked.append("explicit_manual_apply_required must be true.")
    if apply_gate.dry_run_status != "DRY_RUN_PLANNED":
        blocked.append(f"dry-run status is {apply_gate.dry_run_status}.")
    if apply_gate.registry_update_mode != "dry_run":
        blocked.append("registry_update_mode must be dry_run.")
    if contract.command_type != COMMAND_TYPE:
        blocked.append("command_type is invalid.")
    if not contract.explicit_confirmation_phrase_match:
        blocked.append("human confirmation phrase did not match.")
    if not contract.safety_confirmations_complete:
        blocked.append("safety confirmations are incomplete.")
    if not contract.replay_protection_fields_present:
        blocked.append("replay protection fields are incomplete.")
    if contract.target_asset != apply_gate.target_asset:
        blocked.append("asset_id mismatch across contract and apply gate.")
    if not contract.asset_id_match:
        blocked.append("contract asset_id match is false.")
    if not contract.current_status_match:
        blocked.append("current approval_status match is false.")
    if not contract.proposed_status_match:
        blocked.append("proposed approval_status match is false.")
    if not contract.dry_run_fingerprint_match:
        blocked.append("dry-run fingerprint match is false.")
    if contract.apply_executed or apply_gate.apply_executed:
        blocked.append("apply_executed must remain false.")
    if contract.registry_file_written or apply_gate.registry_file_written:
        blocked.append("registry_file_written must remain false.")
    if apply_gate.registry_mutation:
        blocked.append("registry_mutation must remain false.")
    if contract.approved_asset or apply_gate.approved_asset:
        blocked.append("approved_asset must remain false.")
    if contract.buy_signal or apply_gate.buy_signal:
        blocked.append("buy_signal must remain false.")

    ready = not blocked
    return FTAWRegistryApplyExecutionReviewPack(
        execution_review_status="READY_FOR_FINAL_MANUAL_REGISTRY_APPLY_PREFLIGHT" if ready else "BLOCKED",
        target_asset=apply_gate.target_asset,
        contract_validation_status=contract.contract_validation_status,
        apply_gate_status=apply_gate.apply_gate_status,
        dry_run_status=apply_gate.dry_run_status,
        command_type=contract.command_type,
        asset_id_match=contract.asset_id_match and contract.target_asset == apply_gate.target_asset,
        current_status_match=contract.current_status_match,
        proposed_status_match=contract.proposed_status_match,
        dry_run_fingerprint_match=contract.dry_run_fingerprint_match,
        human_confirmation_phrase_match=contract.explicit_confirmation_phrase_match,
        safety_confirmations_complete=contract.safety_confirmations_complete,
        replay_protection_fields_present=contract.replay_protection_fields_present,
        explicit_manual_apply_required=apply_gate.explicit_manual_apply_required,
        apply_executed=False,
        registry_file_written=False,
        registry_mutation=apply_gate.registry_mutation,
        approved_asset=False,
        buy_signal=False,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=(
            "A future executor could be designed for explicit manual apply; this preflight executed nothing."
            if ready
            else "Resolve execution-review blockers before any future apply executor can be considered."
        ),
        no_verified_evidence_promotion=True,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_registry_apply_execution_review_pack_from_files(
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
) -> FTAWRegistryApplyExecutionReviewPack:
    Path(execution_review_config_path).read_text(encoding="utf-8")
    apply_gate = build_ftaw_registry_update_apply_gate_from_files(
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
    )
    contract = build_ftaw_explicit_manual_apply_command_contract_from_files(
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
    )
    return build_ftaw_registry_apply_execution_review_pack(contract, apply_gate)
