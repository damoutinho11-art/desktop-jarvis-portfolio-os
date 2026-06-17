"""Report CLI for J.A.R.V.I.S. v7.8 public provider configuration registry."""

from __future__ import annotations

import argparse

from .jarvis_v7_8_public_provider_configuration_registry import (
    PublicProviderConfigurationRegistryResult,
    audit_v7_8_public_provider_configuration_registry,
)


def build_v7_8_public_provider_configuration_registry_report(
    result: PublicProviderConfigurationRegistryResult,
) -> str:
    lines: list[str] = [
        "# J.A.R.V.I.S. v7.8 Public Provider Configuration Registry",
        "",
        f"status: {result.status}",
        f"registry status: {result.registry_status}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"selected candidate id: {result.selected_candidate_id}",
        f"selected sleeve id: {result.selected_sleeve_id}",
        f"provider count: {result.provider_count}",
        f"selected candidate provider count: {result.selected_candidate_provider_count}",
        f"enabled provider count: {result.enabled_provider_count}",
        f"live fetch enabled count: {result.live_fetch_enabled_count}",
        f"network call allowed count: {result.network_call_allowed_count}",
        f"raw response storage allowed count: {result.raw_response_storage_allowed_count}",
        f"live adapter record emit count: {result.live_adapter_record_emit_count}",
        f"no-auth provider count: {result.no_auth_provider_count}",
        f"env-api-key provider count: {result.env_api_key_provider_count}",
        f"compatible with v7.7 enablement preflight: {result.compatible_with_v7_7_enablement_preflight}",
        "",
        "## Public Provider Configurations",
    ]

    for provider in result.providers:
        lines.extend(
            [
                "",
                f"### {provider.provider_id}",
                f"- provider name: {provider.provider_name}",
                f"- provider type: {provider.provider_type}",
                f"- endpoint category: {provider.endpoint_category}",
                f"- base url reference: {provider.base_url_reference}",
                f"- auth mode: {provider.auth_mode}",
                f"- api key env var: {provider.api_key_env_var}",
                f"- timeout seconds: {provider.timeout_seconds}",
                f"- rate limit per minute: {provider.rate_limit_per_minute}",
                f"- max records per request: {provider.max_records_per_request}",
                f"- raw response storage policy: {provider.raw_response_storage_policy}",
                f"- cache policy: {provider.cache_policy}",
                f"- configuration source: {provider.configuration_source}",
                f"- covers selected candidate: {provider.covers_selected_candidate}",
                f"- usable for dry-run plans: {provider.usable_for_dry_run_plans}",
                f"- provider enabled by default: {provider.provider_enabled_by_default}",
                f"- live fetch enabled: {provider.live_fetch_enabled}",
                f"- network call allowed: {provider.network_call_allowed}",
                f"- raw response storage allowed: {provider.raw_response_storage_allowed}",
                f"- emits live adapter record: {provider.emits_live_adapter_record}",
                f"- creates buy request: {provider.creates_buy_request}",
                f"- connects broker: {provider.connects_broker}",
                f"- places order: {provider.places_order}",
                f"- executes trade: {provider.executes_trade}",
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
            f"- provider registry ready: {result.provider_registry_ready}",
            f"- registry only: {result.registry_only}",
            f"- providers disabled by default: {result.providers_disabled_by_default}",
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


def report_v7_8_public_provider_configuration_registry() -> str:
    return build_v7_8_public_provider_configuration_registry_report(
        audit_v7_8_public_provider_configuration_registry()
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report J.A.R.V.I.S. v7.8 public provider configuration registry."
    )
    parser.parse_args()
    print(report_v7_8_public_provider_configuration_registry())


if __name__ == "__main__":
    main()
