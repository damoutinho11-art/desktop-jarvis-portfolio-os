"""Portfolio drift diagnostics against policy and approved universe."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .approved_universe import build_approved_universe
from .asset_registry import CandidateAsset, load_asset_registry
from .manual_snapshot_loader import load_manual_snapshot
from .portfolio_policy import (
    PortfolioPolicy,
    PolicyUniverseValidationResult,
    load_portfolio_policy,
    validate_policy_against_approved_universe,
)
from .portfolio_schema import Holding, PortfolioSnapshot
from .portfolio_snapshot_engine import load_account_roles, load_constitution, validate_snapshot


@dataclass(frozen=True)
class PortfolioDriftResult:
    total_portfolio_value_eur: float
    total_investable_value_eur: float
    protected_cash_eur: float
    legacy_value_eur: float
    unapproved_value_eur: float
    test_position_value_eur: float
    sleeve_current_weights: dict[str, float]
    sleeve_target_weights: dict[str, float]
    sleeve_drift: dict[str, float]
    sleeve_band_status: dict[str, str]
    allocation_ready: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "total_portfolio_value_eur": self.total_portfolio_value_eur,
            "total_investable_value_eur": self.total_investable_value_eur,
            "protected_cash_eur": self.protected_cash_eur,
            "legacy_value_eur": self.legacy_value_eur,
            "unapproved_value_eur": self.unapproved_value_eur,
            "test_position_value_eur": self.test_position_value_eur,
            "sleeve_current_weights": self.sleeve_current_weights,
            "sleeve_target_weights": self.sleeve_target_weights,
            "sleeve_drift": self.sleeve_drift,
            "sleeve_band_status": self.sleeve_band_status,
            "allocation_ready": self.allocation_ready,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def _round(value: float) -> float:
    return round(value, 6)


def _asset_lookup(registry_assets: tuple[CandidateAsset, ...]) -> dict[str, CandidateAsset]:
    lookup: dict[str, CandidateAsset] = {}
    for asset in registry_assets:
        for key in (asset.asset_id, asset.ticker, asset.isin_or_symbol):
            if key:
                lookup[key] = asset
    return lookup


def _account_roles(snapshot: PortfolioSnapshot) -> dict[str, str]:
    return {account.account_id: account.role or "unknown" for account in snapshot.accounts}


def _is_protected_cash(holding: Holding, role: str) -> bool:
    if holding.asset_class != "cash":
        return False
    if holding.classification == "investable_surplus":
        return False
    return role in {"protected_cash", "daily_spending", "spending_cash_rewards", "restricted_crypto_external"}


def _band_status(value: float, sleeve) -> str:
    if value == 0:
        return "missing"
    if value < sleeve.min_weight:
        return "below_min"
    if value > sleeve.max_weight:
        return "above_max"
    return "within_band"


def analyze_portfolio_drift(
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
    strict_mode: bool = True,
) -> PortfolioDriftResult:
    account_roles = load_account_roles()
    constitution = load_constitution()
    snapshot, intake_warnings = load_manual_snapshot(snapshot_path, account_roles)
    snapshot_validation = validate_snapshot(snapshot, constitution, account_roles)
    policy = load_portfolio_policy(policy_path)
    registry = load_asset_registry(registry_path)
    approved_universe = build_approved_universe(
        registry_path,
        etf_universe_expected=False,
        crypto_universe_expected=False,
    )
    policy_coverage = validate_policy_against_approved_universe(policy, approved_universe)
    approved_asset_ids = {asset.asset_id for asset in approved_universe.approved_assets}
    registry_lookup = _asset_lookup(registry.assets)
    roles_by_account = _account_roles(snapshot)

    total_value = 0.0
    protected_cash = 0.0
    legacy_value = 0.0
    unapproved_value = 0.0
    test_position_value = 0.0
    sleeve_values = {sleeve.sleeve_id: 0.0 for sleeve in policy.sleeves}
    warnings = [warning.message for warning in intake_warnings]
    warnings.extend(warning.message for warning in snapshot_validation.warnings)
    warnings.extend(policy_coverage.warnings)
    blockers = list(policy_coverage.blockers)

    if not snapshot_validation.validation_passed:
        blockers.append("snapshot validation failed.")

    for holding in snapshot.holdings:
        amount = float(holding.amount)
        total_value += amount
        role = roles_by_account.get(holding.account_id, "unknown")
        if _is_protected_cash(holding, role):
            protected_cash += amount
            continue
        if role == "legacy_cleanup" or holding.classification == "legacy_existing":
            legacy_value += amount
            continue

        asset = registry_lookup.get(holding.asset_symbol)
        if asset is not None and asset.approval_status == "test_position":
            test_position_value += amount
            warnings.append(f"{holding.asset_symbol}: test position excluded from allocation.")
            continue
        if holding.classification == "test_position":
            test_position_value += amount
            warnings.append(f"{holding.asset_symbol}: test position excluded from allocation.")
            continue

        if asset is None:
            if holding.asset_class == "cash" and holding.classification == "investable_surplus":
                sleeve_values["tactical_cash"] = sleeve_values.get("tactical_cash", 0.0) + amount
                continue
            unapproved_value += amount
            warnings.append(f"{holding.asset_symbol}: unknown_unapproved; excluded_from_allocation.")
            continue

        if asset.asset_id not in approved_asset_ids:
            unapproved_value += amount
            warnings.append(f"{holding.asset_symbol}: not approved_investable; excluded_from_allocation.")
            continue

        if asset.sleeve in sleeve_values:
            sleeve_values[asset.sleeve] += amount
        else:
            unapproved_value += amount
            warnings.append(f"{holding.asset_symbol}: approved asset sleeve {asset.sleeve} is not in policy.")

    if strict_mode and unapproved_value > 0:
        blockers.append("strict_mode blocks unknown/unapproved holdings.")

    investable_value = sum(sleeve_values.values())
    sleeve_current_weights = {}
    sleeve_target_weights = {}
    sleeve_drift = {}
    sleeve_band_status = {}
    for sleeve in policy.sleeves:
        current = _round(sleeve_values.get(sleeve.sleeve_id, 0.0) / investable_value) if investable_value else 0.0
        sleeve_current_weights[sleeve.sleeve_id] = current
        sleeve_target_weights[sleeve.sleeve_id] = sleeve.target_weight
        sleeve_drift[sleeve.sleeve_id] = _round(current - sleeve.target_weight)
        sleeve_band_status[sleeve.sleeve_id] = _band_status(current, sleeve)

    return PortfolioDriftResult(
        total_portfolio_value_eur=_round(total_value),
        total_investable_value_eur=_round(investable_value),
        protected_cash_eur=_round(protected_cash),
        legacy_value_eur=_round(legacy_value),
        unapproved_value_eur=_round(unapproved_value),
        test_position_value_eur=_round(test_position_value),
        sleeve_current_weights=sleeve_current_weights,
        sleeve_target_weights=sleeve_target_weights,
        sleeve_drift=sleeve_drift,
        sleeve_band_status=sleeve_band_status,
        allocation_ready=not blockers,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
