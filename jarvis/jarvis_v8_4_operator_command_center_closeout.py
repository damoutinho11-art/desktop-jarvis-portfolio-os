"""J.A.R.V.I.S. v8.4 operator command center closeout.

Closes out the v8 product layer:
- public market intelligence dashboard visibility;
- autonomous research cycle status panel;
- weekly recommendation evidence pack integration;
- portfolio action brief generation.

This is a closeout audit, not a new safety-only layer.

Safety boundary:
- closeout visibility only
- no live public fetch
- no network calls
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

from .jarvis_v8_0_public_market_intelligence_operator_dashboard import (
    STATUS_READY as V8_0_STATUS_READY,
    audit_v8_0_public_market_intelligence_operator_dashboard,
)
from .jarvis_v8_1_autonomous_research_cycle_status_panel import (
    STATUS_READY as V8_1_STATUS_READY,
    audit_v8_1_autonomous_research_cycle_status_panel,
)
from .jarvis_v8_2_weekly_recommendation_evidence_pack_integration import (
    STATUS_READY as V8_2_STATUS_READY,
    audit_v8_2_weekly_recommendation_evidence_pack_integration,
)
from .jarvis_v8_3_portfolio_action_brief_generator import (
    STATUS_READY as V8_3_STATUS_READY,
    audit_v8_3_portfolio_action_brief_generator,
)


STATUS_READY = "JARVIS_V8_4_OPERATOR_COMMAND_CENTER_CLOSEOUT_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V8_4_OPERATOR_COMMAND_CENTER_CLOSEOUT_BLOCKED_SAFE"

CLOSEOUT_STATUS_READY = "OPERATOR_COMMAND_CENTER_PRODUCT_LAYER_CLOSED_OUT"
CLOSEOUT_STATUS_BLOCKED = "OPERATOR_COMMAND_CENTER_PRODUCT_LAYER_BLOCKED"

NEXT_STAGE = "v9_0_public_market_data_source_selection_plan"


@dataclass(frozen=True)
class OperatorCommandCenterCapability:
    capability_id: str
    stage: str
    title: str
    product_value: str
    evidence: str
    ready: bool
    user_visible: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool
    live_fetch_enabled: bool
    network_call_enabled: bool
    raw_response_storage_enabled: bool
    live_adapter_record_emission_enabled: bool

    def safe_capability_only(self) -> bool:
        return (
            self.ready
            and self.user_visible
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
            and not self.live_fetch_enabled
            and not self.network_call_enabled
            and not self.raw_response_storage_enabled
            and not self.live_adapter_record_emission_enabled
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "stage": self.stage,
            "title": self.title,
            "product_value": self.product_value,
            "evidence": self.evidence,
            "ready": self.ready,
            "user_visible": self.user_visible,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "live_fetch_enabled": self.live_fetch_enabled,
            "network_call_enabled": self.network_call_enabled,
            "raw_response_storage_enabled": self.raw_response_storage_enabled,
            "live_adapter_record_emission_enabled": self.live_adapter_record_emission_enabled,
            "safe_capability_only": self.safe_capability_only(),
        }


@dataclass(frozen=True)
class OperatorCommandCenterCloseoutResult:
    status: str
    closeout_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    capability_count: int
    ready_capability_count: int
    user_visible_capability_count: int
    unsafe_capability_count: int
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    capabilities: tuple[OperatorCommandCenterCapability, ...]
    v8_0_ready: bool
    v8_1_ready: bool
    v8_2_ready: bool
    v8_3_ready: bool
    v8_product_layer_complete: bool
    dashboard_visibility_complete: bool
    research_cycle_visibility_complete: bool
    evidence_pack_integration_complete: bool
    action_brief_generation_complete: bool
    product_value_not_redundant: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool
    live_fetch_deferred: bool
    network_calls_deferred: bool
    raw_response_storage_deferred: bool
    live_adapter_record_emission_deferred: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "closeout_status": self.closeout_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "capability_count": self.capability_count,
            "ready_capability_count": self.ready_capability_count,
            "user_visible_capability_count": self.user_visible_capability_count,
            "unsafe_capability_count": self.unsafe_capability_count,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "capabilities": [capability.to_dict() for capability in self.capabilities],
            "v8_0_ready": self.v8_0_ready,
            "v8_1_ready": self.v8_1_ready,
            "v8_2_ready": self.v8_2_ready,
            "v8_3_ready": self.v8_3_ready,
            "v8_product_layer_complete": self.v8_product_layer_complete,
            "dashboard_visibility_complete": self.dashboard_visibility_complete,
            "research_cycle_visibility_complete": self.research_cycle_visibility_complete,
            "evidence_pack_integration_complete": self.evidence_pack_integration_complete,
            "action_brief_generation_complete": self.action_brief_generation_complete,
            "product_value_not_redundant": self.product_value_not_redundant,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "live_fetch_deferred": self.live_fetch_deferred,
            "network_calls_deferred": self.network_calls_deferred,
            "raw_response_storage_deferred": self.raw_response_storage_deferred,
            "live_adapter_record_emission_deferred": self.live_adapter_record_emission_deferred,
        }


def _capability(
    capability_id: str,
    stage: str,
    title: str,
    product_value: str,
    evidence: str,
    ready: bool,
) -> OperatorCommandCenterCapability:
    return OperatorCommandCenterCapability(
        capability_id=capability_id,
        stage=stage,
        title=title,
        product_value=product_value,
        evidence=evidence,
        ready=ready,
        user_visible=True,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
        live_fetch_enabled=False,
        network_call_enabled=False,
        raw_response_storage_enabled=False,
        live_adapter_record_emission_enabled=False,
    )


def build_operator_command_center_capabilities() -> tuple[OperatorCommandCenterCapability, ...]:
    dashboard = audit_v8_0_public_market_intelligence_operator_dashboard()
    panel = audit_v8_1_autonomous_research_cycle_status_panel()
    pack = audit_v8_2_weekly_recommendation_evidence_pack_integration()
    brief = audit_v8_3_portfolio_action_brief_generator()

    return (
        _capability(
            "public_market_intelligence_operator_dashboard",
            "v8.0",
            "Public market intelligence operator dashboard",
            "Shows v7 public-market-intelligence readiness in an operator-facing dashboard.",
            f"dashboard_status={dashboard.dashboard_status}; card_count={dashboard.card_count}",
            dashboard.status == V8_0_STATUS_READY and not dashboard.blockers,
        ),
        _capability(
            "autonomous_research_cycle_status_panel",
            "v8.1",
            "Autonomous research cycle status panel",
            "Shows what J.A.R.V.I.S. reviewed, what is ready, and what is watch-only.",
            f"panel_status={panel.panel_status}; item_count={panel.item_count}; watch_item_count={panel.watch_item_count}",
            panel.status == V8_1_STATUS_READY and not panel.blockers,
        ),
        _capability(
            "weekly_recommendation_evidence_pack_integration",
            "v8.2",
            "Weekly recommendation evidence pack integration",
            "Connects research-cycle status to the weekly recommendation evidence pack.",
            f"pack_status={pack.pack_status}; section_count={pack.section_count}; watch_section_count={pack.watch_section_count}",
            pack.status == V8_2_STATUS_READY and not pack.blockers,
        ),
        _capability(
            "portfolio_action_brief_generator",
            "v8.3",
            "Portfolio action brief generator",
            "Turns the evidence pack into a concise preparatory operator action brief.",
            f"brief_status={brief.brief_status}; evidence_section_count={brief.evidence_section_count}; blocked_evidence_section_count={brief.blocked_evidence_section_count}",
            brief.status == V8_3_STATUS_READY and not brief.blockers,
        ),
        _capability(
            "execution_boundary_preservation",
            "v8.0-v8.3",
            "Execution boundary preservation",
            "Confirms the product layer remains non-executable and final real-world buying stays manual.",
            (
                f"buy_request_deferred={brief.buy_request_deferred}; "
                f"broker_connection_forbidden={brief.broker_connection_forbidden}; "
                f"order_placement_forbidden={brief.order_placement_forbidden}; "
                f"no_trades_executed={brief.no_trades_executed}"
            ),
            (
                dashboard.no_trades_executed
                and panel.no_trades_executed
                and pack.no_trades_executed
                and brief.no_trades_executed
                and brief.buy_request_deferred
                and brief.broker_connection_forbidden
                and brief.order_placement_forbidden
            ),
        ),
    )


def audit_v8_4_operator_command_center_closeout(
    capabilities: tuple[OperatorCommandCenterCapability, ...] | None | object = None,
) -> OperatorCommandCenterCloseoutResult:
    dashboard = audit_v8_0_public_market_intelligence_operator_dashboard()
    panel = audit_v8_1_autonomous_research_cycle_status_panel()
    pack = audit_v8_2_weekly_recommendation_evidence_pack_integration()
    brief = audit_v8_3_portfolio_action_brief_generator()

    if capabilities is None:
        effective_capabilities = build_operator_command_center_capabilities()
        invalid_override = False
    elif isinstance(capabilities, tuple):
        effective_capabilities = capabilities
        invalid_override = False
    else:
        effective_capabilities = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v8.4 closes the v8 product layer.",
        "Full suite validation is recommended for this closeout stage.",
        "Next stage should not add more v8 safety-only audits unless a real product gap appears.",
        "No buy request, broker connection, order placement, or trade is created.",
        "Live public fetching remains deferred.",
    ]

    if invalid_override:
        blockers.append("Capability override must be a tuple of OperatorCommandCenterCapability.")

    source_checks = {
        "v8.0 operator dashboard": dashboard.status == V8_0_STATUS_READY and not dashboard.blockers,
        "v8.1 research cycle panel": panel.status == V8_1_STATUS_READY and not panel.blockers,
        "v8.2 evidence pack integration": pack.status == V8_2_STATUS_READY and not pack.blockers,
        "v8.3 action brief generator": brief.status == V8_3_STATUS_READY and not brief.blockers,
    }
    for source_name, source_ready in source_checks.items():
        if not source_ready:
            blockers.append(f"Source stage is blocked: {source_name}.")

    if not effective_capabilities:
        blockers.append("No operator command center capabilities were produced.")

    clean_capabilities: list[OperatorCommandCenterCapability] = []
    capability_ids: list[str] = []

    for index, capability in enumerate(effective_capabilities):
        if not isinstance(capability, OperatorCommandCenterCapability):
            blockers.append(f"Capability at index {index} must be an OperatorCommandCenterCapability.")
            continue

        clean_capabilities.append(capability)
        capability_ids.append(capability.capability_id)

        if not capability.capability_id.strip():
            blockers.append("Capability ID is required.")
        if not capability.stage.strip():
            blockers.append(f"{capability.capability_id}: stage is required.")
        if not capability.title.strip():
            blockers.append(f"{capability.capability_id}: title is required.")
        if not capability.product_value.strip():
            blockers.append(f"{capability.capability_id}: product value is required.")
        if not capability.evidence.strip():
            blockers.append(f"{capability.capability_id}: evidence is required.")
        if not capability.ready:
            blockers.append(f"{capability.capability_id}: capability is not ready.")
        if not capability.user_visible:
            blockers.append(f"{capability.capability_id}: capability must be user-visible.")
        if not capability.safe_capability_only():
            blockers.append(f"{capability.capability_id}: capability must remain safe, visible, and non-executable.")
        if capability.creates_buy_request:
            blockers.append(f"{capability.capability_id}: buy request creation is forbidden.")
        if capability.connects_broker:
            blockers.append(f"{capability.capability_id}: broker connection is forbidden.")
        if capability.places_order:
            blockers.append(f"{capability.capability_id}: order placement is forbidden.")
        if capability.executes_trade:
            blockers.append(f"{capability.capability_id}: trade execution is forbidden.")
        if capability.live_fetch_enabled:
            blockers.append(f"{capability.capability_id}: live fetching is forbidden.")
        if capability.network_call_enabled:
            blockers.append(f"{capability.capability_id}: network calls are forbidden.")
        if capability.raw_response_storage_enabled:
            blockers.append(f"{capability.capability_id}: raw response storage is forbidden.")
        if capability.live_adapter_record_emission_enabled:
            blockers.append(f"{capability.capability_id}: live adapter record emission is forbidden.")

    if len(capability_ids) != len(set(capability_ids)):
        blockers.append("Operator command center capability IDs must be unique.")

    required_capability_ids = {
        "public_market_intelligence_operator_dashboard",
        "autonomous_research_cycle_status_panel",
        "weekly_recommendation_evidence_pack_integration",
        "portfolio_action_brief_generator",
        "execution_boundary_preservation",
    }
    missing_ids = sorted(required_capability_ids - set(capability_ids))
    if missing_ids:
        blockers.append("Operator command center closeout must include all required capabilities.")

    clean_tuple = tuple(clean_capabilities)
    ready_capability_count = sum(1 for capability in clean_tuple if capability.ready)
    user_visible_capability_count = sum(1 for capability in clean_tuple if capability.user_visible)
    unsafe_capability_count = sum(1 for capability in clean_tuple if not capability.safe_capability_only())

    v8_0_ready = source_checks["v8.0 operator dashboard"]
    v8_1_ready = source_checks["v8.1 research cycle panel"]
    v8_2_ready = source_checks["v8.2 evidence pack integration"]
    v8_3_ready = source_checks["v8.3 action brief generator"]

    safety_flags = {
        "v8_product_layer_complete": False,
        "dashboard_visibility_complete": v8_0_ready,
        "research_cycle_visibility_complete": v8_1_ready,
        "evidence_pack_integration_complete": v8_2_ready,
        "action_brief_generation_complete": v8_3_ready,
        "product_value_not_redundant": True,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
        "live_fetch_deferred": True,
        "network_calls_deferred": True,
        "raw_response_storage_deferred": True,
        "live_adapter_record_emission_deferred": True,
    }

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return OperatorCommandCenterCloseoutResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        closeout_status=CLOSEOUT_STATUS_READY if ready else CLOSEOUT_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=brief.selected_candidate_id,
        selected_sleeve_id=brief.selected_sleeve_id,
        capability_count=len(clean_tuple),
        ready_capability_count=ready_capability_count,
        user_visible_capability_count=user_visible_capability_count,
        unsafe_capability_count=unsafe_capability_count,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        capabilities=clean_tuple,
        v8_0_ready=v8_0_ready,
        v8_1_ready=v8_1_ready,
        v8_2_ready=v8_2_ready,
        v8_3_ready=v8_3_ready,
        **{**safety_flags, "v8_product_layer_complete": ready},
    )
