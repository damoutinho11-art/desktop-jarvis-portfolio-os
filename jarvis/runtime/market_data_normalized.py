from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from jarvis.runtime.fx_assistant_bridge import build_fx_assistant_bridge_result
from jarvis.runtime.selected_instrument_resolver import build_selected_instrument_resolver_result


STATUS_READY = "JARVIS_V118_0_MARKET_DATA_NORMALIZED_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/market_data_normalized_latest.json"
CRYPTO_NORMALIZED_DIR = Path("jarvis/local/public_data/v22_multi_crypto_normalized")
STOCK_RANKED_PATH = Path("jarvis/local/individual_stock_public_ranked_candidates.local.json")


@dataclass(frozen=True)
class NormalizedMarketDataRecord:
    symbol: str
    lane: str
    selected_amount_eur: float | None
    selected_in_plan: bool
    instrument_identity: dict[str, Any]
    quote_price: float | None
    currency: str | None
    source: str | None
    source_as_of: str | None
    freshness: str
    movement_24h: float | None
    movement_7d: float | None
    movement_30d: float | None
    missing_fields: list[str]
    warnings: list[str]
    blockers: list[str]
    confidence: str
    cache_path: str | None
    source_path: str | None
    manual_review_required: bool
    trusted_for_assistant: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NormalizedMarketDataResult:
    status: str
    current_date: str
    records: list[dict[str, Any]]
    record_count: int
    trusted_record_count: int
    partial_record_count: int
    data_trust_summary: dict[str, Any]
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


def _normalize_symbol(value: Any) -> str:
    return str(value or "").upper().strip().replace(":", ".")


def _future_date(value: str | None, current_date: str) -> bool:
    if not value:
        return False
    try:
        source_day = date.fromisoformat(str(value)[:10])
        current_day = date.fromisoformat(str(current_date)[:10])
    except ValueError:
        return False
    return source_day > current_day


def _product_selections(product_api_result: Any) -> list[dict[str, Any]]:
    return list(getattr(product_api_result, "week_plan", {}).get("selected_instruments", []) or [])


def _crypto_sources() -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    if not CRYPTO_NORMALIZED_DIR.exists():
        return rows
    for path in CRYPTO_NORMALIZED_DIR.glob("*.json"):
        data = _read_json(path)
        if not isinstance(data, dict):
            continue
        symbol = _normalize_symbol(data.get("candidate_id"))
        if not symbol:
            continue
        rows[symbol] = {
            "quote_price": data.get("price_eur"),
            "currency": "EUR",
            "source": data.get("source_id") or "coingecko_normalized_cache",
            "source_as_of": data.get("as_of") or data.get("provider_last_updated_utc"),
            "freshness": "ready" if data.get("source_quality_ready") else "partial_or_unavailable",
            "movement_24h": data.get("change_24h_pct"),
            "movement_7d": None,
            "movement_30d": None,
            "warnings": ["raw provider data is normalized but still marked unverified"] if data.get("raw_data_unverified") else [],
            "blockers": [],
            "confidence": "medium_high" if data.get("source_quality_ready") else "low",
            "cache_path": str(CRYPTO_NORMALIZED_DIR),
            "source_path": str(path),
        }
    return rows


def _stock_sources() -> dict[str, dict[str, Any]]:
    data = _read_json(STOCK_RANKED_PATH)
    rows: dict[str, dict[str, Any]] = {}
    if not isinstance(data, dict):
        return rows
    for item in data.get("ranked_candidates", []) or []:
        if not isinstance(item, dict):
            continue
        symbol = _normalize_symbol(item.get("symbol"))
        if not symbol:
            continue
        ready = item.get("source_status") == "STOCK_PUBLIC_SOURCE_READY"
        rows[symbol] = {
            "quote_price": item.get("close_price"),
            "currency": item.get("currency"),
            "source": item.get("provider") or "stock_ranked_candidates",
            "source_as_of": item.get("source_as_of") or data.get("current_date"),
            "freshness": "ready" if ready else "partial_or_unavailable",
            "movement_24h": None,
            "movement_7d": None,
            "movement_30d": None,
            "warnings": ["stock candidate is ranked for review only; not approved for purchase"],
            "blockers": [],
            "confidence": "medium_high" if ready else "low",
            "cache_path": str(STOCK_RANKED_PATH),
            "source_path": str(STOCK_RANKED_PATH),
        }
    return rows


