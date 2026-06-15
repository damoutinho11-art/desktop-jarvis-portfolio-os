"""J.A.R.V.I.S. v6.14 recommendation dashboard integration.

This stage surfaces the autonomous weekly recommendation draft as a dashboard/
command-center payload.

Safety boundary:
- dashboard visibility only
- autonomous recommendation display allowed
- manual buy instructions display allowed
- no buy request creation
- no broker/API connection
- no order placement
- no trade execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v6_13_autonomous_weekly_recommendation_draft_builder import (
    AutonomousWeeklyRecommendationDraftResult,
    audit_v6_13_autonomous_weekly_recommendation_draft_builder,
)


STATUS_READY = "JARVIS_V6_14_RECOMMENDATION_DASHBOARD_INTEGRATION_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_14_RECOMMENDATION_DASHBOARD_INTEGRATION_BLOCKED_SAFE"

NEXT_STAGE = "v6.15_autonomous_command_center_closeout_audit"

DASHBOARD_CARD_STATUS_VISIBLE = "VISIBLE_AUTONOMOUS_RECOMMENDATION"
DASHBOARD_CARD_STATUS_BLOCKED = "BLOCKED_AUTONOMOUS_RECOMMENDATION"

CARD_ID_WEEKLY_RECOMMENDATION = "weekly_recommendation_card"
CARD_ID_SAFETY_BOUNDARY = "safety_boundary_card"
CARD_ID_MANUAL_ACTION = "manual_action_card"


@dataclass(frozen=True)
class RecommendationDashboardCard:
    card_id: str
    title: str
    status: str
    severity: str
    summary: str
    details: tuple[str, ...]
    action_label: str
    user_action_required: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_display_only(self) -> bool:
        return (
            not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_id": self.card_id,
            "title": self.title,
            "status": self.status,
            "severity": self.severity,
            "summary": self.summary,
            "details": list(self.details),
            "action_label": self.action_label,
            "user_action_required": self.user_action_required,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_display_only": self.safe_display_only(),
        }


@dataclass(frozen=True)
class RecommendationDashboardPayload:
    dashboard_id: str
    dashboard_status: str
    analyzed_policy_id: str
    selected_candidate_id: str
    selected_sleeve_id: str
    recommendation_status: str
    recommendation_decision: str
    confidence_score: int
    headline: str
    cards: tuple[RecommendationDashboardCard, ...]
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_dashboard_only(self) -> bool:
        return (
            not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
            and all(card.safe_display_only() for card in self.cards)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "dashboard_id": self.dashboard_id,
            "dashboard_status": self.dashboard_status,
            "analyzed_policy_id": self.analyzed_policy_id,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "recommendation_status": self.recommendation_status,
            "recommendation_decision": self.recommendation_decision,
            "confidence_score": self.confidence_score,
            "headline": self.headline,
            "cards": [card.to_dict() for card in self.cards],
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_dashboard_only": self.safe_dashboard_only(),
        }


@dataclass(frozen=True)
class RecommendationDashboardIntegrationResult:
    status: str
    recommended_next_stage: str
    analyzed_policy_id: str
    selected_candidate_id: str
    selected_sleeve_id: str
    dashboard_card_count: int
    visible_recommendation_card_count: int
    safety_card_count: int
    manual_action_card_count: int
    dashboard_payload: RecommendationDashboardPayload | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    dashboard_integration_ready: bool
    dashboard_only: bool
    autonomous_recommendation_displayed: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "analyzed_policy_id": self.analyzed_policy_id,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "dashboard_card_count": self.dashboard_card_count,
            "visible_recommendation_card_count": self.visible_recommendation_card_count,
            "safety_card_count": self.safety_card_count,
            "manual_action_card_count": self.manual_action_card_count,
            "dashboard_payload": None if self.dashboard_payload is None else self.dashboard_payload.to_dict(),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "dashboard_integration_ready": self.dashboard_integration_ready,
            "dashboard_only": self.dashboard_only,
            "autonomous_recommendation_displayed": self.autonomous_recommendation_displayed,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def build_recommendation_dashboard_payload(
    recommendation_result: AutonomousWeeklyRecommendationDraftResult,
) -> RecommendationDashboardPayload | None:
    recommendation = recommendation_result.recommendation
    if recommendation is None:
        return None

    recommendation_card = RecommendationDashboardCard(
        card_id=CARD_ID_WEEKLY_RECOMMENDATION,
        title="Autonomous Weekly Recommendation",
        status=DASHBOARD_CARD_STATUS_VISIBLE,
        severity="ACTION_CONTEXT",
        summary=(
            f"J.A.R.V.I.S. selected {recommendation.selected_candidate_id} "
            f"for sleeve {recommendation.selected_sleeve_id}."
        ),
        details=(
            f"decision: {recommendation.decision}",
            f"confidence score: {recommendation.confidence_score}",
            f"amount logic: {recommendation.suggested_manual_amount_logic}",
            f"primary reason: {recommendation.primary_reason}",
        ),
        action_label="Review recommendation and buy manually only if you agree",
        user_action_required=True,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )

    safety_card = RecommendationDashboardCard(
        card_id=CARD_ID_SAFETY_BOUNDARY,
        title="Execution Boundary",
        status=DASHBOARD_CARD_STATUS_VISIBLE,
        severity="SAFETY",
        summary="J.A.R.V.I.S. displays intelligence only and does not execute.",
        details=(
            "No buy request exists.",
            "No broker connection exists.",
            "No order placement exists.",
            "No trade execution exists.",
        ),
        action_label="Keep execution outside J.A.R.V.I.S.",
        user_action_required=False,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )

    manual_action_card = RecommendationDashboardCard(
        card_id=CARD_ID_MANUAL_ACTION,
        title="Only Manual Step",
        status=DASHBOARD_CARD_STATUS_VISIBLE,
        severity="USER_ACTION",
        summary="The only manual step is the user's final real-world buy.",
        details=recommendation.manual_buy_instructions,
        action_label="User manually buys outside J.A.R.V.I.S.",
        user_action_required=True,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )

    return RecommendationDashboardPayload(
        dashboard_id="jarvis_weekly_recommendation_dashboard",
        dashboard_status=DASHBOARD_CARD_STATUS_VISIBLE,
        analyzed_policy_id=recommendation_result.analyzed_policy_id,
        selected_candidate_id=recommendation.selected_candidate_id,
        selected_sleeve_id=recommendation.selected_sleeve_id,
        recommendation_status=recommendation.recommendation_status,
        recommendation_decision=recommendation.decision,
        confidence_score=recommendation.confidence_score,
        headline=(
            f"Weekly autonomous recommendation: {recommendation.selected_candidate_id} "
            f"({recommendation.selected_sleeve_id})"
        ),
        cards=(recommendation_card, safety_card, manual_action_card),
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def audit_v6_14_recommendation_dashboard_integration(
    dashboard_payload: RecommendationDashboardPayload | None | object = None,
) -> RecommendationDashboardIntegrationResult:
    recommendation_result = audit_v6_13_autonomous_weekly_recommendation_draft_builder()

    if dashboard_payload is None:
        effective_dashboard = build_recommendation_dashboard_payload(recommendation_result)
    else:
        effective_dashboard = dashboard_payload

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.14 integrates the autonomous recommendation into dashboard visibility only.",
        "The dashboard can show manual buy instructions but creates no buy request.",
        "No broker connection, order placement, or trade is created.",
    ]

    if recommendation_result.blockers:
        blockers.append("Source autonomous recommendation draft is blocked.")
    if recommendation_result.recommendation is None:
        blockers.append("No autonomous recommendation draft is available for dashboard integration.")

    if effective_dashboard is not None and not isinstance(
        effective_dashboard,
        RecommendationDashboardPayload,
    ):
        blockers.append("Dashboard override must be a RecommendationDashboardPayload.")
        effective_dashboard = None

    if effective_dashboard is None:
        blockers.append("No recommendation dashboard payload was created.")

    if effective_dashboard is not None:
        if not effective_dashboard.headline.strip():
            blockers.append("Dashboard headline is required.")
        if effective_dashboard.dashboard_status != DASHBOARD_CARD_STATUS_VISIBLE:
            blockers.append("Dashboard status must be visible.")
        if not effective_dashboard.cards:
            blockers.append("Dashboard cards are required.")
        if not effective_dashboard.safe_dashboard_only():
            blockers.append("Dashboard payload must remain display-only.")
        if effective_dashboard.creates_buy_request:
            blockers.append("Dashboard buy request creation is forbidden.")
        if effective_dashboard.connects_broker:
            blockers.append("Dashboard broker connection is forbidden.")
        if effective_dashboard.places_order:
            blockers.append("Dashboard order placement is forbidden.")
        if effective_dashboard.executes_trade:
            blockers.append("Dashboard trade execution is forbidden.")

        card_ids = [card.card_id for card in effective_dashboard.cards]
        if len(card_ids) != len(set(card_ids)):
            blockers.append("Dashboard card IDs must be unique.")

        required_cards = {
            CARD_ID_WEEKLY_RECOMMENDATION,
            CARD_ID_SAFETY_BOUNDARY,
            CARD_ID_MANUAL_ACTION,
        }
        missing_cards = required_cards - set(card_ids)
        for card_id in sorted(missing_cards):
            blockers.append(f"Dashboard is missing required card: {card_id}")

        for card in effective_dashboard.cards:
            if not card.title.strip():
                blockers.append(f"{card.card_id}: title is required.")
            if not card.summary.strip():
                blockers.append(f"{card.card_id}: summary is required.")
            if not card.details:
                blockers.append(f"{card.card_id}: details are required.")
            if not card.safe_display_only():
                blockers.append(f"{card.card_id}: card must remain display-only.")
            if card.creates_buy_request:
                blockers.append(f"{card.card_id}: buy request creation is forbidden.")
            if card.connects_broker:
                blockers.append(f"{card.card_id}: broker connection is forbidden.")
            if card.places_order:
                blockers.append(f"{card.card_id}: order placement is forbidden.")
            if card.executes_trade:
                blockers.append(f"{card.card_id}: trade execution is forbidden.")

    cards = () if effective_dashboard is None else effective_dashboard.cards
    visible_recommendation_card_count = sum(
        1 for card in cards if card.card_id == CARD_ID_WEEKLY_RECOMMENDATION
    )
    safety_card_count = sum(1 for card in cards if card.card_id == CARD_ID_SAFETY_BOUNDARY)
    manual_action_card_count = sum(1 for card in cards if card.card_id == CARD_ID_MANUAL_ACTION)

    if visible_recommendation_card_count != 1:
        blockers.append("Exactly one weekly recommendation card is required.")
    if safety_card_count != 1:
        blockers.append("Exactly one safety boundary card is required.")
    if manual_action_card_count != 1:
        blockers.append("Exactly one manual action card is required.")

    safety_flags = {
        "dashboard_integration_ready": False,
        "dashboard_only": True,
        "autonomous_recommendation_displayed": effective_dashboard is not None,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["dashboard_only"]:
        blockers.append("v6.14 must remain dashboard-only.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v6.14 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v6.14 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v6.14 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.14 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))

    selected_candidate_id = ""
    selected_sleeve_id = ""
    analyzed_policy_id = recommendation_result.analyzed_policy_id
    if effective_dashboard is not None:
        selected_candidate_id = effective_dashboard.selected_candidate_id
        selected_sleeve_id = effective_dashboard.selected_sleeve_id
        analyzed_policy_id = effective_dashboard.analyzed_policy_id

    return RecommendationDashboardIntegrationResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        analyzed_policy_id=analyzed_policy_id,
        selected_candidate_id=selected_candidate_id,
        selected_sleeve_id=selected_sleeve_id,
        dashboard_card_count=len(cards),
        visible_recommendation_card_count=visible_recommendation_card_count,
        safety_card_count=safety_card_count,
        manual_action_card_count=manual_action_card_count,
        dashboard_payload=effective_dashboard,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "dashboard_integration_ready": not unique_blockers},
    )
