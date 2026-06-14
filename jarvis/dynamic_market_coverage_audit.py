"""Dynamic market coverage audit for J.A.R.V.I.S. Portfolio OS.

Report-only coverage check.

This module compares the approved universe against local market data fixtures and
reports whether the dynamic optimizer has enough matching market/risk coverage to
move from PARTIAL_SAFE toward READY_SAFE.

No fetching, no source verification, no broker access, no recommendations, and no
execution are performed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .approved_universe import build_approved_universe
from .market_data_loader import MarketDataError, load_market_data
from .risk_metrics import RiskMetricResult, compute_market_risk_metrics


STATUS_BLOCKED = "DYNAMIC_MARKET_COVERAGE_BLOCKED_SAFE"
STATUS_PARTIAL = "DYNAMIC_MARKET_COVERAGE_PARTIAL_SAFE"
STATUS_READY = "DYNAMIC_MARKET_COVERAGE_READY_SAFE"


@dataclass(frozen=True)
class MarketCoverageRow:
    asset_id: str
    sleeve: str
    asset_type: str
    status: str
    has_market_data: bool
    metric_ready: bool
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "sleeve": self.sleeve,
            "asset_type": self.asset_type,
            "status": self.status,
            "has_market_data": self.has_market_data,
            "metric_ready": self.metric_ready,
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class DynamicMarketCoverageAuditResult:
    status: str
    approved_asset_count: int
    market_metric_count: int
    covered_asset_count: int
    missing_asset_count: int
    degraded_asset_count: int
    rows: tuple[MarketCoverageRow, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    manual_approval_required: bool
    execution_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "approved_asset_count": self.approved_asset_count,
            "market_metric_count": self.market_metric_count,
            "covered_asset_count": self.covered_asset_count,
            "missing_asset_count": self.missing_asset_count,
            "degraded_asset_count": self.degraded_asset_count,
            "rows": [row.to_dict() for row in self.rows],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def _load_market_metrics(market_data_path: str | Path | None) -> tuple[dict[str, RiskMetricResult], list[str], list[str]]:
    blockers: list[str] = []
    warnings: list[str] = []

    if market_data_path is None:
        warnings.append("no market data path supplied.")
        return {}, blockers, warnings

    try:
        snapshot = load_market_data(market_data_path)
    except (FileNotFoundError, MarketDataError, ValueError) as exc:
        blockers.append(f"market data could not be loaded: {exc}")
        return {}, blockers, warnings

    metrics = compute_market_risk_metrics(snapshot)
    return {metric.asset_id: metric for metric in metrics}, blockers, warnings


def audit_dynamic_market_coverage(
    registry_path: str | Path,
    market_data_path: str | Path | None = None,
) -> DynamicMarketCoverageAuditResult:
    blockers: list[str] = []
    warnings: list[str] = []

    universe = build_approved_universe(
        registry_path,
        etf_universe_expected=False,
        crypto_universe_expected=False,
    )
    warnings.extend(universe.warnings)

    metrics_by_asset_id, metric_blockers, metric_warnings = _load_market_metrics(market_data_path)
    blockers.extend(metric_blockers)
    warnings.extend(metric_warnings)

    rows: list[MarketCoverageRow] = []

    for asset in universe.approved_assets:
        metric = metrics_by_asset_id.get(asset.asset_id)

        if metric is None:
            rows.append(
                MarketCoverageRow(
                    asset_id=asset.asset_id,
                    sleeve=asset.sleeve,
                    asset_type=asset.asset_type,
                    status="MISSING_MARKET_DATA",
                    has_market_data=False,
                    metric_ready=False,
                    warnings=(f"{asset.asset_id}: no matching market data series.",),
                )
            )
            continue

        metric_warnings_for_asset = tuple(metric.warnings)
        if metric_warnings_for_asset:
            row_status = "DEGRADED_MARKET_DATA"
            metric_ready = False
        else:
            row_status = "MARKET_DATA_READY"
            metric_ready = True

        rows.append(
            MarketCoverageRow(
                asset_id=asset.asset_id,
                sleeve=asset.sleeve,
                asset_type=asset.asset_type,
                status=row_status,
                has_market_data=True,
                metric_ready=metric_ready,
                warnings=metric_warnings_for_asset,
            )
        )

    if universe.total_approved_assets == 0:
        blockers.append("approved universe is empty.")

    missing_count = sum(1 for row in rows if row.status == "MISSING_MARKET_DATA")
    degraded_count = sum(1 for row in rows if row.status == "DEGRADED_MARKET_DATA")
    covered_count = sum(1 for row in rows if row.has_market_data)

    if blockers:
        status = STATUS_BLOCKED
    elif missing_count or degraded_count:
        status = STATUS_PARTIAL
    else:
        status = STATUS_READY

    if metrics_by_asset_id:
        approved_ids = {asset.asset_id for asset in universe.approved_assets}
        extra_metric_ids = sorted(set(metrics_by_asset_id) - approved_ids)
        if extra_metric_ids:
            warnings.append(f"market data contains non-approved asset ids: {extra_metric_ids}")

    return DynamicMarketCoverageAuditResult(
        status=status,
        approved_asset_count=universe.total_approved_assets,
        market_metric_count=len(metrics_by_asset_id),
        covered_asset_count=covered_count,
        missing_asset_count=missing_count,
        degraded_asset_count=degraded_count,
        rows=tuple(rows),
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
        manual_approval_required=True,
        execution_forbidden=True,
    )
