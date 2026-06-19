from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


STATUS_READY = "JARVIS_V119_0_PUBLIC_UNIVERSE_DATA_COVERAGE_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/public_universe_data_coverage_latest.json"

LOCAL_ROOTS = [
    Path("jarvis/local"),
    Path("jarvis/local/public_data"),
]


SYMBOL_KEYS = (
    "symbol",
    "ticker",
    "asset_symbol",
    "instrument_symbol",
    "provider_symbol",
    "resolved_symbol",
    "selected_symbol",
    "candidate_symbol",
    "id",
    "candidate_id",
)

QUOTE_KEYS = (
    "quote_price",
    "price",
    "close_price",
    "regularMarketPrice",
    "current_price",
    "market_price",
    "last_price",
    "nav",
)

CURRENCY_KEYS = (
    "currency",
    "quote_currency",
    "price_currency",
)

AS_OF_KEYS = (
    "source_as_of",
    "as_of",
    "quote_as_of",
    "date",
    "source_date",
    "timestamp_date",
)

SOURCE_KEYS = (
    "source",
    "provider",
    "quote_provider",
    "source_name",
)


@dataclass(frozen=True)
class UniverseCoverageRecord:
    symbol: str
    lane: str
    source_file: str
    selected_now: bool
    quote_available: bool
    trusted_quote: bool
    quote_price: float | None
    currency: str | None
    source: str | None
    source_as_of: str | None
    freshness: str
    identity_confidence: str
    missing_fields: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LaneCoverageSummary:
    lane: str
    total_symbols: int
    selected_symbols: int
    quote_available: int
    trusted_quote: int
    missing_quote: int
    stale_or_untrusted: int
    future_dated: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublicUniverseDataCoverageResult:
    status: str
    current_date: str
    total_records: int
    total_symbols: int
    selected_symbols: list[str]
    lane_summaries: list[dict[str, Any]]
    records: list[dict[str, Any]]
    missing_quote_symbols: list[str]
    future_dated_symbols: list[str]
    untrusted_symbols: list[str]
    next_fetch_priority: list[str]
    report_written: bool
    report_path: str
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool
    auto_approval_enabled: bool
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _iter_dicts(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        found.append(value)
        for child in value.values():
            found.extend(_iter_dicts(child))
    elif isinstance(value, list):
        for item in value:
            found.extend(_iter_dicts(item))
    return found


def _first_value(record: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in record and record[key] not in (None, "", [], {}):
            return record[key]
    return None


def _to_float(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number


def _clean_symbol(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    if len(text) > 40:
        return None
    bad_fragments = [" ", "{", "}", "[", "]", "http", "\\", "/"]
    if any(fragment in text for fragment in bad_fragments):
        return None
    return text.upper()


def _infer_lane(path: Path, record: dict[str, Any], symbol: str) -> str:
    joined = f"{path.as_posix()} {json.dumps(record, default=str)[:500]}".lower()

    explicit = str(record.get("lane") or record.get("asset_lane") or record.get("category") or "").lower()
    if "crypto" in explicit:
        return "crypto"
    if "etf" in explicit or "fund" in explicit:
        return "etf_fund"
    if "stock" in explicit or "equity" in explicit:
        return "individual_stock"

    if "crypto" in joined or symbol in {"BTC", "ETH", "SOL", "LINK", "AVAX", "HYPE", "NEAR", "RENDER", "INJ", "TAO"}:
        return "crypto"
    if "etf" in joined or "fund" in joined or symbol.endswith(".DE") or symbol in {"VWCE", "GLOBAL_CORE_ETF", "IS3Q.DE"}:
        return "etf_fund"
    if "stock" in joined or "equity" in joined or symbol in {"MSFT", "AAPL", "GOOGL", "AMZN", "NVDA", "META"}:
        return "individual_stock"

    return "unknown"


def _freshness(source_as_of: str | None, quote_available: bool, current_date: str) -> tuple[str, list[str]]:
    warnings: list[str] = []
    if not quote_available:
        return "missing_quote", ["quote missing"]
    if not source_as_of:
        return "partial_or_unavailable", ["source_as_of missing"]
    source_text = str(source_as_of)[:10]
    if source_text > current_date:
        return "quarantined_future_date", [f"source_as_of {source_text} is after current_date {current_date}"]
    return "ready", warnings


def _identity_confidence(symbol: str, lane: str, record: dict[str, Any]) -> str:
    if symbol == "GLOBAL_CORE_ETF":
        return "internal_sleeve_placeholder"
    if lane == "etf_fund" and (record.get("isin") or record.get("ISIN")):
        return "high_isin_present"
    if lane in {"crypto", "individual_stock"} and symbol:
        return "medium_symbol_present"
    if lane == "etf_fund" and symbol.endswith(".DE"):
        return "medium_exchange_ticker_present"
    return "partial"


def _record_from_dict(path: Path, record: dict[str, Any], current_date: str, selected: set[str]) -> UniverseCoverageRecord | None:
    symbol = _clean_symbol(_first_value(record, SYMBOL_KEYS))
    if not symbol:
        return None

    # Avoid generic ids like "ready" or "report" becoming fake symbols.
    if symbol in {"READY", "SAFE", "TRUE", "FALSE", "NONE", "NULL", "JSON", "EUR", "USD"}:
        return None

    lane = _infer_lane(path, record, symbol)
    quote_price = _to_float(_first_value(record, QUOTE_KEYS))
    currency_raw = _first_value(record, CURRENCY_KEYS)
    currency = str(currency_raw).upper() if currency_raw else None
    source_raw = _first_value(record, SOURCE_KEYS)
    source = str(source_raw) if source_raw else None
    as_of_raw = _first_value(record, AS_OF_KEYS)
    source_as_of = str(as_of_raw)[:10] if as_of_raw else None

    quote_available = quote_price is not None
    freshness, freshness_warnings = _freshness(source_as_of, quote_available, current_date)

    missing: list[str] = []
    if not quote_available:
        missing.append("quote_price")
    if not currency:
        missing.append("currency")
    if not source:
        missing.append("source")
    if not source_as_of:
        missing.append("source_as_of")

    trusted_quote = quote_available and freshness == "ready" and bool(currency) and bool(source)
    warnings = list(freshness_warnings)
    if symbol == "GLOBAL_CORE_ETF":
        warnings.append("GLOBAL_CORE_ETF appears to be an internal sleeve/placeholder, not a verified tradable instrument.")

    return UniverseCoverageRecord(
        symbol=symbol,
        lane=lane,
        source_file=path.as_posix(),
        selected_now=symbol in selected,
        quote_available=quote_available,
        trusted_quote=trusted_quote,
        quote_price=quote_price,
        currency=currency,
        source=source,
        source_as_of=source_as_of,
        freshness=freshness,
        identity_confidence=_identity_confidence(symbol, lane, record),
        missing_fields=missing,
        warnings=warnings,
    )


def _selected_records_from_finance_core(current_date: str) -> list[UniverseCoverageRecord]:
    try:
        from jarvis.runtime.finance_intelligence_core import build_finance_intelligence_core_result
    except Exception:
        return []

    try:
        result = build_finance_intelligence_core_result(current_date=current_date)
        data = result.to_dict() if hasattr(result, "to_dict") else asdict(result)
    except Exception:
        return []

    source_lists = []
    for key in ("normalized_records", "records", "selected_records"):
        values = data.get(key, []) or []
        if isinstance(values, list):
            source_lists.extend(values)

    records: list[UniverseCoverageRecord] = []
    for raw in source_lists:
        if not isinstance(raw, dict):
            continue

        symbol = _clean_symbol(raw.get("symbol"))
        if not symbol:
            continue

        lane = str(raw.get("lane") or "").strip() or (
            "crypto" if symbol in {"BTC", "ETH"} else
            "individual_stock" if symbol == "MSFT" else
            "etf_fund"
        )

        quote_price = _to_float(raw.get("quote_price") or raw.get("price"))
        currency_raw = raw.get("currency")
        currency = str(currency_raw).upper() if currency_raw else None
        source_raw = raw.get("source") or raw.get("provider")
        source = str(source_raw) if source_raw else None
        source_as_of_raw = raw.get("source_as_of") or raw.get("as_of")
        source_as_of = str(source_as_of_raw)[:10] if source_as_of_raw else None

        quote_available = quote_price is not None
        freshness = str(raw.get("freshness") or "")
        if not freshness:
            freshness, _ = _freshness(source_as_of, quote_available, current_date)

        raw_missing = raw.get("missing_fields") or []
        missing_fields = [str(item) for item in raw_missing if item]
        for required, value in (
            ("quote_price", quote_price),
            ("currency", currency),
            ("source", source),
            ("source_as_of", source_as_of),
        ):
            if value in (None, "") and required not in missing_fields:
                missing_fields.append(required)

        raw_warnings = raw.get("warnings") or []
        warnings = [str(item) for item in raw_warnings if item]

        trusted_raw = raw.get("trusted_quote")
        if trusted_raw is None:
            trusted_quote = quote_available and freshness == "ready" and bool(currency) and bool(source)
        else:
            trusted_quote = bool(trusted_raw)

        records.append(
            UniverseCoverageRecord(
                symbol=symbol,
                lane=lane,
                source_file="finance_intelligence_core",
                selected_now=True,
                quote_available=quote_available,
                trusted_quote=trusted_quote,
                quote_price=quote_price,
                currency=currency,
                source=source,
                source_as_of=source_as_of,
                freshness=freshness,
                identity_confidence=str(raw.get("identity_confidence") or "finance_core_selected_record"),
                missing_fields=missing_fields,
                warnings=warnings,
            )
        )

    return records


def _selected_symbols_from_finance_core(current_date: str) -> set[str]:
    return {record.symbol for record in _selected_records_from_finance_core(current_date)}


def _scan_local_universe(current_date: str, selected: set[str]) -> list[UniverseCoverageRecord]:
    records: list[UniverseCoverageRecord] = []
    seen_paths: set[Path] = set()

    for root in LOCAL_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            if path in seen_paths:
                continue
            seen_paths.add(path)
            path_text = path.as_posix().lower()
            if ".template" in path_text or "example" in path_text:
                continue
            data = _load_json(path)
            if data is None:
                continue
            for item in _iter_dicts(data):
                record = _record_from_dict(path, item, current_date, selected)
                if record is not None:
                    records.append(record)

    # Always include selected symbols even if local scan missed them.
    for symbol in selected:
        if not any(record.symbol == symbol for record in records):
            lane = "crypto" if symbol in {"BTC", "ETH"} else "individual_stock" if symbol == "MSFT" else "etf_fund"
            freshness = "missing_quote"
            records.append(
                UniverseCoverageRecord(
                    symbol=symbol,
                    lane=lane,
                    source_file="finance_intelligence_core_selected_symbols",
                    selected_now=True,
                    quote_available=False,
                    trusted_quote=False,
                    quote_price=None,
                    currency=None,
                    source=None,
                    source_as_of=None,
                    freshness=freshness,
                    identity_confidence="selected_symbol_only",
                    missing_fields=["quote_price", "currency", "source", "source_as_of"],
                    warnings=["selected symbol was not found with complete local quote coverage"],
                )
            )

    return records


def _best_records(records: list[UniverseCoverageRecord]) -> list[UniverseCoverageRecord]:
    def score(record: UniverseCoverageRecord) -> tuple[int, int, int, int, int]:
        return (
            1 if record.selected_now else 0,
            1 if record.trusted_quote else 0,
            1 if record.quote_available else 0,
            1 if record.lane != "unknown" else 0,
            -len(record.missing_fields),
        )

    best: dict[str, UniverseCoverageRecord] = {}
    for record in records:
        existing = best.get(record.symbol)
        if existing is None or score(record) > score(existing):
            best[record.symbol] = record
    return sorted(best.values(), key=lambda r: (r.lane, r.symbol))


def _summaries(records: list[UniverseCoverageRecord]) -> list[LaneCoverageSummary]:
    lanes = sorted({record.lane for record in records})
    summaries: list[LaneCoverageSummary] = []
    for lane in lanes:
        lane_records = [record for record in records if record.lane == lane]
        summaries.append(
            LaneCoverageSummary(
                lane=lane,
                total_symbols=len(lane_records),
                selected_symbols=sum(1 for record in lane_records if record.selected_now),
                quote_available=sum(1 for record in lane_records if record.quote_available),
                trusted_quote=sum(1 for record in lane_records if record.trusted_quote),
                missing_quote=sum(1 for record in lane_records if not record.quote_available),
                stale_or_untrusted=sum(1 for record in lane_records if record.quote_available and not record.trusted_quote),
                future_dated=sum(1 for record in lane_records if record.freshness == "quarantined_future_date"),
            )
        )
    return summaries


def build_public_universe_data_coverage_result(
    *,
    current_date: str = "2026-06-18",
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> PublicUniverseDataCoverageResult:
    selected_core_records = _selected_records_from_finance_core(current_date)
    selected = {record.symbol for record in selected_core_records} or _selected_symbols_from_finance_core(current_date)
    records = _best_records(_scan_local_universe(current_date, selected) + selected_core_records)
    summaries = _summaries(records)

    missing_quote = sorted(record.symbol for record in records if not record.quote_available)
    future_dated = sorted(record.symbol for record in records if record.freshness == "quarantined_future_date")
    untrusted = sorted(record.symbol for record in records if not record.trusted_quote)

    priority = []
    for symbol in ["GLOBAL_CORE_ETF", "VWCE", "IS3Q.DE"]:
        if symbol in untrusted or symbol in missing_quote or symbol in future_dated:
            priority.append(symbol)
    for lane in ["etf_fund", "individual_stock", "crypto"]:
        lane_missing = [record.symbol for record in records if record.lane == lane and not record.trusted_quote and record.symbol not in priority]
        priority.extend(lane_missing[:15])

    result = PublicUniverseDataCoverageResult(
        status=STATUS_READY,
        current_date=current_date,
        total_records=len(records),
        total_symbols=len({record.symbol for record in records}),
        selected_symbols=sorted(selected),
        lane_summaries=[summary.to_dict() for summary in summaries],
        records=[record.to_dict() for record in records],
        missing_quote_symbols=missing_quote,
        future_dated_symbols=future_dated,
        untrusted_symbols=untrusted,
        next_fetch_priority=priority[:30],
        report_written=bool(write_report),
        report_path=str(output_path),
        execution_forbidden=True,
        broker_connection=False,
        credentials_used=False,
        order_created=False,
        trade_executed=False,
        auto_approval_enabled=False,
        warnings=[
            "coverage engine is read-only",
            "this scans J.A.R.V.I.S. local investable universe, not every ETF/stock in the world",
            "missing or untrusted symbols must be fetched/verified before assistant recommendations treat them as quote-ready",
        ],
    )

    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return result


def format_public_universe_data_coverage(result: PublicUniverseDataCoverageResult) -> str:
    lines = [
        "J.A.R.V.I.S. PUBLIC UNIVERSE DATA COVERAGE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"total symbols: {result.total_symbols}",
        f"selected symbols: {', '.join(result.selected_symbols) if result.selected_symbols else 'none detected'}",
        "",
        "LANE COVERAGE:",
    ]
    for summary in result.lane_summaries:
        lines.append(
            f"- {summary['lane']}: total={summary['total_symbols']}; selected={summary['selected_symbols']}; "
            f"quote_available={summary['quote_available']}; trusted_quote={summary['trusted_quote']}; "
            f"missing_quote={summary['missing_quote']}; stale_or_untrusted={summary['stale_or_untrusted']}; "
            f"future_dated={summary['future_dated']}"
        )

    lines.extend(
        [
            "",
            "NEXT FETCH PRIORITY:",
            *[f"- {symbol}" for symbol in result.next_fetch_priority[:30]],
            "",
            "SELECTED SYMBOL DETAILS:",
        ]
    )
    selected = set(result.selected_symbols)
    for record in result.records:
        if record["symbol"] in selected:
            lines.append(
                f"- {record['symbol']}: lane={record['lane']}; quote={record['quote_available']}; "
                f"trusted={record['trusted_quote']}; freshness={record['freshness']}; "
                f"missing={','.join(record['missing_fields']) if record['missing_fields'] else 'none'}"
            )

    lines.extend(
        [
            "",
            "SAFETY:",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            f"- auto approval enabled: {result.auto_approval_enabled}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_public_universe_data_coverage_result(
        current_date=args.current_date,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_public_universe_data_coverage(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
