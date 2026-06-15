"""Report CLI for J.A.R.V.I.S. v6.5 policy candidate generator."""

from __future__ import annotations

import argparse

from .jarvis_v6_5_policy_candidate_generator import (
    PolicyCandidateGeneratorResult,
    audit_v6_5_policy_candidate_generator,
)


def build_v6_5_policy_candidate_generator_report(
    result: PolicyCandidateGeneratorResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.5 Policy Candidate Generator",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"policy candidate count: {result.policy_candidate_count}",
        f"manual review candidate count: {result.manual_review_candidate_count}",
        f"blocked policy candidate count: {result.blocked_policy_candidate_count}",
        f"source quality ready count: {result.source_quality_ready_count}",
        f"source watchlist count: {result.source_watchlist_count}",
        f"private snapshot investable cash EUR: {result.private_snapshot_investable_cash_eur}",
        f"private snapshot protected cash EUR: {result.private_snapshot_protected_cash_eur}",
        "",
        "## Policy Candidates",
    ]

    for candidate in result.policy_candidates:
        lines.extend(
            [
                "",
                f"### {candidate.policy_id}",
                f"- display name: {candidate.display_name}",
                f"- status: {candidate.policy_status}",
                f"- aggressiveness score: {candidate.aggressiveness_score}",
                f"- suitability reason: {candidate.suitability_reason}",
                f"- max crypto weight pct: {candidate.max_crypto_weight_pct()}",
                f"- min cash or defensive pct: {candidate.min_cash_or_defensive_pct()}",
                f"- manual review required: {candidate.manual_review_required}",
                f"- operator approved: {candidate.operator_approved}",
                f"- active policy mutated: {candidate.active_policy_mutated}",
                f"- creates weekly buy ticket: {candidate.creates_weekly_buy_ticket}",
                f"- creates buy request: {candidate.creates_buy_request}",
                f"- executes trade: {candidate.executes_trade}",
                "",
                "#### Allocation Bands",
            ]
        )
        for band in candidate.allocation_bands:
            lines.append(
                f"- {band.sleeve_id}: min={band.min_pct}, preferred={band.preferred_low_pct}-{band.preferred_high_pct}, max={band.max_pct}"
            )

        lines.extend(["", "#### Selected Assets"])
        for selection in candidate.selected_assets:
            lines.append(
                f"- {selection.candidate_id}: {selection.role}, sleeve={selection.sleeve_id}, quality={selection.quality_status}, max={selection.max_candidate_weight_pct}"
            )

        lines.extend(["", "#### Explicit Exclusions"])
        if candidate.explicit_exclusions:
            lines.extend(f"- {item}" for item in candidate.explicit_exclusions)
        else:
            lines.append("- none")

        lines.extend(["", "#### Warnings"])
        if candidate.warnings:
            lines.extend(f"- {warning}" for warning in candidate.warnings)
        else:
            lines.append("- none")

        lines.extend(["", "#### Blockers"])
        if candidate.blockers:
            lines.extend(f"- {blocker}" for blocker in candidate.blockers)
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
            f"- policy candidate generation ready: {result.policy_candidate_generation_ready}",
            f"- manual review required: {result.manual_review_required}",
            f"- active policy mutated: {result.active_policy_mutated}",
            f"- policy approval deferred: {result.policy_approval_deferred}",
            f"- asset approval deferred: {result.asset_approval_deferred}",
            f"- weekly buy ticket deferred: {result.weekly_buy_ticket_deferred}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- automatic approval forbidden: {result.automatic_approval_forbidden}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_5_policy_candidate_generator() -> str:
    return build_v6_5_policy_candidate_generator_report(
        audit_v6_5_policy_candidate_generator()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.5 policy candidate generator."
    )
    parser.parse_args()
    print(report_v6_5_policy_candidate_generator())


if __name__ == "__main__":
    main()
