"""Stable non-versioned J.A.R.V.I.S. runtime operator facade.

This module is the stable active entrypoint used by ``jarvis_operator.py``.

Daily mode delegates to the validated v45 evidence-pack backend. Weekly buy-prep
mode renders the v50 manual weekly amount router. v51 adds the allocation
strategy/data coverage audit. v52 adds brokerless manual portfolio snapshot
intake.
"""

from __future__ import annotations

import sys
from typing import Any

from jarvis.runtime.product_mode_operator import main as _product_mode_operator_main
from jarvis.runtime.correlation_risk_model import main as _correlation_risk_model_main
from jarvis.runtime.stock_specific_public_evidence import main as _stock_specific_public_evidence_main
from jarvis.runtime.data_freshness_acquisition_gate import main as _data_freshness_acquisition_gate_main
from jarvis.runtime.tradable_candidate_universe_gate import main as _tradable_candidate_universe_gate_main
from jarvis.runtime.stock_candidate_universe_expansion import main as _stock_candidate_universe_expansion_main
from jarvis.runtime.cross_lane_dynamic_allocation_preflight import main as _cross_lane_dynamic_allocation_preflight_main
from jarvis.runtime.dynamic_quality_allocator import main as _dynamic_quality_allocator_main
from jarvis.runtime.multi_candidate_instrument_selector import main as _multi_candidate_instrument_selector_main
from jarvis.runtime.data_readiness_status import main as _data_readiness_status_main
from jarvis.runtime.product_api import main as _product_api_main
from jarvis.runtime.full_system_audit import main as _full_system_audit_main
from jarvis.runtime.news_coverage_readiness import main as _news_coverage_readiness_main
from jarvis.runtime.dashboard_contract import main as _dashboard_contract_main
from jarvis.runtime.chat_interface_contract import main as _chat_interface_contract_main
from jarvis.runtime.local_server import main as _local_server_main
from jarvis.runtime.local_server_live_endpoint_smoke import main as _local_server_live_endpoint_smoke_main
from jarvis.runtime.assistant_tool_registry import main as _assistant_tool_registry_main
from jarvis.runtime.assistant_data_source_registry import main as _assistant_data_source_registry_main
from jarvis.runtime.assistant_asset_lookup import main as _assistant_asset_lookup_main
from jarvis.runtime.assistant_market_context import main as _assistant_market_context_main
from jarvis.runtime.assistant_news_context import main as _assistant_news_context_main
from jarvis.runtime.assistant_router import main as _assistant_router_main
from jarvis.runtime.assistant_system_audit import main as _assistant_system_audit_main
from jarvis.runtime.finance_intelligence_core import main as _finance_intelligence_core_main
from jarvis.runtime.market_data_normalized import main as _market_data_normalized_main
from jarvis.runtime.selected_instrument_resolver import main as _selected_instrument_resolver_main
from jarvis.runtime.fx_assistant_bridge import main as _fx_assistant_bridge_main
from jarvis.runtime.news_intelligence_contract import main as _news_intelligence_contract_main
from jarvis.runtime.current_runtime_fast_gate import main as _current_runtime_fast_gate_main
from jarvis.runtime.manual_holdings_update import main as _manual_holdings_update_main
from jarvis.runtime.user_runbook import main as _user_runbook_main
from jarvis.runtime.post_app_acceptance_gate import main as _post_app_acceptance_gate_main
from jarvis.runtime.live_news_fetcher import main as _live_news_fetcher_main
from jarvis.runtime.dashboard_noise_audit import main as _dashboard_noise_audit_main
from jarvis.runtime.dashboard_calm_ui_freeze_gate import main as _dashboard_calm_ui_freeze_gate_main
from jarvis.runtime.jarvis_session_memory import main as _jarvis_session_memory_main
from jarvis.runtime.voice_briefing import main as _voice_briefing_main
from jarvis.runtime.what_changed_since_last_time import main as _what_changed_since_last_time_main
from jarvis.runtime.local_app_packaging_polish import main as _local_app_packaging_polish_main
from jarvis.runtime.final_safe_jarvis_experience_gate import main as _final_safe_jarvis_experience_gate_main
from jarvis.runtime.jarvis_experience_parity_gate import main as _jarvis_experience_parity_gate_main
from jarvis.runtime.finance_database_universe import main as _finance_database_universe_main
from jarvis.runtime.finance_toolkit_fundamentals import main as _finance_toolkit_fundamentals_main
from jarvis.runtime.universe_explorer import main as _universe_explorer_main
from jarvis.runtime.portfolio_health_report_card import main as _portfolio_health_report_card_main
from jarvis.runtime.premium_orbital_design_system import main as _premium_orbital_design_system_main
from jarvis.runtime.premium_command_center_dashboard import main as _premium_command_center_dashboard_main

from jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge import (
    DEFAULT_EVIDENCE_PACK_PATH,
    EVIDENCE_BLOCKED,
    EVIDENCE_READY,
    EVIDENCE_REVIEW_REQUIRED,
    NEXT_STAGE as V45_NEXT_STAGE,
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    FreeResearchCacheEvidencePackBridgeResult,
    build_free_research_cache_evidence_pack_bridge_result,
    format_free_research_cache_evidence_pack_bridge,
    main as _v45_main,
)
from jarvis.runtime.allocation_strategy_audit import main as _allocation_strategy_audit_main
from jarvis.runtime.manual_portfolio_snapshot import main as _manual_portfolio_snapshot_main
from jarvis.runtime.portfolio_exposure_audit import main as _portfolio_exposure_audit_main
from jarvis.runtime.dynamic_target_policy import main as _dynamic_target_policy_main
from jarvis.runtime.platform_lane_policy import main as _platform_lane_policy_main
from jarvis.runtime.platform_weekly_action_packet import main as _platform_weekly_action_packet_main
from jarvis.runtime.platform_data_completeness_gate import main as _platform_data_completeness_gate_main
from jarvis.runtime.monthly_expenses_intake import main as _monthly_expenses_intake_main
from jarvis.runtime.manual_cost_basis_intake import main as _manual_cost_basis_intake_main
from jarvis.runtime.active_runtime_surface_redundancy_audit import main as _active_runtime_surface_redundancy_audit_main
from jarvis.runtime.import_closure_safe_archive_plan import main as _import_closure_safe_archive_plan_main
from jarvis.runtime.personal_finance_contribution_bridge import main as _personal_finance_contribution_bridge_main
from jarvis.runtime.weekly_packet import (
    NEXT_STAGE as WEEKLY_PACKET_NEXT_STAGE,
    build_weekly_manual_buy_packet_result,
    format_weekly_manual_buy_packet,
    main as _weekly_packet_main,
)

