"""J.A.R.V.I.S. v8.1 autonomous research cycle status panel.

This stage exposes what J.A.R.V.I.S. autonomously reviewed and what is ready,
stale, blocked, or watchlisted for the next recommendation cycle.

It is a product-facing status panel, not another hidden safety audit.

Safety boundary:
- research-cycle visibility only
- no live public fetch
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

from .jarvis_v8_0_public_market_intelligence_operator_dashboard import (
    STATUS_READY as V8_0_STATUS_READY,
    audit_v8_0_public_market_intelligence_operator_dashboard,
)


STATUS_READY = "JARVIS_V8_1_AUTONOMOUS_RESEARCH_CYCLE_STATUS_PANEL_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V8_1_AUTONOMOUS_RESEARCH_CYCLE_STATUS_PANEL_BLOCKED_SAFE"

NEXT_STAGE = "v8_2_weekly_recommendation_evidence_pack_integration"

PANEL_STATUS_READY = "AUTONOMOUS_RESEARCH_CYCLE_STATUS_PANEL_READY"
PANEL_STATUS_BLOCKED = "AUTONOMOUS_RESEARCH_CYCLE_STATUS_PANEL_BLOCKED"

ITEM_STATE_READY = "READY"
ITEM_STATE_WATCH = "WATCH"
ITEM_STATE_STALE = "STALE"
ITEM_STATE_BLOCKED = "BLOCKED"
ITEM_STATE_INFO = "INFO"

FRESHNESS_FRESH = "FRESH"
FRESHNESS_STALE = "STALE"
FRESHNESS_NOT_LIVE = "NOT_LIVE"


@dataclass(frozen=True)
class AutonomousResearchCycleStatusItem:
    item_id: str
    title: str
    category: str
    state: str
    freshness: str
    priority: int
    reviewed_by_jarvis: bool
    ready_for_recommendation_pack: bool
    blocked_reason: str
    watch_focus: str
    evidence: str
    operator_summary: str
    user_visible: bool
    live_fetch_enabled: bool
    network_call_enabled: bool
    raw_response_storage_enabled: bool
    live_adapter_record_emission_enabled: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def blocked(self) -> bool:
        return self.state == ITEM_STATE_BLOCKED

    def stale(self) -> bool:
        return self.state == ITEM_STATE_STALE or self.freshness == FRESHNESS_STALE

    def safe_panel_item_only(self) -> bool:
        return (
            self.user_visible
            and self.reviewed_by_jarvis
            and not self.live_fetch_enabled
            and not self.network_call_enabled
            and not self.raw_response_storage_enabled
            and not self.live_adapter_record_emission_enabled
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "category": self.category,
            "state": self.state,
            "freshness": self.freshness,
            "priority": self.priority,
            "reviewed_by_jarvis": self.reviewed_by_jarvis,
            "ready_for_recommendation_pack": self.ready_for_recommendation_pack,
            "blocked_reason": self.blocked_reason,
            "watch_focus": self.watch_focus,
            "evidence": self.evidence,
            "operator_summary": self.operator_summary,
            "user_visible": self.user_visible,
            "live_fetch_enabled": self.live_fetch_enabled,
            "network_call_enabled": self.network_call_enabled,
            "raw_response_storage_enabled": self.raw_response_storage_enabled,
            "live_adapter_record_emission_enabled": self.live_adapter_record_emission_enabled,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "blocked": self.blocked(),
            "stale": self.stale(),
            "safe_panel_item_only": self.safe_panel_item_only(),
        }


@dataclass(frozen=True)
class AutonomousResearchCycleStatusPanelResult:
    status: str
    panel_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    item_count: int
    reviewed_item_count: int
    ready_item_count: int
    watch_item_count: int
    stale_item_count: int
    blocked_item_count: int
    recommendation_pack_ready_item_count: int
    user_visible_item_count: int
    live_fetch_enabled_item_count: int
    network_call_enabled_item_count: int
    raw_response_storage_enabled_item_count: int
    live_adapter_record_emission_enabled_item_count: int
    compatible_with_v8_0_operator_dashboard: bool
    items: tuple[AutonomousResearchCycleStatusItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    research_cycle_panel_ready: bool
    product_visibility_stage: bool
    public_intelligence_review_visible: bool
    candidate_coverage_visible: bool
    freshness_status_visible: bool
    recommendation_pack_readiness_visible: bool
    next_watch_focus_visible: bool
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
            "panel_status": self.panel_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "item_count": self.item_count,
            "reviewed_item_count": self.reviewed_item_count,
            "ready_item_count": self.ready_item_count,
            "watch_item_count": self.watch_item_count,
            "stale_item_count": self.stale_item_count,
            "blocked_item_count": self.blocked_item_count,
            "recommendation_pack_ready_item_count": self.recommendation_pack_ready_item_count,
            "user_visible_item_count": self.user_visible_item_count,
            "live_fetch_enabled_item_count": self.live_fetch_enabled_item_count,
            "network_call_enabled_item_count": self.network_call_enabled_item_count,
            "raw_response_storage_enabled_item_count": self.raw_response_storage_enabled_item_count,
            "live_adapter_record_emission_enabled_item_count": self.live_adapter_record_emission_enabled_item_count,
            "compatible_with_v8_0_operator_dashboard": self.compatible_with_v8_0_operator_dashboard,
            "items": [item.to_dict() for item in self.items],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "research_cycle_panel_ready": self.research_cycle_panel_ready,
            "product_visibility_stage": self.product_visibility_stage,
            "public_intelligence_review_visible": self.public_intelligence_review_visible,
            "candidate_coverage_visible": self.candidate_coverage_visible,
            "freshness_status_visible": self.freshness_status_visible,
            "recommendation_pack_readiness_visible": self.recommendation_pack_readiness_visible,
            "next_watch_focus_visible": self.next_watch_focus_visible,
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


def _item(
    item_id: str,
    title: str,
    category: str,
    state: str,
    freshness: str,
    priority: int,
    ready_for_recommendation_pack: bool,
    blocked_reason: str,
    watch_focus: str,
    evidence: str,
    operator_summary: str,
) -> AutonomousResearchCycleStatusItem:
    return AutonomousResearchCycleStatusItem(
        item_id=item_id,
        title=title,
        category=category,
        state=state,
        freshness=freshness,
        priority=priority,
        reviewed_by_jarvis=True,
        ready_for_recommendation_pack=ready_for_recommendation_pack,
        blocked_reason=blocked_reason,
        watch_focus=watch_focus,
        evidence=evidence,
        operator_summary=operator_summary,
        user_visible=True,
        live_fetch_enabled=False,
        network_call_enabled=False,
        raw_response_storage_enabled=False,
        live_adapter_record_emission_enabled=False,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_autonomous_research_cycle_status_items() -> tuple[
    AutonomousResearchCycleStatusItem, ...
]:
    dashboard = audit_v8_0_public_market_intelligence_operator_dashboard()

    return (
        _item(
            "public_intelligence_readiness_review",
            "Public intelligence readiness review",
            "PUBLIC_INTELLIGENCE",
            ITEM_STATE_READY,
            FRESHNESS_NOT_LIVE,
            10,
            True,
            "",
            "Keep public-intelligence readiness visible while live fetch remains disabled.",
            (
                f"v8_0_status={dashboard.status}; "
                f"card_count={dashboard.card_count}; "
                f"compatible_with_v7_10={dashboard.compatible_with_v7_10_readiness_closeout}"
            ),
            "J.A.R.V.I.S. reviewed the public-market-intelligence readiness chain and surfaced it in the operator dashboard.",
        ),
        _item(
            "selected_candidate_coverage_review",
            "Selected candidate coverage review",
            "CANDIDATE_COVERAGE",
            ITEM_STATE_READY,
            FRESHNESS_NOT_LIVE,
            20,
            True,
            "",
            "Carry selected-candidate coverage into the weekly recommendation evidence pack.",
            (
                f"selected_candidate_id={dashboard.selected_candidate_id}; "
                f"selected_sleeve_id={dashboard.selected_sleeve_id}; "
                f"selected_candidate_visible={dashboard.selected_candidate_visible}"
            ),
            "J.A.R.V.I.S. confirmed that the selected candidate has public-intelligence readiness coverage.",
        ),
        _item(
            "provider_and_binding_review",
            "Provider and binding review",
            "PROVIDER_BINDING",
            ITEM_STATE_READY,
            FRESHNESS_NOT_LIVE,
            30,
            True,
            "",
            "Use provider/binding readiness as context only; do not enable live fetch from this panel.",
            (
                f"provider_readiness_visible={dashboard.provider_readiness_visible}; "
                f"disabled_live_fetch_visible={dashboard.disabled_live_fetch_visible}"
            ),
            "J.A.R.V.I.S. reviewed provider registry and disabled adapter binding visibility.",
        ),
        _item(
            "live_data_freshness_review",
            "Live data freshness review",
            "FRESHNESS",
            ITEM_STATE_WATCH,
            FRESHNESS_NOT_LIVE,
            40,
            False,
            "Live public fetching is intentionally disabled, so live data freshness is not available yet.",
            "Watch for a future explicit public-live-fetch enablement stage; do not treat missing live data as a failure.",
            (
                f"live_fetch_deferred={dashboard.live_fetch_deferred}; "
                f"network_calls_deferred={dashboard.network_calls_deferred}; "
                f"raw_response_storage_deferred={dashboard.raw_response_storage_deferred}"
            ),
            "J.A.R.V.I.S. marked live-data freshness as watch-only because the system is not yet allowed to fetch live public data.",
        ),
        _item(
            "weekly_recommendation_pack_readiness",
            "Weekly recommendation pack readiness",
            "RECOMMENDATION_PACK",
            ITEM_STATE_READY,
            FRESHNESS_NOT_LIVE,
            50,
            True,
            "",
            "Next stage should connect these status items into the weekly recommendation evidence pack.",
            (
                f"operator_dashboard_ready={dashboard.operator_dashboard_ready}; "
                f"execution_safety_visible={dashboard.execution_safety_visible}"
            ),
            "J.A.R.V.I.S. has enough dashboard-visible readiness context to feed a recommendation evidence pack.",
        ),
        _item(
            "execution_boundary_review",
            "Execution boundary review",
            "EXECUTION_SAFETY",
            ITEM_STATE_READY,
            FRESHNESS_FRESH,
            60,
            True,
            "",
            "Keep final buy action outside J.A.R.V.I.S.; recommendations remain informational/preparatory.",
            (
                f"buy_request_deferred={dashboard.buy_request_deferred}; "
                f"broker_connection_forbidden={dashboard.broker_connection_forbidden}; "
                f"order_placement_forbidden={dashboard.order_placement_forbidden}; "
                f"no_trades_executed={dashboard.no_trades_executed}"
            ),
            "J.A.R.V.I.S. reviewed and preserved the no-execution boundary.",
        ),
    )


def audit_v8_1_autonomous_research_cycle_status_panel(
    items: tuple[AutonomousResearchCycleStatusItem, ...] | None | object = None,
) -> AutonomousResearchCycleStatusPanelResult:
    dashboard = audit_v8_0_public_market_intelligence_operator_dashboard()

    if items is None:
        effective_items = build_autonomous_research_cycle_status_items()
        invalid_override = False
    elif isinstance(items, tuple):
        effective_items = items
        invalid_override = False
    else:
        effective_items = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v8.1 is autonomous research-cycle visibility only.",
        "v8.1 shows what J.A.R.V.I.S. reviewed, what is ready, what is watch-only, and what should feed the evidence pack.",
        "Live data freshness is watch-only because live public fetching remains disabled.",
        "No live public network call is attempted in v8.1.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Status item override must be a tuple of AutonomousResearchCycleStatusItem.")

    if dashboard.status != V8_0_STATUS_READY or dashboard.blockers:
        blockers.append("Source v8.0 public market intelligence operator dashboard is blocked.")

    if not effective_items:
        blockers.append("No autonomous research cycle status items were produced.")

    item_ids: list[str] = []
    clean_items: list[AutonomousResearchCycleStatusItem] = []

    for index, item in enumerate(effective_items):
        if not isinstance(item, AutonomousResearchCycleStatusItem):
            blockers.append(f"Status item at index {index} must be an AutonomousResearchCycleStatusItem.")
            continue

        clean_items.append(item)
        item_ids.append(item.item_id)

        if not item.item_id.strip():
            blockers.append("Status item ID is required.")
        if not item.title.strip():
            blockers.append(f"{item.item_id}: title is required.")
        if not item.category.strip():
            blockers.append(f"{item.item_id}: category is required.")
        if item.state not in {ITEM_STATE_READY, ITEM_STATE_WATCH, ITEM_STATE_STALE, ITEM_STATE_BLOCKED, ITEM_STATE_INFO}:
            blockers.append(f"{item.item_id}: state is not allowed.")
        if item.freshness not in {FRESHNESS_FRESH, FRESHNESS_STALE, FRESHNESS_NOT_LIVE}:
            blockers.append(f"{item.item_id}: freshness is not allowed.")
        if item.priority <= 0:
            blockers.append(f"{item.item_id}: priority must be positive.")
        if not item.reviewed_by_jarvis:
            blockers.append(f"{item.item_id}: item must be reviewed by J.A.R.V.I.S.")
        if item.blocked() and not item.blocked_reason.strip():
            blockers.append(f"{item.item_id}: blocked items require a blocked reason.")
        if item.state == ITEM_STATE_WATCH and not item.watch_focus.strip():
            blockers.append(f"{item.item_id}: watch items require a watch focus.")
        if not item.evidence.strip():
            blockers.append(f"{item.item_id}: evidence is required.")
        if not item.operator_summary.strip():
            blockers.append(f"{item.item_id}: operator summary is required.")
        if not item.user_visible:
            blockers.append(f"{item.item_id}: item must be user-visible.")
        if item.live_fetch_enabled:
            blockers.append(f"{item.item_id}: live fetching is forbidden in v8.1.")
        if item.network_call_enabled:
            blockers.append(f"{item.item_id}: network calls are forbidden in v8.1.")
        if item.raw_response_storage_enabled:
            blockers.append(f"{item.item_id}: raw response storage is forbidden in v8.1.")
        if item.live_adapter_record_emission_enabled:
            blockers.append(f"{item.item_id}: live adapter record emission is forbidden in v8.1.")
        if not item.safe_panel_item_only():
            blockers.append(f"{item.item_id}: status item must remain visibility-only and non-executable.")
        if item.creates_buy_request:
            blockers.append(f"{item.item_id}: buy request creation is forbidden.")
        if item.connects_broker:
            blockers.append(f"{item.item_id}: broker connection is forbidden.")
        if item.places_order:
            blockers.append(f"{item.item_id}: order placement is forbidden.")
        if item.executes_trade:
            blockers.append(f"{item.item_id}: trade execution is forbidden.")

    if len(item_ids) != len(set(item_ids)):
        blockers.append("Autonomous research cycle status item IDs must be unique.")

    required_item_ids = {
        "public_intelligence_readiness_review",
        "selected_candidate_coverage_review",
        "provider_and_binding_review",
        "live_data_freshness_review",
        "weekly_recommendation_pack_readiness",
        "execution_boundary_review",
    }
    missing_item_ids = sorted(required_item_ids - set(item_ids))
    if missing_item_ids:
        blockers.append("Research cycle status panel must include all required visibility items.")

    clean_item_tuple = tuple(clean_items)

    reviewed_item_count = sum(1 for item in clean_item_tuple if item.reviewed_by_jarvis)
    ready_item_count = sum(1 for item in clean_item_tuple if item.state == ITEM_STATE_READY)
    watch_item_count = sum(1 for item in clean_item_tuple if item.state == ITEM_STATE_WATCH)
    stale_item_count = sum(1 for item in clean_item_tuple if item.stale())
    blocked_item_count = sum(1 for item in clean_item_tuple if item.blocked())
    recommendation_pack_ready_item_count = sum(
        1 for item in clean_item_tuple if item.ready_for_recommendation_pack
    )
    user_visible_item_count = sum(1 for item in clean_item_tuple if item.user_visible)
    live_fetch_enabled_item_count = sum(1 for item in clean_item_tuple if item.live_fetch_enabled)
    network_call_enabled_item_count = sum(1 for item in clean_item_tuple if item.network_call_enabled)
    raw_response_storage_enabled_item_count = sum(
        1 for item in clean_item_tuple if item.raw_response_storage_enabled
    )
    live_adapter_record_emission_enabled_item_count = sum(
        1 for item in clean_item_tuple if item.live_adapter_record_emission_enabled
    )

    categories = {item.category for item in clean_item_tuple}

    safety_flags = {
        "research_cycle_panel_ready": False,
        "product_visibility_stage": True,
        "public_intelligence_review_visible": "PUBLIC_INTELLIGENCE" in categories,
        "candidate_coverage_visible": "CANDIDATE_COVERAGE" in categories,
        "freshness_status_visible": "FRESHNESS" in categories,
        "recommendation_pack_readiness_visible": "RECOMMENDATION_PACK" in categories,
        "next_watch_focus_visible": any(item.watch_focus.strip() for item in clean_item_tuple),
        "live_fetch_deferred": live_fetch_enabled_item_count == 0 and dashboard.live_fetch_deferred,
        "network_calls_deferred": network_call_enabled_item_count == 0 and dashboard.network_calls_deferred,
        "raw_response_storage_deferred": raw_response_storage_enabled_item_count == 0 and dashboard.raw_response_storage_deferred,
        "live_adapter_record_emission_deferred": (
            live_adapter_record_emission_enabled_item_count == 0
            and dashboard.live_adapter_record_emission_deferred
        ),
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["product_visibility_stage"]:
        blockers.append("v8.1 must remain a product visibility stage.")
    if not safety_flags["public_intelligence_review_visible"]:
        blockers.append("v8.1 must expose public-intelligence review visibility.")
    if not safety_flags["candidate_coverage_visible"]:
        blockers.append("v8.1 must expose candidate coverage visibility.")
    if not safety_flags["freshness_status_visible"]:
        blockers.append("v8.1 must expose freshness/watch visibility.")
    if not safety_flags["recommendation_pack_readiness_visible"]:
        blockers.append("v8.1 must expose recommendation-pack readiness visibility.")
    if not safety_flags["next_watch_focus_visible"]:
        blockers.append("v8.1 must expose at least one next watch focus.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v8.1 must defer live fetching.")
    if not safety_flags["network_calls_deferred"]:
        blockers.append("v8.1 must defer network calls.")
    if not safety_flags["raw_response_storage_deferred"]:
        blockers.append("v8.1 must defer raw response storage.")
    if not safety_flags["live_adapter_record_emission_deferred"]:
        blockers.append("v8.1 must defer live adapter record emission.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v8.1 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v8.1 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v8.1 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v8.1 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return AutonomousResearchCycleStatusPanelResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        panel_status=PANEL_STATUS_READY if ready else PANEL_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=dashboard.selected_candidate_id,
        selected_sleeve_id=dashboard.selected_sleeve_id,
        item_count=len(clean_item_tuple),
        reviewed_item_count=reviewed_item_count,
        ready_item_count=ready_item_count,
        watch_item_count=watch_item_count,
        stale_item_count=stale_item_count,
        blocked_item_count=blocked_item_count,
        recommendation_pack_ready_item_count=recommendation_pack_ready_item_count,
        user_visible_item_count=user_visible_item_count,
        live_fetch_enabled_item_count=live_fetch_enabled_item_count,
        network_call_enabled_item_count=network_call_enabled_item_count,
        raw_response_storage_enabled_item_count=raw_response_storage_enabled_item_count,
        live_adapter_record_emission_enabled_item_count=live_adapter_record_emission_enabled_item_count,
        compatible_with_v8_0_operator_dashboard=dashboard.status == V8_0_STATUS_READY,
        items=clean_item_tuple,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "research_cycle_panel_ready": ready},
    )
