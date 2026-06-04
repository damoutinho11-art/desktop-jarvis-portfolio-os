"""Portfolio target policy validation for the read-only J.A.R.V.I.S. kernel."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .approved_universe import ApprovedUniverse, build_approved_universe


TARGET_TOLERANCE = 0.000001


class PortfolioPolicyError(ValueError):
    """Raised when a portfolio policy fixture is malformed or unsafe."""


@dataclass(frozen=True)
class SleevePolicy:
    sleeve_id: str
    name: str
    target_weight: float
    min_weight: float
    max_weight: float
    allowed_asset_types: tuple[str, ...]
    required: bool
    max_assets: int
    notes: str | None = None


@dataclass(frozen=True)
class PortfolioPolicy:
    policy_id: str
    name: str
    version: str
    base_currency: str
    total_investable_target: float
    sleeves: tuple[SleevePolicy, ...]
    constraints: dict[str, Any]
    manual_approval_required: bool

    def sleeve_by_id(self) -> dict[str, SleevePolicy]:
        return {sleeve.sleeve_id: sleeve for sleeve in self.sleeves}


@dataclass(frozen=True)
class PolicyUniverseValidationResult:
    policy: PortfolioPolicy
    approved_universe: ApprovedUniverse
    allocation_ready: bool
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise PortfolioPolicyError(f"{label} must be an object.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PortfolioPolicyError(f"{field} exists and must be text.")
    return value.strip()


def _require_bool(value: Any, field: str) -> bool:
    if not isinstance(value, bool):
        raise PortfolioPolicyError(f"{field} must be true or false.")
    return value


def _require_number(value: Any, field: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise PortfolioPolicyError(f"{field} must be a number.")
    return float(value)


def _require_weight(value: Any, field: str) -> float:
    weight = _require_number(value, field)
    if weight < 0 or weight > 1:
        raise PortfolioPolicyError(f"{field} must be between 0 and 1.")
    return weight


def _require_text_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise PortfolioPolicyError(f"{field} must be a non-empty list.")
    return tuple(_require_text(item, field) for item in value)


def _parse_sleeve(raw: dict[str, Any]) -> SleevePolicy:
    sleeve_id = _require_text(raw.get("sleeve_id"), "sleeve_id")
    target = _require_weight(raw.get("target_weight"), f"{sleeve_id} target_weight")
    minimum = _require_weight(raw.get("min_weight"), f"{sleeve_id} min_weight")
    maximum = _require_weight(raw.get("max_weight"), f"{sleeve_id} max_weight")
    if not minimum <= target <= maximum:
        raise PortfolioPolicyError(f"{sleeve_id} must satisfy min_weight <= target_weight <= max_weight.")
    required = _require_bool(raw.get("required"), f"{sleeve_id} required")
    if required and target == 0:
        raise PortfolioPolicyError(f"{sleeve_id} is required and cannot have target_weight 0.")
    max_assets = raw.get("max_assets")
    if not isinstance(max_assets, int) or isinstance(max_assets, bool) or max_assets <= 0:
        raise PortfolioPolicyError(f"{sleeve_id} max_assets must be a positive integer.")
    notes = raw.get("notes")
    return SleevePolicy(
        sleeve_id=sleeve_id,
        name=_require_text(raw.get("name"), f"{sleeve_id} name"),
        target_weight=target,
        min_weight=minimum,
        max_weight=maximum,
        allowed_asset_types=_require_text_list(raw.get("allowed_asset_types"), f"{sleeve_id} allowed_asset_types"),
        required=required,
        max_assets=max_assets,
        notes=_require_text(notes, f"{sleeve_id} notes") if notes is not None else None,
    )


def _validate_constraints(constraints: dict[str, Any]) -> None:
    if _require_bool(constraints.get("no_leverage"), "no_leverage") is not True:
        raise PortfolioPolicyError("no_leverage must be true.")
    if _require_bool(constraints.get("no_auto_execution"), "no_auto_execution") is not True:
        raise PortfolioPolicyError("no_auto_execution must be true.")
    if _require_weight(constraints.get("max_total_crypto_weight"), "max_total_crypto_weight") > 0.25:
        raise PortfolioPolicyError("max_total_crypto_weight must be <= 0.25.")
    if _require_weight(constraints.get("max_speculative_crypto_weight"), "max_speculative_crypto_weight") > 0.10:
        raise PortfolioPolicyError("max_speculative_crypto_weight must be <= 0.10.")
    _require_weight(constraints.get("max_single_asset_weight"), "max_single_asset_weight")
    _require_weight(constraints.get("max_high_risk_weight"), "max_high_risk_weight")
    if _require_number(constraints.get("min_emergency_cash_eur"), "min_emergency_cash_eur") < 0:
        raise PortfolioPolicyError("min_emergency_cash_eur must be >= 0.")


def load_portfolio_policy(path: str | Path) -> PortfolioPolicy:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "portfolio policy")
    base_currency = _require_text(raw.get("base_currency"), "base_currency")
    if base_currency != "EUR":
        raise PortfolioPolicyError("base_currency must be EUR.")
    manual_approval_required = _require_bool(raw.get("manual_approval_required"), "manual_approval_required")
    if not manual_approval_required:
        raise PortfolioPolicyError("manual_approval_required must be true.")
    constraints = _require_mapping(raw.get("constraints"), "constraints")
    _validate_constraints(constraints)

    raw_sleeves = raw.get("sleeves")
    if not isinstance(raw_sleeves, list) or not raw_sleeves:
        raise PortfolioPolicyError("sleeves must be a non-empty list.")
    sleeves = tuple(_parse_sleeve(_require_mapping(item, "sleeve")) for item in raw_sleeves)
    sleeve_ids = [sleeve.sleeve_id for sleeve in sleeves]
    if len(set(sleeve_ids)) != len(sleeve_ids):
        raise PortfolioPolicyError("sleeve_id values must be unique.")
    total_target = sum(sleeve.target_weight for sleeve in sleeves)
    if abs(total_target - 1.0) > TARGET_TOLERANCE:
        raise PortfolioPolicyError("target weights must sum to 1.0.")

    return PortfolioPolicy(
        policy_id=_require_text(raw.get("policy_id"), "policy_id"),
        name=_require_text(raw.get("name"), "name"),
        version=_require_text(raw.get("version"), "version"),
        base_currency=base_currency,
        total_investable_target=_require_number(raw.get("total_investable_target"), "total_investable_target"),
        sleeves=sleeves,
        constraints=constraints,
        manual_approval_required=manual_approval_required,
    )


def validate_policy_against_approved_universe(
    policy: PortfolioPolicy,
    approved_universe: ApprovedUniverse,
) -> PolicyUniverseValidationResult:
    warnings: list[str] = list(approved_universe.warnings)
    blockers: list[str] = []
    sleeve_by_id = policy.sleeve_by_id()

    if approved_universe.total_approved_assets == 0:
        blockers.append("approved universe is empty.")

    for sleeve in policy.sleeves:
        approved_assets = approved_universe.assets_by_sleeve.get(sleeve.sleeve_id, ())
        if sleeve.required and not approved_assets:
            message = f"required sleeve {sleeve.sleeve_id} has no approved asset."
            warnings.append(message)
            blockers.append(message)
        if len(approved_assets) > sleeve.max_assets and not any(
            getattr(asset, "multi_asset_allowed", False) for asset in approved_assets
        ):
            warnings.append(f"{sleeve.sleeve_id}: more approved assets than max_assets.")

    for asset in approved_universe.approved_assets:
        if asset.sleeve not in sleeve_by_id:
            warnings.append(f"{asset.asset_id}: approved asset sleeve {asset.sleeve} does not exist in policy.")

    return PolicyUniverseValidationResult(
        policy=policy,
        approved_universe=approved_universe,
        allocation_ready=not blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
    )


def load_policy_and_validate_universe(
    policy_path: str | Path,
    registry_path: str | Path,
) -> PolicyUniverseValidationResult:
    policy = load_portfolio_policy(policy_path)
    universe = build_approved_universe(registry_path, etf_universe_expected=False, crypto_universe_expected=False)
    return validate_policy_against_approved_universe(policy, universe)
