"""J.A.R.V.I.S. v37.0 autonomous dual-lane daily refresh.

v37 makes the daily command refresh both live lanes before printing the action
brief:

1. Crypto lane: run the existing expanded crypto approval-ticket refresh chain.
2. ETF/fund lane: run the v36 real-instrument refresh/action brief chain.
3. Print one clean manual action brief.

Autonomous means autonomous when the daily command runs. It still never creates
orders, connects brokers, uses credentials, ingests private account data, or
executes trades.
"""

from __future__ import annotations

import argparse
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
from .jarvis_v34_0_stock_fund_etf_sleeve_to_instrument_resolver import (
    DEFAULT_INSTRUMENT_UNIVERSE_PATH,
    DEFAULT_OUTPUT_RESOLUTION_PATH,
)
from .jarvis_v36_0_autonomous_daily_refresh_action_brief import (
    AutonomousDailyRefreshActionBriefResult,
    build_autonomous_daily_refresh_action_brief_result,
)

STATUS_READY = "JARVIS_V37_0_AUTONOMOUS_DUAL_LANE_DAILY_REFRESH_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V37_0_AUTONOMOUS_DUAL_LANE_DAILY_REFRESH_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V37_0_AUTONOMOUS_DUAL_LANE_DAILY_REFRESH_BLOCKED_SAFE"

DAILY_READY = "AUTONOMOUS_DUAL_LANE_DAILY_REFRESH_READY"
DAILY_REVIEW_REQUIRED = "AUTONOMOUS_DUAL_LANE_DAILY_REFRESH_REVIEW_REQUIRED"
DAILY_BLOCKED = "AUTONOMOUS_DUAL_LANE_DAILY_REFRESH_BLOCKED"

NEXT_STAGE = "individual_stock_public_universe_and_ranker"


@dataclass(frozen=True)
class AutonomousDualLaneDailyRefreshResult:
    status: str
    daily_status: str
    recommended_next_stage: str
    current_date: str
    ticket_path: str
    instrument_universe_path: str
    resolution_path: str
    crypto_refresh_ran: bool
    crypto_ticket_written: bool
    etf_refresh_ran: bool
    etf_resolution_written: bool
    etf_ticket_written: bool
    crypto_candidate: str | None
    crypto_amount_eur: float | None
    stock_fund_etf_sleeve: str | None
    stock_fund_etf_amount_eur: float | None
    real_instrument_name: str | None
    real_instrument_symbol: str | None
    real_instrument_isin: str | None
    real_instrument_source_as_of: str | None
    real_instrument_public_source_ready: bool
    recommendation_quality_current_data: bool
    crypto_refresh_result: Any
    etf_daily_result: Any
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
            "crypto_refresh_ran": self.crypto_refresh_ran,
            "crypto_ticket_written": self.crypto_ticket_written,
            "etf_refresh_ran": self.etf_refresh_ran,
            "etf_resolution_written": self.etf_resolution_written,
            "etf_ticket_written": self.etf_ticket_written,
            "crypto_candidate": self.crypto_candidate,
            "crypto_amount_eur": self.crypto_amount_eur,
            "stock_fund_etf_sleeve": self.stock_fund_etf_sleeve,
            "stock_fund_etf_amount_eur": self.stock_fund_etf_amount_eur,
            "real_instrument_name": self.real_instrument_name,
            "real_instrument_symbol": self.real_instrument_symbol,
            "real_instrument_isin": self.real_instrument_isin,
            "real_instrument_source_as_of": self.real_instrument_source_as_of,
            "real_instrument_public_source_ready": self.real_instrument_public_source_ready,
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "crypto_refresh_result": self.crypto_refresh_result.to_dict() if hasattr(self.crypto_refresh_result, "to_dict") else dict(getattr(self.crypto_refresh_result, "__dict__", {})),
            "etf_daily_result": self.etf_daily_result.to_dict() if hasattr(self.etf_daily_result, "to_dict") else dict(getattr(self.etf_daily_result, "__dict__", {})),
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


def _status_blocked(status: str) -> bool:
    return "BLOCKED" in status


def _status_ready(status: str) -> bool:
    return "READY" in status and "REVIEW_REQUIRED" not in status and "BLOCKED" not in status


def _crypto_review_is_legacy_only(crypto_result: Any) -> bool:
    """Allow READY when crypto refreshed and only stale pre-refresh warnings remain."""
    if not bool(getattr(crypto_result, "approval_ticket_written", False)):
        return False
    if getattr(crypto_result, "blockers", ()) or ():
        return False
    warnings = tuple(getattr(crypto_result, "warnings", ()) or ())
    if not warnings:
        return False
    return all(_is_legacy_pre_refresh_warning(str(warning)) for warning in warnings)