def _missing_fields(
    *,
    quote_price: float | None,
    currency: str | None,
    source: str | None,
    source_as_of: str | None,
    movement_24h: float | None,
    movement_7d: float | None,
    movement_30d: float | None,
) -> list[str]:
    missing = []
    if quote_price is None:
        missing.append("quote_price")
    if not currency:
        missing.append("currency")
    if not source:
        missing.append("source")
    if not source_as_of:
        missing.append("source_as_of")
    if movement_24h is None:
        missing.append("movement_24h")
    if movement_7d is None:
        missing.append("movement_7d")
    if movement_30d is None:
        missing.append("movement_30d")
    return missing


def _record_from_selection(
    selection: dict[str, Any],
    *,
    current_date: str,
    crypto_sources: dict[str, dict[str, Any]],
    stock_sources: dict[str, dict[str, Any]],
    etf_resolutions: dict[str, dict[str, Any]],
    fx_conversion_available: bool,
) -> NormalizedMarketDataRecord:
    symbol = _normalize_symbol(selection.get("symbol"))
    lane = str(selection.get("lane") or "")
    amount = selection.get("amount_eur")
    identity = {
        "candidate_id": selection.get("candidate_id"),
        "symbol": symbol,
        "name": selection.get("name"),
        "lane": lane,
    }
    source_row: dict[str, Any] = {}
    trusted = False
    if lane == "crypto":
        source_row = crypto_sources.get(symbol, {})
        trusted = bool(source_row and source_row.get("freshness") == "ready")
    elif lane == "individual_stock":
        source_row = stock_sources.get(symbol, {})
        trusted = bool(source_row and source_row.get("freshness") == "ready")
    elif lane == "etf_fund":
        resolution = etf_resolutions.get(symbol, {})
        source_row = {
            "quote_price": resolution.get("quote_price"),
            "currency": resolution.get("currency"),
            "source": resolution.get("source"),
            "source_as_of": resolution.get("source_as_of"),
            "freshness": resolution.get("freshness"),
            "movement_24h": None,
            "movement_7d": None,
            "movement_30d": None,
            "warnings": list(resolution.get("warnings", []) or []),
            "blockers": list(resolution.get("blockers", []) or []),
            "confidence": resolution.get("confidence"),
            "cache_path": resolution.get("cache_path"),
            "source_path": resolution.get("source_path"),
        }
        identity.update(
            {
                "classification": resolution.get("classification"),
                "tradable_symbol": resolution.get("tradable_symbol"),
                "instrument_identity": resolution.get("instrument_identity"),
                "next_action": resolution.get("next_action"),
            }
        )
        trusted = bool(resolution.get("trusted_quote"))

    quote_price = source_row.get("quote_price")
    currency = source_row.get("currency")
    source = source_row.get("source")
    source_as_of = source_row.get("source_as_of")
    movement_24h = source_row.get("movement_24h")
    movement_7d = source_row.get("movement_7d")
    movement_30d = source_row.get("movement_30d")
    freshness = str(source_row.get("freshness") or "partial_or_unavailable")
    warnings = list(selection.get("warnings") or []) + list(source_row.get("warnings", []) or [])
    blockers = list(source_row.get("blockers", []) or [])

    if _future_date(str(source_as_of) if source_as_of else None, current_date):
        trusted = False
        freshness = "quarantined_future_date"
        warnings.append("source_as_of is after current_date; record is not trusted for assistant decisions")
        blockers.append("future_source_as_of")
    if currency == "USD" and not fx_conversion_available:
        warnings.append("quote is USD; trusted EUR conversion is unavailable, so no EUR conversion is shown")
    if quote_price is None:
        warnings.append("quote price is missing from local assistant-facing data")
    if movement_7d is None or movement_30d is None:
        warnings.append("7d/30d movement history is unavailable from current local cache")

    missing = _missing_fields(
        quote_price=quote_price,
        currency=currency,
        source=source,
        source_as_of=source_as_of,
        movement_24h=movement_24h,
        movement_7d=movement_7d,
        movement_30d=movement_30d,
    )

    return NormalizedMarketDataRecord(
        symbol=symbol,
        lane=lane,
        selected_amount_eur=round(float(amount), 2) if amount is not None else None,
        selected_in_plan=True,
        instrument_identity=identity,
        quote_price=round(float(quote_price), 6) if quote_price is not None else None,
        currency=str(currency) if currency else None,
        source=str(source) if source else None,
        source_as_of=str(source_as_of) if source_as_of else None,
        freshness=freshness,
        movement_24h=round(float(movement_24h), 6) if movement_24h is not None else None,
        movement_7d=round(float(movement_7d), 6) if movement_7d is not None else None,
        movement_30d=round(float(movement_30d), 6) if movement_30d is not None else None,
        missing_fields=missing,
        warnings=list(dict.fromkeys(warnings)),
        blockers=list(dict.fromkeys(blockers)),
        confidence=str(source_row.get("confidence") or ("medium" if trusted else "low")),
        cache_path=source_row.get("cache_path"),
        source_path=source_row.get("source_path"),
        manual_review_required=True,
        trusted_for_assistant=trusted,
    )


