"""Report CLI for J.A.R.V.I.S. v6.6 manual policy review queue."""

from __future__ import annotations

import argparse

from .jarvis_v6_6_manual_policy_review_queue import (
    ManualPolicyReviewQueueResult,
    audit_v6_6_manual_policy_review_queue,
)


def build_v6_6_manual_policy_review_queue_report(
    result: ManualPolicyReviewQueueResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.6 Manual Policy Review Queue",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"source policy candidate count: {result.source_policy_candidate_count}",
        f"review item count: {result.review_item_count}",
        f"accept for active policy review count: {result.accept_for_active_policy_review_count}",
        f"defer count: {result.defer_count}",
        f"reject count: {result.reject_count}",
        f"needs correction count: {result.needs_correction_count}",
        "",
        "## Review Items",
    ]

    for item in result.review_items:
        lines.extend(
            [
                "",
                f"### {item.review_id}",
                f"- policy id: {item.policy_id}",
                f"- policy display name: {item.policy_display_name}",
                f"- decision: {item.decision}",
                f"- reviewer: {item.reviewer}",
                f"- review note: {item.review_note}",
                f"- retained for future review: {item.retained_for_future_review}",
                f"- manual review recorded: {item.manual_review_recorded}",
                f"- creates active policy: {item.creates_active_policy}",
                f"- operator approved active policy: {item.operator_approved_active_policy}",
                f"- creates weekly buy ticket: {item.creates_weekly_buy_ticket}",
                f"- creates buy request: {item.creates_buy_request}",
                f"- executes trade: {item.executes_trade}",
                "",
                "#### Required Corrections",
            ]
        )
        if item.required_corrections:
            lines.extend(f"- {correction}" for correction in item.required_corrections)
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
            f"- manual policy review queue ready: {result.manual_policy_review_queue_ready}",
            f"- manual review records only: {result.manual_review_records_only}",
            f"- active policy creation deferred: {result.active_policy_creation_deferred}",
            f"- policy approval deferred: {result.policy_approval_deferred}",
            f"- asset approval deferred: {result.asset_approval_deferred}",
            f"- weekly buy ticket deferred: {result.weekly_buy_ticket_deferred}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_6_manual_policy_review_queue() -> str:
    return build_v6_6_manual_policy_review_queue_report(
        audit_v6_6_manual_policy_review_queue()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.6 manual policy review queue."
    )
    parser.parse_args()
    print(report_v6_6_manual_policy_review_queue())


if __name__ == "__main__":
    main()