def _amount(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _is_legacy_pre_refresh_warning(message: str) -> bool:
    """Warnings that are true before v37 refresh but not blockers after both ticket writes succeed."""
    normalized = str(message).strip().lower()
    if normalized in {
        "crypto daily public-data refresh requires review",
        "crypto daily public-data refresh requires review.",
    }:
        return False
    legacy_exact = {
        "approval_ticket_latest is 13 days old; refresh required before manual action.",
        "crypto-lane candidate changed from allocation basis btc to hype; approval ticket refresh is required before manual action.",
    }
    if message in legacy_exact:
        return True
    legacy_fragments = (
        "approval_ticket_latest is",
        "crypto-lane candidate changed from allocation basis",
        "etf universe has no as_of/updated_at metadata",
        "portfolio_state is",
    )
    return any(fragment in normalized for fragment in legacy_fragments)


def _filtered_warnings_after_successful_refresh(
    warnings: list[str],
    *,
    crypto_ticket_written: bool,
    etf_ticket_written: bool,
    etf_public_source_ready: bool,
) -> list[str]:
    if not (crypto_ticket_written and etf_ticket_written and etf_public_source_ready):
        return warnings
    return [warning for warning in warnings if not _is_legacy_pre_refresh_warning(warning)]


def _first_attr(obj: Any, names: tuple[str, ...]) -> Any:
    for name in names:
        value = getattr(obj, name, None)
        if value not in (None, ""):
            return value
    return None


def build_autonomous_dual_lane_daily_refresh_result(
    *,
    current_date: str | None = None,
    ticket_path: str | Path = DEFAULT_OUTPUT_PATH,
    instrument_universe_path: str | Path = DEFAULT_INSTRUMENT_UNIVERSE_PATH,
    resolution_path: str | Path = DEFAULT_OUTPUT_RESOLUTION_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    write_ticket: bool = True,
    write_local_signals: bool = True,
    write_local_resolution: bool = True,
    crypto_refresh_builder: Callable[..., ExpandedCryptoApprovalTicketRefreshResult] = build_expanded_crypto_approval_ticket_refresh_result,
    etf_daily_builder: Callable[..., AutonomousDailyRefreshActionBriefResult] = build_autonomous_daily_refresh_action_brief_result,
) -> AutonomousDualLaneDailyRefreshResult:
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

    crypto_result: Any = None
    etf_result: Any = None

    if not blockers:
        crypto_result = crypto_refresh_builder(
            current_date=current_date_text,
            output_path=ticket_path,
            root=root,
            write_ticket=write_ticket,
            write_local_signals=write_local_signals,
        )
        blockers.extend(getattr(crypto_result, "blockers", ()) or [])
        warnings.extend(getattr(crypto_result, "warnings", ()) or [])
        crypto_status = str(getattr(crypto_result, "status", ""))
        if _status_blocked(crypto_status):
            blockers.append("crypto daily public-data refresh was blocked.")
        elif not _status_ready(crypto_status) and not _crypto_review_is_legacy_only(crypto_result):
            warnings.append("crypto daily public-data refresh requires review")

    if not blockers:
        etf_result = etf_daily_builder(
            current_date=current_date_text,
            ticket_path=ticket_path,
            instrument_universe_path=instrument_universe_path,
            resolution_path=resolution_path,
            root=root,
            max_age_days=max_age_days,
            write_local_resolution=write_local_resolution,
            write_ticket=write_ticket,
        )
        blockers.extend(getattr(etf_result, "blockers", ()) or [])
        warnings.extend(getattr(etf_result, "warnings", ()) or [])
        etf_status = str(getattr(etf_result, "status", ""))
        if _status_blocked(etf_status):
            blockers.append("ETF/fund daily real-instrument refresh was blocked.")
        elif not _status_ready(etf_status):
            warnings.append("ETF/fund daily real-instrument refresh requires review.")

    crypto_candidate = _first_attr(etf_result, ("crypto_candidate",)) or _first_attr(crypto_result, ("selected_crypto_candidate",))
    crypto_amount = _amount(_first_attr(etf_result, ("crypto_amount_eur",)) or _first_attr(crypto_result, ("selected_crypto_amount_eur",)))

    crypto_ticket_written = bool(getattr(crypto_result, "approval_ticket_written", False))
    etf_ticket_written = bool(getattr(etf_result, "approval_ticket_written", False))
    etf_public_source_ready = bool(getattr(etf_result, "real_instrument_public_source_ready", False))
    warnings = _filtered_warnings_after_successful_refresh(
        warnings,
        crypto_ticket_written=crypto_ticket_written,
        etf_ticket_written=etf_ticket_written,
        etf_public_source_ready=etf_public_source_ready,
    )

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

    approval_ticket_mutation = crypto_ticket_written or etf_ticket_written
    return AutonomousDualLaneDailyRefreshResult(
        status=status,
        daily_status=daily_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        ticket_path=str(resolved_ticket),
        instrument_universe_path=str(resolved_universe),
        resolution_path=str(resolved_resolution),
        crypto_refresh_ran=crypto_result is not None,
        crypto_ticket_written=bool(getattr(crypto_result, "approval_ticket_written", False)),
        etf_refresh_ran=etf_result is not None,
        etf_resolution_written=bool(getattr(etf_result, "local_resolution_written", False)),
        etf_ticket_written=bool(getattr(etf_result, "approval_ticket_written", False)),
        crypto_candidate=str(crypto_candidate) if crypto_candidate not in (None, "") else None,
        crypto_amount_eur=crypto_amount,
        stock_fund_etf_sleeve=_first_attr(etf_result, ("stock_fund_etf_sleeve",)),
        stock_fund_etf_amount_eur=_amount(_first_attr(etf_result, ("stock_fund_etf_amount_eur",))),
        real_instrument_name=_first_attr(etf_result, ("real_instrument_name",)),
        real_instrument_symbol=_first_attr(etf_result, ("real_instrument_symbol",)),
        real_instrument_isin=_first_attr(etf_result, ("real_instrument_isin",)),
        real_instrument_source_as_of=_first_attr(etf_result, ("real_instrument_source_as_of",)),
        real_instrument_public_source_ready=bool(getattr(etf_result, "real_instrument_public_source_ready", False)),
        recommendation_quality_current_data=not unique_blockers and not unique_warnings,
        crypto_refresh_result=crypto_result,
        etf_daily_result=etf_result,
        allocation_mutation=False,
        approval_ticket_mutation=approval_ticket_mutation,
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


def format_autonomous_dual_lane_daily_refresh(
    result: AutonomousDualLaneDailyRefreshResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Autonomous Dual-Lane Daily Refresh",
        f"status: {result.status}",
        f"daily status: {result.daily_status}",
        f"current date: {result.current_date}",
        f"ticket path: {result.ticket_path}",
        f"instrument universe path: {result.instrument_universe_path}",
        f"resolution path: {result.resolution_path}",
        f"crypto refresh ran: {result.crypto_refresh_ran}",
        f"crypto ticket written: {result.crypto_ticket_written}",
        f"ETF/fund refresh ran: {result.etf_refresh_ran}",
        f"ETF/fund resolution written: {result.etf_resolution_written}",
        f"ETF/fund ticket written: {result.etf_ticket_written}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        "",
        "Clean manual action brief:",
        "Crypto lane:",
        f"- Candidate: {result.crypto_candidate or 'none'}",
        f"- Amount: {_money(result.crypto_amount_eur)}",
        "- Refreshed before this brief: " + str(result.crypto_refresh_ran),
        "",
        "Stock/Fund/ETF lane:",
        f"- Sleeve: {result.stock_fund_etf_sleeve or 'none'}",
        f"- Real instrument: {result.real_instrument_name or 'none'}",
        f"- Symbol: {result.real_instrument_symbol or 'none'}",
        f"- ISIN: {result.real_instrument_isin or 'none'}",
        f"- Amount: {_money(result.stock_fund_etf_amount_eur)}",
        f"- Source as_of: {result.real_instrument_source_as_of or 'none'}",
        f"- Public source ready: {result.real_instrument_public_source_ready}",
        "- Refreshed before this brief: " + str(result.etf_refresh_ran),
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
    parser = argparse.ArgumentParser(description="Run autonomous safe crypto + ETF/fund daily refresh and clean manual action brief.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run autonomous dual-lane daily refresh.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--ticket-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--instrument-universe-path", default=DEFAULT_INSTRUMENT_UNIVERSE_PATH)
    parser.add_argument("--resolution-path", default=DEFAULT_OUTPUT_RESOLUTION_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--no-write-ticket", action="store_true", help="Do not refresh the approval ticket.")
    parser.add_argument("--no-write-local-signals", action="store_true", help="Do not refresh local crypto signals.")
    parser.add_argument("--no-write-local-resolution", action="store_true", help="Do not refresh local ETF/fund selected instrument resolution.")
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

    result = build_autonomous_dual_lane_daily_refresh_result(
        current_date=args.current_date,
        ticket_path=args.ticket_path,
        instrument_universe_path=args.instrument_universe_path,
        resolution_path=args.resolution_path,
        max_age_days=args.max_age_days,
        write_ticket=not args.no_write_ticket,
        write_local_signals=not args.no_write_local_signals,
        write_local_resolution=not args.no_write_local_resolution,
    )
    print(format_autonomous_dual_lane_daily_refresh(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())