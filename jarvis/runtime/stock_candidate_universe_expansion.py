from __future__ import annotations

import argparse
import json
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V85_0_STOCK_CANDIDATE_UNIVERSE_EXPANSION_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V85_0_STOCK_CANDIDATE_UNIVERSE_EXPANSION_REVIEW_REQUIRED_SAFE"

DEFAULT_OUTPUT_PATH = "jarvis/local/individual_stock_ranked_candidates.local.json"
DEFAULT_SYMBOLS = ['MSFT', 'META', 'AAPL', 'NVDA', 'GOOGL', 'AMZN', 'AVGO', 'ASML', 'AMD', 'JPM', 'V', 'MA', 'UNH', 'LLY', 'JNJ', 'COST', 'HD', 'PG', 'KO', 'PEP', 'XOM', 'CVX', 'CAT', 'CRM', 'NFLX']

NAMES = {'MSFT': 'Microsoft Corporation', 'META': 'Meta Platforms Inc.', 'AAPL': 'Apple Inc.', 'NVDA': 'NVIDIA Corporation', 'GOOGL': 'Alphabet Inc.', 'AMZN': 'Amazon.com Inc.', 'AVGO': 'Broadcom Inc.', 'ASML': 'ASML Holding N.V.', 'AMD': 'Advanced Micro Devices Inc.', 'JPM': 'JPMorgan Chase & Co.', 'V': 'Visa Inc.', 'MA': 'Mastercard Inc.', 'UNH': 'UnitedHealth Group Inc.', 'LLY': 'Eli Lilly and Company', 'JNJ': 'Johnson & Johnson', 'COST': 'Costco Wholesale Corporation', 'HD': 'The Home Depot Inc.', 'PG': 'Procter & Gamble Co.', 'KO': 'The Coca-Cola Company', 'PEP': 'PepsiCo Inc.', 'XOM': 'Exxon Mobil Corporation', 'CVX': 'Chevron Corporation', 'CAT': 'Caterpillar Inc.', 'CRM': 'Salesforce Inc.', 'NFLX': 'Netflix Inc.'}


@dataclass(frozen=True)
class StockCandidateUniverseExpansionResult:
    status: str
    current_date: str
    stock_universe_ready: bool
    candidate_count: int
    fresh_candidate_count: int
    min_required_candidates: int
    output_written: bool
    output_path: str
    candidates: list[dict[str, Any]]
    warnings: list[str]
    blockers: list[str]
    safety_check_blocked_execution: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def fetch_yahoo_chart_quote(symbol: str) -> dict[str, Any] | None:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range=5d&interval=1d&includeAdjustedClose=true"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 JARVIS"})

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        result = payload["chart"]["result"][0]
        meta = result.get("meta", {})
        timestamps = result.get("timestamp", [])
        closes = result["indicators"]["quote"][0].get("close", [])
    except Exception:
        return None

    valid = [
        (ts, close)
        for ts, close in zip(timestamps, closes)
        if ts is not None and close is not None and float(close) > 0
    ]
    if not valid:
        return None

    ts, close = valid[-1]
    as_of = datetime.fromtimestamp(int(ts), tz=timezone.utc).date().isoformat()

    return {
        "symbol": symbol,
        "name": NAMES.get(symbol, symbol),
        "close_price": round(float(close), 4),
        "currency": meta.get("currency") or "USD",
        "as_of": as_of,
        "source": "yahoo_chart_public",
        "asset_type": "stock",
        "public_source_ready": True,
        "approved_for_purchase": False,
        "buy_request_created": False,
        "order_created": False,
        "trade_executed": False,
    }


def build_stock_candidate_universe_expansion_result(
    current_date: str = "2026-06-18",
    symbols: list[str] | None = None,
    min_required_candidates: int = 15,
    write_candidates: bool = False,
    output_path: str = DEFAULT_OUTPUT_PATH,
) -> StockCandidateUniverseExpansionResult:
    symbols = symbols or DEFAULT_SYMBOLS
    candidates: list[dict[str, Any]] = []
    warnings: list[str] = []

    for symbol in symbols:
        quote = fetch_yahoo_chart_quote(symbol.upper())
        if quote is None:
            warnings.append(f"public quote fetch failed for {symbol.upper()}")
        else:
            candidates.append(quote)

    fresh_count = sum(1 for c in candidates if c.get("symbol") and c.get("close_price") and c.get("as_of"))

    safety = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety and "No execution action was taken" in safety

    blockers: list[str] = []
    if fresh_count < min_required_candidates:
        blockers.append(f"fresh_stock_candidates_{fresh_count}_of_{min_required_candidates}")
    if not safety_blocked:
        blockers.append("safety_check_did_not_block_execution")

    output_written = False
    if write_candidates:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "current_date": current_date,
                    "source": "yahoo_chart_public",
                    "ranked_candidates": candidates,
                    "policy": {
                        "manual_review_only": True,
                        "approved_for_purchase": False,
                        "buy_request_created": False,
                        "order_created": False,
                        "trade_executed": False,
                    },
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        output_written = True

    ready = not blockers

    return StockCandidateUniverseExpansionResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        stock_universe_ready=ready,
        candidate_count=len(candidates),
        fresh_candidate_count=fresh_count,
        min_required_candidates=min_required_candidates,
        output_written=output_written,
        output_path=output_path,
        candidates=candidates,
        warnings=warnings,
        blockers=blockers,
        safety_check_blocked_execution=safety_blocked,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection=False,
        credentials_used=False,
        order_created=False,
        trade_executed=False,
    )


def format_result(result: StockCandidateUniverseExpansionResult) -> str:
    lines = [
        "J.A.R.V.I.S. STOCK CANDIDATE UNIVERSE EXPANSION",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"stock universe ready: {result.stock_universe_ready}",
        f"fresh candidates: {result.fresh_candidate_count} / {result.min_required_candidates}",
        f"output written: {result.output_written}",
        f"output path: {result.output_path}",
        "candidates:",
    ]
    for c in result.candidates:
        lines.append(f"- {c['symbol']}: {c['name']}; price={c['close_price']} {c['currency']}; as_of={c['as_of']}; source={c['source']}")
    lines.append("warnings:")
    lines.extend(f"- {w}" for w in result.warnings or ["none"])
    lines.append("blockers:")
    lines.extend(f"- {b}" for b in result.blockers or ["none"])
    lines.extend([
        "Safety:",
        f"- safety-check blocked execution: {result.safety_check_blocked_execution}",
        f"- buy request created: {result.buy_request_created}",
        f"- broker connection: {result.broker_connection}",
        f"- order created: {result.order_created}",
        f"- trade executed: {result.trade_executed}",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stock-candidate-universe-expansion", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--symbols", nargs="*", default=None)
    parser.add_argument("--min-required-candidates", type=int, default=15)
    parser.add_argument("--write-candidates", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_stock_candidate_universe_expansion_result(
        current_date=args.current_date,
        symbols=args.symbols,
        min_required_candidates=args.min_required_candidates,
        write_candidates=args.write_candidates,
        output_path=args.output_path,
    )
    print(format_result(result))
    return 0 if not result.blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
