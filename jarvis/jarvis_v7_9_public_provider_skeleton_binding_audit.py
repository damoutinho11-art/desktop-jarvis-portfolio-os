"""J.A.R.V.I.S. v7.9 public provider skeleton binding audit.

This stage audits that every disabled live-fetch adapter skeleton from v7.6
can be matched to an approved public provider configuration from v7.8.

It does not enable live fetching.

Safety boundary:
- provider/skeleton binding audit only
- providers remain disabled by default
- adapter remains disabled
- no network calls attempted
- no raw response storage
- no live adapter record emission
- no buy request creation
- no broker/API connection
- no order placement
- no trade execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v7_6_disabled_live_public_market_fetch_adapter_skeleton import (
    DisabledLivePublicMarketFetchAdapterSkeleton,
    STATUS_READY as V7_6_STATUS_READY,
    audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton,
)
from .jarvis_v7_8_public_provider_configuration_registry import (
    PublicProviderConfiguration,
    STATUS_READY as V7_8_STATUS_READY,
    audit_v7_8_public_provider_configuration_registry,
)


STATUS_READY = "JARVIS_V7_9_PUBLIC_PROVIDER_SKELETON_BINDING_AUDIT_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V7_9_PUBLIC_PROVIDER_SKELETON_BINDING_AUDIT_BLOCKED_SAFE"

NEXT_STAGE = "v7_10_live_public_market_intelligence_readiness_closeout_audit"

BINDING_STATUS_READY = "PUBLIC_PROVIDER_SKELETON_BINDING_AUDIT_READY"
BINDING_STATUS_BLOCKED = "PUBLIC_PROVIDER_SKELETON_BINDING_AUDIT_BLOCKED"


@dataclass(frozen=True)
class PublicProviderSkeletonBinding:
    binding_id: str
    skeleton_id: str
    provider_id: str
    candidate_id: str
    endpoint_category: str
    skeleton_provider_name: str
    provider_name: str
    provider_type: str
    provider_auth_mode: str
    provider_disabled_by_default: bool
    adapter_disabled: bool
    endpoint_category_match: bool
    selected_candidate_covered: bool
    usable_for_dry_run_plans: bool
    binding_ready: bool
    live_fetch_enabled: bool
    network_call_allowed: bool
    raw_response_storage_allowed: bool
    live_adapter_record_emission_allowed: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_binding_only(self) -> bool:
        return (
            self.binding_ready
            and self.endpoint_category_match
            and self.usable_for_dry_run_plans
            and self.provider_disabled_by_default
            and self.adapter_disabled
            and not self.live_fetch_enabled
            and not self.network_call_allowed
            and not self.raw_response_storage_allowed
            and not self.live_adapter_record_emission_allowed
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "binding_id": self.binding_id,
            "skeleton_id": self.skeleton_id,
            "provider_id": self.provider_id,
            "candidate_id": self.candidate_id,
            "endpoint_category": self.endpoint_category,
            "skeleton_provider_name": self.skeleton_provider_name,
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "provider_auth_mode": self.provider_auth_mode,
            "provider_disabled_by_default": self.provider_disabled_by_default,
            "adapter_disabled": self.adapter_disabled,
            "endpoint_category_match": self.endpoint_category_match,
            "selected_candidate_covered": self.selected_candidate_covered,
            "usable_for_dry_run_plans": self.usable_for_dry_run_plans,
            "binding_ready": self.binding_ready,
            "live_fetch_enabled": self.live_fetch_enabled,
            "network_call_allowed": self.network_call_allowed,
            "raw_response_storage_allowed": self.raw_response_storage_allowed,
            "live_adapter_record_emission_allowed": self.live_adapter_record_emission_allowed,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_binding_only": self.safe_binding_only(),
        }


@dataclass(frozen=True)
class PublicProviderSkeletonBindingAuditResult:
    status: str
    binding_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    binding_count: int
    skeleton_count: int
    provider_count: int
    unbound_skeleton_count: int
    selected_candidate_binding_count: int
    provider_disabled_binding_count: int
    adapter_disabled_binding_count: int
    live_fetch_enabled_count: int
    network_call_allowed_count: int
    raw_response_storage_allowed_count: int
    live_adapter_record_emission_allowed_count: int
    compatible_with_v7_6_disabled_adapter_skeleton: bool
    compatible_with_v7_8_provider_registry: bool
    bindings: tuple[PublicProviderSkeletonBinding, ...]
    unbound_skeleton_ids: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    binding_audit_ready: bool
    binding_audit_only: bool
    providers_disabled_by_default: bool
    adapters_disabled_by_default: bool
    live_fetch_deferred: bool
    network_calls_deferred: bool
    raw_response_storage_deferred: bool
    live_adapter_record_emission_deferred: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "binding_status": self.binding_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "binding_count": self.binding_count,
            "skeleton_count": self.skeleton_count,
            "provider_count": self.provider_count,
            "unbound_skeleton_count": self.unbound_skeleton_count,
            "selected_candidate_binding_count": self.selected_candidate_binding_count,
            "provider_disabled_binding_count": self.provider_disabled_binding_count,
            "adapter_disabled_binding_count": self.adapter_disabled_binding_count,
            "live_fetch_enabled_count": self.live_fetch_enabled_count,
            "network_call_allowed_count": self.network_call_allowed_count,
            "raw_response_storage_allowed_count": self.raw_response_storage_allowed_count,
            "live_adapter_record_emission_allowed_count": self.live_adapter_record_emission_allowed_count,
            "compatible_with_v7_6_disabled_adapter_skeleton": self.compatible_with_v7_6_disabled_adapter_skeleton,
            "compatible_with_v7_8_provider_registry": self.compatible_with_v7_8_provider_registry,
            "bindings": [binding.to_dict() for binding in self.bindings],
            "unbound_skeleton_ids": list(self.unbound_skeleton_ids),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "binding_audit_ready": self.binding_audit_ready,
            "binding_audit_only": self.binding_audit_only,
            "providers_disabled_by_default": self.providers_disabled_by_default,
            "adapters_disabled_by_default": self.adapters_disabled_by_default,
            "live_fetch_deferred": self.live_fetch_deferred,
            "network_calls_deferred": self.network_calls_deferred,
            "raw_response_storage_deferred": self.raw_response_storage_deferred,
            "live_adapter_record_emission_deferred": self.live_adapter_record_emission_deferred,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _provider_for_skeleton(
    skeleton: DisabledLivePublicMarketFetchAdapterSkeleton,
    providers: tuple[PublicProviderConfiguration, ...],
) -> PublicProviderConfiguration | None:
    endpoint_matches = [
        provider
        for provider in providers
        if provider.endpoint_category == skeleton.endpoint_category
    ]
    if endpoint_matches:
        selected_matches = [
            provider for provider in endpoint_matches if provider.covers_selected_candidate
        ]
        if skeleton.candidate_id == "btc_candidate" and selected_matches:
            return selected_matches[0]
        return endpoint_matches[0]
    return None


def build_public_provider_skeleton_bindings(
    skeletons: tuple[DisabledLivePublicMarketFetchAdapterSkeleton, ...],
    providers: tuple[PublicProviderConfiguration, ...],
) -> tuple[PublicProviderSkeletonBinding, ...]:
    bindings: list[PublicProviderSkeletonBinding] = []

    for skeleton in skeletons:
        provider = _provider_for_skeleton(skeleton, providers)
        if provider is None:
            continue

        endpoint_match = provider.endpoint_category == skeleton.endpoint_category
        provider_disabled = not provider.provider_enabled_by_default
        adapter_disabled = not skeleton.adapter_enabled

        bindings.append(
            PublicProviderSkeletonBinding(
                binding_id=f"binding_{skeleton.skeleton_id}_to_{provider.provider_id}",
                skeleton_id=skeleton.skeleton_id,
                provider_id=provider.provider_id,
                candidate_id=skeleton.candidate_id,
                endpoint_category=skeleton.endpoint_category,
                skeleton_provider_name=skeleton.provider_name,
                provider_name=provider.provider_name,
                provider_type=provider.provider_type,
                provider_auth_mode=provider.auth_mode,
                provider_disabled_by_default=provider_disabled,
                adapter_disabled=adapter_disabled,
                endpoint_category_match=endpoint_match,
                selected_candidate_covered=provider.covers_selected_candidate,
                usable_for_dry_run_plans=provider.usable_for_dry_run_plans,
                binding_ready=endpoint_match and provider_disabled and adapter_disabled,
                live_fetch_enabled=provider.live_fetch_enabled or skeleton.live_fetch_enabled,
                network_call_allowed=provider.network_call_allowed or skeleton.network_call_allowed,
                raw_response_storage_allowed=(
                    provider.raw_response_storage_allowed or skeleton.raw_response_storage_allowed
                ),
                live_adapter_record_emission_allowed=(
                    provider.emits_live_adapter_record or skeleton.emits_live_adapter_record
                ),
                creates_buy_request=provider.creates_buy_request or skeleton.creates_buy_request,
                connects_broker=provider.connects_broker or skeleton.connects_broker,
                places_order=provider.places_order or skeleton.places_order,
                executes_trade=provider.executes_trade or skeleton.executes_trade,
            )
        )

    return tuple(bindings)


def audit_v7_9_public_provider_skeleton_binding_audit(
    bindings: tuple[PublicProviderSkeletonBinding, ...] | None | object = None,
) -> PublicProviderSkeletonBindingAuditResult:
    skeleton_result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()
    provider_result = audit_v7_8_public_provider_configuration_registry()

    if bindings is None:
        effective_bindings = build_public_provider_skeleton_bindings(
            skeleton_result.adapter_skeletons,
            provider_result.providers,
        )
        invalid_override = False
    elif isinstance(bindings, tuple):
        effective_bindings = bindings
        invalid_override = False
    else:
        effective_bindings = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v7.9 audits provider-to-skeleton bindings only.",
        "Provider and adapter paths remain disabled by default.",
        "No live public network call is attempted in v7.9.",
        "No raw public response payload is stored in v7.9.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Binding override must be a tuple of PublicProviderSkeletonBinding.")

    if skeleton_result.status != V7_6_STATUS_READY or skeleton_result.blockers:
        blockers.append("Source v7.6 disabled live public market fetch adapter skeleton is blocked.")
    if provider_result.status != V7_8_STATUS_READY or provider_result.blockers:
        blockers.append("Source v7.8 public provider configuration registry is blocked.")

    if not effective_bindings:
        blockers.append("No public provider skeleton bindings were produced.")

    skeleton_ids = {skeleton.skeleton_id for skeleton in skeleton_result.adapter_skeletons}
    provider_ids = {provider.provider_id for provider in provider_result.providers}
    binding_ids: list[str] = []
    bound_skeleton_ids: list[str] = []
    clean_bindings: list[PublicProviderSkeletonBinding] = []

    for index, binding in enumerate(effective_bindings):
        if not isinstance(binding, PublicProviderSkeletonBinding):
            blockers.append(f"Binding at index {index} must be a PublicProviderSkeletonBinding.")
            continue

        clean_bindings.append(binding)
        binding_ids.append(binding.binding_id)
        bound_skeleton_ids.append(binding.skeleton_id)

        if not binding.binding_id.strip():
            blockers.append("Binding ID is required.")
        if binding.skeleton_id not in skeleton_ids:
            blockers.append(f"{binding.binding_id}: skeleton ID is not registered in v7.6.")
        if binding.provider_id not in provider_ids:
            blockers.append(f"{binding.binding_id}: provider ID is not registered in v7.8.")
        if not binding.candidate_id.strip():
            blockers.append(f"{binding.binding_id}: candidate ID is required.")
        if not binding.endpoint_category.strip():
            blockers.append(f"{binding.binding_id}: endpoint category is required.")
        if not binding.skeleton_provider_name.strip():
            blockers.append(f"{binding.binding_id}: skeleton provider name is required.")
        if not binding.provider_name.strip():
            blockers.append(f"{binding.binding_id}: provider name is required.")
        if not binding.provider_type.strip():
            blockers.append(f"{binding.binding_id}: provider type is required.")
        if not binding.provider_auth_mode.strip():
            blockers.append(f"{binding.binding_id}: provider auth mode is required.")
        if not binding.endpoint_category_match:
            blockers.append(f"{binding.binding_id}: endpoint category must match.")
        if not binding.usable_for_dry_run_plans:
            blockers.append(f"{binding.binding_id}: provider must be usable for dry-run plans.")
        if not binding.provider_disabled_by_default:
            blockers.append(f"{binding.binding_id}: provider must remain disabled by default.")
        if not binding.adapter_disabled:
            blockers.append(f"{binding.binding_id}: adapter skeleton must remain disabled.")
        if not binding.binding_ready:
            blockers.append(f"{binding.binding_id}: binding must be ready.")
        if binding.live_fetch_enabled:
            blockers.append(f"{binding.binding_id}: live fetching is forbidden in v7.9.")
        if binding.network_call_allowed:
            blockers.append(f"{binding.binding_id}: network calls are forbidden in v7.9.")
        if binding.raw_response_storage_allowed:
            blockers.append(f"{binding.binding_id}: raw response storage is forbidden in v7.9.")
        if binding.live_adapter_record_emission_allowed:
            blockers.append(f"{binding.binding_id}: live adapter record emission is forbidden in v7.9.")
        if not binding.safe_binding_only():
            blockers.append(f"{binding.binding_id}: binding must remain audit-only and non-executable.")
        if binding.creates_buy_request:
            blockers.append(f"{binding.binding_id}: buy request creation is forbidden.")
        if binding.connects_broker:
            blockers.append(f"{binding.binding_id}: broker connection is forbidden.")
        if binding.places_order:
            blockers.append(f"{binding.binding_id}: order placement is forbidden.")
        if binding.executes_trade:
            blockers.append(f"{binding.binding_id}: trade execution is forbidden.")

    if len(binding_ids) != len(set(binding_ids)):
        blockers.append("Public provider skeleton binding IDs must be unique.")

    unbound_skeleton_ids = tuple(sorted(skeleton_ids - set(bound_skeleton_ids)))
    if unbound_skeleton_ids:
        blockers.append("Every disabled adapter skeleton must bind to an approved public provider configuration.")

    clean_binding_tuple = tuple(clean_bindings)

    selected_candidate_binding_count = sum(
        1
        for binding in clean_binding_tuple
        if binding.candidate_id == skeleton_result.selected_candidate_id
    )
    if selected_candidate_binding_count <= 0:
        blockers.append("At least one binding must cover the selected candidate.")

    provider_disabled_binding_count = sum(
        1 for binding in clean_binding_tuple if binding.provider_disabled_by_default
    )
    adapter_disabled_binding_count = sum(
        1 for binding in clean_binding_tuple if binding.adapter_disabled
    )
    live_fetch_enabled_count = sum(1 for binding in clean_binding_tuple if binding.live_fetch_enabled)
    network_call_allowed_count = sum(1 for binding in clean_binding_tuple if binding.network_call_allowed)
    raw_response_storage_allowed_count = sum(
        1 for binding in clean_binding_tuple if binding.raw_response_storage_allowed
    )
    live_adapter_record_emission_allowed_count = sum(
        1 for binding in clean_binding_tuple if binding.live_adapter_record_emission_allowed
    )

    safety_flags = {
        "binding_audit_ready": False,
        "binding_audit_only": True,
        "providers_disabled_by_default": provider_disabled_binding_count == len(clean_binding_tuple),
        "adapters_disabled_by_default": adapter_disabled_binding_count == len(clean_binding_tuple),
        "live_fetch_deferred": live_fetch_enabled_count == 0,
        "network_calls_deferred": network_call_allowed_count == 0,
        "raw_response_storage_deferred": raw_response_storage_allowed_count == 0,
        "live_adapter_record_emission_deferred": live_adapter_record_emission_allowed_count == 0,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["binding_audit_only"]:
        blockers.append("v7.9 must remain binding-audit-only.")
    if not safety_flags["providers_disabled_by_default"]:
        blockers.append("v7.9 must keep all bound providers disabled by default.")
    if not safety_flags["adapters_disabled_by_default"]:
        blockers.append("v7.9 must keep all bound adapters disabled by default.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v7.9 must defer live fetching.")
    if not safety_flags["network_calls_deferred"]:
        blockers.append("v7.9 must defer network calls.")
    if not safety_flags["raw_response_storage_deferred"]:
        blockers.append("v7.9 must defer raw response storage.")
    if not safety_flags["live_adapter_record_emission_deferred"]:
        blockers.append("v7.9 must defer live adapter record emission.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v7.9 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v7.9 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v7.9 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v7.9 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return PublicProviderSkeletonBindingAuditResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        binding_status=BINDING_STATUS_READY if ready else BINDING_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=skeleton_result.selected_candidate_id,
        selected_sleeve_id=skeleton_result.selected_sleeve_id,
        binding_count=len(clean_binding_tuple),
        skeleton_count=len(skeleton_result.adapter_skeletons),
        provider_count=len(provider_result.providers),
        unbound_skeleton_count=len(unbound_skeleton_ids),
        selected_candidate_binding_count=selected_candidate_binding_count,
        provider_disabled_binding_count=provider_disabled_binding_count,
        adapter_disabled_binding_count=adapter_disabled_binding_count,
        live_fetch_enabled_count=live_fetch_enabled_count,
        network_call_allowed_count=network_call_allowed_count,
        raw_response_storage_allowed_count=raw_response_storage_allowed_count,
        live_adapter_record_emission_allowed_count=live_adapter_record_emission_allowed_count,
        compatible_with_v7_6_disabled_adapter_skeleton=skeleton_result.status == V7_6_STATUS_READY,
        compatible_with_v7_8_provider_registry=provider_result.status == V7_8_STATUS_READY,
        bindings=clean_binding_tuple,
        unbound_skeleton_ids=unbound_skeleton_ids,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "binding_audit_ready": ready},
    )
