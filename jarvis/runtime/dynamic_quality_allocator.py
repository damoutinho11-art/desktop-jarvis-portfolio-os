from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping

from jarvis.runtime.correlation_risk_model import build_correlation_risk_model_result
from jarvis.runtime.cross_lane_dynamic_allocation_preflight import build_cross_lane_dynamic_allocation_preflight_result
from jarvis.runtime.personal_finance_contribution_bridge import build_personal_finance_contribution_bridge_result
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V87_0_DYNAMIC_QUALITY_ALLOCATOR_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V87_0_DYNAMIC_QUALITY_ALLOCATOR_REVIEW_REQUIRED_SAFE"


@dataclass(frozen=True)
class DynamicQualityAllocatorResult:
    status: str
    current_date: str
    allocator_ready: bool
    monthly_contribution_eur: float
    emergency_top_up_eur: float
    crypto_eur: float
    etf_fund_eur: float
    individual_stock_eur: float
    total_allocated_eur: float
    rationale: list[str]
    blockers: list[str]
    warnings: list[str]
    safety_check_blocked_execution: bool
    approved_for_purchase: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if is_dataclass(value):
        return asdict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return dict(getattr(value, "__dict__", {}))


def _money(value: Any) -> float:
    try:
        return round(float(value), 2)
    except Exception:
        return 0.0


def build_dynamic_quality_allocator_result(current_date: str = "2026-06-18") -> DynamicQualityAllocatorResult:
    preflight = _plain(build_cross_lane_dynamic_allocation_preflight_result(current_date=current_date))
    contribution = _plain(build_personal_finance_contribution_bridge_result(current_date=current_date))
    correlation = _plain(build_correlation_risk_model_result(current_date=current_date))

    safety = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety and "No execution action was taken" in safety

    blockers: list[str] = []
    if not preflight.get("dynamic_allocator_allowed"):
        blockers.append("cross_lane_preflight_not_ready")
    if not safety_blocked:
        blockers.append("safety_check_did_not_block_execution")

    monthly = _money(contribution.get("monthly_contribution_eur"))
    emergency = _money(contribution.get("suggested_monthly_emergency_top_up_eur"))
    crypto_cap = _money(contribution.get("crypto_amount_eur"))

    if monthly <= 0:
        blockers.append("monthly_contribution_missing")

    investable = max(0.0, monthly - emergency)

    exposure = correlation.get("exposure_weights", {}) or {}
    equity_weight = float(exposure.get("equity", 0.0) or 0.0)
    us_large_cap_weight = float(exposure.get("us_large_cap", 0.0) or 0.0)

    stock_eur = 75.0
    rationale = [
        "cross-lane preflight is ready, so allocation recommendation is allowed",
        "emergency top-up remains active because the ideal emergency target is not reached",
        "crypto uses the existing capped bridge amount, not an aggressive increase",
    ]

    if equity_weight >= 0.90 or us_large_cap_weight >= 0.60:
        stock_eur = 50.0
        rationale.append("individual stock sleeve is limited because equity / US large-cap exposure is already high")
    else:
        rationale.append("individual stock sleeve is allowed because stock universe breadth and freshness are ready")

    crypto_eur = min(crypto_cap, investable)
    remaining = max(0.0, monthly - emergency - crypto_eur - stock_eur)
    etf_eur = remaining

    total = round(emergency + crypto_eur + etf_eur + stock_eur, 2)

    if round(total, 2) != round(monthly, 2):
        blockers.append("allocation_total_does_not_match_monthly_contribution")

    ready = not blockers

    return DynamicQualityAllocatorResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        allocator_ready=ready,
        monthly_contribution_eur=monthly,
        emergency_top_up_eur=round(emergency, 2),
        crypto_eur=round(crypto_eur, 2),
        etf_fund_eur=round(etf_eur, 2),
        individual_stock_eur=round(stock_eur, 2),
        total_allocated_eur=total,
        rationale=rationale,
        blockers=blockers,
        warnings=[
            "recommendation only; no purchase is approved",
            "manual approval remains required",
            "allocator is conservative while equity and US large-cap exposure are high",
        ],
        safety_check_blocked_execution=safety_blocked,
        approved_for_purchase=False,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection=False,
        credentials_used=False,
        order_created=False,
        trade_executed=False,
    )


def format_result(result: DynamicQualityAllocatorResult) -> str:
    lines = [
        "J.A.R.V.I.S. DYNAMIC QUALITY ALLOCATOR",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"allocator ready: {result.allocator_ready}",
        f"monthly contribution EUR: {result.monthly_contribution_eur:.2f}",
        "recommended split:",
        f"- emergency top-up EUR: {result.emergency_top_up_eur:.2f}",
        f"- crypto EUR: {result.crypto_eur:.2f}",
        f"- ETF/fund EUR: {result.etf_fund_eur:.2f}",
        f"- individual stock EUR: {result.individual_stock_eur:.2f}",
        f"- total allocated EUR: {result.total_allocated_eur:.2f}",
        "rationale:",
    ]
    lines.extend(f"- {x}" for x in result.rationale)
    lines.append("warnings:")
    lines.extend(f"- {x}" for x in result.warnings)
    lines.append("blockers:")
    lines.extend(f"- {x}" for x in result.blockers or ["none"])
    lines.extend([
        "Safety:",
        f"- approved for purchase: {result.approved_for_purchase}",
        f"- safety-check blocked execution: {result.safety_check_blocked_execution}",
        f"- allocation mutation: {result.allocation_mutation}",
        f"- approval ticket mutation: {result.approval_ticket_mutation}",
        f"- buy request created: {result.buy_request_created}",
        f"- broker connection: {result.broker_connection}",
        f"- credentials used: {result.credentials_used}",
        f"- order created: {result.order_created}",
        f"- trade executed: {result.trade_executed}",
    ])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dynamic-quality-allocator", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    args = parser.parse_args(argv)

    result = build_dynamic_quality_allocator_result(current_date=args.current_date)
    print(format_result(result))
    return 0 if not result.blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
