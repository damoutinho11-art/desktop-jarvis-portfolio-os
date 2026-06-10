"""Explicit manual apply command contract for FTAW registry updates.

This layer validates the human-authored command payload required before a
future registry apply executor could even be considered. It does not execute
the apply, mutate registries, approve assets, promote evidence, recommend
allocations, create orders, or trade.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ftaw_registry_update_apply_gate import (
    FTAWRegistryUpdateApplyGatePack,
    build_ftaw_registry_update_apply_gate_from_files,
)


COMMAND_TYPE = "explicit_manual_registry_apply_request"
REQUIRED_CONFIRMATION_PHRASE = "I EXPLICITLY REQUEST A DRY-RUN MATCHED REGISTRY APPLY REVIEW FOR THIS ASSET ONLY"
REQUIRED_SAFETY_CONFIRMATIONS = (
    "I understand this is a registry update request only",
    "I understand this is not a buy/sell request",
    "I understand this does not execute trades",
    "I understand allocation recommendations are separate",
    "I understand this must match the dry-run plan exactly",
)


@dataclass(frozen=True)
class FTAWExplicitManualApplyCommand:
    command_id: str
    asset_id: str
    dry_run_plan_reference: str
    proposed_approval_status: str
    current_approval_status: str
    command_type: str
    human_confirmation_text: str
    human_operator: str
    command_timestamp: str
    dry_run_plan_fingerprint: str
    safety_confirmations: dict[str, bool]


@dataclass(frozen=True)
class FTAWExplicitManualApplyCommandConfig:
    command: FTAWExplicitManualApplyCommand | None


@dataclass(frozen=True)
class FTAWExplicitManualApplyCommandContractPack:
    contract_validation_status: str
    target_asset: str
    apply_gate_status: str
    command_file_used: str
    command_type: str | None
    asset_id_match: bool
    current_status_match: bool
    proposed_status_match: bool
    dry_run_fingerprint_match: bool
    safety_confirmations_complete: bool
    explicit_confirmation_phrase_match: bool
    replay_protection_fields_present: bool
    apply_executed: bool
    registry_file_written: bool
    approved_asset: bool
    buy_signal: bool
    blocked_reasons: tuple[str, ...]
    no_verified_evidence_promotion: bool = True
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")
    return value.strip()


def build_expected_dry_run_plan_reference(gate: FTAWRegistryUpdateApplyGatePack) -> str:
    return f"{gate.target_asset}:{gate.current_approval_status}:{gate.proposed_approval_status}:dry_run"


def build_expected_dry_run_plan_fingerprint(gate: FTAWRegistryUpdateApplyGatePack) -> str:
    payload = "|".join(
        (
            gate.target_asset,
            gate.current_approval_status or "",
            gate.proposed_approval_status or "",
            gate.registry_update_mode or "",
        )
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _parse_command(value: Any) -> FTAWExplicitManualApplyCommand:
    raw = _require_mapping(value, "explicit manual apply command")
    confirmations = _require_mapping(raw.get("safety_confirmations"), "safety_confirmations")
    return FTAWExplicitManualApplyCommand(
        command_id=_require_text(raw.get("command_id"), "command_id"),
        asset_id=_require_text(raw.get("asset_id"), "asset_id"),
        dry_run_plan_reference=_require_text(raw.get("dry_run_plan_reference"), "dry_run_plan_reference"),
        proposed_approval_status=_require_text(raw.get("proposed_approval_status"), "proposed_approval_status"),
        current_approval_status=_require_text(raw.get("current_approval_status"), "current_approval_status"),
        command_type=_require_text(raw.get("command_type"), "command_type"),
        human_confirmation_text=_require_text(raw.get("human_confirmation_text"), "human_confirmation_text"),
        human_operator=_require_text(raw.get("human_operator"), "human_operator"),
        command_timestamp=_require_text(raw.get("command_timestamp"), "command_timestamp"),
        dry_run_plan_fingerprint=_require_text(raw.get("dry_run_plan_fingerprint"), "dry_run_plan_fingerprint"),
        safety_confirmations={str(key): bool(value) for key, value in confirmations.items()},
    )


def load_ftaw_explicit_manual_apply_command_config(path: str | Path) -> FTAWExplicitManualApplyCommandConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "FTAW explicit manual apply command contract config")
    command = raw.get("command")
    if command is None:
        return FTAWExplicitManualApplyCommandConfig(command=None)
    return FTAWExplicitManualApplyCommandConfig(command=_parse_command(command))


def build_ftaw_explicit_manual_apply_command_contract(
    apply_gate: FTAWRegistryUpdateApplyGatePack,
    command_config: FTAWExplicitManualApplyCommandConfig,
    command_file_used: str | Path,
) -> FTAWExplicitManualApplyCommandContractPack:
    command = command_config.command
    blocked: list[str] = []
    if apply_gate.apply_gate_status != "READY_FOR_EXPLICIT_MANUAL_REGISTRY_APPLY":
        blocked.append(f"apply gate status is {apply_gate.apply_gate_status}.")
        return FTAWExplicitManualApplyCommandContractPack(
            contract_validation_status="BLOCKED",
            target_asset=apply_gate.target_asset,
            apply_gate_status=apply_gate.apply_gate_status,
            command_file_used=str(command_file_used),
            command_type=command.command_type if command else None,
            asset_id_match=False,
            current_status_match=False,
            proposed_status_match=False,
            dry_run_fingerprint_match=False,
            safety_confirmations_complete=False,
            explicit_confirmation_phrase_match=False,
            replay_protection_fields_present=False,
            apply_executed=False,
            registry_file_written=False,
            approved_asset=False,
            buy_signal=False,
            blocked_reasons=tuple(blocked),
        )
    if not apply_gate.explicit_manual_apply_required:
        blocked.append("explicit_manual_apply_required must be true.")
    if apply_gate.apply_executed:
        blocked.append("apply_executed must remain false.")
    if apply_gate.registry_file_written:
        blocked.append("registry_file_written must remain false.")
    if command is None:
        return FTAWExplicitManualApplyCommandContractPack(
            contract_validation_status="PENDING_EXPLICIT_MANUAL_APPLY_COMMAND",
            target_asset=apply_gate.target_asset,
            apply_gate_status=apply_gate.apply_gate_status,
            command_file_used=str(command_file_used),
            command_type=None,
            asset_id_match=False,
            current_status_match=False,
            proposed_status_match=False,
            dry_run_fingerprint_match=False,
            safety_confirmations_complete=False,
            explicit_confirmation_phrase_match=False,
            replay_protection_fields_present=False,
            apply_executed=False,
            registry_file_written=False,
            approved_asset=False,
            buy_signal=False,
            blocked_reasons=tuple(blocked),
        )

    expected_reference = build_expected_dry_run_plan_reference(apply_gate)
    expected_fingerprint = build_expected_dry_run_plan_fingerprint(apply_gate)
    asset_match = command.asset_id == apply_gate.target_asset
    current_match = command.current_approval_status == apply_gate.current_approval_status
    proposed_match = command.proposed_approval_status == apply_gate.proposed_approval_status
    fingerprint_match = command.dry_run_plan_fingerprint == expected_fingerprint and command.dry_run_plan_reference == expected_reference
    safety_complete = all(command.safety_confirmations.get(item) is True for item in REQUIRED_SAFETY_CONFIRMATIONS)
    phrase_match = command.human_confirmation_text == REQUIRED_CONFIRMATION_PHRASE
    replay_present = bool(command.command_id and command.command_timestamp)

    if command.command_type != COMMAND_TYPE:
        blocked.append("command_type is invalid.")
    if not asset_match:
        blocked.append("command asset_id does not match apply gate target asset.")
    if not current_match:
        blocked.append("command current_approval_status does not match apply gate.")
    if not proposed_match:
        blocked.append("command proposed_approval_status does not match apply gate.")
    if not fingerprint_match:
        blocked.append("dry-run plan reference or fingerprint does not match.")
    if not safety_complete:
        blocked.append("required safety confirmations are incomplete.")
    if not phrase_match:
        blocked.append("explicit confirmation phrase does not match.")
    if not replay_present:
        blocked.append("command replay-protection fields are incomplete.")

    return FTAWExplicitManualApplyCommandContractPack(
        contract_validation_status="BLOCKED" if blocked else "READY_FOR_MANUAL_REGISTRY_APPLY_EXECUTION_REVIEW",
        target_asset=apply_gate.target_asset,
        apply_gate_status=apply_gate.apply_gate_status,
        command_file_used=str(command_file_used),
        command_type=command.command_type,
        asset_id_match=asset_match,
        current_status_match=current_match,
        proposed_status_match=proposed_match,
        dry_run_fingerprint_match=fingerprint_match,
        safety_confirmations_complete=safety_complete,
        explicit_confirmation_phrase_match=phrase_match,
        replay_protection_fields_present=replay_present,
        apply_executed=False,
        registry_file_written=False,
        approved_asset=False,
        buy_signal=False,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        no_verified_evidence_promotion=True,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_explicit_manual_apply_command_contract_from_files(
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
) -> FTAWExplicitManualApplyCommandContractPack:
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
    return build_ftaw_explicit_manual_apply_command_contract(
        apply_gate,
        load_ftaw_explicit_manual_apply_command_config(explicit_manual_apply_command_config_path),
        explicit_manual_apply_command_config_path,
    )
