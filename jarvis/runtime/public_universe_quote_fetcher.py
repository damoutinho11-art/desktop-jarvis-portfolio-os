from __future__ import annotations

import argparse
import json
import math
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_READY = "JARVIS_V123_0_AUTONOMOUS_ETF_IDENTITY_QUOTE_BRIDGE_READY_SAFE"
DEFAULT_CACHE_PATH = "jarvis/local/public_data/v120_public_universe_quote_cache.local.json"
DEFAULT_OUTPUT_PATH = "outputs/public_universe_quote_fetch_latest.json"

CRYPTO_ID_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "LINK": "chainlink",
    "AVAX": "avalanche-2",
    "HYPE": "hyperliquid",
    "INJ": "injective-protocol",
    "NEAR": "near",
    "RENDER": "render-token",
    "TAO": "bittensor",
}

CORE_CRYPTO_REFRESH_SYMBOLS = ("BTC", "ETH")

UNRESOLVED_PROVIDER_SYMBOLS = {
    "GROWTH_NASDAQ_ETF": "autonomous identity unresolved: generic growth/Nasdaq sleeve has no verified tradable ticker/ISIN yet",
}

MANUAL_PROVIDER_SYMBOLS = {
    "VWCE": ("VWCE.DE", "autonomous identity check: VWCE.DE was used as the read-only quote symbol; final buy remains manual outside J.A.R.V.I.S."),
    "IS3Q.DE": ("IS3Q.DE", "direct exchange ticker"),
    "GLOBAL_CORE_ETF": ("EUNL.DE", "autonomous identity verification incomplete: GLOBAL_CORE_ETF is an internal sleeve mapped to EUNL.DE as a candidate quote symbol; final buy remains manual outside J.A.R.V.I.S."),
    "QUALITY_ETF": ("IS3Q.DE", "autonomous identity verification incomplete: QUALITY_ETF is mapped to IS3Q.DE as a candidate quote symbol; final buy remains manual outside J.A.R.V.I.S."),
}


@dataclass(frozen=True)
class QuoteFetchTarget:
    symbol: str
    lane: str
    provider: str
    provider_symbol: str
    manual_review_required: bool
    mapping_warning: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class QuoteFetchRecord:
    symbol: str
    lane: str
    provider: str
    provider_symbol: str
    quote_price: float | None
    currency: str | None
    source_as_of: str | None
    freshness: str
    movement_24h_pct: float | None
    movement_7d_pct: float | None
    movement_30d_pct: float | None
    source_url: str
    manual_review_required: bool
    missing_fields: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublicUniverseQuoteFetchResult:
    status: str
    current_date: str
    dry_run: bool
    cache_written: bool
    cache_path: str
    report_written: bool
    report_path: str
    target_count: int
    records: list[dict[str, Any]]
    provider_failures: list[str]
    unresolved_symbols: list[str]
    warnings: list[str]
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    buy_sell_request_created: bool
    order_created: bool
    trade_executed: bool
    auto_approval_enabled: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _fetch_json(url: str, timeout: int = 20) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "JARVIS-Portfolio-OS/1.0 read-only public quote cache",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _pct(current: float | None, previous: float | None) -> float | None:
    if current is None or previous in (None, 0):
        return None
    value = ((current - previous) / previous) * 100.0
    if not math.isfinite(value):
        return None
    return round(value, 6)


def _last_non_null(values: list[Any]) -> tuple[int | None, float | None]:
    for index in range(len(values) - 1, -1, -1):
        try:
            value = float(values[index])
        except (TypeError, ValueError):
            continue
        if math.isfinite(value):
            return index, value
    return None, None


def _value_days_back(values: list[Any], latest_index: int, days_back: int) -> float | None:
    target = max(0, latest_index - days_back)
    for index in range(target, -1, -1):
        try:
            value = float(values[index])
        except (TypeError, ValueError):
            continue
        if math.isfinite(value):
            return value
    return None


def _date_from_unix(seconds: Any) -> str | None:
    if seconds is None:
        return None
    try:
        return datetime.fromtimestamp(float(seconds), tz=timezone.utc).date().isoformat()
    except Exception:
        return None


def _date_from_ms(ms: Any) -> str | None:
    if ms is None:
        return None
    try:
        return datetime.fromtimestamp(float(ms) / 1000.0, tz=timezone.utc).date().isoformat()
    except Exception:
        return None


