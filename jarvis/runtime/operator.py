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
ACTIVE_RUNTIME_STAGE = "v92.0"
STABLE_RUNTIME_FACADE = "jarvis.runtime.operator"
CURRENT_OPERATOR_SURFACE = "product_mode_instrument_selector_integration"
ACTIVE_PLATFORM_DATA_COMPLETENESS_GATE_MODULE = "jarvis.runtime.platform_data_completeness_gate"
ACTIVE_MONTHLY_EXPENSES_INTAKE_MODULE = "jarvis.runtime.monthly_expenses_intake"


def get_active_runtime_surface() -> dict[str, str]:
    """Return the current stable-to-versioned runtime mapping."""

    return {
        "stable_runtime_facade": STABLE_RUNTIME_FACADE,
        "active_runtime_module": ACTIVE_RUNTIME_MODULE,
        "active_weekly_packet_module": ACTIVE_WEEKLY_PACKET_MODULE,
        "active_allocation_strategy_audit_module": ACTIVE_ALLOCATION_STRATEGY_AUDIT_MODULE,
        "active_manual_portfolio_snapshot_module": ACTIVE_MANUAL_PORTFOLIO_SNAPSHOT_MODULE,
        "active_runtime_stage": ACTIVE_RUNTIME_STAGE,
        "active_portfolio_exposure_audit_module": "jarvis.runtime.portfolio_exposure_audit",
        "active_dynamic_target_policy_module": "jarvis.runtime.dynamic_target_policy",
        "active_platform_lane_policy_module": "jarvis.runtime.platform_lane_policy",
        "active_platform_weekly_action_packet_module": "jarvis.runtime.platform_weekly_action_packet",
        "active_platform_data_completeness_gate_module": ACTIVE_PLATFORM_DATA_COMPLETENESS_GATE_MODULE,
        "active_monthly_expenses_intake_module": ACTIVE_MONTHLY_EXPENSES_INTAKE_MODULE,
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


def main(argv: list[str] | None = None) -> int:
    """Run the stable active J.A.R.V.I.S. operator surface."""

    args = list(sys.argv[1:] if argv is None else argv)
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
    "ACTIVE_MANUAL_PORTFOLIO_SNAPSHOT_MODULE",
    "ACTIVE_MONTHLY_EXPENSES_INTAKE_MODULE",
    "ACTIVE_PLATFORM_DATA_COMPLETENESS_GATE_MODULE",
    "ACTIVE_PLATFORM_DATA_COMPLETENESS_GATE_MODULE",
    "ACTIVE_RUNTIME_MODULE",
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