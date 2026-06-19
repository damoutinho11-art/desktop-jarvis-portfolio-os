from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.cross_lane_dynamic_allocation_preflight import (
    build_cross_lane_dynamic_allocation_preflight_result,
)
from jarvis.runtime.data_freshness_acquisition_gate import (
    build_data_freshness_acquisition_gate_result,
)
from jarvis.runtime.product_mode_operator import build_product_mode_result
from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.tradable_candidate_universe_gate import (
    MIN_CRYPTO,
    MIN_ETF,
    MIN_STOCK,
    build_tradable_candidate_universe_gate_result,
)

STATUS_READY = "JARVIS_V95_0_DATA_READINESS_STATUS_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V95_0_DATA_READINESS_STATUS_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/data_readiness_status_latest.json"


@dataclass(frozen=True)
class DataReadinessStatusResult:
    status: str
    current_date: str
    data_readiness_ready: bool
    product_recommendations_allowed: bool
    freshness_ready: bool
    universe_ready: bool
    preflight_ready: bool
    dynamic_allocator_allowed: bool
    crypto_data_ready: bool
    fx_data_ready: bool
    etf_fund_data_ready: bool
    stock_data_ready: bool
    portfolio_data_ready: bool
    monthly_expenses_data_ready: bool
    crypto_candidate_count: int
    etf_candidate_count: int
    stock_candidate_count: int
    crypto_candidate_minimum: int
    etf_candidate_minimum: int
    stock_candidate_minimum: int
    crypto_lane_ready: bool
    etf_fund_lane_ready: bool
    stock_lane_ready: bool
    missing_data: list[str]
    missing_universe: list[str]
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
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return dict(getattr(value, "__dict__", {}))