def _freshness(source_as_of: str | None, quote_available: bool, current_date: str) -> tuple[str, list[str]]:
    if not quote_available:
        return "missing_quote", ["quote missing"]
    if not source_as_of:
        return "partial_or_unavailable", ["missing source_as_of"]
    if source_as_of[:10] > current_date:
        return "quarantined_future_date", [f"source_as_of {source_as_of[:10]} is after current_date {current_date}"]
    return "ready", []


def _missing_fields(record: QuoteFetchRecord) -> list[str]:
    missing = []
    if record.quote_price is None:
        missing.append("quote_price")
    if not record.currency:
        missing.append("currency")
    if not record.provider:
        missing.append("source")
    if not record.source_as_of:
        missing.append("source_as_of")
    if record.movement_24h_pct is None:
        missing.append("movement_24h")
    if record.movement_7d_pct is None:
        missing.append("movement_7d")
    if record.movement_30d_pct is None:
        missing.append("movement_30d")
    return missing


def fetch_yahoo_quote(target: QuoteFetchTarget, current_date: str) -> QuoteFetchRecord:
    encoded = urllib.parse.quote(target.provider_symbol)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{encoded}?range=1mo&interval=1d"
    data = _fetch_json(url)
    result = (data.get("chart", {}).get("result") or [None])[0]
    if not result:
        raise RuntimeError(f"Yahoo chart returned no result for {target.provider_symbol}")

    meta = result.get("meta", {}) or {}
    quote = ((result.get("indicators", {}) or {}).get("quote") or [{}])[0]
    closes = quote.get("close") or []
    timestamps = result.get("timestamp") or []

    latest_index, latest_close = _last_non_null(closes)
    quote_price = None
    if meta.get("regularMarketPrice") is not None:
        try:
            quote_price = float(meta["regularMarketPrice"])
        except Exception:
            quote_price = None
    if quote_price is None:
        quote_price = latest_close

    source_as_of = _date_from_unix(meta.get("regularMarketTime"))
    if not source_as_of and latest_index is not None and latest_index < len(timestamps):
        source_as_of = _date_from_unix(timestamps[latest_index])

    movement_24h = movement_7d = movement_30d = None
    if latest_index is not None and latest_close is not None:
        movement_24h = _pct(latest_close, _value_days_back(closes, latest_index, 1))
        movement_7d = _pct(latest_close, _value_days_back(closes, latest_index, 7))
        movement_30d = _pct(latest_close, _value_days_back(closes, latest_index, 30))

    freshness, freshness_warnings = _freshness(source_as_of, quote_price is not None, current_date)
    warnings = list(freshness_warnings)
    if target.mapping_warning:
        warnings.append(target.mapping_warning)

    temp = QuoteFetchRecord(
        symbol=target.symbol,
        lane=target.lane,
        provider=target.provider,
        provider_symbol=target.provider_symbol,
        quote_price=round(float(quote_price), 6) if quote_price is not None else None,
        currency=meta.get("currency"),
        source_as_of=source_as_of,
        freshness=freshness,
        movement_24h_pct=movement_24h,
        movement_7d_pct=movement_7d,
        movement_30d_pct=movement_30d,
        source_url=url,
        manual_review_required=target.manual_review_required or freshness != "ready",
        missing_fields=[],
        warnings=warnings,
    )
    return QuoteFetchRecord(**{**temp.to_dict(), "missing_fields": _missing_fields(temp)})