ACTIVE_RUNTIME_MODULE = "jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge"
ACTIVE_WEEKLY_PACKET_MODULE = "jarvis.runtime.weekly_packet"
ACTIVE_ALLOCATION_STRATEGY_AUDIT_MODULE = "jarvis.runtime.allocation_strategy_audit"
ACTIVE_MANUAL_PORTFOLIO_SNAPSHOT_MODULE = "jarvis.runtime.manual_portfolio_snapshot"
ACTIVE_RUNTIME_STAGE = "v138.0"
STABLE_RUNTIME_FACADE = "jarvis.runtime.operator"
CURRENT_OPERATOR_SURFACE = "live_news_ui_acceptance_gate"
ACTIVE_LIVE_NEWS_UI_ACCEPTANCE_GATE_MODULE = "jarvis.runtime.live_news_ui_acceptance_gate"
ACTIVE_PLATFORM_DATA_COMPLETENESS_GATE_MODULE = "jarvis.runtime.platform_data_completeness_gate"
ACTIVE_MONTHLY_EXPENSES_INTAKE_MODULE = "jarvis.runtime.monthly_expenses_intake"
ACTIVE_FINANCE_INTELLIGENCE_CORE_MODULE = "jarvis.runtime.finance_intelligence_core"
ACTIVE_MARKET_DATA_NORMALIZED_MODULE = "jarvis.runtime.market_data_normalized"
ACTIVE_SELECTED_INSTRUMENT_RESOLVER_MODULE = "jarvis.runtime.selected_instrument_resolver"
ACTIVE_FX_ASSISTANT_BRIDGE_MODULE = "jarvis.runtime.fx_assistant_bridge"
ACTIVE_NEWS_INTELLIGENCE_CONTRACT_MODULE = "jarvis.runtime.news_intelligence_contract"
ACTIVE_CURRENT_RUNTIME_FAST_GATE_MODULE = "jarvis.runtime.current_runtime_fast_gate"
ACTIVE_MANUAL_HOLDINGS_UPDATE_MODULE = "jarvis.runtime.manual_holdings_update"
ACTIVE_USER_RUNBOOK_MODULE = "jarvis.runtime.user_runbook"
ACTIVE_POST_APP_ACCEPTANCE_GATE_MODULE = "jarvis.runtime.post_app_acceptance_gate"
ACTIVE_LIVE_NEWS_FETCHER_MODULE = "jarvis.runtime.live_news_fetcher"
ACTIVE_DASHBOARD_NOISE_AUDIT_MODULE = "jarvis.runtime.dashboard_noise_audit"
ACTIVE_DASHBOARD_CALM_UI_FREEZE_GATE_MODULE = "jarvis.runtime.dashboard_calm_ui_freeze_gate"
ACTIVE_JARVIS_SESSION_MEMORY_MODULE = "jarvis.runtime.jarvis_session_memory"
ACTIVE_VOICE_BRIEFING_MODULE = "jarvis.runtime.voice_briefing"
ACTIVE_WHAT_CHANGED_SINCE_LAST_TIME_MODULE = "jarvis.runtime.what_changed_since_last_time"
ACTIVE_LOCAL_APP_PACKAGING_POLISH_MODULE = "jarvis.runtime.local_app_packaging_polish"
ACTIVE_FINAL_SAFE_JARVIS_EXPERIENCE_GATE_MODULE = "jarvis.runtime.final_safe_jarvis_experience_gate"
ACTIVE_JARVIS_EXPERIENCE_PARITY_GATE_MODULE = "jarvis.runtime.jarvis_experience_parity_gate"
ACTIVE_FINANCE_DATABASE_UNIVERSE_MODULE = "jarvis.runtime.finance_database_universe"
ACTIVE_FINANCE_TOOLKIT_FUNDAMENTALS_MODULE = "jarvis.runtime.finance_toolkit_fundamentals"
ACTIVE_UNIVERSE_EXPLORER_MODULE = "jarvis.runtime.universe_explorer"
ACTIVE_PORTFOLIO_HEALTH_REPORT_CARD_MODULE = "jarvis.runtime.portfolio_health_report_card"
ACTIVE_PREMIUM_ORBITAL_DESIGN_SYSTEM_MODULE = "jarvis.runtime.premium_orbital_design_system"
ACTIVE_PREMIUM_COMMAND_CENTER_DASHBOARD_MODULE = "jarvis.runtime.premium_command_center_dashboard"


