"""Local market data fixture loader for the read-only J.A.R.V.I.S. kernel."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


class MarketDataError(ValueError):
    """Raised when local market data fixture input is malformed."""


@dataclass(frozen=True)
class PricePoint:
    date: date
    close: float


@dataclass(frozen=True)
class MarketSeries:
    asset_id: str
    currency: str
    prices: tuple[PricePoint, ...]


@dataclass(frozen=True)
class MarketDataSnapshot:
    as_of: date
    base_currency: str
    series: tuple[MarketSeries, ...]


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MarketDataError(f"{label} must be an object.")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MarketDataError(f"{label} exists and must be text.")
    return value.strip()


def _parse_iso_date(value: Any, label: str) -> date:
    text = _require_text(value, label)
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError as exc:
        raise MarketDataError(f"{label} must be a parseable ISO date.") from exc


def _parse_positive_close(value: Any) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise MarketDataError("price close must be a number.")
    if value <= 0:
        raise MarketDataError("price close must be positive.")
    return float(value)


def load_market_data(path: str | Path) -> MarketDataSnapshot:
    """Load deterministic local fixture data and sort prices by date."""
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "market data")
    as_of = _parse_iso_date(raw.get("as_of"), "as_of")
    base_currency = _require_text(raw.get("base_currency"), "base_currency")
    if base_currency != "EUR":
        raise MarketDataError("base_currency must be EUR.")

    raw_series = raw.get("series")
    if not isinstance(raw_series, list):
        raise MarketDataError("series must be a list.")

    parsed_series: list[MarketSeries] = []
    for series_index, raw_series_item in enumerate(raw_series):
        item = _require_mapping(raw_series_item, f"series[{series_index}]")
        asset_id = _require_text(item.get("asset_id"), "asset_id")
        currency = _require_text(item.get("currency"), "currency")
        raw_prices = item.get("prices")
        if not isinstance(raw_prices, list) or not raw_prices:
            raise MarketDataError(f"{asset_id} prices must be a non-empty list.")

        seen_dates: set[date] = set()
        prices: list[PricePoint] = []
        for price_index, raw_price in enumerate(raw_prices):
            price = _require_mapping(raw_price, f"prices[{price_index}]")
            price_date = _parse_iso_date(price.get("date"), "price date")
            if price_date in seen_dates:
                raise MarketDataError(f"{asset_id} has duplicate price date {price_date.isoformat()}.")
            seen_dates.add(price_date)
            prices.append(PricePoint(price_date, _parse_positive_close(price.get("close"))))

        parsed_series.append(MarketSeries(asset_id, currency, tuple(sorted(prices, key=lambda point: point.date))))

    return MarketDataSnapshot(as_of, base_currency, tuple(parsed_series))
