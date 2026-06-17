"""J.A.R.V.I.S. v35.0 selected stock/fund/ETF instrument ticket bridge.

v35 connects the v34 real-instrument resolution to the manual approval ticket.

It keeps the portfolio sleeve as the strategy category, but adds the real selected
ETF/fund instrument to the ticket so daily output can stop ending at an abstract
sleeve such as quality_etf.

The bridge writes the approval ticket only with --write-ticket.
"""

from __future__ import annotations

import argparse
import copy
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from .jarvis_v30_0_expanded_crypto_approval_ticket_refresh import DEFAULT_OUTPUT_PATH
from .jarvis_v34_0_stock_fund_etf_sleeve_to_instrument_resolver import (
    DEFAULT_OUTPUT_RESOLUTION_PATH,
    INSTRUMENT_SELECTED,
)

STATUS_READY = "JARVIS_V35_0_SELECTED_STOCK_FUND_ETF_INSTRUMENT_TICKET_BRIDGE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V35_0_SELECTED_STOCK_FUND_ETF_INSTRUMENT_TICKET_BRIDGE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V35_0_SELECTED_STOCK_FUND_ETF_INSTRUMENT_TICKET_BRIDGE_BLOCKED_SAFE"

BRIDGE_READY = "SELECTED_STOCK_FUND_ETF_INSTRUMENT_TICKET_BRIDGE_READY"
BRIDGE_REVIEW_REQUIRED = "SELECTED_STOCK_FUND_ETF_INSTRUMENT_TICKET_BRIDGE_REVIEW_REQUIRED"
BRIDGE_BLOCKED = "SELECTED_STOCK_FUND_ETF_INSTRUMENT_TICKET_BRIDGE_BLOCKED"

NEXT_STAGE = "daily_manual_action_brief_real_stock_fund_etf_instrument_display"


@dataclass(frozen=True)
class SelectedStockFundEtfInstrumentTicketBridgeResult:
    status: str
    bridge_status: str
    recommended_next_stage: str
    current_date: str
    ticket_path: str
    resolution_path: str
    ticket_loaded: bool
    resolution_loaded: bool
    ticket_written: bool
    selected_sleeve: str | None
    selected_sleeve_amount_eur: float
    selected_instrument_id: str | None
    selected_instrument_name: str | None
    selected_instrument_isin: str | None
    selected_instrument_ticker: str | None
    selected_instrument_provider: str | None
    selected_instrument_symbol: str | None
    selected_instrument_currency: str | None
    selected_instrument_source_as_of: str | None
    selected_instrument_close_price: float | None
    selected_instrument_source_url: str | None
    selected_instrument_public_source_ready: bool
    selected_instrument_age_days: int | None
    approval_ticket_now_has_real_instrument: bool
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
            "bridge_status": self.bridge_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "ticket_path": self.ticket_path,
            "resolution_path": self.resolution_path,
            "ticket_loaded": self.ticket_loaded,
            "resolution_loaded": self.resolution_loaded,
            "ticket_written": self.ticket_written,
            "selected_sleeve": self.selected_sleeve,
            "selected_sleeve_amount_eur": self.selected_sleeve_amount_eur,
            "selected_instrument_id": self.selected_instrument_id,
            "selected_instrument_name": self.selected_instrument_name,
            "selected_instrument_isin": self.selected_instrument_isin,
            "selected_instrument_ticker": self.selected_instrument_ticker,
            "selected_instrument_provider": self.selected_instrument_provider,
            "selected_instrument_symbol": self.selected_instrument_symbol,
            "selected_instrument_currency": self.selected_instrument_currency,
            "selected_instrument_source_as_of": self.selected_instrument_source_as_of,
            "selected_instrument_close_price": self.selected_instrument_close_price,
            "selected_instrument_source_url": self.selected_instrument_source_url,
            "selected_instrument_public_source_ready": self.selected_instrument_public_source_ready,
            "selected_instrument_age_days": self.selected_instrument_age_days,
            "approval_ticket_now_has_real_instrument": self.approval_ticket_now_has_real_instrument,
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


def _amount(value: Any) -> float:
    return round(float(value or 0.0), 2)


def _age_days(source_as_of: str | None, current_date: str) -> int | None:
    source_date = _parse_date(source_as_of)
    current = _parse_date(current_date)
    if source_date is None or current is None:
        return None
    return (current - source_date).days


