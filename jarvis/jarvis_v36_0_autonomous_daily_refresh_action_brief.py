"""J.A.R.V.I.S. v36.0 autonomous daily refresh and clean action brief.

v36 turns the stock/fund/ETF lane into a safe daily refresh loop:

1. Refresh the selected ETF sleeve into a real instrument using v34.
2. Fetch fresh public quote data for that real instrument.
3. Bridge the selected real instrument into the approval ticket using v35.
4. Print a clean manual action brief.

Autonomous here means autonomous when the daily command runs. It does not mean
background execution, broker connectivity, private account access, or trading.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from .jarvis_v30_0_expanded_crypto_approval_ticket_refresh import DEFAULT_OUTPUT_PATH
from .jarvis_v34_0_stock_fund_etf_sleeve_to_instrument_resolver import (
    DEFAULT_INSTRUMENT_UNIVERSE_PATH,
    DEFAULT_OUTPUT_RESOLUTION_PATH,
    StockFundEtfSleeveToInstrumentResolverResult,
    build_stock_fund_etf_sleeve_to_instrument_resolver_result,
)
from .jarvis_v33_0_stock_fund_etf_public_source_fetcher import _default_fetch_text
from .jarvis_v35_0_selected_stock_fund_etf_instrument_ticket_bridge import (
    SelectedStockFundEtfInstrumentTicketBridgeResult,
    build_selected_stock_fund_etf_instrument_ticket_bridge_result,
)

STATUS_READY = "JARVIS_V36_0_AUTONOMOUS_DAILY_REFRESH_ACTION_BRIEF_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V36_0_AUTONOMOUS_DAILY_REFRESH_ACTION_BRIEF_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V36_0_AUTONOMOUS_DAILY_REFRESH_ACTION_BRIEF_BLOCKED_SAFE"

DAILY_READY = "AUTONOMOUS_DAILY_REFRESH_ACTION_BRIEF_READY"
DAILY_REVIEW_REQUIRED = "AUTONOMOUS_DAILY_REFRESH_ACTION_BRIEF_REVIEW_REQUIRED"
DAILY_BLOCKED = "AUTONOMOUS_DAILY_REFRESH_ACTION_BRIEF_BLOCKED"

NEXT_STAGE = "portfolio_state_freshness_refresh_or_individual_stock_universe"


@dataclass(frozen=True)
class AutonomousDailyRefreshActionBriefResult:
    status: str
    daily_status: str
    recommended_next_stage: str
    current_date: str
    ticket_path: str
    instrument_universe_path: str
    resolution_path: str
    resolver_ran: bool
    bridge_ran: bool
    local_resolution_written: bool
    approval_ticket_written: bool
    ticket_loaded_after_refresh: bool
    crypto_candidate: str | None
    crypto_amount_eur: float | None
    stock_fund_etf_sleeve: str | None
    stock_fund_etf_amount_eur: float | None
    real_instrument_id: str | None
    real_instrument_name: str | None
    real_instrument_isin: str | None
    real_instrument_symbol: str | None
    real_instrument_provider: str | None
    real_instrument_currency: str | None
    real_instrument_source_as_of: str | None
    real_instrument_source_age_days: int | None
    real_instrument_close_price: float | None
    real_instrument_public_source_ready: bool
    recommendation_quality_current_data: bool
    resolver_result: Any
    bridge_result: Any
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
            "daily_status": self.daily_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "ticket_path": self.ticket_path,
            "instrument_universe_path": self.instrument_universe_path,
            "resolution_path": self.resolution_path,
            "resolver_ran": self.resolver_ran,
            "bridge_ran": self.bridge_ran,
            "local_resolution_written": self.local_resolution_written,
            "approval_ticket_written": self.approval_ticket_written,
            "ticket_loaded_after_refresh": self.ticket_loaded_after_refresh,
            "crypto_candidate": self.crypto_candidate,
            "crypto_amount_eur": self.crypto_amount_eur,
            "stock_fund_etf_sleeve": self.stock_fund_etf_sleeve,
            "stock_fund_etf_amount_eur": self.stock_fund_etf_amount_eur,
            "real_instrument_id": self.real_instrument_id,
            "real_instrument_name": self.real_instrument_name,
            "real_instrument_isin": self.real_instrument_isin,
            "real_instrument_symbol": self.real_instrument_symbol,
            "real_instrument_provider": self.real_instrument_provider,
            "real_instrument_currency": self.real_instrument_currency,
            "real_instrument_source_as_of": self.real_instrument_source_as_of,
            "real_instrument_source_age_days": self.real_instrument_source_age_days,
            "real_instrument_close_price": self.real_instrument_close_price,
            "real_instrument_public_source_ready": self.real_instrument_public_source_ready,
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "resolver_result": self.resolver_result.to_dict() if hasattr(self.resolver_result, "to_dict") else dict(getattr(self.resolver_result, "__dict__", {})),
            "bridge_result": self.bridge_result.to_dict() if hasattr(self.bridge_result, "to_dict") else dict(getattr(self.bridge_result, "__dict__", {})),
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


def _load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _amount_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _crypto_candidate(ticket: dict[str, Any]) -> str | None:
    for key in ("selected_crypto_candidate", "selected_crypto_asset", "crypto_candidate", "crypto_asset"):
        value = ticket.get(key)
        if value:
            return str(value)
    crypto_lane = ticket.get("crypto_lane")
    if isinstance(crypto_lane, dict):
        for key in ("asset", "candidate", "symbol", "id"):
            value = crypto_lane.get(key)
            if value:
                return str(value)
    return None


def _crypto_amount(ticket: dict[str, Any]) -> float | None:
    for key in ("selected_crypto_amount_eur", "crypto_amount_eur", "selected_crypto_candidate_amount_eur"):
        value = _amount_or_none(ticket.get(key))
        if value is not None:
            return value
    crypto_lane = ticket.get("crypto_lane")
    if isinstance(crypto_lane, dict):
        for key in ("amount_eur", "eur_amount", "amount"):
            value = _amount_or_none(crypto_lane.get(key))
            if value is not None:
                return value
    allocation = ticket.get("approval_amounts_eur")
    if isinstance(allocation, dict):
        for key in ("crypto", "crypto_lane", "hype", "btc"):
            value = _amount_or_none(allocation.get(key))
            if value is not None:
                return value
    return None


def _ready_upstream_public_source_result() -> SimpleNamespace:
    status = "JARVIS_V33_0_STOCK_FUND_ETF_PUBLIC_SOURCE_FETCHER_SUPERSEDED_BY_REAL_INSTRUMENT_RESOLVER_READY_SAFE"
    return SimpleNamespace(
        status=status,
        selected_stock_fund_etf_candidate="real_instrument_resolver",
        selected_candidate_source_status="SUPERSEDED_BY_REAL_INSTRUMENT_RESOLVER",
        blockers=(),
        warnings=(),
        to_dict=lambda: {
            "status": status,
            "selected_candidate_source_status": "SUPERSEDED_BY_REAL_INSTRUMENT_RESOLVER",
            "reason": "v36 refreshes the real instrument public source directly through v34.",
        },
    )


def _extract_ticket_display(ticket: dict[str, Any]) -> dict[str, Any]:
    real = ticket.get("selected_stock_fund_etf_real_instrument")
    if not isinstance(real, dict):
        real = {}

    return {
        "crypto_candidate": _crypto_candidate(ticket),
        "crypto_amount_eur": _crypto_amount(ticket),
        "stock_fund_etf_sleeve": str(ticket.get("selected_stock_fund_etf_sleeve") or ticket.get("selected_stock_fund_etf_candidate") or "") or None,
        "stock_fund_etf_amount_eur": _amount_or_none(real.get("amount_eur") or ticket.get("selected_stock_fund_etf_amount_eur")),
        "real_instrument_id": str(real.get("instrument_id") or ticket.get("selected_stock_fund_etf_real_instrument_id") or "") or None,
        "real_instrument_name": str(real.get("name") or "") or None,
        "real_instrument_isin": str(real.get("isin") or "") or None,
        "real_instrument_symbol": str(real.get("symbol") or ticket.get("selected_stock_fund_etf_real_instrument_symbol") or "") or None,
        "real_instrument_provider": str(real.get("provider") or "") or None,
        "real_instrument_currency": str(real.get("currency") or "") or None,
        "real_instrument_source_as_of": str(real.get("source_as_of") or ticket.get("selected_stock_fund_etf_real_instrument_source_as_of") or "") or None,
        "real_instrument_source_age_days": int(real["source_age_days"]) if real.get("source_age_days") is not None else None,
        "real_instrument_close_price": _float_or_none(real.get("close_price")),
        "real_instrument_public_source_ready": str(real.get("public_source_status") or "") == "ETF_PUBLIC_SOURCE_READY",
    }


def build_autonomous_daily_refresh_action_brief_result(
    *,
    current_date: str | None = None,
    ticket_path: str | Path = DEFAULT_OUTPUT_PATH,
    instrument_universe_path: str | Path = DEFAULT_INSTRUMENT_UNIVERSE_PATH,
    resolution_path: str | Path = DEFAULT_OUTPUT_RESOLUTION_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    write_local_resolution: bool = True,
    write_ticket: bool = True,
    fetch_text: Callable[[str], str] = _default_fetch_text,
    resolver_builder: Callable[..., StockFundEtfSleeveToInstrumentResolverResult] = build_stock_fund_etf_sleeve_to_instrument_resolver_result,
    bridge_builder: Callable[..., SelectedStockFundEtfInstrumentTicketBridgeResult] = build_selected_stock_fund_etf_instrument_ticket_bridge_result,
) -> AutonomousDailyRefreshActionBriefResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")
    if max_age_days < 0:
        blockers.append("max_age_days must be non-negative.")

    resolved_ticket = _resolve_path(ticket_path, root)
    resolved_universe = _resolve_path(instrument_universe_path, root)
    resolved_resolution = _resolve_path(resolution_path, root)

    if not _is_under(resolved_ticket, root, "outputs"):
        blockers.append("approval ticket path must remain under outputs/.")
    if not _is_under(resolved_universe, root, "jarvis/local"):
        blockers.append("instrument universe path must remain under jarvis/local/.")
    if not _is_under(resolved_resolution, root, "jarvis/local"):
        blockers.append("selected instrument resolution path must remain under jarvis/local/.")

    resolver_result: Any = None
    bridge_result: Any = None

    if not blockers:
        resolver_result = resolver_builder(
            current_date=current_date_text,
            ticket_path=ticket_path,
            instrument_universe_path=instrument_universe_path,
            output_resolution_path=resolution_path,
            root=root,
            max_age_days=max_age_days,
            write_local_resolution=write_local_resolution,
            fetch_text=fetch_text,
            upstream_public_source_result=_ready_upstream_public_source_result(),
        )
        blockers.extend(getattr(resolver_result, "blockers", ()) or [])
        if "BLOCKED" in str(getattr(resolver_result, "status", "")):
            blockers.append("stock/fund/ETF real instrument refresh was blocked.")
        elif "READY" not in str(getattr(resolver_result, "status", "")):
            warnings.append("stock/fund/ETF real instrument refresh requires review.")

    if not blockers:
        bridge_result = bridge_builder(
            current_date=current_date_text,
            ticket_path=ticket_path,
            resolution_path=resolution_path,
            root=root,
            max_age_days=max_age_days,
            write_ticket=write_ticket,
        )
        blockers.extend(getattr(bridge_result, "blockers", ()) or [])
        if "BLOCKED" in str(getattr(bridge_result, "status", "")):
            blockers.append("stock/fund/ETF selected real instrument ticket bridge was blocked.")
        elif "READY" not in str(getattr(bridge_result, "status", "")):
            warnings.append("stock/fund/ETF selected real instrument ticket bridge requires review.")

    ticket = _load_json_if_exists(resolved_ticket)
    display = _extract_ticket_display(ticket)
    if not ticket:
        warnings.append("approval ticket could not be loaded after daily refresh.")
    if display["crypto_candidate"] is None:
        warnings.append("crypto candidate is missing from approval ticket.")
    if display["real_instrument_id"] is None:
        warnings.append("stock/fund/ETF real instrument is missing from approval ticket.")
    if not display["real_instrument_public_source_ready"]:
        warnings.append("stock/fund/ETF real instrument public source is not ready in approval ticket.")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        daily_status = DAILY_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        daily_status = DAILY_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        daily_status = DAILY_READY

    return AutonomousDailyRefreshActionBriefResult(
        status=status,
        daily_status=daily_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        ticket_path=str(resolved_ticket),
        instrument_universe_path=str(resolved_universe),
        resolution_path=str(resolved_resolution),
        resolver_ran=resolver_result is not None,
        bridge_ran=bridge_result is not None,
        local_resolution_written=bool(getattr(resolver_result, "instrument_resolution_written", False)),
        approval_ticket_written=bool(getattr(bridge_result, "ticket_written", False)),
        ticket_loaded_after_refresh=bool(ticket),
        crypto_candidate=display["crypto_candidate"],
        crypto_amount_eur=display["crypto_amount_eur"],
        stock_fund_etf_sleeve=display["stock_fund_etf_sleeve"],
        stock_fund_etf_amount_eur=display["stock_fund_etf_amount_eur"],
        real_instrument_id=display["real_instrument_id"],
        real_instrument_name=display["real_instrument_name"],
        real_instrument_isin=display["real_instrument_isin"],
        real_instrument_symbol=display["real_instrument_symbol"],
        real_instrument_provider=display["real_instrument_provider"],
        real_instrument_currency=display["real_instrument_currency"],
        real_instrument_source_as_of=display["real_instrument_source_as_of"],
        real_instrument_source_age_days=display["real_instrument_source_age_days"],
        real_instrument_close_price=display["real_instrument_close_price"],
        real_instrument_public_source_ready=display["real_instrument_public_source_ready"],
        recommendation_quality_current_data=not unique_blockers and not unique_warnings,
        resolver_result=resolver_result,
        bridge_result=bridge_result,
        allocation_mutation=False,
        approval_ticket_mutation=bool(getattr(bridge_result, "ticket_written", False)),
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


def _money(value: float | None) -> str:
    return f"EUR {value:,.2f}" if value is not None else "EUR unknown"


def format_autonomous_daily_refresh_action_brief(
    result: AutonomousDailyRefreshActionBriefResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Autonomous Daily Refresh Action Brief",
        f"status: {result.status}",
        f"daily status: {result.daily_status}",
        f"current date: {result.current_date}",
        f"ticket path: {result.ticket_path}",
        f"instrument universe path: {result.instrument_universe_path}",
        f"resolution path: {result.resolution_path}",
        f"resolver ran: {result.resolver_ran}",
        f"bridge ran: {result.bridge_ran}",
        f"local resolution written: {result.local_resolution_written}",
        f"approval ticket written: {result.approval_ticket_written}",
        f"ticket loaded after refresh: {result.ticket_loaded_after_refresh}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        "",
        "Clean manual action brief:",
        "Crypto lane:",
        f"- Candidate: {result.crypto_candidate or 'none'}",
        f"- Amount: {_money(result.crypto_amount_eur)}",
        "",
        "Stock/Fund/ETF lane:",
        f"- Sleeve: {result.stock_fund_etf_sleeve or 'none'}",
        f"- Real instrument: {result.real_instrument_name or 'none'}",
        f"- Symbol: {result.real_instrument_symbol or 'none'}",
        f"- ISIN: {result.real_instrument_isin or 'none'}",
        f"- Provider: {result.real_instrument_provider or 'none'}",
        f"- Currency: {result.real_instrument_currency or 'none'}",
        f"- Amount: {_money(result.stock_fund_etf_amount_eur)}",
        f"- Source as_of: {result.real_instrument_source_as_of or 'none'}",
        f"- Source age days: {result.real_instrument_source_age_days if result.real_instrument_source_age_days is not None else 'unknown'}",
        f"- Close price: {result.real_instrument_close_price if result.real_instrument_close_price is not None else 'none'}",
        f"- Public source ready: {result.real_instrument_public_source_ready}",
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
        "- final real-world buy remains manual outside J.A.R.V.I.S.",
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
    parser = argparse.ArgumentParser(description="Run autonomous safe daily refresh and clean manual action brief.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run autonomous daily refresh/action brief.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--ticket-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--instrument-universe-path", default=DEFAULT_INSTRUMENT_UNIVERSE_PATH)
    parser.add_argument("--resolution-path", default=DEFAULT_OUTPUT_RESOLUTION_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--no-write-local-resolution", action="store_true", help="Do not refresh the local selected instrument resolution.")
    parser.add_argument("--no-write-ticket", action="store_true", help="Do not refresh the approval ticket with the selected real instrument.")
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

    result = build_autonomous_daily_refresh_action_brief_result(
        current_date=args.current_date,
        ticket_path=args.ticket_path,
        instrument_universe_path=args.instrument_universe_path,
        resolution_path=args.resolution_path,
        max_age_days=args.max_age_days,
        write_local_resolution=not args.no_write_local_resolution,
        write_ticket=not args.no_write_ticket,
    )
    print(format_autonomous_daily_refresh_action_brief(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())