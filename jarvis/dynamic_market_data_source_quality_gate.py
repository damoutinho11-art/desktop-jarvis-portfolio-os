"""Dynamic market data source quality gate for J.A.R.V.I.S.

Report-only source quality checks for dynamic market-data fixtures. This module
does not fetch market data, call APIs, connect to brokers, approve assets,
create buy requests, mutate registries, or execute trades.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .approved_universe import build_approved_universe


STATUS_READY = "DYNAMIC_MARKET_DATA_SOURCE_QUALITY_READY_SAFE"
STATUS_BLOCKED = "DYNAMIC_MARKET_DATA_SOURCE_QUALITY_BLOCKED_SAFE"
STATUS_PARTIAL = "DYNAMIC_MARKET_DATA_SOURCE_QUALITY_PARTIAL_SAFE"

ALLOWED_SOURCE_TYPES = {
    "public_market_data_csv",
    "public_market_data_json",
    "public_market_data_api",
}
CRYPTO_IDENTITY_FIELDS = ("coin_id", "coingecko_coin_id", "source_coin_id")
MAX_STALE_DAYS = 7


@dataclass(frozen=True)
class DynamicMarketDataSourceQualityRow:
    asset_id: str
    status: str
    source_provider: str | None
    source_type: str | None
    freshness_status: str
    identity_status: str
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "status": self.status,
            "source_provider": self.source_provider,
            "source_type": self.source_type,
            "freshness_status": self.freshness_status,
            "identity_status": self.identity_status,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class DynamicMarketDataSourceQualityResult:
    status: str
    approved_asset_count: int
    endpoint_count: int
    binding_count: int
    market_series_count: int
    ready_row_count: int
    blocked_row_count: int
    rows: tuple[DynamicMarketDataSourceQualityRow, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    raw_data_unverified: bool
    execution_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "approved_asset_count": self.approved_asset_count,
            "endpoint_count": self.endpoint_count,
            "binding_count": self.binding_count,
            "market_series_count": self.market_series_count,
            "ready_row_count": self.ready_row_count,
            "blocked_row_count": self.blocked_row_count,
            "rows": [row.to_dict() for row in self.rows],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "raw_data_unverified": self.raw_data_unverified,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def load_json(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("dynamic source quality input must be a JSON object.")
    return raw


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _bool(value: Any) -> bool:
    return value is True


def _items_by_asset_id(config: dict[str, Any], key: str) -> dict[str, list[dict[str, Any]]]:
    items = config.get(key, [])
    result: dict[str, list[dict[str, Any]]] = {}
    if not isinstance(items, list):
        return result
    for item in items:
        if not isinstance(item, dict):
            continue
        asset_id = _text(item.get("asset_id"))
        if asset_id:
            result.setdefault(asset_id, []).append(item)
    return result


def _raw_registry_assets_by_id(registry_config: dict[str, Any]) -> dict[str, dict[str, Any]]:
    assets = registry_config.get("assets", [])
    result: dict[str, dict[str, Any]] = {}
    if not isinstance(assets, list):
        return result
    for item in assets:
        if not isinstance(item, dict):
            continue
        asset_id = _text(item.get("asset_id"))
        if asset_id:
            result[asset_id] = item
    return result


def _looks_like_isin(value: str) -> bool:
    return bool(re.match(r"^[A-Z]{2}[A-Z0-9]{8,}$", value.strip().upper()))


def _has_crypto_identity(*records: dict[str, Any] | None) -> bool:
    for record in records:
        if not record:
            continue
        for field in CRYPTO_IDENTITY_FIELDS:
            if _text(record.get(field)):
                return True
    return False


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _freshness_status(series: dict[str, Any] | None, as_of: date | None) -> tuple[str, str | None]:
    if series is None:
        return "MISSING_SERIES", "market data series is missing."
    prices = series.get("prices", [])
    if not isinstance(prices, list) or len(prices) < 12:
        return "INSUFFICIENT_PRICE_POINTS", "market data series has fewer than 12 price points."
    parsed_dates = sorted(
        parsed for item in prices
        if isinstance(item, dict)
        for parsed in [_parse_date(_text(item.get("date")))]
        if parsed is not None
    )
    if not parsed_dates:
        return "MISSING_PRICE_DATES", "market data series has no valid price dates."
    if as_of is None:
        return "UNKNOWN_AS_OF_DATE", "market data as_of date is missing or invalid."
    latest = parsed_dates[-1]
    stale_days = (as_of - latest).days
    if stale_days < 0:
        return "PRICE_AFTER_AS_OF", "latest market data price date is after as_of date."
    if stale_days > MAX_STALE_DAYS:
        return "STALE_PRICE_SERIES", f"latest market data price is {stale_days} days before as_of."
    return "FRESH_ENOUGH", None


def _row_for_asset(
    asset: Any,
    raw_asset: dict[str, Any],
    endpoints: list[dict[str, Any]],
    bindings: list[dict[str, Any]],
    series_items: list[dict[str, Any]],
    market_as_of: date | None,
) -> DynamicMarketDataSourceQualityRow:
    blockers: list[str] = []
    warnings: list[str] = []

    endpoint = endpoints[0] if len(endpoints) == 1 else None
    binding = bindings[0] if len(bindings) == 1 else None
    series = series_items[0] if len(series_items) == 1 else None

    if len(endpoints) != 1:
        blockers.append(f"{asset.asset_id}: expected exactly one endpoint row, found {len(endpoints)}.")
    if len(bindings) != 1:
        blockers.append(f"{asset.asset_id}: expected exactly one binding row, found {len(bindings)}.")
    if len(series_items) != 1:
        blockers.append(f"{asset.asset_id}: expected exactly one market data series, found {len(series_items)}.")

    source_provider = _text(binding.get("source_provider")) if binding else ""
    source_type = _text(endpoint.get("source_type")) if endpoint else ""

    if endpoint:
        if "example.com" in _text(endpoint.get("source_url")).lower():
            blockers.append(f"{asset.asset_id}: endpoint source_url contains example.com placeholder.")
        if not _bool(endpoint.get("public_source_only")):
            blockers.append(f"{asset.asset_id}: endpoint must be public_source_only true.")
        if _bool(endpoint.get("requires_authentication")):
            blockers.append(f"{asset.asset_id}: endpoint requires authentication.")
        if _bool(endpoint.get("requires_credentials")):
            blockers.append(f"{asset.asset_id}: endpoint requires credentials.")
        if _bool(endpoint.get("broker_or_trading_api")):
            blockers.append(f"{asset.asset_id}: endpoint is marked broker_or_trading_api.")
        if _bool(endpoint.get("contains_private_data")):
            blockers.append(f"{asset.asset_id}: endpoint contains private data.")
        if source_type not in ALLOWED_SOURCE_TYPES:
            blockers.append(f"{asset.asset_id}: endpoint source_type {source_type or '<missing>'} is not allowed.")
        if not _text(endpoint.get("cross_check_source")) and not _bool(endpoint.get("manual_cross_check_waiver")):
            blockers.append(f"{asset.asset_id}: missing cross_check_source or manual_cross_check_waiver.")

    if binding:
        if source_provider == "manual_market_fixture":
            blockers.append(f"{asset.asset_id}: source_provider manual_market_fixture is not real quality ready.")
        if series and _text(series.get("currency")) != _text(binding.get("expected_currency")):
            blockers.append(
                f"{asset.asset_id}: market data currency {_text(series.get('currency')) or '<missing>'} "
                f"does not match expected_currency {_text(binding.get('expected_currency')) or '<missing>'}."
            )

    data_source = asset.data_source
    if "synthetic" in data_source.lower() or "fixture" in data_source.lower():
        blockers.append(f"{asset.asset_id}: registry data_source is synthetic or fixture.")

    if asset.asset_type == "ETF":
        identity_status = "ETF_ISIN_READY" if _looks_like_isin(asset.isin_or_symbol) else "ETF_ISIN_BLOCKED"
        if identity_status != "ETF_ISIN_READY":
            blockers.append(f"{asset.asset_id}: ETF isin_or_symbol is not ISIN-like.")
    elif asset.asset_type == "crypto":
        identity_status = (
            "CRYPTO_IDENTITY_READY"
            if _has_crypto_identity(raw_asset, endpoint)
            else "CRYPTO_IDENTITY_BLOCKED"
        )
        if identity_status != "CRYPTO_IDENTITY_READY":
            blockers.append(f"{asset.asset_id}: crypto asset requires coin_id/coingecko_coin_id/source_coin_id.")
    else:
        identity_status = "IDENTITY_NOT_APPLICABLE"

    freshness_status, freshness_blocker = _freshness_status(series, market_as_of)
    if freshness_blocker:
        blockers.append(f"{asset.asset_id}: {freshness_blocker}")

    status = "SOURCE_QUALITY_READY" if not blockers else "SOURCE_QUALITY_BLOCKED"
    return DynamicMarketDataSourceQualityRow(
        asset_id=asset.asset_id,
        status=status,
        source_provider=source_provider or None,
        source_type=source_type or None,
        freshness_status=freshness_status,
        identity_status=identity_status,
        warnings=tuple(warnings),
        blockers=tuple(blockers),
    )


def audit_dynamic_market_data_source_quality(
    registry_path: str | Path,
    binding_path: str | Path,
    endpoint_path: str | Path,
    market_data_path: str | Path,
) -> DynamicMarketDataSourceQualityResult:
    registry_config = load_json(registry_path)
    binding_config = load_json(binding_path)
    endpoint_config = load_json(endpoint_path)
    market_data_config = load_json(market_data_path)

    universe = build_approved_universe(
        registry_path,
        etf_universe_expected=False,
        crypto_universe_expected=False,
    )

    raw_assets = _raw_registry_assets_by_id(registry_config)
    bindings_by_asset = _items_by_asset_id(binding_config, "bindings")
    endpoints_by_asset = _items_by_asset_id(endpoint_config, "endpoints")
    series_by_asset = _items_by_asset_id(market_data_config, "series")
    market_as_of = _parse_date(_text(market_data_config.get("as_of")))

    warnings: list[str] = list(universe.warnings)
    blockers: list[str] = []

    if universe.total_approved_assets == 0:
        blockers.append("approved universe is empty.")
    if binding_config.get("manual_review_required") is not True:
        blockers.append("binding config must keep manual_review_required true.")
    if endpoint_config.get("manual_review_required") is not True:
        blockers.append("endpoint config must keep manual_review_required true.")
    if binding_config.get("execution_forbidden") is not True:
        blockers.append("binding config must keep execution_forbidden true.")
    if endpoint_config.get("execution_forbidden") is not True:
        blockers.append("endpoint config must keep execution_forbidden true.")
    if market_data_config.get("raw_data_unverified") is False:
        blockers.append("market data must not mark raw_data_unverified false.")
    if market_data_config.get("creates_buy_request") is True:
        blockers.append("market data must not create buy requests.")
    if market_data_config.get("no_trades_executed") is False:
        blockers.append("market data must keep no_trades_executed true when provided.")

    rows = tuple(
        _row_for_asset(
            asset,
            raw_assets.get(asset.asset_id, {}),
            endpoints_by_asset.get(asset.asset_id, []),
            bindings_by_asset.get(asset.asset_id, []),
            series_by_asset.get(asset.asset_id, []),
            market_as_of,
        )
        for asset in universe.approved_assets
    )

    approved_ids = {asset.asset_id for asset in universe.approved_assets}
    for label, ids in (
        ("endpoint", set(endpoints_by_asset) - approved_ids),
        ("binding", set(bindings_by_asset) - approved_ids),
        ("market data series", set(series_by_asset) - approved_ids),
    ):
        if ids:
            warnings.append(f"{label} config contains non-approved asset ids: {sorted(ids)}")

    for row in rows:
        warnings.extend(row.warnings)
        blockers.extend(row.blockers)

    ready_count = sum(1 for row in rows if row.status == "SOURCE_QUALITY_READY")
    blocked_count = sum(1 for row in rows if row.status == "SOURCE_QUALITY_BLOCKED")

    status = STATUS_BLOCKED if blockers else STATUS_READY

    return DynamicMarketDataSourceQualityResult(
        status=status,
        approved_asset_count=universe.total_approved_assets,
        endpoint_count=sum(len(items) for items in endpoints_by_asset.values()),
        binding_count=sum(len(items) for items in bindings_by_asset.values()),
        market_series_count=sum(len(items) for items in series_by_asset.values()),
        ready_row_count=ready_count,
        blocked_row_count=blocked_count,
        rows=rows,
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        manual_approval_required=True,
        raw_data_unverified=True,
        execution_forbidden=True,
    )
