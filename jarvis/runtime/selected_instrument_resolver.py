from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any


STATUS_READY = "JARVIS_V118_0_SELECTED_INSTRUMENT_RESOLVER_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/selected_instrument_resolver_latest.json"
ETF_SELECTED_PATH = Path("jarvis/local/stock_fund_etf_selected_instrument.local.json")
ETF_UNIVERSE_PATH = Path("jarvis/local/stock_fund_etf_instrument_universe.local.json")
ETF_PUBLIC_SOURCES_PATH = Path("jarvis/local/stock_fund_etf_public_sources.local.json")
ETF_PUBLIC_SIGNALS_PATH = Path("jarvis/local/stock_fund_etf_public_signals.local.json")


@dataclass(frozen=True)
class SelectedInstrumentResolution:
    symbol: str
    candidate_id: str | None
    lane: str
    selected_amount_eur: float | None
    selected_in_plan: bool
    classification: str
    tradable_symbol: str | None
    instrument_identity: dict[str, Any]
    quote_price: float | None
    currency: str | None
    source: str | None
    source_as_of: str | None
    freshness: str
    trusted_quote: bool
    missing_fields: list[str]
    warnings: list[str]
    blockers: list[str]
    confidence: str
    cache_path: str | None
    source_path: str | None
    next_action: str
    manual_review_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SelectedInstrumentResolverResult:
    status: str
    current_date: str
    resolutions: list[dict[str, Any]]
    trusted_quote_count: int
    missing_or_untrusted_count: int
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


def _date_is_future(value: str | None, current_date: str) -> bool:
    if not value:
        return False
    try:
        source_day = date.fromisoformat(str(value)[:10])
        current_day = date.fromisoformat(str(current_date)[:10])
    except ValueError:
        return False
    return source_day > current_day


def _product_selections(product_api_result: Any) -> list[dict[str, Any]]:
    if product_api_result is None:
        from jarvis.runtime.product_api import build_product_api_result

        product_api_result = build_product_api_result(current_date="2026-06-18")
    return list(getattr(product_api_result, "week_plan", {}).get("selected_instruments", []) or [])


def _etf_decisions_by_symbol() -> dict[str, dict[str, Any]]:
    data = _read_json(ETF_SELECTED_PATH)
    rows: dict[str, dict[str, Any]] = {}
    if not isinstance(data, dict):
        return rows
    for item in data.get("instrument_decisions", []) or []:
        if isinstance(item, dict):
            symbol = _normalize_symbol(item.get("symbol"))
            if symbol:
                rows[symbol] = item
    return rows


def _universe_instruments() -> dict[str, list[dict[str, Any]]]:
    data = _read_json(ETF_UNIVERSE_PATH)
    rows: dict[str, list[dict[str, Any]]] = {}
    if not isinstance(data, dict):
        return rows
    sleeves = data.get("sleeves", {}) or {}
    if not isinstance(sleeves, dict):
        return rows
    for sleeve_id, sleeve in sleeves.items():
        if isinstance(sleeve, dict):
            instruments = [item for item in sleeve.get("instruments", []) or [] if isinstance(item, dict)]
            rows[str(sleeve_id).lower()] = instruments
    return rows


def _public_source_for_candidate(candidate_id: str | None) -> dict[str, Any] | None:
    data = _read_json(ETF_PUBLIC_SOURCES_PATH)
    if not isinstance(data, dict) or not candidate_id:
        return None
    sources = data.get("sources", {}) or {}
    item = sources.get(str(candidate_id).lower())
    return item if isinstance(item, dict) else None


def _public_signal_for_candidate(candidate_id: str | None) -> dict[str, Any] | None:
    data = _read_json(ETF_PUBLIC_SIGNALS_PATH)
    if not isinstance(data, dict) or not candidate_id:
        return None
    target = str(candidate_id).lower()
    for item in data.get("signals", []) or []:
        if isinstance(item, dict) and str(item.get("candidate_id") or "").lower() == target:
            return item
    return None


