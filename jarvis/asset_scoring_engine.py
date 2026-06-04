"""Read-only candidate asset scoring engine."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .asset_approval_gate import check_asset_approval
from .asset_registry import CandidateAsset, load_asset_registry
from .asset_scorecard import AssetScorecard
from .portfolio_snapshot_engine import load_simple_yaml


INCOMPLETE_TEXT = {"", "unknown", "UNKNOWN", "manual_placeholder", "n/a", "N/A"}


def clamp_score(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return round(max(minimum, min(maximum, value)), 2)


def load_scoring_rules(path: str | Path = "jarvis/scoring_rules.yaml") -> dict[str, Any]:
    return load_simple_yaml(path)


def _is_incomplete(value: object) -> bool:
    return value is None or (isinstance(value, str) and value.strip() in INCOMPLETE_TEXT)


def _risk_score(asset: CandidateAsset, rules: dict[str, Any]) -> float:
    risk_scores = rules.get("risk_scores", {})
    return float(risk_scores.get(asset.risk_level, 50))


def _portfolio_role_score(asset: CandidateAsset, rules: dict[str, Any]) -> float:
    return 85.0 if asset.sleeve in set(rules.get("preferred_sleeves", [])) else 50.0


def _platform_fit_score(asset: CandidateAsset, rules: dict[str, Any]) -> float:
    preferred = set(rules.get("preferred_platforms", {}).get(asset.asset_type, []))
    if preferred.intersection(asset.platforms):
        return 90.0
    if asset.platforms:
        return 60.0
    return 0.0


def _cost_score(asset: CandidateAsset) -> float:
    multiplier = 200.0 if asset.asset_type == "ETF" else 100.0
    return clamp_score(100.0 - asset.ter_or_fee * multiplier)


def _tax_fit_score(asset: CandidateAsset) -> float:
    if asset.asset_type == "ETF":
        score = 70.0
        if asset.distribution_policy == "accumulating":
            score += 15.0
        if asset.domicile == "Ireland":
            score += 5.0
        if asset.currency != "EUR":
            score -= 20.0
        return clamp_score(score)
    if asset.asset_type == "crypto":
        score = 80.0 if asset.mica_route_possible else 45.0
        if asset.currency != "EUR":
            score -= 15.0
        return clamp_score(score)
    return 60.0


def _data_quality_score(asset: CandidateAsset) -> tuple[float, list[str]]:
    warnings: list[str] = []
    fields: list[tuple[str, object]] = [
        ("ticker", asset.ticker),
        ("isin_or_symbol", asset.isin_or_symbol),
        ("data_source", asset.data_source),
    ]
    if asset.asset_type == "ETF":
        fields.extend(
            [
                ("provider", asset.provider),
                ("index_tracked", asset.index_tracked),
                ("replication_method", asset.replication_method),
            ]
        )
    elif asset.asset_type == "crypto":
        fields.extend(
            [
                ("network_or_protocol", asset.network_or_protocol),
                ("custody_platforms", asset.custody_platforms),
                ("transferable", asset.transferable),
                ("mica_route_possible", asset.mica_route_possible),
            ]
        )

    score = 100.0
    for field_name, value in fields:
        incomplete = False
        if isinstance(value, tuple):
            incomplete = len(value) == 0
        else:
            incomplete = _is_incomplete(value)
        if incomplete:
            score -= 15.0
            warnings.append(f"{asset.asset_id}: {field_name} is incomplete or manually placeholdered.")
    return clamp_score(score), warnings


def _complexity_penalty(asset: CandidateAsset) -> float:
    penalty = 0.0
    if asset.currency != "EUR":
        penalty += 15.0
    if asset.asset_type == "ETF":
        if _is_incomplete(asset.provider) or _is_incomplete(asset.index_tracked):
            penalty += 15.0
        if asset.replication_method and asset.replication_method not in {"physical", "optimized", "unknown"}:
            penalty += 10.0
    elif asset.asset_type == "crypto":
        if asset.transferable is False:
            penalty += 20.0
        if len(asset.custody_platforms) <= 1:
            penalty += 10.0
        if asset.mica_route_possible is False:
            penalty += 20.0
    return clamp_score(penalty)


def _weighted_final_score(breakdown: dict[str, float], rules: dict[str, Any]) -> float:
    weights = rules.get("weights", {})
    positive_keys = (
        "data_quality_score",
        "cost_score",
        "platform_fit_score",
        "tax_fit_score",
        "risk_fit_score",
        "portfolio_role_score",
    )
    positive_weight = sum(float(weights.get(key, 0.0)) for key in positive_keys)
    if positive_weight <= 0:
        return 0.0
    positive_score = sum(breakdown[key] * float(weights.get(key, 0.0)) for key in positive_keys) / positive_weight
    penalty = breakdown["complexity_penalty"] * float(weights.get("complexity_penalty", 0.0))
    bounds = rules.get("score_bounds", {})
    return clamp_score(positive_score - penalty, float(bounds.get("minimum", 0)), float(bounds.get("maximum", 100)))


def score_asset(asset: CandidateAsset, rules: dict[str, Any] | None = None) -> AssetScorecard:
    rules = rules or load_scoring_rules()
    gate_result = check_asset_approval(asset)
    data_quality_score, warnings = _data_quality_score(asset)
    if asset.currency != "EUR":
        warnings.append(f"{asset.asset_id}: currency is {asset.currency}; EUR base currency review required.")

    breakdown = {
        "data_quality_score": data_quality_score,
        "cost_score": _cost_score(asset),
        "platform_fit_score": _platform_fit_score(asset, rules),
        "tax_fit_score": _tax_fit_score(asset),
        "risk_fit_score": _risk_score(asset, rules),
        "portfolio_role_score": _portfolio_role_score(asset, rules),
        "complexity_penalty": _complexity_penalty(asset),
    }
    final_score = _weighted_final_score(breakdown, rules)
    blockers = [] if gate_result.eligible_for_allocation else [gate_result.reason]
    reasons = [
        f"{asset.asset_id}: score generated from offline registry data only.",
        gate_result.reason,
    ]
    return AssetScorecard(
        asset_id=asset.asset_id,
        asset_type=asset.asset_type,
        approval_status=asset.approval_status,
        approved_for_allocation=gate_result.eligible_for_allocation,
        manual_approval_required=True,
        final_candidate_score=final_score,
        score_breakdown=breakdown,
        reasons=tuple(reasons),
        warnings=tuple(warnings),
        blockers=tuple(blockers),
    )


def score_registry(path: str | Path, rules_path: str | Path = "jarvis/scoring_rules.yaml") -> list[AssetScorecard]:
    registry = load_asset_registry(path)
    rules = load_scoring_rules(rules_path)
    scorecards = [score_asset(asset, rules) for asset in registry.assets]
    registry_warnings = [warning.message for warning in registry.warnings]
    if registry_warnings:
        patched: list[AssetScorecard] = []
        warnings_by_asset = {warning.asset_id: warning.message for warning in registry.warnings}
        for scorecard in scorecards:
            warning = warnings_by_asset.get(scorecard.asset_id)
            if warning:
                patched.append(
                    AssetScorecard(
                        asset_id=scorecard.asset_id,
                        asset_type=scorecard.asset_type,
                        approval_status=scorecard.approval_status,
                        approved_for_allocation=scorecard.approved_for_allocation,
                        manual_approval_required=scorecard.manual_approval_required,
                        final_candidate_score=scorecard.final_candidate_score,
                        score_breakdown=scorecard.score_breakdown,
                        reasons=scorecard.reasons,
                        warnings=(*scorecard.warnings, warning),
                        blockers=scorecard.blockers,
                    )
                )
            else:
                patched.append(scorecard)
        return patched
    return scorecards


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Score offline candidate assets without generating recommendations.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.example.json")
    args = parser.parse_args()
    scorecards = [scorecard.to_dict() for scorecard in score_registry(args.registry_path)]
    print(json.dumps(scorecards, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
