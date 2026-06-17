"""J.A.R.V.I.S. v53.0 portfolio exposure and dynamic emergency fund audit.

Reads the local brokerless manual snapshot and calculates emergency-fund policy
from monthly expenses instead of relying on a fixed arbitrary target.

This stage is audit/advice-prep only. It does not mutate allocation, approve
buys, create buy requests, connect to brokers, create orders, or execute trades.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from jarvis.jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from jarvis.runtime.manual_portfolio_snapshot import DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH

STATUS_READY = "JARVIS_V53_0_DYNAMIC_EMERGENCY_FUND_POLICY_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V53_0_DYNAMIC_EMERGENCY_FUND_POLICY_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V53_0_DYNAMIC_EMERGENCY_FUND_POLICY_BLOCKED_SAFE"

AUDIT_READY = "DYNAMIC_EMERGENCY_FUND_POLICY_READY"
AUDIT_REVIEW_REQUIRED = "DYNAMIC_EMERGENCY_FUND_POLICY_REVIEW_REQUIRED"
AUDIT_BLOCKED = "DYNAMIC_EMERGENCY_FUND_POLICY_BLOCKED"

DEFAULT_MIN_EMERGENCY_MONTHS = 3.0
DEFAULT_IDEAL_EMERGENCY_MONTHS = 6.0
DEFAULT_TINY_POSITION_THRESHOLD_EUR = 5.0


@dataclass(frozen=True)
class LaneExposure:
    lane: str
    market_value_eur: float
    pct_of_total_visible: float | None
    pct_of_invested_assets: float | None
    holdings_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane": self.lane,
            "market_value_eur": self.market_value_eur,
            "pct_of_total_visible": self.pct_of_total_visible,
            "pct_of_invested_assets": self.pct_of_invested_assets,
            "holdings_count": self.holdings_count,
        }


@dataclass(frozen=True)
class PositionFlag:
    flag_type: str
    instrument_id: str
    asset_name: str
    lane: str
    market_value_eur: float
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "flag_type": self.flag_type,
            "instrument_id": self.instrument_id,
            "asset_name": self.asset_name,
            "lane": self.lane,
            "market_value_eur": self.market_value_eur,
            "message": self.message,
        }


@dataclass(frozen=True)
class PortfolioExposureDynamicEmergencyFundAuditResult:
    status: str
    audit_status: str
    current_date: str
    snapshot_path: str
    snapshot_ready: bool
    monthly_contribution_eur: float | None
    monthly_expenses_eur: float | None
    minimum_emergency_months: float
    ideal_emergency_months: float
    minimum_emergency_target_eur: float | None
    ideal_emergency_target_eur: float | None
    emergency_fund_current_eur: float
    emergency_months_covered: float | None
    minimum_emergency_gap_eur: float | None
    ideal_emergency_gap_eur: float | None
    emergency_fund_decision: str
    emergency_fund_action: str
    suggested_monthly_emergency_top_up_eur: float | None
    suggested_monthly_investment_after_emergency_eur: float | None
    visible_cash_excluding_emergency_eur: float
    visible_invested_assets_eur: float
    visible_total_excluding_emergency_eur: float
    visible_total_including_emergency_eur: float
    lane_exposures: tuple[LaneExposure, ...]
    position_flags: tuple[PositionFlag, ...]
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "audit_status": self.audit_status,
            "current_date": self.current_date,
            "snapshot_path": self.snapshot_path,
            "snapshot_ready": self.snapshot_ready,
            "monthly_contribution_eur": self.monthly_contribution_eur,
            "monthly_expenses_eur": self.monthly_expenses_eur,
            "minimum_emergency_months": self.minimum_emergency_months,
            "ideal_emergency_months": self.ideal_emergency_months,
            "minimum_emergency_target_eur": self.minimum_emergency_target_eur,
            "ideal_emergency_target_eur": self.ideal_emergency_target_eur,
            "emergency_fund_current_eur": self.emergency_fund_current_eur,
            "emergency_months_covered": self.emergency_months_covered,
            "minimum_emergency_gap_eur": self.minimum_emergency_gap_eur,
            "ideal_emergency_gap_eur": self.ideal_emergency_gap_eur,
            "emergency_fund_decision": self.emergency_fund_decision,
            "emergency_fund_action": self.emergency_fund_action,
            "suggested_monthly_emergency_top_up_eur": self.suggested_monthly_emergency_top_up_eur,
            "suggested_monthly_investment_after_emergency_eur": self.suggested_monthly_investment_after_emergency_eur,
            "visible_cash_excluding_emergency_eur": self.visible_cash_excluding_emergency_eur,
            "visible_invested_assets_eur": self.visible_invested_assets_eur,
            "visible_total_excluding_emergency_eur": self.visible_total_excluding_emergency_eur,
            "visible_total_including_emergency_eur": self.visible_total_including_emergency_eur,
            "lane_exposures": [item.to_dict() for item in self.lane_exposures],
            "position_flags": [item.to_dict() for item in self.position_flags],
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def _today_iso() -> str:
    return date.today().isoformat()


def _round2(value: float | int | None) -> float | None:
    if value is None:
        return None
    return round(float(value) + 0.0, 2)


def _dedupe(items: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _load_snapshot(path: Path) -> Mapping[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


def _safe_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    return default


def _holdings(snapshot: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    holdings = snapshot.get("holdings")
    return [item for item in holdings if isinstance(item, Mapping)] if isinstance(holdings, list) else []


def _market_value(item: Mapping[str, Any]) -> float:
    return _safe_float(item.get("market_value_eur"), 0.0)


def _pct(part: float, whole: float) -> float | None:
    if whole <= 0:
        return None
    return round((part / whole) * 100.0, 2)


def _lane_exposures(holdings: Sequence[Mapping[str, Any]], total_visible: float, invested_assets: float) -> tuple[LaneExposure, ...]:
    buckets: dict[str, tuple[float, int]] = {}
    for item in holdings:
        lane = str(item.get("lane") or "unknown")
        value = _market_value(item)
        current_value, count = buckets.get(lane, (0.0, 0))
        buckets[lane] = (current_value + value, count + 1)

    return tuple(
        LaneExposure(
            lane=lane,
            market_value_eur=round(value, 2),
            pct_of_total_visible=_pct(value, total_visible),
            pct_of_invested_assets=_pct(value, invested_assets) if lane not in {"cash", "cash_reserve"} else None,
            holdings_count=count,
        )
        for lane, (value, count) in sorted(buckets.items(), key=lambda item: item[0])
    )


def _position_flags(holdings: Sequence[Mapping[str, Any]], tiny_threshold_eur: float) -> tuple[PositionFlag, ...]:
    flags: list[PositionFlag] = []
    risk_holdings = [item for item in holdings if str(item.get("lane")) not in {"cash", "cash_reserve"}]
    invested_assets = sum(_market_value(item) for item in risk_holdings)

    for item in risk_holdings:
        value = _market_value(item)
        name = str(item.get("asset_name") or item.get("symbol") or "unknown")
        instrument_id = str(item.get("instrument_id") or item.get("symbol") or "unknown")
        lane = str(item.get("lane") or "unknown")

        if 0 < value < tiny_threshold_eur:
            flags.append(
                PositionFlag(
                    flag_type="TINY_RESIDUAL_POSITION",
                    instrument_id=instrument_id,
                    asset_name=name,
                    lane=lane,
                    market_value_eur=round(value, 2),
                    message=f"Position is below {tiny_threshold_eur:.2f} EUR and may be operational noise.",
                )
            )

        pct_invested = _pct(value, invested_assets)
        if pct_invested is not None and pct_invested >= 50.0:
            flags.append(
                PositionFlag(
                    flag_type="TOP_HOLDING_CONCENTRATION_REVIEW",
                    instrument_id=instrument_id,
                    asset_name=name,
                    lane=lane,
                    market_value_eur=round(value, 2),
                    message=f"Position is {pct_invested:.2f}% of visible invested assets.",
                )
            )

    return tuple(flags)


def _dynamic_emergency_policy(
    *,
    emergency_current: float,
    monthly_expenses: float | None,
    monthly_contribution: float | None,
    minimum_months: float,
    ideal_months: float,
) -> tuple[
    str,
    str,
    float | None,
    float | None,
    float | None,
    float | None,
    float | None,
    float | None,
    float | None,
]:
    if monthly_expenses is None or monthly_expenses <= 0:
        return (
            "EXPENSES_REQUIRED_FOR_DYNAMIC_EMERGENCY_POLICY",
            "ASK_DIOGO_FOR_REAL_MONTHLY_EXPENSES_BEFORE_DECIDING_EMERGENCY_VS_INVEST",
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    min_target = round(monthly_expenses * minimum_months, 2)
    ideal_target = round(monthly_expenses * ideal_months, 2)
    months_covered = round(emergency_current / monthly_expenses, 2)
    min_gap = round(max(min_target - emergency_current, 0.0), 2)
    ideal_gap = round(max(ideal_target - emergency_current, 0.0), 2)

    if months_covered < minimum_months:
        decision = "BELOW_MINIMUM_EMERGENCY_FUND"
        action = "PRIORITIZE_EMERGENCY_FUND_UNTIL_MINIMUM_MONTHS_COVERED"
        top_up_goal = min_gap
    elif months_covered < ideal_months:
        decision = "MINIMUM_EMERGENCY_FUND_MET_IDEAL_NOT_MET"
        action = "SPLIT_MONTHLY_CONTRIBUTION_BETWEEN_EMERGENCY_TOP_UP_AND_INVESTING"
        top_up_goal = ideal_gap
    else:
        decision = "IDEAL_EMERGENCY_FUND_MET"
        action = "NO_EXTRA_EMERGENCY_TOP_UP_REQUIRED_BY_EXPENSE_POLICY"
        top_up_goal = 0.0

    emergency_top_up = None
    invest_after = None
    if monthly_contribution is not None and monthly_contribution >= 0:
        if decision == "BELOW_MINIMUM_EMERGENCY_FUND":
            emergency_top_up = min(monthly_contribution, top_up_goal)
        elif decision == "MINIMUM_EMERGENCY_FUND_MET_IDEAL_NOT_MET":
            emergency_top_up = min(75.0, round(monthly_contribution * 0.20, 2), top_up_goal)
        else:
            emergency_top_up = 0.0

        emergency_top_up = round(emergency_top_up, 2)
        invest_after = round(max(monthly_contribution - emergency_top_up, 0.0), 2)

    return (
        decision,
        action,
        months_covered,
        min_target,
        ideal_target,
        min_gap,
        ideal_gap,
        emergency_top_up,
        invest_after,
    )


def build_portfolio_exposure_dynamic_emergency_fund_audit_result(
    *,
    current_date: str | None = None,
    snapshot_path: str | Path = DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH,
    monthly_contribution_eur: float | None = None,
    monthly_expenses_eur: float | None = None,
    minimum_emergency_months: float = DEFAULT_MIN_EMERGENCY_MONTHS,
    ideal_emergency_months: float = DEFAULT_IDEAL_EMERGENCY_MONTHS,
    tiny_position_threshold_eur: float = DEFAULT_TINY_POSITION_THRESHOLD_EUR,
) -> PortfolioExposureDynamicEmergencyFundAuditResult:
    current_date_text = current_date or _today_iso()
    path = Path(snapshot_path)
    blockers: list[str] = []
    warnings: list[str] = []

    snapshot = _load_snapshot(path)
    if snapshot is None:
        blockers.append("manual portfolio snapshot missing or unreadable.")
        snapshot = {}

    snapshot_ready = bool(snapshot) and not bool(snapshot.get("is_template", False)) and bool(snapshot.get("brokerless_manual_snapshot", False))
    if not snapshot_ready:
        warnings.append("manual portfolio snapshot is not ready for exposure audit.")

    holdings = _holdings(snapshot)
    emergency_current = _safe_float(snapshot.get("emergency_fund_reserved_eur"), 0.0)
    cash_ex_emergency = _safe_float(snapshot.get("cash_eur"), 0.0)
    invested_assets = sum(_market_value(item) for item in holdings if str(item.get("lane")) not in {"cash", "cash_reserve"})

    totals = snapshot.get("totals") if isinstance(snapshot.get("totals"), Mapping) else {}
    visible_total_including_emergency = _safe_float(
        totals.get("visible_total_including_emergency_eur") if isinstance(totals, Mapping) else None,
        emergency_current + cash_ex_emergency + invested_assets,
    )
    visible_total_excluding_emergency = _safe_float(
        totals.get("visible_portfolio_excluding_emergency_eur") if isinstance(totals, Mapping) else None,
        cash_ex_emergency + invested_assets,
    )

    (
        decision,
        action,
        months_covered,
        min_target,
        ideal_target,
        min_gap,
        ideal_gap,
        emergency_top_up,
        invest_after,
    ) = _dynamic_emergency_policy(
        emergency_current=emergency_current,
        monthly_expenses=monthly_expenses_eur,
        monthly_contribution=monthly_contribution_eur,
        minimum_months=minimum_emergency_months,
        ideal_months=ideal_emergency_months,
    )

    if monthly_expenses_eur is None or monthly_expenses_eur <= 0:
        warnings.append("monthly expenses are required before J.A.R.V.I.S. can decide if emergency fund is good.")
    elif ideal_gap and ideal_gap > 0:
        warnings.append("emergency fund is below ideal months-of-expenses target.")

    lanes = _lane_exposures(holdings, visible_total_including_emergency, invested_assets)
    flags = _position_flags(holdings, tiny_position_threshold_eur)
    if flags:
        warnings.append("position flags require review.")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        audit_status = AUDIT_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        audit_status = AUDIT_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        audit_status = AUDIT_READY

    return PortfolioExposureDynamicEmergencyFundAuditResult(
        status=status,
        audit_status=audit_status,
        current_date=current_date_text,
        snapshot_path=str(path),
        snapshot_ready=snapshot_ready,
        monthly_contribution_eur=_round2(monthly_contribution_eur),
        monthly_expenses_eur=_round2(monthly_expenses_eur),
        minimum_emergency_months=minimum_emergency_months,
        ideal_emergency_months=ideal_emergency_months,
        minimum_emergency_target_eur=_round2(min_target),
        ideal_emergency_target_eur=_round2(ideal_target),
        emergency_fund_current_eur=_round2(emergency_current) or 0.0,
        emergency_months_covered=_round2(months_covered),
        minimum_emergency_gap_eur=_round2(min_gap),
        ideal_emergency_gap_eur=_round2(ideal_gap),
        emergency_fund_decision=decision,
        emergency_fund_action=action,
        suggested_monthly_emergency_top_up_eur=_round2(emergency_top_up),
        suggested_monthly_investment_after_emergency_eur=_round2(invest_after),
        visible_cash_excluding_emergency_eur=_round2(cash_ex_emergency) or 0.0,
        visible_invested_assets_eur=_round2(invested_assets) or 0.0,
        visible_total_excluding_emergency_eur=_round2(visible_total_excluding_emergency) or 0.0,
        visible_total_including_emergency_eur=_round2(visible_total_including_emergency) or 0.0,
        lane_exposures=lanes,
        position_flags=flags,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )


def format_portfolio_exposure_dynamic_emergency_fund_audit(
    result: PortfolioExposureDynamicEmergencyFundAuditResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. PORTFOLIO EXPOSURE + DYNAMIC EMERGENCY FUND AUDIT",
        f"status: {result.status}",
        f"audit status: {result.audit_status}",
        f"current date: {result.current_date}",
        f"snapshot path: {result.snapshot_path}",
        f"snapshot ready: {result.snapshot_ready}",
        "",
        "Portfolio totals:",
        f"- visible cash excluding emergency EUR: {result.visible_cash_excluding_emergency_eur}",
        f"- visible invested assets EUR: {result.visible_invested_assets_eur}",
        f"- visible total excluding emergency EUR: {result.visible_total_excluding_emergency_eur}",
        f"- visible total including emergency EUR: {result.visible_total_including_emergency_eur}",
        "",
        "Emergency fund policy:",
        "- target basis: monthly expenses, not fixed EUR",
        f"- monthly contribution EUR: {result.monthly_contribution_eur}",
        f"- monthly expenses EUR: {result.monthly_expenses_eur}",
        f"- minimum emergency months: {result.minimum_emergency_months}",
        f"- ideal emergency months: {result.ideal_emergency_months}",
        f"- current emergency fund EUR: {result.emergency_fund_current_eur}",
        f"- emergency months covered: {result.emergency_months_covered}",
        f"- minimum emergency target EUR: {result.minimum_emergency_target_eur}",
        f"- ideal emergency target EUR: {result.ideal_emergency_target_eur}",
        f"- minimum emergency gap EUR: {result.minimum_emergency_gap_eur}",
        f"- ideal emergency gap EUR: {result.ideal_emergency_gap_eur}",
        f"- decision: {result.emergency_fund_decision}",
        f"- action: {result.emergency_fund_action}",
        f"- suggested monthly emergency top-up EUR: {result.suggested_monthly_emergency_top_up_eur}",
        f"- suggested monthly investment after emergency EUR: {result.suggested_monthly_investment_after_emergency_eur}",
        "",
        "Lane exposure:",
    ]

    for lane in result.lane_exposures:
        lines.append(
            f"- {lane.lane}: {lane.market_value_eur} EUR; total pct: {lane.pct_of_total_visible}; invested pct: {lane.pct_of_invested_assets}; holdings: {lane.holdings_count}"
        )

    if result.position_flags:
        lines.extend(["", "Position flags:"])
        for flag in result.position_flags:
            lines.append(f"- {flag.flag_type}: {flag.asset_name} ({flag.market_value_eur} EUR) - {flag.message}")
    else:
        lines.extend(["", "Position flags: none"])

    lines.extend(
        [
            "",
            "Safety:",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
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
    parser = argparse.ArgumentParser(description="Audit portfolio exposure and dynamic emergency fund policy.")
    parser.add_argument("--portfolio-exposure-audit", action="store_true")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--manual-portfolio-snapshot-path", default=DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH)
    parser.add_argument("--monthly-contribution-eur", type=float, default=None)
    parser.add_argument("--monthly-expenses-eur", type=float, default=None)
    parser.add_argument("--minimum-emergency-months", type=float, default=DEFAULT_MIN_EMERGENCY_MONTHS)
    parser.add_argument("--ideal-emergency-months", type=float, default=DEFAULT_IDEAL_EMERGENCY_MONTHS)
    parser.add_argument("--tiny-position-threshold-eur", type=float, default=DEFAULT_TINY_POSITION_THRESHOLD_EUR)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_portfolio_exposure_dynamic_emergency_fund_audit_result(
        current_date=args.current_date,
        snapshot_path=args.manual_portfolio_snapshot_path,
        monthly_contribution_eur=args.monthly_contribution_eur,
        monthly_expenses_eur=args.monthly_expenses_eur,
        minimum_emergency_months=args.minimum_emergency_months,
        ideal_emergency_months=args.ideal_emergency_months,
        tiny_position_threshold_eur=args.tiny_position_threshold_eur,
    )
    print(format_portfolio_exposure_dynamic_emergency_fund_audit(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())