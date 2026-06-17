"""Report CLI for J.A.R.V.I.S. v6.8 active policy manual approval gate."""

from __future__ import annotations

import argparse

from .jarvis_v6_8_active_policy_manual_approval_gate import (
    ActivePolicyManualApprovalGateResult,
    audit_v6_8_active_policy_manual_approval_gate,
)


def build_v6_8_active_policy_manual_approval_gate_report(
    result: ActivePolicyManualApprovalGateResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.8 Active Policy Manual Approval Gate",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"source draft count: {result.source_draft_count}",
        f"approval decision count: {result.approval_decision_count}",
        f"approve count: {result.approve_count}",
        f"defer count: {result.defer_count}",
        f"reject count: {result.reject_count}",
        f"request changes count: {result.request_changes_count}",
        f"active policy count: {result.active_policy_count}",
        "",
        "## Approval Decisions",
    ]

    for decision in result.approval_decisions:
        lines.extend(
            [
                "",
                f"### {decision.approval_id}",
                f"- draft id: {decision.draft_id}",
                f"- source policy id: {decision.source_policy_id}",
                f"- decision: {decision.decision}",
                f"- reviewer: {decision.reviewer}",
                f"- decision note: {decision.decision_note}",
                f"- approval recorded: {decision.approval_recorded}",
                f"- retained for future review: {decision.retained_for_future_review}",
                f"- authorizes active policy registry draft: {decision.authorizes_active_policy_registry_draft}",
                f"- creates active policy: {decision.creates_active_policy}",
                f"- mutates active policy: {decision.mutates_active_policy}",
                f"- approves assets: {decision.approves_assets}",
                f"- creates weekly buy ticket: {decision.creates_weekly_buy_ticket}",
                f"- creates buy request: {decision.creates_buy_request}",
                f"- executes trade: {decision.executes_trade}",
                "",
                "#### Required Changes",
            ]
        )
        if decision.required_changes:
            lines.extend(f"- {change}" for change in decision.required_changes)
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
            f"- manual approval gate ready: {result.manual_approval_gate_ready}",
            f"- manual approval records only: {result.manual_approval_records_only}",
            f"- active policy registry deferred: {result.active_policy_registry_deferred}",
            f"- asset approval deferred: {result.asset_approval_deferred}",
            f"- weekly buy ticket deferred: {result.weekly_buy_ticket_deferred}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_8_active_policy_manual_approval_gate() -> str:
    return build_v6_8_active_policy_manual_approval_gate_report(
        audit_v6_8_active_policy_manual_approval_gate()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.8 active policy manual approval gate."
    )
    parser.parse_args()
    print(report_v6_8_active_policy_manual_approval_gate())


if __name__ == "__main__":
    main()
