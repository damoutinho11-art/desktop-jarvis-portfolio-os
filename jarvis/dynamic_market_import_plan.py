"""Dynamic market import plan for J.A.R.V.I.S. Portfolio OS.

Report-only import planner.

This module converts approved asset market source bindings into explicit
market-data import requirements. It does not fetch, download, scrape, call APIs,
connect to brokers, create buy requests, approve assets, mutate registries, or
execute trades.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .dynamic_market_source_binding import (
    STATUS_READY as SOURCE_BINDING_READY,
    audit_dynamic_market_source_bindings,
)


STATUS_BLOCKED = "DYNAMIC_MARKET_IMPORT_PLAN_BLOCKED_SAFE"
STATUS_READY = "DYNAMIC_MARKET_IMPORT_PLAN_READY_SAFE"


@dataclass(frozen=True)
class DynamicMarketImportPlanRow:
    asset_id: str
    sleeve: str
    asset_type: str
    source_provider: str | None
    source_symbol: str | None
    cache_series_id: str | None
    expected_currency: str | None
    planned_market_series_id: str | None
    status: str
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "sleeve": self.sleeve,
            "asset_type": self.asset_type,
            "source_provider": self.source_provider,
            "source_symbol": self.source_symbol,
            "cache_series_id": self.cache_series_id,
            "expected_currency": self.expected_currency,
            "planned_market_series_id": self.planned_market_series_id,
            "status": self.status,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class DynamicMarketImportPlanResult:
    status: str
    source_binding_status: str
    approved_asset_count: int
    import_plan_row_count: int
    ready_row_count: int
    blocked_row_count: int
    rows: tuple[DynamicMarketImportPlanRow, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    execution_forbidden: bool
    fetching_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "source_binding_status": self.source_binding_status,
            "approved_asset_count": self.approved_asset_count,
            "import_plan_row_count": self.import_plan_row_count,
            "ready_row_count": self.ready_row_count,
            "blocked_row_count": self.blocked_row_count,
            "rows": [row.to_dict() for row in self.rows],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
            "fetching_forbidden": self.fetching_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def _load_json(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("market import binding config must be a JSON object.")
    return raw


def _text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def _binding_config_by_asset_id(path: str | Path) -> dict[str, dict[str, Any]]:
    raw = _load_json(path)
    bindings = raw.get("bindings", [])
    if not isinstance(bindings, list):
        return {}

    result: dict[str, dict[str, Any]] = {}
    for binding in bindings:
        if not isinstance(binding, dict):
            continue
        asset_id = _text(binding.get("asset_id"))
        if asset_id:
            result[asset_id] = binding
    return result


def build_dynamic_market_import_plan(
    registry_path: str | Path,
    binding_path: str | Path,
) -> DynamicMarketImportPlanResult:
    source_result = audit_dynamic_market_source_bindings(registry_path, binding_path)
    binding_config = _binding_config_by_asset_id(binding_path)

    warnings: list[str] = list(source_result.warnings)
    blockers: list[str] = list(source_result.blockers)
    rows: list[DynamicMarketImportPlanRow] = []

    for source_row in source_result.rows:
        config = binding_config.get(source_row.asset_id, {})
        expected_currency = _text(config.get("expected_currency"))

        row_blockers = list(source_row.blockers)
        row_warnings = list(source_row.warnings)

        if source_row.status != "BINDING_READY":
            row_blockers.append(f"{source_row.asset_id}: source binding is not ready.")
        if expected_currency is None:
            row_blockers.append(f"{source_row.asset_id}: expected_currency is missing.")
        if source_row.cache_series_id is None:
            row_blockers.append(f"{source_row.asset_id}: cache_series_id is missing.")

        status = "IMPORT_PLAN_READY" if not row_blockers else "IMPORT_PLAN_BLOCKED"

        rows.append(
            DynamicMarketImportPlanRow(
                asset_id=source_row.asset_id,
                sleeve=source_row.sleeve,
                asset_type=source_row.asset_type,
                source_provider=source_row.source_provider,
                source_symbol=source_row.source_symbol,
                cache_series_id=source_row.cache_series_id,
                expected_currency=expected_currency,
                planned_market_series_id=source_row.cache_series_id,
                status=status,
                warnings=tuple(row_warnings),
                blockers=tuple(dict.fromkeys(row_blockers)),
            )
        )

    for row in rows:
        warnings.extend(row.warnings)
        blockers.extend(row.blockers)

    if source_result.status != SOURCE_BINDING_READY:
        blockers.append(f"source binding audit is not ready: {source_result.status}")

    ready_count = sum(1 for row in rows if row.status == "IMPORT_PLAN_READY")
    blocked_count = sum(1 for row in rows if row.status == "IMPORT_PLAN_BLOCKED")
    status = STATUS_READY if not blockers else STATUS_BLOCKED

    return DynamicMarketImportPlanResult(
        status=status,
        source_binding_status=source_result.status,
        approved_asset_count=source_result.approved_asset_count,
        import_plan_row_count=len(rows),
        ready_row_count=ready_count,
        blocked_row_count=blocked_count,
        rows=tuple(rows),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        manual_approval_required=True,
        execution_forbidden=True,
        fetching_forbidden=True,
    )
