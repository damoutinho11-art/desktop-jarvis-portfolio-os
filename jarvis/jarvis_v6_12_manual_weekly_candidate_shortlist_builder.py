"""J.A.R.V.I.S. v6.12 manual weekly candidate shortlist builder.

This stage converts manual weekly planning context into a shortlist of candidate
sleeves/assets for human review.

Safety boundary:
- shortlist only
- no final recommendation
- no asset approval
- no weekly buy ticket
- no buy request creation
- no broker/API execution
- no trades
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v6_9_active_policy_registry import audit_v6_9_active_policy_registry
from .jarvis_v6_11_manual_weekly_planning_context_builder import (
    CONTEXT_ACTION_CONSIDER_FUTURE_ALLOCATION,
    CONTEXT_PRIORITY_CRITICAL,
    CONTEXT_PRIORITY_HIGH,
    ManualPlanningContextItem,
    audit_v6_11_manual_weekly_planning_context_builder,
)


STATUS_READY = "JARVIS_V6_12_MANUAL_WEEKLY_CANDIDATE_SHORTLIST_BUILDER_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_12_MANUAL_WEEKLY_CANDIDATE_SHORTLIST_BUILDER_BLOCKED_SAFE"

NEXT_STAGE = "v6.13_manual_weekly_shortlist_review_queue"

SHORTLIST_STATUS_MANUAL_REVIEW_REQUIRED = "SHORTLIST_MANUAL_REVIEW_REQUIRED"
SHORTLIST_STATUS_BLOCKED = "SHORTLIST_BLOCKED"

REASON_UNDER_MIN = "POLICY_UNDER_MIN"
REASON_BELOW_PREFERRED = "POLICY_BELOW_PREFERRED"
REASON_INVESTABLE_CASH_AVAILABLE = "INVESTABLE_CASH_AVAILABLE"
REASON_PROTECTED_CASH_GUARD_ACTIVE = "PROTECTED_CASH_GUARD_ACTIVE"
REASON_CRYPTO_CEILING_GUARD_ACTIVE = "CRYPTO_CEILING_GUARD_ACTIVE"
REASON_ACTIVE_POLICY_SELECTED_ASSET = "ACTIVE_POLICY_SELECTED_ASSET"

SLEEVE_CRYPTO_CORE_BTC = "crypto_core_btc"
SLEEVE_CRYPTO_SPECULATIVE = "crypto_speculative"


@dataclass(frozen=True)
class ManualWeeklyShortlistCandidate:
    shortlist_id: str
    rank: int
    sleeve_id: str
    candidate_id: str
    candidate_role: str
    quality_status: str
    source_context_id: str
    source_priority: str
    source_gap_status: str
    shortlist_status: str
    reason_codes: tuple[str, ...]
    constraints: tuple[str, ...]
    manual_review_required: bool
    shortlisted_for_manual_review: bool
    final_recommendation_created: bool
    asset_approved: bool
    creates_weekly_buy_ticket: bool
    creates_buy_request: bool
    connects_broker: bool
    executes_trade: bool

    def is_crypto_candidate(self) -> bool:
        return self.sleeve_id in {SLEEVE_CRYPTO_CORE_BTC, SLEEVE_CRYPTO_SPECULATIVE}

    def safe_shortlist_only(self) -> bool:
        return (
            self.manual_review_required
            and self.shortlisted_for_manual_review
            and not self.final_recommendation_created
            and not self.asset_approved
            and not self.creates_weekly_buy_ticket
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "shortlist_id": self.shortlist_id,
            "rank": self.rank,
            "sleeve_id": self.sleeve_id,
            "candidate_id": self.candidate_id,
            "candidate_role": self.candidate_role,
            "quality_status": self.quality_status,
            "source_context_id": self.source_context_id,
            "source_priority": self.source_priority,
            "source_gap_status": self.source_gap_status,
            "shortlist_status": self.shortlist_status,
            "reason_codes": list(self.reason_codes),
            "constraints": list(self.constraints),
            "manual_review_required": self.manual_review_required,
            "shortlisted_for_manual_review": self.shortlisted_for_manual_review,
            "final_recommendation_created": self.final_recommendation_created,
            "asset_approved": self.asset_approved,
            "creates_weekly_buy_ticket": self.creates_weekly_buy_ticket,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "executes_trade": self.executes_trade,
            "is_crypto_candidate": self.is_crypto_candidate(),
            "safe_shortlist_only": self.safe_shortlist_only(),
        }


@dataclass(frozen=True)
class ManualWeeklyCandidateShortlistResult:
    status: str
    recommended_next_stage: str
    analyzed_policy_id: str
    source_planning_context_item_count: int
    shortlist_candidate_count: int
    critical_source_count: int
    high_source_count: int
    crypto_shortlist_count: int
    manual_review_required_count: int
    investable_cash_eur: float
    protected_cash_eur: float
    shortlist_candidates: tuple[ManualWeeklyShortlistCandidate, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    manual_weekly_shortlist_ready: bool
    shortlist_only: bool
    final_recommendation_deferred: bool
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
            "source_planning_context_item_count": self.source_planning_context_item_count,
            "shortlist_candidate_count": self.shortlist_candidate_count,
            "critical_source_count": self.critical_source_count,
            "high_source_count": self.high_source_count,
            "crypto_shortlist_count": self.crypto_shortlist_count,
            "manual_review_required_count": self.manual_review_required_count,
            "investable_cash_eur": self.investable_cash_eur,
            "protected_cash_eur": self.protected_cash_eur,
            "shortlist_candidates": [candidate.to_dict() for candidate in self.shortlist_candidates],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "manual_weekly_shortlist_ready": self.manual_weekly_shortlist_ready,
            "shortlist_only": self.shortlist_only,
            "final_recommendation_deferred": self.final_recommendation_deferred,
            "asset_approval_deferred": self.asset_approval_deferred,
            "weekly_buy_ticket_deferred": self.weekly_buy_ticket_deferred,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _priority_sort_key(item: ManualPlanningContextItem) -> tuple[int, str]:
    priority_order = {
        CONTEXT_PRIORITY_CRITICAL: 0,
        CONTEXT_PRIORITY_HIGH: 1,
    }
    return (priority_order.get(item.priority, 9), item.sleeve_id)


def _reason_codes_for_context(item: ManualPlanningContextItem) -> tuple[str, ...]:
    codes: list[str] = [REASON_ACTIVE_POLICY_SELECTED_ASSET]

    if item.gap_status == "UNDER_MIN":
        codes.append(REASON_UNDER_MIN)
    if item.gap_status == "BELOW_PREFERRED":
        codes.append(REASON_BELOW_PREFERRED)
    if item.investable_cash_considered:
        codes.append(REASON_INVESTABLE_CASH_AVAILABLE)
    if item.protected_cash_guard_active:
        codes.append(REASON_PROTECTED_CASH_GUARD_ACTIVE)
    if item.crypto_ceiling_guard_active:
        codes.append(REASON_CRYPTO_CEILING_GUARD_ACTIVE)

    return tuple(dict.fromkeys(codes))


def _constraints_for_context(item: ManualPlanningContextItem) -> tuple[str, ...]:
    constraints = [
        "Manual review is required before any later recommendation.",
        "This shortlist item is not a buy ticket.",
        "This shortlist item is not a buy request.",
        "Protected cash must remain non-investable.",
    ]

    if item.crypto_ceiling_guard_active:
        constraints.append("Crypto ceiling must be checked before any later manual recommendation.")
    if item.sleeve_id == SLEEVE_CRYPTO_SPECULATIVE:
        constraints.append("Speculative crypto remains excluded unless quality and policy gates improve.")

    return tuple(constraints)


def build_manual_weekly_shortlist_candidates(
    planning_items: tuple[ManualPlanningContextItem, ...],
) -> tuple[ManualWeeklyShortlistCandidate, ...]:
    active_policy_result = audit_v6_9_active_policy_registry()
    if not active_policy_result.active_policies:
        return ()

    active_policy = active_policy_result.active_policies[0]
    assets_by_sleeve: dict[str, list[Any]] = {}
    for selection in active_policy.selected_assets:
        assets_by_sleeve.setdefault(selection.sleeve_id, []).append(selection)

    source_items = tuple(
        sorted(
            (
                item
                for item in planning_items
                if item.context_action == CONTEXT_ACTION_CONSIDER_FUTURE_ALLOCATION
            ),
            key=_priority_sort_key,
        )
    )

    shortlist: list[ManualWeeklyShortlistCandidate] = []
    rank = 1
    for item in source_items:
        for selection in assets_by_sleeve.get(item.sleeve_id, []):
            shortlist.append(
                ManualWeeklyShortlistCandidate(
                    shortlist_id=f"shortlist_{rank}_{item.sleeve_id}_{selection.candidate_id}",
                    rank=rank,
                    sleeve_id=item.sleeve_id,
                    candidate_id=selection.candidate_id,
                    candidate_role=selection.role,
                    quality_status=selection.quality_status,
                    source_context_id=item.context_id,
                    source_priority=item.priority,
                    source_gap_status=item.gap_status,
                    shortlist_status=SHORTLIST_STATUS_MANUAL_REVIEW_REQUIRED,
                    reason_codes=_reason_codes_for_context(item),
                    constraints=_constraints_for_context(item),
                    manual_review_required=True,
                    shortlisted_for_manual_review=True,
                    final_recommendation_created=False,
                    asset_approved=False,
                    creates_weekly_buy_ticket=False,
                    creates_buy_request=False,
                    connects_broker=False,
                    executes_trade=False,
                )
            )
            rank += 1

    return tuple(shortlist)


def audit_v6_12_manual_weekly_candidate_shortlist_builder(
    shortlist_candidates: tuple[ManualWeeklyShortlistCandidate, ...] | None = None,
) -> ManualWeeklyCandidateShortlistResult:
    planning_result = audit_v6_11_manual_weekly_planning_context_builder()

    effective_shortlist = (
        build_manual_weekly_shortlist_candidates(planning_result.planning_items)
        if shortlist_candidates is None
        else shortlist_candidates
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.12 creates a manual weekly candidate shortlist only.",
        "Shortlisted candidates are not final recommendations.",
        "No weekly buy ticket, buy request, broker action, or trade is created.",
    ]

    if planning_result.blockers:
        blockers.append("Source manual weekly planning context builder is blocked.")
    if not planning_result.planning_items:
        blockers.append("No manual weekly planning context items are available.")
    if not effective_shortlist:
        blockers.append("No manual weekly shortlist candidates were created.")

    shortlist_ids = [candidate.shortlist_id for candidate in effective_shortlist]
    if len(shortlist_ids) != len(set(shortlist_ids)):
        blockers.append("Manual weekly shortlist IDs must be unique.")

    ranks = [candidate.rank for candidate in effective_shortlist]
    if ranks and ranks != list(range(1, len(ranks) + 1)):
        blockers.append("Manual weekly shortlist ranks must be contiguous starting at 1.")

    source_context_ids = {item.context_id for item in planning_result.planning_items}
    for candidate in effective_shortlist:
        if candidate.source_context_id not in source_context_ids:
            blockers.append(f"{candidate.shortlist_id}: source planning context is unknown.")
        if candidate.shortlist_status != SHORTLIST_STATUS_MANUAL_REVIEW_REQUIRED:
            blockers.append(f"{candidate.shortlist_id}: shortlist status must require manual review.")
        if not candidate.manual_review_required:
            blockers.append(f"{candidate.shortlist_id}: manual review is required.")
        if not candidate.shortlisted_for_manual_review:
            blockers.append(f"{candidate.shortlist_id}: candidate must be shortlisted for manual review.")
        if not candidate.reason_codes:
            blockers.append(f"{candidate.shortlist_id}: reason codes are required.")
        if not candidate.constraints:
            blockers.append(f"{candidate.shortlist_id}: constraints are required.")
        if not candidate.safe_shortlist_only():
            blockers.append(f"{candidate.shortlist_id}: shortlist candidate must remain shortlist-only.")
        if candidate.final_recommendation_created:
            blockers.append(f"{candidate.shortlist_id}: final recommendation creation is forbidden in v6.12.")
        if candidate.asset_approved:
            blockers.append(f"{candidate.shortlist_id}: asset approval is forbidden in v6.12.")
        if candidate.creates_weekly_buy_ticket:
            blockers.append(f"{candidate.shortlist_id}: weekly buy ticket creation is forbidden in v6.12.")
        if candidate.creates_buy_request:
            blockers.append(f"{candidate.shortlist_id}: buy request creation is forbidden in v6.12.")
        if candidate.connects_broker:
            blockers.append(f"{candidate.shortlist_id}: broker connection is forbidden in v6.12.")
        if candidate.executes_trade:
            blockers.append(f"{candidate.shortlist_id}: trade execution is forbidden in v6.12.")
        if candidate.is_crypto_candidate() and REASON_CRYPTO_CEILING_GUARD_ACTIVE not in candidate.reason_codes:
            blockers.append(f"{candidate.shortlist_id}: crypto shortlist candidate must carry crypto ceiling guard reason.")

    critical_source_count = sum(
        1 for candidate in effective_shortlist if candidate.source_priority == CONTEXT_PRIORITY_CRITICAL
    )
    high_source_count = sum(
        1 for candidate in effective_shortlist if candidate.source_priority == CONTEXT_PRIORITY_HIGH
    )
    crypto_shortlist_count = sum(1 for candidate in effective_shortlist if candidate.is_crypto_candidate())
    manual_review_required_count = sum(1 for candidate in effective_shortlist if candidate.manual_review_required)

    if critical_source_count < 1:
        warnings.append("No critical-priority shortlist candidate detected.")
    if high_source_count < 1:
        warnings.append("No high-priority shortlist candidate detected.")
    if crypto_shortlist_count < 1:
        warnings.append("No crypto shortlist candidate detected.")

    safety_flags = {
        "manual_weekly_shortlist_ready": False,
        "shortlist_only": True,
        "final_recommendation_deferred": True,
        "asset_approval_deferred": True,
        "weekly_buy_ticket_deferred": True,
        "buy_request_deferred": True,
        "broker_execution_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["shortlist_only"]:
        blockers.append("v6.12 must remain shortlist-only.")
    if not safety_flags["final_recommendation_deferred"]:
        blockers.append("v6.12 must defer final recommendations.")
    if not safety_flags["asset_approval_deferred"]:
        blockers.append("v6.12 must defer asset approval.")
    if not safety_flags["weekly_buy_ticket_deferred"]:
        blockers.append("v6.12 must defer weekly buy tickets.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v6.12 must defer buy requests.")
    if not safety_flags["broker_execution_forbidden"]:
        blockers.append("v6.12 must forbid broker execution.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.12 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))

    return ManualWeeklyCandidateShortlistResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        analyzed_policy_id=planning_result.analyzed_policy_id,
        source_planning_context_item_count=planning_result.planning_context_item_count,
        shortlist_candidate_count=len(effective_shortlist),
        critical_source_count=critical_source_count,
        high_source_count=high_source_count,
        crypto_shortlist_count=crypto_shortlist_count,
        manual_review_required_count=manual_review_required_count,
        investable_cash_eur=planning_result.investable_cash_eur,
        protected_cash_eur=planning_result.protected_cash_eur,
        shortlist_candidates=effective_shortlist,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "manual_weekly_shortlist_ready": not unique_blockers},
    )
