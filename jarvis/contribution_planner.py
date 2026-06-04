"""Draft-only weekly/monthly contribution planner."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from .approved_universe import ApprovedUniverse, build_approved_universe
from .portfolio_drift import PortfolioDriftResult, analyze_portfolio_drift
from .portfolio_policy import PortfolioPolicy, load_portfolio_policy


ALLOWED_FREQUENCIES = {"weekly", "monthly"}


class ContributionPlanError(ValueError):
    """Raised when contribution plan input is malformed."""


@dataclass(frozen=True)
class ContributionPlanInput:
    plan_id: str
    created_at: str
    contribution_amount_eur: float
    frequency: str
    source_account_id: str | None = None
    strict_mode: bool = True
    manual_approval_required: bool = True


@dataclass(frozen=True)
class PlanLine:
    sleeve_id: str
    asset_id: str
    platform: str
    amount_eur: float
    reason: str

    def to_dict(self) -> dict[str, object]:
        return {
            "sleeve_id": self.sleeve_id,
            "asset_id": self.asset_id,
            "platform": self.platform,
            "amount_eur": self.amount_eur,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class ContributionPlanResult:
    status: str
    contribution_amount_eur: float
    plan_lines: tuple[PlanLine, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    manual_approval_required: bool
    creates_buy_request: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "contribution_amount_eur": self.contribution_amount_eur,
            "plan_lines": [line.to_dict() for line in self.plan_lines],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "manual_approval_required": self.manual_approval_required,
            "creates_buy_request": self.creates_buy_request,
        }


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContributionPlanError(f"{field} exists and must be text.")
    return value.strip()


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _require_text(value, field)


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise ContributionPlanError(f"{field} must be true or false.")
    return value


def _require_number(value: Any, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ContributionPlanError(f"{field} must be a number.")
    return float(value)


def _validate_iso_datetime(value: str) -> str:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContributionPlanError("created_at must be ISO-like datetime text.") from exc
    return value


def parse_contribution_plan(raw: dict[str, Any]) -> ContributionPlanInput:
    if not isinstance(raw, dict):
        raise ContributionPlanError("contribution plan input must be an object.")
    frequency = _require_text(raw.get("frequency"), "frequency")
    if frequency not in ALLOWED_FREQUENCIES:
        raise ContributionPlanError("frequency must be weekly or monthly.")
    return ContributionPlanInput(
        plan_id=_require_text(raw.get("plan_id"), "plan_id"),
        created_at=_validate_iso_datetime(_require_text(raw.get("created_at"), "created_at")),
        contribution_amount_eur=_require_number(raw.get("contribution_amount_eur"), "contribution_amount_eur"),
        frequency=frequency,
        source_account_id=_optional_text(raw.get("source_account_id"), "source_account_id"),
        strict_mode=_require_bool(raw.get("strict_mode", True), "strict_mode"),
        manual_approval_required=_require_bool(raw.get("manual_approval_required"), "manual_approval_required"),
    )


def load_contribution_plan(path: str | Path) -> ContributionPlanInput:
    return parse_contribution_plan(json.loads(Path(path).read_text(encoding="utf-8")))


def _plan_input_blockers(plan: ContributionPlanInput) -> list[str]:
    blockers: list[str] = []
    if plan.contribution_amount_eur <= 0:
        blockers.append("contribution_amount_eur must be > 0.")
    if not plan.manual_approval_required:
        blockers.append("manual_approval_required must be true.")
    return blockers


def _asset_groups_by_sleeve(universe: ApprovedUniverse) -> tuple[dict[str, tuple], list[str]]:
    blockers: list[str] = []
    for sleeve_id, assets in universe.assets_by_sleeve.items():
        if len(assets) > 1 and not any(getattr(asset, "multi_asset_allowed", False) for asset in assets):
            blockers.append(f"{sleeve_id}: multiple approved assets require multi_asset_allowed.")
    return universe.assets_by_sleeve, blockers


def _priority_sleeves(policy: PortfolioPolicy, drift: PortfolioDriftResult) -> list[tuple[str, float]]:
    sleeves = []
    for sleeve in policy.sleeves:
        current = drift.sleeve_current_weights.get(sleeve.sleeve_id, 0.0)
        gap = sleeve.target_weight - current
        if gap <= 0:
            continue
        if drift.sleeve_band_status.get(sleeve.sleeve_id) == "above_max":
            continue
        sleeves.append((sleeve.sleeve_id, gap))
    required = {sleeve.sleeve_id for sleeve in policy.sleeves if sleeve.required}
    return sorted(sleeves, key=lambda item: (item[0] not in required, -item[1], item[0]))


def _platform_for_asset(asset) -> str:
    return asset.platforms[0] if asset.platforms else "unknown"


def _build_lines(
    plan: ContributionPlanInput,
    policy: PortfolioPolicy,
    drift: PortfolioDriftResult,
    universe: ApprovedUniverse,
) -> tuple[PlanLine, ...]:
    remaining = plan.contribution_amount_eur
    plan_lines: list[PlanLine] = []
    sleeve_by_id = policy.sleeve_by_id()
    for sleeve_id, gap in _priority_sleeves(policy, drift):
        assets = universe.assets_by_sleeve.get(sleeve_id, ())
        if not assets:
            continue
        future_total = drift.total_investable_value_eur + plan.contribution_amount_eur
        current_value = drift.sleeve_current_weights.get(sleeve_id, 0.0) * drift.total_investable_value_eur
        target_value = sleeve_by_id[sleeve_id].target_weight * future_total
        amount = min(remaining, max(0.0, target_value - current_value))
        if amount <= 0:
            continue
        per_asset_amount = round(amount / len(assets), 2)
        for index, asset in enumerate(assets):
            line_amount = per_asset_amount
            if index == len(assets) - 1:
                already = per_asset_amount * (len(assets) - 1)
                line_amount = round(amount - already, 2)
            if line_amount > 0:
                plan_lines.append(
                    PlanLine(
                        sleeve_id=sleeve_id,
                        asset_id=asset.asset_id,
                        platform=_platform_for_asset(asset),
                        amount_eur=line_amount,
                        reason=f"Draft allocation of new contribution cash to underweight sleeve {sleeve_id}.",
                    )
                )
        remaining = round(remaining - amount, 2)
        if remaining <= 0:
            break
    return tuple(plan_lines)


def plan_contribution(
    plan: ContributionPlanInput,
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
) -> ContributionPlanResult:
    policy = load_portfolio_policy(policy_path)
    universe = build_approved_universe(registry_path, etf_universe_expected=False, crypto_universe_expected=False)
    drift = analyze_portfolio_drift(snapshot_path, policy_path, registry_path, strict_mode=plan.strict_mode)
    blockers = _plan_input_blockers(plan)
    warnings = list(drift.warnings)
    if not policy.manual_approval_required:
        blockers.append("policy manual_approval_required must be true.")
    if universe.total_approved_assets == 0:
        blockers.append("approved universe is empty.")
    if not drift.allocation_ready:
        blockers.append("portfolio drift allocation_ready is false.")
        blockers.extend(drift.blockers)
    _, multi_asset_blockers = _asset_groups_by_sleeve(universe)
    blockers.extend(multi_asset_blockers)
    blockers = list(dict.fromkeys(blockers))
    if blockers:
        return ContributionPlanResult(
            status="BLOCKED",
            contribution_amount_eur=plan.contribution_amount_eur,
            plan_lines=(),
            blockers=tuple(blockers),
            warnings=tuple(dict.fromkeys(warnings)),
            manual_approval_required=plan.manual_approval_required,
            creates_buy_request=False,
        )
    lines = _build_lines(plan, policy, drift, universe)
    if not lines:
        blockers.append("no eligible underweight approved sleeve available for new contribution cash.")
        return ContributionPlanResult(
            status="BLOCKED",
            contribution_amount_eur=plan.contribution_amount_eur,
            plan_lines=(),
            blockers=tuple(blockers),
            warnings=tuple(dict.fromkeys(warnings)),
            manual_approval_required=plan.manual_approval_required,
            creates_buy_request=False,
        )
    return ContributionPlanResult(
        status="DRAFT_PLAN",
        contribution_amount_eur=plan.contribution_amount_eur,
        plan_lines=lines,
        blockers=(),
        warnings=tuple(dict.fromkeys(warnings)),
        manual_approval_required=True,
        creates_buy_request=False,
    )


def load_and_plan_contribution(
    plan_path: str | Path,
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
) -> ContributionPlanResult:
    return plan_contribution(load_contribution_plan(plan_path), snapshot_path, policy_path, registry_path)
