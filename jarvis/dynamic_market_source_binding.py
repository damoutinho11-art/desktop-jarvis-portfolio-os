"""Dynamic market source binding audit for J.A.R.V.I.S. Portfolio OS.

Report-only binding contract.

This module maps approved portfolio assets to market-data source identifiers and
local cache/series identifiers. It does not fetch, download, verify external
truth, connect to brokers, create buy requests, or execute trades.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .approved_universe import build_approved_universe


STATUS_BLOCKED = "DYNAMIC_MARKET_SOURCE_BINDING_BLOCKED_SAFE"
STATUS_PARTIAL = "DYNAMIC_MARKET_SOURCE_BINDING_PARTIAL_SAFE"
STATUS_READY = "DYNAMIC_MARKET_SOURCE_BINDING_READY_SAFE"

PLACEHOLDERS = {"", "unknown", "UNKNOWN", "manual_placeholder", "n/a", "N/A", "TODO", "todo"}


@dataclass(frozen=True)
class MarketSourceBindingRow:
    asset_id: str
    sleeve: str
    asset_type: str
    status: str
    source_provider: str | None
    source_symbol: str | None
    cache_series_id: str | None
    enabled: bool
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
            "enabled": self.enabled,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class DynamicMarketSourceBindingResult:
    status: str
    approved_asset_count: int
    binding_count: int
    ready_binding_count: int
    missing_binding_count: int
    blocked_binding_count: int
    rows: tuple[MarketSourceBindingRow, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    execution_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "approved_asset_count": self.approved_asset_count,
            "binding_count": self.binding_count,
            "ready_binding_count": self.ready_binding_count,
            "missing_binding_count": self.missing_binding_count,
            "blocked_binding_count": self.blocked_binding_count,
            "rows": [row.to_dict() for row in self.rows],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def _text(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def _bool(value: Any) -> bool:
    return value is True


def load_json(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("binding config must be a JSON object.")
    return raw


def _is_placeholder(value: str | None) -> bool:
    return value is None or value.strip() in PLACEHOLDERS


def _bindings_by_asset_id(config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    bindings = config.get("bindings", [])
    if not isinstance(bindings, list):
        return {}

    result: dict[str, dict[str, Any]] = {}
    for item in bindings:
        if not isinstance(item, dict):
            continue
        asset_id = _text(item.get("asset_id"))
        if asset_id:
            result[asset_id] = item
    return result


def _row_for_asset(asset, binding: dict[str, Any] | None) -> MarketSourceBindingRow:
    if binding is None:
        return MarketSourceBindingRow(
            asset_id=asset.asset_id,
            sleeve=asset.sleeve,
            asset_type=asset.asset_type,
            status="MISSING_BINDING",
            source_provider=None,
            source_symbol=None,
            cache_series_id=None,
            enabled=False,
            warnings=(),
            blockers=(f"{asset.asset_id}: no market source binding found.",),
        )

    blockers: list[str] = []
    warnings: list[str] = []

    source_provider = _text(binding.get("source_provider"))
    source_symbol = _text(binding.get("source_symbol"))
    cache_series_id = _text(binding.get("cache_series_id"))
    enabled = _bool(binding.get("enabled"))

    if not enabled:
        blockers.append(f"{asset.asset_id}: binding is not enabled.")
    if _is_placeholder(source_provider):
        blockers.append(f"{asset.asset_id}: source_provider is missing or placeholder.")
    if _is_placeholder(source_symbol):
        blockers.append(f"{asset.asset_id}: source_symbol is missing or placeholder.")
    if _is_placeholder(cache_series_id):
        blockers.append(f"{asset.asset_id}: cache_series_id is missing or placeholder.")
    if cache_series_id and cache_series_id != asset.asset_id:
        warnings.append(f"{asset.asset_id}: cache_series_id differs from approved asset_id.")

    status = "BINDING_READY" if not blockers else "BINDING_BLOCKED"

    return MarketSourceBindingRow(
        asset_id=asset.asset_id,
        sleeve=asset.sleeve,
        asset_type=asset.asset_type,
        status=status,
        source_provider=source_provider or None,
        source_symbol=source_symbol or None,
        cache_series_id=cache_series_id or None,
        enabled=enabled,
        warnings=tuple(warnings),
        blockers=tuple(blockers),
    )


def audit_dynamic_market_source_bindings(
    registry_path: str | Path,
    binding_path: str | Path,
) -> DynamicMarketSourceBindingResult:
    universe = build_approved_universe(
        registry_path,
        etf_universe_expected=False,
        crypto_universe_expected=False,
    )
    config = load_json(binding_path)
    bindings = _bindings_by_asset_id(config)

    warnings: list[str] = list(universe.warnings)
    blockers: list[str] = []

    if universe.total_approved_assets == 0:
        blockers.append("approved universe is empty.")

    rows = tuple(
        _row_for_asset(asset, bindings.get(asset.asset_id))
        for asset in universe.approved_assets
    )

    approved_ids = {asset.asset_id for asset in universe.approved_assets}
    extra_binding_ids = sorted(set(bindings) - approved_ids)
    if extra_binding_ids:
        warnings.append(f"binding config contains non-approved asset ids: {extra_binding_ids}")

    for row in rows:
        blockers.extend(row.blockers)
        warnings.extend(row.warnings)

    ready_count = sum(1 for row in rows if row.status == "BINDING_READY")
    missing_count = sum(1 for row in rows if row.status == "MISSING_BINDING")
    blocked_count = sum(1 for row in rows if row.status == "BINDING_BLOCKED")

    if blockers:
        status = STATUS_BLOCKED if ready_count == 0 else STATUS_PARTIAL
    else:
        status = STATUS_READY

    return DynamicMarketSourceBindingResult(
        status=status,
        approved_asset_count=universe.total_approved_assets,
        binding_count=len(bindings),
        ready_binding_count=ready_count,
        missing_binding_count=missing_count,
        blocked_binding_count=blocked_count,
        rows=rows,
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        manual_approval_required=True,
        execution_forbidden=True,
    )
