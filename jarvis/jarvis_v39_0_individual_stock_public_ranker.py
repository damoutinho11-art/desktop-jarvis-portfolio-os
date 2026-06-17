"""J.A.R.V.I.S. v39.0 individual stock public ranker.

v39 consumes the v38 individual-stock public signals and ranks only fresh,
public-source-ready stocks.

It deliberately does not approve a stock, write stock approval tickets, mutate
allocation, connect brokers, create orders, or trade.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from .jarvis_v38_0_individual_stock_public_universe_engine import (
    DEFAULT_STOCK_SIGNALS_PATH,
    DEFAULT_STOCK_UNIVERSE_PATH,
    STOCK_READY,
    IndividualStockPublicUniverseEngineResult,
    build_individual_stock_public_universe_engine_result,
    format_individual_stock_public_universe_engine,
)

STATUS_READY = "JARVIS_V39_0_INDIVIDUAL_STOCK_PUBLIC_RANKER_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V39_0_INDIVIDUAL_STOCK_PUBLIC_RANKER_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V39_0_INDIVIDUAL_STOCK_PUBLIC_RANKER_BLOCKED_SAFE"

RANKER_READY = "INDIVIDUAL_STOCK_PUBLIC_RANKER_READY"
RANKER_REVIEW_REQUIRED = "INDIVIDUAL_STOCK_PUBLIC_RANKER_REVIEW_REQUIRED"
RANKER_BLOCKED = "INDIVIDUAL_STOCK_PUBLIC_RANKER_BLOCKED"

NEXT_STAGE = "individual_stock_ranked_candidate_ticket_bridge"

DEFAULT_RANKED_STOCKS_PATH = "jarvis/local/individual_stock_public_ranked_candidates.local.json"

DECISION_STATUS_NOT_APPROVED = "RANKED_STOCK_CANDIDATE_FOR_REVIEW_NOT_APPROVED"


@dataclass(frozen=True)
class RankedIndividualStockCandidate:
    rank: int
    stock_id: str
    name: str | None
    ticker: str | None
    exchange: str | None
    market: str | None
    sector: str | None
    provider: str | None
    symbol: str | None
    currency: str | None
    source_url: str | None
    source_as_of: str | None
    close_price: float
    priority_score: float
    ranking_score: float
    source_status: str
    decision_status: str
    rationale: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "stock_id": self.stock_id,
            "name": self.name,
            "ticker": self.ticker,
            "exchange": self.exchange,
            "market": self.market,
            "sector": self.sector,
            "provider": self.provider,
            "symbol": self.symbol,
            "currency": self.currency,
            "source_url": self.source_url,
            "source_as_of": self.source_as_of,
            "close_price": self.close_price,
            "priority_score": self.priority_score,
            "ranking_score": self.ranking_score,
            "source_status": self.source_status,
            "decision_status": self.decision_status,
            "rationale": list(self.rationale),
        }


@dataclass(frozen=True)
class IndividualStockPublicRankerResult:
    status: str
    ranker_status: str
    recommended_next_stage: str
    current_date: str
    stock_universe_path: str
    stock_signals_path: str
    ranked_stocks_path: str
    ranked_stocks_written: bool
    ready_stock_count: int
    ranked_candidate_count: int
    top_ranked_stock_id: str | None
    top_ranked_symbol: str | None
    top_ranked_name: str | None
    ranked_candidates: tuple[RankedIndividualStockCandidate, ...]
    upstream_stock_universe_result: Any
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
            "ranker_status": self.ranker_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "stock_universe_path": self.stock_universe_path,
            "stock_signals_path": self.stock_signals_path,
            "ranked_stocks_path": self.ranked_stocks_path,
            "ranked_stocks_written": self.ranked_stocks_written,
            "ready_stock_count": self.ready_stock_count,
            "ranked_candidate_count": self.ranked_candidate_count,
            "top_ranked_stock_id": self.top_ranked_stock_id,
            "top_ranked_symbol": self.top_ranked_symbol,
            "top_ranked_name": self.top_ranked_name,
            "ranked_candidates": [candidate.to_dict() for candidate in self.ranked_candidates],
            "upstream_stock_universe_result": self.upstream_stock_universe_result.to_dict()
            if hasattr(self.upstream_stock_universe_result, "to_dict")
            else dict(getattr(self.upstream_stock_universe_result, "__dict__", {})),
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


def _days_old(*, source_as_of: str | None, current_date: str) -> int | None:
    source_date = _parse_date(source_as_of)
    current = _parse_date(current_date)
    if source_date is None or current is None:
        return None
    return (current - source_date).days


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _dedupe(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


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


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _signal_attr(signal: Any, name: str, default: Any = None) -> Any:
    if isinstance(signal, dict):
        return signal.get(name, default)
    return getattr(signal, name, default)


def _is_rankable_signal(signal: Any) -> bool:
    close_price = _float_or_none(_signal_attr(signal, "close_price"))
    return (
        str(_signal_attr(signal, "source_status", "")) == STOCK_READY
        and close_price is not None
        and close_price > 0
        and bool(str(_signal_attr(signal, "source_as_of", "") or "").strip())
    )


def _ranking_score(signal: Any, *, current_date: str) -> float:
    priority = _float_or_none(_signal_attr(signal, "priority_score")) or 0.0
    close_price = _float_or_none(_signal_attr(signal, "close_price")) or 0.0
    age = _days_old(source_as_of=_signal_attr(signal, "source_as_of"), current_date=current_date)

    source_ready_bonus = 25.0
    price_valid_bonus = 5.0 if close_price > 0 else 0.0
    freshness_bonus = 0.0 if age is None else max(0.0, 10.0 - float(abs(age)))
    return round(priority + source_ready_bonus + price_valid_bonus + freshness_bonus, 6)


def _candidate_from_signal(*, signal: Any, rank: int, current_date: str) -> RankedIndividualStockCandidate:
    close_price = _float_or_none(_signal_attr(signal, "close_price"))
    if close_price is None:
        raise ValueError("ranked stock candidate requires a numeric close_price")

    score = _ranking_score(signal, current_date=current_date)
    rationale = (
        "fresh public stock quote is present",
        f"source status is {STOCK_READY}",
        "candidate is ranked for review only; it is not approved for buying",
        "no approval ticket, order, or trade is created",
    )

    return RankedIndividualStockCandidate(
        rank=rank,
        stock_id=str(_signal_attr(signal, "stock_id", "")),
        name=_signal_attr(signal, "name"),
        ticker=_signal_attr(signal, "ticker"),
        exchange=_signal_attr(signal, "exchange"),
        market=_signal_attr(signal, "market"),
        sector=_signal_attr(signal, "sector"),
        provider=_signal_attr(signal, "provider"),
        symbol=_signal_attr(signal, "symbol"),
        currency=_signal_attr(signal, "currency"),
        source_url=_signal_attr(signal, "source_url"),
        source_as_of=_signal_attr(signal, "source_as_of"),
        close_price=float(close_price),
        priority_score=float(_float_or_none(_signal_attr(signal, "priority_score")) or 0.0),
        ranking_score=score,
        source_status=str(_signal_attr(signal, "source_status", "")),
        decision_status=DECISION_STATUS_NOT_APPROVED,
        rationale=rationale,
    )


def _rank_signals(signals: tuple[Any, ...] | list[Any], *, current_date: str) -> tuple[RankedIndividualStockCandidate, ...]:
    rankable = [signal for signal in signals if _is_rankable_signal(signal)]
    sorted_signals = sorted(
        rankable,
        key=lambda signal: (
            _ranking_score(signal, current_date=current_date),
            _signal_attr(signal, "priority_score") or 0,
            str(_signal_attr(signal, "stock_id", "")),
        ),
        reverse=True,
    )
    return tuple(
        _candidate_from_signal(signal=signal, rank=index + 1, current_date=current_date)
        for index, signal in enumerate(sorted_signals)
    )


def build_individual_stock_public_ranker_result(
    *,
    current_date: str | None = None,
    stock_universe_path: str | Path = DEFAULT_STOCK_UNIVERSE_PATH,
    stock_signals_path: str | Path = DEFAULT_STOCK_SIGNALS_PATH,
    ranked_stocks_path: str | Path = DEFAULT_RANKED_STOCKS_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    write_stock_template: bool = False,
    write_stock_signals: bool = False,
    write_ranked_stocks: bool = False,
    upstream_stock_universe_result: IndividualStockPublicUniverseEngineResult | None = None,
    upstream_builder: Callable[..., IndividualStockPublicUniverseEngineResult] = build_individual_stock_public_universe_engine_result,
) -> IndividualStockPublicRankerResult:
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

    upstream = None
    if not blockers:
        upstream = upstream_stock_universe_result if upstream_stock_universe_result is not None else upstream_builder(
            current_date=current_date_text,
            stock_universe_path=stock_universe_path,
            stock_signals_path=stock_signals_path,
            root=root,
            max_age_days=max_age_days,
            write_stock_template=write_stock_template,
            write_stock_signals=write_stock_signals,
        )
        blockers.extend(getattr(upstream, "blockers", ()) or [])
        upstream_warnings = tuple(getattr(upstream, "warnings", ()) or ())
        warnings.extend(upstream_warnings)
        upstream_status = str(getattr(upstream, "status", ""))
        if "BLOCKED" in upstream_status:
            blockers.append("individual stock public universe engine was blocked.")
        elif "READY" not in upstream_status or "REVIEW_REQUIRED" in upstream_status:
            warnings.append("individual stock public universe engine requires review.")

    stock_signals = tuple(getattr(upstream, "stock_signals", ()) or ()) if upstream is not None else ()
    ready_count = sum(1 for signal in stock_signals if _is_rankable_signal(signal))
    ranked_candidates = _rank_signals(stock_signals, current_date=current_date_text)

    if not ranked_candidates and not blockers:
        warnings.append("individual stock ranker has no fresh ready stocks to rank.")

    ranked_written = False
    if write_ranked_stocks and not blockers:
        _write_json(
            resolved_ranked,
            {
                "version": 1,
                "current_date": current_date_text,
                "ranked_candidate_count": len(ranked_candidates),
                "top_ranked_stock_id": ranked_candidates[0].stock_id if ranked_candidates else None,
                "top_ranked_symbol": ranked_candidates[0].symbol if ranked_candidates else None,
                "ranked_candidates": [candidate.to_dict() for candidate in ranked_candidates],
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
                    "decision_status": "ranked_for_review_only_not_approved",
                },
            },
        )
        ranked_written = True

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        ranker_status = RANKER_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        ranker_status = RANKER_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        ranker_status = RANKER_READY

    top = ranked_candidates[0] if ranked_candidates else None

    return IndividualStockPublicRankerResult(
        status=status,
        ranker_status=ranker_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        stock_universe_path=str(resolved_universe),
        stock_signals_path=str(resolved_signals),
        ranked_stocks_path=str(resolved_ranked),
        ranked_stocks_written=ranked_written,
        ready_stock_count=ready_count,
        ranked_candidate_count=len(ranked_candidates),
        top_ranked_stock_id=top.stock_id if top else None,
        top_ranked_symbol=top.symbol if top else None,
        top_ranked_name=top.name if top else None,
        ranked_candidates=ranked_candidates,
        upstream_stock_universe_result=upstream,
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


def _format_ranked_candidates(result: IndividualStockPublicRankerResult) -> str:
    lines = ["Ranked individual stock candidates:"]
    if not result.ranked_candidates:
        lines.append("- none")
        return "\n".join(lines)

    for candidate in result.ranked_candidates:
        lines.append(
            f"- #{candidate.rank} {candidate.stock_id}: {candidate.name or 'unknown'} "
            f"({candidate.symbol or candidate.ticker or 'no symbol'}) "
            f"score {candidate.ranking_score:,.2f}; close {candidate.close_price:,.6f} "
            f"{candidate.currency or 'unknown'}; as_of {candidate.source_as_of}; "
            f"decision {candidate.decision_status}"
        )
    return "\n".join(lines)


def _upstream_console_output(upstream: Any) -> str:
    if upstream is None:
        return "none"

    dual_lane = getattr(upstream, "upstream_dual_lane_result", None)

    lines = [
        "J.A.R.V.I.S. Individual Stock Public Universe Engine",
        f"status: {getattr(upstream, 'status', 'unknown')}",
        f"stock universe loaded: {getattr(upstream, 'stock_universe_loaded', 'unknown')}",
        f"stock count: {getattr(upstream, 'stock_count', 'unknown')}",
        f"ready stock count: {getattr(upstream, 'ready_stock_count', 'unknown')}",
        f"missing source stock count: {getattr(upstream, 'missing_source_stock_count', 'unknown')}",
        f"network fetch attempted count: {getattr(upstream, 'network_fetch_attempted_count', 'unknown')}",
    ]

    if dual_lane is not None:
        lines.extend(
            [
                "",
                "Upstream dual-lane daily refresh summary:",
                f"status: {getattr(dual_lane, 'status', 'unknown')}",
                f"crypto refresh ran: {getattr(dual_lane, 'crypto_refresh_ran', 'unknown')}",
                f"crypto ticket written: {getattr(dual_lane, 'crypto_ticket_written', 'unknown')}",
                f"ETF/fund refresh ran: {getattr(dual_lane, 'etf_refresh_ran', 'unknown')}",
                f"ETF/fund ticket written: {getattr(dual_lane, 'etf_ticket_written', 'unknown')}",
                f"recommendation quality current data: {getattr(dual_lane, 'recommendation_quality_current_data', 'unknown')}",
            ]
        )

    lines.extend(
        [
            "",
            "Safety:",
            f"allocation mutation: {getattr(upstream, 'allocation_mutation', False)}",
            f"approval ticket mutation: {getattr(upstream, 'approval_ticket_mutation', False)}",
            f"portfolio state mutation: {getattr(upstream, 'portfolio_state_mutation', False)}",
            f"buy request created: {getattr(upstream, 'buy_request_created', False)}",
            "no broker connection",
            "no credentials",
            "no private account data ingestion",
            "no orders created",
            f"no trades executed: {getattr(upstream, 'no_trades_executed', 'unknown')}",
        ]
    )
    return "\n".join(lines)


def format_individual_stock_public_ranker(result: IndividualStockPublicRankerResult) -> str:
    lines = [
        "J.A.R.V.I.S. Individual Stock Public Ranker",
        f"status: {result.status}",
        f"ranker status: {result.ranker_status}",
        f"current date: {result.current_date}",
        f"stock universe path: {result.stock_universe_path}",
        f"stock signals path: {result.stock_signals_path}",
        f"ranked stocks path: {result.ranked_stocks_path}",
        f"ranked stocks written: {result.ranked_stocks_written}",
        f"ready stock count: {result.ready_stock_count}",
        f"ranked candidate count: {result.ranked_candidate_count}",
        f"top ranked stock id: {result.top_ranked_stock_id or 'none'}",
        f"top ranked symbol: {result.top_ranked_symbol or 'none'}",
        f"top ranked name: {result.top_ranked_name or 'none'}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"portfolio state mutation: {result.portfolio_state_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
        "",
        _format_ranked_candidates(result),
        "",
        "Upstream individual stock public universe engine:",
        _upstream_console_output(result.upstream_stock_universe_result),
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
    parser = argparse.ArgumentParser(description="Run individual stock public ranker after v38 public-source refresh.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run individual stock public ranker.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--stock-universe-path", default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--stock-signals-path", default=DEFAULT_STOCK_SIGNALS_PATH)
    parser.add_argument("--ranked-stocks-path", default=DEFAULT_RANKED_STOCKS_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--write-stock-template", action="store_true", help="Write local individual stock universe template under jarvis/local.")
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

    result = build_individual_stock_public_ranker_result(
        current_date=args.current_date,
        stock_universe_path=args.stock_universe_path,
        stock_signals_path=args.stock_signals_path,
        ranked_stocks_path=args.ranked_stocks_path,
        max_age_days=args.max_age_days,
        write_stock_template=args.write_stock_template,
        write_stock_signals=args.write_stock_signals,
        write_ranked_stocks=args.write_ranked_stocks,
    )
    print(format_individual_stock_public_ranker(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())