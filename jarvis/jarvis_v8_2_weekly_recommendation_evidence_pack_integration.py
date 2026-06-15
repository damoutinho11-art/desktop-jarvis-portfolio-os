"""J.A.R.V.I.S. v8.2 weekly recommendation evidence pack integration.

This stage integrates the autonomous research-cycle status panel into a weekly
recommendation evidence pack shape.

It answers:
- why a recommendation can be prepared;
- what J.A.R.V.I.S. reviewed;
- what is ready;
- what is watch-only;
- what is not live yet;
- what remains safely blocked;
- what final action remains manual.

Safety boundary:
- evidence-pack integration only
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

from .jarvis_v8_1_autonomous_research_cycle_status_panel import (
    FRESHNESS_FRESH,
    FRESHNESS_NOT_LIVE,
    ITEM_STATE_READY,
    ITEM_STATE_WATCH,
    STATUS_READY as V8_1_STATUS_READY,
    audit_v8_1_autonomous_research_cycle_status_panel,
)


STATUS_READY = "JARVIS_V8_2_WEEKLY_RECOMMENDATION_EVIDENCE_PACK_INTEGRATION_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V8_2_WEEKLY_RECOMMENDATION_EVIDENCE_PACK_INTEGRATION_BLOCKED_SAFE"

NEXT_STAGE = "v8_3_portfolio_action_brief_generator"

PACK_STATUS_READY = "WEEKLY_RECOMMENDATION_EVIDENCE_PACK_INTEGRATION_READY"
PACK_STATUS_BLOCKED = "WEEKLY_RECOMMENDATION_EVIDENCE_PACK_INTEGRATION_BLOCKED"

SECTION_STATE_READY = "READY"
SECTION_STATE_WATCH = "WATCH"
SECTION_STATE_BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class WeeklyRecommendationEvidencePackSection:
    section_id: str
    title: str
    source_item_id: str
    category: str
    state: str
    freshness: str
    evidence_summary: str
    evidence_detail: str
    recommendation_relevance: str
    status_reason: str
    included_in_weekly_pack: bool
    ready_for_pack: bool
    watch_only: bool
    user_visible: bool
    final_user_action_required: bool
    live_fetch_enabled: bool
    network_call_enabled: bool
    raw_response_storage_enabled: bool
    live_adapter_record_emission_enabled: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def blocked(self) -> bool:
        return self.state == SECTION_STATE_BLOCKED

    def safe_evidence_pack_section_only(self) -> bool:
        return (
            self.user_visible
            and self.included_in_weekly_pack
            and self.final_user_action_required
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
            "section_id": self.section_id,
            "title": self.title,
            "source_item_id": self.source_item_id,
            "category": self.category,
            "state": self.state,
            "freshness": self.freshness,
            "evidence_summary": self.evidence_summary,
            "evidence_detail": self.evidence_detail,
            "recommendation_relevance": self.recommendation_relevance,
            "status_reason": self.status_reason,
            "included_in_weekly_pack": self.included_in_weekly_pack,
            "ready_for_pack": self.ready_for_pack,
            "watch_only": self.watch_only,
            "user_visible": self.user_visible,
            "final_user_action_required": self.final_user_action_required,
            "live_fetch_enabled": self.live_fetch_enabled,
            "network_call_enabled": self.network_call_enabled,
            "raw_response_storage_enabled": self.raw_response_storage_enabled,
            "live_adapter_record_emission_enabled": self.live_adapter_record_emission_enabled,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "blocked": self.blocked(),
            "safe_evidence_pack_section_only": self.safe_evidence_pack_section_only(),
        }


@dataclass(frozen=True)
class WeeklyRecommendationEvidencePackIntegrationResult:
    status: str
    pack_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    section_count: int
    included_section_count: int
    ready_section_count: int
    watch_section_count: int
    blocked_section_count: int
    ready_for_pack_section_count: int
    user_visible_section_count: int
    live_fetch_enabled_section_count: int
    network_call_enabled_section_count: int
    raw_response_storage_enabled_section_count: int
    live_adapter_record_emission_enabled_section_count: int
    compatible_with_v8_1_research_cycle_panel: bool
    sections: tuple[WeeklyRecommendationEvidencePackSection, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    evidence_pack_integration_ready: bool
    product_integration_stage: bool
    research_review_integrated: bool
    selected_candidate_integrated: bool
    public_intelligence_integrated: bool
    freshness_watch_integrated: bool
    execution_boundary_integrated: bool
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
            "pack_status": self.pack_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "section_count": self.section_count,
            "included_section_count": self.included_section_count,
            "ready_section_count": self.ready_section_count,
            "watch_section_count": self.watch_section_count,
            "blocked_section_count": self.blocked_section_count,
            "ready_for_pack_section_count": self.ready_for_pack_section_count,
            "user_visible_section_count": self.user_visible_section_count,
            "live_fetch_enabled_section_count": self.live_fetch_enabled_section_count,
            "network_call_enabled_section_count": self.network_call_enabled_section_count,
            "raw_response_storage_enabled_section_count": self.raw_response_storage_enabled_section_count,
            "live_adapter_record_emission_enabled_section_count": self.live_adapter_record_emission_enabled_section_count,
            "compatible_with_v8_1_research_cycle_panel": self.compatible_with_v8_1_research_cycle_panel,
            "sections": [section.to_dict() for section in self.sections],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "evidence_pack_integration_ready": self.evidence_pack_integration_ready,
            "product_integration_stage": self.product_integration_stage,
            "research_review_integrated": self.research_review_integrated,
            "selected_candidate_integrated": self.selected_candidate_integrated,
            "public_intelligence_integrated": self.public_intelligence_integrated,
            "freshness_watch_integrated": self.freshness_watch_integrated,
            "execution_boundary_integrated": self.execution_boundary_integrated,
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


def _section(
    section_id: str,
    title: str,
    source_item_id: str,
    category: str,
    state: str,
    freshness: str,
    evidence_summary: str,
    evidence_detail: str,
    recommendation_relevance: str,
    status_reason: str,
    ready_for_pack: bool,
    watch_only: bool,
) -> WeeklyRecommendationEvidencePackSection:
    return WeeklyRecommendationEvidencePackSection(
        section_id=section_id,
        title=title,
        source_item_id=source_item_id,
        category=category,
        state=state,
        freshness=freshness,
        evidence_summary=evidence_summary,
        evidence_detail=evidence_detail,
        recommendation_relevance=recommendation_relevance,
        status_reason=status_reason,
        included_in_weekly_pack=True,
        ready_for_pack=ready_for_pack,
        watch_only=watch_only,
        user_visible=True,
        final_user_action_required=True,
        live_fetch_enabled=False,
        network_call_enabled=False,
        raw_response_storage_enabled=False,
        live_adapter_record_emission_enabled=False,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_weekly_recommendation_evidence_pack_sections() -> tuple[
    WeeklyRecommendationEvidencePackSection, ...
]:
    panel = audit_v8_1_autonomous_research_cycle_status_panel()
    item_by_id = {item.item_id: item for item in panel.items}

    public_item = item_by_id["public_intelligence_readiness_review"]
    candidate_item = item_by_id["selected_candidate_coverage_review"]
    provider_item = item_by_id["provider_and_binding_review"]
    freshness_item = item_by_id["live_data_freshness_review"]
    pack_item = item_by_id["weekly_recommendation_pack_readiness"]
    execution_item = item_by_id["execution_boundary_review"]

    return (
        _section(
            "research_cycle_review_summary",
            "Research cycle review summary",
            pack_item.item_id,
            "RESEARCH_REVIEW",
            SECTION_STATE_READY,
            FRESHNESS_NOT_LIVE,
            "J.A.R.V.I.S. reviewed the current autonomous research-cycle status.",
            (
                f"reviewed_item_count={panel.reviewed_item_count}; "
                f"ready_item_count={panel.ready_item_count}; "
                f"watch_item_count={panel.watch_item_count}; "
                f"blocked_item_count={panel.blocked_item_count}"
            ),
            "Explains why the weekly recommendation pack can be prepared.",
            "",
            True,
            False,
        ),
        _section(
            "selected_candidate_evidence_context",
            "Selected candidate evidence context",
            candidate_item.item_id,
            "SELECTED_CANDIDATE",
            SECTION_STATE_READY,
            FRESHNESS_NOT_LIVE,
            "Selected candidate coverage is available for the weekly recommendation pack.",
            candidate_item.evidence,
            "Carries candidate and sleeve identity into the recommendation evidence pack.",
            "",
            True,
            False,
        ),
        _section(
            "public_intelligence_readiness_context",
            "Public intelligence readiness context",
            public_item.item_id,
            "PUBLIC_INTELLIGENCE",
            SECTION_STATE_READY,
            FRESHNESS_NOT_LIVE,
            "Public-market-intelligence readiness is visible but non-live.",
            public_item.evidence,
            "Explains that public-intelligence support exists without live fetching.",
            "",
            True,
            False,
        ),
        _section(
            "provider_binding_context",
            "Provider and binding context",
            provider_item.item_id,
            "PROVIDER_BINDING",
            SECTION_STATE_READY,
            FRESHNESS_NOT_LIVE,
            "Provider registry and adapter binding readiness are visible.",
            provider_item.evidence,
            "Explains provider coverage while preserving disabled live-fetch state.",
            "",
            True,
            False,
        ),
        _section(
            "live_data_freshness_watch_context",
            "Live data freshness watch context",
            freshness_item.item_id,
            "FRESHNESS_WATCH",
            SECTION_STATE_WATCH,
            FRESHNESS_NOT_LIVE,
            "Live data freshness is watch-only because live public fetching is intentionally disabled.",
            freshness_item.evidence,
            "Prevents the recommendation pack from pretending it has live market data.",
            freshness_item.blocked_reason,
            True,
            True,
        ),
        _section(
            "execution_boundary_context",
            "Execution boundary context",
            execution_item.item_id,
            "EXECUTION_SAFETY",
            SECTION_STATE_READY,
            FRESHNESS_FRESH,
            "No execution path exists inside J.A.R.V.I.S.",
            execution_item.evidence,
            "Confirms the final real-world buy remains manual and outside the system.",
            "",
            True,
            False,
        ),
    )


def audit_v8_2_weekly_recommendation_evidence_pack_integration(
    sections: tuple[WeeklyRecommendationEvidencePackSection, ...] | None | object = None,
) -> WeeklyRecommendationEvidencePackIntegrationResult:
    panel = audit_v8_1_autonomous_research_cycle_status_panel()

    if sections is None:
        effective_sections = build_weekly_recommendation_evidence_pack_sections()
        invalid_override = False
    elif isinstance(sections, tuple):
        effective_sections = sections
        invalid_override = False
    else:
        effective_sections = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v8.2 integrates research-cycle status into a weekly recommendation evidence pack.",
        "Live data freshness is included as watch-only, not treated as live evidence.",
        "v8.2 does not create a buy request.",
        "No live public network call is attempted in v8.2.",
        "No broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Evidence pack section override must be a tuple of WeeklyRecommendationEvidencePackSection.")

    if panel.status != V8_1_STATUS_READY or panel.blockers:
        blockers.append("Source v8.1 autonomous research cycle status panel is blocked.")

    if not effective_sections:
        blockers.append("No weekly recommendation evidence pack sections were produced.")

    section_ids: list[str] = []
    clean_sections: list[WeeklyRecommendationEvidencePackSection] = []

    for index, section in enumerate(effective_sections):
        if not isinstance(section, WeeklyRecommendationEvidencePackSection):
            blockers.append(f"Evidence pack section at index {index} must be a WeeklyRecommendationEvidencePackSection.")
            continue

        clean_sections.append(section)
        section_ids.append(section.section_id)

        if not section.section_id.strip():
            blockers.append("Evidence pack section ID is required.")
        if not section.title.strip():
            blockers.append(f"{section.section_id}: title is required.")
        if not section.source_item_id.strip():
            blockers.append(f"{section.section_id}: source item ID is required.")
        if not section.category.strip():
            blockers.append(f"{section.section_id}: category is required.")
        if section.state not in {SECTION_STATE_READY, SECTION_STATE_WATCH, SECTION_STATE_BLOCKED}:
            blockers.append(f"{section.section_id}: state is not allowed.")
        if section.freshness not in {FRESHNESS_FRESH, FRESHNESS_NOT_LIVE}:
            blockers.append(f"{section.section_id}: freshness is not allowed.")
        if not section.evidence_summary.strip():
            blockers.append(f"{section.section_id}: evidence summary is required.")
        if not section.evidence_detail.strip():
            blockers.append(f"{section.section_id}: evidence detail is required.")
        if not section.recommendation_relevance.strip():
            blockers.append(f"{section.section_id}: recommendation relevance is required.")
        if section.state == SECTION_STATE_WATCH and not section.status_reason.strip():
            blockers.append(f"{section.section_id}: watch sections require a status reason.")
        if section.state == SECTION_STATE_BLOCKED and not section.status_reason.strip():
            blockers.append(f"{section.section_id}: blocked sections require a status reason.")
        if not section.included_in_weekly_pack:
            blockers.append(f"{section.section_id}: section must be included in weekly pack.")
        if not section.ready_for_pack:
            blockers.append(f"{section.section_id}: section must be ready for pack integration.")
        if section.watch_only and section.state != SECTION_STATE_WATCH:
            blockers.append(f"{section.section_id}: watch-only sections must use WATCH state.")
        if not section.user_visible:
            blockers.append(f"{section.section_id}: section must be user-visible.")
        if not section.final_user_action_required:
            blockers.append(f"{section.section_id}: final user action boundary must be explicit.")
        if section.live_fetch_enabled:
            blockers.append(f"{section.section_id}: live fetching is forbidden in v8.2.")
        if section.network_call_enabled:
            blockers.append(f"{section.section_id}: network calls are forbidden in v8.2.")
        if section.raw_response_storage_enabled:
            blockers.append(f"{section.section_id}: raw response storage is forbidden in v8.2.")
        if section.live_adapter_record_emission_enabled:
            blockers.append(f"{section.section_id}: live adapter record emission is forbidden in v8.2.")
        if not section.safe_evidence_pack_section_only():
            blockers.append(f"{section.section_id}: section must remain evidence-pack-only and non-executable.")
        if section.creates_buy_request:
            blockers.append(f"{section.section_id}: buy request creation is forbidden.")
        if section.connects_broker:
            blockers.append(f"{section.section_id}: broker connection is forbidden.")
        if section.places_order:
            blockers.append(f"{section.section_id}: order placement is forbidden.")
        if section.executes_trade:
            blockers.append(f"{section.section_id}: trade execution is forbidden.")

    if len(section_ids) != len(set(section_ids)):
        blockers.append("Weekly recommendation evidence pack section IDs must be unique.")

    required_section_ids = {
        "research_cycle_review_summary",
        "selected_candidate_evidence_context",
        "public_intelligence_readiness_context",
        "provider_binding_context",
        "live_data_freshness_watch_context",
        "execution_boundary_context",
    }
    missing_section_ids = sorted(required_section_ids - set(section_ids))
    if missing_section_ids:
        blockers.append("Weekly recommendation evidence pack must include all required sections.")

    clean_section_tuple = tuple(clean_sections)

    included_section_count = sum(1 for section in clean_section_tuple if section.included_in_weekly_pack)
    ready_section_count = sum(1 for section in clean_section_tuple if section.state == SECTION_STATE_READY)
    watch_section_count = sum(1 for section in clean_section_tuple if section.state == SECTION_STATE_WATCH)
    blocked_section_count = sum(1 for section in clean_section_tuple if section.state == SECTION_STATE_BLOCKED)
    ready_for_pack_section_count = sum(1 for section in clean_section_tuple if section.ready_for_pack)
    user_visible_section_count = sum(1 for section in clean_section_tuple if section.user_visible)
    live_fetch_enabled_section_count = sum(1 for section in clean_section_tuple if section.live_fetch_enabled)
    network_call_enabled_section_count = sum(1 for section in clean_section_tuple if section.network_call_enabled)
    raw_response_storage_enabled_section_count = sum(
        1 for section in clean_section_tuple if section.raw_response_storage_enabled
    )
    live_adapter_record_emission_enabled_section_count = sum(
        1 for section in clean_section_tuple if section.live_adapter_record_emission_enabled
    )

    categories = {section.category for section in clean_section_tuple}

    safety_flags = {
        "evidence_pack_integration_ready": False,
        "product_integration_stage": True,
        "research_review_integrated": "RESEARCH_REVIEW" in categories,
        "selected_candidate_integrated": "SELECTED_CANDIDATE" in categories,
        "public_intelligence_integrated": "PUBLIC_INTELLIGENCE" in categories,
        "freshness_watch_integrated": "FRESHNESS_WATCH" in categories,
        "execution_boundary_integrated": "EXECUTION_SAFETY" in categories,
        "live_fetch_deferred": live_fetch_enabled_section_count == 0 and panel.live_fetch_deferred,
        "network_calls_deferred": network_call_enabled_section_count == 0 and panel.network_calls_deferred,
        "raw_response_storage_deferred": raw_response_storage_enabled_section_count == 0 and panel.raw_response_storage_deferred,
        "live_adapter_record_emission_deferred": (
            live_adapter_record_emission_enabled_section_count == 0
            and panel.live_adapter_record_emission_deferred
        ),
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["product_integration_stage"]:
        blockers.append("v8.2 must remain a product integration stage.")
    if not safety_flags["research_review_integrated"]:
        blockers.append("v8.2 must integrate research-review context.")
    if not safety_flags["selected_candidate_integrated"]:
        blockers.append("v8.2 must integrate selected-candidate context.")
    if not safety_flags["public_intelligence_integrated"]:
        blockers.append("v8.2 must integrate public-intelligence context.")
    if not safety_flags["freshness_watch_integrated"]:
        blockers.append("v8.2 must integrate freshness/watch context.")
    if not safety_flags["execution_boundary_integrated"]:
        blockers.append("v8.2 must integrate execution-boundary context.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v8.2 must defer live fetching.")
    if not safety_flags["network_calls_deferred"]:
        blockers.append("v8.2 must defer network calls.")
    if not safety_flags["raw_response_storage_deferred"]:
        blockers.append("v8.2 must defer raw response storage.")
    if not safety_flags["live_adapter_record_emission_deferred"]:
        blockers.append("v8.2 must defer live adapter record emission.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v8.2 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v8.2 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v8.2 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v8.2 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return WeeklyRecommendationEvidencePackIntegrationResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        pack_status=PACK_STATUS_READY if ready else PACK_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=panel.selected_candidate_id,
        selected_sleeve_id=panel.selected_sleeve_id,
        section_count=len(clean_section_tuple),
        included_section_count=included_section_count,
        ready_section_count=ready_section_count,
        watch_section_count=watch_section_count,
        blocked_section_count=blocked_section_count,
        ready_for_pack_section_count=ready_for_pack_section_count,
        user_visible_section_count=user_visible_section_count,
        live_fetch_enabled_section_count=live_fetch_enabled_section_count,
        network_call_enabled_section_count=network_call_enabled_section_count,
        raw_response_storage_enabled_section_count=raw_response_storage_enabled_section_count,
        live_adapter_record_emission_enabled_section_count=live_adapter_record_emission_enabled_section_count,
        compatible_with_v8_1_research_cycle_panel=panel.status == V8_1_STATUS_READY,
        sections=clean_section_tuple,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "evidence_pack_integration_ready": ready},
    )
