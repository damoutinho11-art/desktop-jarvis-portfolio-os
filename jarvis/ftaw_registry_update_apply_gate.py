"""FTAW registry update apply gate.

This gate consumes the v4.22 registry update dry-run pack and decides whether a
future explicit manual apply step could be prepared. It does not perform the
apply step and never writes registry files.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_registry_update_dry_run_pack import (
    FTAWRegistryUpdateDryRunPack,
    build_ftaw_registry_update_dry_run_pack_from_files,
)


@dataclass(frozen=True)
class FTAWRegistryUpdateApplyGatePack:
    apply_gate_status: str
    target_asset: str
    dry_run_status: str
    current_approval_status: str | None
    proposed_approval_status: str | None
    registry_update_mode: str | None
    registry_mutation: bool
    approved_asset: bool
    buy_signal: bool
    explicit_manual_apply_required: bool
    apply_executed: bool
    registry_file_written: bool
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    no_verified_evidence_promotion: bool = True
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def build_ftaw_registry_update_apply_gate(dry_run: FTAWRegistryUpdateDryRunPack) -> FTAWRegistryUpdateApplyGatePack:
    blocked: list[str] = []
    if dry_run.registry_update_dry_run_status != "DRY_RUN_PLANNED":
        blocked.append(f"registry update dry-run status is {dry_run.registry_update_dry_run_status}.")
    if dry_run.registry_update_mode != "dry_run":
        blocked.append("registry_update_mode must be dry_run.")
    if dry_run.registry_mutation:
        blocked.append("registry_mutation must remain false.")
    if dry_run.approved_asset:
        blocked.append("approved_asset must remain false.")
    if dry_run.buy_signal:
        blocked.append("buy_signal must remain false.")
    if not dry_run.proposed_approval_status:
        blocked.append("proposed approval_status is missing.")
    if not dry_run.current_approval_status:
        blocked.append("current approval_status is missing.")
    if dry_run.dry_run_plan is None:
        blocked.append("dry-run plan is missing.")
    elif dry_run.dry_run_plan.asset_id != dry_run.target_asset:
        blocked.append("dry-run plan asset_id does not match target asset.")

    if blocked:
        return FTAWRegistryUpdateApplyGatePack(
            apply_gate_status="BLOCKED",
            target_asset=dry_run.target_asset,
            dry_run_status=dry_run.registry_update_dry_run_status,
            current_approval_status=dry_run.current_approval_status,
            proposed_approval_status=dry_run.proposed_approval_status,
            registry_update_mode=dry_run.registry_update_mode,
            registry_mutation=dry_run.registry_mutation,
            approved_asset=dry_run.approved_asset,
            buy_signal=dry_run.buy_signal,
            explicit_manual_apply_required=True,
            apply_executed=False,
            registry_file_written=False,
            blocked_reasons=tuple(dict.fromkeys(blocked)),
            next_manual_action="Resolve dry-run blockers before preparing any explicit manual apply step.",
        )

    return FTAWRegistryUpdateApplyGatePack(
        apply_gate_status="READY_FOR_EXPLICIT_MANUAL_REGISTRY_APPLY",
        target_asset=dry_run.target_asset,
        dry_run_status=dry_run.registry_update_dry_run_status,
        current_approval_status=dry_run.current_approval_status,
        proposed_approval_status=dry_run.proposed_approval_status,
        registry_update_mode=dry_run.registry_update_mode,
        registry_mutation=False,
        approved_asset=False,
        buy_signal=False,
        explicit_manual_apply_required=True,
        apply_executed=False,
        registry_file_written=False,
        blocked_reasons=(),
        next_manual_action="A future explicit manual apply command may be prepared; no apply was executed.",
        no_verified_evidence_promotion=True,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_registry_update_apply_gate_from_files(
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
) -> FTAWRegistryUpdateApplyGatePack:
    Path(registry_update_apply_gate_config_path).read_text(encoding="utf-8")
    dry_run = build_ftaw_registry_update_dry_run_pack_from_files(
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
    )
    return build_ftaw_registry_update_apply_gate(dry_run)