def build_normalized_market_data_result(
    *,
    current_date: str = "2026-06-18",
    product_api_result: Any | None = None,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> NormalizedMarketDataResult:
    if product_api_result is None:
        from jarvis.runtime.product_api import build_product_api_result

        product_api_result = build_product_api_result(current_date=current_date)
    fx = build_fx_assistant_bridge_result(current_date=current_date)
    resolver = build_selected_instrument_resolver_result(
        current_date=current_date,
        product_api_result=product_api_result,
    )
    etf_resolutions = {
        _normalize_symbol(item.get("symbol")): item
        for item in resolver.resolutions
    }
    crypto_sources = _crypto_sources()
    stock_sources = _stock_sources()
    records = [
        _record_from_selection(
            selection,
            current_date=current_date,
            crypto_sources=crypto_sources,
            stock_sources=stock_sources,
            etf_resolutions=etf_resolutions,
            fx_conversion_available=fx.conversion_available,
        )
        for selection in _product_selections(product_api_result)
    ]
    trusted_count = sum(1 for record in records if record.trusted_for_assistant)
    partial_count = len(records) - trusted_count
    missing_by_symbol = {
        record.symbol: record.missing_fields
        for record in records
        if record.missing_fields
    }
    warnings = [
        "normalized market data is read-only and assistant-facing",
        "selected amount comes from the manual plan; quote trust comes only from local source evidence",
        "manual review remains required for every external real-world action",
    ]
    if partial_count:
        warnings.append("one or more selected instruments have partial or untrusted quote/history data")
    result = NormalizedMarketDataResult(
        status=STATUS_READY,
        current_date=current_date,
        records=[record.to_dict() for record in records],
        record_count=len(records),
        trusted_record_count=trusted_count,
        partial_record_count=partial_count,
        data_trust_summary={
            "trusted_records": trusted_count,
            "partial_records": partial_count,
            "selected_symbols": [record.symbol for record in records],
            "missing_by_symbol": missing_by_symbol,
            "fx_conversion_available": fx.conversion_available,
            "news_live_fetch_enabled": False,
        },
        warnings=warnings,
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
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def find_normalized_market_data_record(symbol: str, *, current_date: str = "2026-06-18") -> dict[str, Any] | None:
    clean = _normalize_symbol(symbol)
    result = build_normalized_market_data_result(current_date=current_date)
    for record in result.records:
        if _normalize_symbol(record.get("symbol")) == clean:
            return record
    return None


def format_normalized_market_data(result: NormalizedMarketDataResult) -> str:
    lines = [
        "J.A.R.V.I.S. NORMALIZED MARKET DATA",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"records: {result.record_count}",
        f"trusted records: {result.trusted_record_count}",
        f"partial records: {result.partial_record_count}",
        "",
        "RECORDS:",
    ]
    for record in result.records:
        lines.append(
            f"- {record['symbol']}: lane={record['lane']}; amount={record['selected_amount_eur']}; "
            f"price={record['quote_price']} {record['currency']}; 24h={record['movement_24h']}; "
            f"7d={record['movement_7d']}; 30d={record['movement_30d']}; "
            f"source={record['source']}; as_of={record['source_as_of']}; freshness={record['freshness']}; "
            f"trusted={record['trusted_for_assistant']}; missing={', '.join(record['missing_fields']) or 'none'}"
        )
    lines.extend(
        [
            "",
            "WARNINGS:",
            *[f"- {warning}" for warning in result.warnings],
            "safety: no broker, credentials, orders, trades, buy/sell requests, or auto-approval.",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build normalized assistant-facing market data.")
    parser.add_argument("--market-data-normalized", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)
    result = build_normalized_market_data_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_normalized_market_data(result))
    return 0


__all__ = [
    "STATUS_READY",
    "NormalizedMarketDataRecord",
    "NormalizedMarketDataResult",
    "build_normalized_market_data_result",
    "find_normalized_market_data_record",
    "format_normalized_market_data",
    "main",
]