def get_active_runtime_surface() -> dict[str, str]:
    """Return the current stable-to-versioned runtime mapping."""

    return {
        "stable_runtime_facade": STABLE_RUNTIME_FACADE,
        "active_runtime_module": ACTIVE_RUNTIME_MODULE,
        "active_weekly_packet_module": ACTIVE_WEEKLY_PACKET_MODULE,
        "active_allocation_strategy_audit_module": ACTIVE_ALLOCATION_STRATEGY_AUDIT_MODULE,
        "active_manual_portfolio_snapshot_module": ACTIVE_MANUAL_PORTFOLIO_SNAPSHOT_MODULE,
        "active_runtime_stage": ACTIVE_RUNTIME_STAGE,
    "active_live_news_ui_acceptance_gate_module": ACTIVE_LIVE_NEWS_UI_ACCEPTANCE_GATE_MODULE,
        "active_portfolio_exposure_audit_module": "jarvis.runtime.portfolio_exposure_audit",
        "active_dynamic_target_policy_module": "jarvis.runtime.dynamic_target_policy",
        "active_platform_lane_policy_module": "jarvis.runtime.platform_lane_policy",
        "active_platform_weekly_action_packet_module": "jarvis.runtime.platform_weekly_action_packet",
        "active_platform_data_completeness_gate_module": ACTIVE_PLATFORM_DATA_COMPLETENESS_GATE_MODULE,
        "active_monthly_expenses_intake_module": ACTIVE_MONTHLY_EXPENSES_INTAKE_MODULE,
        "active_personal_finance_contribution_bridge_module": "jarvis.runtime.personal_finance_contribution_bridge",
        "active_full_allocation_blocker_reconciliation_module": "jarvis.runtime.personal_finance_contribution_bridge",
        "active_manual_cost_basis_intake_module": "jarvis.runtime.manual_cost_basis_intake",
        "active_manual_cost_basis_bridge_module": "jarvis.runtime.personal_finance_contribution_bridge + jarvis.runtime.allocation_strategy_audit",
        "active_runtime_surface_redundancy_audit_module": "jarvis.runtime.active_runtime_surface_redundancy_audit",
        "active_import_closure_safe_archive_plan_module": "jarvis.runtime.import_closure_safe_archive_plan",
        "active_stable_runtime_safety_module": "jarvis.runtime.safety",
        "active_import_closure_precision_hotfix": "utf-8-sig import parser support",
        "active_import_closure_relative_import_precision": "relative import parser support",
        "active_non_active_archive_candidate_report_module": "jarvis.runtime.non_active_archive_candidate_report",
        "active_reversible_archive_staging_plan_module": "jarvis.runtime.reversible_archive_staging_plan",
        "active_reversible_report_archive_execution_archive_root": "archive/non_active/v70_report_only_python_safe",
        "active_remaining_python_archive_risk_audit_module": "jarvis.runtime.remaining_python_archive_risk_audit",
        "active_next_safe_python_archive_execution_plan_module": "jarvis.runtime.next_safe_python_archive_execution_plan",
        "active_next_safe_python_archive_execution_archive_root": "archive/non_active/v72_next_safe_python_safe",
        "active_validation_blocked_legacy_candidate_decoupling_audit_module": "jarvis.runtime.validation_blocked_legacy_candidate_decoupling_audit",
        "active_validation_blocked_v5_replacement_plan_module": "jarvis.runtime.validation_blocked_v5_replacement_plan",
        "active_runtime_v5_replacement_coverage_module": "jarvis.runtime.active_runtime_v5_replacement_coverage",
        "active_final_v5_archive_execution_plan_module": "jarvis.runtime.final_v5_archive_execution_plan",
        "active_final_v5_archive_execution_module": "jarvis.runtime.final_v5_archive_execution",
        "active_product_mode_operator_module": "jarvis.runtime.product_mode_operator",
        "active_correlation_risk_model_module": "jarvis.runtime.correlation_risk_model",
        "active_stock_specific_public_evidence_module": "jarvis.runtime.stock_specific_public_evidence",
        "active_data_freshness_acquisition_gate_module": "jarvis.runtime.data_freshness_acquisition_gate",
        "active_tradable_candidate_universe_gate_module": "jarvis.runtime.tradable_candidate_universe_gate",
        "active_stock_candidate_universe_expansion_module": "jarvis.runtime.stock_candidate_universe_expansion",
        "active_cross_lane_dynamic_allocation_preflight_module": "jarvis.runtime.cross_lane_dynamic_allocation_preflight",
        "active_dynamic_quality_allocator_module": "jarvis.runtime.dynamic_quality_allocator",
        "active_data_readiness_status_module": "jarvis.runtime.data_readiness_status",
        "active_product_api_module": "jarvis.runtime.product_api",
        "active_full_system_audit_module": "jarvis.runtime.full_system_audit",
        "active_news_coverage_readiness_module": "jarvis.runtime.news_coverage_readiness",
        "active_dashboard_contract_module": "jarvis.runtime.dashboard_contract",
        "active_chat_interface_contract_module": "jarvis.runtime.chat_interface_contract",
        "active_local_server_module": "jarvis.runtime.local_server",
        "active_local_server_live_endpoint_smoke_module": "jarvis.runtime.local_server_live_endpoint_smoke",
        "active_local_browser_chat_page_module": "jarvis.runtime.local_server",
        "active_assistant_tool_registry_module": "jarvis.runtime.assistant_tool_registry",
        "active_assistant_data_source_registry_module": "jarvis.runtime.assistant_data_source_registry",
        "active_assistant_asset_lookup_module": "jarvis.runtime.assistant_asset_lookup",
        "active_assistant_market_context_module": "jarvis.runtime.assistant_market_context",
        "active_assistant_news_context_module": "jarvis.runtime.assistant_news_context",
        "active_assistant_router_module": "jarvis.runtime.assistant_router",
        "active_assistant_answer_style_module": "jarvis.runtime.assistant_router",
        "active_assistant_system_audit_module": "jarvis.runtime.assistant_system_audit",
        "active_finance_intelligence_core_module": ACTIVE_FINANCE_INTELLIGENCE_CORE_MODULE,
        "active_market_data_normalized_module": ACTIVE_MARKET_DATA_NORMALIZED_MODULE,
        "active_selected_instrument_resolver_module": ACTIVE_SELECTED_INSTRUMENT_RESOLVER_MODULE,
        "active_fx_assistant_bridge_module": ACTIVE_FX_ASSISTANT_BRIDGE_MODULE,
        "active_news_intelligence_contract_module": ACTIVE_NEWS_INTELLIGENCE_CONTRACT_MODULE,
        "active_current_runtime_fast_gate_module": ACTIVE_CURRENT_RUNTIME_FAST_GATE_MODULE,
        "active_manual_holdings_update_module": ACTIVE_MANUAL_HOLDINGS_UPDATE_MODULE,
        "active_user_runbook_module": ACTIVE_USER_RUNBOOK_MODULE,
        "active_post_app_acceptance_gate_module": ACTIVE_POST_APP_ACCEPTANCE_GATE_MODULE,
        "active_live_news_fetcher_module": ACTIVE_LIVE_NEWS_FETCHER_MODULE,
        "active_dashboard_noise_audit_module": ACTIVE_DASHBOARD_NOISE_AUDIT_MODULE,
        "active_dashboard_calm_ui_freeze_gate_module": ACTIVE_DASHBOARD_CALM_UI_FREEZE_GATE_MODULE,
        "active_jarvis_session_memory_module": ACTIVE_JARVIS_SESSION_MEMORY_MODULE,
        "active_voice_briefing_module": ACTIVE_VOICE_BRIEFING_MODULE,
        "active_what_changed_since_last_time_module": ACTIVE_WHAT_CHANGED_SINCE_LAST_TIME_MODULE,
        "active_local_app_packaging_polish_module": ACTIVE_LOCAL_APP_PACKAGING_POLISH_MODULE,
        "active_final_safe_jarvis_experience_gate_module": ACTIVE_FINAL_SAFE_JARVIS_EXPERIENCE_GATE_MODULE,
        "active_jarvis_experience_parity_gate_module": ACTIVE_JARVIS_EXPERIENCE_PARITY_GATE_MODULE,
        "active_finance_database_universe_module": ACTIVE_FINANCE_DATABASE_UNIVERSE_MODULE,
        "active_finance_toolkit_fundamentals_module": ACTIVE_FINANCE_TOOLKIT_FUNDAMENTALS_MODULE,
        "active_universe_explorer_module": ACTIVE_UNIVERSE_EXPLORER_MODULE,
        "active_portfolio_health_report_card_module": ACTIVE_PORTFOLIO_HEALTH_REPORT_CARD_MODULE,
        "active_premium_orbital_design_system_module": ACTIVE_PREMIUM_ORBITAL_DESIGN_SYSTEM_MODULE,
        "active_premium_command_center_dashboard_module": ACTIVE_PREMIUM_COMMAND_CENTER_DASHBOARD_MODULE,
        "execution_forbidden": True,
        "manual_approval_required": True,
        "current_operator_surface": CURRENT_OPERATOR_SURFACE,
        "default_evidence_pack_path": DEFAULT_EVIDENCE_PACK_PATH,
        "recommended_next_stage": WEEKLY_PACKET_NEXT_STAGE,
    }


