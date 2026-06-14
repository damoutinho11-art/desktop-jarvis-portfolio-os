"""Dynamic allocation weekly contribution bridge for J.A.R.V.I.S.

Report-only bridge.

This module takes a dynamic allocation proposal, converts it into a temporary
policy draft, and feeds the existing contribution planner. It does not create
buy requests, grant approvals, write durable files, connect to brokers, or
execute trades.
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contribution_planner import ContributionPlanResult, load_and_plan_contribution
from .dynamic_allocation_optimizer import (
    STATUS_BLOCKED,
    DynamicAllocationResult,
    propose_dynamic_allocation,
)


@dataclass(frozen=True)
class DynamicWeeklyPlanResult:
    optimizer_result: DynamicAllocationResult
    contribution_result: ContributionPlanResult | None
    status: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    manual_approval_required: bool
    execution_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "optimizer_status": self.optimizer_result.status,
            "contribution_status": self.contribution_result.status if self.contribution_result else None,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
            "optimizer": self.optimizer_result.to_dict(),
            "contribution": self.contribution_result.to_dict() if self.contribution_result else None,
        }


def _load_policy_payload(policy_path: str | Path) -> dict[str, Any]:
    return json.loads(Path(policy_path).read_text(encoding="utf-8"))


def _dynamic_policy_payload(
    policy_path: str | Path,
    optimizer_result: DynamicAllocationResult,
) -> dict[str, Any]:
    payload = _load_policy_payload(policy_path)
    payload["policy_id"] = f"{payload.get('policy_id', 'jarvis_policy')}_dynamic_{optimizer_result.horizon}"
    payload["name"] = f"{payload.get('name', 'J.A.R.V.I.S. Portfolio Policy')} Dynamic {optimizer_result.horizon}"
    payload["version"] = f"{payload.get('version', 'unknown')}-dynamic-{optimizer_result.horizon}"
    payload["dynamic_optimizer"] = {
        "status": optimizer_result.status,
        "horizon": optimizer_result.horizon,
        "report_only": True,
        "manual_approval_required": True,
        "execution_forbidden": True,
        "creates_buy_request": False,
    }

    for sleeve in payload.get("sleeves", []):
        sleeve_id = sleeve.get("sleeve_id")
        if sleeve_id in optimizer_result.proposed_targets:
            sleeve["target_weight"] = optimizer_result.proposed_targets[sleeve_id]

    return payload


def _plan_with_temporary_policy(
    plan_path: str | Path,
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
    optimizer_result: DynamicAllocationResult,
) -> ContributionPlanResult:
    payload = _dynamic_policy_payload(policy_path, optimizer_result)

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump(payload, file)
        temporary_policy_path = Path(file.name)

    try:
        return load_and_plan_contribution(
            plan_path=plan_path,
            snapshot_path=snapshot_path,
            policy_path=temporary_policy_path,
            registry_path=registry_path,
        )
    finally:
        temporary_policy_path.unlink(missing_ok=True)


def build_dynamic_weekly_plan(
    horizon: str,
    plan_path: str | Path,
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
    market_data_path: str | Path | None = None,
) -> DynamicWeeklyPlanResult:
    optimizer_result = propose_dynamic_allocation(
        horizon=horizon,
        policy_path=policy_path,
        registry_path=registry_path,
        market_data_path=market_data_path,
    )

    blockers = list(optimizer_result.blockers)
    warnings = list(optimizer_result.warnings)

    if optimizer_result.status == STATUS_BLOCKED:
        return DynamicWeeklyPlanResult(
            optimizer_result=optimizer_result,
            contribution_result=None,
            status="DYNAMIC_WEEKLY_PLAN_BLOCKED_SAFE",
            blockers=tuple(dict.fromkeys(blockers)),
            warnings=tuple(dict.fromkeys(warnings)),
            manual_approval_required=True,
            execution_forbidden=True,
        )

    contribution_result = _plan_with_temporary_policy(
        plan_path=plan_path,
        snapshot_path=snapshot_path,
        policy_path=policy_path,
        registry_path=registry_path,
        optimizer_result=optimizer_result,
    )

    warnings.extend(contribution_result.warnings)
    blockers.extend(contribution_result.blockers)

    if contribution_result.status == "BLOCKED":
        status = "DYNAMIC_WEEKLY_PLAN_BLOCKED_SAFE"
    elif optimizer_result.status.endswith("PARTIAL_SAFE"):
        status = "DYNAMIC_WEEKLY_PLAN_PARTIAL_SAFE"
    else:
        status = "DYNAMIC_WEEKLY_PLAN_READY_SAFE"

    return DynamicWeeklyPlanResult(
        optimizer_result=optimizer_result,
        contribution_result=contribution_result,
        status=status,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
        manual_approval_required=True,
        execution_forbidden=True,
    )