def fetch_coingecko_quote(target: QuoteFetchTarget, current_date: str) -> QuoteFetchRecord:
    url = (
        "https://api.coingecko.com/api/v3/coins/"
        + urllib.parse.quote(target.provider_symbol)
        + "/market_chart?vs_currency=eur&days=31&interval=daily"
    )
    data = _fetch_json(url)
    prices = data.get("prices") or []
    if not prices:
        raise RuntimeError(f"CoinGecko returned no price rows for {target.provider_symbol}")

    timestamps = [row[0] for row in prices if isinstance(row, list) and len(row) >= 2]
    values = [row[1] for row in prices if isinstance(row, list) and len(row) >= 2]

    latest_index, latest_price = _last_non_null(values)
    source_as_of = _date_from_ms(timestamps[latest_index]) if latest_index is not None and latest_index < len(timestamps) else None

    movement_24h = movement_7d = movement_30d = None
    if latest_index is not None and latest_price is not None:
        movement_24h = _pct(latest_price, _value_days_back(values, latest_index, 1))
        movement_7d = _pct(latest_price, _value_days_back(values, latest_index, 7))
        movement_30d = _pct(latest_price, _value_days_back(values, latest_index, 30))

    freshness, warnings = _freshness(source_as_of, latest_price is not None, current_date)
    temp = QuoteFetchRecord(
        symbol=target.symbol,
        lane=target.lane,
        provider=target.provider,
        provider_symbol=target.provider_symbol,
        quote_price=round(float(latest_price), 6) if latest_price is not None else None,
        currency="EUR",
        source_as_of=source_as_of,
        freshness=freshness,
        movement_24h_pct=movement_24h,
        movement_7d_pct=movement_7d,
        movement_30d_pct=movement_30d,
        source_url=url,
        manual_review_required=target.manual_review_required or freshness != "ready",
        missing_fields=[],
        warnings=warnings,
    )
    return QuoteFetchRecord(**{**temp.to_dict(), "missing_fields": _missing_fields(temp)})



def fetch_coingecko_markets_quotes(
    targets: list[QuoteFetchTarget],
    current_date: str,
) -> tuple[list[QuoteFetchRecord], list[str]]:
    if not targets:
        return [], []

    ids = ",".join(dict.fromkeys(target.provider_symbol for target in targets))
    url = (
        "https://api.coingecko.com/api/v3/coins/markets"
        + "?vs_currency=eur"
        + "&ids="
        + urllib.parse.quote(ids)
        + "&price_change_percentage=24h,7d,30d"
        + "&per_page=250&page=1&sparkline=false"
    )
    data = _fetch_json(url)
    if not isinstance(data, list):
        raise RuntimeError("CoinGecko markets endpoint returned non-list payload")

    by_id = {str(row.get("id") or ""): row for row in data if isinstance(row, dict)}
    records: list[QuoteFetchRecord] = []
    failures: list[str] = []

    for target in targets:
        row = by_id.get(target.provider_symbol)
        if not row:
            failures.append(f"{target.symbol}:{target.provider}:{target.provider_symbol}: CoinGecko markets batch returned no row")
            continue

        latest_price = row.get("current_price")
        source_as_of = str(row.get("last_updated") or "")[:10] or None
        freshness, freshness_warnings = _freshness(source_as_of, latest_price is not None, current_date)

        warnings = [
            "CoinGecko markets batch endpoint used to reduce public rate-limit risk",
            *freshness_warnings,
        ]
        if target.mapping_warning:
            warnings.append(target.mapping_warning)

        record = QuoteFetchRecord(
            symbol=target.symbol,
            lane=target.lane,
            provider=target.provider,
            provider_symbol=target.provider_symbol,
            quote_price=float(latest_price) if latest_price is not None else None,
            currency="EUR",
            source_as_of=source_as_of,
            freshness=freshness,
            movement_24h_pct=round(float(row.get("price_change_percentage_24h_in_currency") or row.get("price_change_percentage_24h")), 6) if (row.get("price_change_percentage_24h_in_currency") or row.get("price_change_percentage_24h")) is not None else None,
            movement_7d_pct=round(float(row.get("price_change_percentage_7d_in_currency")), 6) if row.get("price_change_percentage_7d_in_currency") is not None else None,
            movement_30d_pct=round(float(row.get("price_change_percentage_30d_in_currency")), 6) if row.get("price_change_percentage_30d_in_currency") is not None else None,
            source_url=url,
            manual_review_required=target.manual_review_required,
            missing_fields=[],
            warnings=warnings,
        )
        record = replace(record, missing_fields=_missing_fields(record))
        records.append(record)

    return records, failures