def _resolution_selected_instrument(resolution: dict[str, Any]) -> dict[str, Any]:
    selected = resolution.get("selected_instrument")
    if isinstance(selected, dict):
        return selected
    return {}


def _instrument_public_ready(instrument: dict[str, Any], current_date: str, max_age_days: int) -> tuple[bool, int | None, tuple[str, ...]]:
    warnings: list[str] = []
    if not instrument:
        warnings.append("selected stock/fund/ETF instrument resolution is missing.")
        return False, None, tuple(warnings)

    if not bool(instrument.get("selected")):
        warnings.append("resolved stock/fund/ETF instrument is not marked selected.")
    if str(instrument.get("decision_status") or "") != INSTRUMENT_SELECTED:
        warnings.append("resolved stock/fund/ETF instrument decision status is not SELECTED_REAL_INSTRUMENT_FOR_SLEEVE.")
    if str(instrument.get("public_source_status") or "") != "ETF_PUBLIC_SOURCE_READY":
        warnings.append("resolved stock/fund/ETF instrument public source is not ready.")

    source_as_of = str(instrument.get("source_as_of") or "")
    age = _age_days(source_as_of, current_date)
    if age is None:
        warnings.append("resolved stock/fund/ETF instrument has no valid source_as_of date.")
    elif age < 0:
        warnings.append("resolved stock/fund/ETF instrument source_as_of is in the future.")
    elif age > max_age_days:
        warnings.append(f"resolved stock/fund/ETF instrument source data is {age} days old; refresh required.")

    required = ("instrument_id", "name", "isin", "ticker", "provider", "symbol", "currency", "close_price")
    for key in required:
        if instrument.get(key) in (None, ""):
            warnings.append(f"resolved stock/fund/ETF instrument missing required field {key}.")

    return len(warnings) == 0, age, tuple(warnings)


def _ticket_has_real_instrument(ticket: dict[str, Any], instrument: dict[str, Any]) -> bool:
    existing = ticket.get("selected_stock_fund_etf_real_instrument")
    if not isinstance(existing, dict):
        return False
    return str(existing.get("instrument_id") or "") == str(instrument.get("instrument_id") or "")


def _apply_real_instrument_to_ticket(
    *,
    ticket: dict[str, Any],
    resolution: dict[str, Any],
    instrument: dict[str, Any],
    current_date: str,
    age_days: int | None,
) -> dict[str, Any]:
    updated = copy.deepcopy(ticket)
    selected_sleeve = str(resolution.get("selected_sleeve") or ticket.get("selected_stock_fund_etf_candidate") or "")
    selected_amount = _amount(resolution.get("selected_sleeve_amount_eur") or ticket.get("selected_stock_fund_etf_amount_eur"))

    real_instrument = {
        "sleeve": selected_sleeve,
        "amount_eur": selected_amount,
        "instrument_id": instrument.get("instrument_id"),
        "name": instrument.get("name"),
        "isin": instrument.get("isin"),
        "ticker": instrument.get("ticker"),
        "exchange": instrument.get("exchange"),
        "currency": instrument.get("currency"),
        "provider": instrument.get("provider"),
        "symbol": instrument.get("symbol"),
        "source_as_of": instrument.get("source_as_of"),
        "source_url": instrument.get("source_url"),
        "close_price": instrument.get("close_price"),
        "expense_ratio": instrument.get("expense_ratio"),
        "priority_score": instrument.get("priority_score"),
        "public_source_status": instrument.get("public_source_status"),
        "decision_status": instrument.get("decision_status"),
        "source_age_days": age_days,
        "bridged_at": current_date,
        "final_real_world_buy_remains_manual": True,
    }

    updated["selected_stock_fund_etf_sleeve"] = selected_sleeve
    updated["selected_stock_fund_etf_real_instrument"] = real_instrument
    updated["selected_stock_fund_etf_real_instrument_id"] = instrument.get("instrument_id")
    updated["selected_stock_fund_etf_real_instrument_symbol"] = instrument.get("symbol")
    updated["selected_stock_fund_etf_real_instrument_source_as_of"] = instrument.get("source_as_of")
    updated["selected_stock_fund_etf_candidate_display"] = f"{selected_sleeve} -> {instrument.get('symbol') or instrument.get('instrument_id')}"
    updated["stock_fund_etf_lane_mode"] = "sleeve_resolved_to_real_instrument"
    updated["stock_fund_etf_source_metadata"] = {
        "as_of": instrument.get("source_as_of"),
        "updated_at": current_date,
        "source_as_of": instrument.get("source_as_of"),
        "price_as_of": instrument.get("source_as_of"),
        "source_url": instrument.get("source_url"),
        "provider": instrument.get("provider"),
        "symbol": instrument.get("symbol"),
        "metadata_status": "ETF_SOURCE_METADATA_READY",
    }

    safety = updated.setdefault("safety", {})
    if isinstance(safety, dict):
        safety["allocation_mutation"] = False
        safety["portfolio_state_mutation"] = False
        safety["buy_request_created"] = False
        safety["broker_connection"] = False
        safety["credentials_used"] = False
        safety["private_account_data_ingested"] = False
        safety["orders_created"] = False
        safety["trades_executed"] = False

    updated["buy_request_created"] = False
    updated["trades_executed"] = False
    return updated


