from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping

from jarvis.runtime.correlation_risk_model import build_correlation_risk_model_result
from jarvis.runtime.cross_lane_dynamic_allocation_preflight import build_cross_lane_dynamic_allocation_preflight_result
from jarvis.runtime.personal_finance_contribution_bridge import build_personal_finance_contribution_bridge_result
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V93_0_DYNAMIC_STOCK_SLEEVE_SCORING_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V93_0_DYNAMIC_STOCK_SLEEVE_SCORING_REVIEW_REQUIRED_SAFE"


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
    stock_sleeve_score: DynamicStockSleeveScore
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


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


@dataclass(frozen=True)
class DynamicStockSleeveScore:
    stock_lane_ready: bool
    universe_ready: bool
    freshness_ready: bool
    availability_score: float
    equity_weight: float
    us_large_cap_weight: float
    equity_concentration_risk: float
    us_large_cap_concentration_risk: float
    concentration_score: float
    stock_quality_score: float
    stock_capacity_pct: float
    final_stock_pct: float
    investable_eur: float
    stock_eur_before_rounding: float
    stock_eur_after_rounding: float
    method: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def score_dynamic_stock_sleeve(
    *,
    stock_lane_ready: bool,
    universe_ready: bool,
    freshness_ready: bool,
    equity_weight: float,
    us_large_cap_weight: float,
    investable_eur: float,
) -> DynamicStockSleeveScore:
    if not stock_lane_ready:
        availability_score = 0.0
        equity_concentration_risk = 0.0
        us_large_cap_concentration_risk = 0.0
        concentration_score = 0.0
        stock_quality_score = 0.0
        stock_capacity_pct = 0.0
        final_stock_pct = 0.0
    else:
        readiness_inputs = [
            1.0,
            1.0 if universe_ready else 0.0,
            1.0 if freshness_ready else 0.0,
        ]
        availability_score = sum(readiness_inputs) / len(readiness_inputs)

        equity_concentration_risk = _clamp((equity_weight - 0.90) / 0.10)
        us_large_cap_concentration_risk = _clamp((us_large_cap_weight - 0.60) / 0.40)

        concentration_score = _clamp(
            1.0 - ((equity_concentration_risk + us_large_cap_concentration_risk) / 2.0)
        )

        stock_quality_score = _clamp(availability_score * concentration_score)

        stock_capacity_pct = 0.20 * availability_score
        final_stock_pct = _clamp(stock_quality_score * stock_capacity_pct, 0.0, stock_capacity_pct)

    before_rounding = round(max(0.0, investable_eur * final_stock_pct), 2)
    after_rounding = round(max(0.0, int((before_rounding + 2.5) // 5) * 5.0), 2)

    return DynamicStockSleeveScore(
        stock_lane_ready=stock_lane_ready,
        universe_ready=universe_ready,
        freshness_ready=freshness_ready,
        availability_score=round(availability_score, 4),
        equity_weight=round(float(equity_weight), 4),
        us_large_cap_weight=round(float(us_large_cap_weight), 4),
        equity_concentration_risk=round(equity_concentration_risk, 4),
        us_large_cap_concentration_risk=round(us_large_cap_concentration_risk, 4),
        concentration_score=round(concentration_score, 4),
        stock_quality_score=round(stock_quality_score, 4),
        stock_capacity_pct=round(stock_capacity_pct, 4),
        final_stock_pct=round(final_stock_pct, 4),
        investable_eur=round(investable_eur, 2),
        stock_eur_before_rounding=before_rounding,
        stock_eur_after_rounding=after_rounding,
        method=(
            "dynamic score = availability_score * concentration_score; "
            "stock_pct = dynamic score * availability-adjusted stock capacity"
        ),
    )


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

    stock_sleeve_score = score_dynamic_stock_sleeve(
        stock_lane_ready=bool(preflight.get("stock_lane_ready")),
        universe_ready=bool(preflight.get("universe_ready")),
        freshness_ready=bool(preflight.get("freshness_ready")),
        equity_weight=equity_weight,
        us_large_cap_weight=us_large_cap_weight,
        investable_eur=investable,
    )
    stock_pct = stock_sleeve_score.final_stock_pct
    stock_eur = stock_sleeve_score.stock_eur_after_rounding

    rationale = [
        "cross-lane preflight is ready, so allocation recommendation is allowed",
        "emergency top-up remains active because the ideal emergency target is not reached",
        "crypto is capped at 20% of monthly contribution",
        f"individual stock sleeve is score-based at {stock_pct:.0%} of investable from dynamic quality score {stock_sleeve_score.stock_quality_score:.0%}",
        (
            "stock sleeve dynamic inputs: "
            f"availability {stock_sleeve_score.availability_score:.0%}, "
            f"concentration score {stock_sleeve_score.concentration_score:.0%}, "
            f"equity risk {stock_sleeve_score.equity_concentration_risk:.0%}, "
            f"US large-cap risk {stock_sleeve_score.us_large_cap_concentration_risk:.0%}"
        ),
    ]

    crypto_policy_cap = monthly * 0.20
    crypto_eur = min(crypto_cap, investable, crypto_policy_cap)
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
        stock_sleeve_score=stock_sleeve_score,
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
    lines.extend([
        "stock sleeve score:",
        f"- availability score: {result.stock_sleeve_score.availability_score:.0%}",
        f"- concentration score: {result.stock_sleeve_score.concentration_score:.0%}",
        f"- equity concentration risk: {result.stock_sleeve_score.equity_concentration_risk:.0%}",
        f"- US large-cap concentration risk: {result.stock_sleeve_score.us_large_cap_concentration_risk:.0%}",
        f"- stock quality score: {result.stock_sleeve_score.stock_quality_score:.0%}",
        f"- stock capacity pct: {result.stock_sleeve_score.stock_capacity_pct:.0%}",
        f"- final stock pct: {result.stock_sleeve_score.final_stock_pct:.0%}",
        f"- stock EUR before rounding: {result.stock_sleeve_score.stock_eur_before_rounding:.2f}",
        f"- stock EUR after rounding: {result.stock_sleeve_score.stock_eur_after_rounding:.2f}",
        f"- method: {result.stock_sleeve_score.method}",
    ])
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


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "DynamicStockSleeveScore",
    "DynamicQualityAllocatorResult",
    "score_dynamic_stock_sleeve",
    "build_dynamic_quality_allocator_result",
    "format_result",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
