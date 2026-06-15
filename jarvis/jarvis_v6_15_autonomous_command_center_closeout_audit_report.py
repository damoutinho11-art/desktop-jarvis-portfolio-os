"""Report CLI for J.A.R.V.I.S. v6.15 autonomous command center closeout audit."""

from __future__ import annotations

import argparse

from .jarvis_v6_15_autonomous_command_center_closeout_audit import (
    AutonomousCommandCenterCloseoutAuditResult,
    audit_v6_15_autonomous_command_center_closeout_audit,
)


def build_v6_15_autonomous_command_center_closeout_audit_report(
    result: AutonomousCommandCenterCloseoutAuditResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.15 Autonomous Command Center Closeout Audit",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"analyzed policy id: {result.analyzed_policy_id}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"check count: {result.check_count}",
        f"passed check count: {result.passed_check_count}",
        f"failed check count: {result.failed_check_count}",
        f"v6 chain complete: {result.v6_chain_complete}",
        f"autonomous intelligence ready: {result.autonomous_intelligence_ready}",
        f"command center ready: {result.command_center_ready}",
        f"final user buy action required: {result.final_user_buy_action_required}",
        "",
        "## Closeout Checks",
    ]

    for check in result.checks:
        lines.extend(
            [
                "",
                f"### {check.check_id}",
                f"- title: {check.title}",
                f"- status: {check.status}",
                f"- evidence: {check.evidence}",
                f"- blocker if failed: {check.blocker_if_failed}",
                f"- no buy request: {check.no_buy_request}",
                f"- no broker connection: {check.no_broker_connection}",
                f"- no order placement: {check.no_order_placement}",
                f"- no trade execution: {check.no_trade_execution}",
            ]
        )

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
            f"- closeout audit ready: {result.closeout_audit_ready}",
            f"- no manual review queue added: {result.no_manual_review_queue_added}",
            f"- no buy request created: {result.no_buy_request_created}",
            f"- no broker connection created: {result.no_broker_connection_created}",
            f"- no order placement created: {result.no_order_placement_created}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_15_autonomous_command_center_closeout_audit() -> str:
    return build_v6_15_autonomous_command_center_closeout_audit_report(
        audit_v6_15_autonomous_command_center_closeout_audit()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.15 autonomous command center closeout audit."
    )
    parser.parse_args()
    print(report_v6_15_autonomous_command_center_closeout_audit())


if __name__ == "__main__":
    main()
