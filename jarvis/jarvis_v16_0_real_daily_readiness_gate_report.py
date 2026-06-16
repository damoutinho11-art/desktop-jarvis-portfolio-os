"""Report CLI for J.A.R.V.I.S. v16.0 real daily readiness gate."""

from __future__ import annotations

from .jarvis_v16_0_real_daily_readiness_gate import (
    RealDailyReadinessGateResult,
    build_real_daily_readiness_console_output,
    build_real_daily_readiness_gate,
)


def build_v16_0_real_daily_readiness_gate_report(result: RealDailyReadinessGateResult) -> str:
    lines = [
        "# J.A.R.V.I.S. v16.0 Real Daily Readiness Gate",
        "",
        f"status: {result.status}",
        f"readiness status: {result.readiness_status}",
        f"current date: {result.current_date}",
        f"max fresh age days: {result.max_fresh_age_days}",
        f"recommendation trust: {result.recommendation_trust}",
        f"data ready for manual review: {result.data_ready_for_manual_review}",
        f"stale data review required: {result.stale_data_review_required}",
        f"real allocation engine used: {result.real_allocation_engine_used}",
        f"portfolio state file checked: {result.portfolio_state_file_checked}",
        f"approval ticket file checked: {result.approval_ticket_file_checked}",
        f"ETF universe file checked: {result.etf_universe_file_checked}",
        f"selected ideal sleeve: {result.allocation_result.selected_ideal_sleeve}",
        f"executable allocation: {result.allocation_result.executable_allocation}",
        f"manual approval required: {result.manual_approval_required}",
        f"broker connection forbidden: {result.broker_connection_forbidden}",
        f"order creation forbidden: {result.order_creation_forbidden}",
        f"no trades executed: {result.no_trades_executed}",
        f"blockers: {', '.join(result.blockers) if result.blockers else 'none'}",
        f"warnings: {', '.join(result.warnings) if result.warnings else 'none'}",
        "",
        "## Freshness Checks",
        "",
    ]

    if result.freshness_checks:
        for check in result.freshness_checks:
            age = "unknown" if check.age_days is None else str(check.age_days)
            lines.append(
                f"- {check.name}: {check.status}; as_of={check.as_of}; age_days={age}; source={check.source_path}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Daily Console Output",
            "",
            "```text",
            build_real_daily_readiness_console_output(result),
            "```",
        ]
    )
    return "\n".join(lines)


def report_v16_0_real_daily_readiness_gate() -> str:
    return build_v16_0_real_daily_readiness_gate_report(build_real_daily_readiness_gate())


def main() -> None:
    print(report_v16_0_real_daily_readiness_gate())


if __name__ == "__main__":
    main()
