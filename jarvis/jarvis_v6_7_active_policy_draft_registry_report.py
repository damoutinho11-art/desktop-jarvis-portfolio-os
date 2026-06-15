"""Report CLI for J.A.R.V.I.S. v6.7 active policy draft registry."""

from __future__ import annotations

import argparse

from .jarvis_v6_7_active_policy_draft_registry import (
    ActivePolicyDraftRegistryResult,
    audit_v6_7_active_policy_draft_registry,
)


def build_v6_7_active_policy_draft_registry_report(
    result: ActivePolicyDraftRegistryResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.7 Active Policy Draft Registry",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"source review item count: {result.source_review_item_count}",
        f"accepted review count: {result.accepted_review_count}",
        f"active policy draft count: {result.active_policy_draft_count}",
        f"active policy count: {result.active_policy_count}",
        "",
        "## Draft Items",
    ]

    for draft in result.draft_items:
        lines.extend(
            [
                "",
                f"### {draft.draft_id}",
                f"- source review id: {draft.source_review_id}",
                f"- source policy id: {draft.source_policy_id}",
                f"- display name: {draft.display_name}",
                f"- draft status: {draft.draft_status}",
                f"- aggressiveness score: {draft.aggressiveness_score}",
                f"- suitability reason: {draft.suitability_reason}",
                f"- max crypto weight pct: {draft.max_crypto_weight_pct()}",
                f"- min defensive weight pct: {draft.min_defensive_weight_pct()}",
                f"- manual approval required: {draft.manual_approval_required}",
                f"- operator approved active policy: {draft.operator_approved_active_policy}",
                f"- active policy created: {draft.active_policy_created}",
                f"- active policy mutated: {draft.active_policy_mutated}",
                f"- asset approval created: {draft.asset_approval_created}",
                f"- creates weekly buy ticket: {draft.creates_weekly_buy_ticket}",
                f"- creates buy request: {draft.creates_buy_request}",
                f"- executes trade: {draft.executes_trade}",
                "",
                "#### Allocation Bands",
            ]
        )
        for band in draft.allocation_bands:
            lines.append(
                f"- {band.sleeve_id}: min={band.min_pct}, preferred={band.preferred_low_pct}-{band.preferred_high_pct}, max={band.max_pct}"
            )

        lines.extend(["", "#### Selected Assets"])
        for selection in draft.selected_assets:
            lines.append(
                f"- {selection.candidate_id}: role={selection.role}, sleeve={selection.sleeve_id}, quality={selection.quality_status}"
            )

        lines.extend(["", "#### Risk Constraints"])
        lines.extend(f"- {item}" for item in draft.risk_constraints)

        lines.extend(["", "#### Activation Requirements"])
        lines.extend(f"- {item}" for item in draft.activation_requirements)

        lines.extend(["", "#### Warnings"])
        if draft.warnings:
            lines.extend(f"- {warning}" for warning in draft.warnings)
        else:
            lines.append("- none")

        lines.extend(["", "#### Blockers"])
        if draft.blockers:
            lines.extend(f"- {blocker}" for blocker in draft.blockers)
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
            f"- active policy draft registry ready: {result.active_policy_draft_registry_ready}",
            f"- draft only: {result.draft_only}",
            f"- manual approval required: {result.manual_approval_required}",
            f"- active policy approval deferred: {result.active_policy_approval_deferred}",
            f"- active policy activation deferred: {result.active_policy_activation_deferred}",
            f"- asset approval deferred: {result.asset_approval_deferred}",
            f"- weekly buy ticket deferred: {result.weekly_buy_ticket_deferred}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_7_active_policy_draft_registry() -> str:
    return build_v6_7_active_policy_draft_registry_report(
        audit_v6_7_active_policy_draft_registry()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.7 active policy draft registry."
    )
    parser.parse_args()
    print(report_v6_7_active_policy_draft_registry())


if __name__ == "__main__":
    main()
