"""FTAW registry update dry-run planner.

This layer consumes the human approval review decision recorder output and
creates a proposed registry update plan only when the human decision explicitly
allows a registry-update dry-run. It never mutates registry files.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ftaw_human_approval_review_decision_recorder import (
    FTAWHumanApprovalReviewDecisionPack,
    build_ftaw_human_approval_review_decision_pack_from_files,
)


PROPOSED_APPROVAL_STATUS = "approved_by_human_review_dry_run"


@dataclass(frozen=True)
class FTAWRegistryUpdateDryRunPlan:
    asset_id: str
    current_approval_status: str
    proposed_approval_status: str
    proposed_registry_fields: dict[str, Any]
    evidence_coverage_summary: str
    promotion_dry_run_references: tuple[str, ...]
    human_approval_review_decision_reference: str
    registry_update_mode: str = "dry_run"
    registry_mutation: bool = False
    approved_asset: bool = False
    buy_signal: bool = False


@dataclass(frozen=True)
class FTAWRegistryUpdateDryRunPack:
    registry_update_dry_run_status: str
    target_asset: str
    human_decision_status: str
    registry_update_dry_run_ready: bool
    dry_run_plan_created: bool
    current_approval_status: str | None
    proposed_approval_status: str | None
    registry_update_mode: str | None
    registry_mutation: bool
    approved_asset: bool
    buy_signal: bool
    blocked_reasons: tuple[str, ...]
    dry_run_plan: FTAWRegistryUpdateDryRunPlan | None
    no_verified_evidence_promotion: bool = True
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _load_assets(path: str | Path) -> tuple[dict[str, Any], ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    assets = raw.get("assets") if isinstance(raw, dict) else None
    if not isinstance(assets, list):
        raise ValueError("candidate registry must contain assets list.")
    return tuple(asset for asset in assets if isinstance(asset, dict))


def _find_asset(path: str | Path, asset_id: str) -> dict[str, Any] | None:
    for asset in _load_assets(path):
        if asset.get("asset_id") == asset_id:
            return dict(asset)
    return None


def _promotion_references(asset_id: str) -> tuple[str, ...]:
    evidence_types = ("distribution_policy", "exposure_data", "fee_metadata", "fund_metadata", "market_data")
    return tuple(f"{asset_id}:{evidence_type}:dry_run" for evidence_type in evidence_types)


def build_ftaw_registry_update_dry_run_pack(
    decision_pack: FTAWHumanApprovalReviewDecisionPack,
    source_registry_path: str | Path,
) -> FTAWRegistryUpdateDryRunPack:
    asset = _find_asset(source_registry_path, decision_pack.target_asset)
    current_status = asset.get("approval_status") if asset else None
    blocked: list[str] = []

    if asset is None:
        blocked.append(f"{decision_pack.target_asset}: asset not found in registry.")
    if not decision_pack.registry_update_dry_run_ready:
        blocked.append("human approval review decision is not ready for registry-update dry-run.")
    if decision_pack.decision_status != "decision_recorded_for_registry_update_dry_run":
        blocked.append(f"human decision status is {decision_pack.decision_status}.")

    if blocked:
        return FTAWRegistryUpdateDryRunPack(
            registry_update_dry_run_status="BLOCKED",
            target_asset=decision_pack.target_asset,
            human_decision_status=decision_pack.decision_status,
            registry_update_dry_run_ready=decision_pack.registry_update_dry_run_ready,
            dry_run_plan_created=False,
            current_approval_status=current_status,
            proposed_approval_status=None,
            registry_update_mode=None,
            registry_mutation=False,
            approved_asset=False,
            buy_signal=False,
            blocked_reasons=tuple(dict.fromkeys(blocked)),
            dry_run_plan=None,
        )

    assert asset is not None
    references = _promotion_references(decision_pack.target_asset)
    proposed_fields = {
        "approval_status": PROPOSED_APPROVAL_STATUS,
        "approval_status_proposed_only": True,
        "registry_update_mode": "dry_run",
        "human_approval_review_decision_status": decision_pack.decision_status,
    }
    plan = FTAWRegistryUpdateDryRunPlan(
        asset_id=decision_pack.target_asset,
        current_approval_status=str(current_status),
        proposed_approval_status=PROPOSED_APPROVAL_STATUS,
        proposed_registry_fields=proposed_fields,
        evidence_coverage_summary="5 of 5 required evidence types have dry-run planned promotions.",
        promotion_dry_run_references=references,
        human_approval_review_decision_reference=decision_pack.review_packet_id or f"{decision_pack.target_asset}:manual_approval_review",
        registry_update_mode="dry_run",
        registry_mutation=False,
        approved_asset=False,
        buy_signal=False,
    )
    return FTAWRegistryUpdateDryRunPack(
        registry_update_dry_run_status="DRY_RUN_PLANNED",
        target_asset=decision_pack.target_asset,
        human_decision_status=decision_pack.decision_status,
        registry_update_dry_run_ready=True,
        dry_run_plan_created=True,
        current_approval_status=str(current_status),
        proposed_approval_status=PROPOSED_APPROVAL_STATUS,
        registry_update_mode="dry_run",
        registry_mutation=False,
        approved_asset=False,
        buy_signal=False,
        blocked_reasons=(),
        dry_run_plan=plan,
        no_verified_evidence_promotion=True,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_registry_update_dry_run_pack_from_files(
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
) -> FTAWRegistryUpdateDryRunPack:
    Path(registry_update_dry_run_config_path).read_text(encoding="utf-8")
    decision_pack = build_ftaw_human_approval_review_decision_pack_from_files(
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
    )
    return build_ftaw_registry_update_dry_run_pack(decision_pack, source_registry_path)
