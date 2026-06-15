"""J.A.R.V.I.S. v7.7 live public market intelligence enablement preflight.

This stage audits the disabled live public market fetch adapter skeleton and
defines the hard preflight requirements that must be true before live public
market fetching can ever be enabled.

It does not enable live fetching.

Safety boundary:
- enablement preflight only
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
    STATUS_READY as V7_6_STATUS_READY,
    audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton,
)


STATUS_READY = "JARVIS_V7_7_LIVE_PUBLIC_MARKET_INTELLIGENCE_ENABLEMENT_PREFLIGHT_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V7_7_LIVE_PUBLIC_MARKET_INTELLIGENCE_ENABLEMENT_PREFLIGHT_BLOCKED_SAFE"

NEXT_STAGE = "v7_8_public_provider_configuration_registry"

PREFLIGHT_STATUS_READY = "LIVE_PUBLIC_MARKET_INTELLIGENCE_ENABLEMENT_PREFLIGHT_READY"
PREFLIGHT_STATUS_BLOCKED = "LIVE_PUBLIC_MARKET_INTELLIGENCE_ENABLEMENT_PREFLIGHT_BLOCKED"

CHECK_PASS = "PASS"
CHECK_FAIL = "FAIL"


@dataclass(frozen=True)
class LivePublicMarketEnablementPreflightRequirement:
    requirement_id: str
    category: str
    title: str
    status: str
    evidence: str
    required_before_live_enablement: bool
    blocker_if_failed: str
    adapter_still_disabled: bool
    live_fetch_still_disabled: bool
    network_calls_still_disabled: bool
    raw_response_storage_still_disabled: bool
    live_adapter_record_emission_still_disabled: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def passed(self) -> bool:
        return self.status == CHECK_PASS

    def safe_preflight_only(self) -> bool:
        return (
            self.adapter_still_disabled
            and self.live_fetch_still_disabled
            and self.network_calls_still_disabled
            and self.raw_response_storage_still_disabled
            and self.live_adapter_record_emission_still_disabled
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "category": self.category,
            "title": self.title,
            "status": self.status,
            "evidence": self.evidence,
            "required_before_live_enablement": self.required_before_live_enablement,
            "blocker_if_failed": self.blocker_if_failed,
            "adapter_still_disabled": self.adapter_still_disabled,
            "live_fetch_still_disabled": self.live_fetch_still_disabled,
            "network_calls_still_disabled": self.network_calls_still_disabled,
            "raw_response_storage_still_disabled": self.raw_response_storage_still_disabled,
            "live_adapter_record_emission_still_disabled": self.live_adapter_record_emission_still_disabled,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "passed": self.passed(),
            "safe_preflight_only": self.safe_preflight_only(),
        }


@dataclass(frozen=True)
class LivePublicMarketEnablementPreflightResult:
    status: str
    preflight_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    requirement_count: int
    passed_requirement_count: int
    failed_requirement_count: int
    required_before_live_enablement_count: int
    live_fetch_enablement_allowed: bool
    compatible_with_v7_6_disabled_adapter_skeleton: bool
    requirements: tuple[LivePublicMarketEnablementPreflightRequirement, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    enablement_preflight_ready: bool
    preflight_only: bool
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
            "preflight_status": self.preflight_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "requirement_count": self.requirement_count,
            "passed_requirement_count": self.passed_requirement_count,
            "failed_requirement_count": self.failed_requirement_count,
            "required_before_live_enablement_count": self.required_before_live_enablement_count,
            "live_fetch_enablement_allowed": self.live_fetch_enablement_allowed,
            "compatible_with_v7_6_disabled_adapter_skeleton": self.compatible_with_v7_6_disabled_adapter_skeleton,
            "requirements": [requirement.to_dict() for requirement in self.requirements],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "enablement_preflight_ready": self.enablement_preflight_ready,
            "preflight_only": self.preflight_only,
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


def _requirement(
    requirement_id: str,
    category: str,
    title: str,
    condition: bool,
    evidence: str,
    blocker_if_failed: str,
) -> LivePublicMarketEnablementPreflightRequirement:
    return LivePublicMarketEnablementPreflightRequirement(
        requirement_id=requirement_id,
        category=category,
        title=title,
        status=CHECK_PASS if condition else CHECK_FAIL,
        evidence=evidence,
        required_before_live_enablement=True,
        blocker_if_failed=blocker_if_failed,
        adapter_still_disabled=True,
        live_fetch_still_disabled=True,
        network_calls_still_disabled=True,
        raw_response_storage_still_disabled=True,
        live_adapter_record_emission_still_disabled=True,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_live_public_market_enablement_preflight_requirements() -> tuple[
    LivePublicMarketEnablementPreflightRequirement, ...
]:
    skeleton_result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()

    return (
        _requirement(
            "disabled_adapter_skeleton_ready",
            "UPSTREAM_CHAIN",
            "Disabled adapter skeleton is ready",
            skeleton_result.status == V7_6_STATUS_READY
            and skeleton_result.disabled_adapter_skeleton_ready,
            f"skeleton_count={skeleton_result.skeleton_count}",
            "v7.6 disabled adapter skeleton must be ready before enablement preflight.",
        ),
        _requirement(
            "adapter_disabled_by_default",
            "ENABLEMENT_CONTROL",
            "Adapter remains disabled by default",
            skeleton_result.enabled_adapter_count == 0
            and skeleton_result.adapter_disabled_by_default,
            f"enabled_adapter_count={skeleton_result.enabled_adapter_count}",
            "Adapter must remain disabled by default.",
        ),
        _requirement(
            "selected_candidate_coverage",
            "CANDIDATE_COVERAGE",
            "Selected candidate has disabled adapter skeleton coverage",
            skeleton_result.selected_candidate_skeleton_count > 0,
            f"selected_candidate_id={skeleton_result.selected_candidate_id}; selected_candidate_skeleton_count={skeleton_result.selected_candidate_skeleton_count}",
            "Selected candidate must have at least one disabled adapter skeleton.",
        ),
        _requirement(
            "boundary_dry_run_normalizer_wired",
            "WIRING",
            "Boundary, dry-run planner, and normalizer are wired",
            skeleton_result.compatible_with_v7_3_fetch_boundary
            and skeleton_result.compatible_with_v7_4_dry_run_planner
            and skeleton_result.compatible_with_v7_5_response_normalizer,
            (
                f"v7_3={skeleton_result.compatible_with_v7_3_fetch_boundary}; "
                f"v7_4={skeleton_result.compatible_with_v7_4_dry_run_planner}; "
                f"v7_5={skeleton_result.compatible_with_v7_5_response_normalizer}"
            ),
            "Boundary, dry-run planner, and normalizer must all be compatible.",
        ),
        _requirement(
            "live_fetch_deferred",
            "LIVE_FETCH_CONTROL",
            "Live fetching remains deferred",
            skeleton_result.live_fetch_enabled_count == 0
            and skeleton_result.live_fetch_deferred,
            f"live_fetch_enabled_count={skeleton_result.live_fetch_enabled_count}",
            "Live fetching must remain deferred.",
        ),
        _requirement(
            "network_calls_deferred",
            "NETWORK_CONTROL",
            "Network calls remain deferred",
            skeleton_result.network_call_allowed_count == 0
            and skeleton_result.network_call_attempt_count == 0
            and skeleton_result.network_calls_deferred,
            (
                f"network_call_allowed_count={skeleton_result.network_call_allowed_count}; "
                f"network_call_attempt_count={skeleton_result.network_call_attempt_count}"
            ),
            "Network calls must remain deferred.",
        ),
        _requirement(
            "raw_response_storage_deferred",
            "DATA_RETENTION_CONTROL",
            "Raw response storage remains deferred",
            skeleton_result.raw_response_storage_allowed_count == 0
            and skeleton_result.raw_response_storage_count == 0
            and skeleton_result.raw_response_storage_deferred,
            (
                f"raw_response_storage_allowed_count={skeleton_result.raw_response_storage_allowed_count}; "
                f"raw_response_storage_count={skeleton_result.raw_response_storage_count}"
            ),
            "Raw public response storage must remain deferred.",
        ),
        _requirement(
            "live_adapter_record_emission_deferred",
            "DATA_EMISSION_CONTROL",
            "Live adapter record emission remains deferred",
            skeleton_result.live_adapter_record_emit_count == 0
            and skeleton_result.live_adapter_record_emission_deferred,
            f"live_adapter_record_emit_count={skeleton_result.live_adapter_record_emit_count}",
            "Live adapter record emission must remain deferred.",
        ),
        _requirement(
            "execution_boundary_preserved",
            "EXECUTION_SAFETY",
            "No execution path exists",
            skeleton_result.buy_request_deferred
            and skeleton_result.broker_connection_forbidden
            and skeleton_result.order_placement_forbidden
            and skeleton_result.no_trades_executed,
            "buy_request=False; broker=False; order=False; trade=False",
            "No buy request, broker connection, order placement, or trade execution may exist.",
        ),
        _requirement(
            "manual_final_buy_boundary_preserved",
            "USER_ACTION_BOUNDARY",
            "Final real-world buy remains the only manual execution step",
            skeleton_result.final_user_buy_action_required,
            "final_user_buy_action_required=True",
            "Final user buy action boundary must remain explicit.",
        ),
    )


def audit_v7_7_live_public_market_intelligence_enablement_preflight(
    requirements: tuple[LivePublicMarketEnablementPreflightRequirement, ...] | None | object = None,
) -> LivePublicMarketEnablementPreflightResult:
    skeleton_result = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()

    if requirements is None:
        effective_requirements = build_live_public_market_enablement_preflight_requirements()
        invalid_override = False
    elif isinstance(requirements, tuple):
        effective_requirements = requirements
        invalid_override = False
    else:
        effective_requirements = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v7.7 is an enablement preflight only; it does not enable live fetching.",
        "Passing v7.7 means the disabled adapter skeleton is safe and auditable, not that live fetching is on.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Preflight requirement override must be a tuple of LivePublicMarketEnablementPreflightRequirement.")

    if skeleton_result.status != V7_6_STATUS_READY or skeleton_result.blockers:
        blockers.append("Source v7.6 disabled live public market fetch adapter skeleton is blocked.")

    if not effective_requirements:
        blockers.append("No live public market enablement preflight requirements were produced.")

    requirement_ids: list[str] = []
    clean_requirements: list[LivePublicMarketEnablementPreflightRequirement] = []

    for index, requirement in enumerate(effective_requirements):
        if not isinstance(requirement, LivePublicMarketEnablementPreflightRequirement):
            blockers.append(
                f"Preflight requirement at index {index} must be a LivePublicMarketEnablementPreflightRequirement."
            )
            continue

        clean_requirements.append(requirement)
        requirement_ids.append(requirement.requirement_id)

        if not requirement.requirement_id.strip():
            blockers.append("Preflight requirement ID is required.")
        if not requirement.category.strip():
            blockers.append(f"{requirement.requirement_id}: category is required.")
        if not requirement.title.strip():
            blockers.append(f"{requirement.requirement_id}: title is required.")
        if requirement.status not in {CHECK_PASS, CHECK_FAIL}:
            blockers.append(f"{requirement.requirement_id}: status must be PASS or FAIL.")
        if not requirement.evidence.strip():
            blockers.append(f"{requirement.requirement_id}: evidence is required.")
        if not requirement.required_before_live_enablement:
            blockers.append(f"{requirement.requirement_id}: requirement must be marked required before live enablement.")
        if not requirement.passed():
            blockers.append(requirement.blocker_if_failed)
        if not requirement.safe_preflight_only():
            blockers.append(f"{requirement.requirement_id}: preflight requirement must remain non-executable.")
        if not requirement.adapter_still_disabled:
            blockers.append(f"{requirement.requirement_id}: adapter must still be disabled.")
        if not requirement.live_fetch_still_disabled:
            blockers.append(f"{requirement.requirement_id}: live fetch must still be disabled.")
        if not requirement.network_calls_still_disabled:
            blockers.append(f"{requirement.requirement_id}: network calls must still be disabled.")
        if not requirement.raw_response_storage_still_disabled:
            blockers.append(f"{requirement.requirement_id}: raw response storage must still be disabled.")
        if not requirement.live_adapter_record_emission_still_disabled:
            blockers.append(f"{requirement.requirement_id}: live adapter record emission must still be disabled.")
        if requirement.creates_buy_request:
            blockers.append(f"{requirement.requirement_id}: buy request creation is forbidden.")
        if requirement.connects_broker:
            blockers.append(f"{requirement.requirement_id}: broker connection is forbidden.")
        if requirement.places_order:
            blockers.append(f"{requirement.requirement_id}: order placement is forbidden.")
        if requirement.executes_trade:
            blockers.append(f"{requirement.requirement_id}: trade execution is forbidden.")

    if len(requirement_ids) != len(set(requirement_ids)):
        blockers.append("Live public market enablement preflight requirement IDs must be unique.")

    clean_requirement_tuple = tuple(clean_requirements)
    passed_count = sum(1 for requirement in clean_requirement_tuple if requirement.passed())
    failed_count = len(clean_requirement_tuple) - passed_count
    required_count = sum(
        1 for requirement in clean_requirement_tuple if requirement.required_before_live_enablement
    )

    live_fetch_enablement_allowed = False

    safety_flags = {
        "enablement_preflight_ready": False,
        "preflight_only": True,
        "adapter_disabled_by_default": True,
        "live_fetch_deferred": True,
        "network_calls_deferred": True,
        "raw_response_storage_deferred": True,
        "live_adapter_record_emission_deferred": True,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if live_fetch_enablement_allowed:
        blockers.append("v7.7 must not allow live fetch enablement.")
    if not safety_flags["preflight_only"]:
        blockers.append("v7.7 must remain preflight-only.")
    if not safety_flags["adapter_disabled_by_default"]:
        blockers.append("v7.7 must keep the adapter disabled by default.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v7.7 must defer live fetching.")
    if not safety_flags["network_calls_deferred"]:
        blockers.append("v7.7 must defer network calls.")
    if not safety_flags["raw_response_storage_deferred"]:
        blockers.append("v7.7 must defer raw response storage.")
    if not safety_flags["live_adapter_record_emission_deferred"]:
        blockers.append("v7.7 must defer live adapter record emission.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v7.7 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v7.7 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v7.7 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v7.7 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return LivePublicMarketEnablementPreflightResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        preflight_status=PREFLIGHT_STATUS_READY if ready else PREFLIGHT_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=skeleton_result.selected_candidate_id,
        selected_sleeve_id=skeleton_result.selected_sleeve_id,
        requirement_count=len(clean_requirement_tuple),
        passed_requirement_count=passed_count,
        failed_requirement_count=failed_count,
        required_before_live_enablement_count=required_count,
        live_fetch_enablement_allowed=live_fetch_enablement_allowed,
        compatible_with_v7_6_disabled_adapter_skeleton=skeleton_result.status == V7_6_STATUS_READY,
        requirements=clean_requirement_tuple,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "enablement_preflight_ready": ready},
    )
