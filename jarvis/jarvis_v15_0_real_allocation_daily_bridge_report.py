"""Report CLI for J.A.R.V.I.S. v15.0 real allocation daily bridge."""

from __future__ import annotations

from .jarvis_v15_0_real_allocation_daily_bridge import (
    RealAllocationDailyBridgeResult,
    build_real_allocation_daily_bridge,
    build_real_allocation_daily_console_output,
)


def build_v15_0_real_allocation_daily_bridge_report(result: RealAllocationDailyBridgeResult) -> str:
    lines = [
        "# J.A.R.V.I.S. v15.0 Real Allocation Daily Bridge",
        "",
        f"status: {result.status}",
        f"bridge status: {result.bridge_status}",
        f"daily bridge ready: {result.daily_bridge_ready}",
        f"real allocation engine used: {result.real_allocation_engine_used}",
        f"approval ticket used: {result.approval_ticket_used}",
        f"selected ideal sleeve: {result.selected_ideal_sleeve}",
        f"executable allocation: {result.executable_allocation}",
        f"manual approval required: {result.manual_approval_required}",
        f"broker connection forbidden: {result.broker_connection_forbidden}",
        f"order creation forbidden: {result.order_creation_forbidden}",
        f"no trades executed: {result.no_trades_executed}",
        f"blockers: {', '.join(result.blockers) if result.blockers else 'none'}",
        f"warnings: {', '.join(result.warnings) if result.warnings else 'none'}",
        "",
        "## Daily Console Output",
        "",
        "```text",
        build_real_allocation_daily_console_output(result),
        "```",
    ]
    return "\n".join(lines)


def report_v15_0_real_allocation_daily_bridge() -> str:
    return build_v15_0_real_allocation_daily_bridge_report(
        build_real_allocation_daily_bridge()
    )


def main() -> None:
    print(report_v15_0_real_allocation_daily_bridge())


if __name__ == "__main__":
    main()

