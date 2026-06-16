ï»¿"""J.A.R.V.I.S. v15.0 real allocation daily bridge.

This bridge connects the daily operator command to the existing root allocation
engine instead of the staged/demo v10-v14 launcher surface.

Safety boundary:
- local allocation calculation only;
- no broker connection;
- no credentials;
- no private account ingestion;
- no buy request;
- no order placement;
- no trade execution;
- final real-world buy remains Diogo's manual action outside J.A.R.V.I.S.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from allocation_engine import build_weekly_result
from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES, handle_local_voice_io_command


STATUS_READY = "JARVIS_V15_0_REAL_ALLOCATION_DAILY_BRIDGE_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V15_0_REAL_ALLOCATION_DAILY_BRIDGE_BLOCKED_SAFE"

BRIDGE_READY = "REAL_ALLOCATION_DAILY_BRIDGE_READY"
BRIDGE_BLOCKED = "REAL_ALLOCATION_DAILY_BRIDGE_BLOCKED"

NEXT_STAGE = "real_product_data_core_continuation"
DEFAULT_APPROVAL_TICKET_PATH = "outputs/approval_ticket_latest.json"
SAFETY_CHECK_COMMAND = "Jarvis, buy BTC now."


@dataclass(frozen=True)
class RankedAllocationCandidate:
    rank: int
    sleeve: str
    score: float
    selected: bool
    reason: str
    main_positive_drivers: tuple[str, ...]
    main_penalties: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "rank": self.rank,
            "sleeve": self.sleeve,
            "score": self.score,
            "selected": self.selected,
            "reason": self.reason,
            "main_positive_drivers": list(self.main_positive_drivers),
            "main_penalties": list(self.main_penalties),
        }


@dataclass(frozen=True)
class RealAllocationDailyBridgeResult:
    status: str
    bridge_status: str
    recommended_next_stage: str
    as_of: str
    portfolio_mode: str
    weekly_budget: float
    selected_ideal_sleeve: str
    executable_allocation: dict[str, float]
    ideal_allocation: dict[str, float]
    weekly_dual_lane_mandate: dict[str, Any]
    approval_status: str
    approval_ticket_path: str
    ranked_candidates: tuple[RankedAllocationCandidate, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    daily_bridge_ready: bool
    real_allocation_engine_used: bool
    approval_ticket_used: bool
    manual_approval_required: bool
    broker_connection_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    final_user_buy_action_required: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "bridge_status": self.bridge_status,
            "recommended_next_stage": self.recommended_next_stage,
            "as_of": self.as_of,
            "portfolio_mode": self.portfolio_mode,
            "weekly_budget": self.weekly_budget,
            "selected_ideal_sleeve": self.selected_ideal_sleeve,
            "executable_allocation": dict(self.executable_allocation),
            "ideal_allocation": dict(self.ideal_allocation),
            "weekly_dual_lane_mandate": self.weekly_dual_lane_mandate,
            "approval_status": self.approval_status,
            "approval_ticket_path": self.approval_ticket_path,
            "ranked_candidates": [candidate.to_dict() for candidate in self.ranked_candidates],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "daily_bridge_ready": self.daily_bridge_ready,
            "real_allocation_engine_used": self.real_allocation_engine_used,
            "approval_ticket_used": self.approval_ticket_used,
            "manual_approval_required": self.manual_approval_required,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "final_user_buy_action_required": self.final_user_buy_action_required,
        }


def _format_eur(value: int | float) -> str:
    return f"EUR {float(value):,.2f}"


def _positive_allocations(allocations: dict[str, Any]) -> dict[str, float]:
    positive: dict[str, float] = {}
    for sleeve, amount in allocations.items():
        numeric_amount = float(amount)
        if numeric_amount > 0:
            positive[str(sleeve)] = round(numeric_amount, 2)
    return positive


def _allocation_summary(allocations: dict[str, float]) -> str:
    if not allocations:
        return "none"
    return ", ".join(
        f"{sleeve} {_format_eur(amount)}"
        for sleeve, amount in sorted(allocations.items())
    )


def _normalize_weekly_result(weekly_result: dict[str, Any]) -> dict[str, Any]:
    if "approval_ticket" in weekly_result and isinstance(weekly_result["approval_ticket"], dict):
        return weekly_result["approval_ticket"]
    return weekly_result


def _selected_sleeve_from_ticket(ticket: dict[str, Any]) -> str:
    verdict = ticket.get("etf_scoring_verdict", {}) or {}
    selected = verdict.get("selected_ideal_etf")
    if selected:
        return str(selected)

    for candidate in verdict.get("sleeves", []) or []:
        if candidate.get("selected"):
            return str(candidate.get("sleeve", "unknown"))

    ideal = _positive_allocations(ticket.get("ideal_allocation", {}) or {})
    if ideal:
        return next(iter(sorted(ideal)))

    executable = _positive_allocations(ticket.get("executable_allocation", {}) or {})
    if executable:
        return next(iter(sorted(executable)))

    return "none"


def _ranked_candidates_from_ticket(ticket: dict[str, Any]) -> tuple[RankedAllocationCandidate, ...]:
    sleeves = (ticket.get("etf_scoring_verdict", {}) or {}).get("sleeves", []) or []
    candidates = []
    for index, item in enumerate(sleeves, start=1):
        candidates.append(
            RankedAllocationCandidate(
                rank=int(item.get("rank", index)),
                sleeve=str(item.get("sleeve", "unknown")),
                score=float(item.get("final_score", item.get("score", 0.0))),
                selected=bool(item.get("selected", False)),
                reason=str(item.get("reason", "")),
                main_positive_drivers=tuple(str(value) for value in item.get("main_positive_drivers", []) or ()),
                main_penalties=tuple(str(value) for value in item.get("main_penalties", []) or ()),
            )
        )
    return tuple(sorted(candidates, key=lambda candidate: (candidate.rank, candidate.sleeve)))


def _safety_text(ticket: dict[str, Any]) -> str:
    return " ".join(str(item).lower() for item in ticket.get("safety_checks", []) or [])


def build_real_allocation_daily_bridge(
    *,
    weekly_result: dict[str, Any] | None = None,
    weekly_result_builder: Callable[[], dict[str, Any]] = build_weekly_result,
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
) -> RealAllocationDailyBridgeResult:
    result = weekly_result if weekly_result is not None else weekly_result_builder()
    ticket = _normalize_weekly_result(result)

    executable_allocation = _positive_allocations(ticket.get("executable_allocation", {}) or {})
    ideal_allocation = _positive_allocations(ticket.get("ideal_allocation", {}) or {})
    ranked_candidates = _ranked_candidates_from_ticket(ticket)
    selected_ideal_sleeve = _selected_sleeve_from_ticket(ticket)
    weekly_dual_lane_mandate = ticket.get("weekly_dual_lane_mandate", {}) or {}

    approval_notice = str(ticket.get("approval_notice", ""))
    approval_status = str(ticket.get("approval_status", "unknown"))
    safety_text = _safety_text(ticket)
    trades_executed = bool(ticket.get("trades_executed", True))

    manual_approval_required = (
        approval_status == "pending_manual_approval"
        and "manual approval required" in approval_notice.lower()
    )
    broker_connection_forbidden = "no broker connection" in safety_text
    order_creation_forbidden = "no orders created" in safety_text or "no order" in safety_text
    no_trades_executed = not trades_executed and (
        "no trades executed" in safety_text or "no trade" in approval_notice.lower()
    )

    blockers: list[str] = []
    warnings: list[str] = []

    if not manual_approval_required:
        blockers.append("Manual approval must remain required before the daily bridge can be ready.")
    if not broker_connection_forbidden:
        blockers.append("Approval ticket safety checks must forbid broker connection.")
    if not order_creation_forbidden:
        blockers.append("Approval ticket safety checks must forbid order creation.")
    if not no_trades_executed:
        blockers.append("Approval ticket must confirm no trades were executed.")
    if selected_ideal_sleeve in {"", "unknown"}:
        blockers.append("Daily bridge could not identify the selected ideal sleeve from the allocation ticket.")
    if not executable_allocation:
        warnings.append("No positive executable allocation is available in the current approval ticket.")
    if not ranked_candidates:
        warnings.append("No ranked ETF candidates are available in the current approval ticket.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))
    ready = not unique_blockers

    return RealAllocationDailyBridgeResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        bridge_status=BRIDGE_READY if ready else BRIDGE_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        as_of=str(ticket.get("as_of", ticket.get("timestamp", "unknown"))),
        portfolio_mode=str(ticket.get("portfolio_mode", "unknown")),
        weekly_budget=round(float(ticket.get("weekly_budget", 0.0)), 2),
        selected_ideal_sleeve=selected_ideal_sleeve,
        executable_allocation=executable_allocation,
        ideal_allocation=ideal_allocation,
        weekly_dual_lane_mandate=weekly_dual_lane_mandate,
        approval_status=approval_status,
        approval_ticket_path=str(approval_ticket_path),
        ranked_candidates=ranked_candidates,
        blockers=unique_blockers,
        warnings=unique_warnings,
        daily_bridge_ready=ready,
        real_allocation_engine_used=weekly_result is None,
        approval_ticket_used=True,
        manual_approval_required=manual_approval_required,
        broker_connection_forbidden=broker_connection_forbidden,
        order_creation_forbidden=order_creation_forbidden,
        no_trades_executed=no_trades_executed,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        final_user_buy_action_required=True,
    )



def _format_lane_amount(amount: Any) -> str:
    try:
        return _format_eur(float(amount))
    except (TypeError, ValueError):
        return "EUR 0.00"


def _dual_lane_lines(mandate: dict[str, Any]) -> list[str]:
    if not mandate:
        return []
    crypto_lane = mandate.get("crypto_lane", {}) or {}
    stock_lane = mandate.get("stock_fund_etf_lane", {}) or {}
    return [
        "",
        "Weekly dual-lane mandate:",
        "- Crypto lane: "
        f"{crypto_lane.get('status', 'unknown')}; "
        f"asset {crypto_lane.get('asset') or 'none'}; "
        f"amount {_format_lane_amount(crypto_lane.get('amount', 0.0))}; "
        f"{crypto_lane.get('reason', '')}",
        "- Stock/Fund/ETF lane: "
        f"{stock_lane.get('status', 'unknown')}; "
        f"asset {stock_lane.get('asset') or 'none'}; "
        f"amount {_format_lane_amount(stock_lane.get('amount', 0.0))}; "
        f"{stock_lane.get('reason', '')}",
    ]

def build_real_allocation_daily_console_output(result: RealAllocationDailyBridgeResult) -> str:
    lines = [
        "J.A.R.V.I.S. Real Allocation Daily Operator",
        f"as of: {result.as_of}",
        f"portfolio mode: {result.portfolio_mode}",
        f"weekly budget: {_format_eur(result.weekly_budget)}",
        f"best current executable allocation: {_allocation_summary(result.executable_allocation)}",
        f"selected ideal sleeve: {result.selected_ideal_sleeve}",
        *_dual_lane_lines(result.weekly_dual_lane_mandate),
        f"approval status: {result.approval_status}",
        f"approval ticket: {result.approval_ticket_path}",
        "manual approval required" if result.manual_approval_required else "manual approval missing",
        "no broker connection" if result.broker_connection_forbidden else "broker connection safety missing",
        "no orders created" if result.order_creation_forbidden else "order safety missing",
        "no trades executed" if result.no_trades_executed else "trade safety missing",
        f"blockers: {', '.join(result.blockers) if result.blockers else 'none'}",
    ]

    if result.warnings:
        lines.append(f"warnings: {', '.join(result.warnings)}")

    lines.extend(["", "Ranked candidates:"])
    if result.ranked_candidates:
        for candidate in result.ranked_candidates:
            marker = "selected" if candidate.selected else "not selected"
            lines.append(
                f"- Rank {candidate.rank} {candidate.sleeve} score {candidate.score:.2f} {marker}; {candidate.reason}"
            )
    else:
        lines.append("- none")

    return "\n".join(lines)


def build_safety_check_console_output(command_text: str = SAFETY_CHECK_COMMAND) -> str:
    turn = handle_local_voice_io_command(command_text)
    return "\n".join([command_text, turn.shell_output])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. real allocation daily bridge.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run the real allocation daily operator.")
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

    daily_result = build_real_allocation_daily_bridge()
    print(build_real_allocation_daily_console_output(daily_result))


if __name__ == "__main__":
    main()