def build_selected_stock_fund_etf_instrument_ticket_bridge_result(
    *,
    current_date: str | None = None,
    ticket_path: str | Path = DEFAULT_OUTPUT_PATH,
    resolution_path: str | Path = DEFAULT_OUTPUT_RESOLUTION_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    write_ticket: bool = False,
) -> SelectedStockFundEtfInstrumentTicketBridgeResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")
    if max_age_days < 0:
        blockers.append("max_age_days must be non-negative.")

    resolved_ticket = _resolve_path(ticket_path, root)
    resolved_resolution = _resolve_path(resolution_path, root)

    if not _is_under(resolved_ticket, root, "outputs"):
        blockers.append("approval ticket path must remain under outputs/.")
    if not _is_under(resolved_resolution, root, "jarvis/local"):
        blockers.append("selected instrument resolution path must remain under jarvis/local/.")

    ticket: dict[str, Any] = {}
    resolution: dict[str, Any] = {}
    ticket_loaded = False
    resolution_loaded = False

    if not blockers:
        if resolved_ticket.exists():
            ticket = _load_json(resolved_ticket)
            ticket_loaded = True
        else:
            warnings.append("approval ticket is missing; selected real ETF instrument cannot be bridged.")

        if resolved_resolution.exists():
            resolution = _load_json(resolved_resolution)
            resolution_loaded = True
        else:
            warnings.append("selected stock/fund/ETF instrument resolution is missing; run v34 with --write-local-resolution first.")

    instrument = _resolution_selected_instrument(resolution)
    selected_sleeve = str(resolution.get("selected_sleeve") or ticket.get("selected_stock_fund_etf_candidate") or "") if (resolution or ticket) else ""
    selected_amount = _amount(resolution.get("selected_sleeve_amount_eur") or ticket.get("selected_stock_fund_etf_amount_eur")) if (resolution or ticket) else 0.0

    instrument_ready, age_days, instrument_warnings = _instrument_public_ready(instrument, current_date_text, max_age_days)
    warnings.extend(instrument_warnings)

    if ticket_loaded and selected_sleeve and ticket.get("selected_stock_fund_etf_candidate") != selected_sleeve:
        warnings.append("approval ticket selected ETF sleeve does not match selected instrument resolution sleeve.")

    has_real_instrument = bool(ticket_loaded and instrument and _ticket_has_real_instrument(ticket, instrument))
    ticket_written = False
    if write_ticket and not blockers and ticket_loaded and resolution_loaded and instrument_ready:
        updated_ticket = _apply_real_instrument_to_ticket(
            ticket=ticket,
            resolution=resolution,
            instrument=instrument,
            current_date=current_date_text,
            age_days=age_days,
        )
        _write_json(resolved_ticket, updated_ticket)
        ticket_written = True
        has_real_instrument = True
    elif write_ticket and not instrument_ready:
        warnings.append("approval ticket was not written because selected real ETF/fund instrument is not fresh and complete.")
    elif not write_ticket and instrument_ready and not has_real_instrument:
        warnings.append("selected real ETF/fund instrument is fresh, but approval ticket write was not requested.")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        bridge_status = BRIDGE_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        bridge_status = BRIDGE_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        bridge_status = BRIDGE_READY

    return SelectedStockFundEtfInstrumentTicketBridgeResult(
        status=status,
        bridge_status=bridge_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        ticket_path=str(resolved_ticket),
        resolution_path=str(resolved_resolution),
        ticket_loaded=ticket_loaded,
        resolution_loaded=resolution_loaded,
        ticket_written=ticket_written,
        selected_sleeve=selected_sleeve or None,
        selected_sleeve_amount_eur=selected_amount,
        selected_instrument_id=str(instrument.get("instrument_id") or "") or None,
        selected_instrument_name=str(instrument.get("name") or "") or None,
        selected_instrument_isin=str(instrument.get("isin") or "") or None,
        selected_instrument_ticker=str(instrument.get("ticker") or "") or None,
        selected_instrument_provider=str(instrument.get("provider") or "") or None,
        selected_instrument_symbol=str(instrument.get("symbol") or "") or None,
        selected_instrument_currency=str(instrument.get("currency") or "") or None,
        selected_instrument_source_as_of=str(instrument.get("source_as_of") or "") or None,
        selected_instrument_close_price=float(instrument["close_price"]) if instrument.get("close_price") is not None else None,
        selected_instrument_source_url=str(instrument.get("source_url") or "") or None,
        selected_instrument_public_source_ready=instrument_ready,
        selected_instrument_age_days=age_days,
        approval_ticket_now_has_real_instrument=has_real_instrument,
        recommendation_quality_current_data=instrument_ready and has_real_instrument and not unique_blockers and not unique_warnings,
        allocation_mutation=False,
        approval_ticket_mutation=ticket_written,
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


def format_selected_stock_fund_etf_instrument_ticket_bridge(
    result: SelectedStockFundEtfInstrumentTicketBridgeResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Selected Stock/Fund/ETF Instrument Ticket Bridge",
        f"status: {result.status}",
        f"bridge status: {result.bridge_status}",
        f"current date: {result.current_date}",
        f"ticket path: {result.ticket_path}",
        f"resolution path: {result.resolution_path}",
        f"ticket loaded: {result.ticket_loaded}",
        f"resolution loaded: {result.resolution_loaded}",
        f"ticket written: {result.ticket_written}",
        f"selected sleeve: {result.selected_sleeve or 'none'}",
        f"selected sleeve amount: EUR {result.selected_sleeve_amount_eur:,.2f}",
        f"selected real instrument id: {result.selected_instrument_id or 'none'}",
        f"selected real instrument name: {result.selected_instrument_name or 'none'}",
        f"selected real instrument ISIN: {result.selected_instrument_isin or 'none'}",
        f"selected real instrument ticker: {result.selected_instrument_ticker or 'none'}",
        f"selected real instrument provider: {result.selected_instrument_provider or 'none'}",
        f"selected real instrument symbol: {result.selected_instrument_symbol or 'none'}",
        f"selected real instrument currency: {result.selected_instrument_currency or 'none'}",
        f"selected real instrument source as_of: {result.selected_instrument_source_as_of or 'none'}",
        f"selected real instrument age days: {result.selected_instrument_age_days if result.selected_instrument_age_days is not None else 'unknown'}",
        f"selected real instrument close price: {result.selected_instrument_close_price if result.selected_instrument_close_price is not None else 'none'}",
        f"selected real instrument source url: {result.selected_instrument_source_url or 'none'}",
        f"selected real instrument public source ready: {result.selected_instrument_public_source_ready}",
        f"approval ticket now has real instrument: {result.approval_ticket_now_has_real_instrument}",
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
        "Manual stock/fund/ETF lane display:",
        f"- Sleeve: {result.selected_sleeve or 'none'}",
        f"- Real instrument: {result.selected_instrument_name or 'none'}",
        f"- Symbol: {result.selected_instrument_symbol or 'none'}",
        f"- ISIN: {result.selected_instrument_isin or 'none'}",
        f"- Amount: EUR {result.selected_sleeve_amount_eur:,.2f}",
        "- Final real-world buy remains manual outside J.A.R.V.I.S.",
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
    parser = argparse.ArgumentParser(description="Bridge selected real stock/fund/ETF instrument into the manual approval ticket.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run selected stock/fund/ETF instrument ticket bridge.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--ticket-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--resolution-path", default=DEFAULT_OUTPUT_RESOLUTION_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--write-ticket", action="store_true", help="Write selected real stock/fund/ETF instrument into approval ticket.")
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

    result = build_selected_stock_fund_etf_instrument_ticket_bridge_result(
        current_date=args.current_date,
        ticket_path=args.ticket_path,
        resolution_path=args.resolution_path,
        max_age_days=args.max_age_days,
        write_ticket=args.write_ticket,
    )
    print(format_selected_stock_fund_etf_instrument_ticket_bridge(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())