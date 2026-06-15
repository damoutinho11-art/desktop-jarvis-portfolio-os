"""J.A.R.V.I.S. v8.3 portfolio action brief generator.

Turns the weekly recommendation evidence pack into a concise operator-facing
portfolio action brief.

This is not a buy request.

Safety boundary:
- action brief only
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

from .jarvis_v8_2_weekly_recommendation_evidence_pack_integration import (
    STATUS_READY as V8_2_STATUS_READY,
    audit_v8_2_weekly_recommendation_evidence_pack_integration,
)


STATUS_READY = "JARVIS_V8_3_PORTFOLIO_ACTION_BRIEF_GENERATOR_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V8_3_PORTFOLIO_ACTION_BRIEF_GENERATOR_BLOCKED_SAFE"

BRIEF_STATUS_READY = "PORTFOLIO_ACTION_BRIEF_READY"
BRIEF_STATUS_BLOCKED = "PORTFOLIO_ACTION_BRIEF_BLOCKED"

NEXT_STAGE = "v8_4_operator_command_center_closeout"

BRIEF_TYPE_PREPARATORY = "PREPARATORY_PORTFOLIO_ACTION_BRIEF"


@dataclass(frozen=True)
class PortfolioActionBrief:
    brief_id: str
    brief_type: str
    selected_candidate_id: str
    selected_sleeve_id: str
    headline: str
    preparation_reason: str
    evidence_summary: str
    watch_summary: str
    blocked_summary: str
    final_manual_action: str
    operator_instruction: str
    user_visible: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool
    live_fetch_enabled: bool
    network_call_enabled: bool
    raw_response_storage_enabled: bool
    live_adapter_record_emission_enabled: bool

    def safe_brief_only(self) -> bool:
        return (
            self.user_visible
            and self.brief_type == BRIEF_TYPE_PREPARATORY
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
            "brief_id": self.brief_id,
            "brief_type": self.brief_type,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "headline": self.headline,
            "preparation_reason": self.preparation_reason,
            "evidence_summary": self.evidence_summary,
            "watch_summary": self.watch_summary,
            "blocked_summary": self.blocked_summary,
            "final_manual_action": self.final_manual_action,
            "operator_instruction": self.operator_instruction,
            "user_visible": self.user_visible,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "live_fetch_enabled": self.live_fetch_enabled,
            "network_call_enabled": self.network_call_enabled,
            "raw_response_storage_enabled": self.raw_response_storage_enabled,
            "live_adapter_record_emission_enabled": self.live_adapter_record_emission_enabled,
            "safe_brief_only": self.safe_brief_only(),
        }


@dataclass(frozen=True)
class PortfolioActionBriefGeneratorResult:
    status: str
    brief_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    evidence_section_count: int
    ready_evidence_section_count: int
    watch_evidence_section_count: int
    blocked_evidence_section_count: int
    compatible_with_v8_2_evidence_pack: bool
    brief: PortfolioActionBrief
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    action_brief_ready: bool
    product_brief_stage: bool
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
            "brief_status": self.brief_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "evidence_section_count": self.evidence_section_count,
            "ready_evidence_section_count": self.ready_evidence_section_count,
            "watch_evidence_section_count": self.watch_evidence_section_count,
            "blocked_evidence_section_count": self.blocked_evidence_section_count,
            "compatible_with_v8_2_evidence_pack": self.compatible_with_v8_2_evidence_pack,
            "brief": self.brief.to_dict(),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "action_brief_ready": self.action_brief_ready,
            "product_brief_stage": self.product_brief_stage,
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


def build_portfolio_action_brief() -> PortfolioActionBrief:
    pack = audit_v8_2_weekly_recommendation_evidence_pack_integration()

    ready_sections = [section for section in pack.sections if section.state == "READY"]
    watch_sections = [section for section in pack.sections if section.state == "WATCH"]
    blocked_sections = [section for section in pack.sections if section.state == "BLOCKED"]

    evidence_names = ", ".join(section.title for section in ready_sections)
    watch_names = ", ".join(section.title for section in watch_sections) or "none"
    blocked_names = ", ".join(section.title for section in blocked_sections) or "none"

    return PortfolioActionBrief(
        brief_id="weekly_portfolio_action_brief",
        brief_type=BRIEF_TYPE_PREPARATORY,
        selected_candidate_id=pack.selected_candidate_id,
        selected_sleeve_id=pack.selected_sleeve_id,
        headline="J.A.R.V.I.S. has prepared a weekly portfolio action brief.",
        preparation_reason=(
            "The weekly recommendation evidence pack is ready and contains reviewed "
            "research-cycle, selected-candidate, public-intelligence, freshness-watch, "
            "and execution-boundary context."
        ),
        evidence_summary=f"Ready evidence sections: {evidence_names}.",
        watch_summary=f"Watch-only sections: {watch_names}.",
        blocked_summary=f"Blocked sections: {blocked_names}.",
        final_manual_action=(
            "Any real-world buy remains a manual action outside J.A.R.V.I.S."
        ),
        operator_instruction=(
            "Review the brief, confirm the evidence context, then decide manually outside the system. "
            "Do not treat this brief as an order or broker instruction."
        ),
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


def audit_v8_3_portfolio_action_brief_generator(
    brief: PortfolioActionBrief | None | object = None,
) -> PortfolioActionBriefGeneratorResult:
    pack = audit_v8_2_weekly_recommendation_evidence_pack_integration()

    if brief is None:
        effective_brief = build_portfolio_action_brief()
        invalid_override = False
    elif isinstance(brief, PortfolioActionBrief):
        effective_brief = brief
        invalid_override = False
    else:
        effective_brief = PortfolioActionBrief(
            brief_id="invalid",
            brief_type="INVALID",
            selected_candidate_id="",
            selected_sleeve_id="",
            headline="",
            preparation_reason="",
            evidence_summary="",
            watch_summary="",
            blocked_summary="",
            final_manual_action="",
            operator_instruction="",
            user_visible=False,
            creates_buy_request=False,
            connects_broker=False,
            places_order=False,
            executes_trade=False,
            live_fetch_enabled=False,
            network_call_enabled=False,
            raw_response_storage_enabled=False,
            live_adapter_record_emission_enabled=False,
        )
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v8.3 generates a preparatory portfolio action brief only.",
        "The action brief is not a buy request.",
        "No broker connection, order placement, or trade is created.",
        "Live public fetching remains disabled.",
    ]

    if invalid_override:
        blockers.append("Brief override must be a PortfolioActionBrief.")

    if pack.status != V8_2_STATUS_READY or pack.blockers:
        blockers.append("Source v8.2 weekly recommendation evidence pack integration is blocked.")

    if not effective_brief.brief_id.strip():
        blockers.append("Brief ID is required.")
    if effective_brief.brief_type != BRIEF_TYPE_PREPARATORY:
        blockers.append("Brief type must be preparatory.")
    if not effective_brief.selected_candidate_id.strip():
        blockers.append("Selected candidate ID is required.")
    if not effective_brief.selected_sleeve_id.strip():
        blockers.append("Selected sleeve ID is required.")
    if not effective_brief.headline.strip():
        blockers.append("Brief headline is required.")
    if not effective_brief.preparation_reason.strip():
        blockers.append("Preparation reason is required.")
    if not effective_brief.evidence_summary.strip():
        blockers.append("Evidence summary is required.")
    if not effective_brief.watch_summary.strip():
        blockers.append("Watch summary is required.")
    if not effective_brief.blocked_summary.strip():
        blockers.append("Blocked summary is required.")
    if not effective_brief.final_manual_action.strip():
        blockers.append("Final manual action text is required.")
    if not effective_brief.operator_instruction.strip():
        blockers.append("Operator instruction is required.")
    if not effective_brief.user_visible:
        blockers.append("Brief must be user-visible.")
    if not effective_brief.safe_brief_only():
        blockers.append("Brief must remain preparatory, visible, and non-executable.")
    if effective_brief.creates_buy_request:
        blockers.append("Buy request creation is forbidden.")
    if effective_brief.connects_broker:
        blockers.append("Broker connection is forbidden.")
    if effective_brief.places_order:
        blockers.append("Order placement is forbidden.")
    if effective_brief.executes_trade:
        blockers.append("Trade execution is forbidden.")
    if effective_brief.live_fetch_enabled:
        blockers.append("Live fetching is forbidden.")
    if effective_brief.network_call_enabled:
        blockers.append("Network calls are forbidden.")
    if effective_brief.raw_response_storage_enabled:
        blockers.append("Raw response storage is forbidden.")
    if effective_brief.live_adapter_record_emission_enabled:
        blockers.append("Live adapter record emission is forbidden.")

    ready_count = sum(1 for section in pack.sections if section.state == "READY")
    watch_count = sum(1 for section in pack.sections if section.state == "WATCH")
    blocked_count = sum(1 for section in pack.sections if section.state == "BLOCKED")

    safety_flags = {
        "action_brief_ready": False,
        "product_brief_stage": True,
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

    return PortfolioActionBriefGeneratorResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        brief_status=BRIEF_STATUS_READY if ready else BRIEF_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=pack.selected_candidate_id,
        selected_sleeve_id=pack.selected_sleeve_id,
        evidence_section_count=pack.section_count,
        ready_evidence_section_count=ready_count,
        watch_evidence_section_count=watch_count,
        blocked_evidence_section_count=blocked_count,
        compatible_with_v8_2_evidence_pack=pack.status == V8_2_STATUS_READY,
        brief=effective_brief,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "action_brief_ready": ready},
    )
