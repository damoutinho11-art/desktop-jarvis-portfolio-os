"""Report CLI for J.A.R.V.I.S. v6.11 manual weekly planning context builder."""

from __future__ import annotations

import argparse

from .jarvis_v6_11_manual_weekly_planning_context_builder import (
    ManualWeeklyPlanningContextResult,
    audit_v6_11_manual_weekly_planning_context_builder,
)


def build_v6_11_manual_weekly_planning_context_builder_report(
    result: ManualWeeklyPlanningContextResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.11 Manual Weekly Planning Context Builder",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"analyzed policy id: {result.analyzed_policy_id}",
        f"source sleeve gap count: {result.source_sleeve_gap_count}",
        f"planning context item count: {result.planning_context_item_count}",
        f"critical priority count: {result.critical_priority_count}",
        f"high priority count: {result.high_priority_count}",
        f"medium priority count: {result.medium_priority_count}",
        f"low priority count: {result.low_priority_count}",
        f"investable cash EUR: {result.investable_cash_eur}",
        f"protected cash EUR: {result.protected_cash_eur}",
        f"cash available for future manual planning: {result.cash_available_for_future_manual_planning}",
        f"protected cash guard active: {result.protected_cash_guard_active}",
        f"crypto ceiling guard active: {result.crypto_ceiling_guard_active}",
        "",
        "## Planning Context Items",
    ]

    for item in result.planning_items:
        lines.extend(
            [
                "",
                f"### {item.context_id}",
                f"- sleeve id: {item.sleeve_id}",
                f"- gap status: {item.gap_status}",
                f"- priority: {item.priority}",
                f"- context action: {item.context_action}",
                f"- rationale: {item.rationale}",
                f"- current weight pct: {item.current_weight_pct}",
                f"- preferred low pct: {item.preferred_low_pct}",
                f"- preferred high pct: {item.preferred_high_pct}",
                f"- max pct: {item.max_pct}",
                f"- investable cash considered: {item.investable_cash_considered}",
                f"- protected cash guard active: {item.protected_cash_guard_active}",
                f"- crypto ceiling guard active: {item.crypto_ceiling_guard_active}",
                f"- creates weekly buy ticket: {item.creates_weekly_buy_ticket}",
                f"- creates buy request: {item.creates_buy_request}",
                f"- executes trade: {item.executes_trade}",
            ]
        )

    lines.extend(["", "## Manual Planning Notes"])
    lines.extend(f"- {note}" for note in result.manual_planning_notes)

    lines.extend(["", "## Warnings"])
    if result.warnings:
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("- none")

    lines.extend(["", "## Blockers"])
    if result.blockers:
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Safety",
            "",
            f"- weekly planning context ready: {result.weekly_planning_context_ready}",
            f"- context only: {result.context_only}",
            f"- asset approval deferred: {result.asset_approval_deferred}",
            f"- weekly buy ticket deferred: {result.weekly_buy_ticket_deferred}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_11_manual_weekly_planning_context_builder() -> str:
    return build_v6_11_manual_weekly_planning_context_builder_report(
        audit_v6_11_manual_weekly_planning_context_builder()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.11 manual weekly planning context builder."
    )
    parser.parse_args()
    print(report_v6_11_manual_weekly_planning_context_builder())


if __name__ == "__main__":
    main()
