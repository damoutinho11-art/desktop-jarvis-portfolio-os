"""Report CLI for J.A.R.V.I.S. v6.3 universal asset candidate registry."""

from __future__ import annotations

import argparse

from .jarvis_v6_3_universal_asset_candidate_registry import (
    UniversalAssetCandidateRegistryResult,
    audit_v6_3_universal_asset_candidate_registry,
)


def build_v6_3_universal_asset_candidate_registry_report(
    result: UniversalAssetCandidateRegistryResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.3 Universal Asset Candidate Registry",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"candidate count: {result.candidate_count}",
        f"quality scoring ready count: {result.quality_scoring_ready_count}",
        f"approved policy asset count: {result.approved_policy_asset_count}",
        f"weekly buy candidate count: {result.weekly_buy_candidate_count}",
        "",
        "## Asset Types Covered",
    ]

    lines.extend(f"- {asset_type}" for asset_type in result.asset_types_covered)

    lines.extend(["", "## Candidate States Present"])
    lines.extend(f"- {state}" for state in result.candidate_states_present)

    lines.extend(["", "## Candidates"])
    for candidate in result.candidates:
        lines.extend(
            [
                "",
                f"### {candidate.candidate_id}",
                f"- display name: {candidate.display_name}",
                f"- asset type: {candidate.asset_type}",
                f"- state: {candidate.candidate_state}",
                f"- sleeve ids: {', '.join(candidate.sleeve_ids)}",
                f"- currency: {candidate.currency}",
                f"- region/network: {candidate.region_or_network}",
                f"- platform options: {', '.join(candidate.platform_options)}",
                f"- required data ready: {candidate.required_data_ready()}",
                f"- blocker free: {candidate.blocker_free()}",
                f"- can enter quality scoring next: {candidate.can_enter_quality_scoring_next()}",
                f"- operator approved: {candidate.operator_approved}",
                f"- policy asset approved: {candidate.policy_asset_approved}",
                f"- weekly buy candidate: {candidate.weekly_buy_candidate}",
                f"- creates buy request: {candidate.creates_buy_request}",
                f"- executes trade: {candidate.executes_trade}",
            ]
        )

        lines.append("- data requirements:")
        for requirement in candidate.data_requirements:
            lines.append(
                f"  - {requirement.requirement_id}: required={requirement.required}, "
                f"satisfied={requirement.satisfied}, source={requirement.source_kind}"
            )

        lines.append("- eligibility checks:")
        for check in candidate.eligibility_checks:
            lines.append(
                f"  - {check.check_id}: passed={check.passed}, severity={check.severity}, "
                f"message={check.message}"
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
            f"- broad universe registry ready: {result.broad_universe_registry_ready}",
            f"- candidates only: {result.candidates_only}",
            f"- exact asset scoring deferred: {result.exact_asset_scoring_deferred}",
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


def report_v6_3_universal_asset_candidate_registry() -> str:
    return build_v6_3_universal_asset_candidate_registry_report(
        audit_v6_3_universal_asset_candidate_registry()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.3 universal asset candidate registry."
    )
    parser.parse_args()
    print(report_v6_3_universal_asset_candidate_registry())


if __name__ == "__main__":
    main()
