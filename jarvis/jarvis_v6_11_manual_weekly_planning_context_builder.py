"""J.A.R.V.I.S. v6.11 manual weekly planning context builder.

This stage converts active-policy snapshot gaps into manual weekly planning context.

Safety boundary:
- planning context only
- no recommended order
- no asset approval
- no weekly buy ticket
- no buy request creation
- no broker/API execution
- no trades
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v6_10_active_policy_snapshot_gap_analyzer import (
    GAP_ABOVE_PREFERRED,
    GAP_BELOW_PREFERRED,
    GAP_OVER_MAX,
    GAP_UNDER_MIN,
    ActivePolicySleeveGap,
    audit_v6_10_active_policy_snapshot_gap_analyzer,
)


STATUS_READY = "JARVIS_V6_11_MANUAL_WEEKLY_PLANNING_CONTEXT_BUILDER_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_11_MANUAL_WEEKLY_PLANNING_CONTEXT_BUILDER_BLOCKED_SAFE"

NEXT_STAGE = "v6.12_manual_weekly_candidate_shortlist_builder"

CONTEXT_PRIORITY_CRITICAL = "CRITICAL"
CONTEXT_PRIORITY_HIGH = "HIGH"
CONTEXT_PRIORITY_MEDIUM = "MEDIUM"
CONTEXT_PRIORITY_LOW = "LOW"

CONTEXT_ACTION_MONITOR_ONLY = "MONITOR_ONLY"
CONTEXT_ACTION_CONSIDER_FUTURE_ALLOCATION = "CONSIDER_FUTURE_ALLOCATION"
CONTEXT_ACTION_AVOID_ADDITIONAL_EXPOSURE = "AVOID_ADDITIONAL_EXPOSURE"

SLEEVE_CASH_DEFENSIVE = "cash_defensive"
SLEEVE_CRYPTO_CORE_BTC = "crypto_core_btc"
SLEEVE_CRYPTO_SPECULATIVE = "crypto_speculative"


@dataclass(frozen=True)
class ManualPlanningContextItem:
    context_id: str
    sleeve_id: str
    gap_status: str
    priority: str
    context_action: str
    rationale: str
    current_weight_pct: float
    preferred_low_pct: float
    preferred_high_pct: float
    max_pct: float
    investable_cash_considered: bool
    protected_cash_guard_active: bool
    crypto_ceiling_guard_active: bool
    creates_weekly_buy_ticket: bool
    creates_buy_request: bool
    executes_trade: bool

    def is_crypto_context(self) -> bool:
        return self.sleeve_id in {SLEEVE_CRYPTO_CORE_BTC, SLEEVE_CRYPTO_SPECULATIVE}

    def safe_context_only(self) -> bool:
        return (
            not self.creates_weekly_buy_ticket
            and not self.creates_buy_request
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "sleeve_id": self.sleeve_id,
            "gap_status": self.gap_status,
            "priority": self.priority,
            "context_action": self.context_action,
            "rationale": self.rationale,
            "current_weight_pct": self.current_weight_pct,
            "preferred_low_pct": self.preferred_low_pct,
            "preferred_high_pct": self.preferred_high_pct,
            "max_pct": self.max_pct,
            "investable_cash_considered": self.investable_cash_considered,
            "protected_cash_guard_active": self.protected_cash_guard_active,
            "crypto_ceiling_guard_active": self.crypto_ceiling_guard_active,
            "creates_weekly_buy_ticket": self.creates_weekly_buy_ticket,
            "creates_buy_request": self.creates_buy_request,
            "executes_trade": self.executes_trade,
            "is_crypto_context": self.is_crypto_context(),
            "safe_context_only": self.safe_context_only(),
        }


@dataclass(frozen=True)
class ManualWeeklyPlanningContextResult:
    status: str
    recommended_next_stage: str
    analyzed_policy_id: str
    source_sleeve_gap_count: int
    planning_context_item_count: int
    critical_priority_count: int
    high_priority_count: int
    medium_priority_count: int
    low_priority_count: int
    investable_cash_eur: float
    protected_cash_eur: float
    cash_available_for_future_manual_planning: bool
    protected_cash_guard_active: bool
    crypto_ceiling_guard_active: bool
    planning_items: tuple[ManualPlanningContextItem, ...]
    manual_planning_notes: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    weekly_planning_context_ready: bool
    context_only: bool
    asset_approval_deferred: bool
    weekly_buy_ticket_deferred: bool
    buy_request_deferred: bool
    broker_execution_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "analyzed_policy_id": self.analyzed_policy_id,
            "source_sleeve_gap_count": self.source_sleeve_gap_count,
            "planning_context_item_count": self.planning_context_item_count,
            "critical_priority_count": self.critical_priority_count,
            "high_priority_count": self.high_priority_count,
            "medium_priority_count": self.medium_priority_count,
            "low_priority_count": self.low_priority_count,
            "investable_cash_eur": self.investable_cash_eur,
            "protected_cash_eur": self.protected_cash_eur,
            "cash_available_for_future_manual_planning": self.cash_available_for_future_manual_planning,
            "protected_cash_guard_active": self.protected_cash_guard_active,
            "crypto_ceiling_guard_active": self.crypto_ceiling_guard_active,
            "planning_items": [item.to_dict() for item in self.planning_items],
            "manual_planning_notes": list(self.manual_planning_notes),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "weekly_planning_context_ready": self.weekly_planning_context_ready,
            "context_only": self.context_only,
            "asset_approval_deferred": self.asset_approval_deferred,
            "weekly_buy_ticket_deferred": self.weekly_buy_ticket_deferred,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _priority_for_gap(gap: ActivePolicySleeveGap) -> str:
    if gap.gap_status in {GAP_OVER_MAX, GAP_UNDER_MIN}:
        return CONTEXT_PRIORITY_CRITICAL
    if gap.gap_status in {GAP_BELOW_PREFERRED, GAP_ABOVE_PREFERRED}:
        return CONTEXT_PRIORITY_HIGH
    return CONTEXT_PRIORITY_LOW


def _context_action_for_gap(gap: ActivePolicySleeveGap) -> str:
    if gap.gap_status in {GAP_UNDER_MIN, GAP_BELOW_PREFERRED}:
        return CONTEXT_ACTION_CONSIDER_FUTURE_ALLOCATION
    if gap.gap_status in {GAP_OVER_MAX, GAP_ABOVE_PREFERRED}:
        return CONTEXT_ACTION_AVOID_ADDITIONAL_EXPOSURE
    return CONTEXT_ACTION_MONITOR_ONLY


def _rationale_for_gap(gap: ActivePolicySleeveGap) -> str:
    if gap.gap_status == GAP_UNDER_MIN:
        return f"{gap.sleeve_id} is under its hard minimum and should be visible in future manual planning context."
    if gap.gap_status == GAP_BELOW_PREFERRED:
        return f"{gap.sleeve_id} is below preferred range and may deserve future manual allocation consideration."
    if gap.gap_status == GAP_OVER_MAX:
        return f"{gap.sleeve_id} is above hard maximum; future manual planning should avoid adding exposure."
    if gap.gap_status == GAP_ABOVE_PREFERRED:
        return f"{gap.sleeve_id} is above preferred range; future manual planning should slow or pause additions."
    return f"{gap.sleeve_id} is inside preferred range and can be monitored."


def build_manual_planning_context_items(
    sleeve_gaps: tuple[ActivePolicySleeveGap, ...],
    investable_cash_eur: float,
    protected_cash_eur: float,
) -> tuple[ManualPlanningContextItem, ...]:
    cash_available = investable_cash_eur > 0.0
    protected_cash_guard_active = protected_cash_eur > 0.0

    items: list[ManualPlanningContextItem] = []
    for gap in sleeve_gaps:
        crypto_ceiling_guard_active = gap.sleeve_id in {
            SLEEVE_CRYPTO_CORE_BTC,
            SLEEVE_CRYPTO_SPECULATIVE,
        }
        items.append(
            ManualPlanningContextItem(
                context_id=f"context_{gap.sleeve_id}",
                sleeve_id=gap.sleeve_id,
                gap_status=gap.gap_status,
                priority=_priority_for_gap(gap),
                context_action=_context_action_for_gap(gap),
                rationale=_rationale_for_gap(gap),
                current_weight_pct=gap.current_weight_pct,
                preferred_low_pct=gap.preferred_low_pct,
                preferred_high_pct=gap.preferred_high_pct,
                max_pct=gap.max_pct,
                investable_cash_considered=cash_available,
                protected_cash_guard_active=protected_cash_guard_active,
                crypto_ceiling_guard_active=crypto_ceiling_guard_active,
                creates_weekly_buy_ticket=False,
                creates_buy_request=False,
                executes_trade=False,
            )
        )

    return tuple(items)


def audit_v6_11_manual_weekly_planning_context_builder(
    planning_items: tuple[ManualPlanningContextItem, ...] | None = None,
) -> ManualWeeklyPlanningContextResult:
    gap_result = audit_v6_10_active_policy_snapshot_gap_analyzer()

    effective_items = (
        build_manual_planning_context_items(
            gap_result.sleeve_gaps,
            gap_result.investable_cash_eur,
            gap_result.protected_cash_eur,
        )
        if planning_items is None
        else planning_items
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.11 creates manual weekly planning context only.",
        "Planning context may rank sleeve attention, but creates no buy ticket.",
        "No buy request, broker action, or trade is created.",
    ]

    if gap_result.blockers:
        blockers.append("Source active-policy snapshot gap analyzer is blocked.")
    if not gap_result.sleeve_gaps:
        blockers.append("No sleeve gaps are available for planning context.")
    if not effective_items:
        blockers.append("No manual planning context items were created.")

    context_ids = [item.context_id for item in effective_items]
    if len(context_ids) != len(set(context_ids)):
        blockers.append("Manual planning context IDs must be unique.")

    source_sleeve_ids = {gap.sleeve_id for gap in gap_result.sleeve_gaps}
    context_sleeve_ids = {item.sleeve_id for item in effective_items}

    missing_context = source_sleeve_ids - context_sleeve_ids
    for sleeve_id in sorted(missing_context):
        blockers.append(f"Missing manual planning context for sleeve: {sleeve_id}")

    unknown_context = context_sleeve_ids - source_sleeve_ids
    for sleeve_id in sorted(unknown_context):
        blockers.append(f"Manual planning context references unknown sleeve: {sleeve_id}")

    critical_count = sum(1 for item in effective_items if item.priority == CONTEXT_PRIORITY_CRITICAL)
    high_count = sum(1 for item in effective_items if item.priority == CONTEXT_PRIORITY_HIGH)
    medium_count = sum(1 for item in effective_items if item.priority == CONTEXT_PRIORITY_MEDIUM)
    low_count = sum(1 for item in effective_items if item.priority == CONTEXT_PRIORITY_LOW)

    if critical_count < 1:
        warnings.append("No critical context item detected.")
    if high_count < 1:
        warnings.append("No high-priority context item detected.")

    for item in effective_items:
        if not item.rationale.strip():
            blockers.append(f"{item.context_id}: rationale is required.")
        if not item.safe_context_only():
            blockers.append(f"{item.context_id}: planning context must remain context-only.")
        if item.creates_weekly_buy_ticket:
            blockers.append(f"{item.context_id}: weekly buy ticket creation is forbidden in v6.11.")
        if item.creates_buy_request:
            blockers.append(f"{item.context_id}: buy request creation is forbidden in v6.11.")
        if item.executes_trade:
            blockers.append(f"{item.context_id}: trade execution is forbidden in v6.11.")
        if item.is_crypto_context() and not item.crypto_ceiling_guard_active:
            blockers.append(f"{item.context_id}: crypto ceiling guard must be active for crypto context.")
        if item.sleeve_id == SLEEVE_CASH_DEFENSIVE and not item.protected_cash_guard_active:
            warnings.append(f"{item.context_id}: protected cash guard is not active.")

    cash_available = gap_result.investable_cash_eur > 0.0
    protected_cash_guard_active = gap_result.protected_cash_eur > 0.0
    crypto_ceiling_guard_active = any(item.crypto_ceiling_guard_active for item in effective_items)

    manual_planning_notes = (
        "Use active policy gaps as manual planning context only.",
        "Protected cash is not investable.",
        "BTC can be considered in future manual planning only if crypto ceiling and cash rules allow.",
        "Cash over-max context does not automatically authorize investment.",
        "No weekly buy ticket exists in v6.11.",
    )

    safety_flags = {
        "weekly_planning_context_ready": False,
        "context_only": True,
        "asset_approval_deferred": True,
        "weekly_buy_ticket_deferred": True,
        "buy_request_deferred": True,
        "broker_execution_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["context_only"]:
        blockers.append("v6.11 must remain context-only.")
    if not safety_flags["asset_approval_deferred"]:
        blockers.append("v6.11 must defer asset approval.")
    if not safety_flags["weekly_buy_ticket_deferred"]:
        blockers.append("v6.11 must defer weekly buy tickets.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v6.11 must defer buy requests.")
    if not safety_flags["broker_execution_forbidden"]:
        blockers.append("v6.11 must forbid broker execution.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.11 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))

    return ManualWeeklyPlanningContextResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        analyzed_policy_id=gap_result.analyzed_policy_id,
        source_sleeve_gap_count=gap_result.sleeve_gap_count,
        planning_context_item_count=len(effective_items),
        critical_priority_count=critical_count,
        high_priority_count=high_count,
        medium_priority_count=medium_count,
        low_priority_count=low_count,
        investable_cash_eur=gap_result.investable_cash_eur,
        protected_cash_eur=gap_result.protected_cash_eur,
        cash_available_for_future_manual_planning=cash_available,
        protected_cash_guard_active=protected_cash_guard_active,
        crypto_ceiling_guard_active=crypto_ceiling_guard_active,
        planning_items=effective_items,
        manual_planning_notes=manual_planning_notes,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "weekly_planning_context_ready": not unique_blockers},
    )
