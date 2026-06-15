"""Report CLI for J.A.R.V.I.S. v7.10 readiness closeout audit."""

from __future__ import annotations

import argparse

from .jarvis_v7_10_live_public_market_intelligence_readiness_closeout_audit import (
    LivePublicMarketReadinessCloseoutAuditResult,
    audit_v7_10_live_public_market_intelligence_readiness_closeout_audit,
)


def build_v7_10_live_public_market_intelligence_readiness_closeout_audit_report(
    result: LivePublicMarketReadinessCloseoutAuditResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v7.10 Live Public Market Intelligence Readiness Closeout Audit",
        "",
        f"status: {result.status}",
        f"closeout status: {result.closeout_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"check count: {result.check_count}",
        f"passed check count: {result.passed_check_count}",
        f"failed check count: {result.failed_check_count}",
        f"required check count: {result.required_check_count}",
        f"chain stage count: {result.chain_stage_count}",
        f"ready chain stage count: {result.ready_chain_stage_count}",
        f"live fetch enablement allowed: {result.live_fetch_enablement_allowed}",
        f"v7 chain closeout complete: {result.v7_chain_closeout_complete}",
        "",
        "## Closeout Checks",
    ]

    for check in result.checks:
        lines.extend(
            [
                "",
                f"### {check.check_id}",
                f"- stage id: {check.stage_id}",
                f"- title: {check.title}",
                f"- expected status: {check.expected_status}",
                f"- observed status: {check.observed_status}",
                f"- status: {check.status}",
                f"- evidence: {check.evidence}",
                f"- required for closeout: {check.required_for_closeout}",
                f"- live fetch enabled: {check.live_fetch_enabled}",
                f"- network call attempted: {check.network_call_attempted}",
                f"- raw response stored: {check.raw_response_stored}",
                f"- live adapter record emitted: {check.live_adapter_record_emitted}",
                f"- creates buy request: {check.creates_buy_request}",
                f"- connects broker: {check.connects_broker}",
                f"- places order: {check.places_order}",
                f"- executes trade: {check.executes_trade}",
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
            f"- readiness closeout ready: {result.readiness_closeout_ready}",
            f"- closeout audit only: {result.closeout_audit_only}",
            f"- providers disabled by default: {result.providers_disabled_by_default}",
            f"- adapters disabled by default: {result.adapters_disabled_by_default}",
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


def report_v7_10_live_public_market_intelligence_readiness_closeout_audit() -> str:
    return build_v7_10_live_public_market_intelligence_readiness_closeout_audit_report(
        audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v7.10 readiness closeout audit."
    )
    parser.parse_args()
    print(report_v7_10_live_public_market_intelligence_readiness_closeout_audit())


if __name__ == "__main__":
    main()
