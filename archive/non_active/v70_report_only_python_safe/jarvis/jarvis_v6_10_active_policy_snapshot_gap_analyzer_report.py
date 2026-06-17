"""Report CLI for J.A.R.V.I.S. v6.10 active policy snapshot gap analyzer."""

from __future__ import annotations

import argparse

from .jarvis_v6_10_active_policy_snapshot_gap_analyzer import (
    ActivePolicySnapshotGapAnalyzerResult,
    audit_v6_10_active_policy_snapshot_gap_analyzer,
)


def build_v6_10_active_policy_snapshot_gap_analyzer_report(
    result: ActivePolicySnapshotGapAnalyzerResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.10 Active Policy Snapshot Gap Analyzer",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"active policy count: {result.active_policy_count}",
        f"analyzed policy id: {result.analyzed_policy_id}",
        f"sleeve gap count: {result.sleeve_gap_count}",
        f"under min count: {result.under_min_count}",
        f"below preferred count: {result.below_preferred_count}",
        f"within preferred count: {result.within_preferred_count}",
        f"above preferred count: {result.above_preferred_count}",
        f"over max count: {result.over_max_count}",
        f"unmapped sleeve count: {result.unmapped_sleeve_count}",
        f"investable cash EUR: {result.investable_cash_eur}",
        f"protected cash EUR: {result.protected_cash_eur}",
        f"current sleeve weight total pct: {result.current_sleeve_weight_total_pct}",
        "",
        "## Sleeve Gaps",
    ]

    for gap in result.sleeve_gaps:
        lines.extend(
            [
                "",
                f"### {gap.sleeve_id}",
                f"- current weight pct: {gap.current_weight_pct}",
                f"- min pct: {gap.min_pct}",
                f"- preferred low pct: {gap.preferred_low_pct}",
                f"- preferred high pct: {gap.preferred_high_pct}",
                f"- max pct: {gap.max_pct}",
                f"- gap status: {gap.gap_status}",
                f"- distance to min pct: {gap.distance_to_min_pct}",
                f"- distance to preferred low pct: {gap.distance_to_preferred_low_pct}",
                f"- distance to preferred high pct: {gap.distance_to_preferred_high_pct}",
                f"- distance to max pct: {gap.distance_to_max_pct}",
                f"- attention required: {gap.attention_required}",
                f"- future planning hint: {gap.future_planning_hint}",
                f"- creates weekly buy ticket: {gap.creates_weekly_buy_ticket}",
                f"- creates buy request: {gap.creates_buy_request}",
                f"- executes trade: {gap.executes_trade}",
            ]
        )

    lines.extend(["", "## Unmapped Sleeves"])
    if result.unmapped_sleeves:
        for sleeve in result.unmapped_sleeves:
            lines.extend(
                [
                    "",
                    f"### {sleeve.sleeve_id}",
                    f"- current weight pct: {sleeve.current_weight_pct}",
                    f"- current value EUR: {sleeve.current_value_eur}",
                    f"- reason: {sleeve.reason}",
                    f"- creates weekly buy ticket: {sleeve.creates_weekly_buy_ticket}",
                    f"- creates buy request: {sleeve.creates_buy_request}",
                    f"- executes trade: {sleeve.executes_trade}",
                ]
            )
    else:
        lines.append("- none")

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
            f"- gap analyzer ready: {result.gap_analyzer_ready}",
            f"- analysis only: {result.analysis_only}",
            f"- asset approval deferred: {result.asset_approval_deferred}",
            f"- weekly buy ticket deferred: {result.weekly_buy_ticket_deferred}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_10_active_policy_snapshot_gap_analyzer() -> str:
    return build_v6_10_active_policy_snapshot_gap_analyzer_report(
        audit_v6_10_active_policy_snapshot_gap_analyzer()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.10 active policy snapshot gap analyzer."
    )
    parser.parse_args()
    print(report_v6_10_active_policy_snapshot_gap_analyzer())


if __name__ == "__main__":
    main()
