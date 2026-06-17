from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping

from jarvis.runtime.correlation_risk_model import build_correlation_risk_model_result
from jarvis.runtime.data_freshness_acquisition_gate import build_data_freshness_acquisition_gate_result
from jarvis.runtime.personal_finance_contribution_bridge import build_personal_finance_contribution_bridge_result
from jarvis.runtime.product_mode_operator import build_product_mode_result
from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.tradable_candidate_universe_gate import (
    MIN_CRYPTO,
    MIN_ETF,
    MIN_STOCK,
    build_tradable_candidate_universe_gate_result,
)

STATUS_READY = "JARVIS_V86_0_CROSS_LANE_DYNAMIC_ALLOCATION_PREFLIGHT_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V86_0_CROSS_LANE_DYNAMIC_ALLOCATION_PREFLIGHT_REVIEW_REQUIRED_SAFE"


@dataclass(frozen=True)
class CrossLaneDynamicAllocationPreflightResult:
    status: str
    current_date: str
    preflight_ready: bool
    dynamic_allocator_allowed: bool
    freshness_ready: bool
    universe_ready: bool
    contribution_ready: bool
    correlation_ready: bool
    product_ready: bool
    crypto_lane_ready: bool
    etf_fund_lane_ready: bool
    stock_lane_ready: bool
    blockers: list[str]
    warnings: list[str]
    safety_check_blocked_execution: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection: bool
    credentials_used: bool
    private_account_data_ingestion: bool
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


def _ready_status(data: Mapping[str, Any]) -> bool:
    return str(data.get("status", "")).endswith("_READY_SAFE")


def _no_blockers(data: Mapping[str, Any]) -> bool:
    blockers = data.get("blockers", [])
    return not blockers


def build_cross_lane_dynamic_allocation_preflight_result(
    current_date: str = "2026-06-18",
) -> CrossLaneDynamicAllocationPreflightResult:
    freshness = _plain(build_data_freshness_acquisition_gate_result(current_date=current_date))
    universe = _plain(build_tradable_candidate_universe_gate_result(current_date=current_date))
    contribution = _plain(build_personal_finance_contribution_bridge_result(current_date=current_date))
    correlation = _plain(build_correlation_risk_model_result(current_date=current_date))
    product = _plain(build_product_mode_result(current_date=current_date))

    safety = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety and "No execution action was taken" in safety

    freshness_ready = _ready_status(freshness) and bool(freshness.get("dynamic_allocator_allowed"))
    universe_ready = _ready_status(universe) and bool(universe.get("dynamic_allocator_allowed"))
    contribution_ready = (
        bool(contribution.get("trusted_monthly_contribution_decision_allowed"))
        and bool(contribution.get("monthly_expenses_confirmed"))
        and bool(contribution.get("snapshot_ready"))
        and bool(contribution.get("manual_cost_basis_ready"))
        and _no_blockers(contribution)
    )
    correlation_ready = bool(correlation.get("correlation_model_ready")) and _no_blockers(correlation)
    product_ready = product.get("verdict") == "READY_FOR_MANUAL_USE" or _ready_status(product)

    crypto_lane_ready = int(universe.get("crypto_candidate_count", 0)) >= MIN_CRYPTO
    etf_fund_lane_ready = int(universe.get("etf_candidate_count", 0)) >= MIN_ETF
    stock_lane_ready = int(universe.get("stock_candidate_count", 0)) >= MIN_STOCK

    blockers: list[str] = []
    if not freshness_ready:
        blockers.append("freshness_not_ready")
    if not universe_ready:
        blockers.append("tradable_universe_not_ready")
    if not contribution_ready:
        blockers.append("contribution_not_ready")
    if not correlation_ready:
        blockers.append("correlation_not_ready")
    if not product_ready:
        blockers.append("product_not_ready")
    if not crypto_lane_ready:
        blockers.append("crypto_lane_not_ready")
    if not etf_fund_lane_ready:
        blockers.append("etf_fund_lane_not_ready")
    if not stock_lane_ready:
        blockers.append("stock_lane_not_ready")
    if not safety_blocked:
        blockers.append("safety_check_did_not_block_execution")

    ready = not blockers

    return CrossLaneDynamicAllocationPreflightResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        preflight_ready=ready,
        dynamic_allocator_allowed=ready,
        freshness_ready=freshness_ready,
        universe_ready=universe_ready,
        contribution_ready=contribution_ready,
        correlation_ready=correlation_ready,
        product_ready=product_ready,
        crypto_lane_ready=crypto_lane_ready,
        etf_fund_lane_ready=etf_fund_lane_ready,
        stock_lane_ready=stock_lane_ready,
        blockers=blockers,
        warnings=[
            "preflight only; no allocation is created here",
            "manual approval remains required",
        ],
        safety_check_blocked_execution=safety_blocked,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection=False,
        credentials_used=False,
        private_account_data_ingestion=False,
        order_created=False,
        trade_executed=False,
    )


def format_result(result: CrossLaneDynamicAllocationPreflightResult) -> str:
    lines = [
        "J.A.R.V.I.S. CROSS-LANE DYNAMIC ALLOCATION PREFLIGHT",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"preflight ready: {result.preflight_ready}",
        f"dynamic allocator allowed: {result.dynamic_allocator_allowed}",
        "readiness:",
        f"- freshness ready: {result.freshness_ready}",
        f"- universe ready: {result.universe_ready}",
        f"- contribution ready: {result.contribution_ready}",
        f"- correlation ready: {result.correlation_ready}",
        f"- product ready: {result.product_ready}",
        f"- crypto lane ready: {result.crypto_lane_ready}",
        f"- ETF/fund lane ready: {result.etf_fund_lane_ready}",
        f"- stock lane ready: {result.stock_lane_ready}",
        "blockers:",
    ]
    lines.extend(f"- {x}" for x in result.blockers or ["none"])
    lines.extend([
        "Safety:",
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
    parser.add_argument("--cross-lane-dynamic-allocation-preflight", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    args = parser.parse_args(argv)

    result = build_cross_lane_dynamic_allocation_preflight_result(current_date=args.current_date)
    print(format_result(result))
    return 0 if not result.blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