def _load_existing_cache_payload(cache_path: str | Path) -> dict[str, Any]:
    path = Path(cache_path)
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _merge_cache_records(existing_records: list[Any], new_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    for raw in existing_records or []:
        if isinstance(raw, dict) and raw.get("symbol"):
            merged[str(raw["symbol"]).upper()] = raw
    for raw in new_records or []:
        if isinstance(raw, dict) and raw.get("symbol"):
            merged[str(raw["symbol"]).upper()] = raw
    return [merged[symbol] for symbol in sorted(merged)]



def _target_from_symbol(symbol: str, lane: str) -> QuoteFetchTarget | None:
    symbol = symbol.upper()
    if symbol in UNRESOLVED_PROVIDER_SYMBOLS:
        try:
            from jarvis.runtime.etf_identity_resolver import resolve_etf_identity

            resolution = resolve_etf_identity(symbol)
            best = resolution.best_candidate or {}
            provider_symbol = best.get("provider_symbol")
            if provider_symbol:
                return QuoteFetchTarget(
                    symbol=symbol,
                    lane=lane,
                    provider="yahoo_chart_read_only",
                    provider_symbol=str(provider_symbol),
                    manual_review_required=True,
                    mapping_warning=(
                        f"autonomous identity resolver selected {best.get('symbol')} / {provider_symbol} "
                        f"for {symbol}; final buy remains manual outside J.A.R.V.I.S."
                    ),
                )
        except Exception:
            return None
        return None

    if lane == "crypto" or symbol in CRYPTO_ID_MAP:
        coin_id = CRYPTO_ID_MAP.get(symbol)
        if not coin_id:
            return None
        return QuoteFetchTarget(
            symbol=symbol,
            lane="crypto",
            provider="coingecko_read_only",
            provider_symbol=coin_id,
            manual_review_required=False,
            mapping_warning=None,
        )

    if lane in {"etf_fund", "individual_stock"}:
        if symbol in MANUAL_PROVIDER_SYMBOLS:
            provider_symbol, warning = MANUAL_PROVIDER_SYMBOLS[symbol]
            return QuoteFetchTarget(
                symbol=symbol,
                lane=lane,
                provider="yahoo_chart_read_only",
                provider_symbol=provider_symbol,
                manual_review_required="candidate mapping" in warning or "placeholder" in warning,
                mapping_warning=warning,
            )
        if "." in symbol or lane == "individual_stock":
            return QuoteFetchTarget(
                symbol=symbol,
                lane=lane,
                provider="yahoo_chart_read_only",
                provider_symbol=symbol,
                manual_review_required=False,
                mapping_warning=None,
            )

    return None


def build_quote_fetch_targets(current_date: str, max_targets: int = 30) -> tuple[list[QuoteFetchTarget], list[str]]:
    from jarvis.runtime.public_universe_data_coverage import build_public_universe_data_coverage_result

    coverage = build_public_universe_data_coverage_result(current_date=current_date)
    by_symbol = {record["symbol"].upper(): record for record in coverage.records}

    targets: list[QuoteFetchTarget] = []
    unresolved: list[str] = []
    seen: set[str] = set()

    for symbol in coverage.next_fetch_priority[:max_targets]:
        clean = str(symbol).upper()
        if clean in seen:
            continue
        seen.add(clean)
        lane = str(by_symbol.get(clean, {}).get("lane") or "")
        target = _target_from_symbol(clean, lane)
        if target is None:
            unresolved.append(clean)
        else:
            targets.append(target)

    for core_symbol in CORE_CRYPTO_REFRESH_SYMBOLS:
        if core_symbol in seen:
            continue
        target = _target_from_symbol(core_symbol, "crypto")
        if target is not None:
            targets.append(target)
            seen.add(core_symbol)

    return targets, unresolved


def build_public_universe_quote_fetch_result(
    *,
    current_date: str = "2026-06-20",
    dry_run: bool = False,
    write_cache: bool = False,
    write_report: bool = False,
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    report_path: str | Path = DEFAULT_OUTPUT_PATH,
    max_targets: int = 30,
) -> PublicUniverseQuoteFetchResult:
    targets, unresolved = build_quote_fetch_targets(current_date=current_date, max_targets=max_targets)
    records: list[dict[str, Any]] = []
    failures: list[str] = []
    warnings = [
        "read-only public quote fetch only",
        "no broker, credential, order, trade, or auto-approval capability is enabled",
        "provider URLs are public and contain no API keys",
        "GLOBAL_CORE_ETF and QUALITY_ETF mappings require stronger autonomous identity evidence before J.A.R.V.I.S. treats them as fully resolved; final real-world buy remains manual.",
    ]

    if not dry_run:
        coingecko_targets = [target for target in targets if target.provider == "coingecko_read_only"]
        other_targets = [target for target in targets if target.provider != "coingecko_read_only"]
        if coingecko_targets:
            try:
                batch_records, batch_failures = fetch_coingecko_markets_quotes(coingecko_targets, current_date)
                records.extend(record.to_dict() for record in batch_records)
                failures.extend(batch_failures)
            except Exception as exc:
                failures.append(f"coingecko_batch: {exc}")
        for target in other_targets:
            try:
                if target.provider == "yahoo_chart_read_only":
                    record = fetch_yahoo_quote(target, current_date)
                else:
                    raise RuntimeError(f"unsupported provider {target.provider}")
                records.append(record.to_dict())
            except Exception as exc:
                failures.append(f"{target.symbol}:{target.provider}:{target.provider_symbol}: {exc}")
    payload = {
        "status": STATUS_READY,
        "current_date": current_date,
        "dry_run": dry_run,
        "targets": [target.to_dict() for target in targets],
        "records": records,
        "provider_failures": failures,
        "unresolved_symbols": unresolved,
        "warnings": warnings,
    }

    if write_cache and not dry_run:
        Path(cache_path).parent.mkdir(parents=True, exist_ok=True)
        existing_payload = _load_existing_cache_payload(cache_path)
        payload_to_write = dict(payload)
        payload_to_write["records"] = _merge_cache_records(existing_payload.get("records", []), records)
        Path(cache_path).write_text(json.dumps(payload_to_write, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result = PublicUniverseQuoteFetchResult(
        status=STATUS_READY,
        current_date=current_date,
        dry_run=dry_run,
        cache_written=bool(write_cache and not dry_run),
        cache_path=str(cache_path),
        report_written=bool(write_report),
        report_path=str(report_path),
        target_count=len(targets),
        records=records,
        provider_failures=failures,
        unresolved_symbols=unresolved,
        warnings=warnings,
        execution_forbidden=True,
        broker_connection=False,
        credentials_used=False,
        buy_sell_request_created=False,
        order_created=False,
        trade_executed=False,
        auto_approval_enabled=False,
    )

    if write_report:
        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        Path(report_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return result


def format_public_universe_quote_fetch(result: PublicUniverseQuoteFetchResult) -> str:
    lines = [
        "J.A.R.V.I.S. PUBLIC UNIVERSE QUOTE FETCHER",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"dry run: {result.dry_run}",
        f"target count: {result.target_count}",
        f"records fetched: {len(result.records)}",
        f"cache written: {result.cache_written}",
        f"cache path: {result.cache_path}",
        "",
        "FETCHED RECORDS:",
    ]
    if result.records:
        for record in result.records:
            lines.append(
                f"- {record['symbol']} via {record['provider_symbol']}: "
                f"price={record['quote_price']} {record['currency']}; "
                f"as_of={record['source_as_of']}; freshness={record['freshness']}; "
                f"24h={record['movement_24h_pct']}; 7d={record['movement_7d_pct']}; 30d={record['movement_30d_pct']}; "
                f"verification_status={'AUTO_VERIFICATION_INCOMPLETE' if record['manual_review_required'] else 'AUTO_VERIFIED'}; final_buy_manual=True"
            )
            for warning in record.get("warnings") or []:
                lines.append(f"  warning: {warning}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("UNRESOLVED SYMBOLS:")
    lines.extend([f"- {symbol}" for symbol in result.unresolved_symbols] or ["- none"])

    lines.append("")
    lines.append("PROVIDER FAILURES:")
    lines.extend([f"- {failure}" for failure in result.provider_failures] or ["- none"])

    lines.extend(
        [
            "",
            "SAFETY:",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- buy/sell request created: {result.buy_sell_request_created}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            f"- auto approval enabled: {result.auto_approval_enabled}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-date", default="2026-06-20")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write-cache", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--cache-path", default=DEFAULT_CACHE_PATH)
    parser.add_argument("--report-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--max-targets", type=int, default=30)
    args = parser.parse_args(argv)

    result = build_public_universe_quote_fetch_result(
        current_date=args.current_date,
        dry_run=args.dry_run,
        write_cache=args.write_cache,
        write_report=args.write_report,
        cache_path=args.cache_path,
        report_path=args.report_path,
        max_targets=args.max_targets,
    )
    print(format_public_universe_quote_fetch(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
