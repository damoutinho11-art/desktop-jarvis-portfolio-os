"""Report CLI for J.A.R.V.I.S. v7.9 public provider skeleton binding audit."""

from __future__ import annotations

import argparse

from .jarvis_v7_9_public_provider_skeleton_binding_audit import (
    PublicProviderSkeletonBindingAuditResult,
    audit_v7_9_public_provider_skeleton_binding_audit,
)


def build_v7_9_public_provider_skeleton_binding_audit_report(
    result: PublicProviderSkeletonBindingAuditResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v7.9 Public Provider Skeleton Binding Audit",
        "",
        f"status: {result.status}",
        f"binding status: {result.binding_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"binding count: {result.binding_count}",
        f"skeleton count: {result.skeleton_count}",
        f"provider count: {result.provider_count}",
        f"unbound skeleton count: {result.unbound_skeleton_count}",
        f"selected candidate binding count: {result.selected_candidate_binding_count}",
        f"provider disabled binding count: {result.provider_disabled_binding_count}",
        f"adapter disabled binding count: {result.adapter_disabled_binding_count}",
        f"live fetch enabled count: {result.live_fetch_enabled_count}",
        f"network call allowed count: {result.network_call_allowed_count}",
        f"raw response storage allowed count: {result.raw_response_storage_allowed_count}",
        f"live adapter record emission allowed count: {result.live_adapter_record_emission_allowed_count}",
        f"compatible with v7.6 disabled adapter skeleton: {result.compatible_with_v7_6_disabled_adapter_skeleton}",
        f"compatible with v7.8 provider registry: {result.compatible_with_v7_8_provider_registry}",
        "",
        "## Public Provider Skeleton Bindings",
    ]

    for binding in result.bindings:
        lines.extend(
            [
                "",
                f"### {binding.binding_id}",
                f"- skeleton id: {binding.skeleton_id}",
                f"- provider id: {binding.provider_id}",
                f"- candidate id: {binding.candidate_id}",
                f"- endpoint category: {binding.endpoint_category}",
                f"- skeleton provider name: {binding.skeleton_provider_name}",
                f"- provider name: {binding.provider_name}",
                f"- provider type: {binding.provider_type}",
                f"- provider auth mode: {binding.provider_auth_mode}",
                f"- provider disabled by default: {binding.provider_disabled_by_default}",
                f"- adapter disabled: {binding.adapter_disabled}",
                f"- endpoint category match: {binding.endpoint_category_match}",
                f"- selected candidate covered: {binding.selected_candidate_covered}",
                f"- usable for dry-run plans: {binding.usable_for_dry_run_plans}",
                f"- binding ready: {binding.binding_ready}",
                f"- live fetch enabled: {binding.live_fetch_enabled}",
                f"- network call allowed: {binding.network_call_allowed}",
                f"- raw response storage allowed: {binding.raw_response_storage_allowed}",
                f"- live adapter record emission allowed: {binding.live_adapter_record_emission_allowed}",
                f"- creates buy request: {binding.creates_buy_request}",
                f"- connects broker: {binding.connects_broker}",
                f"- places order: {binding.places_order}",
                f"- executes trade: {binding.executes_trade}",
            ]
        )

    lines.extend(["", "## Unbound Skeletons"])
    if result.unbound_skeleton_ids:
        lines.extend(f"- {skeleton_id}" for skeleton_id in result.unbound_skeleton_ids)
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
            f"- binding audit ready: {result.binding_audit_ready}",
            f"- binding audit only: {result.binding_audit_only}",
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


def report_v7_9_public_provider_skeleton_binding_audit() -> str:
    return build_v7_9_public_provider_skeleton_binding_audit_report(
        audit_v7_9_public_provider_skeleton_binding_audit()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v7.9 public provider skeleton binding audit."
    )
    parser.parse_args()
    print(report_v7_9_public_provider_skeleton_binding_audit())


if __name__ == "__main__":
    main()