def _missing_fields(
    *,
    quote_price: float | None,
    currency: str | None,
    source: str | None,
    source_as_of: str | None,
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
    return missing


def _resolution_for_etf_selection(selection: dict[str, Any], current_date: str) -> SelectedInstrumentResolution:
    symbol = _normalize_symbol(selection.get("symbol"))
    candidate_id = str(selection.get("candidate_id") or "").lower() or None
    amount = selection.get("amount_eur")
    decisions = _etf_decisions_by_symbol()
    universe = _universe_instruments()
    decision = decisions.get(symbol, {})
    public_source = _public_source_for_candidate(candidate_id)
    public_signal = _public_signal_for_candidate(candidate_id)
    warnings = list(selection.get("warnings") or [])
    blockers: list[str] = []
    identity: dict[str, Any] = {}
    tradable_symbol: str | None = None
    quote_price: float | None = None
    currency: str | None = None
    source: str | None = None
    source_as_of: str | None = None
    source_path: str | None = None
    cache_path = str(ETF_SELECTED_PATH)
    trusted_quote = False
    classification = "etf_fund_candidate_missing_quote_source"
    freshness = "partial_or_unavailable"
    confidence = "low"
    next_action = "Add a verified public quote source/cache row with symbol, provider, price, currency, source_as_of, and source URL."

    if symbol == "GLOBAL_CORE_ETF":
        mapped = (universe.get("global_core_etf") or [None])[0]
        if isinstance(mapped, dict):
            identity = dict(mapped)
            tradable_symbol = _normalize_symbol(mapped.get("symbol")) or None
            warnings.append(
                "GLOBAL_CORE_ETF is an internal sleeve placeholder; local universe suggests a candidate instrument, but no public quote/source evidence is present."
            )
        classification = "internal_sleeve_placeholder_not_tradable"
        blockers.append("GLOBAL_CORE_ETF has no trusted tradable-instrument quote/source evidence")
        next_action = "Choose and verify the real core ETF instrument, then populate the public source manifest and quote cache."
    elif symbol == "VWCE":
        identity = {
            "name": selection.get("name") or "Vanguard FTSE All-World UCITS ETF",
            "symbol": "VWCE",
            "candidate_id": candidate_id,
        }
        warnings.append("VWCE is selected by the scoring model, but no local quote/source/freshness record exists.")
        blockers.append("VWCE quote/source/freshness missing")
        next_action = "Add VWCE to the ETF public source manifest and refresh a local quote cache before trusting the assistant answer."
    elif symbol == "IS3Q.DE":
        identity = dict(decision) if decision else {
            "name": selection.get("name"),
            "symbol": symbol,
            "candidate_id": candidate_id,
        }
        tradable_symbol = symbol
        quote_price = decision.get("close_price") if decision else None
        currency = decision.get("currency") if decision else None
        source = decision.get("provider") if decision else None
        source_as_of = decision.get("source_as_of") if decision else None
        source_path = str(ETF_SELECTED_PATH)
        if _date_is_future(source_as_of, current_date):
            classification = "tradable_instrument_quarantined_future_source_date"
            freshness = "quarantined_future_date"
            warnings.extend(list(decision.get("warnings") or []))
            warnings.append("IS3Q.DE source_as_of is after the requested current_date, so the quote is not trusted.")
            blockers.append("IS3Q.DE quote source_as_of is in the future")
            next_action = "Refresh or correct the IS3Q.DE quote cache so source_as_of is not in the future."
        elif decision.get("public_source_status") == "ETF_PUBLIC_SOURCE_READY":
            classification = "tradable_instrument_trusted_quote"
            freshness = "ready"
            trusted_quote = True
            confidence = "medium_high"
            next_action = "Manually verify the platform ticker/ISIN and latest quote before any external action."
        else:
            classification = "tradable_instrument_untrusted_quote"
            freshness = "partial_or_unavailable"
            warnings.extend(list(decision.get("warnings") or []))
            blockers.append("IS3Q.DE public source status is not trusted")
    else:
        signal = public_signal or {}
        source_row = public_source or {}
        identity = {"name": selection.get("name"), "symbol": symbol, "candidate_id": candidate_id}
        quote_price = signal.get("close_price")
        currency = signal.get("currency") or source_row.get("currency")
        source = signal.get("provider") or source_row.get("provider")
        source_as_of = signal.get("source_as_of")
        source_path = str(ETF_PUBLIC_SIGNALS_PATH) if signal else str(ETF_PUBLIC_SOURCES_PATH)
        if signal.get("source_status") == "ETF_PUBLIC_SOURCE_READY" and not _date_is_future(source_as_of, current_date):
            classification = "tradable_instrument_trusted_quote"
            freshness = "ready"
            trusted_quote = True
            confidence = "medium_high"
        else:
            warnings.append(f"{symbol} has no trusted local ETF/fund quote record.")
            blockers.append(f"{symbol} quote/source/freshness missing or untrusted")

    missing = _missing_fields(
        quote_price=quote_price,
        currency=currency,
        source=source,
        source_as_of=source_as_of,
    )
    if missing:
        warnings.append("Missing ETF/fund fields: " + ", ".join(missing) + ".")

    return SelectedInstrumentResolution(
        symbol=symbol,
        candidate_id=candidate_id,
        lane="etf_fund",
        selected_amount_eur=round(float(amount), 2) if amount is not None else None,
        selected_in_plan=True,
        classification=classification,
        tradable_symbol=tradable_symbol,
        instrument_identity=identity,
        quote_price=round(float(quote_price), 6) if quote_price is not None else None,
        currency=str(currency) if currency else None,
        source=str(source) if source else None,
        source_as_of=str(source_as_of) if source_as_of else None,
        freshness=freshness,
        trusted_quote=trusted_quote,
        missing_fields=missing,
        warnings=list(dict.fromkeys(warnings)),
        blockers=list(dict.fromkeys(blockers)),
        confidence=confidence,
        cache_path=cache_path,
        source_path=source_path,
        next_action=next_action,
        manual_review_required=True,
    )


def build_selected_instrument_resolver_result(
    *,
    current_date: str = "2026-06-18",
    product_api_result: Any | None = None,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> SelectedInstrumentResolverResult:
    if product_api_result is None:
        from jarvis.runtime.product_api import build_product_api_result

        product_api_result = build_product_api_result(current_date=current_date)
    selections = _product_selections(product_api_result)
    resolutions = [
        _resolution_for_etf_selection(selection, current_date)
        for selection in selections
        if str(selection.get("lane") or "") == "etf_fund"
    ]
    trusted = sum(1 for item in resolutions if item.trusted_quote)
    untrusted = len(resolutions) - trusted
    warnings = [
        "selected instrument resolver is read-only",
        "ETF/fund scoring selections are not treated as trusted tradable quote data unless source evidence is present",
    ]
    if untrusted:
        warnings.append("one or more ETF/fund selected instruments require manual data review before external action")
    result = SelectedInstrumentResolverResult(
        status=STATUS_READY,
        current_date=current_date,
        resolutions=[item.to_dict() for item in resolutions],
        trusted_quote_count=trusted,
        missing_or_untrusted_count=untrusted,
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


def find_selected_instrument_resolution(symbol: str, *, current_date: str = "2026-06-18") -> dict[str, Any] | None:
    clean = _normalize_symbol(symbol)
    result = build_selected_instrument_resolver_result(current_date=current_date)
    for item in result.resolutions:
        if _normalize_symbol(item.get("symbol")) == clean:
            return item
    return None


def format_selected_instrument_resolver(result: SelectedInstrumentResolverResult) -> str:
    lines = [
        "J.A.R.V.I.S. SELECTED INSTRUMENT RESOLVER",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"trusted ETF/fund quotes: {result.trusted_quote_count}",
        f"missing or untrusted ETF/fund records: {result.missing_or_untrusted_count}",
        "",
        "RESOLUTIONS:",
    ]
    for item in result.resolutions:
        lines.append(
            f"- {item['symbol']}: classification={item['classification']}; trusted_quote={item['trusted_quote']}; "
            f"price={item['quote_price']} {item['currency']}; source={item['source']}; "
            f"as_of={item['source_as_of']}; freshness={item['freshness']}; next_action={item['next_action']}"
        )
    lines.extend(
        [
            "",
            "WARNINGS:",
            *[f"- {warning}" for warning in result.warnings],
            "",
            "SAFETY:",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve selected ETF/fund instruments safely.")
    parser.add_argument("--selected-instrument-resolver", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)
    result = build_selected_instrument_resolver_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_selected_instrument_resolver(result))
    return 0


__all__ = [
    "STATUS_READY",
    "SelectedInstrumentResolution",
    "SelectedInstrumentResolverResult",
    "build_selected_instrument_resolver_result",
    "find_selected_instrument_resolution",
    "format_selected_instrument_resolver",
    "main",
]
