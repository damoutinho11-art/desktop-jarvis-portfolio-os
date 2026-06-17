"""J.A.R.V.I.S. v40.0 individual stock public universe bootstrap.

v40 gives the v39 stock ranker something real to rank without committing any
local/private state.

It can write a local public stock starter universe under jarvis/local, then run
v39 over that universe. The starter universe is a bootstrap list, not a buy list,
not an approval, and not a recommendation.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from .jarvis_v38_0_individual_stock_public_universe_engine import (
    DEFAULT_STOCK_SIGNALS_PATH,
    DEFAULT_STOCK_UNIVERSE_PATH,
)
from .jarvis_v39_0_individual_stock_public_ranker import (
    DEFAULT_RANKED_STOCKS_PATH,
    IndividualStockPublicRankerResult,
    build_individual_stock_public_ranker_result,
    format_individual_stock_public_ranker,
)

STATUS_READY = "JARVIS_V40_0_INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_BOOTSTRAP_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V40_0_INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_BOOTSTRAP_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V40_0_INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_BOOTSTRAP_BLOCKED_SAFE"

BOOTSTRAP_READY = "INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_BOOTSTRAP_READY"
BOOTSTRAP_REVIEW_REQUIRED = "INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_BOOTSTRAP_REVIEW_REQUIRED"
BOOTSTRAP_BLOCKED = "INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_BOOTSTRAP_BLOCKED"

NEXT_STAGE = "individual_stock_ranked_candidate_ticket_bridge"

DEFAULT_BOOTSTRAP_STYLE = "quality_large_cap_public_watchlist"


STARTER_STOCK_UNIVERSE: tuple[dict[str, Any], ...] = (
    {
        "stock_id": "apple_aapl_us",
        "name": "Apple Inc.",
        "ticker": "AAPL",
        "exchange": "NASDAQ",
        "market": "USA",
        "sector": "Technology",
        "currency": "USD",
        "provider": "yahoo_chart",
        "symbol": "AAPL",
        "source_url": "https://query1.finance.yahoo.com/v8/finance/chart/AAPL?range=5d&interval=1d",
        "priority_score": 76.0,
    },
    {
        "stock_id": "microsoft_msft_us",
        "name": "Microsoft Corporation",
        "ticker": "MSFT",
        "exchange": "NASDAQ",
        "market": "USA",
        "sector": "Technology",
        "currency": "USD",
        "provider": "yahoo_chart",
        "symbol": "MSFT",
        "source_url": "https://query1.finance.yahoo.com/v8/finance/chart/MSFT?range=5d&interval=1d",
        "priority_score": 78.0,
    },
    {
        "stock_id": "nvidia_nvda_us",
        "name": "NVIDIA Corporation",
        "ticker": "NVDA",
        "exchange": "NASDAQ",
        "market": "USA",
        "sector": "Semiconductors",
        "currency": "USD",
        "provider": "yahoo_chart",
        "symbol": "NVDA",
        "source_url": "https://query1.finance.yahoo.com/v8/finance/chart/NVDA?range=5d&interval=1d",
        "priority_score": 72.0,
    },
    {
        "stock_id": "alphabet_googl_us",
        "name": "Alphabet Inc. Class A",
        "ticker": "GOOGL",
        "exchange": "NASDAQ",
        "market": "USA",
        "sector": "Communication Services",
        "currency": "USD",
        "provider": "yahoo_chart",
        "symbol": "GOOGL",
        "source_url": "https://query1.finance.yahoo.com/v8/finance/chart/GOOGL?range=5d&interval=1d",
        "priority_score": 70.0,
    },
    {
        "stock_id": "amazon_amzn_us",
        "name": "Amazon.com Inc.",
        "ticker": "AMZN",
        "exchange": "NASDAQ",
        "market": "USA",
        "sector": "Consumer Discretionary",
        "currency": "USD",
        "provider": "yahoo_chart",
        "symbol": "AMZN",
        "source_url": "https://query1.finance.yahoo.com/v8/finance/chart/AMZN?range=5d&interval=1d",
        "priority_score": 68.0,
    },
    {
        "stock_id": "meta_meta_us",
        "name": "Meta Platforms Inc.",
        "ticker": "META",
        "exchange": "NASDAQ",
        "market": "USA",
        "sector": "Communication Services",
        "currency": "USD",
        "provider": "yahoo_chart",
        "symbol": "META",
        "source_url": "https://query1.finance.yahoo.com/v8/finance/chart/META?range=5d&interval=1d",
        "priority_score": 66.0,
    },
    {
        "stock_id": "johnson_jnj_us",
        "name": "Johnson & Johnson",
        "ticker": "JNJ",
        "exchange": "NYSE",
        "market": "USA",
        "sector": "Healthcare",
        "currency": "USD",
        "provider": "yahoo_chart",
        "symbol": "JNJ",
        "source_url": "https://query1.finance.yahoo.com/v8/finance/chart/JNJ?range=5d&interval=1d",
        "priority_score": 62.0,
    },
    {
        "stock_id": "procter_gamble_pg_us",
        "name": "Procter & Gamble Company",
        "ticker": "PG",
        "exchange": "NYSE",
        "market": "USA",
        "sector": "Consumer Staples",
        "currency": "USD",
        "provider": "yahoo_chart",
        "symbol": "PG",
        "source_url": "https://query1.finance.yahoo.com/v8/finance/chart/PG?range=5d&interval=1d",
        "priority_score": 60.0,
    },
    {
        "stock_id": "coca_cola_ko_us",
        "name": "The Coca-Cola Company",
        "ticker": "KO",
        "exchange": "NYSE",
        "market": "USA",
        "sector": "Consumer Staples",
        "currency": "USD",
        "provider": "yahoo_chart",
        "symbol": "KO",
        "source_url": "https://query1.finance.yahoo.com/v8/finance/chart/KO?range=5d&interval=1d",
        "priority_score": 58.0,
    },
    {
        "stock_id": "costco_cost_us",
        "name": "Costco Wholesale Corporation",
        "ticker": "COST",
        "exchange": "NASDAQ",
        "market": "USA",
        "sector": "Consumer Staples",
        "currency": "USD",
        "provider": "yahoo_chart",
        "symbol": "COST",
        "source_url": "https://query1.finance.yahoo.com/v8/finance/chart/COST?range=5d&interval=1d",
        "priority_score": 64.0,
    },
)


@dataclass(frozen=True)
class IndividualStockPublicUniverseBootstrapResult:
    status: str
    bootstrap_status: str
    recommended_next_stage: str
    current_date: str
    stock_universe_path: str
    stock_signals_path: str
    ranked_stocks_path: str
    bootstrap_style: str
    bootstrap_stock_count: int
    bootstrap_universe_written: bool
    stock_signals_written: bool
    ranked_stocks_written: bool
    upstream_ranker_result: Any
    ranked_candidate_count: int
    top_ranked_stock_id: str | None
    top_ranked_symbol: str | None
    recommendation_quality_current_data: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    portfolio_state_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    final_user_buy_action_required: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "bootstrap_status": self.bootstrap_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "stock_universe_path": self.stock_universe_path,
            "stock_signals_path": self.stock_signals_path,
            "ranked_stocks_path": self.ranked_stocks_path,
            "bootstrap_style": self.bootstrap_style,
            "bootstrap_stock_count": self.bootstrap_stock_count,
            "bootstrap_universe_written": self.bootstrap_universe_written,
            "stock_signals_written": self.stock_signals_written,
            "ranked_stocks_written": self.ranked_stocks_written,
            "upstream_ranker_result": self.upstream_ranker_result.to_dict()
            if hasattr(self.upstream_ranker_result, "to_dict")
            else dict(getattr(self.upstream_ranker_result, "__dict__", {})),
            "ranked_candidate_count": self.ranked_candidate_count,
            "top_ranked_stock_id": self.top_ranked_stock_id,
            "top_ranked_symbol": self.top_ranked_symbol,
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "portfolio_state_mutation": self.portfolio_state_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def _today_iso() -> str:
    return date.today().isoformat()


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    text = str(value).strip()
    if len(text) >= 10:
        text = text[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _resolve_path(path: str | Path, root: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return Path(root) / candidate


def _is_under(path: Path, root: str | Path, child: str) -> bool:
    resolved = path.resolve()
    allowed_root = (Path(root) / child).resolve()
    try:
        resolved.relative_to(allowed_root)
        return True
    except ValueError:
        return False


def _dedupe(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_bootstrap_stock_universe_payload(*, current_date: str, bootstrap_style: str = DEFAULT_BOOTSTRAP_STYLE) -> dict[str, Any]:
    return {
        "version": 1,
        "generated_at": current_date,
        "bootstrap_style": bootstrap_style,
        "decision_status": "PUBLIC_STOCK_UNIVERSE_BOOTSTRAP_NOT_APPROVED_NOT_A_BUY_LIST",
        "purpose": "Starter public stock universe for quote fetching/ranking only. Local file; do not commit.",
        "supported_providers": ["yahoo_chart"],
        "safety": {
            "allocation_mutation": False,
            "approval_ticket_mutation": False,
            "portfolio_state_mutation": False,
            "buy_request_created": False,
            "broker_connection": False,
            "credentials_used": False,
            "private_account_data_ingested": False,
            "orders_created": False,
            "trades_executed": False,
        },
        "stocks": [dict(stock) for stock in STARTER_STOCK_UNIVERSE],
    }


def write_bootstrap_stock_universe(
    *,
    path: str | Path = DEFAULT_STOCK_UNIVERSE_PATH,
    root: str | Path = ".",
    current_date: str,
    bootstrap_style: str = DEFAULT_BOOTSTRAP_STYLE,
) -> Path:
    resolved = _resolve_path(path, root)
    if not _is_under(resolved, root, "jarvis/local"):
        raise ValueError("stock universe bootstrap path must remain under jarvis/local/.")
    _write_json(resolved, build_bootstrap_stock_universe_payload(current_date=current_date, bootstrap_style=bootstrap_style))
    return resolved


def build_individual_stock_public_universe_bootstrap_result(
    *,
    current_date: str | None = None,
    stock_universe_path: str | Path = DEFAULT_STOCK_UNIVERSE_PATH,
    stock_signals_path: str | Path = DEFAULT_STOCK_SIGNALS_PATH,
    ranked_stocks_path: str | Path = DEFAULT_RANKED_STOCKS_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    bootstrap_stock_universe: bool = False,
    write_stock_signals: bool = False,
    write_ranked_stocks: bool = False,
    bootstrap_style: str = DEFAULT_BOOTSTRAP_STYLE,
) -> IndividualStockPublicUniverseBootstrapResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")

    resolved_universe = _resolve_path(stock_universe_path, root)
    resolved_signals = _resolve_path(stock_signals_path, root)
    resolved_ranked = _resolve_path(ranked_stocks_path, root)

    for label, path in (
        ("stock universe path", resolved_universe),
        ("stock signals path", resolved_signals),
        ("ranked stocks path", resolved_ranked),
    ):
        if not _is_under(path, root, "jarvis/local"):
            blockers.append(f"{label} must remain under jarvis/local/.")

    universe_written = False
    if bootstrap_stock_universe and not blockers:
        write_bootstrap_stock_universe(
            path=stock_universe_path,
            root=root,
            current_date=current_date_text,
            bootstrap_style=bootstrap_style,
        )
        universe_written = True

    ranker_result = None
    if not blockers:
        ranker_result = build_individual_stock_public_ranker_result(
            current_date=current_date_text,
            stock_universe_path=stock_universe_path,
            stock_signals_path=stock_signals_path,
            ranked_stocks_path=ranked_stocks_path,
            root=root,
            max_age_days=max_age_days,
            write_stock_signals=write_stock_signals,
            write_ranked_stocks=write_ranked_stocks,
        )
        blockers.extend(getattr(ranker_result, "blockers", ()) or [])
        warnings.extend(getattr(ranker_result, "warnings", ()) or [])
        ranker_status = str(getattr(ranker_result, "status", ""))
        if "BLOCKED" in ranker_status:
            blockers.append("individual stock public ranker was blocked.")
        elif "READY" not in ranker_status or "REVIEW_REQUIRED" in ranker_status:
            warnings.append("individual stock public ranker requires review.")

    ranked_candidate_count = int(getattr(ranker_result, "ranked_candidate_count", 0) or 0)
    if bootstrap_stock_universe and ranked_candidate_count == 0 and not blockers:
        warnings.append("bootstrap stock universe was written but no fresh ranked candidates were produced.")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        bootstrap_status = BOOTSTRAP_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        bootstrap_status = BOOTSTRAP_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        bootstrap_status = BOOTSTRAP_READY

    return IndividualStockPublicUniverseBootstrapResult(
        status=status,
        bootstrap_status=bootstrap_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        stock_universe_path=str(resolved_universe),
        stock_signals_path=str(resolved_signals),
        ranked_stocks_path=str(resolved_ranked),
        bootstrap_style=bootstrap_style,
        bootstrap_stock_count=len(STARTER_STOCK_UNIVERSE),
        bootstrap_universe_written=universe_written,
        stock_signals_written=bool(getattr(ranker_result, "upstream_stock_universe_result", None) and getattr(getattr(ranker_result, "upstream_stock_universe_result"), "stock_signals_written", False)),
        ranked_stocks_written=bool(getattr(ranker_result, "ranked_stocks_written", False)),
        upstream_ranker_result=ranker_result,
        ranked_candidate_count=ranked_candidate_count,
        top_ranked_stock_id=getattr(ranker_result, "top_ranked_stock_id", None),
        top_ranked_symbol=getattr(ranker_result, "top_ranked_symbol", None),
        recommendation_quality_current_data=not unique_blockers and not unique_warnings,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        portfolio_state_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        final_user_buy_action_required=True,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )


def _upstream_ranker_summary(ranker: Any) -> str:
    if ranker is None:
        return "none"

    lines = [
        "J.A.R.V.I.S. Individual Stock Public Ranker",
        f"status: {getattr(ranker, 'status', 'unknown')}",
        f"ready stock count: {getattr(ranker, 'ready_stock_count', 'unknown')}",
        f"ranked candidate count: {getattr(ranker, 'ranked_candidate_count', 'unknown')}",
        f"top ranked stock id: {getattr(ranker, 'top_ranked_stock_id', None) or 'none'}",
        f"top ranked symbol: {getattr(ranker, 'top_ranked_symbol', None) or 'none'}",
    ]

    candidates = tuple(getattr(ranker, "ranked_candidates", ()) or ())
    if candidates:
        lines.append("Top ranked candidates:")
        for candidate in candidates[:5]:
            lines.append(
                f"- #{getattr(candidate, 'rank', '?')} {getattr(candidate, 'stock_id', 'unknown')}: "
                f"{getattr(candidate, 'symbol', None) or getattr(candidate, 'ticker', None) or 'no symbol'}; "
                f"score {float(getattr(candidate, 'ranking_score', 0.0)):,.2f}; "
                f"decision {getattr(candidate, 'decision_status', 'unknown')}"
            )
    else:
        lines.append("Top ranked candidates: none")

    return "\n".join(lines)


def format_individual_stock_public_universe_bootstrap(result: IndividualStockPublicUniverseBootstrapResult) -> str:
    lines = [
        "J.A.R.V.I.S. Individual Stock Public Universe Bootstrap",
        f"status: {result.status}",
        f"bootstrap status: {result.bootstrap_status}",
        f"current date: {result.current_date}",
        f"stock universe path: {result.stock_universe_path}",
        f"stock signals path: {result.stock_signals_path}",
        f"ranked stocks path: {result.ranked_stocks_path}",
        f"bootstrap style: {result.bootstrap_style}",
        f"bootstrap stock count: {result.bootstrap_stock_count}",
        f"bootstrap universe written: {result.bootstrap_universe_written}",
        f"stock signals written: {result.stock_signals_written}",
        f"ranked stocks written: {result.ranked_stocks_written}",
        f"ranked candidate count: {result.ranked_candidate_count}",
        f"top ranked stock id: {result.top_ranked_stock_id or 'none'}",
        f"top ranked symbol: {result.top_ranked_symbol or 'none'}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        "",
        "Important:",
        "- bootstrap universe is not a buy list",
        "- ranked candidates are for review only",
        "- no stock approval ticket is written",
        "- final real-world buy remains manual outside J.A.R.V.I.S.",
        "",
        "Safety:",
        f"- allocation mutation: {result.allocation_mutation}",
        f"- approval ticket mutation: {result.approval_ticket_mutation}",
        f"- portfolio state mutation: {result.portfolio_state_mutation}",
        f"- buy request created: {result.buy_request_created}",
        "- no broker connection",
        "- no credentials",
        "- no private account data ingestion",
        "- no orders created",
        "- no trades executed",
        "",
        "Upstream ranker summary:",
        _upstream_ranker_summary(result.upstream_ranker_result),
    ]

    if result.blockers:
        lines.extend(["", "Blockers:"])
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("blockers: none")

    if result.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("warnings: none")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bootstrap local public stock universe and run safe individual-stock ranker.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run stock universe bootstrap/ranker wrapper.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--stock-universe-path", default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--stock-signals-path", default=DEFAULT_STOCK_SIGNALS_PATH)
    parser.add_argument("--ranked-stocks-path", default=DEFAULT_RANKED_STOCKS_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--bootstrap-stock-universe", action="store_true", help="Write starter public stock universe under jarvis/local.")
    parser.add_argument("--write-stock-signals", action="store_true", help="Write local individual stock public signals under jarvis/local.")
    parser.add_argument("--write-ranked-stocks", action="store_true", help="Write local ranked individual stock candidates under jarvis/local.")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    if args.voice_command:
        print(build_safety_check_console_output(args.voice_command))
        return 0

    if args.demo:
        print("Available typed Jarvis commands:")
        for command in DEFAULT_COMMAND_SAMPLES:
            print(f"- {command}")
        return 0

    result = build_individual_stock_public_universe_bootstrap_result(
        current_date=args.current_date,
        stock_universe_path=args.stock_universe_path,
        stock_signals_path=args.stock_signals_path,
        ranked_stocks_path=args.ranked_stocks_path,
        max_age_days=args.max_age_days,
        bootstrap_stock_universe=args.bootstrap_stock_universe,
        write_stock_signals=args.write_stock_signals,
        write_ranked_stocks=args.write_ranked_stocks,
    )
    print(format_individual_stock_public_universe_bootstrap(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())