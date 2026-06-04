"""Read-only source adapter interfaces and starter local CSV adapter."""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from datetime import date, datetime
from pathlib import Path

from .data_contracts import (
    NormalizedMarketDataSnapshot,
    NormalizedMarketSeries,
    NormalizedPricePoint,
    SourceMetadata,
)
from .market_data_loader import MarketDataError


class BaseSourceAdapter(ABC):
    """Read-only interface for future source adapters."""

    adapter_name: str = "base"
    source_quality: str = "fixture"
    read_only: bool = True

    @abstractmethod
    def load_market_data(self) -> NormalizedMarketDataSnapshot:
        """Return normalized market data without mutating external systems."""


def _parse_iso_date(value: str, label: str) -> date:
    if not value or not value.strip():
        raise MarketDataError(f"{label} exists and must be text.")
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except ValueError as exc:
        raise MarketDataError(f"{label} must be a parseable ISO date.") from exc


def _parse_positive_close(value: str) -> float:
    try:
        close = float(value)
    except (TypeError, ValueError) as exc:
        raise MarketDataError("price close must be a number.") from exc
    if close <= 0:
        raise MarketDataError("price close must be positive.")
    return close


class LocalCSVMarketAdapter(BaseSourceAdapter):
    """Starter adapter for local CSV market data exports.

    Required CSV columns: asset_id, currency, date, close.
    """

    adapter_name = "local_csv_market"
    source_quality = "manual_csv"
    read_only = True

    def __init__(
        self,
        path: str | Path,
        as_of: str | date,
        base_currency: str = "EUR",
        source_id: str = "local_csv_market",
        source_name: str = "Local CSV market data",
    ) -> None:
        self.path = Path(path)
        self.as_of = _parse_iso_date(as_of, "as_of") if isinstance(as_of, str) else as_of
        self.base_currency = base_currency
        self.source_id = source_id
        self.source_name = source_name

    def load_market_data(self) -> NormalizedMarketDataSnapshot:
        if self.base_currency != "EUR":
            raise MarketDataError("base_currency must be EUR.")

        rows_by_asset: dict[tuple[str, str], list[NormalizedPricePoint]] = {}
        with self.path.open("r", encoding="utf-8", newline="") as file:
            reader = csv.DictReader(file)
            required = {"asset_id", "currency", "date", "close"}
            if reader.fieldnames is None or not required.issubset(set(reader.fieldnames)):
                raise MarketDataError("CSV must contain asset_id, currency, date, and close columns.")
            for row in reader:
                asset_id = (row.get("asset_id") or "").strip()
                currency = (row.get("currency") or "").strip()
                if not asset_id:
                    raise MarketDataError("asset_id exists and must be text.")
                if not currency:
                    raise MarketDataError("currency exists and must be text.")
                point = NormalizedPricePoint(
                    date=_parse_iso_date(row.get("date", ""), "price date"),
                    close=_parse_positive_close(row.get("close", "")),
                )
                rows_by_asset.setdefault((asset_id, currency), []).append(point)

        source_metadata = SourceMetadata(
            source_id=self.source_id,
            source_name=self.source_name,
            source_quality=self.source_quality,
            as_of=self.as_of,
            retrieved_at=self.as_of,
            read_only=self.read_only,
        )
        series: list[NormalizedMarketSeries] = []
        for (asset_id, currency), prices in sorted(rows_by_asset.items()):
            seen_dates: set[date] = set()
            sorted_prices = tuple(sorted(prices, key=lambda point: point.date))
            for point in sorted_prices:
                if point.date in seen_dates:
                    raise MarketDataError(f"{asset_id} has duplicate price date {point.date.isoformat()}.")
                seen_dates.add(point.date)
            latest_date = sorted_prices[-1].date
            freshness_days = (self.as_of - latest_date).days
            series_metadata = SourceMetadata(
                source_id=self.source_id,
                source_name=self.source_name,
                source_quality=self.source_quality,
                as_of=self.as_of,
                retrieved_at=latest_date,
                freshness_days=freshness_days,
                read_only=self.read_only,
            )
            series.append(NormalizedMarketSeries(asset_id, currency, sorted_prices, series_metadata))

        return NormalizedMarketDataSnapshot(
            as_of=self.as_of,
            base_currency=self.base_currency,
            series=tuple(series),
            source_metadata=source_metadata,
        )
