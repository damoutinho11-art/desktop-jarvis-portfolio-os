"""J.A.R.V.I.S. v54.0 dynamic target policy engine.

This stage turns the real manual snapshot, monthly expenses, emergency-fund
state, and monthly contribution into a target-policy layer. It is not a full
allocator and does not execute trades.

Safety invariant:
Automated research. Manual trust. Manual approval. No execution.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Sequence

from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.manual_portfolio_snapshot import DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH
from jarvis.runtime.portfolio_exposure_audit import (
    DEFAULT_IDEAL_EMERGENCY_MONTHS,
    DEFAULT_MIN_EMERGENCY_MONTHS,
    PortfolioExposureDynamicEmergencyFundAuditResult,
    build_portfolio_exposure_dynamic_emergency_fund_audit_result,
)

STATUS_READY = "JARVIS_V54_0_DYNAMIC_TARGET_POLICY_ENGINE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V54_0_DYNAMIC_TARGET_POLICY_ENGINE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V54_0_DYNAMIC_TARGET_POLICY_ENGINE_BLOCKED_SAFE"

POLICY_READY = "DYNAMIC_TARGET_POLICY_READY"
POLICY_REVIEW_REQUIRED = "DYNAMIC_TARGET_POLICY_REVIEW_REQUIRED"
POLICY_BLOCKED = "DYNAMIC_TARGET_POLICY_BLOCKED"

DEFAULT_AGE_YEARS = 26
DEFAULT_CRYPTO_TARGET_FLOOR_PCT = 5.0
DEFAULT_CRYPTO_TARGET_CEILING_PCT = 10.0
DEFAULT_CORE_TARGET_FLOOR_PCT = 80.0
DEFAULT_CORE_TARGET_CEILING_PCT = 90.0
DEFAULT_INDIVIDUAL_STOCK_TARGET_CEILING_PCT = 10.0
DEFAULT_CRYPTO_CONTRIBUTION_CAP_PCT = 40.0


@dataclass(frozen=True)
class TargetBand:
    lane: str
    role: str
    target_floor_pct: float | None
    target_mid_pct: float | None
    target_ceiling_pct: float | None
    current_pct_of_invested_assets: float | None
    policy_note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane": self.lane,
            "role": self.role,
            "target_floor_pct": self.target_floor_pct,
            "target_mid_pct": self.target_mid_pct,
            "target_ceiling_pct": self.target_ceiling_pct,
            "current_pct_of_invested_assets": self.current_pct_of_invested_assets,
            "policy_note": self.policy_note,
        }


@dataclass(frozen=True)
class ContributionTarget:
    lane: str
    amount_eur: float
    review_only: bool
    policy_note: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "lane": self.lane,
            "amount_eur": self.amount_eur,
            "review_only": self.review_only,
            "policy_note": self.policy_note,
        }


@dataclass(frozen=True)
class DynamicTargetPolicyResult:
    status: str
    policy_status: str
    current_date: str
    snapshot_path: str
    snapshot_ready: bool
    age_years: int | None
    risk_profile: str
    monthly_contribution_eur: float | None
    monthly_expenses_eur: float | None
    emergency_fund_current_eur: float
    emergency_months_covered: float | None
    minimum_emergency_target_eur: float | None
    ideal_emergency_target_eur: float | None
    suggested_monthly_emergency_top_up_eur: float | None
    suggested_monthly_investment_after_emergency_eur: float | None
    target_bands: tuple[TargetBand, ...]
    proposed_contribution_targets: tuple[ContributionTarget, ...]
    policy_flags: tuple[str, ...]
    full_allocation_still_requires: tuple[str, ...]
    target_policy_data_gate_covered: bool
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
            "policy_status": self.policy_status,
            "current_date": self.current_date,
            "snapshot_path": self.snapshot_path,
            "snapshot_ready": self.snapshot_ready,
            "age_years": self.age_years,
            "risk_profile": self.risk_profile,
            "monthly_contribution_eur": self.monthly_contribution_eur,
            "monthly_expenses_eur": self.monthly_expenses_eur,
            "emergency_fund_current_eur": self.emergency_fund_current_eur,
            "emergency_months_covered": self.emergency_months_covered,
            "minimum_emergency_target_eur": self.minimum_emergency_target_eur,
            "ideal_emergency_target_eur": self.ideal_emergency_target_eur,
            "suggested_monthly_emergency_top_up_eur": self.suggested_monthly_emergency_top_up_eur,
            "suggested_monthly_investment_after_emergency_eur": self.suggested_monthly_investment_after_emergency_eur,
            "target_bands": [band.to_dict() for band in self.target_bands],
            "proposed_contribution_targets": [target.to_dict() for target in self.proposed_contribution_targets],
            "policy_flags": list(self.policy_flags),
            "full_allocation_still_requires": list(self.full_allocation_still_requires),
            "target_policy_data_gate_covered": self.target_policy_data_gate_covered,
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
    return round(float(value), 2)


def _dedupe(items: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _lane_pct(base: PortfolioExposureDynamicEmergencyFundAuditResult, lane: str) -> float | None:
    for item in base.lane_exposures:
        if item.lane == lane:
            return item.pct_of_invested_assets
    return None


def _target_mid(floor: float, ceiling: float) -> float:
    return round((floor + ceiling) / 2.0, 2)


def _build_target_bands(base: PortfolioExposureDynamicEmergencyFundAuditResult) -> tuple[TargetBand, ...]:
    crypto_pct = _lane_pct(base, "crypto")
    core_pct = _lane_pct(base, "stock_fund_etf")

    return (
        TargetBand(
            lane="cash_reserve",
            role="protected emergency reserve, not an investment sleeve",
            target_floor_pct=None,
            target_mid_pct=None,
            target_ceiling_pct=None,
            current_pct_of_invested_assets=None,
            policy_note="Target is measured in months of expenses, not portfolio percent.",
        ),
        TargetBand(
            lane="stock_fund_etf",
            role="core long-term compounding sleeve",
            target_floor_pct=DEFAULT_CORE_TARGET_FLOOR_PCT,
            target_mid_pct=_target_mid(DEFAULT_CORE_TARGET_FLOOR_PCT, DEFAULT_CORE_TARGET_CEILING_PCT),
            target_ceiling_pct=DEFAULT_CORE_TARGET_CEILING_PCT,
            current_pct_of_invested_assets=core_pct,
            policy_note="Use broad ETF/fund exposure as the core sleeve until a risk model and richer evidence exist.",
        ),
        TargetBand(
            lane="crypto",
            role="volatile satellite sleeve",
            target_floor_pct=DEFAULT_CRYPTO_TARGET_FLOOR_PCT,
            target_mid_pct=_target_mid(DEFAULT_CRYPTO_TARGET_FLOOR_PCT, DEFAULT_CRYPTO_TARGET_CEILING_PCT),
            target_ceiling_pct=DEFAULT_CRYPTO_TARGET_CEILING_PCT,
            current_pct_of_invested_assets=crypto_pct,
            policy_note="Crypto may receive catch-up contributions but remains capped because of volatility.",
        ),
        TargetBand(
            lane="individual_stock",
            role="research-only satellite sleeve",
            target_floor_pct=0.0,
            target_mid_pct=0.0,
            target_ceiling_pct=DEFAULT_INDIVIDUAL_STOCK_TARGET_CEILING_PCT,
            current_pct_of_invested_assets=0.0,
            policy_note="Individual stocks remain 0 EUR until stock-specific evidence and manual approval exist.",
        ),
    )


def _build_contribution_targets(*, investable_amount: float, crypto_current_pct: float | None) -> tuple[ContributionTarget, ...]:
    investable = max(float(investable_amount), 0.0)
    if investable <= 0:
        return (
            ContributionTarget("crypto", 0.0, True, "No investable contribution after emergency rule."),
            ContributionTarget("stock_fund_etf", 0.0, True, "No investable contribution after emergency rule."),
            ContributionTarget("individual_stock", 0.0, True, "Review-only; no stock-specific evidence gate yet."),
        )

    crypto_pct = crypto_current_pct if crypto_current_pct is not None else 0.0
    if crypto_pct < DEFAULT_CRYPTO_TARGET_FLOOR_PCT:
        crypto_amount = min(round(investable * (DEFAULT_CRYPTO_CONTRIBUTION_CAP_PCT / 100.0), 2), investable)
        crypto_note = "Crypto is below target floor, but contribution remains capped at 40 percent."
    elif crypto_pct < DEFAULT_CRYPTO_TARGET_CEILING_PCT:
        crypto_amount = round(investable * 0.10, 2)
        crypto_note = "Crypto is within target band; only maintenance contribution is allowed."
    else:
        crypto_amount = 0.0
        crypto_note = "Crypto is at or above target ceiling; no new crypto contribution suggested."

    etf_amount = round(max(investable - crypto_amount, 0.0), 2)

    return (
        ContributionTarget("crypto", _round2(crypto_amount) or 0.0, False, crypto_note),
        ContributionTarget("stock_fund_etf", _round2(etf_amount) or 0.0, False, "ETF/fund core receives the remaining investable contribution."),
        ContributionTarget("individual_stock", 0.0, True, "Individual stock lane remains review-only at 0 EUR until stock-specific evidence exists."),
    )


def build_dynamic_target_policy_result(
    *,
    current_date: str | None = None,
    snapshot_path: str | Path = DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH,
    monthly_contribution_eur: float | None = None,
    monthly_expenses_eur: float | None = None,
    minimum_emergency_months: float = DEFAULT_MIN_EMERGENCY_MONTHS,
    ideal_emergency_months: float = DEFAULT_IDEAL_EMERGENCY_MONTHS,
    age_years: int | None = DEFAULT_AGE_YEARS,
    risk_profile: str = "young_disciplined_growth_with_emergency_buffer",
) -> DynamicTargetPolicyResult:
    effective_date = current_date or _today_iso()
    base = build_portfolio_exposure_dynamic_emergency_fund_audit_result(
        current_date=effective_date,
        snapshot_path=snapshot_path,
        monthly_contribution_eur=monthly_contribution_eur,
        monthly_expenses_eur=monthly_expenses_eur,
        minimum_emergency_months=minimum_emergency_months,
        ideal_emergency_months=ideal_emergency_months,
    )

    blockers: list[str] = []
    warnings: list[str] = []
    flags: list[str] = []

    if not base.snapshot_ready:
        blockers.append("manual_portfolio_snapshot_required")
    if monthly_expenses_eur is None or monthly_expenses_eur <= 0:
        blockers.append("monthly_expenses_required_for_dynamic_target_policy")
    if monthly_contribution_eur is None or monthly_contribution_eur < 0:
        blockers.append("monthly_contribution_required_for_dynamic_target_policy")

    if base.emergency_fund_decision == "MINIMUM_EMERGENCY_FUND_MET_IDEAL_NOT_MET":
        flags.append("EMERGENCY_IDEAL_NOT_MET_MAINTENANCE_TOP_UP")
        warnings.append("emergency fund is at minimum target but below ideal target")
    elif base.emergency_fund_decision == "BELOW_MINIMUM_EMERGENCY_FUND":
        flags.append("EMERGENCY_BELOW_MINIMUM_TARGET")

    crypto_pct = _lane_pct(base, "crypto")
    core_pct = _lane_pct(base, "stock_fund_etf")

    if crypto_pct is not None and crypto_pct < DEFAULT_CRYPTO_TARGET_FLOOR_PCT:
        flags.append("CRYPTO_UNDER_TARGET_FLOOR_BUT_CAPPED")
    if core_pct is not None and core_pct > 95.0:
        flags.append("CORE_ETF_DOMINANT_CURRENT_PORTFOLIO")
    if base.position_flags:
        flags.append("POSITION_FLAGS_REQUIRE_REVIEW")
        warnings.append("position flags require review before full allocation")

    investable = base.suggested_monthly_investment_after_emergency_eur or 0.0
    target_bands = _build_target_bands(base)
    contribution_targets = _build_contribution_targets(investable_amount=investable, crypto_current_pct=crypto_pct)

    if blockers:
        status = STATUS_BLOCKED
        policy_status = POLICY_BLOCKED
    elif warnings or flags:
        status = STATUS_REVIEW_REQUIRED
        policy_status = POLICY_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        policy_status = POLICY_READY

    return DynamicTargetPolicyResult(
        status=status,
        policy_status=policy_status,
        current_date=effective_date,
        snapshot_path=str(snapshot_path),
        snapshot_ready=base.snapshot_ready,
        age_years=age_years,
        risk_profile=risk_profile,
        monthly_contribution_eur=monthly_contribution_eur,
        monthly_expenses_eur=monthly_expenses_eur,
        emergency_fund_current_eur=base.emergency_fund_current_eur,
        emergency_months_covered=base.emergency_months_covered,
        minimum_emergency_target_eur=base.minimum_emergency_target_eur,
        ideal_emergency_target_eur=base.ideal_emergency_target_eur,
        suggested_monthly_emergency_top_up_eur=base.suggested_monthly_emergency_top_up_eur,
        suggested_monthly_investment_after_emergency_eur=base.suggested_monthly_investment_after_emergency_eur,
        target_bands=target_bands,
        proposed_contribution_targets=contribution_targets,
        policy_flags=_dedupe(flags),
        full_allocation_still_requires=("stock_specific_public_evidence", "correlation_risk_model"),
        target_policy_data_gate_covered=True,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        blockers=_dedupe(blockers),
        warnings=_dedupe(warnings),
    )


def format_dynamic_target_policy(result: DynamicTargetPolicyResult) -> str:
    lines = [
        "J.A.R.V.I.S. DYNAMIC TARGET POLICY ENGINE",
        f"status: {result.status}",
        f"policy status: {result.policy_status}",
        f"current date: {result.current_date}",
        f"snapshot path: {result.snapshot_path}",
        f"snapshot ready: {result.snapshot_ready}",
        f"age years: {result.age_years}",
        f"risk profile: {result.risk_profile}",
        "",
        "Emergency and contribution policy:",
        f"- monthly contribution EUR: {result.monthly_contribution_eur}",
        f"- monthly expenses EUR: {result.monthly_expenses_eur}",
        f"- current emergency fund EUR: {result.emergency_fund_current_eur}",
        f"- emergency months covered: {result.emergency_months_covered}",
        f"- minimum emergency target EUR: {result.minimum_emergency_target_eur}",
        f"- ideal emergency target EUR: {result.ideal_emergency_target_eur}",
        f"- suggested monthly emergency top-up EUR: {result.suggested_monthly_emergency_top_up_eur}",
        f"- suggested monthly investment after emergency EUR: {result.suggested_monthly_investment_after_emergency_eur}",
        "",
        "Target bands:",
    ]

    for band in result.target_bands:
        lines.append(
            f"- {band.lane}: floor={band.target_floor_pct}; mid={band.target_mid_pct}; ceiling={band.target_ceiling_pct}; current invested pct={band.current_pct_of_invested_assets}; role={band.role}"
        )
        lines.append(f"  note: {band.policy_note}")

    lines.extend(["", "Proposed contribution targets:"])
    for target in result.proposed_contribution_targets:
        lines.append(f"- {target.lane}: {target.amount_eur} EUR; review only: {target.review_only}; note: {target.policy_note}")

    lines.extend(["", "Full allocation still requires:"])
    lines.extend(f"- {item}" for item in result.full_allocation_still_requires)

    if result.policy_flags:
        lines.extend(["", "Policy flags:"])
        lines.extend(f"- {item}" for item in result.policy_flags)
    else:
        lines.extend(["", "Policy flags: none"])

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
    parser = argparse.ArgumentParser(description="Build dynamic target policy from manual snapshot and expense-based emergency policy.")
    parser.add_argument("--dynamic-target-policy", action="store_true")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--manual-portfolio-snapshot-path", default=DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH)
    parser.add_argument("--monthly-contribution-eur", type=float, default=None)
    parser.add_argument("--monthly-expenses-eur", type=float, default=None)
    parser.add_argument("--minimum-emergency-months", type=float, default=DEFAULT_MIN_EMERGENCY_MONTHS)
    parser.add_argument("--ideal-emergency-months", type=float, default=DEFAULT_IDEAL_EMERGENCY_MONTHS)
    parser.add_argument("--age-years", type=int, default=DEFAULT_AGE_YEARS)
    parser.add_argument("--risk-profile", default="young_disciplined_growth_with_emergency_buffer")
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_dynamic_target_policy_result(
        current_date=args.current_date,
        snapshot_path=args.manual_portfolio_snapshot_path,
        monthly_contribution_eur=args.monthly_contribution_eur,
        monthly_expenses_eur=args.monthly_expenses_eur,
        minimum_emergency_months=args.minimum_emergency_months,
        ideal_emergency_months=args.ideal_emergency_months,
        age_years=args.age_years,
        risk_profile=args.risk_profile,
    )
    print(format_dynamic_target_policy(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())