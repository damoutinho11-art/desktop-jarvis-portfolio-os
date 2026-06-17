"""J.A.R.V.I.S. v56.0 platform-aware weekly manual action packet.

This stage converts the v55 platform-lane policy into one clean weekly manual
action packet:
- LHV emergency fund top-up
- LHV crypto review amount
- Lightyear ETF/fund/core review amount
- Lightyear individual stock review-only
- Legacy holdings observe-only

Safety invariant:
Automated research. Manual trust. Manual approval. No execution.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from jarvis.jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from jarvis.runtime.manual_portfolio_snapshot import DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH
from jarvis.runtime.platform_lane_policy import (
    PlatformLaneAction,
    PlatformLanePolicyResult,
    build_platform_lane_policy_result,
)
from jarvis.runtime.portfolio_exposure_audit import (
    DEFAULT_IDEAL_EMERGENCY_MONTHS,
    DEFAULT_MIN_EMERGENCY_MONTHS,
)

STATUS_READY = "JARVIS_V56_0_PLATFORM_AWARE_WEEKLY_ACTION_PACKET_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V56_0_PLATFORM_AWARE_WEEKLY_ACTION_PACKET_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V56_0_PLATFORM_AWARE_WEEKLY_ACTION_PACKET_BLOCKED_SAFE"

PACKET_READY = "PLATFORM_AWARE_WEEKLY_ACTION_PACKET_READY"
PACKET_REVIEW_REQUIRED = "PLATFORM_AWARE_WEEKLY_ACTION_PACKET_REVIEW_REQUIRED"
PACKET_BLOCKED = "PLATFORM_AWARE_WEEKLY_ACTION_PACKET_BLOCKED"

DEFAULT_AGE_YEARS = 26


@dataclass(frozen=True)
class WeeklyPlatformAction:
    step: int
    platform: str
    lane: str
    amount_eur: float
    manual_action: str
    review_only: bool
    manual_only: bool
    action_allowed_by_policy: bool
    policy_note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "platform": self.platform,
            "lane": self.lane,
            "amount_eur": self.amount_eur,
            "manual_action": self.manual_action,
            "review_only": self.review_only,
            "manual_only": self.manual_only,
            "action_allowed_by_policy": self.action_allowed_by_policy,
            "policy_note": self.policy_note,
        }


@dataclass(frozen=True)
class PlatformAwareWeeklyActionPacketResult:
    status: str
    packet_status: str
    current_date: str
    snapshot_path: str
    snapshot_ready: bool
    monthly_contribution_eur: float | None
    monthly_expenses_eur: float | None
    emergency_top_up_eur: float | None
    investable_after_emergency_eur: float | None
    new_investing_platform: str
    crypto_platform: str
    cash_emergency_platform: str
    legacy_positions_mode: str
    weekly_actions: tuple[WeeklyPlatformAction, ...]
    total_manual_action_amount_eur: float
    legacy_sell_allowed: bool
    evidence_refresh_required_before_manual_buy: bool
    policy_flags: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    allocation_mutation: bool
    approval_ticket_mutation: bool
    evidence_pack_mutation: bool
    local_cache_mutation: bool
    portfolio_state_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "packet_status": self.packet_status,
            "current_date": self.current_date,
            "snapshot_path": self.snapshot_path,
            "snapshot_ready": self.snapshot_ready,
            "monthly_contribution_eur": self.monthly_contribution_eur,
            "monthly_expenses_eur": self.monthly_expenses_eur,
            "emergency_top_up_eur": self.emergency_top_up_eur,
            "investable_after_emergency_eur": self.investable_after_emergency_eur,
            "new_investing_platform": self.new_investing_platform,
            "crypto_platform": self.crypto_platform,
            "cash_emergency_platform": self.cash_emergency_platform,
            "legacy_positions_mode": self.legacy_positions_mode,
            "weekly_actions": [action.to_dict() for action in self.weekly_actions],
            "total_manual_action_amount_eur": self.total_manual_action_amount_eur,
            "legacy_sell_allowed": self.legacy_sell_allowed,
            "evidence_refresh_required_before_manual_buy": self.evidence_refresh_required_before_manual_buy,
            "policy_flags": list(self.policy_flags),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "evidence_pack_mutation": self.evidence_pack_mutation,
            "local_cache_mutation": self.local_cache_mutation,
            "portfolio_state_mutation": self.portfolio_state_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _today_iso() -> str:
    return date.today().isoformat()


def _round2(value: float | int | None) -> float:
    if value is None:
        return 0.0
    return round(float(value), 2)


def _dedupe(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _action_text(action: PlatformLaneAction) -> str:
    if action.lane == "cash_reserve":
        return f"Top up emergency fund manually on {action.platform}."
    if action.lane == "crypto":
        return f"Review crypto evidence, then buy manually on {action.platform} if satisfied."
    if action.lane == "stock_fund_etf":
        return f"Review ETF/fund evidence, then buy manually on {action.platform} if satisfied."
    if action.lane == "individual_stock":
        return f"Keep individual-stock action at 0 EUR on {action.platform}; stock-specific evidence is not complete."
    if action.lane == "legacy_positions":
        return "Observe legacy positions only; no selling or migration without a separate review."
    return f"Review {action.lane} manually on {action.platform}."


def _weekly_actions_from_policy(policy: PlatformLanePolicyResult) -> tuple[WeeklyPlatformAction, ...]:
    actions: list[WeeklyPlatformAction] = []
    for idx, item in enumerate(policy.platform_actions, start=1):
        allowed = item.amount_eur > 0 and not item.review_only and not policy.blockers
        actions.append(
            WeeklyPlatformAction(
                step=idx,
                platform=item.platform,
                lane=item.lane,
                amount_eur=_round2(item.amount_eur),
                manual_action=_action_text(item),
                review_only=item.review_only,
                manual_only=True,
                action_allowed_by_policy=allowed,
                policy_note=item.policy_note,
            )
        )
    return tuple(actions)


def build_platform_aware_weekly_action_packet_result(
    *,
    current_date: str | None = None,
    snapshot_path: str | Path = DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH,
    monthly_contribution_eur: float | None = None,
    monthly_expenses_eur: float | None = None,
    minimum_emergency_months: float = DEFAULT_MIN_EMERGENCY_MONTHS,
    ideal_emergency_months: float = DEFAULT_IDEAL_EMERGENCY_MONTHS,
    age_years: int | None = DEFAULT_AGE_YEARS,
    new_investing_platform: str = "Lightyear",
    crypto_platform: str = "LHV",
    cash_emergency_platform: str = "LHV",
    legacy_positions_mode: str = "LEGACY_OBSERVED_ONLY",
) -> PlatformAwareWeeklyActionPacketResult:
    effective_date = current_date or _today_iso()
    policy = build_platform_lane_policy_result(
        current_date=effective_date,
        snapshot_path=snapshot_path,
        monthly_contribution_eur=monthly_contribution_eur,
        monthly_expenses_eur=monthly_expenses_eur,
        minimum_emergency_months=minimum_emergency_months,
        ideal_emergency_months=ideal_emergency_months,
        age_years=age_years,
        new_investing_platform=new_investing_platform,
        crypto_platform=crypto_platform,
        cash_emergency_platform=cash_emergency_platform,
        legacy_positions_mode=legacy_positions_mode,
        legacy_sell_allowed=False,
    )

    weekly_actions = _weekly_actions_from_policy(policy)
    total_amount = round(sum(action.amount_eur for action in weekly_actions if action.amount_eur > 0), 2)

    warnings = list(policy.warnings)
    flags = list(policy.platform_policy_flags)
    blockers = list(policy.blockers)

    if policy.blockers:
        status = STATUS_BLOCKED
        packet_status = PACKET_BLOCKED
    elif warnings or flags:
        status = STATUS_REVIEW_REQUIRED
        packet_status = PACKET_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        packet_status = PACKET_READY

    warnings.append("refresh public evidence before any real-world manual buy")
    flags.append("PLATFORM_AWARE_WEEKLY_PACKET_MANUAL_ONLY")
    flags.append("NO_LEGACY_SELL_WITHOUT_MIGRATION_REVIEW")

    return PlatformAwareWeeklyActionPacketResult(
        status=status,
        packet_status=packet_status,
        current_date=effective_date,
        snapshot_path=str(snapshot_path),
        snapshot_ready=policy.snapshot_ready,
        monthly_contribution_eur=monthly_contribution_eur,
        monthly_expenses_eur=monthly_expenses_eur,
        emergency_top_up_eur=policy.suggested_monthly_emergency_top_up_eur,
        investable_after_emergency_eur=policy.suggested_monthly_investment_after_emergency_eur,
        new_investing_platform=policy.new_investing_platform,
        crypto_platform=policy.crypto_platform,
        cash_emergency_platform=policy.cash_emergency_platform,
        legacy_positions_mode=policy.legacy_positions_mode,
        weekly_actions=weekly_actions,
        total_manual_action_amount_eur=total_amount,
        legacy_sell_allowed=policy.legacy_sell_allowed,
        evidence_refresh_required_before_manual_buy=True,
        policy_flags=_dedupe(flags),
        blockers=_dedupe(blockers),
        warnings=_dedupe(warnings),
        allocation_mutation=False,
        approval_ticket_mutation=False,
        evidence_pack_mutation=False,
        local_cache_mutation=False,
        portfolio_state_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
    )


def format_platform_aware_weekly_action_packet(result: PlatformAwareWeeklyActionPacketResult) -> str:
    lines = [
        "J.A.R.V.I.S. WEEKLY PLATFORM ACTION PACKET",
        f"status: {result.status}",
        f"packet status: {result.packet_status}",
        f"current date: {result.current_date}",
        f"snapshot path: {result.snapshot_path}",
        f"snapshot ready: {result.snapshot_ready}",
        "",
        "Monthly policy:",
        f"- monthly contribution EUR: {result.monthly_contribution_eur}",
        f"- monthly expenses EUR: {result.monthly_expenses_eur}",
        f"- emergency top-up EUR: {result.emergency_top_up_eur}",
        f"- investable after emergency EUR: {result.investable_after_emergency_eur}",
        "",
        "Platform map:",
        f"- cash/emergency: {result.cash_emergency_platform}",
        f"- crypto: {result.crypto_platform}",
        f"- ETF/stock/fund: {result.new_investing_platform}",
        f"- legacy positions: {result.legacy_positions_mode}",
        "",
        "Manual weekly actions:",
    ]

    for action in result.weekly_actions:
        lines.append(
            f"{action.step}. {action.platform} / {action.lane}: {action.amount_eur} EUR; allowed by policy={action.action_allowed_by_policy}; review only={action.review_only}"
        )
        lines.append(f"   action: {action.manual_action}")
        lines.append(f"   note: {action.policy_note}")

    lines.extend(
        [
            "",
            f"Total positive manual action amount EUR: {result.total_manual_action_amount_eur}",
            f"Evidence refresh required before manual buy: {result.evidence_refresh_required_before_manual_buy}",
            "",
            "Safety:",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
            f"- evidence pack mutation: {result.evidence_pack_mutation}",
            f"- local cache mutation: {result.local_cache_mutation}",
            f"- portfolio state mutation: {result.portfolio_state_mutation}",
            f"- buy request created: {result.buy_request_created}",
            "- no broker connection",
            "- no credentials",
            "- no private account data ingestion",
            "- no orders created",
            "- no trades executed",
        ]
    )

    if result.policy_flags:
        lines.extend(["", "Policy flags:"])
        lines.extend(f"- {item}" for item in result.policy_flags)
    else:
        lines.extend(["", "Policy flags: none"])

    if result.blockers:
        lines.extend(["", "Blockers:"])
        lines.extend(f"- {item}" for item in result.blockers)
    else:
        lines.append("blockers: none")

    if result.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {item}" for item in result.warnings)
    else:
        lines.append("warnings: none")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a platform-aware weekly manual action packet.")
    parser.add_argument("--weekly-platform-action-packet", action="store_true")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--manual-portfolio-snapshot-path", default=DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH)
    parser.add_argument("--monthly-contribution-eur", type=float, default=None)
    parser.add_argument("--monthly-expenses-eur", type=float, default=None)
    parser.add_argument("--minimum-emergency-months", type=float, default=DEFAULT_MIN_EMERGENCY_MONTHS)
    parser.add_argument("--ideal-emergency-months", type=float, default=DEFAULT_IDEAL_EMERGENCY_MONTHS)
    parser.add_argument("--age-years", type=int, default=DEFAULT_AGE_YEARS)
    parser.add_argument("--new-investing-platform", default="Lightyear")
    parser.add_argument("--crypto-platform", default="LHV")
    parser.add_argument("--cash-emergency-platform", default="LHV")
    parser.add_argument("--legacy-positions-mode", default="LEGACY_OBSERVED_ONLY")
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_platform_aware_weekly_action_packet_result(
        current_date=args.current_date,
        snapshot_path=args.manual_portfolio_snapshot_path,
        monthly_contribution_eur=args.monthly_contribution_eur,
        monthly_expenses_eur=args.monthly_expenses_eur,
        minimum_emergency_months=args.minimum_emergency_months,
        ideal_emergency_months=args.ideal_emergency_months,
        age_years=args.age_years,
        new_investing_platform=args.new_investing_platform,
        crypto_platform=args.crypto_platform,
        cash_emergency_platform=args.cash_emergency_platform,
        legacy_positions_mode=args.legacy_positions_mode,
    )
    print(format_platform_aware_weekly_action_packet(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())