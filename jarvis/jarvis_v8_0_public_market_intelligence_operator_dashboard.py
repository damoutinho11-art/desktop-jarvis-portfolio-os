"""J.A.R.V.I.S. v8.0 public market intelligence operator dashboard.

This stage exposes the v7 public-market-intelligence readiness chain in a
user-facing operator dashboard shape.

It does not enable live fetching.

Safety boundary:
- dashboard visibility only
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

from .jarvis_v7_10_live_public_market_intelligence_readiness_closeout_audit import (
    STATUS_READY as V7_10_STATUS_READY,
    audit_v7_10_live_public_market_intelligence_readiness_closeout_audit,
)


STATUS_READY = "JARVIS_V8_0_PUBLIC_MARKET_INTELLIGENCE_OPERATOR_DASHBOARD_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V8_0_PUBLIC_MARKET_INTELLIGENCE_OPERATOR_DASHBOARD_BLOCKED_SAFE"

NEXT_STAGE = "v8_1_autonomous_research_cycle_status_panel"

DASHBOARD_STATUS_READY = "PUBLIC_MARKET_INTELLIGENCE_OPERATOR_DASHBOARD_READY"
DASHBOARD_STATUS_BLOCKED = "PUBLIC_MARKET_INTELLIGENCE_OPERATOR_DASHBOARD_BLOCKED"

CARD_STATE_READY = "READY"
CARD_STATE_DISABLED = "DISABLED"
CARD_STATE_BLOCKED = "BLOCKED"
CARD_STATE_INFO = "INFO"


@dataclass(frozen=True)
class PublicMarketIntelligenceDashboardCard:
    card_id: str
    title: str
    category: str
    state: str
    priority: int
    summary: str
    evidence: str
    next_operator_action: str
    user_visible: bool
    blocks_live_fetch: bool
    live_fetch_enabled: bool
    network_call_enabled: bool
    raw_response_storage_enabled: bool
    live_adapter_record_emission_enabled: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_dashboard_card_only(self) -> bool:
        return (
            self.user_visible
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
            "card_id": self.card_id,
            "title": self.title,
            "category": self.category,
            "state": self.state,
            "priority": self.priority,
            "summary": self.summary,
            "evidence": self.evidence,
            "next_operator_action": self.next_operator_action,
            "user_visible": self.user_visible,
            "blocks_live_fetch": self.blocks_live_fetch,
            "live_fetch_enabled": self.live_fetch_enabled,
            "network_call_enabled": self.network_call_enabled,
            "raw_response_storage_enabled": self.raw_response_storage_enabled,
            "live_adapter_record_emission_enabled": self.live_adapter_record_emission_enabled,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_dashboard_card_only": self.safe_dashboard_card_only(),
        }


@dataclass(frozen=True)
class PublicMarketIntelligenceOperatorDashboardResult:
    status: str
    dashboard_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    card_count: int
    ready_card_count: int
    disabled_card_count: int
    blocked_card_count: int
    user_visible_card_count: int
    live_fetch_enabled_card_count: int
    network_call_enabled_card_count: int
    raw_response_storage_enabled_card_count: int
    live_adapter_record_emission_enabled_card_count: int
    compatible_with_v7_10_readiness_closeout: bool
    cards: tuple[PublicMarketIntelligenceDashboardCard, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    operator_dashboard_ready: bool
    dashboard_visibility_only: bool
    v7_chain_closeout_visible: bool
    selected_candidate_visible: bool
    provider_readiness_visible: bool
    disabled_live_fetch_visible: bool
    execution_safety_visible: bool
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
            "dashboard_status": self.dashboard_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "card_count": self.card_count,
            "ready_card_count": self.ready_card_count,
            "disabled_card_count": self.disabled_card_count,
            "blocked_card_count": self.blocked_card_count,
            "user_visible_card_count": self.user_visible_card_count,
            "live_fetch_enabled_card_count": self.live_fetch_enabled_card_count,
            "network_call_enabled_card_count": self.network_call_enabled_card_count,
            "raw_response_storage_enabled_card_count": self.raw_response_storage_enabled_card_count,
            "live_adapter_record_emission_enabled_card_count": self.live_adapter_record_emission_enabled_card_count,
            "compatible_with_v7_10_readiness_closeout": self.compatible_with_v7_10_readiness_closeout,
            "cards": [card.to_dict() for card in self.cards],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "operator_dashboard_ready": self.operator_dashboard_ready,
            "dashboard_visibility_only": self.dashboard_visibility_only,
            "v7_chain_closeout_visible": self.v7_chain_closeout_visible,
            "selected_candidate_visible": self.selected_candidate_visible,
            "provider_readiness_visible": self.provider_readiness_visible,
            "disabled_live_fetch_visible": self.disabled_live_fetch_visible,
            "execution_safety_visible": self.execution_safety_visible,
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


def _card(
    card_id: str,
    title: str,
    category: str,
    state: str,
    priority: int,
    summary: str,
    evidence: str,
    next_operator_action: str,
    blocks_live_fetch: bool,
) -> PublicMarketIntelligenceDashboardCard:
    return PublicMarketIntelligenceDashboardCard(
        card_id=card_id,
        title=title,
        category=category,
        state=state,
        priority=priority,
        summary=summary,
        evidence=evidence,
        next_operator_action=next_operator_action,
        user_visible=True,
        blocks_live_fetch=blocks_live_fetch,
        live_fetch_enabled=False,
        network_call_enabled=False,
        raw_response_storage_enabled=False,
        live_adapter_record_emission_enabled=False,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_public_market_intelligence_dashboard_cards() -> tuple[
    PublicMarketIntelligenceDashboardCard, ...
]:
    closeout = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()

    return (
        _card(
            "v7_public_market_chain_closeout",
            "Public market intelligence chain",
            "READINESS",
            CARD_STATE_READY if closeout.v7_chain_closeout_complete else CARD_STATE_BLOCKED,
            10,
            "v7 public-market-intelligence preparation chain is closed out up to, but not including, live fetching.",
            (
                f"check_count={closeout.check_count}; "
                f"passed_check_count={closeout.passed_check_count}; "
                f"failed_check_count={closeout.failed_check_count}; "
                f"chain_stage_count={closeout.chain_stage_count}"
            ),
            "Use dashboard state for operator visibility; do not enable live fetch from v8.0.",
            True,
        ),
        _card(
            "selected_candidate_public_intelligence_coverage",
            "Selected candidate public intelligence coverage",
            "CANDIDATE",
            CARD_STATE_READY,
            20,
            "Selected candidate has public-intelligence readiness coverage from the v7 chain.",
            (
                f"selected_candidate_id={closeout.selected_candidate_id}; "
                f"selected_sleeve_id={closeout.selected_sleeve_id}"
            ),
            "Surface this in the weekly recommendation evidence pack.",
            False,
        ),
        _card(
            "provider_registry_and_binding_readiness",
            "Provider registry and binding readiness",
            "PROVIDERS",
            CARD_STATE_READY if closeout.providers_disabled_by_default else CARD_STATE_BLOCKED,
            30,
            "Approved provider metadata and disabled adapter skeleton bindings are visible.",
            (
                f"providers_disabled_by_default={closeout.providers_disabled_by_default}; "
                f"adapters_disabled_by_default={closeout.adapters_disabled_by_default}"
            ),
            "Keep provider visibility dashboard-only until explicit live-fetch stage.",
            True,
        ),
        _card(
            "live_fetch_disabled_status",
            "Live fetch disabled status",
            "LIVE_FETCH",
            CARD_STATE_DISABLED,
            40,
            "Live public market fetching remains disabled.",
            (
                f"live_fetch_enablement_allowed={closeout.live_fetch_enablement_allowed}; "
                f"live_fetch_deferred={closeout.live_fetch_deferred}"
            ),
            "Do not enable live fetching from the dashboard.",
            True,
        ),
        _card(
            "network_and_raw_storage_status",
            "Network and raw response storage status",
            "DATA_SAFETY",
            CARD_STATE_DISABLED,
            50,
            "Network calls and raw response storage remain disabled.",
            (
                f"network_calls_deferred={closeout.network_calls_deferred}; "
                f"raw_response_storage_deferred={closeout.raw_response_storage_deferred}; "
                f"live_adapter_record_emission_deferred={closeout.live_adapter_record_emission_deferred}"
            ),
            "Show as blocked until a future explicit live public data stage.",
            True,
        ),
        _card(
            "execution_safety_boundary",
            "Execution safety boundary",
            "EXECUTION_SAFETY",
            CARD_STATE_READY,
            60,
            "No buy request, broker connection, order placement, or trade execution exists.",
            (
                f"buy_request_deferred={closeout.buy_request_deferred}; "
                f"broker_connection_forbidden={closeout.broker_connection_forbidden}; "
                f"order_placement_forbidden={closeout.order_placement_forbidden}; "
                f"no_trades_executed={closeout.no_trades_executed}"
            ),
            "Final real-world buy remains outside J.A.R.V.I.S. and manual.",
            False,
        ),
    )


def audit_v8_0_public_market_intelligence_operator_dashboard(
    cards: tuple[PublicMarketIntelligenceDashboardCard, ...] | None | object = None,
) -> PublicMarketIntelligenceOperatorDashboardResult:
    closeout = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()

    if cards is None:
        effective_cards = build_public_market_intelligence_dashboard_cards()
        invalid_override = False
    elif isinstance(cards, tuple):
        effective_cards = cards
        invalid_override = False
    else:
        effective_cards = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v8.0 is operator dashboard visibility only.",
        "v8.0 exposes v7 readiness state but does not enable live fetching.",
        "No live public network call is attempted in v8.0.",
        "No raw public response payload is stored in v8.0.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Dashboard card override must be a tuple of PublicMarketIntelligenceDashboardCard.")

    if closeout.status != V7_10_STATUS_READY or closeout.blockers:
        blockers.append("Source v7.10 live public market intelligence readiness closeout audit is blocked.")

    if not effective_cards:
        blockers.append("No public market intelligence dashboard cards were produced.")

    card_ids: list[str] = []
    clean_cards: list[PublicMarketIntelligenceDashboardCard] = []

    for index, card in enumerate(effective_cards):
        if not isinstance(card, PublicMarketIntelligenceDashboardCard):
            blockers.append(f"Dashboard card at index {index} must be a PublicMarketIntelligenceDashboardCard.")
            continue

        clean_cards.append(card)
        card_ids.append(card.card_id)

        if not card.card_id.strip():
            blockers.append("Dashboard card ID is required.")
        if not card.title.strip():
            blockers.append(f"{card.card_id}: title is required.")
        if not card.category.strip():
            blockers.append(f"{card.card_id}: category is required.")
        if card.state not in {CARD_STATE_READY, CARD_STATE_DISABLED, CARD_STATE_BLOCKED, CARD_STATE_INFO}:
            blockers.append(f"{card.card_id}: state is not allowed.")
        if card.priority <= 0:
            blockers.append(f"{card.card_id}: priority must be positive.")
        if not card.summary.strip():
            blockers.append(f"{card.card_id}: summary is required.")
        if not card.evidence.strip():
            blockers.append(f"{card.card_id}: evidence is required.")
        if not card.next_operator_action.strip():
            blockers.append(f"{card.card_id}: next operator action is required.")
        if not card.user_visible:
            blockers.append(f"{card.card_id}: dashboard card must be user-visible.")
        if card.live_fetch_enabled:
            blockers.append(f"{card.card_id}: live fetching is forbidden in v8.0.")
        if card.network_call_enabled:
            blockers.append(f"{card.card_id}: network calls are forbidden in v8.0.")
        if card.raw_response_storage_enabled:
            blockers.append(f"{card.card_id}: raw response storage is forbidden in v8.0.")
        if card.live_adapter_record_emission_enabled:
            blockers.append(f"{card.card_id}: live adapter record emission is forbidden in v8.0.")
        if not card.safe_dashboard_card_only():
            blockers.append(f"{card.card_id}: dashboard card must remain visibility-only and non-executable.")
        if card.creates_buy_request:
            blockers.append(f"{card.card_id}: buy request creation is forbidden.")
        if card.connects_broker:
            blockers.append(f"{card.card_id}: broker connection is forbidden.")
        if card.places_order:
            blockers.append(f"{card.card_id}: order placement is forbidden.")
        if card.executes_trade:
            blockers.append(f"{card.card_id}: trade execution is forbidden.")

    if len(card_ids) != len(set(card_ids)):
        blockers.append("Public market intelligence dashboard card IDs must be unique.")

    clean_card_tuple = tuple(clean_cards)

    required_card_ids = {
        "v7_public_market_chain_closeout",
        "selected_candidate_public_intelligence_coverage",
        "provider_registry_and_binding_readiness",
        "live_fetch_disabled_status",
        "network_and_raw_storage_status",
        "execution_safety_boundary",
    }
    missing_card_ids = sorted(required_card_ids - set(card_ids))
    if missing_card_ids:
        blockers.append("Dashboard must include all required public market intelligence visibility cards.")

    ready_card_count = sum(1 for card in clean_card_tuple if card.state == CARD_STATE_READY)
    disabled_card_count = sum(1 for card in clean_card_tuple if card.state == CARD_STATE_DISABLED)
    blocked_card_count = sum(1 for card in clean_card_tuple if card.state == CARD_STATE_BLOCKED)
    user_visible_card_count = sum(1 for card in clean_card_tuple if card.user_visible)
    live_fetch_enabled_card_count = sum(1 for card in clean_card_tuple if card.live_fetch_enabled)
    network_call_enabled_card_count = sum(1 for card in clean_card_tuple if card.network_call_enabled)
    raw_response_storage_enabled_card_count = sum(
        1 for card in clean_card_tuple if card.raw_response_storage_enabled
    )
    live_adapter_record_emission_enabled_card_count = sum(
        1 for card in clean_card_tuple if card.live_adapter_record_emission_enabled
    )

    categories = {card.category for card in clean_card_tuple}

    safety_flags = {
        "operator_dashboard_ready": False,
        "dashboard_visibility_only": True,
        "v7_chain_closeout_visible": "READINESS" in categories,
        "selected_candidate_visible": "CANDIDATE" in categories,
        "provider_readiness_visible": "PROVIDERS" in categories,
        "disabled_live_fetch_visible": "LIVE_FETCH" in categories,
        "execution_safety_visible": "EXECUTION_SAFETY" in categories,
        "live_fetch_deferred": live_fetch_enabled_card_count == 0 and closeout.live_fetch_deferred,
        "network_calls_deferred": network_call_enabled_card_count == 0 and closeout.network_calls_deferred,
        "raw_response_storage_deferred": raw_response_storage_enabled_card_count == 0 and closeout.raw_response_storage_deferred,
        "live_adapter_record_emission_deferred": (
            live_adapter_record_emission_enabled_card_count == 0
            and closeout.live_adapter_record_emission_deferred
        ),
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["dashboard_visibility_only"]:
        blockers.append("v8.0 must remain dashboard-visibility-only.")
    if not safety_flags["v7_chain_closeout_visible"]:
        blockers.append("v8.0 must expose v7 chain closeout visibility.")
    if not safety_flags["selected_candidate_visible"]:
        blockers.append("v8.0 must expose selected-candidate visibility.")
    if not safety_flags["provider_readiness_visible"]:
        blockers.append("v8.0 must expose provider readiness visibility.")
    if not safety_flags["disabled_live_fetch_visible"]:
        blockers.append("v8.0 must expose disabled live-fetch visibility.")
    if not safety_flags["execution_safety_visible"]:
        blockers.append("v8.0 must expose execution safety visibility.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v8.0 must defer live fetching.")
    if not safety_flags["network_calls_deferred"]:
        blockers.append("v8.0 must defer network calls.")
    if not safety_flags["raw_response_storage_deferred"]:
        blockers.append("v8.0 must defer raw response storage.")
    if not safety_flags["live_adapter_record_emission_deferred"]:
        blockers.append("v8.0 must defer live adapter record emission.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v8.0 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v8.0 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v8.0 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v8.0 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return PublicMarketIntelligenceOperatorDashboardResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        dashboard_status=DASHBOARD_STATUS_READY if ready else DASHBOARD_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=closeout.selected_candidate_id,
        selected_sleeve_id=closeout.selected_sleeve_id,
        card_count=len(clean_card_tuple),
        ready_card_count=ready_card_count,
        disabled_card_count=disabled_card_count,
        blocked_card_count=blocked_card_count,
        user_visible_card_count=user_visible_card_count,
        live_fetch_enabled_card_count=live_fetch_enabled_card_count,
        network_call_enabled_card_count=network_call_enabled_card_count,
        raw_response_storage_enabled_card_count=raw_response_storage_enabled_card_count,
        live_adapter_record_emission_enabled_card_count=live_adapter_record_emission_enabled_card_count,
        compatible_with_v7_10_readiness_closeout=closeout.status == V7_10_STATUS_READY,
        cards=clean_card_tuple,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "operator_dashboard_ready": ready},
    )