def _dedupe(items: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for item in items:
        clean = str(item).strip()
        if clean and clean not in seen:
            seen.add(clean)
            out.append(clean)
    return out


def build_data_readiness_status_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> DataReadinessStatusResult:
    freshness = build_data_freshness_acquisition_gate_result(current_date=current_date)
    universe = build_tradable_candidate_universe_gate_result(current_date=current_date)
    preflight = build_cross_lane_dynamic_allocation_preflight_result(current_date=current_date)
    product = build_product_mode_result(mode="status", current_date=current_date)

    freshness_data = _plain(freshness)
    universe_data = _plain(universe)
    preflight_data = _plain(preflight)
    product_data = _plain(product)

    safety_output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output

    freshness_ready = bool(freshness_data.get("freshness_gate_ready"))
    universe_ready = bool(universe_data.get("universe_gate_ready"))
    product_ready = str(product_data.get("status", "")).endswith("_READY_SAFE")

    raw_preflight_blockers = list(preflight_data.get("blockers", []) or [])
    data_relevant_preflight_blockers = [
        blocker for blocker in raw_preflight_blockers if blocker != "product_not_ready"
    ]
    preflight_ready = bool(preflight_data.get("preflight_ready")) or not data_relevant_preflight_blockers

    crypto_data_ready = bool(freshness_data.get("crypto_data_fresh"))
    fx_data_ready = bool(freshness_data.get("fx_data_fresh"))
    etf_fund_data_ready = bool(freshness_data.get("etf_fund_data_fresh"))
    stock_data_ready = bool(freshness_data.get("stock_data_fresh"))
    portfolio_data_ready = bool(freshness_data.get("portfolio_data_fresh"))
    monthly_expenses_data_ready = bool(freshness_data.get("monthly_expenses_data_fresh"))

    missing_data = _dedupe(list(freshness_data.get("missing_freshness", []) or []))
    missing_universe = _dedupe(list(universe_data.get("missing_breadth", []) or []))

    blockers = _dedupe(
        list(missing_data)
        + list(missing_universe)
        + data_relevant_preflight_blockers
    )
    if not safety_blocked:
        blockers.append("safety_check_did_not_block_execution")

    dynamic_allocator_allowed = bool(
        freshness_data.get("dynamic_allocator_allowed")
        and universe_data.get("dynamic_allocator_allowed")
        and preflight_ready
    )

    data_readiness_ready = not blockers
    product_recommendations_allowed = bool(
        data_readiness_ready
        and dynamic_allocator_allowed
        and safety_blocked
        and preflight_ready
    )

    warnings = [
        "data readiness status aggregates existing freshness, universe, and preflight gates",
        "this command does not fetch data, approve purchases, connect brokers, create orders, or trade",
    ]
    if missing_data:
        warnings.append("some freshness lanes are missing or stale")
    if missing_universe:
        warnings.append("candidate universe breadth is incomplete")
    if "product_not_ready" in raw_preflight_blockers:
        warnings.append("ignored non-data preflight blocker product_not_ready; current data lanes are assessed separately")

    result = DataReadinessStatusResult(
        status=STATUS_READY if data_readiness_ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        data_readiness_ready=data_readiness_ready,
        product_recommendations_allowed=product_recommendations_allowed,
        freshness_ready=freshness_ready,
        universe_ready=universe_ready,
        preflight_ready=preflight_ready,
        dynamic_allocator_allowed=dynamic_allocator_allowed,
        crypto_data_ready=crypto_data_ready,
        fx_data_ready=fx_data_ready,
        etf_fund_data_ready=etf_fund_data_ready,
        stock_data_ready=stock_data_ready,
        portfolio_data_ready=portfolio_data_ready,
        monthly_expenses_data_ready=monthly_expenses_data_ready,
        crypto_candidate_count=int(universe_data.get("crypto_candidate_count", 0) or 0),
        etf_candidate_count=int(universe_data.get("etf_candidate_count", 0) or 0),
        stock_candidate_count=int(universe_data.get("stock_candidate_count", 0) or 0),
        crypto_candidate_minimum=MIN_CRYPTO,
        etf_candidate_minimum=MIN_ETF,
        stock_candidate_minimum=MIN_STOCK,
        crypto_lane_ready=bool(preflight_data.get("crypto_lane_ready")),
        etf_fund_lane_ready=bool(preflight_data.get("etf_fund_lane_ready")),
        stock_lane_ready=bool(preflight_data.get("stock_lane_ready")),
        missing_data=missing_data,
        missing_universe=missing_universe,
        blockers=blockers,
        warnings=warnings,
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

    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return result


def format_data_readiness_status(result: DataReadinessStatusResult) -> str:
    verdict = (
        "READY_FOR_PRODUCT_RECOMMENDATIONS"
        if result.product_recommendations_allowed
        else "REVIEW_REQUIRED"
    )

    lines = [
        "J.A.R.V.I.S. DATA READINESS STATUS",
        f"status: {result.status}",
        f"verdict: {verdict}",
        f"current date: {result.current_date}",
        "",
        "READINESS:",
        f"- data readiness ready: {result.data_readiness_ready}",
        f"- product recommendations allowed: {result.product_recommendations_allowed}",
        f"- freshness ready: {result.freshness_ready}",
        f"- universe ready: {result.universe_ready}",
        f"- preflight ready: {result.preflight_ready}",
        f"- dynamic allocator allowed: {result.dynamic_allocator_allowed}",
        "",
        "DATA LANES:",
        f"- crypto data ready: {result.crypto_data_ready}",
        f"- FX data ready: {result.fx_data_ready}",
        f"- ETF/fund data ready: {result.etf_fund_data_ready}",
        f"- stock data ready: {result.stock_data_ready}",
        f"- portfolio data ready: {result.portfolio_data_ready}",
        f"- monthly expenses data ready: {result.monthly_expenses_data_ready}",
        "",
        "CANDIDATE UNIVERSE:",
        f"- crypto candidates: {result.crypto_candidate_count} / {result.crypto_candidate_minimum}",
        f"- ETF/fund candidates: {result.etf_candidate_count} / {result.etf_candidate_minimum}",
        f"- stock candidates: {result.stock_candidate_count} / {result.stock_candidate_minimum}",
        "",
        "LANE READINESS:",
        f"- crypto lane ready: {result.crypto_lane_ready}",
        f"- ETF/fund lane ready: {result.etf_fund_lane_ready}",
        f"- stock lane ready: {result.stock_lane_ready}",
        "",
        "MISSING DATA:",
    ]
    lines.extend(f"- {item}" for item in result.missing_data or ["none"])
    lines.append("")
    lines.append("MISSING UNIVERSE:")
    lines.extend(f"- {item}" for item in result.missing_universe or ["none"])
    lines.append("")
    lines.append("SAFETY:")
    lines.extend(
        [
            f"- safety-check blocked execution: {result.safety_check_blocked_execution}",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
            f"- buy request created: {result.buy_request_created}",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- private account data ingestion: {result.private_account_data_ingestion}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
        ]
    )
    lines.append("")
    lines.append("WARNINGS:")
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. data readiness status.")
    parser.add_argument("--data-readiness-status", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_data_readiness_status_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_data_readiness_status(result))
    return 0 if result.product_recommendations_allowed else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "DataReadinessStatusResult",
    "build_data_readiness_status_result",
    "format_data_readiness_status",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
