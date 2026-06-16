"""J.A.R.V.I.S. v16.0 real daily readiness gate.

This module keeps the v15 real allocation bridge as the active recommendation
source, then adds the missing daily product check: whether the local data behind
that recommendation is fresh enough to trust before Diogo performs any manual
real-world buy outside J.A.R.V.I.S.

Safety boundary remains unchanged:
- local files only;
- no broker connection;
- no credentials;
- no private brokerage/account data ingestion;
- no buy request;
- no order placement;
- no trade execution.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable

from allocation_engine import build_weekly_result
from .jarvis_v15_0_real_allocation_daily_bridge import (
    STATUS_READY as V15_STATUS_READY,
    RealAllocationDailyBridgeResult,
    build_real_allocation_daily_bridge,
    build_safety_check_console_output,
    _dual_lane_lines,
)
from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES


STATUS_READY = "JARVIS_V16_0_REAL_DAILY_READINESS_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V16_0_REAL_DAILY_READINESS_GATE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V16_0_REAL_DAILY_READINESS_GATE_BLOCKED_SAFE"

READINESS_READY = "FRESH_READY_FOR_MANUAL_REVIEW"
READINESS_REVIEW_REQUIRED = "STALE_REVIEW_REQUIRED"
READINESS_BLOCKED = "READINESS_BLOCKED"

DEFAULT_PORTFOLIO_STATE_PATH = "portfolio_state.json"
DEFAULT_APPROVAL_TICKET_PATH = "outputs/approval_ticket_latest.json"
DEFAULT_ETF_UNIVERSE_PATH = "etf_universe.json"
DEFAULT_MAX_FRESH_AGE_DAYS = 7
NEXT_STAGE = "real_manual_action_brief"


@dataclass(frozen=True)
class DateFreshnessCheck:
    name: str
    source_path: str
    as_of: str
    current_date: str
    age_days: int | None
    max_age_days: int
    status: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "source_path": self.source_path,
            "as_of": self.as_of,
            "current_date": self.current_date,
            "age_days": self.age_days,
            "max_age_days": self.max_age_days,
            "status": self.status,
            "message": self.message,
        }


@dataclass(frozen=True)
class RealDailyReadinessGateResult:
    status: str
    readiness_status: str
    recommended_next_stage: str
    current_date: str
    max_fresh_age_days: int
    recommendation_trust: str
    manual_action_guidance: str
    allocation_result: RealAllocationDailyBridgeResult
    freshness_checks: tuple[DateFreshnessCheck, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    data_ready_for_manual_review: bool
    stale_data_review_required: bool
    real_allocation_engine_used: bool
    approval_ticket_file_checked: bool
    portfolio_state_file_checked: bool
    etf_universe_file_checked: bool
    manual_approval_required: bool
    broker_connection_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    final_user_buy_action_required: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "readiness_status": self.readiness_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "max_fresh_age_days": self.max_fresh_age_days,
            "recommendation_trust": self.recommendation_trust,
            "manual_action_guidance": self.manual_action_guidance,
            "allocation_result": self.allocation_result.to_dict(),
            "freshness_checks": [check.to_dict() for check in self.freshness_checks],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "data_ready_for_manual_review": self.data_ready_for_manual_review,
            "stale_data_review_required": self.stale_data_review_required,
            "real_allocation_engine_used": self.real_allocation_engine_used,
            "approval_ticket_file_checked": self.approval_ticket_file_checked,
            "portfolio_state_file_checked": self.portfolio_state_file_checked,
            "etf_universe_file_checked": self.etf_universe_file_checked,
            "manual_approval_required": self.manual_approval_required,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "final_user_buy_action_required": self.final_user_buy_action_required,
        }


def _read_json_object(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as file:
        value = json.load(file)
    if not isinstance(value, dict):
        raise ValueError(f"Expected JSON object at {path}.")
    return value


def _parse_iso_date(value: str) -> date | None:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _date_freshness_check(
    *,
    name: str,
    source_path: str | Path,
    as_of: str,
    current_date: date,
    max_age_days: int,
) -> DateFreshnessCheck:
    parsed = _parse_iso_date(as_of)
    current_text = current_date.isoformat()
    if parsed is None:
        return DateFreshnessCheck(
            name=name,
            source_path=str(source_path),
            as_of=str(as_of),
            current_date=current_text,
            age_days=None,
            max_age_days=max_age_days,
            status="UNKNOWN_DATE",
            message=f"{name} has an invalid or missing as_of date: {as_of}.",
        )

    age_days = (current_date - parsed).days
    if age_days < 0:
        return DateFreshnessCheck(
            name=name,
            source_path=str(source_path),
            as_of=parsed.isoformat(),
            current_date=current_text,
            age_days=age_days,
            max_age_days=max_age_days,
            status="FUTURE_DATE",
            message=f"{name} is dated in the future by {abs(age_days)} days.",
        )
    if age_days > max_age_days:
        return DateFreshnessCheck(
            name=name,
            source_path=str(source_path),
            as_of=parsed.isoformat(),
            current_date=current_text,
            age_days=age_days,
            max_age_days=max_age_days,
            status="STALE",
            message=f"{name} is {age_days} days old; refresh required before manual action.",
        )
    return DateFreshnessCheck(
        name=name,
        source_path=str(source_path),
        as_of=parsed.isoformat(),
        current_date=current_text,
        age_days=age_days,
        max_age_days=max_age_days,
        status="FRESH",
        message=f"{name} is {age_days} days old and within the {max_age_days}-day freshness window.",
    )


def _warnings_from_checks(checks: tuple[DateFreshnessCheck, ...]) -> tuple[str, ...]:
    warnings: list[str] = []
    for check in checks:
        if check.status == "STALE":
            warnings.append(check.message)
    return tuple(dict.fromkeys(warnings))


def _blockers_from_checks(checks: tuple[DateFreshnessCheck, ...]) -> tuple[str, ...]:
    blockers: list[str] = []
    for check in checks:
        if check.status in {"UNKNOWN_DATE", "FUTURE_DATE"}:
            blockers.append(check.message)
    return tuple(dict.fromkeys(blockers))


def build_real_daily_readiness_gate(
    *,
    weekly_result: dict[str, Any] | None = None,
    weekly_result_builder: Callable[[], dict[str, Any]] = build_weekly_result,
    current_date: date | None = None,
    portfolio_state_path: str | Path = DEFAULT_PORTFOLIO_STATE_PATH,
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    etf_universe_path: str | Path = DEFAULT_ETF_UNIVERSE_PATH,
    max_fresh_age_days: int = DEFAULT_MAX_FRESH_AGE_DAYS,
) -> RealDailyReadinessGateResult:
    today = current_date or date.today()
    allocation_result = build_real_allocation_daily_bridge(
        weekly_result=weekly_result,
        weekly_result_builder=weekly_result_builder,
        approval_ticket_path=approval_ticket_path,
    )

    blockers: list[str] = list(allocation_result.blockers)
    warnings: list[str] = list(allocation_result.warnings)
    freshness_checks: list[DateFreshnessCheck] = []

    portfolio_state_file_checked = False
    approval_ticket_file_checked = False
    etf_universe_file_checked = False

    try:
        portfolio_state = _read_json_object(portfolio_state_path)
        portfolio_state_file_checked = True
        freshness_checks.append(
            _date_freshness_check(
                name="portfolio_state",
                source_path=portfolio_state_path,
                as_of=str(portfolio_state.get("as_of", "unknown")),
                current_date=today,
                max_age_days=max_fresh_age_days,
            )
        )
    except FileNotFoundError:
        blockers.append(f"Missing portfolio state file: {portfolio_state_path}.")
    except (json.JSONDecodeError, ValueError) as exc:
        blockers.append(f"Could not read portfolio state file {portfolio_state_path}: {exc}")

    try:
        approval_ticket = _read_json_object(approval_ticket_path)
        approval_ticket_file_checked = True
        ticket_as_of = str(approval_ticket.get("as_of", approval_ticket.get("timestamp", "unknown")))
        freshness_checks.append(
            _date_freshness_check(
                name="approval_ticket_latest",
                source_path=approval_ticket_path,
                as_of=ticket_as_of,
                current_date=today,
                max_age_days=max_fresh_age_days,
            )
        )
        if ticket_as_of != allocation_result.as_of:
            blockers.append(
                "Approval ticket file as_of does not match current allocation engine result "
                f"({ticket_as_of} vs {allocation_result.as_of})."
            )
    except FileNotFoundError:
        blockers.append(f"Missing approval ticket file: {approval_ticket_path}.")
    except (json.JSONDecodeError, ValueError) as exc:
        blockers.append(f"Could not read approval ticket file {approval_ticket_path}: {exc}")

    try:
        etf_universe = _read_json_object(etf_universe_path)
        etf_universe_file_checked = True
        etf_as_of = etf_universe.get("as_of") or etf_universe.get("updated_at")
        if etf_as_of:
            freshness_checks.append(
                _date_freshness_check(
                    name="etf_universe",
                    source_path=etf_universe_path,
                    as_of=str(etf_as_of),
                    current_date=today,
                    max_age_days=max_fresh_age_days,
                )
            )
        else:
            warnings.append(
                "ETF universe has no as_of/updated_at metadata; scoring inputs are treated as manually maintained local scores."
            )
    except FileNotFoundError:
        blockers.append(f"Missing ETF universe file: {etf_universe_path}.")
    except (json.JSONDecodeError, ValueError) as exc:
        blockers.append(f"Could not read ETF universe file {etf_universe_path}: {exc}")

    checks_tuple = tuple(freshness_checks)
    blockers.extend(_blockers_from_checks(checks_tuple))
    warnings.extend(_warnings_from_checks(checks_tuple))

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))
    has_stale_data = any(check.status == "STALE" for check in checks_tuple)

    if unique_blockers or allocation_result.status != V15_STATUS_READY:
        status = STATUS_BLOCKED
        readiness_status = READINESS_BLOCKED
        recommendation_trust = "blocked_until_local_data_and_safety_checks_pass"
        manual_action_guidance = "Do not use this recommendation for a manual buy until blockers are resolved."
        data_ready = False
    elif has_stale_data:
        status = STATUS_REVIEW_REQUIRED
        readiness_status = READINESS_REVIEW_REQUIRED
        recommendation_trust = "refresh_required_before_manual_action"
        manual_action_guidance = "Refresh local portfolio data and approval ticket before any manual buy."
        data_ready = False
    else:
        status = STATUS_READY
        readiness_status = READINESS_READY
        recommendation_trust = "fresh_enough_for_manual_review"
        manual_action_guidance = "Data is fresh enough for manual review; Diogo still performs any real-world buy outside J.A.R.V.I.S."
        data_ready = True

    return RealDailyReadinessGateResult(
        status=status,
        readiness_status=readiness_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=today.isoformat(),
        max_fresh_age_days=max_fresh_age_days,
        recommendation_trust=recommendation_trust,
        manual_action_guidance=manual_action_guidance,
        allocation_result=allocation_result,
        freshness_checks=checks_tuple,
        blockers=unique_blockers,
        warnings=unique_warnings,
        data_ready_for_manual_review=data_ready,
        stale_data_review_required=has_stale_data and not unique_blockers,
        real_allocation_engine_used=allocation_result.real_allocation_engine_used,
        approval_ticket_file_checked=approval_ticket_file_checked,
        portfolio_state_file_checked=portfolio_state_file_checked,
        etf_universe_file_checked=etf_universe_file_checked,
        manual_approval_required=allocation_result.manual_approval_required,
        broker_connection_forbidden=allocation_result.broker_connection_forbidden,
        order_creation_forbidden=allocation_result.order_creation_forbidden,
        no_trades_executed=allocation_result.no_trades_executed,
        final_user_buy_action_required=True,
    )


def build_real_daily_readiness_console_output(result: RealDailyReadinessGateResult) -> str:
    allocation = result.allocation_result
    lines = [
        "J.A.R.V.I.S. Real Allocation Daily Operator",
        f"operator date: {result.current_date}",
        f"data readiness: {result.readiness_status}",
        f"recommendation trust: {result.recommendation_trust}",
        f"manual action guidance: {result.manual_action_guidance}",
        "",
        "Freshness checks:",
    ]

    if result.freshness_checks:
        for check in result.freshness_checks:
            age = "unknown" if check.age_days is None else f"{check.age_days} days"
            lines.append(
                f"- {check.name}: {check.status}; as_of {check.as_of}; age {age}; source {check.source_path}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "Real allocation:",
            f"as of: {allocation.as_of}",
            f"portfolio mode: {allocation.portfolio_mode}",
            f"weekly budget: EUR {allocation.weekly_budget:,.2f}",
            "best current executable allocation: "
            + (
                ", ".join(
                    f"{sleeve} EUR {amount:,.2f}"
                    for sleeve, amount in sorted(allocation.executable_allocation.items())
                )
                if allocation.executable_allocation
                else "none"
            ),
            f"selected ideal sleeve: {allocation.selected_ideal_sleeve}",
            *_dual_lane_lines(allocation.weekly_dual_lane_mandate),
            f"approval status: {allocation.approval_status}",
            f"approval ticket: {allocation.approval_ticket_path}",
            "manual approval required" if result.manual_approval_required else "manual approval missing",
            "no broker connection" if result.broker_connection_forbidden else "broker connection safety missing",
            "no orders created" if result.order_creation_forbidden else "order safety missing",
            "no trades executed" if result.no_trades_executed else "trade safety missing",
            f"blockers: {', '.join(result.blockers) if result.blockers else 'none'}",
            f"warnings: {', '.join(result.warnings) if result.warnings else 'none'}",
            "",
            "Ranked candidates:",
        ]
    )

    if allocation.ranked_candidates:
        for candidate in allocation.ranked_candidates:
            marker = "selected" if candidate.selected else "not selected"
            lines.append(
                f"- Rank {candidate.rank} {candidate.sleeve} score {candidate.score:.2f} {marker}; {candidate.reason}"
            )
    else:
        lines.append("- none")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. real daily readiness gate.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run the real allocation daily operator with readiness checks.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    args = parser.parse_args()

    if args.safety_check:
        print(build_safety_check_console_output())
        return

    if args.voice_command:
        print(build_safety_check_console_output(args.voice_command))
        return

    if args.demo:
        print("Available typed Jarvis commands:")
        for command in DEFAULT_COMMAND_SAMPLES:
            print(f"- {command}")
        return

    readiness_result = build_real_daily_readiness_gate()
    print(build_real_daily_readiness_console_output(readiness_result))


if __name__ == "__main__":
    main()
