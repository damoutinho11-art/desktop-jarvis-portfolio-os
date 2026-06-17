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
ACTIVE_RUNTIME_STAGE = "v52.0"
STABLE_RUNTIME_FACADE = "jarvis.runtime.operator"
CURRENT_OPERATOR_SURFACE = "manual_portfolio_snapshot_intake_and_allocation_audit"


def get_active_runtime_surface() -> dict[str, str]:
    """Return the current stable-to-versioned runtime mapping."""

    return {
        "stable_runtime_facade": STABLE_RUNTIME_FACADE,
        "active_runtime_module": ACTIVE_RUNTIME_MODULE,
        "active_weekly_packet_module": ACTIVE_WEEKLY_PACKET_MODULE,
        "active_allocation_strategy_audit_module": ACTIVE_ALLOCATION_STRATEGY_AUDIT_MODULE,
        "active_manual_portfolio_snapshot_module": ACTIVE_MANUAL_PORTFOLIO_SNAPSHOT_MODULE,
        "active_runtime_stage": ACTIVE_RUNTIME_STAGE,
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
    if any(
        flag in args
        for flag in (
            "--manual-portfolio-snapshot-intake",
            "--manual-portfolio-snapshot-template",
            "--write-manual-portfolio-snapshot-template",
        )
    ):
        return _manual_portfolio_snapshot_main(args)
    if "--allocation-strategy-audit" in args:
        return _allocation_strategy_audit_main(args)
    if "--weekly-buy-prep" in args:
        return _weekly_packet_main(args)
    return _v45_main(args)


__all__ = [
    "ACTIVE_ALLOCATION_STRATEGY_AUDIT_MODULE",
    "ACTIVE_MANUAL_PORTFOLIO_SNAPSHOT_MODULE",
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