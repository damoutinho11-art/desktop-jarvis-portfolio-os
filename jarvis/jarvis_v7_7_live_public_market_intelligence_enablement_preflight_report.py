"""Report CLI for J.A.R.V.I.S. v7.7 live public market intelligence enablement preflight."""

from __future__ import annotations

import argparse

from .jarvis_v7_7_live_public_market_intelligence_enablement_preflight import (
    LivePublicMarketEnablementPreflightResult,
    audit_v7_7_live_public_market_intelligence_enablement_preflight,
)


def build_v7_7_live_public_market_intelligence_enablement_preflight_report(
    result: LivePublicMarketEnablementPreflightResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v7.7 Live Public Market Intelligence Enablement Preflight",
        "",
        f"status: {result.status}",
        f"preflight status: {result.preflight_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"requirement count: {result.requirement_count}",
        f"passed requirement count: {result.passed_requirement_count}",
        f"failed requirement count: {result.failed_requirement_count}",
        f"required before live enablement count: {result.required_before_live_enablement_count}",
        f"live fetch enablement allowed: {result.live_fetch_enablement_allowed}",
        f"compatible with v7.6 disabled adapter skeleton: {result.compatible_with_v7_6_disabled_adapter_skeleton}",
        "",
        "## Enablement Preflight Requirements",
    ]

    for requirement in result.requirements:
        lines.extend(
            [
                "",
                f"### {requirement.requirement_id}",
                f"- category: {requirement.category}",
                f"- title: {requirement.title}",
                f"- status: {requirement.status}",
                f"- evidence: {requirement.evidence}",
                f"- required before live enablement: {requirement.required_before_live_enablement}",
                f"- blocker if failed: {requirement.blocker_if_failed}",
                f"- adapter still disabled: {requirement.adapter_still_disabled}",
                f"- live fetch still disabled: {requirement.live_fetch_still_disabled}",
                f"- network calls still disabled: {requirement.network_calls_still_disabled}",
                f"- raw response storage still disabled: {requirement.raw_response_storage_still_disabled}",
                f"- live adapter record emission still disabled: {requirement.live_adapter_record_emission_still_disabled}",
                f"- creates buy request: {requirement.creates_buy_request}",
                f"- connects broker: {requirement.connects_broker}",
                f"- places order: {requirement.places_order}",
                f"- executes trade: {requirement.executes_trade}",
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
            f"- enablement preflight ready: {result.enablement_preflight_ready}",
            f"- preflight only: {result.preflight_only}",
            f"- adapter disabled by default: {result.adapter_disabled_by_default}",
            f"- live fetch deferred: {result.live_fetch_deferred}",
            f"- network calls deferred: {result.network_calls_deferred}",
            f"- raw response storage deferred: {result.raw_response_storage_deferred}",
            f"- live adapter record emission deferred: {result.live_adapter_record_emission_deferred}",
            f"- final user buy action required: {result.final_user_buy_action_required}",
            f"- buy request deferred: {result.buy_request_deferred}",
            f"- broker connection forbidden: {result.broker_connection_forbidden}",
            f"- order placement forbidden: {result.order_placement_forbidden}",
            f"- no trades executed: {result.no_trades_executed}",
        ]
    )

    return "\n".join(lines) + "\n"


def report_v7_7_live_public_market_intelligence_enablement_preflight() -> str:
    return build_v7_7_live_public_market_intelligence_enablement_preflight_report(
        audit_v7_7_live_public_market_intelligence_enablement_preflight()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v7.7 live public market intelligence enablement preflight."
    )
    parser.parse_args()
    print(report_v7_7_live_public_market_intelligence_enablement_preflight())


if __name__ == "__main__":
    main()