def build_current_operator_result(**kwargs: Any) -> FreeResearchCacheEvidencePackBridgeResult:
    """Build the current daily/evidence operator result through the stable runtime facade."""

    return build_free_research_cache_evidence_pack_bridge_result(**kwargs)


def format_current_operator_result(result: FreeResearchCacheEvidencePackBridgeResult) -> str:
    """Format the current daily/evidence operator result through the stable runtime facade."""

    return format_free_research_cache_evidence_pack_bridge(result)


from jarvis.runtime.daily_operator import main as _daily_operator_main
from jarvis.runtime.final_product_acceptance_gate import build_final_product_acceptance_gate_result, format_final_product_acceptance_gate
from jarvis.runtime.etf_identity_resolver import main as _etf_identity_resolver_main
from jarvis.runtime.live_news_ui_acceptance_gate import main as _live_news_ui_acceptance_gate_main

def main(argv: list[str] | None = None) -> int:
    """Run the stable active J.A.R.V.I.S. operator surface."""

    args = list(sys.argv[1:] if argv is None else argv)
    if "--local-server-live-smoke" in args:
        return _local_server_live_endpoint_smoke_main(args)
    if "--assistant-tool-registry" in args:
        return _assistant_tool_registry_main(args)
    if "--assistant-data-sources" in args:
        return _assistant_data_source_registry_main(args)
    if "--assistant-asset-lookup" in args:
        return _assistant_asset_lookup_main(args)
    if "--public-data-provider-registry" in args:
        from jarvis.runtime.public_data_provider_registry import main as _public_data_provider_registry_main
        provider_args = [arg for arg in args if arg != "--public-data-provider-registry"]
        return _public_data_provider_registry_main(provider_args)
    if "--assistant-market-data-bridge" in args:
        from jarvis.runtime.assistant_market_data_bridge import main as _assistant_market_data_bridge_main
        bridge_args = [arg for arg in args if arg != "--assistant-market-data-bridge"]
        return _assistant_market_data_bridge_main(bridge_args)
    if "--assistant-market-context" in args:
        return _assistant_market_context_main(args)
    if "--assistant-news-context" in args:
        return _assistant_news_context_main(args)
    if "--assistant-router" in args:
        return _assistant_router_main(args)
    if "--assistant-system-audit" in args:
        return _assistant_system_audit_main(args)
    if "--etf-identity-resolver" in args:
        return _etf_identity_resolver_main(args)
    if "--public-universe-quote-fetch" in args:
        from jarvis.runtime.public_universe_quote_fetcher import main as _public_universe_quote_fetch_main
        quote_args = [arg for arg in args if arg != "--public-universe-quote-fetch"]
        return _public_universe_quote_fetch_main(quote_args)
    if "--public-universe-data-coverage" in args:
        from jarvis.runtime.public_universe_data_coverage import main as _public_universe_data_coverage_main
        coverage_args = [arg for arg in args if arg != "--public-universe-data-coverage"]
        return _public_universe_data_coverage_main(coverage_args)
    if "--finance-intelligence-core" in args:
        return _finance_intelligence_core_main(args)
    if "--current-runtime-fast-gate" in args:
        return _current_runtime_fast_gate_main(args)
    if "--market-data-normalized" in args:
        return _market_data_normalized_main(args)
    if "--selected-instrument-resolver" in args:
        return _selected_instrument_resolver_main(args)
    if "--fx-assistant-bridge" in args:
        return _fx_assistant_bridge_main(args)
    if "--news-intelligence-contract" in args:
        return _news_intelligence_contract_main(args)
    if "--local-server" in args or "--local-server-smoke" in args:
        return _local_server_main(args)
    if "--ask" in args:
        return _chat_interface_contract_main(args)
    if "--chat-interface" in args:
        return _chat_interface_contract_main(args)
    if "--daily-operator" in args:
        return _daily_operator_main(args)

    if "--live-news-ui-acceptance-gate" in args:
        return _live_news_ui_acceptance_gate_main(args)

    if "--post-app-acceptance-gate" in args:
        return _post_app_acceptance_gate_main(args)

    if "--live-news-fetch" in args or "--live-news-status" in args:
        return _live_news_fetcher_main(args)

    if "--dashboard-noise-audit" in args:
        return _dashboard_noise_audit_main(args)

    if "--dashboard-calm-ui-freeze-gate" in args:
        return _dashboard_calm_ui_freeze_gate_main(args)

    if any(
        flag in args
        for flag in (
            "--session-memory-status",
            "--session-memory-write-snapshot",
            "--session-memory-summary",
        )
    ):
        return _jarvis_session_memory_main(args)

    if "--voice-briefing" in args or "--voice-briefing-text" in args or "--voice-briefing-speak" in args:
        return _voice_briefing_main(args)

    if "--what-changed" in args:
        return _what_changed_since_last_time_main(args)

    if "--local-app-packaging-polish" in args:
        return _local_app_packaging_polish_main(args)

    if "--final-safe-jarvis-experience-gate" in args:
        return _final_safe_jarvis_experience_gate_main(args)

    if "--jarvis-experience-parity-gate" in args:
        return _jarvis_experience_parity_gate_main(args)

    if "--finance-database-universe" in args:
        return _finance_database_universe_main(args)

    if "--finance-toolkit-fundamentals" in args:
        return _finance_toolkit_fundamentals_main(args)

    if "--universe-explorer" in args:
        return _universe_explorer_main(args)

    if "--portfolio-health-report-card" in args:
        return _portfolio_health_report_card_main(args)

    if "--premium-orbital-design-system" in args:
        return _premium_orbital_design_system_main(args)

    if "--command-center-dashboard" in args:
        return _premium_command_center_dashboard_main(args)

    if "--user-runbook" in args:
        return _user_runbook_main(args)

    if any(
        flag in args
        for flag in (
            "--holdings-template",
            "--write-holdings-template",
            "--holdings-status",
        )
    ):
        return _manual_holdings_update_main(args)

    if "--final-product-acceptance-gate" in args:
        current_date = "2026-06-20"
        if "--current-date" in args:
            idx = args.index("--current-date")
            if idx + 1 < len(args):
                current_date = args[idx + 1]
        result = build_final_product_acceptance_gate_result(current_date=current_date)
        print(format_final_product_acceptance_gate(result))
        return 0 if result.final_acceptance_ready else 1

    if "--dashboard-contract" in args:
        return _dashboard_contract_main(args)
    if "--news-coverage-readiness" in args:
        return _news_coverage_readiness_main(args)
    if "--full-system-audit" in args:
        return _full_system_audit_main(args)
    if "--product-api-status" in args:
        return _product_api_main(args)
    if "--data-readiness-status" in args:
        return _data_readiness_status_main(args)
    if "--multi-candidate-instrument-selector" in args:
        return _multi_candidate_instrument_selector_main(args)
    if "--dynamic-quality-allocator" in args:
        return _dynamic_quality_allocator_main(args)
    if "--cross-lane-dynamic-allocation-preflight" in args:
        return _cross_lane_dynamic_allocation_preflight_main(args)
    if "--stock-candidate-universe-expansion" in args:
        return _stock_candidate_universe_expansion_main(args)
    if "--tradable-candidate-universe-gate" in args:
        return _tradable_candidate_universe_gate_main(args)
    if "--data-freshness-acquisition-gate" in args:
        return _data_freshness_acquisition_gate_main(args)
    if "--stock-specific-public-evidence" in args:
        return _stock_specific_public_evidence_main(args)
    if "--correlation-risk-model" in args:
        return _correlation_risk_model_main(args)
    if any(flag in args for flag in ("--today", "--week", "--status", "--product-mode")):
        return _product_mode_operator_main(args)
    if any(
        flag in args
        for flag in (
            "--manual-portfolio-snapshot-intake",
            "--manual-portfolio-snapshot-template",
            "--write-manual-portfolio-snapshot-template",
        )
    ):
        return _manual_portfolio_snapshot_main(args)
    if any(flag in args for flag in ("--monthly-expenses-intake", "--write-monthly-expenses-template")):
        return _monthly_expenses_intake_main(args)
    if any(flag in args for flag in ("--platform-data-completeness-gate", "--write-platform-data-templates")):
        return _platform_data_completeness_gate_main(args)
    if "--import-closure-safe-archive-plan" in args or "--write-import-closure-safe-archive-plan" in args:
        return _import_closure_safe_archive_plan_main(args)
    if "--active-runtime-surface-redundancy-audit" in args or "--write-active-runtime-surface-audit" in args:
        return _active_runtime_surface_redundancy_audit_main(args)
    if "--manual-cost-basis-intake" in args or "--write-manual-cost-basis-template" in args:
        return _manual_cost_basis_intake_main(args)
    if "--personal-finance-contribution-bridge" in args:
        return _personal_finance_contribution_bridge_main(args)
    if "--weekly-platform-action-packet" in args:
        return _platform_weekly_action_packet_main(args)
    if "--platform-lane-policy" in args:
        return _platform_lane_policy_main(args)
    if "--dynamic-target-policy" in args:
        return _dynamic_target_policy_main(args)
    if "--portfolio-exposure-audit" in args:
        return _portfolio_exposure_audit_main(args)
    if "--allocation-strategy-audit" in args:
        return _allocation_strategy_audit_main(args)
    if "--weekly-buy-prep" in args:
        return _weekly_packet_main(args)
    return _v45_main(args)


