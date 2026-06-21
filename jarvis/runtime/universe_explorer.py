"""J.A.R.V.I.S. v159.0 safe universe explorer and search."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.finance_database_universe import build_finance_database_universe_result

STATUS_READY = "JARVIS_V159_0_UNIVERSE_EXPLORER_AI_SEARCH_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/universe_explorer_latest.json"

DEFAULT_FIXTURE_UNIVERSE: dict[str, Any] = {
    "equities": [
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "asset_type": "equity",
            "exchange": "NASDAQ",
            "country": "United States",
            "currency": "USD",
            "sector": "Software Technology Quality Large Cap",
            "source": "JARVIS fixture universe",
        },
        {
            "symbol": "ASML",
            "name": "ASML Holding N.V.",
            "asset_type": "equity",
            "exchange": "Euronext Amsterdam",
            "country": "Netherlands",
            "currency": "EUR",
            "sector": "Semiconductor Technology Quality Large Cap",
            "source": "JARVIS fixture universe",
        },
    ],
    "etfs_funds": [
        {
            "symbol": "VWCE",
            "name": "Vanguard FTSE All-World UCITS ETF Accumulating",
            "asset_type": "fund",
            "exchange": "XETRA",
            "country": "Ireland",
            "currency": "EUR",
            "category": "Global equity ETF accumulating",
            "source": "JARVIS fixture universe",
        },
        {
            "symbol": "IS3Q.DE",
            "name": "iShares Edge MSCI World Quality Factor UCITS ETF",
            "asset_type": "fund",
            "exchange": "XETRA",
            "country": "Ireland",
            "currency": "EUR",
            "category": "Quality global equity ETF accumulating",
            "source": "JARVIS fixture universe",
        },
        {
            "symbol": "EUNL.DE",
            "name": "iShares Core MSCI World UCITS ETF Accumulating",
            "asset_type": "fund",
            "exchange": "XETRA",
            "country": "Ireland",
            "currency": "EUR",
            "category": "Global equity ETF accumulating",
            "source": "JARVIS fixture universe",
        },
    ],
    "indices": [
        {"symbol": "SPX", "name": "S&P 500", "asset_type": "index", "exchange": "CBOE", "country": "United States", "currency": "USD", "category": "large cap index", "source": "JARVIS fixture universe"}
    ],
    "currencies": [
        {"symbol": "EUR", "name": "Euro", "asset_type": "currency", "country": "Euro Area", "currency": "EUR", "category": "currency", "source": "JARVIS fixture universe"}
    ],
    "crypto": [
        {"symbol": "BTC", "name": "Bitcoin", "asset_type": "crypto", "currency": "USD", "category": "digital asset", "source": "JARVIS fixture universe"}
    ],
}

ASSET_ALIASES = {
    "stock": "equity",
    "stocks": "equity",
    "equity": "equity",
    "equities": "equity",
    "etf": "fund",
    "etfs": "fund",
    "fund": "fund",
    "funds": "fund",
    "index": "index",
    "indices": "index",
    "currency": "currency",
    "currencies": "currency",
    "crypto": "crypto",
}


@dataclass(frozen=True)
class UniverseExplorerResult:
    status: str
    query: str
    filters: dict[str, Any]
    candidate_count: int
    top_candidates: list[dict[str, Any]]
    missing_data_notes: list[str]
    manual_review_required: bool
    source: str
    blockers: list[str]
    warnings: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _norm(value: Any) -> str:
    return str(value or "").strip().lower()


def _tokens(text: str) -> list[str]:
    return [token for token in re.split(r"[^a-zA-Z0-9.]+", text.lower()) if token]


def _asset_filter(value: Any) -> str | None:
    text = _norm(value)
    return ASSET_ALIASES.get(text, text or None)


def parse_universe_query(query: str) -> dict[str, Any]:
    normalized = _norm(query)
    filters: dict[str, Any] = {"keywords": []}
    for token in _tokens(normalized):
        asset_type = _asset_filter(token)
        if asset_type in {"equity", "fund", "index", "currency", "crypto"}:
            filters["asset_type"] = asset_type

    if "eur-denominated" in normalized or "eur denominated" in normalized or " in eur" in normalized:
        filters["currency"] = "EUR"
    elif "usd-denominated" in normalized or "usd denominated" in normalized or " in usd" in normalized:
        filters["currency"] = "USD"

    if "european" in normalized or "europe" in normalized:
        filters["country"] = ["Ireland", "Germany", "Netherlands", "France", "Luxembourg", "Euro Area"]
    if "xetra" in normalized:
        filters["exchange"] = "XETRA"
    if "nasdaq" in normalized:
        filters["exchange"] = "NASDAQ"
    if "similar to msft" in normalized or "like msft" in normalized:
        filters["asset_type"] = "equity"
        filters["sector_category"] = "software technology quality large cap"
        filters.setdefault("exclude_symbols", []).append("MSFT")
    for keyword in ("global", "quality", "software", "technology", "large", "large-cap", "accumulating", "acc"):
        if keyword in normalized:
            filters["keywords"].append(keyword.replace("large-cap", "large"))
    return filters


def _record_text(record: Mapping[str, Any]) -> str:
    return " ".join(str(record.get(key) or "") for key in ("symbol", "name", "asset_type", "exchange", "country", "currency", "sector_category", "source")).lower()


def _matches_text(expected: Any, actual: Any) -> bool:
    if expected in (None, "", [], {}):
        return True
    actual_text = _norm(actual)
    if isinstance(expected, list):
        return any(_norm(item) in actual_text for item in expected)
    return _norm(expected) in actual_text


def _matches_asset_type(expected: Any, actual: Any) -> bool:
    expected_text = _asset_filter(expected)
    actual_text = _asset_filter(actual)
    if expected_text == "fund" and actual_text in {"fund", "etf", "etf_fund"}:
        return True
    return expected_text == actual_text


def _candidate_score(record: Mapping[str, Any], filters: Mapping[str, Any]) -> tuple[bool, int, list[str], list[str]]:
    why: list[str] = []
    missing: list[str] = []
    score = 0
    if filters.get("asset_type"):
        if not record.get("asset_type"):
            missing.append("asset_type missing")
        elif _matches_asset_type(filters.get("asset_type"), record.get("asset_type")):
            why.append(f"asset_type matched {filters.get('asset_type')}")
            score += 3
        else:
            return False, 0, why, missing
    for key in ("country", "exchange", "currency", "sector_category"):
        if filters.get(key):
            if not record.get(key):
                missing.append(f"{key} missing")
            elif _matches_text(filters.get(key), record.get(key)):
                why.append(f"{key} matched")
                score += 2
            elif key in {"currency", "exchange"}:
                return False, 0, why, missing
    text = _record_text(record)
    for keyword in filters.get("keywords", []) or []:
        if keyword in text:
            why.append(f"keyword matched {keyword}")
            score += 1
    exclude = {str(item).upper() for item in filters.get("exclude_symbols", []) or []}
    if str(record.get("symbol") or "").upper() in exclude:
        return False, 0, why, missing
    if not filters.get("keywords") and not why:
        why.append("included from available universe metadata")
    return True, score, why, missing


def _load_universe(fixture_universe: Mapping[str, Any] | None) -> tuple[list[dict[str, Any]], str, list[str]]:
    result = build_finance_database_universe_result(fixture_universe=fixture_universe)
    source = "FinanceDatabase" if result.dependency_available and result.universe_ready and fixture_universe is None else "local_fixture_universe"
    warnings = list(result.warnings or [])
    if not result.sample_instruments:
        fallback = build_finance_database_universe_result(fixture_universe=DEFAULT_FIXTURE_UNIVERSE)
        return list(fallback.sample_instruments), "local_fixture_universe", warnings + ["FinanceDatabase universe unavailable; local fixture metadata used"]
    return list(result.sample_instruments), source, warnings


def build_universe_explorer_result(
    *,
    query: str = "find European accumulating global ETFs",
    filters: Mapping[str, Any] | None = None,
    fixture_universe: Mapping[str, Any] | None = None,
    max_candidates: int = 10,
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> UniverseExplorerResult:
    parsed = parse_universe_query(query)
    if filters:
        parsed.update({key: value for key, value in filters.items() if value not in (None, "", [], {})})
    records, source, warnings = _load_universe(fixture_universe)
    candidates: list[dict[str, Any]] = []
    missing_notes: list[str] = []
    for record in records:
        matched, score, why, missing = _candidate_score(record, parsed)
        if not matched:
            continue
        candidate = dict(record)
        candidate["why_matched"] = why
        candidate["match_score"] = score
        candidates.append(candidate)
        missing_notes.extend(f"{record.get('symbol')}: {item}" for item in missing)
    candidates.sort(key=lambda item: (-int(item.get("match_score") or 0), str(item.get("symbol") or "")))
    result = UniverseExplorerResult(
        status=STATUS_READY,
        query=query,
        filters=dict(parsed),
        candidate_count=len(candidates),
        top_candidates=candidates[:max_candidates],
        missing_data_notes=list(dict.fromkeys(missing_notes)),
        manual_review_required=True,
        source=source,
        blockers=[],
        warnings=list(dict.fromkeys(warnings + ["universe explorer is metadata search for manual review"])),
        report_written=bool(write_report),
        report_path=str(output_path),
    )
    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def format_universe_explorer(result: UniverseExplorerResult) -> str:
    lines = [
        "J.A.R.V.I.S. Universe Explorer",
        f"status: {result.status}",
        f"query: {result.query}",
        f"source: {result.source}",
        f"candidate count: {result.candidate_count}",
        f"manual review required: {result.manual_review_required}",
        "",
        "FILTERS:",
    ]
    for key, value in result.filters.items():
        if value not in (None, "", [], {}):
            lines.append(f"- {key}: {value}")
    lines.extend(["", "TOP CANDIDATES:"])
    for item in result.top_candidates:
        lines.append(
            f"- {item.get('symbol')}: {item.get('name')}; type={item.get('asset_type')}; "
            f"exchange={item.get('exchange') or 'n/a'}; country={item.get('country') or 'n/a'}; "
            f"currency={item.get('currency') or 'n/a'}; why={'; '.join(item.get('why_matched') or [])}"
        )
    if not result.top_candidates:
        lines.append("- none")
    lines.extend(["", "MISSING DATA NOTES:"])
    lines.extend(f"- {item}" for item in result.missing_data_notes or ["none"])
    lines.extend(["", "WARNINGS:"])
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.extend(["", "BLOCKERS:"])
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search the read-only J.A.R.V.I.S. universe metadata.")
    parser.add_argument("--universe-explorer", action="store_true")
    parser.add_argument("--query", default="find European accumulating global ETFs")
    parser.add_argument("--asset-type", default=None)
    parser.add_argument("--country", default=None)
    parser.add_argument("--exchange", default=None)
    parser.add_argument("--currency", default=None)
    parser.add_argument("--sector-category", default=None)
    parser.add_argument("--keyword", default=None)
    parser.add_argument("--max-candidates", type=int, default=10)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)
    explicit_filters = {
        "asset_type": args.asset_type,
        "country": args.country,
        "exchange": args.exchange,
        "currency": args.currency,
        "sector_category": args.sector_category,
        "keywords": [args.keyword] if args.keyword else [],
    }
    result = build_universe_explorer_result(
        query=args.query,
        filters=explicit_filters,
        max_candidates=args.max_candidates,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_universe_explorer(result))
    return 0


__all__ = [
    "STATUS_READY",
    "DEFAULT_FIXTURE_UNIVERSE",
    "UniverseExplorerResult",
    "parse_universe_query",
    "build_universe_explorer_result",
    "format_universe_explorer",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())

