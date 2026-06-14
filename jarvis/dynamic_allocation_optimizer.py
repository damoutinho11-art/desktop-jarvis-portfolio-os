"""Dynamic allocation optimizer for J.A.R.V.I.S. Portfolio OS.

Report-only v1.5 bridge.

This module proposes horizon-aware target sleeve weights inside the existing
portfolio policy boundaries. It does not create buy requests, approvals, broker
orders, recommendations, trades, registry mutations, or file writes.

The output is a proposed policy draft for manual review only.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .approved_universe import build_approved_universe
from .asset_scoring_engine import score_registry
from .market_data_loader import MarketDataError, load_market_data
from .portfolio_policy import PortfolioPolicy, load_portfolio_policy
from .risk_metrics import RiskMetricResult, compute_market_risk_metrics


STATUS_BLOCKED = "DYNAMIC_POLICY_BLOCKED_SAFE"
STATUS_PARTIAL = "DYNAMIC_POLICY_PARTIAL_SAFE"
STATUS_READY = "DYNAMIC_POLICY_READY_SAFE"

SUPPORTED_HORIZONS = {"5y", "10y", "20y"}

BASELINE_TARGETS = {
    "5y": {
        "global_core": 0.50,
        "growth_innovation": 0.15,
        "quality_factor": 0.10,
        "crypto_core": 0.10,
        "speculative_crypto": 0.05,
        "tactical_cash": 0.10,
    },
    "10y": {
        "global_core": 0.425,
        "growth_innovation": 0.20,
        "quality_factor": 0.10,
        "crypto_core": 0.15,
        "speculative_crypto": 0.075,
        "tactical_cash": 0.05,
    },
    "20y": {
        "global_core": 0.35,
        "growth_innovation": 0.25,
        "quality_factor": 0.10,
        "crypto_core": 0.15,
        "speculative_crypto": 0.10,
        "tactical_cash": 0.05,
    },
}

SLEEVE_RISK_WEIGHTS = {
    "global_core": 0.25,
    "growth_innovation": 0.35,
    "quality_factor": 0.20,
    "crypto_core": 0.45,
    "speculative_crypto": 0.60,
    "tactical_cash": 0.00,
}


@dataclass(frozen=True)
class DynamicAllocationResult:
    status: str
    horizon: str
    proposed_targets: dict[str, float]
    baseline_targets: dict[str, float]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    reasons: tuple[str, ...]
    approved_asset_count: int
    scored_asset_count: int
    risk_metric_count: int
    manual_approval_required: bool
    execution_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "horizon": self.horizon,
            "proposed_targets": self.proposed_targets,
            "baseline_targets": self.baseline_targets,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "reasons": list(self.reasons),
            "approved_asset_count": self.approved_asset_count,
            "scored_asset_count": self.scored_asset_count,
            "risk_metric_count": self.risk_metric_count,
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def _round_weight(value: float) -> float:
    return round(value, 6)


def _score_by_asset_id(registry_path: str | Path) -> dict[str, float]:
    scorecards = score_registry(registry_path)
    return {
        scorecard.asset_id: float(scorecard.final_candidate_score)
        for scorecard in scorecards
        if scorecard.approved_for_allocation
    }


def _risk_by_asset_id(market_data_path: str | Path | None) -> tuple[dict[str, RiskMetricResult], list[str]]:
    if market_data_path is None:
        return {}, ["no market data path supplied; optimizer falls back to score/policy baseline only."]

    try:
        snapshot = load_market_data(market_data_path)
    except (FileNotFoundError, MarketDataError, ValueError) as exc:
        return {}, [f"market data unavailable: {exc}"]

    metrics = compute_market_risk_metrics(snapshot)
    return {metric.asset_id: metric for metric in metrics}, []


def _sleeve_asset_scores(policy: PortfolioPolicy, registry_path: str | Path) -> dict[str, float]:
    universe = build_approved_universe(
        registry_path,
        etf_universe_expected=False,
        crypto_universe_expected=False,
    )
    asset_scores = _score_by_asset_id(registry_path)
    sleeve_scores: dict[str, list[float]] = {}

    for asset in universe.approved_assets:
        score = asset_scores.get(asset.asset_id)
        if score is not None:
            sleeve_scores.setdefault(asset.sleeve, []).append(score)

    averaged: dict[str, float] = {}
    for sleeve in policy.sleeves:
        scores = sleeve_scores.get(sleeve.sleeve_id, [])
        if scores:
            averaged[sleeve.sleeve_id] = sum(scores) / len(scores)
        else:
            averaged[sleeve.sleeve_id] = 50.0

    return averaged


def _sleeve_risk_adjustment(
    policy: PortfolioPolicy,
    registry_path: str | Path,
    risk_metrics: dict[str, RiskMetricResult],
) -> dict[str, float]:
    universe = build_approved_universe(
        registry_path,
        etf_universe_expected=False,
        crypto_universe_expected=False,
    )

    adjustments = {sleeve.sleeve_id: 0.0 for sleeve in policy.sleeves}
    counts = {sleeve.sleeve_id: 0 for sleeve in policy.sleeves}

    for asset in universe.approved_assets:
        metric = risk_metrics.get(asset.asset_id)
        if metric is None:
            continue

        score = 0.0

        if metric.return_12m is not None:
            if metric.return_12m > 0.25:
                score += 0.015
            elif metric.return_12m > 0.10:
                score += 0.010
            elif metric.return_12m < -0.10:
                score -= 0.015

        if metric.annualized_volatility is not None:
            if metric.annualized_volatility > 0.80:
                score -= 0.020
            elif metric.annualized_volatility > 0.40:
                score -= 0.010

        if metric.max_drawdown < -0.30:
            score -= 0.020
        elif metric.max_drawdown < -0.15:
            score -= 0.010

        if metric.distance_from_high < -0.20:
            score -= 0.010

        adjustments[asset.sleeve] = adjustments.get(asset.sleeve, 0.0) + score
        counts[asset.sleeve] = counts.get(asset.sleeve, 0) + 1

    for sleeve_id, count in counts.items():
        if count > 0:
            adjustments[sleeve_id] = adjustments[sleeve_id] / count

    return adjustments


def _apply_policy_bounds(policy: PortfolioPolicy, targets: dict[str, float]) -> dict[str, float]:
    bounded: dict[str, float] = {}
    sleeve_by_id = policy.sleeve_by_id()

    for sleeve_id, target in targets.items():
        sleeve = sleeve_by_id[sleeve_id]
        bounded[sleeve_id] = min(max(target, sleeve.min_weight), sleeve.max_weight)

    total = sum(bounded.values())
    if total <= 0:
        return bounded

    normalized = {sleeve_id: value / total for sleeve_id, value in bounded.items()}

    # Second pass after normalization to avoid violating hard min/max too much.
    for sleeve_id, value in list(normalized.items()):
        sleeve = sleeve_by_id[sleeve_id]
        normalized[sleeve_id] = min(max(value, sleeve.min_weight), sleeve.max_weight)

    total = sum(normalized.values())
    if total > 0:
        normalized = {sleeve_id: _round_weight(value / total) for sleeve_id, value in normalized.items()}

    return normalized


def _enforce_crypto_caps(policy: PortfolioPolicy, targets: dict[str, float]) -> tuple[dict[str, float], list[str]]:
    constraints = policy.constraints
    warnings: list[str] = []
    adjusted = dict(targets)

    crypto_sleeves = ["crypto_core", "speculative_crypto"]
    total_crypto = sum(adjusted.get(sleeve, 0.0) for sleeve in crypto_sleeves)
    max_total_crypto = float(constraints.get("max_total_crypto_weight", 0.25))
    if total_crypto > max_total_crypto:
        scale = max_total_crypto / total_crypto
        freed = 0.0
        for sleeve in crypto_sleeves:
            old = adjusted.get(sleeve, 0.0)
            new = old * scale
            adjusted[sleeve] = new
            freed += old - new
        adjusted["global_core"] = adjusted.get("global_core", 0.0) + freed
        warnings.append("total crypto cap enforced; excess moved to global_core.")

    max_spec = float(constraints.get("max_speculative_crypto_weight", 0.10))
    spec = adjusted.get("speculative_crypto", 0.0)
    if spec > max_spec:
        freed = spec - max_spec
        adjusted["speculative_crypto"] = max_spec
        adjusted["global_core"] = adjusted.get("global_core", 0.0) + freed
        warnings.append("speculative crypto cap enforced; excess moved to global_core.")

    total = sum(adjusted.values())
    if total > 0:
        adjusted = {sleeve_id: _round_weight(value / total) for sleeve_id, value in adjusted.items()}

    return adjusted, warnings


def propose_dynamic_allocation(
    horizon: str,
    policy_path: str | Path,
    registry_path: str | Path,
    market_data_path: str | Path | None = None,
) -> DynamicAllocationResult:
    blockers: list[str] = []
    warnings: list[str] = []
    reasons: list[str] = []

    horizon = str(horizon).strip().lower()
    if horizon not in SUPPORTED_HORIZONS:
        blockers.append("horizon must be one of: 5y, 10y, 20y")
        horizon = "10y"

    policy = load_portfolio_policy(policy_path)
    universe = build_approved_universe(
        registry_path,
        etf_universe_expected=False,
        crypto_universe_expected=False,
    )

    if not policy.manual_approval_required:
        blockers.append("policy manual_approval_required must be true.")
    if universe.total_approved_assets == 0:
        blockers.append("approved universe is empty.")

    required_sleeves = {sleeve.sleeve_id for sleeve in policy.sleeves if sleeve.required}
    approved_sleeves = set(universe.assets_by_sleeve)
    missing_required = sorted(required_sleeves - approved_sleeves)
    for sleeve_id in missing_required:
        blockers.append(f"required sleeve {sleeve_id} has no approved asset.")

    baseline = dict(BASELINE_TARGETS[horizon])
    sleeve_scores = _sleeve_asset_scores(policy, registry_path)
    risk_metrics, risk_warnings = _risk_by_asset_id(market_data_path)
    warnings.extend(risk_warnings)

    approved_asset_ids = {asset.asset_id for asset in universe.approved_assets}
    risk_covered_asset_ids = approved_asset_ids & set(risk_metrics)
    if risk_metrics and not risk_covered_asset_ids:
        warnings.append("market data has no matching approved asset IDs; optimizer uses score/policy baseline only.")
    elif risk_metrics and risk_covered_asset_ids != approved_asset_ids:
        missing = sorted(approved_asset_ids - risk_covered_asset_ids)
        warnings.append(f"market data missing approved asset metrics: {missing}")

    risk_adjustments = _sleeve_risk_adjustment(policy, registry_path, risk_metrics)

    proposed = dict(baseline)

    for sleeve in policy.sleeves:
        sleeve_id = sleeve.sleeve_id
        score = sleeve_scores.get(sleeve_id, 50.0)
        score_adjustment = ((score - 50.0) / 50.0) * 0.025
        risk_adjustment = risk_adjustments.get(sleeve_id, 0.0)
        risk_budget = SLEEVE_RISK_WEIGHTS.get(sleeve_id, 0.0)
        proposed[sleeve_id] = proposed.get(sleeve_id, sleeve.target_weight) + score_adjustment + risk_adjustment

        if risk_budget > 0 and not any(asset.sleeve == sleeve_id and asset.asset_id in risk_metrics for asset in universe.approved_assets):
            warnings.append(f"{sleeve_id}: no matching market risk metric for approved asset; using score/baseline only.")

    proposed = _apply_policy_bounds(policy, proposed)
    proposed, cap_warnings = _enforce_crypto_caps(policy, proposed)
    warnings.extend(cap_warnings)

    total = sum(proposed.values())
    if abs(total - 1.0) > 0.00001:
        blockers.append(f"proposed targets must sum to 1.0, got {total:.6f}")

    if market_data_path is None or not risk_metrics:
        status = STATUS_PARTIAL
        reasons.append("dynamic allocation generated with incomplete market/risk data.")
    elif not risk_covered_asset_ids:
        status = STATUS_PARTIAL
        reasons.append("dynamic allocation generated without matching approved-asset market/risk data.")
    elif risk_covered_asset_ids != approved_asset_ids:
        status = STATUS_PARTIAL
        reasons.append("dynamic allocation generated with partial approved-asset market/risk data.")
    else:
        status = STATUS_READY
        reasons.append("dynamic allocation generated with complete approved-asset market/risk data.")

    if blockers:
        status = STATUS_BLOCKED

    reasons.extend(
        [
            "baseline horizon profile adjusted by approved asset scorecards.",
            "risk metrics adjust sleeve weights only when approved asset IDs match market data.",
            "policy min/max sleeve bounds are enforced.",
            "crypto and speculative hard caps are enforced.",
            "manual approval remains required.",
            "execution is forbidden.",
        ]
    )

    return DynamicAllocationResult(
        status=status,
        horizon=horizon,
        proposed_targets=dict(sorted(proposed.items())),
        baseline_targets=dict(sorted(baseline.items())),
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings + list(universe.warnings))),
        reasons=tuple(dict.fromkeys(reasons)),
        approved_asset_count=universe.total_approved_assets,
        scored_asset_count=len(_score_by_asset_id(registry_path)),
        risk_metric_count=len(risk_metrics),
        manual_approval_required=True,
        execution_forbidden=True,
    )
