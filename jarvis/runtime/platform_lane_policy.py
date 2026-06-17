"""J.A.R.V.I.S. v55.0 platform lane policy engine.

This stage maps the v54 dynamic target policy to platform-specific lanes:
- LHV: cash, emergency fund, and crypto.
- Lightyear: ETF/fund/stock long-term investing.
- Legacy positions: observed only; no automatic sell/migration.

Safety invariant:
Automated research. Manual trust. Manual approval. No execution.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.dynamic_target_policy import (
    DynamicTargetPolicyResult,
    build_dynamic_target_policy_result,
)
from jarvis.runtime.manual_portfolio_snapshot import DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH
from jarvis.runtime.portfolio_exposure_audit import (
    DEFAULT_IDEAL_EMERGENCY_MONTHS,
    DEFAULT_MIN_EMERGENCY_MONTHS,
)

STATUS_READY = "JARVIS_V55_0_PLATFORM_LANE_POLICY_ENGINE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V55_0_PLATFORM_LANE_POLICY_ENGINE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V55_0_PLATFORM_LANE_POLICY_ENGINE_BLOCKED_SAFE"

POLICY_READY = "PLATFORM_LANE_POLICY_READY"
POLICY_REVIEW_REQUIRED = "PLATFORM_LANE_POLICY_REVIEW_REQUIRED"
POLICY_BLOCKED = "PLATFORM_LANE_POLICY_BLOCKED"

DEFAULT_LHV_PLATFORM = "LHV"
DEFAULT_LIGHTYEAR_PLATFORM = "Lightyear"
DEFAULT_LEGACY_MODE = "LEGACY_OBSERVED_ONLY"
DEFAULT_AGE_YEARS = 26


@dataclass(frozen=True)
class PlatformLaneAction:
    platform: str
    lane: str
    amount_eur: float
    action_type: str
    review_only: bool
    manual_only: bool
    policy_note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "platform": self.platform,
            "lane": self.lane,
            "amount_eur": self.amount_eur,
            "action_type": self.action_type,
            "review_only": self.review_only,
            "manual_only": self.manual_only,
            "policy_note": self.policy_note,
        }


@dataclass(frozen=True)
class PlatformLanePolicyResult:
    status: str
    policy_status: str
    current_date: str
    snapshot_path: str
    snapshot_ready: bool
    legacy_positions_mode: str
    legacy_sell_allowed: bool
    new_investing_platform: str
    crypto_platform: str
    cash_emergency_platform: str
    monthly_contribution_eur: float | None
    monthly_expenses_eur: float | None
    suggested_monthly_emergency_top_up_eur: float | None
    suggested_monthly_investment_after_emergency_eur: float | None
    dynamic_policy_status: str
    platform_actions: tuple[PlatformLaneAction, ...]
    platform_policy_flags: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    allocation_mutation: bool
    approval_ticket_mutation: bool
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
            "policy_status": self.policy_status,
            "current_date": self.current_date,
            "snapshot_path": self.snapshot_path,
            "snapshot_ready": self.snapshot_ready,
            "legacy_positions_mode": self.legacy_positions_mode,
            "legacy_sell_allowed": self.legacy_sell_allowed,
            "new_investing_platform": self.new_investing_platform,
            "crypto_platform": self.crypto_platform,
            "cash_emergency_platform": self.cash_emergency_platform,
            "monthly_contribution_eur": self.monthly_contribution_eur,
            "monthly_expenses_eur": self.monthly_expenses_eur,
            "suggested_monthly_emergency_top_up_eur": self.suggested_monthly_emergency_top_up_eur,
            "suggested_monthly_investment_after_emergency_eur": self.suggested_monthly_investment_after_emergency_eur,
            "dynamic_policy_status": self.dynamic_policy_status,
            "platform_actions": [action.to_dict() for action in self.platform_actions],
            "platform_policy_flags": list(self.platform_policy_flags),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
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


def _amount(dynamic: DynamicTargetPolicyResult, lane: str) -> float:
    for item in dynamic.proposed_contribution_targets:
        if item.lane == lane:
            return _round2(item.amount_eur)
    return 0.0


def _dedupe(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(item for item in items if item))


def _build_actions(
    *,
    dynamic: DynamicTargetPolicyResult,
    lhv_platform: str,
    lightyear_platform: str,
) -> tuple[PlatformLaneAction, ...]:
    emergency_amount = _round2(dynamic.suggested_monthly_emergency_top_up_eur)
    crypto_amount = _amount(dynamic, "crypto")
    etf_amount = _amount(dynamic, "stock_fund_etf")
    stock_amount = _amount(dynamic, "individual_stock")

    return (
        PlatformLaneAction(
            platform=lhv_platform,
            lane="cash_reserve",
            amount_eur=emergency_amount,
            action_type="manual_emergency_fund_top_up",
            review_only=False,
            manual_only=True,
            policy_note="Emergency fund and cash reserve stay at LHV.",
        ),
        PlatformLaneAction(
            platform=lhv_platform,
            lane="crypto",
            amount_eur=crypto_amount,
            action_type="manual_crypto_buy_review",
            review_only=False,
            manual_only=True,
            policy_note="Crypto investing stays at LHV for platform/perk reasons and remains capped by v54 target policy.",
        ),
        PlatformLaneAction(
            platform=lightyear_platform,
            lane="stock_fund_etf",
            amount_eur=etf_amount,
            action_type="manual_lightyear_core_etf_fund_buy_review",
            review_only=False,
            manual_only=True,
            policy_note="ETF/fund/core long-term investing starts clean on Lightyear.",
        ),
        PlatformLaneAction(
            platform=lightyear_platform,
            lane="individual_stock",
            amount_eur=stock_amount,
            action_type="manual_lightyear_individual_stock_review_only",
            review_only=True,
            manual_only=True,
            policy_note="Individual stocks are Lightyear-eligible later, but remain 0 EUR until stock-specific evidence is approved.",
        ),
        PlatformLaneAction(
            platform="legacy_observed",
            lane="legacy_positions",
            amount_eur=0.0,
            action_type="observe_only_no_new_money_no_auto_sell",
            review_only=True,
            manual_only=True,
            policy_note="Old ETF/fund positions are tracked for net worth and risk; selling requires a separate migration review.",
        ),
    )


def build_platform_lane_policy_result(
    *,
    current_date: str | None = None,
    snapshot_path: str | Path = DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH,
    monthly_contribution_eur: float | None = None,
    monthly_expenses_eur: float | None = None,
    minimum_emergency_months: float = DEFAULT_MIN_EMERGENCY_MONTHS,
    ideal_emergency_months: float = DEFAULT_IDEAL_EMERGENCY_MONTHS,
    age_years: int | None = DEFAULT_AGE_YEARS,
    new_investing_platform: str = DEFAULT_LIGHTYEAR_PLATFORM,
    crypto_platform: str = DEFAULT_LHV_PLATFORM,
    cash_emergency_platform: str = DEFAULT_LHV_PLATFORM,
    legacy_positions_mode: str = DEFAULT_LEGACY_MODE,
    legacy_sell_allowed: bool = False,
) -> PlatformLanePolicyResult:
    effective_date = current_date or _today_iso()
    dynamic = build_dynamic_target_policy_result(
        current_date=effective_date,
        snapshot_path=snapshot_path,
        monthly_contribution_eur=monthly_contribution_eur,
        monthly_expenses_eur=monthly_expenses_eur,
        minimum_emergency_months=minimum_emergency_months,
        ideal_emergency_months=ideal_emergency_months,
        age_years=age_years,
    )

    blockers = list(dynamic.blockers)
    warnings = list(dynamic.warnings)
    flags: list[str] = []

    if not dynamic.snapshot_ready:
        blockers.append("manual_portfolio_snapshot_required")
    if not new_investing_platform:
        blockers.append("new_investing_platform_required")
    if not crypto_platform:
        blockers.append("crypto_platform_required")
    if legacy_sell_allowed:
        blockers.append("legacy_sell_requires_separate_manual_migration_review")
    else:
        flags.append("LEGACY_SELL_BLOCKED_BY_DEFAULT")

    if new_investing_platform.lower() == crypto_platform.lower():
        warnings.append("crypto and ETF/stock/fund platforms are the same; clean-start separation is not active")
    else:
        flags.append("ETF_STOCK_FUND_NEW_MONEY_TO_LIGHTYEAR")
        flags.append("CRYPTO_NEW_MONEY_TO_LHV")

    if legacy_positions_mode != DEFAULT_LEGACY_MODE:
        warnings.append("legacy positions mode differs from observed-only default")
    else:
        flags.append("LEGACY_POSITIONS_OBSERVED_ONLY")

    actions = _build_actions(
        dynamic=dynamic,
        lhv_platform=crypto_platform,
        lightyear_platform=new_investing_platform,
    )

    if blockers:
        status = STATUS_BLOCKED
        policy_status = POLICY_BLOCKED
    elif warnings or flags:
        status = STATUS_REVIEW_REQUIRED
        policy_status = POLICY_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        policy_status = POLICY_READY

    return PlatformLanePolicyResult(
        status=status,
        policy_status=policy_status,
        current_date=effective_date,
        snapshot_path=str(snapshot_path),
        snapshot_ready=dynamic.snapshot_ready,
        legacy_positions_mode=legacy_positions_mode,
        legacy_sell_allowed=legacy_sell_allowed,
        new_investing_platform=new_investing_platform,
        crypto_platform=crypto_platform,
        cash_emergency_platform=cash_emergency_platform,
        monthly_contribution_eur=monthly_contribution_eur,
        monthly_expenses_eur=monthly_expenses_eur,
        suggested_monthly_emergency_top_up_eur=dynamic.suggested_monthly_emergency_top_up_eur,
        suggested_monthly_investment_after_emergency_eur=dynamic.suggested_monthly_investment_after_emergency_eur,
        dynamic_policy_status=dynamic.policy_status,
        platform_actions=actions,
        platform_policy_flags=_dedupe(flags),
        blockers=_dedupe(blockers),
        warnings=_dedupe(warnings),
        allocation_mutation=False,
        approval_ticket_mutation=False,
        portfolio_state_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
    )


def format_platform_lane_policy(result: PlatformLanePolicyResult) -> str:
    lines = [
        "J.A.R.V.I.S. PLATFORM LANE POLICY ENGINE",
        f"status: {result.status}",
        f"policy status: {result.policy_status}",
        f"current date: {result.current_date}",
        f"snapshot path: {result.snapshot_path}",
        f"snapshot ready: {result.snapshot_ready}",
        "",
        "Platform map:",
        f"- cash/emergency platform: {result.cash_emergency_platform}",
        f"- crypto platform: {result.crypto_platform}",
        f"- ETF/stock/fund new investing platform: {result.new_investing_platform}",
        f"- legacy positions mode: {result.legacy_positions_mode}",
        f"- legacy sell allowed: {result.legacy_sell_allowed}",
        "",
        "Contribution policy:",
        f"- monthly contribution EUR: {result.monthly_contribution_eur}",
        f"- monthly expenses EUR: {result.monthly_expenses_eur}",
        f"- emergency top-up EUR: {result.suggested_monthly_emergency_top_up_eur}",
        f"- investment after emergency EUR: {result.suggested_monthly_investment_after_emergency_eur}",
        "",
        "Platform actions:",
    ]

    for action in result.platform_actions:
        lines.append(
            f"- {action.platform} / {action.lane}: {action.amount_eur} EUR; action={action.action_type}; review only={action.review_only}; manual only={action.manual_only}"
        )
        lines.append(f"  note: {action.policy_note}")

    if result.platform_policy_flags:
        lines.extend(["", "Platform policy flags:"])
        lines.extend(f"- {flag}" for flag in result.platform_policy_flags)
    else:
        lines.extend(["", "Platform policy flags: none"])

    lines.extend(
        [
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
        ]
    )

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
    parser = argparse.ArgumentParser(description="Build platform lane policy for LHV crypto and Lightyear ETF/stock/fund investing.")
    parser.add_argument("--platform-lane-policy", action="store_true")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--manual-portfolio-snapshot-path", default=DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH)
    parser.add_argument("--monthly-contribution-eur", type=float, default=None)
    parser.add_argument("--monthly-expenses-eur", type=float, default=None)
    parser.add_argument("--minimum-emergency-months", type=float, default=DEFAULT_MIN_EMERGENCY_MONTHS)
    parser.add_argument("--ideal-emergency-months", type=float, default=DEFAULT_IDEAL_EMERGENCY_MONTHS)
    parser.add_argument("--age-years", type=int, default=DEFAULT_AGE_YEARS)
    parser.add_argument("--new-investing-platform", default=DEFAULT_LIGHTYEAR_PLATFORM)
    parser.add_argument("--crypto-platform", default=DEFAULT_LHV_PLATFORM)
    parser.add_argument("--cash-emergency-platform", default=DEFAULT_LHV_PLATFORM)
    parser.add_argument("--legacy-positions-mode", default=DEFAULT_LEGACY_MODE)
    parser.add_argument("--legacy-sell-allowed", action="store_true")
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_platform_lane_policy_result(
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
        legacy_sell_allowed=args.legacy_sell_allowed,
    )
    print(format_platform_lane_policy(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())