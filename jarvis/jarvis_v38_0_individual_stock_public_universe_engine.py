"""J.A.R.V.I.S. v38.0 individual stock public universe engine.

v38 starts the individual-stock lane safely.

It keeps the v37 crypto + ETF/fund daily refresh intact, then checks a local
individual-stock public universe. A stock can count as data-ready only if it has
a real public provider/symbol and a fresh fetched public quote.

No stock picks are promoted yet. This is the public-data foundation for a later
stock ranker.
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
from .jarvis_v33_0_stock_fund_etf_public_source_fetcher import (
    SOURCE_FETCH_FAILED,
    SOURCE_INVALID,
    SOURCE_MISSING,
    SOURCE_READY,
    SOURCE_STALE,
    SOURCE_UNSUPPORTED,
    StockFundEtfPublicSourceSignal,
    _default_fetch_text,
    _fetch_source,
)
from .jarvis_v37_0_autonomous_dual_lane_daily_refresh import (
    AutonomousDualLaneDailyRefreshResult,
    build_autonomous_dual_lane_daily_refresh_result,
    format_autonomous_dual_lane_daily_refresh,
)

STATUS_READY = "JARVIS_V38_0_INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_ENGINE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V38_0_INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_ENGINE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V38_0_INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_ENGINE_BLOCKED_SAFE"

ENGINE_READY = "INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_ENGINE_READY"
ENGINE_REVIEW_REQUIRED = "INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_ENGINE_REVIEW_REQUIRED"
ENGINE_BLOCKED = "INDIVIDUAL_STOCK_PUBLIC_UNIVERSE_ENGINE_BLOCKED"

NEXT_STAGE = "individual_stock_public_ranker_and_ticket_lane"

DEFAULT_STOCK_UNIVERSE_PATH = "jarvis/local/individual_stock_public_universe.local.json"
DEFAULT_STOCK_SIGNALS_PATH = "jarvis/local/individual_stock_public_signals.local.json"

STOCK_READY = "STOCK_PUBLIC_SOURCE_READY"
STOCK_MISSING_SOURCE = "STOCK_PUBLIC_SOURCE_MISSING"
STOCK_UNSUPPORTED_SOURCE = "STOCK_PUBLIC_SOURCE_UNSUPPORTED"
STOCK_FETCH_FAILED = "STOCK_PUBLIC_SOURCE_FETCH_FAILED"
STOCK_STALE = "STOCK_PUBLIC_SOURCE_STALE"
STOCK_INVALID = "STOCK_PUBLIC_SOURCE_INVALID"


@dataclass(frozen=True)
class IndividualStockSignal:
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
    close_price: float | None
    priority_score: float
    source_status: str
    original_source_status: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
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
            "source_status": self.source_status,
            "original_source_status": self.original_source_status,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class IndividualStockPublicUniverseEngineResult:
    status: str
    engine_status: str
    recommended_next_stage: str
    current_date: str
    stock_universe_path: str
    stock_signals_path: str
    stock_universe_loaded: bool
    stock_universe_template_written: bool
    stock_signals_written: bool
    stock_count: int
    ready_stock_count: int
    missing_source_stock_count: int
    stale_or_failed_stock_count: int
    network_fetch_attempted_count: int
    stock_signals: tuple[IndividualStockSignal, ...]
    upstream_dual_lane_result: Any
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
            "engine_status": self.engine_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "stock_universe_path": self.stock_universe_path,
            "stock_signals_path": self.stock_signals_path,
            "stock_universe_loaded": self.stock_universe_loaded,
            "stock_universe_template_written": self.stock_universe_template_written,
            "stock_signals_written": self.stock_signals_written,
            "stock_count": self.stock_count,
            "ready_stock_count": self.ready_stock_count,
            "missing_source_stock_count": self.missing_source_stock_count,
            "stale_or_failed_stock_count": self.stale_or_failed_stock_count,
            "network_fetch_attempted_count": self.network_fetch_attempted_count,
            "stock_signals": [signal.to_dict() for signal in self.stock_signals],
            "upstream_dual_lane_result": self.upstream_dual_lane_result.to_dict() if hasattr(self.upstream_dual_lane_result, "to_dict") else dict(getattr(self.upstream_dual_lane_result, "__dict__", {})),
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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_individual_stock_universe_template(*, current_date: str) -> dict[str, Any]:
    return {
        "version": 1,
        "generated_at": current_date,
        "purpose": "Local operator-managed individual-stock public universe. Fill real public stock instruments only; do not commit this file.",
        "supported_providers": ["yahoo_chart", "stooq_csv"],
        "stocks": [
            {
                "stock_id": "",
                "name": "",
                "ticker": "",
                "exchange": "",
                "market": "",
                "sector": "",
                "currency": "",
                "provider": "",
                "symbol": "",
                "source_url": "",
                "priority_score": 0.0,
                "notes": "Fill with a real listed stock and verified public quote provider/symbol. Blank rows never count as data.",
            }
        ],
    }


def _stocks_from_universe(universe: dict[str, Any]) -> list[dict[str, Any]]:
    stocks = universe.get("stocks", [])
    if isinstance(stocks, list):
        return [dict(item) for item in stocks if isinstance(item, dict)]
    if isinstance(stocks, dict):
        output: list[dict[str, Any]] = []
        for key, value in stocks.items():
            if isinstance(value, dict):
                item = dict(value)
                item.setdefault("stock_id", key)
                output.append(item)
        return output
    return []


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _stock_id(stock: dict[str, Any], index: int) -> str:
    for key in ("stock_id", "id", "ticker", "symbol", "name"):
        value = stock.get(key)
        if value:
            return str(value)
    return f"unnamed_stock_{index + 1}"


def _map_source_status(status: str) -> str:
    mapping = {
        SOURCE_READY: STOCK_READY,
        SOURCE_MISSING: STOCK_MISSING_SOURCE,
        SOURCE_UNSUPPORTED: STOCK_UNSUPPORTED_SOURCE,
        SOURCE_FETCH_FAILED: STOCK_FETCH_FAILED,
        SOURCE_STALE: STOCK_STALE,
        SOURCE_INVALID: STOCK_INVALID,
    }
    return mapping.get(status, STOCK_FETCH_FAILED)


def _signal_from_stock(
    *,
    stock: dict[str, Any],
    index: int,
    public_signal: StockFundEtfPublicSourceSignal,
) -> IndividualStockSignal:
    return IndividualStockSignal(
        stock_id=_stock_id(stock, index),
        name=str(stock.get("name") or "") or None,
        ticker=str(stock.get("ticker") or "") or None,
        exchange=str(stock.get("exchange") or "") or None,
        market=str(stock.get("market") or "") or None,
        sector=str(stock.get("sector") or "") or None,
        provider=public_signal.provider,
        symbol=public_signal.symbol,
        currency=public_signal.currency or str(stock.get("currency") or "") or None,
        source_url=public_signal.source_url,
        source_as_of=public_signal.source_as_of,
        close_price=public_signal.close_price,
        priority_score=float(_float_or_none(stock.get("priority_score")) or 0.0),
        source_status=_map_source_status(public_signal.source_status),
        original_source_status=public_signal.source_status,
        blockers=tuple(
            str(blocker).replace("ETF/fund", "individual stock").replace("ETF", "stock")
            for blocker in public_signal.blockers
        ),
        warnings=tuple(
            str(warning).replace("ETF/fund", "individual stock").replace("ETF", "stock")
            for warning in public_signal.warnings
        ),
    )


def build_individual_stock_public_universe_engine_result(
    *,
    current_date: str | None = None,
    stock_universe_path: str | Path = DEFAULT_STOCK_UNIVERSE_PATH,
    stock_signals_path: str | Path = DEFAULT_STOCK_SIGNALS_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    write_stock_template: bool = False,
    write_stock_signals: bool = False,
    fetch_text: Callable[[str], str] = _default_fetch_text,
    upstream_dual_lane_result: AutonomousDualLaneDailyRefreshResult | None = None,
    upstream_builder: Callable[..., AutonomousDualLaneDailyRefreshResult] = build_autonomous_dual_lane_daily_refresh_result,
) -> IndividualStockPublicUniverseEngineResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")
    if max_age_days < 0:
        blockers.append("max_age_days must be non-negative.")

    resolved_universe = _resolve_path(stock_universe_path, root)
    resolved_signals = _resolve_path(stock_signals_path, root)

    if not _is_under(resolved_universe, root, "jarvis/local"):
        blockers.append("individual stock universe path must remain under jarvis/local/.")
    if not _is_under(resolved_signals, root, "jarvis/local"):
        blockers.append("individual stock signals path must remain under jarvis/local/.")

    upstream = None
    if not blockers:
        upstream = upstream_dual_lane_result if upstream_dual_lane_result is not None else upstream_builder(
            current_date=current_date_text,
            root=root,
        )
        blockers.extend(getattr(upstream, "blockers", ()) or [])
        warnings.extend(getattr(upstream, "warnings", ()) or [])
        upstream_status = str(getattr(upstream, "status", ""))
        if "BLOCKED" in upstream_status:
            blockers.append("dual-lane daily refresh was blocked.")
        elif "READY" not in upstream_status or "REVIEW_REQUIRED" in upstream_status:
            warnings.append("dual-lane daily refresh requires review.")

    template_written = False
    if write_stock_template and not blockers:
        _write_json(resolved_universe, build_individual_stock_universe_template(current_date=current_date_text))
        template_written = True

    universe: dict[str, Any] = {}
    universe_loaded = False
    if not blockers and resolved_universe.exists():
        universe = _load_json(resolved_universe)
        universe_loaded = True
    elif not blockers:
        warnings.append("individual stock public universe is missing; no stock lane data can be refreshed.")

    stocks = _stocks_from_universe(universe)
    stock_signals: list[IndividualStockSignal] = []
    network_fetch_attempts = 0

    for index, stock in enumerate(stocks):
        source = {
            "provider": stock.get("provider"),
            "symbol": stock.get("symbol") or stock.get("ticker"),
            "source_url": stock.get("source_url"),
            "currency": stock.get("currency"),
        }
        if str(source.get("provider") or "").strip() and str(source.get("symbol") or "").strip():
            network_fetch_attempts += 1
        signal = _fetch_source(
            candidate_id=_stock_id(stock, index),
            source=source,
            current_date_text=current_date_text,
            max_age_days=max_age_days,
            fetch_text=fetch_text,
        )
        stock_signals.append(_signal_from_stock(stock=stock, index=index, public_signal=signal))

    for signal in stock_signals:
        blockers.extend(signal.blockers)
        warnings.extend(signal.warnings)

    ready_count = sum(1 for signal in stock_signals if signal.source_status == STOCK_READY)
    missing_count = sum(1 for signal in stock_signals if signal.source_status in {STOCK_MISSING_SOURCE, STOCK_UNSUPPORTED_SOURCE})
    stale_or_failed_count = sum(1 for signal in stock_signals if signal.source_status in {STOCK_STALE, STOCK_FETCH_FAILED, STOCK_INVALID})

    if universe_loaded and not stock_signals:
        warnings.append("individual stock public universe has no stocks.")
    if stock_signals and ready_count == 0:
        warnings.append("individual stock public universe has no fresh ready stock quotes.")

    signals_written = False
    if write_stock_signals and not blockers:
        _write_json(
            resolved_signals,
            {
                "version": 1,
                "current_date": current_date_text,
                "stock_count": len(stock_signals),
                "ready_stock_count": ready_count,
                "stock_signals": [signal.to_dict() for signal in stock_signals],
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
            },
        )
        signals_written = True

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        engine_status = ENGINE_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        engine_status = ENGINE_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        engine_status = ENGINE_READY

    return IndividualStockPublicUniverseEngineResult(
        status=status,
        engine_status=engine_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        stock_universe_path=str(resolved_universe),
        stock_signals_path=str(resolved_signals),
        stock_universe_loaded=universe_loaded,
        stock_universe_template_written=template_written,
        stock_signals_written=signals_written,
        stock_count=len(stock_signals),
        ready_stock_count=ready_count,
        missing_source_stock_count=missing_count,
        stale_or_failed_stock_count=stale_or_failed_count,
        network_fetch_attempted_count=network_fetch_attempts,
        stock_signals=tuple(stock_signals),
        upstream_dual_lane_result=upstream,
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


def _format_stock_signals(result: IndividualStockPublicUniverseEngineResult) -> str:
    lines = ["Individual stock public signals:"]
    if not result.stock_signals:
        lines.append("- none")
        return "\n".join(lines)

    for signal in result.stock_signals:
        close = f"{signal.close_price:,.6f}" if signal.close_price is not None else "none"
        lines.append(
            f"- {signal.stock_id}: {signal.source_status}; ticker {signal.ticker or 'none'}; "
            f"provider {signal.provider or 'none'}; symbol {signal.symbol or 'none'}; "
            f"as_of {signal.source_as_of or 'none'}; close {close}; "
            f"currency {signal.currency or 'unknown'}; priority_score {signal.priority_score:,.2f}"
        )
        if signal.source_url:
            lines.append(f"  source_url: {signal.source_url}")
        for warning in signal.warnings:
            lines.append(f"  warning: {warning}")
    return "\n".join(lines)


def _upstream_console_output(upstream: Any) -> str:
    if upstream is None:
        return "none"

    required = (
        "current_date",
        "ticket_path",
        "instrument_universe_path",
        "resolution_path",
        "crypto_refresh_ran",
        "etf_refresh_ran",
    )
    if hasattr(upstream, "daily_status") and all(hasattr(upstream, attr) for attr in required):
        return format_autonomous_dual_lane_daily_refresh(upstream)

    return "\n".join(
        [
            "J.A.R.V.I.S. Autonomous Dual-Lane Daily Refresh",
            f"status: {getattr(upstream, 'status', 'unknown')}",
            f"daily status: {getattr(upstream, 'daily_status', 'unknown')}",
            f"approval ticket mutation: {getattr(upstream, 'approval_ticket_mutation', 'unknown')}",
            f"buy request created: {getattr(upstream, 'buy_request_created', 'unknown')}",
            "no broker connection",
            "no credentials",
            "no private account data ingestion",
            "no orders created",
            f"no trades executed: {getattr(upstream, 'no_trades_executed', 'unknown')}",
        ]
    )


def format_individual_stock_public_universe_engine(result: IndividualStockPublicUniverseEngineResult) -> str:
    lines = [
        "J.A.R.V.I.S. Individual Stock Public Universe Engine",
        f"status: {result.status}",
        f"engine status: {result.engine_status}",
        f"current date: {result.current_date}",
        f"stock universe path: {result.stock_universe_path}",
        f"stock signals path: {result.stock_signals_path}",
        f"stock universe loaded: {result.stock_universe_loaded}",
        f"stock universe template written: {result.stock_universe_template_written}",
        f"stock signals written: {result.stock_signals_written}",
        f"stock count: {result.stock_count}",
        f"ready stock count: {result.ready_stock_count}",
        f"missing source stock count: {result.missing_source_stock_count}",
        f"stale or failed stock count: {result.stale_or_failed_stock_count}",
        f"network fetch attempted count: {result.network_fetch_attempted_count}",
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
        _format_stock_signals(result),
        "",
        "Upstream dual-lane daily refresh:",
        _upstream_console_output(result.upstream_dual_lane_result),
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
    parser = argparse.ArgumentParser(description="Run individual stock public universe engine after safe dual-lane daily refresh.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run individual stock public universe engine.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--stock-universe-path", default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--stock-signals-path", default=DEFAULT_STOCK_SIGNALS_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--write-stock-template", action="store_true", help="Write local individual stock universe template under jarvis/local.")
    parser.add_argument("--write-stock-signals", action="store_true", help="Write local individual stock public signals under jarvis/local.")
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

    result = build_individual_stock_public_universe_engine_result(
        current_date=args.current_date,
        stock_universe_path=args.stock_universe_path,
        stock_signals_path=args.stock_signals_path,
        max_age_days=args.max_age_days,
        write_stock_template=args.write_stock_template,
        write_stock_signals=args.write_stock_signals,
    )
    print(format_individual_stock_public_universe_engine(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())