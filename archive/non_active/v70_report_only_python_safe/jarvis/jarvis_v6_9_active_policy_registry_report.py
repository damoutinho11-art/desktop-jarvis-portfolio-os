"""Report CLI for J.A.R.V.I.S. v6.9 active policy registry."""

from __future__ import annotations

import argparse

from .jarvis_v6_9_active_policy_registry import (
    ActivePolicyRegistryResult,
    audit_v6_9_active_policy_registry,
)


def build_v6_9_active_policy_registry_report(
    result: ActivePolicyRegistryResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.9 Active Policy Registry",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"source draft count: {result.source_draft_count}",
        f"source approval decision count: {result.source_approval_decision_count}",
        f"approved draft count: {result.approved_draft_count}",
        f"active policy count: {result.active_policy_count}",
        "",
        "## Active Policies",
    ]

    for policy in result.active_policies:
        lines.extend(
            [
                "",
                f"### {policy.active_policy_id}",
                f"- source approval id: {policy.source_approval_id}",
                f"- source draft id: {policy.source_draft_id}",
                f"- source policy id: {policy.source_policy_id}",
                f"- display name: {policy.display_name}",
                f"- policy status: {policy.policy_status}",
                f"- policy version: {policy.policy_version}",
                f"- aggressiveness score: {policy.aggressiveness_score}",
                f"- suitability reason: {policy.suitability_reason}",
                f"- max crypto weight pct: {policy.max_crypto_weight_pct()}",
                f"- min defensive weight pct: {policy.min_defensive_weight_pct()}",
                f"- manually approved: {policy.manually_approved}",
                f"- active policy created: {policy.active_policy_created}",
                f"- automatic policy change allowed: {policy.automatic_policy_change_allowed}",
                f"- assets individually approved: {policy.assets_individually_approved}",
                f"- creates weekly buy ticket: {policy.creates_weekly_buy_ticket}",
                f"- creates buy request: {policy.creates_buy_request}",
                f"- connects broker: {policy.connects_broker}",
                f"- executes trade: {policy.executes_trade}",
                "",
                "#### Allocation Bands",
            ]
        )
        for band in policy.allocation_bands:
            lines.append(
                f"- {band.sleeve_id}: min={band.min_pct}, preferred={band.preferred_low_pct}-{band.preferred_high_pct}, max={band.max_pct}"
            )

        lines.extend(["", "#### Selected Assets"])
        for selection in policy.selected_assets:
            lines.append(
                f"- {selection.candidate_id}: role={selection.role}, sleeve={selection.sleeve_id}, quality={selection.quality_status}"
            )

        lines.extend(["", "#### Policy Constraints"])
        lines.extend(f"- {item}" for item in policy.policy_constraints)

        lines.extend(["", "#### Monitoring Rules"])
        lines.extend(f"- {item}" for item in policy.monitoring_rules)

        lines.extend(["", "#### Warnings"])
        if policy.warnings:
            lines.extend(f"- {warning}" for warning in policy.warnings)
        else:
            lines.append("- none")

        lines.extend(["", "#### Blockers"])
        if policy.blockers:
            lines.extend(f"- {blocker}" for blocker in policy.blockers)
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
            f"- active policy registry ready: {result.active_policy_registry_ready}",
            f"- active policy record created: {result.active_policy_record_created}",
            f"- manual approval satisfied: {result.manual_approval_satisfied}",
            f"- automatic policy change forbidden: {result.automatic_policy_change_forbidden}",
            f"- asset approval deferred: {result.asset_approval_deferred}",
            f"- weekly buy ticket deferred: {result.weekly_buy_ticket_deferred}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_9_active_policy_registry() -> str:
    return build_v6_9_active_policy_registry_report(audit_v6_9_active_policy_registry())


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.9 active policy registry."
    )
    parser.parse_args()
    print(report_v6_9_active_policy_registry())


if __name__ == "__main__":
    main()
