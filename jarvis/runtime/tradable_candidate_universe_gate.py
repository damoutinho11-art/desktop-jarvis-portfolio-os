"""J.A.R.V.I.S. v84.0 tradable candidate universe breadth gate.

Checks if the available candidate universe is broad enough before any dynamic
allocator is allowed. No fetching, broker, credentials, orders, or trades.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.data_freshness_acquisition_gate import build_data_freshness_acquisition_gate_result
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V84_0_TRADABLE_CANDIDATE_UNIVERSE_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V84_0_TRADABLE_CANDIDATE_UNIVERSE_GATE_REVIEW_REQUIRED_SAFE"

MIN_CRYPTO = 5
MIN_ETF = 3
MIN_STOCK = 5

DEFAULT_PATHS = [
    "outputs/approval_ticket_latest.json",
    "outputs/free_research_evidence_pack_latest.json",
    "jarvis/local/free_research_api_cache.local.json",
    "jarvis/local/crypto_universe.local.json",
    "jarvis/local/individual_stock_ranked_candidates.local.json",
    "jarvis/local/individual_stock_signals.local.json",
    "jarvis/local/lightyear_instrument_universe.local.json",
]


@dataclass(frozen=True)
class TradableCandidateUniverseGateResult:
    status: str
    current_date: str
    universe_gate_ready: bool
    dynamic_allocator_allowed: bool
    crypto_candidate_count: int
    etf_candidate_count: int
    stock_candidate_count: int
    crypto_candidates: list[str]
    etf_candidates: list[str]
    stock_candidates: list[str]
    missing_breadth: list[str]
    missing_freshness: list[str]
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


def _load(path: str) -> Any | None:
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _walk(value: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, Mapping):
        rows.append(dict(value))
        for child in value.values():
            rows.extend(_walk(child))
    elif isinstance(value, list):
        for child in value:
            rows.extend(_walk(child))
    return rows


def _txt(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str).lower()


def _dedupe(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        clean = item.strip().upper()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return out


def _candidates(rows: list[dict[str, Any]], lane: str) -> list[str]:
    crypto_known = [
        "BTC", "ETH", "SOL", "HYPE", "LINK", "AVAX", "NEAR", "INJ", "RENDER", "TAO",
        "BNB", "XRP", "ADA", "DOT", "TON", "ARB", "OP", "AAVE", "UNI",
    ]

    etf_known = [
        "QUALITY_ETF", "GROWTH_NASDAQ_ETF", "GLOBAL_CORE_ETF", "SP500_CORE_ETF", "TECHNOLOGY_TILT_ETF",
        "IS3Q.DE", "IS3Q", "SXR8", "SXR8:XETRA", "VWCE", "VWCE:XETRA",
        "QDVE", "QDVE:XETRA", "IWDA", "SWDA", "IEMM", "EMIM", "EIMI",
    ]

    stock_known = [
        "MSFT", "META", "AAPL", "NVDA", "GOOGL", "AMZN", "TSLA", "AVGO", "ASML", "AMD",
    ]

    known = {
        "crypto": crypto_known,
        "etf": etf_known,
        "stock": stock_known,
    }[lane]

    found: list[str] = []
    for row in rows:
        text = _txt(row)
        for token in known:
            if token.lower() in text:
                found.append(token)

    return _dedupe(found)

def build_tradable_candidate_universe_gate_result(current_date: str = "2026-06-18") -> TradableCandidateUniverseGateResult:
    rows: list[dict[str, Any]] = []
    for path in DEFAULT_PATHS:
        rows.extend(_walk(_load(path)))

    crypto = _candidates(rows, "crypto")
    etf = _candidates(rows, "etf")
    stock = _candidates(rows, "stock")

    freshness = build_data_freshness_acquisition_gate_result(current_date=current_date)

    missing_breadth: list[str] = []
    if len(crypto) < MIN_CRYPTO:
        missing_breadth.append(f"crypto_candidates_{len(crypto)}_of_{MIN_CRYPTO}")
    if len(etf) < MIN_ETF:
        missing_breadth.append(f"etf_candidates_{len(etf)}_of_{MIN_ETF}")
    if len(stock) < MIN_STOCK:
        missing_breadth.append(f"stock_candidates_{len(stock)}_of_{MIN_STOCK}")

    safety = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety and "No execution action was taken" in safety

    blockers = missing_breadth + list(freshness.missing_freshness)
    if not safety_blocked:
        blockers.append("safety_check_did_not_block_execution")

    ready = not blockers

    return TradableCandidateUniverseGateResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        universe_gate_ready=ready,
        dynamic_allocator_allowed=ready,
        crypto_candidate_count=len(crypto),
        etf_candidate_count=len(etf),
        stock_candidate_count=len(stock),
        crypto_candidates=crypto,
        etf_candidates=etf,
        stock_candidates=stock,
        missing_breadth=missing_breadth,
        missing_freshness=list(freshness.missing_freshness),
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


def format_result(result: TradableCandidateUniverseGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. TRADABLE CANDIDATE UNIVERSE GATE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"universe gate ready: {result.universe_gate_ready}",
        f"dynamic allocator allowed: {result.dynamic_allocator_allowed}",
        f"crypto candidates: {result.crypto_candidate_count} / {MIN_CRYPTO} -> {', '.join(result.crypto_candidates) or 'none'}",
        f"ETF/fund candidates: {result.etf_candidate_count} / {MIN_ETF} -> {', '.join(result.etf_candidates) or 'none'}",
        f"stock candidates: {result.stock_candidate_count} / {MIN_STOCK} -> {', '.join(result.stock_candidates) or 'none'}",
        "missing breadth:",
    ]
    lines.extend(f"- {x}" for x in result.missing_breadth or ["none"])
    lines.append("missing freshness:")
    lines.extend(f"- {x}" for x in result.missing_freshness or ["none"])
    lines.append("blockers:")
    lines.extend(f"- {x}" for x in result.blockers or ["none"])
    lines.extend([
        "Safety:",
        f"- safety-check blocked execution: {result.safety_check_blocked_execution}",
        f"- buy request created: {result.buy_request_created}",
        f"- order created: {result.order_created}",
        f"- trade executed: {result.trade_executed}",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tradable-candidate-universe-gate", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    args = parser.parse_args(argv)
    result = build_tradable_candidate_universe_gate_result(current_date=args.current_date)
    print(format_result(result))
    return 0 if not result.blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
