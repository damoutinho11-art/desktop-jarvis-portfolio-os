"""Report CLI for J.A.R.V.I.S. v6.1 policy intelligence boundary."""

from __future__ import annotations

import argparse

from .jarvis_v6_1_policy_intelligence_boundary import (
    PolicyIntelligenceBoundaryResult,
    audit_v6_1_policy_intelligence_boundary,
)


def build_v6_1_policy_intelligence_boundary_report(
    result: PolicyIntelligenceBoundaryResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v6.1 Policy Intelligence Boundary",
        "",
        f"status: {result.status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"candidate policy count: {result.candidate_policy_count}",
        f"recommended policy id: {result.recommended_policy_id}",
        "",
        "## Boundary Flags",
        "",
        f"- policy intelligence enabled: {result.policy_intelligence_enabled}",
        f"- flexible bands required: {result.flexible_bands_required}",
        f"- broad ETF universe required: {result.broad_etf_universe_required}",
        (
            "- weekly crypto buy allowed if within risk bands: "
            f"{result.weekly_crypto_buy_allowed_if_within_risk_bands}"
        ),
        "",
        "## Candidate Policies",
    ]

    for policy in result.candidate_policies:
        lines.extend(
            [
                "",
                f"### {policy.policy_id}",
                f"- name: {policy.name}",
                f"- status: {policy.status}",
                f"- risk profile: {policy.risk_profile}",
                f"- score total: {policy.score_total}",
                f"- crypto weekly buy allowed: {policy.crypto_weekly_buy_allowed()}",
                f"- uses flexible bands: {policy.uses_flexible_bands()}",
                f"- broad ETF universe: {policy.has_broad_etf_universe()}",
                f"- max crypto weight pct: {policy.max_crypto_weight_pct()}",
                f"- manual policy-change ticket required: {policy.manual_policy_change_ticket_required}",
                f"- active policy mutated: {policy.active_policy_mutated}",
                f"- automatic approval granted: {policy.automatic_approval_granted}",
                f"- creates buy request: {policy.creates_buy_request}",
                f"- executes trade: {policy.executes_trade}",
                "- score breakdown:",
            ]
        )
        for key, value in policy.score_breakdown.items():
            lines.append(f"  - {key}: {value}")

        lines.append("- bands:")
        for band in policy.bands:
            lines.extend(
                [
                    f"  - {band.sleeve_id}:",
                    (
                        "    - range: "
                        f"{band.min_weight_pct} / {band.preferred_min_weight_pct}-"
                        f"{band.preferred_max_weight_pct} / {band.max_weight_pct}"
                    ),
                    f"    - weekly buy allowed: {band.weekly_buy_allowed}",
                    f"    - asset universe: {', '.join(band.asset_universe)}",
                ]
            )

        lines.append("- rationale:")
        lines.extend(f"  - {item}" for item in policy.rationale)

        lines.append("- counterarguments:")
        lines.extend(f"  - {item}" for item in policy.counterarguments)

    lines.extend(["", "## Policy Change Tickets"])
    for ticket in result.policy_change_tickets:
        lines.extend(
            [
                "",
                f"### {ticket.candidate_policy_id}",
                f"- ticket type: {ticket.ticket_type}",
                f"- manual approval required: {ticket.manual_approval_required}",
                f"- approved: {ticket.approved}",
                f"- active policy mutated: {ticket.active_policy_mutated}",
                f"- creates buy request: {ticket.creates_buy_request}",
                f"- executes trade: {ticket.executes_trade}",
                f"- reason: {ticket.reason}",
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
            f"- active policy mutated: {result.active_policy_mutated}",
            f"- automatic policy change forbidden: {result.automatic_policy_change_forbidden}",
            f"- automatic approval forbidden: {result.automatic_approval_forbidden}",
            f"- manual policy approval required: {result.manual_policy_approval_required}",
            f"- broker execution forbidden: {result.broker_execution_forbidden}",
            f"- creates buy request: {result.creates_buy_request}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v6_1_policy_intelligence_boundary() -> str:
    return build_v6_1_policy_intelligence_boundary_report(
        audit_v6_1_policy_intelligence_boundary()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v6.1 policy intelligence boundary."
    )
    parser.parse_args()
    print(report_v6_1_policy_intelligence_boundary())


if __name__ == "__main__":
    main()
