from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.product_api import build_product_api_result


STATUS_READY = "JARVIS_V116_0_ASSISTANT_MARKET_DATA_BRIDGE_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/assistant_market_data_bridge_latest.json"

CRYPTO_NORMALIZED_DIR = Path("jarvis/local/public_data/v22_multi_crypto_normalized")
STOCK_RANKED_PATH = Path("jarvis/local/individual_stock_public_ranked_candidates.local.json")
ETF_SELECTED_PATH = Path("jarvis/local/stock_fund_etf_selected_instrument.local.json")


@dataclass(frozen=True)
class AssistantMarketDataRecord:
    symbol: str
    lane: str
    selected_in_plan: bool
    recommended_amount_eur: float | None
    current_price: float | None
    currency: str | None
    source: str | None
    as_of: str | None
    freshness: str
    live_fetch_enabled: bool
    local_cache_only: bool
    movement_24h_pct: float | None
    movement_7d_pct: float | None
    movement_available: bool
    missing_fields: list[str]
    warnings: list[str]
    blockers: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AssistantMarketDataBridgeResult:
    status: str
    current_date: str
    records: list[dict[str, Any]]
    warnings: list[str]
    blockers: list[str]
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_json(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _normalize_symbol(value: str) -> str:
    return value.upper().strip().replace(":", ".")


def _selected_amounts(current_date: str) -> dict[str, dict[str, Any]]:
    product = build_product_api_result(current_date=current_date)
    selected = {}
    for item in product.week_plan.get("selected_instruments", []) or []:
        symbol = _normalize_symbol(str(item.get("symbol") or ""))
        if symbol:
            selected[symbol] = {
                "lane": str(item.get("lane") or ""),
                "amount_eur": round(float(item.get("amount_eur") or 0.0), 2),
                "name": item.get("name"),
            }
    return selected


def _load_crypto_records() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not CRYPTO_NORMALIZED_DIR.exists():
        return rows
    for path in CRYPTO_NORMALIZED_DIR.glob("*.json"):
        data = _read_json(path)
        if not isinstance(data, dict):
            continue
        candidate_id = str(data.get("candidate_id") or "").upper()
        if not candidate_id:
            continue
        rows[candidate_id] = {
            "symbol": candidate_id,
            "lane": "crypto",
            "current_price": data.get("price_eur"),
            "currency": "EUR",
            "source": data.get("source_id") or "coingecko_normalized_cache",
            "as_of": data.get("as_of") or data.get("provider_last_updated_utc"),
            "freshness": "ready" if data.get("source_quality_ready") else "partial_or_unavailable",
            "movement_24h_pct": data.get("change_24h_pct"),
            "movement_7d_pct": None,
            "warnings": ["raw provider data is normalized but still marked unverified"] if data.get("raw_data_unverified") else [],
            "blockers": [],
        }
    return rows


def _load_stock_records() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    data = _read_json(STOCK_RANKED_PATH)
    if not isinstance(data, dict):
        return rows
    for item in data.get("ranked_candidates", []) or []:
        if not isinstance(item, dict):
            continue
        symbol = _normalize_symbol(str(item.get("symbol") or ""))
        if not symbol:
            continue
        rows[symbol] = {
            "symbol": symbol,
            "lane": "individual_stock",
            "current_price": item.get("close_price"),
            "currency": item.get("currency"),
            "source": item.get("provider") or "stock_ranked_candidates",
            "as_of": item.get("source_as_of") or data.get("current_date"),
            "freshness": "ready" if item.get("source_status") == "STOCK_PUBLIC_SOURCE_READY" else "partial_or_unavailable",
            "movement_24h_pct": None,
            "movement_7d_pct": None,
            "warnings": ["stock candidate is ranked for review only; not approved for purchase"],
            "blockers": [],
        }
    return rows


def _load_etf_records() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    data = _read_json(ETF_SELECTED_PATH)
    if not isinstance(data, dict):
        return rows
    for item in data.get("instrument_decisions", []) or []:
        if not isinstance(item, dict):
            continue
        symbol = _normalize_symbol(str(item.get("symbol") or ""))
        if not symbol:
            continue
        warnings = list(item.get("warnings") or [])
        status = item.get("public_source_status")
        rows[symbol] = {
            "symbol": symbol,
            "lane": "etf_fund",
            "current_price": item.get("close_price"),
            "currency": item.get("currency"),
            "source": item.get("provider") or "etf_selected_instrument",
            "as_of": item.get("source_as_of") or data.get("current_date"),
            "freshness": "ready" if status == "ETF_PUBLIC_SOURCE_READY" else "partial_or_unavailable",
            "movement_24h_pct": None,
            "movement_7d_pct": None,
            "warnings": warnings or ["ETF/fund quote requires manual platform/source verification"],
            "blockers": list(item.get("blockers") or []),
        }
    return rows


def _record_for_symbol(symbol: str, selected: dict[str, Any], sources: dict[str, dict[str, Any]]) -> AssistantMarketDataRecord:
    source_row = sources.get(symbol, {})
    lane = str(selected.get("lane") or source_row.get("lane") or "")
    amount = selected.get("amount_eur")
    price = source_row.get("current_price")
    currency = source_row.get("currency")
    source = source_row.get("source")
    as_of = source_row.get("as_of")
    movement_24h = source_row.get("movement_24h_pct")
    movement_7d = source_row.get("movement_7d_pct")

    missing = []
    if price is None:
        missing.append("current_price")
    if currency is None:
        missing.append("currency")
    if source is None:
        missing.append("source")
    if as_of is None:
        missing.append("as_of")
    if movement_24h is None and movement_7d is None:
        missing.append("movement_history")

    warnings = list(source_row.get("warnings") or [])
    if price is None:
        warnings.append("allocation data is ready, but quote price is missing from the assistant market bridge")
    if movement_24h is None and movement_7d is None:
        warnings.append("movement data is unavailable from current local cache")

    return AssistantMarketDataRecord(
        symbol=symbol,
        lane=lane,
        selected_in_plan=bool(selected),
        recommended_amount_eur=amount,
        current_price=round(float(price), 6) if price is not None else None,
        currency=str(currency) if currency is not None else None,
        source=str(source) if source is not None else None,
        as_of=str(as_of) if as_of is not None else None,
        freshness=str(source_row.get("freshness") or "partial_or_unavailable"),
        live_fetch_enabled=False,
        local_cache_only=True,
        movement_24h_pct=round(float(movement_24h), 6) if movement_24h is not None else None,
        movement_7d_pct=round(float(movement_7d), 6) if movement_7d is not None else None,
        movement_available=movement_24h is not None or movement_7d is not None,
        missing_fields=missing,
        warnings=list(dict.fromkeys(warnings)),
        blockers=list(source_row.get("blockers") or []),
    )


def build_assistant_market_data_bridge_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> AssistantMarketDataBridgeResult:
    selected = _selected_amounts(current_date)
    source_rows = {}
    source_rows.update(_load_crypto_records())
    source_rows.update(_load_stock_records())
    source_rows.update(_load_etf_records())

    symbols = sorted(set(selected) | set(source_rows))
    records = [
        _record_for_symbol(symbol, selected.get(symbol, {}), source_rows)
        for symbol in symbols
    ]

    result = AssistantMarketDataBridgeResult(
        status=STATUS_READY,
        current_date=current_date,
        records=[record.to_dict() for record in records],
        warnings=[
            "assistant market data bridge is read-only",
            "live fetch is disabled; local cache/public files only",
            "missing movement fields are disclosed instead of inferred",
        ],
        blockers=[],
        execution_forbidden=True,
        broker_connection=False,
        credentials_used=False,
        order_created=False,
        trade_executed=False,
        report_written=bool(write_report),
        report_path=str(output_path),
    )

    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return result


def find_market_data_record(symbol: str, *, current_date: str = "2026-06-18") -> dict[str, Any] | None:
    clean = _normalize_symbol(symbol)
    result = build_assistant_market_data_bridge_result(current_date=current_date)
    for record in result.records:
        if _normalize_symbol(str(record.get("symbol") or "")) == clean:
            return record
    if clean.endswith(".DE"):
        shorter = clean[:-3]
        for record in result.records:
            if _normalize_symbol(str(record.get("symbol") or "")) == shorter:
                return record
    return None


def format_assistant_market_data_bridge_report(result: AssistantMarketDataBridgeResult) -> str:
    lines = [
        "J.A.R.V.I.S. ASSISTANT MARKET DATA BRIDGE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"record count: {len(result.records)}",
        "records:",
    ]
    for record in result.records:
        if record.get("selected_in_plan") or record.get("symbol") in {"BTC", "ETH", "MSFT", "IS3Q.DE"}:
            lines.append(
                f"- {record.get('symbol')}: lane={record.get('lane')}; amount={record.get('recommended_amount_eur')}; "
                f"price={record.get('current_price')} {record.get('currency')}; 24h={record.get('movement_24h_pct')}; "
                f"source={record.get('source')}; as_of={record.get('as_of')}; freshness={record.get('freshness')}"
            )
    lines.extend(
        [
            "warnings:",
            *[f"- {warning}" for warning in result.warnings],
            "safety: no broker, credentials, order, trade, or auto-approval path is enabled.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_assistant_market_data_bridge_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_assistant_market_data_bridge_report(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
