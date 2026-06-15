"""J.A.R.V.I.S. v7.6 disabled live public market fetch adapter skeleton.

This stage wires the v7.3 fetch boundary, v7.4 dry-run planner, and v7.5
response normalizer contract into a disabled live-fetch adapter skeleton.

It does not perform live fetching.

Safety boundary:
- disabled adapter skeleton only
- adapter disabled by default
- no network calls attempted
- no raw response storage
- no buy request creation
- no broker/API connection
- no order placement
- no trade execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v7_3_live_public_market_intelligence_fetcher_boundary import (
    STATUS_READY as V7_3_STATUS_READY,
    audit_v7_3_live_public_market_intelligence_fetcher_boundary,
)
from .jarvis_v7_4_live_public_market_intelligence_dry_run_planner import (
    STATUS_READY as V7_4_STATUS_READY,
    audit_v7_4_live_public_market_intelligence_dry_run_planner,
)
from .jarvis_v7_5_live_public_market_intelligence_response_normalizer_contract import (
    STATUS_READY as V7_5_STATUS_READY,
    audit_v7_5_live_public_market_intelligence_response_normalizer_contract,
)


STATUS_READY = "JARVIS_V7_6_DISABLED_LIVE_PUBLIC_MARKET_FETCH_ADAPTER_SKELETON_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V7_6_DISABLED_LIVE_PUBLIC_MARKET_FETCH_ADAPTER_SKELETON_BLOCKED_SAFE"

NEXT_STAGE = "v7_7_live_public_market_intelligence_enablement_preflight"

SKELETON_STATUS_READY = "DISABLED_LIVE_PUBLIC_MARKET_FETCH_ADAPTER_SKELETON_READY"
SKELETON_STATUS_BLOCKED = "DISABLED_LIVE_PUBLIC_MARKET_FETCH_ADAPTER_SKELETON_BLOCKED"


@dataclass(frozen=True)
class DisabledLivePublicMarketFetchAdapterSkeleton:
    skeleton_id: str
    candidate_id: str
    provider_name: str
    endpoint_category: str
    linked_boundary_request_id: str
    linked_dry_run_plan_id: str
    linked_normalization_input_id: str
    boundary_available: bool
    dry_run_plan_available: bool
    normalizer_contract_available: bool
    adapter_enabled: bool
    live_fetch_enabled: bool
    network_call_allowed: bool
    network_call_attempted: bool
    raw_response_storage_allowed: bool
    raw_response_stored: bool
    emits_live_adapter_record: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_disabled_skeleton_only(self) -> bool:
        return (
            self.boundary_available
            and self.dry_run_plan_available
            and self.normalizer_contract_available
            and not self.adapter_enabled
            and not self.live_fetch_enabled
            and not self.network_call_allowed
            and not self.network_call_attempted
            and not self.raw_response_storage_allowed
            and not self.raw_response_stored
            and not self.emits_live_adapter_record
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "skeleton_id": self.skeleton_id,
            "candidate_id": self.candidate_id,
            "provider_name": self.provider_name,
            "endpoint_category": self.endpoint_category,
            "linked_boundary_request_id": self.linked_boundary_request_id,
            "linked_dry_run_plan_id": self.linked_dry_run_plan_id,
            "linked_normalization_input_id": self.linked_normalization_input_id,
            "boundary_available": self.boundary_available,
            "dry_run_plan_available": self.dry_run_plan_available,
            "normalizer_contract_available": self.normalizer_contract_available,
            "adapter_enabled": self.adapter_enabled,
            "live_fetch_enabled": self.live_fetch_enabled,
            "network_call_allowed": self.network_call_allowed,
            "network_call_attempted": self.network_call_attempted,
            "raw_response_storage_allowed": self.raw_response_storage_allowed,
            "raw_response_stored": self.raw_response_stored,
            "emits_live_adapter_record": self.emits_live_adapter_record,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_disabled_skeleton_only": self.safe_disabled_skeleton_only(),
        }


@dataclass(frozen=True)
class DisabledLivePublicMarketFetchAdapterSkeletonResult:
    status: str
    skeleton_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    skeleton_count: int
    selected_candidate_skeleton_count: int
    enabled_adapter_count: int
    live_fetch_enabled_count: int
    network_call_allowed_count: int
    network_call_attempt_count: int
    raw_response_storage_allowed_count: int
    raw_response_storage_count: int
    live_adapter_record_emit_count: int
    compatible_with_v7_3_fetch_boundary: bool
    compatible_with_v7_4_dry_run_planner: bool
    compatible_with_v7_5_response_normalizer: bool
    adapter_skeletons: tuple[DisabledLivePublicMarketFetchAdapterSkeleton, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    disabled_adapter_skeleton_ready: bool
    skeleton_only: bool
    adapter_disabled_by_default: bool
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
            "skeleton_status": self.skeleton_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "skeleton_count": self.skeleton_count,
            "selected_candidate_skeleton_count": self.selected_candidate_skeleton_count,
            "enabled_adapter_count": self.enabled_adapter_count,
            "live_fetch_enabled_count": self.live_fetch_enabled_count,
            "network_call_allowed_count": self.network_call_allowed_count,
            "network_call_attempt_count": self.network_call_attempt_count,
            "raw_response_storage_allowed_count": self.raw_response_storage_allowed_count,
            "raw_response_storage_count": self.raw_response_storage_count,
            "live_adapter_record_emit_count": self.live_adapter_record_emit_count,
            "compatible_with_v7_3_fetch_boundary": self.compatible_with_v7_3_fetch_boundary,
            "compatible_with_v7_4_dry_run_planner": self.compatible_with_v7_4_dry_run_planner,
            "compatible_with_v7_5_response_normalizer": self.compatible_with_v7_5_response_normalizer,
            "adapter_skeletons": [skeleton.to_dict() for skeleton in self.adapter_skeletons],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "disabled_adapter_skeleton_ready": self.disabled_adapter_skeleton_ready,
            "skeleton_only": self.skeleton_only,
            "adapter_disabled_by_default": self.adapter_disabled_by_default,
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


def build_disabled_adapter_skeletons() -> tuple[
    DisabledLivePublicMarketFetchAdapterSkeleton, ...
]:
    boundary_result = audit_v7_3_live_public_market_intelligence_fetcher_boundary()
    dry_run_result = audit_v7_4_live_public_market_intelligence_dry_run_planner()
    normalizer_result = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()

    boundary_by_request_id = {
        request.request_id: request for request in boundary_result.fetch_boundary_requests
    }
    plan_by_request_id = {
        plan.source_request_id: plan for plan in dry_run_result.dry_run_fetch_plans
    }
    normalizer_by_plan_id = {
        item.source_plan_id: item for item in normalizer_result.normalization_inputs
    }

    skeletons: list[DisabledLivePublicMarketFetchAdapterSkeleton] = []

    for request_id, boundary_request in boundary_by_request_id.items():
        plan = plan_by_request_id.get(request_id)
        normalizer_input = normalizer_by_plan_id.get(plan.plan_id) if plan is not None else None

        skeletons.append(
            DisabledLivePublicMarketFetchAdapterSkeleton(
                skeleton_id=f"disabled_live_fetch_skeleton_{request_id}",
                candidate_id=boundary_request.candidate_id,
                provider_name=boundary_request.provider_name,
                endpoint_category=boundary_request.endpoint_category,
                linked_boundary_request_id=request_id,
                linked_dry_run_plan_id=plan.plan_id if plan is not None else "",
                linked_normalization_input_id=(
                    normalizer_input.normalization_input_id
                    if normalizer_input is not None
                    else ""
                ),
                boundary_available=True,
                dry_run_plan_available=plan is not None,
                normalizer_contract_available=normalizer_input is not None,
                adapter_enabled=False,
                live_fetch_enabled=False,
                network_call_allowed=False,
                network_call_attempted=False,
                raw_response_storage_allowed=False,
                raw_response_stored=False,
                emits_live_adapter_record=False,
                creates_buy_request=False,
                connects_broker=False,
                places_order=False,
                executes_trade=False,
            )
        )

    return tuple(skeletons)


def audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton(
    adapter_skeletons: tuple[DisabledLivePublicMarketFetchAdapterSkeleton, ...] | None | object = None,
) -> DisabledLivePublicMarketFetchAdapterSkeletonResult:
    boundary_result = audit_v7_3_live_public_market_intelligence_fetcher_boundary()
    dry_run_result = audit_v7_4_live_public_market_intelligence_dry_run_planner()
    normalizer_result = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()

    if adapter_skeletons is None:
        effective_skeletons = build_disabled_adapter_skeletons()
        invalid_override = False
    elif isinstance(adapter_skeletons, tuple):
        effective_skeletons = adapter_skeletons
        invalid_override = False
    else:
        effective_skeletons = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v7.6 wires the live public market fetch adapter skeleton but keeps it disabled.",
        "No live public network call is attempted in v7.6.",
        "No raw public response payload is stored in v7.6.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Adapter skeleton override must be a tuple of DisabledLivePublicMarketFetchAdapterSkeleton.")

    if boundary_result.status != V7_3_STATUS_READY or boundary_result.blockers:
        blockers.append("Source v7.3 live public market intelligence fetcher boundary is blocked.")
    if dry_run_result.status != V7_4_STATUS_READY or dry_run_result.blockers:
        blockers.append("Source v7.4 live public market intelligence dry-run planner is blocked.")
    if normalizer_result.status != V7_5_STATUS_READY or normalizer_result.blockers:
        blockers.append("Source v7.5 response normalizer contract is blocked.")

    if not effective_skeletons:
        blockers.append("No disabled live public market fetch adapter skeletons were produced.")

    skeleton_ids: list[str] = []
    boundary_ids = {request.request_id for request in boundary_result.fetch_boundary_requests}
    dry_run_plan_ids = {plan.plan_id for plan in dry_run_result.dry_run_fetch_plans}
    normalizer_input_ids = {
        item.normalization_input_id for item in normalizer_result.normalization_inputs
    }
    clean_skeletons: list[DisabledLivePublicMarketFetchAdapterSkeleton] = []

    for index, skeleton in enumerate(effective_skeletons):
        if not isinstance(skeleton, DisabledLivePublicMarketFetchAdapterSkeleton):
            blockers.append(
                f"Adapter skeleton at index {index} must be a DisabledLivePublicMarketFetchAdapterSkeleton."
            )
            continue

        clean_skeletons.append(skeleton)
        skeleton_ids.append(skeleton.skeleton_id)

        if not skeleton.skeleton_id.strip():
            blockers.append("Adapter skeleton ID is required.")
        if not skeleton.candidate_id.strip():
            blockers.append(f"{skeleton.skeleton_id}: candidate ID is required.")
        if not skeleton.provider_name.strip():
            blockers.append(f"{skeleton.skeleton_id}: provider name is required.")
        if not skeleton.endpoint_category.strip():
            blockers.append(f"{skeleton.skeleton_id}: endpoint category is required.")
        if skeleton.linked_boundary_request_id not in boundary_ids:
            blockers.append(f"{skeleton.skeleton_id}: linked boundary request ID is invalid.")
        if skeleton.linked_dry_run_plan_id not in dry_run_plan_ids:
            blockers.append(f"{skeleton.skeleton_id}: linked dry-run plan ID is invalid.")
        if skeleton.linked_normalization_input_id not in normalizer_input_ids:
            blockers.append(f"{skeleton.skeleton_id}: linked normalization input ID is invalid.")
        if not skeleton.boundary_available:
            blockers.append(f"{skeleton.skeleton_id}: boundary must be available.")
        if not skeleton.dry_run_plan_available:
            blockers.append(f"{skeleton.skeleton_id}: dry-run plan must be available.")
        if not skeleton.normalizer_contract_available:
            blockers.append(f"{skeleton.skeleton_id}: normalizer contract must be available.")
        if skeleton.adapter_enabled:
            blockers.append(f"{skeleton.skeleton_id}: adapter must remain disabled in v7.6.")
        if skeleton.live_fetch_enabled:
            blockers.append(f"{skeleton.skeleton_id}: live fetching is forbidden in v7.6.")
        if skeleton.network_call_allowed:
            blockers.append(f"{skeleton.skeleton_id}: network calls are forbidden in v7.6.")
        if skeleton.network_call_attempted:
            blockers.append(f"{skeleton.skeleton_id}: network call attempt is forbidden in v7.6.")
        if skeleton.raw_response_storage_allowed:
            blockers.append(f"{skeleton.skeleton_id}: raw response storage is forbidden in v7.6.")
        if skeleton.raw_response_stored:
            blockers.append(f"{skeleton.skeleton_id}: raw response storage attempt is forbidden in v7.6.")
        if skeleton.emits_live_adapter_record:
            blockers.append(f"{skeleton.skeleton_id}: live adapter record emission is forbidden in v7.6.")
        if not skeleton.safe_disabled_skeleton_only():
            blockers.append(f"{skeleton.skeleton_id}: skeleton must remain disabled and non-executable.")
        if skeleton.creates_buy_request:
            blockers.append(f"{skeleton.skeleton_id}: buy request creation is forbidden.")
        if skeleton.connects_broker:
            blockers.append(f"{skeleton.skeleton_id}: broker connection is forbidden.")
        if skeleton.places_order:
            blockers.append(f"{skeleton.skeleton_id}: order placement is forbidden.")
        if skeleton.executes_trade:
            blockers.append(f"{skeleton.skeleton_id}: trade execution is forbidden.")

    if len(skeleton_ids) != len(set(skeleton_ids)):
        blockers.append("Disabled live public market fetch adapter skeleton IDs must be unique.")

    clean_skeleton_tuple = tuple(clean_skeletons)

    selected_candidate_skeleton_count = sum(
        1
        for skeleton in clean_skeleton_tuple
        if skeleton.candidate_id == normalizer_result.selected_candidate_id
    )
    if selected_candidate_skeleton_count <= 0:
        blockers.append("At least one disabled adapter skeleton must cover the selected candidate.")

    enabled_adapter_count = sum(1 for skeleton in clean_skeleton_tuple if skeleton.adapter_enabled)
    live_fetch_enabled_count = sum(1 for skeleton in clean_skeleton_tuple if skeleton.live_fetch_enabled)
    network_call_allowed_count = sum(1 for skeleton in clean_skeleton_tuple if skeleton.network_call_allowed)
    network_call_attempt_count = sum(1 for skeleton in clean_skeleton_tuple if skeleton.network_call_attempted)
    raw_response_storage_allowed_count = sum(
        1 for skeleton in clean_skeleton_tuple if skeleton.raw_response_storage_allowed
    )
    raw_response_storage_count = sum(1 for skeleton in clean_skeleton_tuple if skeleton.raw_response_stored)
    live_adapter_record_emit_count = sum(
        1 for skeleton in clean_skeleton_tuple if skeleton.emits_live_adapter_record
    )

    safety_flags = {
        "disabled_adapter_skeleton_ready": False,
        "skeleton_only": True,
        "adapter_disabled_by_default": enabled_adapter_count == 0,
        "live_fetch_deferred": live_fetch_enabled_count == 0,
        "network_calls_deferred": network_call_allowed_count == 0 and network_call_attempt_count == 0,
        "raw_response_storage_deferred": (
            raw_response_storage_allowed_count == 0 and raw_response_storage_count == 0
        ),
        "live_adapter_record_emission_deferred": live_adapter_record_emit_count == 0,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["skeleton_only"]:
        blockers.append("v7.6 must remain skeleton-only.")
    if not safety_flags["adapter_disabled_by_default"]:
        blockers.append("v7.6 must keep the adapter disabled by default.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v7.6 must defer live fetching.")
    if not safety_flags["network_calls_deferred"]:
        blockers.append("v7.6 must defer network calls.")
    if not safety_flags["raw_response_storage_deferred"]:
        blockers.append("v7.6 must defer raw response storage.")
    if not safety_flags["live_adapter_record_emission_deferred"]:
        blockers.append("v7.6 must defer live adapter record emission.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v7.6 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v7.6 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v7.6 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v7.6 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return DisabledLivePublicMarketFetchAdapterSkeletonResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        skeleton_status=SKELETON_STATUS_READY if ready else SKELETON_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=normalizer_result.selected_candidate_id,
        selected_sleeve_id=normalizer_result.selected_sleeve_id,
        skeleton_count=len(clean_skeleton_tuple),
        selected_candidate_skeleton_count=selected_candidate_skeleton_count,
        enabled_adapter_count=enabled_adapter_count,
        live_fetch_enabled_count=live_fetch_enabled_count,
        network_call_allowed_count=network_call_allowed_count,
        network_call_attempt_count=network_call_attempt_count,
        raw_response_storage_allowed_count=raw_response_storage_allowed_count,
        raw_response_storage_count=raw_response_storage_count,
        live_adapter_record_emit_count=live_adapter_record_emit_count,
        compatible_with_v7_3_fetch_boundary=boundary_result.status == V7_3_STATUS_READY,
        compatible_with_v7_4_dry_run_planner=dry_run_result.status == V7_4_STATUS_READY,
        compatible_with_v7_5_response_normalizer=normalizer_result.status == V7_5_STATUS_READY,
        adapter_skeletons=clean_skeleton_tuple,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "disabled_adapter_skeleton_ready": ready},
    )
