"""CoinGecko market_chart raw fixture transformer for J.A.R.V.I.S.

Local-only transformer for CoinGecko-style market_chart JSON payloads:
{"prices": [[timestamp_ms, price], ...]}.

The output shape is normalizer-ready JSON:
{"prices": [{"date": "YYYY-MM-DD", "close": price}, ...]}.

This module does not fetch, call APIs, use credentials, connect to brokers,
grant approvals, create buy requests, promote endpoints, execute trades, or
mutate registries.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


STATUS_READY = "DYNAMIC_COINGECKO_MARKET_CHART_TRANSFORMER_READY_SAFE"
STATUS_BLOCKED = "DYNAMIC_COINGECKO_MARKET_CHART_TRANSFORMER_BLOCKED_SAFE"

MIN_PRICE_ROWS = 12


@dataclass(frozen=True)
class DynamicCoinGeckoMarketChartTransformerResult:
    status: str
    input_path: str | None
    output_path: str | None
    normalized_price_count: int
    normalized_payload: dict[str, Any]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    fetching_forbidden: bool = True
    local_fixture_only: bool = True
    raw_data_unverified: bool = True
    manual_approval_required: bool = True
    execution_forbidden: bool = True
    creates_buy_request: bool = False
    grants_approval: bool = False
    no_trades_executed: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "input_path": self.input_path,
            "output_path": self.output_path,
            "normalized_price_count": self.normalized_price_count,
            "normalized_payload": self.normalized_payload,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "fetching_forbidden": self.fetching_forbidden,
            "local_fixture_only": self.local_fixture_only,
            "raw_data_unverified": self.raw_data_unverified,
            "manual_approval_required": self.manual_approval_required,
            "execution_forbidden": self.execution_forbidden,
            "creates_buy_request": self.creates_buy_request,
            "grants_approval": self.grants_approval,
            "no_trades_executed": self.no_trades_executed,
        }


def _is_positive_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and value > 0


def _date_from_timestamp_ms(timestamp_ms: int | float) -> str:
    return datetime.fromtimestamp(float(timestamp_ms) / 1000.0, tz=UTC).date().isoformat()


def _blocked(
    blockers: list[str],
    *,
    input_path: str | None = None,
    output_path: str | None = None,
    normalized_payload: dict[str, Any] | None = None,
    warnings: list[str] | None = None,
) -> DynamicCoinGeckoMarketChartTransformerResult:
    payload = normalized_payload or {"prices": []}
    return DynamicCoinGeckoMarketChartTransformerResult(
        status=STATUS_BLOCKED,
        input_path=input_path,
        output_path=output_path,
        normalized_price_count=len(payload.get("prices", [])) if isinstance(payload.get("prices"), list) else 0,
        normalized_payload=payload,
        warnings=tuple(dict.fromkeys(warnings or [])),
        blockers=tuple(dict.fromkeys(blockers)),
    )


def transform_coingecko_market_chart_payload(
    payload: Any,
) -> DynamicCoinGeckoMarketChartTransformerResult:
    blockers: list[str] = []

    if not isinstance(payload, dict):
        return _blocked(["payload must be a JSON object."])

    raw_prices = payload.get("prices")
    if not isinstance(raw_prices, list) or not raw_prices:
        return _blocked(["payload prices must be a non-empty list."])

    prices_by_date: dict[str, float] = {}

    for index, row in enumerate(raw_prices):
        if not isinstance(row, (list, tuple)) or len(row) != 2:
            blockers.append(f"price row {index} must be exactly a two-item list or tuple.")
            continue

        timestamp_ms, price = row
        if not _is_positive_number(timestamp_ms):
            blockers.append(f"price row {index} timestamp must be a positive number and not bool.")
            continue
        if not _is_positive_number(price):
            blockers.append(f"price row {index} price must be a positive number and not bool.")
            continue

        try:
            parsed_date = _date_from_timestamp_ms(timestamp_ms)
        except (OverflowError, OSError, ValueError) as exc:
            blockers.append(f"price row {index} timestamp could not be converted to UTC date: {exc}.")
            continue

        prices_by_date[parsed_date] = float(price)

    normalized_prices = [
        {"date": parsed_date, "close": close}
        for parsed_date, close in sorted(prices_by_date.items())
    ]
    normalized_payload = {"prices": normalized_prices}

    if len(normalized_prices) < MIN_PRICE_ROWS:
        blockers.append(f"fewer than {MIN_PRICE_ROWS} normalized price rows.")

    if blockers:
        return _blocked(blockers, normalized_payload=normalized_payload)

    return DynamicCoinGeckoMarketChartTransformerResult(
        status=STATUS_READY,
        input_path=None,
        output_path=None,
        normalized_price_count=len(normalized_prices),
        normalized_payload=normalized_payload,
        warnings=(),
        blockers=(),
    )


def transform_coingecko_market_chart_file(
    input_path: str | Path,
    output_path: str | Path | None = None,
) -> DynamicCoinGeckoMarketChartTransformerResult:
    source = Path(input_path)
    try:
        payload = json.loads(source.read_text(encoding="utf-8"))
    except Exception as exc:
        return _blocked([f"failed to parse input JSON: {exc}"], input_path=str(source))

    result = transform_coingecko_market_chart_payload(payload)
    written_output_path: str | None = None

    if result.status == STATUS_READY and output_path is not None:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            json.dumps(result.normalized_payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        written_output_path = str(target)

    return DynamicCoinGeckoMarketChartTransformerResult(
        status=result.status,
        input_path=str(source),
        output_path=written_output_path,
        normalized_price_count=result.normalized_price_count,
        normalized_payload=result.normalized_payload,
        warnings=result.warnings,
        blockers=result.blockers,
    )
