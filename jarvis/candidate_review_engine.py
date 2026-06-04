"""Build read-only candidate review packs from local evidence fixtures."""

from __future__ import annotations

import json
from pathlib import Path

from .asset_approval_gate import check_asset_approval
from .asset_registry import CandidateAsset, load_asset_registry
from .asset_scorecard import AssetScorecard
from .asset_scoring_engine import score_asset, score_registry
from .candidate_review_pack import CandidateReviewPack
from .concentration_engine import calculate_combined_top_holdings
from .exposure_loader import AssetExposure, ExposureSnapshot, load_exposure_data
from .market_data_loader import load_market_data
from .risk_metrics import RiskMetricResult, compute_market_risk_metrics


def _market_summary(metric: RiskMetricResult | None) -> dict[str, object] | None:
    if metric is None:
        return None
    return {
        "latest_price": metric.latest_price,
        "return_1m": metric.return_1m,
        "return_3m": metric.return_3m,
        "return_6m": metric.return_6m,
        "return_12m": metric.return_12m,
        "annualized_volatility": metric.annualized_volatility,
        "max_drawdown": metric.max_drawdown,
        "data_points": metric.data_points,
        "latest_date": metric.latest_date,
    }


def _exposure_summary(asset: AssetExposure | None) -> dict[str, object] | None:
    if asset is None:
        return None
    top_holdings = calculate_combined_top_holdings({asset.asset_id: 1.0}, {asset.asset_id: asset})[:5]
    return {
        "holding_count": len(asset.holdings),
        "country_count": len(asset.countries),
        "sector_count": len(asset.sectors),
        "top_holdings": [{"name": name, "weight": weight} for name, weight in top_holdings],
    }


def _missing_market_is_hard_blocker(asset: CandidateAsset) -> bool:
    return asset.asset_type in {"ETF", "crypto"} and asset.approval_status not in {"legacy_existing", "test_position"}


def _missing_exposure_is_hard_blocker(asset: CandidateAsset) -> bool:
    return asset.asset_type == "ETF" and asset.approval_status not in {"legacy_existing", "test_position"}


def build_candidate_review_pack(
    asset: CandidateAsset,
    scorecard: AssetScorecard | None,
    market_metric: RiskMetricResult | None,
    exposure: AssetExposure | None,
    exposure_snapshot: ExposureSnapshot | None = None,
) -> CandidateReviewPack:
    gate = check_asset_approval(asset)
    warnings: list[str] = []
    blockers: list[str] = []

    if scorecard is None:
        return CandidateReviewPack(
            asset_id=asset.asset_id,
            asset_type=asset.asset_type,
            sleeve=asset.sleeve,
            approval_status=asset.approval_status,
            approved_for_allocation=gate.eligible_for_allocation,
            final_candidate_score=None,
            market_metrics_summary=_market_summary(market_metric),
            exposure_summary=_exposure_summary(exposure),
            warnings=tuple(warnings),
            blockers=("missing scorecard.",),
            review_status="blocked_missing_scorecard",
            can_submit_for_manual_approval=False,
            manual_approval_required=True,
        )

    warnings.extend(scorecard.warnings)
    if not gate.eligible_for_allocation:
        blockers.append(gate.reason)

    if market_metric is None:
        message = f"{asset.asset_id}: missing market data evidence."
        if _missing_market_is_hard_blocker(asset):
            blockers.append(message)
            review_status = "blocked_missing_market_data"
        else:
            warnings.append(message)
            review_status = "review_ready"
    elif exposure is None and _missing_exposure_is_hard_blocker(asset):
        blockers.append(f"{asset.asset_id}: missing exposure data evidence.")
        review_status = "blocked_missing_exposure_data"
    elif asset.approval_status == "rejected":
        review_status = "blocked_by_approval_gate"
    elif gate.eligible_for_allocation:
        review_status = "manual_decision_required"
    else:
        review_status = "review_ready"

    if exposure_snapshot is not None:
        warnings.extend(warning for warning in exposure_snapshot.warnings if warning.startswith(f"{asset.asset_id}:"))
    if market_metric is not None:
        warnings.extend(market_metric.warnings)
    if exposure is None and asset.asset_type == "crypto":
        warnings.append(f"{asset.asset_id}: ETF-style exposure data not required for crypto review readiness.")

    hard_blocked = review_status.startswith("blocked_")
    can_submit = not hard_blocked and scorecard is not None
    return CandidateReviewPack(
        asset_id=asset.asset_id,
        asset_type=asset.asset_type,
        sleeve=asset.sleeve,
        approval_status=asset.approval_status,
        approved_for_allocation=gate.eligible_for_allocation,
        final_candidate_score=scorecard.final_candidate_score,
        market_metrics_summary=_market_summary(market_metric),
        exposure_summary=_exposure_summary(exposure),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        review_status=review_status,
        can_submit_for_manual_approval=can_submit,
        manual_approval_required=True,
    )


def build_candidate_review_packs(
    registry_path: str | Path,
    market_data_path: str | Path | None = None,
    exposure_path: str | Path | None = None,
) -> list[CandidateReviewPack]:
    registry = load_asset_registry(registry_path)
    scorecards = {scorecard.asset_id: scorecard for scorecard in score_registry(registry_path)}
    market_metrics = {}
    if market_data_path is not None:
        market_metrics = {
            metric.asset_id: metric for metric in compute_market_risk_metrics(load_market_data(market_data_path))
        }
    exposure_snapshot = load_exposure_data(exposure_path) if exposure_path is not None else None
    exposures = exposure_snapshot.by_asset_id() if exposure_snapshot is not None else {}
    return [
        build_candidate_review_pack(
            asset,
            scorecards.get(asset.asset_id),
            market_metrics.get(asset.asset_id),
            exposures.get(asset.asset_id),
            exposure_snapshot,
        )
        for asset in registry.assets
    ]


def write_review_pack_json(
    packs: list[CandidateReviewPack],
    path: str | Path = "jarvis/data/candidate_review.example.json",
) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"review_packs": [pack.to_dict() for pack in packs]}
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return output_path
