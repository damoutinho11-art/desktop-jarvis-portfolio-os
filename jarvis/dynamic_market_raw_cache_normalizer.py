"""Dynamic raw market cache normalizer for J.A.R.V.I.S. Portfolio OS.

Converts raw public-fetch cache files into the normalized dynamic market-data
JSON shape consumed by the existing market data loader and intake validator.

This module reads local raw cache files only. It does not fetch, download,
scrape, call APIs, connect to brokers, create buy requests, approve assets,
mutate registries, or execute trades.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .dynamic_public_data_fetcher_adapter import (
    STATUS_READY as ADAPTER_READY,
    build_dynamic_public_data_fetcher_adapter,
)


STATUS_READY = "DYNAMIC_MARKET_RAW_CACHE_NORMALIZER_READY_SAFE"
STATUS_BLOCKED = "DYNAMIC_MARKET_RAW_CACHE_NORMALIZER_BLOCKED_SAFE"

MIN_PRICE_POINTS = 12


@dataclass(frozen=True)
class DynamicMarketRawCacheNormalizerRow:
    asset_id: str
    source_id: str
    cache_series_id: str | None
    expected_currency: str | None
    raw_path: str | None
    parsed_price_count: int
    status: str
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "source_id": self.source_id,
            "cache_series_id": self.cache_series_id,
            "expected_currency": self.expected_currency,
            "raw_path": self.raw_path,
            "parsed_price_count": self.parsed_price_count,
            "status": self.status,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class DynamicMarketRawCacheNormalizerResult:
    status: str
    adapter_status: str
    raw_file_count: int
    expected_source_count: int
    normalized_series_count: int
    ready_row_count: int
    blocked_row_count: int
    as_of: str | None
    normalized_market_data: dict[str, Any]
    rows: tuple[DynamicMarketRawCacheNormalizerRow, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    fetching_forbidden: bool
    local_raw_cache_only: bool
    raw_data_unverified: bool
    manual_approval_required: bool
    execution_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "adapter_status": self.adapter_status,
            "raw_file_count": self.raw_file_count,
            "expected_source_count": self.expected_source_count,
            "normalized_series_count": self.normalized_series_count,
            "ready_row_count": self.ready_row_count,
            "blocked_row_count": self.blocked_row_count,
            "as_of": self.as_of,
            "normalized_market_data": self.normalized_market_data,
            "rows": [row.to_dict() for row in self.rows],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "fetching_forbidden": self.fetching_forbidden,
            "local_raw_cache_only": self.local_raw_cache_only,
            "raw_data_unverified": self.raw_data_unverified,
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def _text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def _parse_iso_date(value: Any) -> str | None:
    text = _text(value)
    if text is None:
        return None
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        return None


def _parse_positive_close(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value) if value > 0 else None
    if isinstance(value, str):
        try:
            parsed = float(value.replace(",", "").strip())
        except ValueError:
            return None
        return parsed if parsed > 0 else None
    return None


def _normalize_price_rows(asset_id: str, raw_prices: Any) -> tuple[list[dict[str, Any]], tuple[str, ...]]:
    blockers: list[str] = []

    if not isinstance(raw_prices, list):
        return [], (f"{asset_id}: raw prices must be a list.",)

    prices: list[dict[str, Any]] = []
    seen_dates: set[str] = set()

    for index, item in enumerate(raw_prices):
        if not isinstance(item, dict):
            blockers.append(f"{asset_id}: raw price row {index} is not an object.")
            continue

        parsed_date = _parse_iso_date(item.get("date") or item.get("Date") or item.get("timestamp") or item.get("time"))
        if parsed_date is None:
            blockers.append(f"{asset_id}: raw price row {index} has invalid date.")
            continue

        if parsed_date in seen_dates:
            blockers.append(f"{asset_id}: duplicate raw price date {parsed_date}.")
            continue
        seen_dates.add(parsed_date)

        close = _parse_positive_close(
            item.get("close")
            if "close" in item
            else item.get("Close")
            if "Close" in item
            else item.get("price")
            if "price" in item
            else item.get("value")
        )
        if close is None:
            blockers.append(f"{asset_id}: raw price row {index} has invalid close.")
            continue

        prices.append({"date": parsed_date, "close": close})

    prices = sorted(prices, key=lambda row: row["date"])

    if len(prices) < MIN_PRICE_POINTS:
        blockers.append(f"{asset_id}: fewer than {MIN_PRICE_POINTS} normalized price points.")

    return prices, tuple(dict.fromkeys(blockers))


def _extract_json_prices(raw: Any) -> Any:
    if isinstance(raw, list):
        return raw
    if not isinstance(raw, dict):
        return None

    for key in ("prices", "data", "rows", "values"):
        candidate = raw.get(key)
        if isinstance(candidate, list):
            return candidate

    series = raw.get("series")
    if isinstance(series, list) and series:
        first = series[0]
        if isinstance(first, dict) and isinstance(first.get("prices"), list):
            return first.get("prices")

    return None


def _parse_json_raw(path: Path) -> tuple[Any, tuple[str, ...]]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, (f"{path.name}: failed to parse JSON raw cache: {exc}",)
    return _extract_json_prices(raw), ()


def _parse_csv_raw(path: Path) -> tuple[Any, tuple[str, ...]]:
    try:
        rows = list(csv.DictReader(path.read_text(encoding="utf-8").splitlines()))
    except Exception as exc:
        return None, (f"{path.name}: failed to parse CSV raw cache: {exc}",)
    return rows, ()


def _parse_raw_prices(path: Path) -> tuple[Any, tuple[str, ...]]:
    name = path.name.lower()
    if name.endswith(".json.raw"):
        return _parse_json_raw(path)
    if name.endswith(".csv.raw"):
        return _parse_csv_raw(path)

    try:
        return _parse_json_raw(path)
    except Exception:
        return None, (f"{path.name}: unsupported raw cache extension.",)


def _raw_path_by_source_id(raw_cache_paths: tuple[str | Path, ...], source_ids: set[str]) -> dict[str, Path]:
    result: dict[str, Path] = {}
    for raw_path in raw_cache_paths:
        path = Path(raw_path)
        name = path.name
        for source_id in source_ids:
            if f"_{source_id}." in name or name.startswith(f"{source_id}."):
                result[source_id] = path
    return result


def normalize_dynamic_market_raw_cache(
    registry_path: str | Path,
    binding_path: str | Path,
    endpoint_path: str | Path,
    raw_cache_paths: tuple[str | Path, ...],
    as_of: str | None = None,
) -> DynamicMarketRawCacheNormalizerResult:
    adapter = build_dynamic_public_data_fetcher_adapter(registry_path, binding_path, endpoint_path)

    warnings: list[str] = list(adapter.warnings)
    blockers: list[str] = list(adapter.blockers)

    if adapter.status != ADAPTER_READY:
        blockers.append(f"dynamic public data fetcher adapter is not ready: {adapter.status}")

    valid_rows = tuple(row for row in adapter.rows if row.valid_for_public_fetcher)
    source_ids = {row.source_id for row in valid_rows}
    raw_by_source_id = _raw_path_by_source_id(raw_cache_paths, source_ids)

    rows: list[DynamicMarketRawCacheNormalizerRow] = []
    normalized_series: list[dict[str, Any]] = []
    latest_date: str | None = None

    for adapter_row in valid_rows:
        row_blockers: list[str] = []
        row_warnings: list[str] = []

        raw_path = raw_by_source_id.get(adapter_row.source_id)
        prices: list[dict[str, Any]] = []

        if adapter_row.cache_series_id is None:
            row_blockers.append(f"{adapter_row.asset_id}: cache_series_id is missing.")
        if adapter_row.expected_currency is None:
            row_blockers.append(f"{adapter_row.asset_id}: expected_currency is missing.")
        if raw_path is None:
            row_blockers.append(f"{adapter_row.asset_id}: raw cache file is missing.")
        elif not raw_path.exists():
            row_blockers.append(f"{adapter_row.asset_id}: raw cache file does not exist: {raw_path}.")
        else:
            raw_prices, parse_blockers = _parse_raw_prices(raw_path)
            row_blockers.extend(parse_blockers)
            prices, price_blockers = _normalize_price_rows(adapter_row.asset_id, raw_prices)
            row_blockers.extend(price_blockers)

        if prices:
            latest_date = max(latest_date or prices[-1]["date"], prices[-1]["date"])

        status = "RAW_CACHE_NORMALIZED" if not row_blockers else "RAW_CACHE_NORMALIZATION_BLOCKED"

        if status == "RAW_CACHE_NORMALIZED":
            normalized_series.append(
                {
                    "asset_id": adapter_row.cache_series_id,
                    "currency": adapter_row.expected_currency,
                    "prices": prices,
                }
            )

        rows.append(
            DynamicMarketRawCacheNormalizerRow(
                asset_id=adapter_row.asset_id,
                source_id=adapter_row.source_id,
                cache_series_id=adapter_row.cache_series_id,
                expected_currency=adapter_row.expected_currency,
                raw_path=str(raw_path) if raw_path is not None else None,
                parsed_price_count=len(prices),
                status=status,
                warnings=tuple(dict.fromkeys(row_warnings)),
                blockers=tuple(dict.fromkeys(row_blockers)),
            )
        )

    for row in rows:
        warnings.extend(row.warnings)
        blockers.extend(row.blockers)

    normalized_as_of = as_of or latest_date
    if normalized_as_of is None:
        blockers.append("as_of could not be inferred from raw cache prices.")

    normalized_market_data = {
        "as_of": normalized_as_of,
        "base_currency": "EUR",
        "series": sorted(normalized_series, key=lambda item: item["asset_id"]),
    }

    ready_count = sum(1 for row in rows if row.status == "RAW_CACHE_NORMALIZED")
    blocked_count = sum(1 for row in rows if row.status == "RAW_CACHE_NORMALIZATION_BLOCKED")

    status = STATUS_READY if not blockers else STATUS_BLOCKED

    return DynamicMarketRawCacheNormalizerResult(
        status=status,
        adapter_status=adapter.status,
        raw_file_count=len(raw_cache_paths),
        expected_source_count=len(valid_rows),
        normalized_series_count=len(normalized_series),
        ready_row_count=ready_count,
        blocked_row_count=blocked_count,
        as_of=normalized_as_of,
        normalized_market_data=normalized_market_data,
        rows=tuple(rows),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        fetching_forbidden=True,
        local_raw_cache_only=True,
        raw_data_unverified=True,
        manual_approval_required=True,
        execution_forbidden=True,
    )
