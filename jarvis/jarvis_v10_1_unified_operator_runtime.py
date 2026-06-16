"""J.A.R.V.I.S. v10.1 unified operator runtime.

This is the first one-command J.A.R.V.I.S. brain/router.

It orchestrates existing layers:
- v10.0 autonomous public data refresh runtime;
- v8.0 public market intelligence operator dashboard;
- v6.13 autonomous weekly recommendation draft;
- v6.14 recommendation dashboard integration;
- v8.2 weekly recommendation evidence pack integration;
- v8.3 portfolio action brief generator.

It does not rebuild those layers.

Safety boundary:
- no broker connection;
- no credentials;
- no private account ingestion;
- no buy request;
- no order placement;
- no trade execution;
- only Diogo performs the final real-world buy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v6_13_autonomous_weekly_recommendation_draft_builder import (
    STATUS_READY as V6_13_STATUS_READY,
    audit_v6_13_autonomous_weekly_recommendation_draft_builder,
)
from .jarvis_v6_14_recommendation_dashboard_integration import (
    STATUS_READY as V6_14_STATUS_READY,
    audit_v6_14_recommendation_dashboard_integration,
)
from .jarvis_v8_0_public_market_intelligence_operator_dashboard import (
    STATUS_READY as V8_0_STATUS_READY,
    audit_v8_0_public_market_intelligence_operator_dashboard,
)
from .jarvis_v8_2_weekly_recommendation_evidence_pack_integration import (
    STATUS_READY as V8_2_STATUS_READY,
    audit_v8_2_weekly_recommendation_evidence_pack_integration,
)
from .jarvis_v8_3_portfolio_action_brief_generator import (
    STATUS_READY as V8_3_STATUS_READY,
    audit_v8_3_portfolio_action_brief_generator,
)
from .jarvis_v10_0_autonomous_public_data_refresh_runtime import (
    STATUS_READY as V10_0_STATUS_READY,
    audit_v10_0_autonomous_public_data_refresh_runtime,
)


STATUS_READY = "JARVIS_V10_1_UNIFIED_OPERATOR_RUNTIME_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V10_1_UNIFIED_OPERATOR_RUNTIME_BLOCKED_SAFE"

RUNTIME_READY = "UNIFIED_OPERATOR_RUNTIME_READY"
RUNTIME_BLOCKED = "UNIFIED_OPERATOR_RUNTIME_BLOCKED"

NEXT_STAGE = "v11_0_command_center_ui_shell"


@dataclass(frozen=True)
class UnifiedOperatorRuntimeComponent:
    component_id: str
    title: str
    status: str
    ready: bool
    summary: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    user_visible: bool = True
    creates_buy_request: bool = False
    connects_broker: bool = False
    places_order: bool = False
    executes_trade: bool = False

    def safe_component_only(self) -> bool:
        return (
            self.user_visible
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "component_id": self.component_id,
            "title": self.title,
            "status": self.status,
            "ready": self.ready,
            "summary": self.summary,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "user_visible": self.user_visible,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_component_only": self.safe_component_only(),
        }


@dataclass(frozen=True)
class UnifiedOperatorRuntimeResult:
    status: str
    runtime_status: str
    recommended_next_stage: str
    component_count: int
    ready_component_count: int
    blocked_component_count: int
    warning_count: int
    blocker_count: int
    selected_candidate_id: str
    selected_sleeve_id: str
    data_refresh_status: str
    data_source_manifest_loaded: bool
    autonomous_refresh_ready: bool
    raw_public_data_refreshed: bool
    ready_for_downstream_normalization: bool
    ready_for_downstream_source_quality_gate: bool
    recommendation_quality_current_data: bool
    evidence_pack_status: str
    recommendation_status: str
    recommendation_dashboard_status: str
    public_market_dashboard_status: str
    action_brief_status: str
    voice_summary_ready: bool
    voice_interface_available: bool
    voice_summary: str
    components: tuple[UnifiedOperatorRuntimeComponent, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    unified_operator_runtime_ready: bool
    one_command_runtime: bool
    product_mode_runtime: bool
    data_refresh_integrated: bool
    evidence_pack_integrated: bool
    recommendation_integrated: bool
    dashboard_integrated: bool
    action_brief_integrated: bool
    voice_ready_summary_integrated: bool
    ui_shell_not_built_yet: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "runtime_status": self.runtime_status,
            "recommended_next_stage": self.recommended_next_stage,
            "component_count": self.component_count,
            "ready_component_count": self.ready_component_count,
            "blocked_component_count": self.blocked_component_count,
            "warning_count": self.warning_count,
            "blocker_count": self.blocker_count,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "data_refresh_status": self.data_refresh_status,
            "data_source_manifest_loaded": self.data_source_manifest_loaded,
            "autonomous_refresh_ready": self.autonomous_refresh_ready,
            "raw_public_data_refreshed": self.raw_public_data_refreshed,
            "ready_for_downstream_normalization": self.ready_for_downstream_normalization,
            "ready_for_downstream_source_quality_gate": self.ready_for_downstream_source_quality_gate,
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "evidence_pack_status": self.evidence_pack_status,
            "recommendation_status": self.recommendation_status,
            "recommendation_dashboard_status": self.recommendation_dashboard_status,
            "public_market_dashboard_status": self.public_market_dashboard_status,
            "action_brief_status": self.action_brief_status,
            "voice_summary_ready": self.voice_summary_ready,
            "voice_interface_available": self.voice_interface_available,
            "voice_summary": self.voice_summary,
            "components": [component.to_dict() for component in self.components],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "unified_operator_runtime_ready": self.unified_operator_runtime_ready,
            "one_command_runtime": self.one_command_runtime,
            "product_mode_runtime": self.product_mode_runtime,
            "data_refresh_integrated": self.data_refresh_integrated,
            "evidence_pack_integrated": self.evidence_pack_integrated,
            "recommendation_integrated": self.recommendation_integrated,
            "dashboard_integrated": self.dashboard_integrated,
            "action_brief_integrated": self.action_brief_integrated,
            "voice_ready_summary_integrated": self.voice_ready_summary_integrated,
            "ui_shell_not_built_yet": self.ui_shell_not_built_yet,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
        }


def _component(
    *,
    component_id: str,
    title: str,
    status: str,
    ready: bool,
    summary: str,
    blockers: tuple[str, ...] = (),
    warnings: tuple[str, ...] = (),
) -> UnifiedOperatorRuntimeComponent:
    return UnifiedOperatorRuntimeComponent(
        component_id=component_id,
        title=title,
        status=status,
        ready=ready,
        summary=summary,
        blockers=blockers,
        warnings=warnings,
    )


def build_voice_ready_operator_summary(
    *,
    selected_candidate_id: str,
    selected_sleeve_id: str,
    data_ready: bool,
    raw_public_data_refreshed: bool,
    evidence_ready: bool,
    recommendation_ready: bool,
    action_brief_ready: bool,
) -> str:
    data_sentence = (
        "public data refresh is ready with refreshed raw public data"
        if raw_public_data_refreshed
        else "public data refresh is ready, but raw public data has not been refreshed in this run"
    )
    current_data_sentence = (
        "recommendation-quality current data is available"
        if data_ready
        else "recommendation-quality current data is not yet confirmed"
    )

    return (
        "J.A.R.V.I.S. operator summary. "
        f"Selected candidate is {selected_candidate_id} in sleeve {selected_sleeve_id}. "
        f"The {data_sentence}. "
        f"The {current_data_sentence}. "
        f"Evidence pack ready: {evidence_ready}. "
        f"Recommendation ready: {recommendation_ready}. "
        f"Action brief ready: {action_brief_ready}. "
        "No buy request has been created. No broker is connected. No order has been placed. "
        "The only manual action remains Diogo's final real-world buy."
    )


def audit_v10_1_unified_operator_runtime() -> UnifiedOperatorRuntimeResult:
    data_refresh = audit_v10_0_autonomous_public_data_refresh_runtime()
    public_market_dashboard = audit_v8_0_public_market_intelligence_operator_dashboard()
    recommendation = audit_v6_13_autonomous_weekly_recommendation_draft_builder()
    recommendation_dashboard = audit_v6_14_recommendation_dashboard_integration()
    evidence_pack = audit_v8_2_weekly_recommendation_evidence_pack_integration()
    action_brief = audit_v8_3_portfolio_action_brief_generator()

    selected_candidate_id = action_brief.selected_candidate_id or recommendation.selected_candidate_id
    selected_sleeve_id = action_brief.selected_sleeve_id or recommendation.selected_sleeve_id

    components = (
        _component(
            component_id="autonomous_public_data_refresh_runtime",
            title="Autonomous public data refresh runtime",
            status=data_refresh.status,
            ready=data_refresh.status == V10_0_STATUS_READY,
            summary=(
                f"manifest_loaded={data_refresh.source_manifest_loaded}; "
                f"autonomous_refresh_ready={data_refresh.autonomous_refresh_ready}; "
                f"raw_public_data_refreshed={data_refresh.raw_public_data_refreshed}; "
                f"recommendation_quality_current_data={data_refresh.recommendation_quality_current_data}"
            ),
            blockers=data_refresh.blockers,
            warnings=data_refresh.warnings,
        ),
        _component(
            component_id="public_market_intelligence_dashboard",
            title="Public market intelligence dashboard",
            status=public_market_dashboard.status,
            ready=public_market_dashboard.status == V8_0_STATUS_READY,
            summary=(
                f"cards={public_market_dashboard.card_count}; "
                f"ready_cards={public_market_dashboard.ready_card_count}; "
                f"live_fetch_deferred={public_market_dashboard.live_fetch_deferred}"
            ),
            blockers=public_market_dashboard.blockers,
            warnings=public_market_dashboard.warnings,
        ),
        _component(
            component_id="weekly_recommendation_draft",
            title="Autonomous weekly recommendation draft",
            status=recommendation.status,
            ready=recommendation.status == V6_13_STATUS_READY,
            summary=(
                f"recommendations={recommendation.recommendation_count}; "
                f"selected_candidate={recommendation.selected_candidate_id}; "
                f"selected_sleeve={recommendation.selected_sleeve_id}"
            ),
            blockers=recommendation.blockers,
            warnings=recommendation.warnings,
        ),
        _component(
            component_id="recommendation_dashboard",
            title="Recommendation dashboard integration",
            status=recommendation_dashboard.status,
            ready=recommendation_dashboard.status == V6_14_STATUS_READY,
            summary=(
                f"cards={recommendation_dashboard.dashboard_card_count}; "
                f"dashboard_only={recommendation_dashboard.dashboard_only}; "
                f"recommendation_displayed={recommendation_dashboard.autonomous_recommendation_displayed}"
            ),
            blockers=recommendation_dashboard.blockers,
            warnings=recommendation_dashboard.warnings,
        ),
        _component(
            component_id="weekly_recommendation_evidence_pack",
            title="Weekly recommendation evidence pack integration",
            status=evidence_pack.status,
            ready=evidence_pack.status == V8_2_STATUS_READY,
            summary=(
                f"sections={evidence_pack.section_count}; "
                f"ready={evidence_pack.ready_section_count}; "
                f"watch={evidence_pack.watch_section_count}; "
                f"blocked={evidence_pack.blocked_section_count}"
            ),
            blockers=evidence_pack.blockers,
            warnings=evidence_pack.warnings,
        ),
        _component(
            component_id="portfolio_action_brief",
            title="Portfolio action brief generator",
            status=action_brief.status,
            ready=action_brief.status == V8_3_STATUS_READY,
            summary=(
                f"candidate={action_brief.selected_candidate_id}; "
                f"sleeve={action_brief.selected_sleeve_id}; "
                f"ready_evidence={action_brief.ready_evidence_section_count}; "
                f"watch_evidence={action_brief.watch_evidence_section_count}"
            ),
            blockers=action_brief.blockers,
            warnings=action_brief.warnings,
        ),
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v10.1 is a unified operator runtime only.",
        "It routes existing layers instead of rebuilding them.",
        "Voice is prepared as a voice-ready text summary; no full voice interface exists yet.",
        "UI shell is not built yet; v11.0 should own the browser command center.",
    ]

    for component in components:
        if component.blockers:
            blockers.append(f"{component.component_id} has blockers.")
            blockers.extend(component.blockers)
        if not component.ready:
            blockers.append(f"{component.component_id} is not ready: {component.status}")
        if not component.safe_component_only():
            blockers.append(f"{component.component_id} must remain user-visible and non-executable.")
        warnings.extend(component.warnings)

    ready_component_count = sum(1 for component in components if component.ready)
    blocked_component_count = len(components) - ready_component_count

    voice_summary = build_voice_ready_operator_summary(
        selected_candidate_id=selected_candidate_id,
        selected_sleeve_id=selected_sleeve_id,
        data_ready=data_refresh.recommendation_quality_current_data,
        raw_public_data_refreshed=data_refresh.raw_public_data_refreshed,
        evidence_ready=evidence_pack.status == V8_2_STATUS_READY,
        recommendation_ready=recommendation.status == V6_13_STATUS_READY,
        action_brief_ready=action_brief.status == V8_3_STATUS_READY,
    )

    flags = {
        "one_command_runtime": True,
        "product_mode_runtime": True,
        "data_refresh_integrated": data_refresh.status == V10_0_STATUS_READY,
        "evidence_pack_integrated": evidence_pack.status == V8_2_STATUS_READY,
        "recommendation_integrated": recommendation.status == V6_13_STATUS_READY
        and recommendation_dashboard.status == V6_14_STATUS_READY,
        "dashboard_integrated": public_market_dashboard.status == V8_0_STATUS_READY
        and recommendation_dashboard.status == V6_14_STATUS_READY,
        "action_brief_integrated": action_brief.status == V8_3_STATUS_READY,
        "voice_ready_summary_integrated": bool(voice_summary.strip()),
        "ui_shell_not_built_yet": True,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
        "credentials_forbidden": True,
        "private_account_data_ingestion_forbidden": True,
    }

    if not flags["data_refresh_integrated"]:
        blockers.append("Data refresh runtime must be integrated.")
    if not flags["evidence_pack_integrated"]:
        blockers.append("Evidence pack integration must be integrated.")
    if not flags["recommendation_integrated"]:
        blockers.append("Recommendation layers must be integrated.")
    if not flags["dashboard_integrated"]:
        blockers.append("Dashboard layers must be integrated.")
    if not flags["action_brief_integrated"]:
        blockers.append("Action brief generator must be integrated.")
    if not flags["voice_ready_summary_integrated"]:
        blockers.append("Voice-ready summary must be generated.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))
    ready = not unique_blockers

    return UnifiedOperatorRuntimeResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        runtime_status=RUNTIME_READY if ready else RUNTIME_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        component_count=len(components),
        ready_component_count=ready_component_count,
        blocked_component_count=blocked_component_count,
        warning_count=len(unique_warnings),
        blocker_count=len(unique_blockers),
        selected_candidate_id=selected_candidate_id,
        selected_sleeve_id=selected_sleeve_id,
        data_refresh_status=data_refresh.status,
        data_source_manifest_loaded=data_refresh.source_manifest_loaded,
        autonomous_refresh_ready=data_refresh.autonomous_refresh_ready,
        raw_public_data_refreshed=data_refresh.raw_public_data_refreshed,
        ready_for_downstream_normalization=data_refresh.ready_for_downstream_normalization,
        ready_for_downstream_source_quality_gate=data_refresh.ready_for_downstream_source_quality_gate,
        recommendation_quality_current_data=data_refresh.recommendation_quality_current_data,
        evidence_pack_status=evidence_pack.status,
        recommendation_status=recommendation.status,
        recommendation_dashboard_status=recommendation_dashboard.status,
        public_market_dashboard_status=public_market_dashboard.status,
        action_brief_status=action_brief.status,
        voice_summary_ready=bool(voice_summary.strip()),
        voice_interface_available=False,
        voice_summary=voice_summary,
        components=components,
        blockers=unique_blockers,
        warnings=unique_warnings,
        unified_operator_runtime_ready=ready,
        **flags,
    )
