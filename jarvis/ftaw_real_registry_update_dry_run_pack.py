"""FTAW real registry update dry-run pack.

This read-only pack consumes v4.45 human approval review decisions and plans a
candidate registry status update as dry-run only. It does not mutate registry
files, mark an asset approved, recommend allocations, create orders, trade,
create an executor, ingest private files, fetch sources, download sources, or
extract facts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ftaw_real_human_approval_review_decision_recorder import (
    FTAWRealHumanApprovalReviewDecisionRecorderPack,
    build_ftaw_real_human_approval_review_decision_recorder_from_files,
)


PROPOSED_REAL_APPROVAL_STATUS = "approved_by_human_review_dry_run"


@dataclass(frozen=True)
class FTAWRealRegistryUpdateDryRunPlan:
    asset_id: str
    current_status: str
    proposed_dry_run_status: str
    dry_run: bool
    registry_mutation: bool
    registry_file_written: bool
    current_status_unchanged: bool
    approved_asset: bool
    allocation_recommendation: bool
    buy_signal: bool
    trade_executed: bool


@dataclass(frozen=True)
class FTAWRealRegistryUpdateDryRunPack:
    target_asset: str
    dry_run_status: str
    upstream_v4_45_status: str
    current_status: str | None
    proposed_dry_run_status: str | None
    dry_run_plan_created: bool
    dry_run_plan: FTAWRealRegistryUpdateDryRunPlan | None
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    dry_run: bool = False
    registry_mutation: bool = False
    registry_file_written: bool = False
    current_status_unchanged: bool = True
    approved_asset: bool = False
    approvals_created: bool = False
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


def _load_assets(path: str | Path) -> tuple[dict[str, Any], ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    assets = raw.get("assets") if isinstance(raw, dict) else None
    if not isinstance(assets, list):
        raise ValueError("candidate registry must contain assets list")
    return tuple(asset for asset in assets if isinstance(asset, dict))


def _find_asset(path: str | Path, asset_id: str) -> dict[str, Any] | None:
    for asset in _load_assets(path):
        if asset.get("asset_id") == asset_id:
            return dict(asset)
    return None


def build_ftaw_real_registry_update_dry_run_pack(
    decision_pack: FTAWRealHumanApprovalReviewDecisionRecorderPack,
    source_registry_path: str | Path,
) -> FTAWRealRegistryUpdateDryRunPack:
    asset = _find_asset(source_registry_path, decision_pack.target_asset)
    current_status = str(asset.get("approval_status")) if asset and asset.get("approval_status") is not None else None
    blocked: list[str] = []

    if asset is None:
        blocked.append(f"{decision_pack.target_asset}: asset not found in registry.")
    if decision_pack.recorder_status != "REAL_HUMAN_APPROVAL_REVIEW_DECISION_RECORDED_FOR_REGISTRY_DRY_RUN":
        blocked.append(f"human approval review decision recorder status is {decision_pack.recorder_status}.")
    if not decision_pack.registry_update_dry_run_ready:
        blocked.append("human approval review decision is not registry-dry-run ready.")
    blocked.extend(decision_pack.blocked_reasons)

    partial_plan_allowed = bool(asset is not None and decision_pack.decision_recorded)
    if not blocked or partial_plan_allowed:
        plan = FTAWRealRegistryUpdateDryRunPlan(
            asset_id=decision_pack.target_asset,
            current_status=current_status or "unknown",
            proposed_dry_run_status=PROPOSED_REAL_APPROVAL_STATUS,
            dry_run=True,
            registry_mutation=False,
            registry_file_written=False,
            current_status_unchanged=True,
            approved_asset=False,
            allocation_recommendation=False,
            buy_signal=False,
            trade_executed=False,
        )
    else:
        plan = None

    if not blocked:
        status = "REAL_REGISTRY_UPDATE_DRY_RUN_READY_FOR_FINAL_AUDIT"
        next_action = "A future final audit may inspect this dry-run plan; no registry mutation occurred."
    elif plan is not None:
        status = "PARTIAL_REAL_REGISTRY_UPDATE_DRY_RUN_READY"
        next_action = "Resolve dry-run blockers before final registry update audit."
    else:
        status = "BLOCKED_NO_REAL_HUMAN_APPROVAL_DECISION"
        next_action = "Resolve v4.45 human approval review decision readiness before registry update dry-run planning."

    return FTAWRealRegistryUpdateDryRunPack(
        target_asset=decision_pack.target_asset,
        dry_run_status=status,
        upstream_v4_45_status=decision_pack.recorder_status,
        current_status=current_status,
        proposed_dry_run_status=plan.proposed_dry_run_status if plan is not None else None,
        dry_run_plan_created=plan is not None,
        dry_run_plan=plan,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        dry_run=plan.dry_run if plan is not None else False,
        registry_mutation=False,
        registry_file_written=False,
        current_status_unchanged=True,
        approved_asset=False,
        approvals_created=False,
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


def build_ftaw_real_registry_update_dry_run_pack_from_files(
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
) -> FTAWRealRegistryUpdateDryRunPack:
    Path(real_registry_update_dry_run_pack_config_path).read_text(encoding="utf-8")
    decision_pack = build_ftaw_real_human_approval_review_decision_recorder_from_files(
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
    return build_ftaw_real_registry_update_dry_run_pack(decision_pack, source_registry_path)
