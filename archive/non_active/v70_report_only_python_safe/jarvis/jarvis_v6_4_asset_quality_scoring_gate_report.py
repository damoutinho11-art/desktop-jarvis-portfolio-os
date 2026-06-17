"""Report CLI for J.A.R.V.I.S. v6.4 asset quality scoring gate."""

from __future__ import annotations

import argparse

from .jarvis_v6_4_asset_quality_scoring_gate import (
    AssetQualityScoringGateResult,
    audit_v6_4_asset_quality_scoring_gate,
)


def build_v6_4_asset_quality_scoring_gate_report(
    result: AssetQualityScoringGateResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.4 Asset Quality Scoring Gate",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"assessment count: {result.assessment_count}",
        f"quality ready count: {result.quality_ready_count}",
        f"watchlist count: {result.watchlist_count}",
        f"needs more data count: {result.needs_more_data_count}",
        f"blocked count: {result.blocked_count}",
        f"avoid count: {result.avoid_count}",
        "",
        "## Assessments",
    ]

    for assessment in result.assessments:
        lines.extend(
            [
                "",
                f"### {assessment.candidate_id}",
                f"- display name: {assessment.display_name}",
                f"- asset type: {assessment.asset_type}",
                f"- quality status: {assessment.quality_status}",
                f"- score: {assessment.total_score}/{assessment.max_score}",
                f"- score pct: {assessment.score_pct()}",
                f"- can enter policy generation next: {assessment.can_enter_policy_generation_next}",
                f"- operator approved: {assessment.operator_approved}",
                f"- policy asset approved: {assessment.policy_asset_approved}",
                f"- weekly buy candidate: {assessment.weekly_buy_candidate}",
                f"- creates buy request: {assessment.creates_buy_request}",
                f"- executes trade: {assessment.executes_trade}",
                "- metrics:",
            ]
        )
        for metric in assessment.metrics:
            lines.append(
                f"  - {metric.metric_id}: {metric.score}/{metric.max_score}, "
                f"passed={metric.passed}, reason={metric.reason}"
            )

        lines.append("- warnings:")
        if assessment.warnings:
            lines.extend(f"  - {warning}" for warning in assessment.warnings)
        else:
            lines.append("  - none")

        lines.append("- blockers:")
        if assessment.blockers:
            lines.extend(f"  - {blocker}" for blocker in assessment.blockers)
        else:
            lines.append("  - none")

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
            f"- quality scoring ready: {result.quality_scoring_ready}",
            f"- exact policy generation deferred: {result.exact_policy_generation_deferred}",
            f"- policy approval deferred: {result.policy_approval_deferred}",
            f"- weekly buy ticket deferred: {result.weekly_buy_ticket_deferred}",
            f"- active policy mutated: {result.active_policy_mutated}",
            f"- automatic approval forbidden: {result.automatic_approval_forbidden}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- creates buy request: {result.creates_buy_request}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_4_asset_quality_scoring_gate() -> str:
    return build_v6_4_asset_quality_scoring_gate_report(
        audit_v6_4_asset_quality_scoring_gate()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.4 asset quality scoring gate."
    )
    parser.parse_args()
    print(report_v6_4_asset_quality_scoring_gate())


if __name__ == "__main__":
    main()
