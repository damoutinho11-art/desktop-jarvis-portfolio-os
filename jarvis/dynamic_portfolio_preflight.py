"""Dynamic portfolio preflight for J.A.R.V.I.S. Portfolio OS.

Report-only operator preflight.

This module aggregates the dynamic market source binding bridge and dynamic
weekly plan bridge into one operator-facing readiness check.

It does not fetch market data, verify external truth, connect to brokers, create
buy requests, approve assets, or execute trades.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .dynamic_allocation_weekly_plan import build_dynamic_weekly_plan
from .dynamic_bound_market_coverage import (
    STATUS_READY as BOUND_MARKET_READY,
    audit_dynamic_bound_market_coverage,
)


STATUS_BLOCKED = "DYNAMIC_PORTFOLIO_PREFLIGHT_BLOCKED_SAFE"
STATUS_READY = "DYNAMIC_PORTFOLIO_PREFLIGHT_READY_SAFE"

WEEKLY_PLAN_READY = "DYNAMIC_WEEKLY_PLAN_READY_SAFE"


@dataclass(frozen=True)
class DynamicPortfolioPreflightResult:
    status: str
    horizon: str
    bound_market_status: str
    binding_status: str
    coverage_status: str
    weekly_plan_status: str
    optimizer_status: str
    contribution_status: str
    dynamic_target_weights: dict[str, float]
    weekly_plan_lines: tuple[dict[str, Any], ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    execution_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "horizon": self.horizon,
            "bound_market_status": self.bound_market_status,
            "binding_status": self.binding_status,
            "coverage_status": self.coverage_status,
            "weekly_plan_status": self.weekly_plan_status,
            "optimizer_status": self.optimizer_status,
            "contribution_status": self.contribution_status,
            "dynamic_target_weights": dict(self.dynamic_target_weights),
            "weekly_plan_lines": list(self.weekly_plan_lines),
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def _first_dict_value(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = data.get(key)
        if value is not None:
            return value
    return None


def _first_attr_value(value: Any, keys: tuple[str, ...]) -> Any:
    for key in keys:
        item = getattr(value, key, None)
        if item is not None:
            return item
    return None


def _plan_line_to_dict(line: Any) -> dict[str, Any]:
    if hasattr(line, "to_dict"):
        raw = line.to_dict()
        if isinstance(raw, dict):
            data = dict(raw)
        else:
            data = {}
    elif isinstance(line, dict):
        data = dict(line)
    else:
        data = {}

    if data:
        sleeve = _first_dict_value(data, ("sleeve", "sleeve_id", "target_sleeve", "target_sleeve_id"))
        asset_id = _first_dict_value(data, ("asset_id", "target_asset_id", "candidate_id"))
        platform = _first_dict_value(data, ("platform", "target_platform", "broker", "venue"))
        amount_eur = _first_dict_value(data, ("amount_eur", "eur_amount", "draft_amount_eur"))
        reason = _first_dict_value(data, ("reason", "rationale", "draft_reason"))
        data.update(
            {
                "sleeve": sleeve,
                "asset_id": asset_id,
                "platform": platform,
                "amount_eur": amount_eur,
                "reason": reason,
            }
        )
        return data

    return {
        "sleeve": _first_attr_value(line, ("sleeve", "sleeve_id", "target_sleeve", "target_sleeve_id")),
        "asset_id": _first_attr_value(line, ("asset_id", "target_asset_id", "candidate_id")),
        "platform": _first_attr_value(line, ("platform", "target_platform", "broker", "venue")),
        "amount_eur": _first_attr_value(line, ("amount_eur", "eur_amount", "draft_amount_eur")),
        "reason": _first_attr_value(line, ("reason", "rationale", "draft_reason")),
    }


def run_dynamic_portfolio_preflight(
    horizon: str,
    plan_path: str | Path,
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
    binding_path: str | Path,
    market_data_path: str | Path,
) -> DynamicPortfolioPreflightResult:
    bound_result = audit_dynamic_bound_market_coverage(
        registry_path=registry_path,
        binding_path=binding_path,
        market_data_path=market_data_path,
    )
    weekly_result = build_dynamic_weekly_plan(
        horizon=horizon,
        plan_path=plan_path,
        snapshot_path=snapshot_path,
        policy_path=policy_path,
        registry_path=registry_path,
        market_data_path=market_data_path,
    )

    optimizer_result = weekly_result.optimizer_result
    contribution_result = weekly_result.contribution_result

    warnings: list[str] = []
    blockers: list[str] = []

    warnings.extend(bound_result.warnings)
    warnings.extend(getattr(weekly_result, "warnings", ()))
    blockers.extend(bound_result.blockers)
    blockers.extend(getattr(weekly_result, "blockers", ()))

    if bound_result.status != BOUND_MARKET_READY:
        blockers.append(f"bound market coverage is not ready: {bound_result.status}")
    if weekly_result.status != WEEKLY_PLAN_READY:
        blockers.append(f"dynamic weekly plan is not ready: {weekly_result.status}")

    status = STATUS_READY if not blockers else STATUS_BLOCKED

    plan_lines = tuple(
        _plan_line_to_dict(line)
        for line in getattr(contribution_result, "plan_lines", ())
    )

    return DynamicPortfolioPreflightResult(
        status=status,
        horizon=horizon,
        bound_market_status=bound_result.status,
        binding_status=bound_result.binding_status,
        coverage_status=bound_result.coverage_status,
        weekly_plan_status=weekly_result.status,
        optimizer_status=optimizer_result.status,
        contribution_status=contribution_result.status,
        dynamic_target_weights=dict(optimizer_result.proposed_targets),
        weekly_plan_lines=plan_lines,
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        manual_approval_required=True,
        execution_forbidden=True,
    )
