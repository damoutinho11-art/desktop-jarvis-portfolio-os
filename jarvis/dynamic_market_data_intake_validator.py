"""Dynamic market data intake validator for J.A.R.V.I.S. Portfolio OS.

Report-only local market-data intake validation.

This module validates that a local market-data JSON file satisfies the dynamic
market import plan contract. It does not fetch, download, scrape, call APIs,
connect to brokers, create buy requests, approve assets, mutate registries, or
execute trades.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .dynamic_market_import_plan import (
    STATUS_READY as IMPORT_PLAN_READY,
    build_dynamic_market_import_plan,
)


STATUS_READY = "DYNAMIC_MARKET_DATA_INTAKE_READY_SAFE"
STATUS_BLOCKED = "DYNAMIC_MARKET_DATA_INTAKE_BLOCKED_SAFE"

MIN_PRICE_POINTS = 12


@dataclass(frozen=True)
class DynamicMarketDataIntakeRow:
    asset_id: str
    sleeve: str
    asset_type: str
    planned_market_series_id: str | None
    expected_currency: str | None
    observed_currency: str | None
    price_count: int
    status: str
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "sleeve": self.sleeve,
            "asset_type": self.asset_type,
            "planned_market_series_id": self.planned_market_series_id,
            "expected_currency": self.expected_currency,
            "observed_currency": self.observed_currency,
            "price_count": self.price_count,
            "status": self.status,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class DynamicMarketDataIntakeResult:
    status: str
    import_plan_status: str
    expected_series_count: int
    ready_series_count: int
    blocked_series_count: int
    extra_series_count: int
    rows: tuple[DynamicMarketDataIntakeRow, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    fetching_forbidden: bool
    execution_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "import_plan_status": self.import_plan_status,
            "expected_series_count": self.expected_series_count,
            "ready_series_count": self.ready_series_count,
            "blocked_series_count": self.blocked_series_count,
            "extra_series_count": self.extra_series_count,
            "rows": [row.to_dict() for row in self.rows],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "fetching_forbidden": self.fetching_forbidden,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": False,
            "no_trades_executed": True,
        }


def _load_json(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("market data intake file must be a JSON object.")
    return raw


def _text(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def _parse_date(value: Any) -> date | None:
    if not isinstance(value, str):
        return None
    try:
        return date.fromisoformat(value[:10])
    except ValueError:
        return None


def _series_by_asset_id(market_data: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], tuple[str, ...]]:
    warnings: list[str] = []
    series = market_data.get("series", [])

    if not isinstance(series, list):
        return {}, ("market data series must be a list.",)

    result: dict[str, dict[str, Any]] = {}
    for item in series:
        if not isinstance(item, dict):
            warnings.append("ignored non-object market series item.")
            continue

        asset_id = _text(item.get("asset_id"))
        if asset_id is None:
            warnings.append("ignored market series without asset_id.")
            continue

        if asset_id in result:
            warnings.append(f"{asset_id}: duplicate market series; last one used.")

        result[asset_id] = item

    return result, tuple(warnings)


def _validate_prices(asset_id: str, prices: Any) -> tuple[int, tuple[str, ...]]:
    blockers: list[str] = []

    if not isinstance(prices, list):
        return 0, (f"{asset_id}: prices must be a list.",)

    if len(prices) < MIN_PRICE_POINTS:
        blockers.append(f"{asset_id}: fewer than {MIN_PRICE_POINTS} price points.")

    seen_dates: set[date] = set()
    previous_date: date | None = None

    for index, item in enumerate(prices):
        if not isinstance(item, dict):
            blockers.append(f"{asset_id}: price row {index} is not an object.")
            continue

        parsed_date = _parse_date(item.get("date"))
        if parsed_date is None:
            blockers.append(f"{asset_id}: price row {index} has invalid date.")
            continue

        if parsed_date in seen_dates:
            blockers.append(f"{asset_id}: duplicate price date {parsed_date.isoformat()}.")
        seen_dates.add(parsed_date)

        if previous_date is not None and parsed_date < previous_date:
            blockers.append(f"{asset_id}: prices are not sorted by date.")
        previous_date = parsed_date

        close = item.get("close")
        if not isinstance(close, int | float) or close <= 0:
            blockers.append(f"{asset_id}: price row {index} has invalid close.")

    return len(prices), tuple(blockers)


def validate_dynamic_market_data_intake(
    registry_path: str | Path,
    binding_path: str | Path,
    market_data_path: str | Path,
) -> DynamicMarketDataIntakeResult:
    import_plan = build_dynamic_market_import_plan(registry_path, binding_path)
    market_data = _load_json(market_data_path)
    market_series, market_warnings = _series_by_asset_id(market_data)

    warnings: list[str] = list(import_plan.warnings)
    warnings.extend(market_warnings)
    blockers: list[str] = list(import_plan.blockers)
    rows: list[DynamicMarketDataIntakeRow] = []

    expected_series_ids = {
        row.planned_market_series_id
        for row in import_plan.rows
        if row.planned_market_series_id is not None
    }
    extra_series = sorted(set(market_series) - expected_series_ids)

    if extra_series:
        warnings.append(f"market data contains extra series ids: {extra_series}")

    for plan_row in import_plan.rows:
        row_blockers = list(plan_row.blockers)
        row_warnings = list(plan_row.warnings)

        series_id = plan_row.planned_market_series_id
        series = market_series.get(series_id or "")

        observed_currency = None
        price_count = 0

        if import_plan.status != IMPORT_PLAN_READY:
            row_blockers.append(f"{plan_row.asset_id}: import plan is not ready.")
        if series_id is None:
            row_blockers.append(f"{plan_row.asset_id}: planned market series id is missing.")
        elif series is None:
            row_blockers.append(f"{plan_row.asset_id}: market series is missing.")
        else:
            observed_currency = _text(series.get("currency"))
            if observed_currency != plan_row.expected_currency:
                row_blockers.append(
                    f"{plan_row.asset_id}: currency mismatch expected "
                    f"{plan_row.expected_currency}, observed {observed_currency}."
                )

            price_count, price_blockers = _validate_prices(plan_row.asset_id, series.get("prices"))
            row_blockers.extend(price_blockers)

        status = "MARKET_DATA_INTAKE_READY" if not row_blockers else "MARKET_DATA_INTAKE_BLOCKED"

        rows.append(
            DynamicMarketDataIntakeRow(
                asset_id=plan_row.asset_id,
                sleeve=plan_row.sleeve,
                asset_type=plan_row.asset_type,
                planned_market_series_id=series_id,
                expected_currency=plan_row.expected_currency,
                observed_currency=observed_currency,
                price_count=price_count,
                status=status,
                warnings=tuple(row_warnings),
                blockers=tuple(dict.fromkeys(row_blockers)),
            )
        )

    for row in rows:
        warnings.extend(row.warnings)
        blockers.extend(row.blockers)

    ready_count = sum(1 for row in rows if row.status == "MARKET_DATA_INTAKE_READY")
    blocked_count = sum(1 for row in rows if row.status == "MARKET_DATA_INTAKE_BLOCKED")

    if import_plan.status != IMPORT_PLAN_READY:
        blockers.append(f"market import plan is not ready: {import_plan.status}")

    status = STATUS_READY if not blockers else STATUS_BLOCKED

    return DynamicMarketDataIntakeResult(
        status=status,
        import_plan_status=import_plan.status,
        expected_series_count=len(import_plan.rows),
        ready_series_count=ready_count,
        blocked_series_count=blocked_count,
        extra_series_count=len(extra_series),
        rows=tuple(rows),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        manual_approval_required=True,
        fetching_forbidden=True,
        execution_forbidden=True,
    )
