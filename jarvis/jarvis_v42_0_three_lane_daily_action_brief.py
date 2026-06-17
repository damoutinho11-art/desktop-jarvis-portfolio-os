"""J.A.R.V.I.S. v42.0 three-lane daily action brief.

v42 is the first clean three-lane daily operator:

- crypto lane refreshed through the existing approval-ticket flow
- ETF/fund real instrument lane refreshed through the existing approval-ticket flow
- individual stock lane bootstrapped/ranked/bridged as review-only

It prints one concise manual action brief and still cannot execute trades.
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
)
from .jarvis_v39_0_individual_stock_public_ranker import DEFAULT_RANKED_STOCKS_PATH
from .jarvis_v41_0_ranked_individual_stock_candidate_ticket_bridge import (
    DEFAULT_APPROVAL_TICKET_PATH,
    RankedIndividualStockCandidateTicketBridgeResult,
    build_ranked_individual_stock_candidate_ticket_bridge_result,
)

STATUS_READY = "JARVIS_V42_0_THREE_LANE_DAILY_ACTION_BRIEF_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V42_0_THREE_LANE_DAILY_ACTION_BRIEF_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V42_0_THREE_LANE_DAILY_ACTION_BRIEF_BLOCKED_SAFE"

DAILY_READY = "THREE_LANE_DAILY_ACTION_BRIEF_READY"
DAILY_REVIEW_REQUIRED = "THREE_LANE_DAILY_ACTION_BRIEF_REVIEW_REQUIRED"
DAILY_BLOCKED = "THREE_LANE_DAILY_ACTION_BRIEF_BLOCKED"

NEXT_STAGE = "manual_amount_router_and_three_lane_ticket_review_ui"


@dataclass(frozen=True)
class ThreeLaneDailyActionBriefResult:
    status: str
    daily_status: str
    recommended_next_stage: str
    current_date: str
    approval_ticket_path: str
    stock_universe_path: str
    stock_signals_path: str
    ranked_stocks_path: str
    bridge_ran: bool
    crypto_candidate: str | None
    crypto_amount_eur: float | None
    etf_sleeve: str | None
    etf_name: str | None
    etf_symbol: str | None
    etf_isin: str | None
    etf_amount_eur: float | None
    etf_public_source_ready: bool | None
    stock_candidate_id: str | None
    stock_name: str | None
    stock_symbol: str | None
    stock_amount_eur: float | None
    stock_manual_amount_required: bool | None
    stock_approved_for_purchase: bool | None
    stock_decision_status: str | None
    stock_source_as_of: str | None
    stock_close_price: float | None
    stock_currency: str | None
    stock_ticket_written: bool
    upstream_stock_bridge_result: Any
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
            "daily_status": self.daily_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "approval_ticket_path": self.approval_ticket_path,
            "stock_universe_path": self.stock_universe_path,
            "stock_signals_path": self.stock_signals_path,
            "ranked_stocks_path": self.ranked_stocks_path,
            "bridge_ran": self.bridge_ran,
            "crypto_candidate": self.crypto_candidate,
            "crypto_amount_eur": self.crypto_amount_eur,
            "etf_sleeve": self.etf_sleeve,
            "etf_name": self.etf_name,
            "etf_symbol": self.etf_symbol,
            "etf_isin": self.etf_isin,
            "etf_amount_eur": self.etf_amount_eur,
            "etf_public_source_ready": self.etf_public_source_ready,
            "stock_candidate_id": self.stock_candidate_id,
            "stock_name": self.stock_name,
            "stock_symbol": self.stock_symbol,
            "stock_amount_eur": self.stock_amount_eur,
            "stock_manual_amount_required": self.stock_manual_amount_required,
            "stock_approved_for_purchase": self.stock_approved_for_purchase,
            "stock_decision_status": self.stock_decision_status,
            "stock_source_as_of": self.stock_source_as_of,
            "stock_close_price": self.stock_close_price,
            "stock_currency": self.stock_currency,
            "stock_ticket_written": self.stock_ticket_written,
            "upstream_stock_bridge_result": self.upstream_stock_bridge_result.to_dict()
            if hasattr(self.upstream_stock_bridge_result, "to_dict")
            else dict(getattr(self.upstream_stock_bridge_result, "__dict__", {})),
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


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _number(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _field(payload: dict[str, Any], *names: str) -> Any:
    for name in names:
        if name in payload:
            return payload.get(name)
    return None


def _ticket_stock(ticket: dict[str, Any]) -> dict[str, Any]:
    stock = ticket.get("selected_individual_stock_candidate")
    return dict(stock) if isinstance(stock, dict) else {}


def _ticket_etf(ticket: dict[str, Any]) -> dict[str, Any]:
    etf = ticket.get("selected_stock_fund_etf_real_instrument")
    return dict(etf) if isinstance(etf, dict) else {}


def _ticket_etf_metadata(ticket: dict[str, Any]) -> dict[str, Any]:
    metadata = ticket.get("stock_fund_etf_source_metadata")
    return dict(metadata) if isinstance(metadata, dict) else {}


def _bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "yes", "ready", "source_ready", "public_source_ready"}:
            return True
        if normalized in {"false", "no", "not_ready", "missing", "stale", "failed"}:
            return False
    return None


def _etf_public_source_ready(ticket: dict[str, Any], etf: dict[str, Any], metadata: dict[str, Any]) -> bool | None:
    for source in (metadata, etf, ticket):
        for key in (
            "public_source_ready",
            "real_instrument_public_source_ready",
            "selected_stock_fund_etf_real_instrument_public_source_ready",
            "stock_fund_etf_real_instrument_public_source_ready",
            "source_ready",
        ):
            parsed = _bool_or_none(source.get(key))
            if parsed is not None:
                return parsed

    for source in (metadata, etf, ticket):
        for key in ("source_status", "metadata_status", "real_instrument_source_status"):
            status = str(source.get(key) or "").strip().upper()
            if status in {
                "ETF_SOURCE_METADATA_READY",
                "STOCK_FUND_ETF_SOURCE_METADATA_READY",
                "STOCK_FUND_ETF_PUBLIC_SOURCE_READY",
                "ETF_PUBLIC_SOURCE_READY",
                "SOURCE_READY",
            }:
                return True
            if any(fragment in status for fragment in ("FAILED", "MISSING", "STALE", "UNSUPPORTED", "INVALID")):
                return False

    return None


def build_three_lane_daily_action_brief_result(
    *,
    current_date: str | None = None,
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    stock_universe_path: str | Path = DEFAULT_STOCK_UNIVERSE_PATH,
    stock_signals_path: str | Path = DEFAULT_STOCK_SIGNALS_PATH,
    ranked_stocks_path: str | Path = DEFAULT_RANKED_STOCKS_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    run_stock_bridge: bool = True,
    write_stock_ticket: bool = True,
    bootstrap_stock_universe: bool = True,
    write_stock_signals: bool = True,
    write_ranked_stocks: bool = True,
    bridge_builder: Callable[..., RankedIndividualStockCandidateTicketBridgeResult] = build_ranked_individual_stock_candidate_ticket_bridge_result,
    upstream_stock_bridge_result: RankedIndividualStockCandidateTicketBridgeResult | None = None,
) -> ThreeLaneDailyActionBriefResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")

    resolved_ticket = _resolve_path(approval_ticket_path, root)
    resolved_universe = _resolve_path(stock_universe_path, root)
    resolved_signals = _resolve_path(stock_signals_path, root)
    resolved_ranked = _resolve_path(ranked_stocks_path, root)

    if not _is_under(resolved_ticket, root, "outputs"):
        blockers.append("approval ticket path must remain under outputs/.")
    for label, path in (
        ("stock universe path", resolved_universe),
        ("stock signals path", resolved_signals),
        ("ranked stocks path", resolved_ranked),
    ):
        if not _is_under(path, root, "jarvis/local"):
            blockers.append(f"{label} must remain under jarvis/local/.")

    bridge_result = upstream_stock_bridge_result
    bridge_ran = bridge_result is not None
    if run_stock_bridge and bridge_result is None and not blockers:
        bridge_result = bridge_builder(
            current_date=current_date_text,
            approval_ticket_path=approval_ticket_path,
            stock_universe_path=stock_universe_path,
            stock_signals_path=stock_signals_path,
            ranked_stocks_path=ranked_stocks_path,
            root=root,
            max_age_days=max_age_days,
            bootstrap_stock_universe=bootstrap_stock_universe,
            write_stock_signals=write_stock_signals,
            write_ranked_stocks=write_ranked_stocks,
            write_stock_ticket=write_stock_ticket,
        )
        bridge_ran = True

    if bridge_result is not None:
        blockers.extend(getattr(bridge_result, "blockers", ()) or [])
        warnings.extend(getattr(bridge_result, "warnings", ()) or [])
        bridge_status = str(getattr(bridge_result, "status", ""))
        if "BLOCKED" in bridge_status:
            blockers.append("ranked individual stock candidate ticket bridge was blocked.")
        elif "READY" not in bridge_status or "REVIEW_REQUIRED" in bridge_status:
            warnings.append("ranked individual stock candidate ticket bridge requires review.")
    elif not run_stock_bridge and not blockers:
        warnings.append("stock bridge was not run.")

    ticket: dict[str, Any] = {}
    if not blockers:
        if not resolved_ticket.exists():
            blockers.append(f"approval ticket path does not exist: {resolved_ticket}")
        else:
            try:
                ticket = _read_json(resolved_ticket)
            except json.JSONDecodeError as exc:
                blockers.append(f"approval ticket is not valid JSON: {exc}")

    etf = _ticket_etf(ticket)
    stock = _ticket_stock(ticket)
    etf_metadata = _ticket_etf_metadata(ticket)

    crypto_candidate = ticket.get("selected_crypto_candidate")
    crypto_amount = _number(ticket.get("selected_crypto_amount_eur"))
    if not crypto_candidate:
        warnings.append("crypto lane is missing from approval ticket.")
    if crypto_amount is None:
        warnings.append("crypto amount is missing from approval ticket.")

    etf_symbol = _field(etf, "symbol", "real_instrument_symbol")
    etf_isin = _field(etf, "isin", "real_instrument_isin")
    etf_amount = _number(etf.get("amount_eur"))
    if not etf_symbol:
        warnings.append("ETF/fund real instrument symbol is missing from approval ticket.")
    if etf_amount is None:
        warnings.append("ETF/fund amount is missing from approval ticket.")

    stock_symbol = stock.get("symbol")
    stock_decision_status = stock.get("decision_status")
    stock_manual_amount_required = stock.get("manual_amount_required")
    stock_approved = stock.get("approved_for_purchase")
    stock_amount = _number(stock.get("amount_eur"))
    if not stock_symbol:
        warnings.append("individual stock candidate is missing from approval ticket.")
    if stock_manual_amount_required is not True:
        warnings.append("individual stock candidate must require manual amount.")
    if stock_approved is not False:
        blockers.append("individual stock candidate must not be approved for purchase.")
    if stock_amount is not None:
        blockers.append("individual stock candidate amount_eur must remain null until manual amount routing exists.")

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

    return ThreeLaneDailyActionBriefResult(
        status=status,
        daily_status=daily_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        approval_ticket_path=str(resolved_ticket),
        stock_universe_path=str(resolved_universe),
        stock_signals_path=str(resolved_signals),
        ranked_stocks_path=str(resolved_ranked),
        bridge_ran=bridge_ran,
        crypto_candidate=str(crypto_candidate) if crypto_candidate else None,
        crypto_amount_eur=crypto_amount,
        etf_sleeve=ticket.get("selected_stock_fund_etf_sleeve"),
        etf_name=_field(etf, "name", "real_instrument_name"),
        etf_symbol=str(etf_symbol) if etf_symbol else None,
        etf_isin=str(etf_isin) if etf_isin else None,
        etf_amount_eur=etf_amount,
        etf_public_source_ready=_etf_public_source_ready(ticket, etf, etf_metadata),
        stock_candidate_id=stock.get("stock_id"),
        stock_name=stock.get("name"),
        stock_symbol=stock_symbol,
        stock_amount_eur=stock_amount,
        stock_manual_amount_required=stock_manual_amount_required,
        stock_approved_for_purchase=stock_approved,
        stock_decision_status=stock_decision_status,
        stock_source_as_of=stock.get("source_as_of"),
        stock_close_price=_number(stock.get("close_price")),
        stock_currency=stock.get("currency"),
        stock_ticket_written=bool(getattr(bridge_result, "stock_ticket_written", False)),
        upstream_stock_bridge_result=bridge_result,
        recommendation_quality_current_data=not unique_blockers and not unique_warnings,
        allocation_mutation=False,
        approval_ticket_mutation=bool(getattr(bridge_result, "approval_ticket_mutation", False)),
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


def format_three_lane_daily_action_brief(result: ThreeLaneDailyActionBriefResult) -> str:
    lines = [
        "J.A.R.V.I.S. Three-Lane Daily Action Brief",
        f"status: {result.status}",
        f"daily status: {result.daily_status}",
        f"current date: {result.current_date}",
        f"approval ticket path: {result.approval_ticket_path}",
        f"stock bridge ran: {result.bridge_ran}",
        f"stock ticket written: {result.stock_ticket_written}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        "",
        "Clean manual action brief:",
        "Crypto lane:",
        f"- Candidate: {result.crypto_candidate or 'none'}",
        f"- Amount: EUR {result.crypto_amount_eur:,.2f}" if result.crypto_amount_eur is not None else "- Amount: none",
        "",
        "Stock/Fund/ETF lane:",
        f"- Sleeve: {result.etf_sleeve or 'none'}",
        f"- Real instrument: {result.etf_name or 'none'}",
        f"- Symbol: {result.etf_symbol or 'none'}",
        f"- ISIN: {result.etf_isin or 'none'}",
        f"- Amount: EUR {result.etf_amount_eur:,.2f}" if result.etf_amount_eur is not None else "- Amount: none",
        f"- Public source ready: {result.etf_public_source_ready}",
        "",
        "Individual stock lane:",
        f"- Candidate: {result.stock_candidate_id or 'none'}",
        f"- Name: {result.stock_name or 'none'}",
        f"- Symbol: {result.stock_symbol or 'none'}",
        f"- Last close: {result.stock_close_price:,.6f} {result.stock_currency or ''}".rstrip()
        if result.stock_close_price is not None
        else "- Last close: none",
        f"- Source as_of: {result.stock_source_as_of or 'none'}",
        f"- Amount: manual amount required; not assigned by J.A.R.V.I.S."
        if result.stock_manual_amount_required is True
        else "- Amount: none",
        f"- Decision: {result.stock_decision_status or 'none'}",
        f"- Approved for purchase: {result.stock_approved_for_purchase}",
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
    parser = argparse.ArgumentParser(description="Run the safe three-lane daily action brief.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run three-lane daily action brief.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--approval-ticket-path", default=DEFAULT_APPROVAL_TICKET_PATH)
    parser.add_argument("--stock-universe-path", default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--stock-signals-path", default=DEFAULT_STOCK_SIGNALS_PATH)
    parser.add_argument("--ranked-stocks-path", default=DEFAULT_RANKED_STOCKS_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--skip-stock-bridge", action="store_true", help="Do not run the stock bridge; review-only diagnostic mode.")
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

    result = build_three_lane_daily_action_brief_result(
        current_date=args.current_date,
        approval_ticket_path=args.approval_ticket_path,
        stock_universe_path=args.stock_universe_path,
        stock_signals_path=args.stock_signals_path,
        ranked_stocks_path=args.ranked_stocks_path,
        max_age_days=args.max_age_days,
        run_stock_bridge=not args.skip_stock_bridge,
        write_stock_ticket=not args.skip_stock_bridge,
        bootstrap_stock_universe=not args.skip_stock_bridge,
        write_stock_signals=not args.skip_stock_bridge,
        write_ranked_stocks=not args.skip_stock_bridge,
    )
    print(format_three_lane_daily_action_brief(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())