__all__ = [
    "ACTIVE_ALLOCATION_STRATEGY_AUDIT_MODULE",
    "ACTIVE_CURRENT_RUNTIME_FAST_GATE_MODULE",
    "ACTIVE_FINANCE_INTELLIGENCE_CORE_MODULE",
    "ACTIVE_FX_ASSISTANT_BRIDGE_MODULE",
    "ACTIVE_MANUAL_PORTFOLIO_SNAPSHOT_MODULE",
    "ACTIVE_MARKET_DATA_NORMALIZED_MODULE",
    "ACTIVE_MONTHLY_EXPENSES_INTAKE_MODULE",
    "ACTIVE_NEWS_INTELLIGENCE_CONTRACT_MODULE",
    "ACTIVE_MANUAL_HOLDINGS_UPDATE_MODULE",
    "ACTIVE_USER_RUNBOOK_MODULE",
    "ACTIVE_POST_APP_ACCEPTANCE_GATE_MODULE",
    "ACTIVE_LIVE_NEWS_FETCHER_MODULE",
    "ACTIVE_DASHBOARD_NOISE_AUDIT_MODULE",
    "ACTIVE_DASHBOARD_CALM_UI_FREEZE_GATE_MODULE",
    "ACTIVE_JARVIS_SESSION_MEMORY_MODULE",
    "ACTIVE_VOICE_BRIEFING_MODULE",
    "ACTIVE_WHAT_CHANGED_SINCE_LAST_TIME_MODULE",
    "ACTIVE_LOCAL_APP_PACKAGING_POLISH_MODULE",
    "ACTIVE_FINAL_SAFE_JARVIS_EXPERIENCE_GATE_MODULE",
    "ACTIVE_JARVIS_EXPERIENCE_PARITY_GATE_MODULE",
    "ACTIVE_FINANCE_DATABASE_UNIVERSE_MODULE",
    "ACTIVE_FINANCE_TOOLKIT_FUNDAMENTALS_MODULE",
    "ACTIVE_UNIVERSE_EXPLORER_MODULE",
    "ACTIVE_PORTFOLIO_HEALTH_REPORT_CARD_MODULE",
    "ACTIVE_PREMIUM_ORBITAL_DESIGN_SYSTEM_MODULE",
    "ACTIVE_PREMIUM_COMMAND_CENTER_DASHBOARD_MODULE",
    "ACTIVE_PLATFORM_DATA_COMPLETENESS_GATE_MODULE",
    "ACTIVE_RUNTIME_MODULE",
    "ACTIVE_SELECTED_INSTRUMENT_RESOLVER_MODULE",
    "ACTIVE_LIVE_NEWS_UI_ACCEPTANCE_GATE_MODULE",
    "ACTIVE_RUNTIME_STAGE",
    "ACTIVE_WEEKLY_PACKET_MODULE",
    "CURRENT_OPERATOR_SURFACE",
    "DEFAULT_EVIDENCE_PACK_PATH",
    "EVIDENCE_BLOCKED",
    "EVIDENCE_READY",
    "EVIDENCE_REVIEW_REQUIRED",
    "FreeResearchCacheEvidencePackBridgeResult",
    "STATUS_BLOCKED",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "STABLE_RUNTIME_FACADE",
    "V45_NEXT_STAGE",
    "WEEKLY_PACKET_NEXT_STAGE",
    "build_current_operator_result",
    "build_weekly_manual_buy_packet_result",
    "format_current_operator_result",
    "format_weekly_manual_buy_packet",
    "get_active_runtime_surface",
    "main",
]






