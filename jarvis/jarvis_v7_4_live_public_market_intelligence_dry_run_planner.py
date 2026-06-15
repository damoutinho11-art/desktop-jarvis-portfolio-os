"""J.A.R.V.I.S. v7.4 live public market intelligence dry-run planner.

This stage converts v7.3 live-fetch boundary requests into explicit dry-run
fetch plans.

It does not perform live fetching.

Safety boundary:
- dry-run planning only
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
    LivePublicMarketFetchBoundaryRequest,
    STATUS_READY as V7_3_STATUS_READY,
    audit_v7_3_live_public_market_intelligence_fetcher_boundary,
)


STATUS_READY = "JARVIS_V7_4_LIVE_PUBLIC_MARKET_INTELLIGENCE_DRY_RUN_PLANNER_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V7_4_LIVE_PUBLIC_MARKET_INTELLIGENCE_DRY_RUN_PLANNER_BLOCKED_SAFE"

NEXT_STAGE = "v7_5_live_public_market_intelligence_response_normalizer_contract"

DRY_RUN_STATUS_READY = "LIVE_PUBLIC_MARKET_INTELLIGENCE_DRY_RUN_PLAN_READY"
DRY_RUN_STATUS_BLOCKED = "LIVE_PUBLIC_MARKET_INTELLIGENCE_DRY_RUN_PLAN_BLOCKED"


@dataclass(frozen=True)
class LivePublicMarketDryRunFetchPlan:
    plan_id: str
    source_request_id: str
    candidate_id: str
    provider_name: str
    provider_type: str
    endpoint_category: str
    planned_method: str
    planned_url: str
    planned_reason: str
    expected_adapter_record_type: str
    timeout_seconds: int
    max_records: int
    rate_limit_per_minute: int
    requires_api_key: bool
    dry_run_only: bool
    live_fetch_allowed: bool
    network_call_allowed: bool
    raw_response_storage_allowed: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_dry_run_plan_only(self) -> bool:
        return (
            self.dry_run_only
            and not self.live_fetch_allowed
            and not self.network_call_allowed
            and not self.raw_response_storage_allowed
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "source_request_id": self.source_request_id,
            "candidate_id": self.candidate_id,
            "provider_name": self.provider_name,
            "provider_type": self.provider_type,
            "endpoint_category": self.endpoint_category,
            "planned_method": self.planned_method,
            "planned_url": self.planned_url,
            "planned_reason": self.planned_reason,
            "expected_adapter_record_type": self.expected_adapter_record_type,
            "timeout_seconds": self.timeout_seconds,
            "max_records": self.max_records,
            "rate_limit_per_minute": self.rate_limit_per_minute,
            "requires_api_key": self.requires_api_key,
            "dry_run_only": self.dry_run_only,
            "live_fetch_allowed": self.live_fetch_allowed,
            "network_call_allowed": self.network_call_allowed,
            "raw_response_storage_allowed": self.raw_response_storage_allowed,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_dry_run_plan_only": self.safe_dry_run_plan_only(),
        }


@dataclass(frozen=True)
class LivePublicMarketDryRunPlannerResult:
    status: str
    dry_run_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    dry_run_plan_count: int
    selected_candidate_plan_count: int
    planned_network_call_count: int
    planned_live_fetch_count: int
    raw_response_storage_plan_count: int
    compatible_with_v7_3_fetch_boundary: bool
    dry_run_fetch_plans: tuple[LivePublicMarketDryRunFetchPlan, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    dry_run_planner_ready: bool
    dry_run_only: bool
    live_fetch_deferred: bool
    network_calls_deferred: bool
    raw_response_storage_deferred: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "dry_run_status": self.dry_run_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "dry_run_plan_count": self.dry_run_plan_count,
            "selected_candidate_plan_count": self.selected_candidate_plan_count,
            "planned_network_call_count": self.planned_network_call_count,
            "planned_live_fetch_count": self.planned_live_fetch_count,
            "raw_response_storage_plan_count": self.raw_response_storage_plan_count,
            "compatible_with_v7_3_fetch_boundary": self.compatible_with_v7_3_fetch_boundary,
            "dry_run_fetch_plans": [plan.to_dict() for plan in self.dry_run_fetch_plans],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "dry_run_planner_ready": self.dry_run_planner_ready,
            "dry_run_only": self.dry_run_only,
            "live_fetch_deferred": self.live_fetch_deferred,
            "network_calls_deferred": self.network_calls_deferred,
            "raw_response_storage_deferred": self.raw_response_storage_deferred,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def build_dry_run_plan_from_boundary_request(
    request: LivePublicMarketFetchBoundaryRequest,
) -> LivePublicMarketDryRunFetchPlan:
    planned_url = request.url_template.replace("{candidate_id}", request.candidate_id)

    return LivePublicMarketDryRunFetchPlan(
        plan_id=f"dry_run_{request.request_id}",
        source_request_id=request.request_id,
        candidate_id=request.candidate_id,
        provider_name=request.provider_name,
        provider_type=request.provider_type,
        endpoint_category=request.endpoint_category,
        planned_method=request.method,
        planned_url=planned_url,
        planned_reason=(
            f"Dry-run plan for {request.request_purpose} "
            f"Expected adapter record type: {request.expected_adapter_record_type}."
        ),
        expected_adapter_record_type=request.expected_adapter_record_type,
        timeout_seconds=request.timeout_seconds,
        max_records=request.max_records,
        rate_limit_per_minute=request.rate_limit_per_minute,
        requires_api_key=request.requires_api_key,
        dry_run_only=True,
        live_fetch_allowed=False,
        network_call_allowed=False,
        raw_response_storage_allowed=False,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_dry_run_plans_from_boundary_requests(
    requests: tuple[LivePublicMarketFetchBoundaryRequest, ...],
) -> tuple[LivePublicMarketDryRunFetchPlan, ...]:
    return tuple(build_dry_run_plan_from_boundary_request(request) for request in requests)


def audit_v7_4_live_public_market_intelligence_dry_run_planner(
    dry_run_plans: tuple[LivePublicMarketDryRunFetchPlan, ...] | None | object = None,
) -> LivePublicMarketDryRunPlannerResult:
    boundary_result = audit_v7_3_live_public_market_intelligence_fetcher_boundary()

    if dry_run_plans is None:
        effective_plans = build_dry_run_plans_from_boundary_requests(
            boundary_result.fetch_boundary_requests
        )
        invalid_override = False
    elif isinstance(dry_run_plans, tuple):
        effective_plans = dry_run_plans
        invalid_override = False
    else:
        effective_plans = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v7.4 creates dry-run fetch plans only.",
        "No live public network call is attempted in v7.4.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Dry-run plan override must be a tuple of LivePublicMarketDryRunFetchPlan.")

    if boundary_result.status != V7_3_STATUS_READY or boundary_result.blockers:
        blockers.append("Source v7.3 live public market intelligence fetcher boundary is blocked.")

    if not effective_plans:
        blockers.append("No live public market dry-run fetch plans were produced.")

    plan_ids: list[str] = []
    source_request_ids: list[str] = []
    clean_plans: list[LivePublicMarketDryRunFetchPlan] = []

    for index, plan in enumerate(effective_plans):
        if not isinstance(plan, LivePublicMarketDryRunFetchPlan):
            blockers.append(f"Dry-run plan at index {index} must be a LivePublicMarketDryRunFetchPlan.")
            continue

        clean_plans.append(plan)
        plan_ids.append(plan.plan_id)
        source_request_ids.append(plan.source_request_id)

        if not plan.plan_id.strip():
            blockers.append("Dry-run plan ID is required.")
        if not plan.source_request_id.strip():
            blockers.append(f"{plan.plan_id}: source request ID is required.")
        if not plan.candidate_id.strip():
            blockers.append(f"{plan.plan_id}: candidate ID is required.")
        if not plan.provider_name.strip():
            blockers.append(f"{plan.plan_id}: provider name is required.")
        if not plan.provider_type.strip():
            blockers.append(f"{plan.plan_id}: provider type is required.")
        if not plan.endpoint_category.strip():
            blockers.append(f"{plan.plan_id}: endpoint category is required.")
        if plan.planned_method != "GET":
            blockers.append(f"{plan.plan_id}: only GET dry-run plans are allowed.")
        if not plan.planned_url.startswith("https://"):
            blockers.append(f"{plan.plan_id}: planned URL must be HTTPS.")
        if "example.invalid" not in plan.planned_url:
            blockers.append(f"{plan.plan_id}: v7.4 must use non-live placeholder URLs.")
        if "{candidate_id}" in plan.planned_url:
            blockers.append(f"{plan.plan_id}: planned URL must resolve candidate placeholder.")
        if not plan.planned_reason.strip():
            blockers.append(f"{plan.plan_id}: planned reason is required.")
        if not plan.expected_adapter_record_type.strip():
            blockers.append(f"{plan.plan_id}: expected adapter record type is required.")
        if plan.timeout_seconds <= 0 or plan.timeout_seconds > 30:
            blockers.append(f"{plan.plan_id}: timeout must be between 1 and 30 seconds.")
        if plan.max_records <= 0 or plan.max_records > 50:
            blockers.append(f"{plan.plan_id}: max records must be between 1 and 50.")
        if plan.rate_limit_per_minute <= 0 or plan.rate_limit_per_minute > 60:
            blockers.append(f"{plan.plan_id}: rate limit must be between 1 and 60 per minute.")
        if not plan.dry_run_only:
            blockers.append(f"{plan.plan_id}: dry-run-only flag is required.")
        if plan.live_fetch_allowed:
            blockers.append(f"{plan.plan_id}: live fetching is forbidden in v7.4.")
        if plan.network_call_allowed:
            blockers.append(f"{plan.plan_id}: network calls are forbidden in v7.4.")
        if plan.raw_response_storage_allowed:
            blockers.append(f"{plan.plan_id}: raw response storage is forbidden in v7.4.")
        if not plan.safe_dry_run_plan_only():
            blockers.append(f"{plan.plan_id}: plan must remain dry-run-only.")
        if plan.creates_buy_request:
            blockers.append(f"{plan.plan_id}: buy request creation is forbidden.")
        if plan.connects_broker:
            blockers.append(f"{plan.plan_id}: broker connection is forbidden.")
        if plan.places_order:
            blockers.append(f"{plan.plan_id}: order placement is forbidden.")
        if plan.executes_trade:
            blockers.append(f"{plan.plan_id}: trade execution is forbidden.")

    if len(plan_ids) != len(set(plan_ids)):
        blockers.append("Live public market dry-run plan IDs must be unique.")

    expected_source_request_ids = {
        request.request_id for request in boundary_result.fetch_boundary_requests
    }
    unexpected_source_ids = sorted(set(source_request_ids) - expected_source_request_ids)
    if unexpected_source_ids:
        blockers.append("Dry-run plans must reference v7.3 fetch boundary request IDs.")

    clean_plan_tuple = tuple(clean_plans)

    selected_candidate_plan_count = sum(
        1 for plan in clean_plan_tuple if plan.candidate_id == boundary_result.selected_candidate_id
    )
    if selected_candidate_plan_count <= 0:
        blockers.append("At least one dry-run plan must cover the selected candidate.")

    planned_network_call_count = sum(1 for plan in clean_plan_tuple if plan.network_call_allowed)
    planned_live_fetch_count = sum(1 for plan in clean_plan_tuple if plan.live_fetch_allowed)
    raw_response_storage_plan_count = sum(
        1 for plan in clean_plan_tuple if plan.raw_response_storage_allowed
    )

    safety_flags = {
        "dry_run_planner_ready": False,
        "dry_run_only": True,
        "live_fetch_deferred": planned_live_fetch_count == 0,
        "network_calls_deferred": planned_network_call_count == 0,
        "raw_response_storage_deferred": raw_response_storage_plan_count == 0,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["dry_run_only"]:
        blockers.append("v7.4 must remain dry-run-only.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v7.4 must defer live fetching.")
    if not safety_flags["network_calls_deferred"]:
        blockers.append("v7.4 must defer network calls.")
    if not safety_flags["raw_response_storage_deferred"]:
        blockers.append("v7.4 must defer raw response storage.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v7.4 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v7.4 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v7.4 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v7.4 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return LivePublicMarketDryRunPlannerResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        dry_run_status=DRY_RUN_STATUS_READY if ready else DRY_RUN_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=boundary_result.selected_candidate_id,
        selected_sleeve_id=boundary_result.selected_sleeve_id,
        dry_run_plan_count=len(clean_plan_tuple),
        selected_candidate_plan_count=selected_candidate_plan_count,
        planned_network_call_count=planned_network_call_count,
        planned_live_fetch_count=planned_live_fetch_count,
        raw_response_storage_plan_count=raw_response_storage_plan_count,
        compatible_with_v7_3_fetch_boundary=boundary_result.status == V7_3_STATUS_READY,
        dry_run_fetch_plans=clean_plan_tuple,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "dry_run_planner_ready": ready},
    )
