"""Dynamic bound market coverage bridge for J.A.R.V.I.S. Portfolio OS.

Report-only bridge.

This module verifies that approved assets have ready source bindings and that
those bindings point to market-data series present in local market fixtures.
It does not fetch, download, verify external truth, connect to brokers, create
buy requests, or execute trades.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .dynamic_market_coverage_audit import STATUS_READY as COVERAGE_READY
from .dynamic_market_coverage_audit import audit_dynamic_market_coverage
from .dynamic_market_source_binding import STATUS_READY as BINDING_READY
from .dynamic_market_source_binding import audit_dynamic_market_source_bindings


STATUS_BLOCKED = "DYNAMIC_BOUND_MARKET_COVERAGE_BLOCKED_SAFE"
STATUS_PARTIAL = "DYNAMIC_BOUND_MARKET_COVERAGE_PARTIAL_SAFE"
STATUS_READY = "DYNAMIC_BOUND_MARKET_COVERAGE_READY_SAFE"


@dataclass(frozen=True)
class BoundMarketCoverageRow:
    asset_id: str
    sleeve: str
    asset_type: str
    status: str
    source_provider: str | None
    source_symbol: str | None
    cache_series_id: str | None
    market_series_present: bool
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "sleeve": self.sleeve,
            "asset_type": self.asset_type,
            "status": self.status,
            "source_provider": self.source_provider,
            "source_symbol": self.source_symbol,
            "cache_series_id": self.cache_series_id,
            "market_series_present": self.market_series_present,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class DynamicBoundMarketCoverageResult:
    status: str
    binding_status: str
    coverage_status: str
    approved_asset_count: int
    bound_series_ready_count: int
    missing_bound_series_count: int
    blocked_binding_count: int
    rows: tuple[BoundMarketCoverageRow, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    execution_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "binding_status": self.binding_status,
            "coverage_status": self.coverage_status,
            "approved_asset_count": self.approved_asset_count,
            "bound_series_ready_count": self.bound_series_ready_count,
            "missing_bound_series_count": self.missing_bound_series_count,
            "blocked_binding_count": self.blocked_binding_count,
            "rows": [row.to_dict() for row in self.rows],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def _load_market_series_ids(path: str | Path) -> tuple[set[str], tuple[str, ...]]:
    warnings: list[str] = []
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as exc:
        return set(), (f"failed to load market data: {exc}",)

    series = raw.get("series", [])
    if not isinstance(series, list):
        return set(), ("market data series must be a list.",)

    ids: set[str] = set()
    for item in series:
        if not isinstance(item, dict):
            warnings.append("ignored non-object market series item.")
            continue
        asset_id = item.get("asset_id")
        if isinstance(asset_id, str) and asset_id.strip():
            ids.add(asset_id.strip())
        else:
            warnings.append("ignored market series item without asset_id.")

    return ids, tuple(warnings)


def audit_dynamic_bound_market_coverage(
    registry_path: str | Path,
    binding_path: str | Path,
    market_data_path: str | Path,
) -> DynamicBoundMarketCoverageResult:
    binding_result = audit_dynamic_market_source_bindings(registry_path, binding_path)
    coverage_result = audit_dynamic_market_coverage(registry_path, market_data_path)
    market_series_ids, market_warnings = _load_market_series_ids(market_data_path)

    warnings: list[str] = []
    blockers: list[str] = []

    warnings.extend(binding_result.warnings)
    warnings.extend(coverage_result.warnings)
    warnings.extend(market_warnings)

    rows: list[BoundMarketCoverageRow] = []
    for binding_row in binding_result.rows:
        row_warnings = list(binding_row.warnings)
        row_blockers = list(binding_row.blockers)
        market_series_present = (
            binding_row.cache_series_id is not None
            and binding_row.cache_series_id in market_series_ids
        )

        if binding_row.status != "BINDING_READY":
            status = "BINDING_NOT_READY"
        elif not market_series_present:
            status = "MISSING_BOUND_MARKET_SERIES"
            row_blockers.append(
                f"{binding_row.asset_id}: bound cache_series_id is not present in market data."
            )
        else:
            status = "BOUND_MARKET_SERIES_READY"

        rows.append(
            BoundMarketCoverageRow(
                asset_id=binding_row.asset_id,
                sleeve=binding_row.sleeve,
                asset_type=binding_row.asset_type,
                status=status,
                source_provider=binding_row.source_provider,
                source_symbol=binding_row.source_symbol,
                cache_series_id=binding_row.cache_series_id,
                market_series_present=market_series_present,
                warnings=tuple(row_warnings),
                blockers=tuple(row_blockers),
            )
        )

    for row in rows:
        blockers.extend(row.blockers)
        warnings.extend(row.warnings)

    if binding_result.status != BINDING_READY:
        blockers.append(f"source binding audit is not ready: {binding_result.status}")
    if coverage_result.status != COVERAGE_READY:
        blockers.append(f"market coverage audit is not ready: {coverage_result.status}")

    ready_count = sum(1 for row in rows if row.status == "BOUND_MARKET_SERIES_READY")
    missing_count = sum(1 for row in rows if row.status == "MISSING_BOUND_MARKET_SERIES")
    blocked_count = sum(1 for row in rows if row.status == "BINDING_NOT_READY")

    if not blockers:
        status = STATUS_READY
    elif ready_count > 0:
        status = STATUS_PARTIAL
    else:
        status = STATUS_BLOCKED

    return DynamicBoundMarketCoverageResult(
        status=status,
        binding_status=binding_result.status,
        coverage_status=coverage_result.status,
        approved_asset_count=binding_result.approved_asset_count,
        bound_series_ready_count=ready_count,
        missing_bound_series_count=missing_count,
        blocked_binding_count=blocked_count,
        rows=tuple(rows),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        manual_approval_required=True,
        execution_forbidden=True,
    )
