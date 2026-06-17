"""J.A.R.V.I.S. v31.0 approval ticket consumption closeout.

v31 is a read-only daily operator layer that consumes the refreshed local approval
ticket and prints one clean manual action brief.

It does not refresh/write the ticket, mutate portfolio state, create buy
requests, connect to brokers, create orders, or execute trades.
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
from .jarvis_v30_0_expanded_crypto_approval_ticket_refresh import (
    DEFAULT_OUTPUT_PATH,
    ExpandedCryptoApprovalTicketRefreshResult,
    build_expanded_crypto_approval_ticket_refresh_result,
)

STATUS_READY = "JARVIS_V31_0_APPROVAL_TICKET_CONSUMPTION_CLOSEOUT_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V31_0_APPROVAL_TICKET_CONSUMPTION_CLOSEOUT_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V31_0_APPROVAL_TICKET_CONSUMPTION_CLOSEOUT_BLOCKED_SAFE"

CLOSEOUT_READY = "APPROVAL_TICKET_CONSUMPTION_CLOSEOUT_READY"
CLOSEOUT_REVIEW_REQUIRED = "APPROVAL_TICKET_CONSUMPTION_CLOSEOUT_REVIEW_REQUIRED"
CLOSEOUT_BLOCKED = "APPROVAL_TICKET_CONSUMPTION_CLOSEOUT_BLOCKED"

NEXT_STAGE = "stock_fund_etf_data_freshness_engine"


@dataclass(frozen=True)
class ApprovalTicketConsumptionCloseoutResult:
    status: str
    closeout_status: str
    recommended_next_stage: str
    current_date: str
    ticket_path: str
    ticket_loaded: bool
    ticket_matches_current_preview: bool
    ticket_has_ambiguous_nested_source_bridge_result: bool
    selected_crypto_candidate: str | None
    selected_crypto_amount_eur: float
    selected_stock_fund_etf_candidate: str | None
    selected_stock_fund_etf_amount_eur: float
    approval_status: str
    ticket_as_of: str
    ticket_generated_at: str
    manual_approval_required: bool
    recommendation_quality_current_data: bool
    portfolio_data_stale_review_required: bool
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
            "closeout_status": self.closeout_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "ticket_path": self.ticket_path,
            "ticket_loaded": self.ticket_loaded,
            "ticket_matches_current_preview": self.ticket_matches_current_preview,
            "ticket_has_ambiguous_nested_source_bridge_result": self.ticket_has_ambiguous_nested_source_bridge_result,
            "selected_crypto_candidate": self.selected_crypto_candidate,
            "selected_crypto_amount_eur": self.selected_crypto_amount_eur,
            "selected_stock_fund_etf_candidate": self.selected_stock_fund_etf_candidate,
            "selected_stock_fund_etf_amount_eur": self.selected_stock_fund_etf_amount_eur,
            "approval_status": self.approval_status,
            "ticket_as_of": self.ticket_as_of,
            "ticket_generated_at": self.ticket_generated_at,
            "manual_approval_required": self.manual_approval_required,
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "portfolio_data_stale_review_required": self.portfolio_data_stale_review_required,
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


def _dedupe(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _today_iso() -> str:
    return date.today().isoformat()


def _resolve_ticket_path(path: str | Path, root: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return Path(root) / candidate


def _is_under_outputs(path: Path, root: str | Path) -> bool:
    resolved = path.resolve()
    outputs_root = (Path(root) / "outputs").resolve()
    try:
        resolved.relative_to(outputs_root)
        return True
    except ValueError:
        return False


def _load_ticket(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _preview_value(preview: Any, key: str, default: Any = None) -> Any:
    return getattr(preview, key, default)


def _amount(value: Any) -> float:
    return round(float(value or 0.0), 2)


def _ticket_matches_preview(ticket: dict[str, Any], preview: Any) -> bool:
    expected_pairs = (
        ("selected_crypto_candidate", _preview_value(preview, "selected_crypto_candidate")),
        ("selected_stock_fund_etf_candidate", _preview_value(preview, "selected_stock_fund_etf_candidate")),
    )
    for key, expected in expected_pairs:
        if str(ticket.get(key) or "") != str(expected or ""):
            return False

    amount_pairs = (
        ("selected_crypto_amount_eur", _preview_value(preview, "selected_crypto_amount_eur", 0.0)),
        ("selected_stock_fund_etf_amount_eur", _preview_value(preview, "selected_stock_fund_etf_amount_eur", 0.0)),
    )
    for key, expected in amount_pairs:
        if _amount(ticket.get(key)) != _amount(expected):
            return False

    if str(ticket.get("allocation_basis_as_of") or "") != str(_preview_value(preview, "allocation_basis_as_of", "")):
        return False

    if str(ticket.get("generated_at") or "") != str(_preview_value(preview, "ticket_generated_at", "")):
        return False

    return True


def _validate_ticket_safety(ticket: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if ticket.get("source_bridge_result") is not None:
        blockers.append("approval ticket still contains ambiguous nested source_bridge_result.")
    if not bool(ticket.get("manual_approval_required")):
        blockers.append("approval ticket must require manual approval.")
    if not bool(ticket.get("final_user_buy_action_required")):
        blockers.append("approval ticket must require final user buy action.")
    if bool(ticket.get("buy_request_created")):
        blockers.append("approval ticket must not create a buy request.")
    if not bool(ticket.get("broker_connection_forbidden")):
        blockers.append("approval ticket must forbid broker connection.")
    if not bool(ticket.get("credentials_forbidden")):
        blockers.append("approval ticket must forbid credentials.")
    if not bool(ticket.get("private_account_data_ingestion_forbidden")):
        blockers.append("approval ticket must forbid private account data ingestion.")
    if not bool(ticket.get("order_creation_forbidden")):
        blockers.append("approval ticket must forbid order creation.")
    if bool(ticket.get("trades_executed")):
        blockers.append("approval ticket must not execute trades.")
    return blockers


def build_approval_ticket_consumption_closeout_result(
    *,
    current_date: str | None = None,
    ticket_path: str | Path = DEFAULT_OUTPUT_PATH,
    root: str | Path = ".",
    preview_result: ExpandedCryptoApprovalTicketRefreshResult | None = None,
    preview_builder: Callable[..., ExpandedCryptoApprovalTicketRefreshResult] = build_expanded_crypto_approval_ticket_refresh_result,
    write_local_signals: bool = False,
) -> ApprovalTicketConsumptionCloseoutResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")

    resolved_ticket = _resolve_ticket_path(ticket_path, root)
    if not _is_under_outputs(resolved_ticket, root):
        blockers.append("approval ticket path must remain under outputs/.")

    ticket: dict[str, Any] = {}
    ticket_loaded = False
    if not blockers:
        if not resolved_ticket.exists():
            warnings.append("approval ticket is missing; refresh it before manual action.")
        else:
            ticket = _load_ticket(resolved_ticket)
            ticket_loaded = True

    preview = None
    if not blockers:
        preview = preview_result if preview_result is not None else preview_builder(
            current_date=current_date_text,
            output_path=ticket_path,
            write_ticket=False,
            write_local_signals=write_local_signals,
        )
        warnings.extend(getattr(preview, "warnings", ()) or [])
        blockers.extend(getattr(preview, "blockers", ()) or [])

    ticket_matches_preview = bool(ticket and preview and _ticket_matches_preview(ticket, preview))
    if ticket_loaded and not ticket_matches_preview:
        warnings.append("approval ticket does not match the current v30 preview; refresh ticket before manual action.")

    if ticket_loaded:
        blockers.extend(_validate_ticket_safety(ticket))

    ambiguous_nested_source_bridge = bool(ticket.get("source_bridge_result")) if ticket else False
    portfolio_stale = bool(
        ticket.get("portfolio_data_stale_review_required")
        or (preview is not None and getattr(preview, "portfolio_data_stale_review_required", False))
    )

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        closeout_status = CLOSEOUT_BLOCKED
    elif portfolio_stale or unique_warnings or not ticket_loaded or not ticket_matches_preview:
        status = STATUS_REVIEW_REQUIRED
        closeout_status = CLOSEOUT_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        closeout_status = CLOSEOUT_READY

    return ApprovalTicketConsumptionCloseoutResult(
        status=status,
        closeout_status=closeout_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        ticket_path=str(resolved_ticket),
        ticket_loaded=ticket_loaded,
        ticket_matches_current_preview=ticket_matches_preview,
        ticket_has_ambiguous_nested_source_bridge_result=ambiguous_nested_source_bridge,
        selected_crypto_candidate=ticket.get("selected_crypto_candidate") if ticket else None,
        selected_crypto_amount_eur=_amount(ticket.get("selected_crypto_amount_eur")) if ticket else 0.0,
        selected_stock_fund_etf_candidate=ticket.get("selected_stock_fund_etf_candidate") if ticket else None,
        selected_stock_fund_etf_amount_eur=_amount(ticket.get("selected_stock_fund_etf_amount_eur")) if ticket else 0.0,
        approval_status=str(ticket.get("approval_status") or "unknown") if ticket else "missing",
        ticket_as_of=str(ticket.get("as_of") or "") if ticket else "",
        ticket_generated_at=str(ticket.get("generated_at") or "") if ticket else "",
        manual_approval_required=bool(ticket.get("manual_approval_required")) if ticket else False,
        recommendation_quality_current_data=False,
        portfolio_data_stale_review_required=portfolio_stale,
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


def format_approval_ticket_consumption_closeout(
    result: ApprovalTicketConsumptionCloseoutResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Daily Manual Action Brief",
        f"status: {result.status}",
        f"closeout status: {result.closeout_status}",
        f"current date: {result.current_date}",
        f"ticket path: {result.ticket_path}",
        f"ticket loaded: {result.ticket_loaded}",
        f"ticket matches current preview: {result.ticket_matches_current_preview}",
        f"ticket has ambiguous nested source_bridge_result: {result.ticket_has_ambiguous_nested_source_bridge_result}",
        f"ticket as_of: {result.ticket_as_of or 'none'}",
        f"ticket generated_at: {result.ticket_generated_at or 'none'}",
        f"approval status: {result.approval_status}",
        f"manual approval required: {result.manual_approval_required}",
        "",
        "Current refreshed approval ticket:",
        f"- Crypto lane manual buy candidate: {result.selected_crypto_candidate or 'none'} EUR {result.selected_crypto_amount_eur:,.2f}",
        f"- Stock/Fund/ETF lane manual buy candidate: {result.selected_stock_fund_etf_candidate or 'none'} EUR {result.selected_stock_fund_etf_amount_eur:,.2f}",
        "- Final real-world buy remains manual outside J.A.R.V.I.S.",
        "",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"portfolio data stale review required: {result.portfolio_data_stale_review_required}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"portfolio state mutation: {result.portfolio_state_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
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
    parser = argparse.ArgumentParser(description="Show the J.A.R.V.I.S. daily manual action brief from the refreshed approval ticket.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Show the daily manual action brief.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--ticket-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--write-local-signals", action="store_true", help="Write normalized local public crypto signals under jarvis/local while building preview.")
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

    result = build_approval_ticket_consumption_closeout_result(
        current_date=args.current_date,
        ticket_path=args.ticket_path,
        write_local_signals=args.write_local_signals,
    )
    print(format_approval_ticket_consumption_closeout(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())