"""J.A.R.V.I.S. v6.13 autonomous weekly recommendation draft builder.

This stage converts the weekly candidate shortlist into one autonomous weekly
recommendation draft.

Safety boundary:
- autonomous recommendation draft allowed
- manual buy instructions allowed
- no buy request creation
- no broker/API connection
- no order placement
- no trade execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v6_12_manual_weekly_candidate_shortlist_builder import (
    ManualWeeklyShortlistCandidate,
    audit_v6_12_manual_weekly_candidate_shortlist_builder,
)


STATUS_READY = "JARVIS_V6_13_AUTONOMOUS_WEEKLY_RECOMMENDATION_DRAFT_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_13_AUTONOMOUS_WEEKLY_RECOMMENDATION_DRAFT_BLOCKED_SAFE"

NEXT_STAGE = "v6.14_recommendation_dashboard_integration"

RECOMMENDATION_STATUS_DRAFT_READY = "AUTONOMOUS_RECOMMENDATION_DRAFT_READY"
RECOMMENDATION_STATUS_BLOCKED = "AUTONOMOUS_RECOMMENDATION_DRAFT_BLOCKED"

DECISION_BUY_CANDIDATE = "BUY_CANDIDATE"
DECISION_WAIT = "WAIT"

SLEEVE_CRYPTO_CORE_BTC = "crypto_core_btc"
SLEEVE_CRYPTO_SPECULATIVE = "crypto_speculative"


@dataclass(frozen=True)
class WeeklyRecommendationDraft:
    recommendation_id: str
    recommendation_status: str
    decision: str
    selected_shortlist_id: str
    selected_candidate_id: str
    selected_sleeve_id: str
    selected_rank: int
    confidence_score: int
    suggested_manual_amount_logic: str
    primary_reason: str
    supporting_reasons: tuple[str, ...]
    rejection_reasons_for_others: tuple[str, ...]
    risk_warnings: tuple[str, ...]
    manual_buy_instructions: tuple[str, ...]
    final_user_action_required: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def is_crypto_recommendation(self) -> bool:
        return self.selected_sleeve_id in {SLEEVE_CRYPTO_CORE_BTC, SLEEVE_CRYPTO_SPECULATIVE}

    def safe_recommendation_draft_only(self) -> bool:
        return (
            self.final_user_action_required
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "recommendation_status": self.recommendation_status,
            "decision": self.decision,
            "selected_shortlist_id": self.selected_shortlist_id,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "selected_rank": self.selected_rank,
            "confidence_score": self.confidence_score,
            "suggested_manual_amount_logic": self.suggested_manual_amount_logic,
            "primary_reason": self.primary_reason,
            "supporting_reasons": list(self.supporting_reasons),
            "rejection_reasons_for_others": list(self.rejection_reasons_for_others),
            "risk_warnings": list(self.risk_warnings),
            "manual_buy_instructions": list(self.manual_buy_instructions),
            "final_user_action_required": self.final_user_action_required,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "is_crypto_recommendation": self.is_crypto_recommendation(),
            "safe_recommendation_draft_only": self.safe_recommendation_draft_only(),
        }


@dataclass(frozen=True)
class AutonomousWeeklyRecommendationDraftResult:
    status: str
    recommended_next_stage: str
    analyzed_policy_id: str
    shortlist_candidate_count: int
    recommendation_count: int
    selected_candidate_id: str
    selected_sleeve_id: str
    investable_cash_eur: float
    protected_cash_eur: float
    recommendation: WeeklyRecommendationDraft | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    autonomous_recommendation_ready: bool
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
            "shortlist_candidate_count": self.shortlist_candidate_count,
            "recommendation_count": self.recommendation_count,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "investable_cash_eur": self.investable_cash_eur,
            "protected_cash_eur": self.protected_cash_eur,
            "recommendation": None if self.recommendation is None else self.recommendation.to_dict(),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "autonomous_recommendation_ready": self.autonomous_recommendation_ready,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _candidate_score(candidate: ManualWeeklyShortlistCandidate) -> int:
    score = 100 - candidate.rank * 5

    if candidate.source_priority == "CRITICAL":
        score += 20
    if candidate.source_gap_status == "UNDER_MIN":
        score += 15
    if candidate.sleeve_id == SLEEVE_CRYPTO_CORE_BTC:
        score += 10
    if candidate.sleeve_id == SLEEVE_CRYPTO_SPECULATIVE:
        score -= 30
    if "CRYPTO_CEILING_GUARD_ACTIVE" in candidate.reason_codes:
        score -= 5

    return max(0, min(score, 100))


def select_best_weekly_candidate(
    shortlist: tuple[ManualWeeklyShortlistCandidate, ...],
) -> ManualWeeklyShortlistCandidate | None:
    if not shortlist:
        return None

    safe_candidates = tuple(
        candidate
        for candidate in shortlist
        if candidate.safe_shortlist_only()
        and candidate.manual_review_required
        and not candidate.final_recommendation_created
        and not candidate.asset_approved
        and not candidate.creates_buy_request
        and not candidate.connects_broker
        and not candidate.executes_trade
    )

    if not safe_candidates:
        return None

    return sorted(
        safe_candidates,
        key=lambda candidate: (-_candidate_score(candidate), candidate.rank, candidate.candidate_id),
    )[0]


def build_weekly_recommendation_draft(
    shortlist: tuple[ManualWeeklyShortlistCandidate, ...],
    investable_cash_eur: float,
    protected_cash_eur: float,
) -> WeeklyRecommendationDraft | None:
    selected = select_best_weekly_candidate(shortlist)
    if selected is None:
        return None

    confidence = _candidate_score(selected)

    rejection_reasons = tuple(
        f"{candidate.candidate_id}: ranked below {selected.candidate_id} because priority/gap score was lower."
        for candidate in shortlist
        if candidate.shortlist_id != selected.shortlist_id
    )

    risk_warnings = [
        "This is an autonomous recommendation draft, not an order.",
        "Protected cash must remain untouched.",
        "Final buy action must be done manually by the user outside J.A.R.V.I.S.",
    ]

    if selected.is_crypto_candidate():
        risk_warnings.append("Crypto recommendation requires crypto ceiling and volatility discipline.")

    manual_instructions = (
        "Review the selected candidate and reasoning.",
        "Open the chosen external platform manually.",
        "Place the real-world buy manually only if you agree.",
        "Do not treat this draft as a broker order or executable ticket.",
    )

    amount_logic = (
        "Use available investable cash only after Protected cash remains untouched. "
        "Prefer a modest weekly amount that moves the selected sleeve toward policy range "
        "without breaching crypto ceiling, concentration, or cash rules."
    )

    return WeeklyRecommendationDraft(
        recommendation_id=f"weekly_draft_{selected.candidate_id}",
        recommendation_status=RECOMMENDATION_STATUS_DRAFT_READY,
        decision=DECISION_BUY_CANDIDATE,
        selected_shortlist_id=selected.shortlist_id,
        selected_candidate_id=selected.candidate_id,
        selected_sleeve_id=selected.sleeve_id,
        selected_rank=selected.rank,
        confidence_score=confidence,
        suggested_manual_amount_logic=amount_logic,
        primary_reason=(
            f"{selected.candidate_id} is the top autonomous shortlist candidate because "
            f"{selected.sleeve_id} has source priority {selected.source_priority} and gap status {selected.source_gap_status}."
        ),
        supporting_reasons=(
            f"reason codes: {', '.join(selected.reason_codes)}",
            f"investable cash context: {investable_cash_eur}",
            f"protected cash context: {protected_cash_eur}",
            "candidate came from active-policy-aligned shortlist, not from ad-hoc selection.",
        ),
        rejection_reasons_for_others=rejection_reasons,
        risk_warnings=tuple(risk_warnings),
        manual_buy_instructions=manual_instructions,
        final_user_action_required=True,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def audit_v6_13_autonomous_weekly_recommendation_draft_builder(
    recommendation: WeeklyRecommendationDraft | None | object = None,
) -> AutonomousWeeklyRecommendationDraftResult:
    shortlist_result = audit_v6_12_manual_weekly_candidate_shortlist_builder()

    if recommendation is None:
        effective_recommendation = build_weekly_recommendation_draft(
            shortlist_result.shortlist_candidates,
            shortlist_result.investable_cash_eur,
            shortlist_result.protected_cash_eur,
        )
    else:
        effective_recommendation = recommendation

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.13 creates an autonomous weekly recommendation draft only.",
        "The only manual action is the user's final real-world buy outside J.A.R.V.I.S.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if shortlist_result.blockers:
        blockers.append("Source weekly candidate shortlist is blocked.")
    if not shortlist_result.shortlist_candidates:
        blockers.append("No shortlist candidates are available.")

    if effective_recommendation is not None and not isinstance(
        effective_recommendation,
        WeeklyRecommendationDraft,
    ):
        blockers.append("Recommendation override must be a WeeklyRecommendationDraft.")
        effective_recommendation = None

    if effective_recommendation is None:
        blockers.append("No autonomous weekly recommendation draft was created.")

    if effective_recommendation is not None:
        if effective_recommendation.recommendation_status != RECOMMENDATION_STATUS_DRAFT_READY:
            blockers.append("Recommendation status must be autonomous draft ready.")
        if effective_recommendation.decision != DECISION_BUY_CANDIDATE:
            blockers.append("Recommendation decision must be BUY_CANDIDATE or explicitly blocked.")
        if not effective_recommendation.selected_candidate_id:
            blockers.append("Selected candidate is required.")
        if not effective_recommendation.primary_reason.strip():
            blockers.append("Primary reason is required.")
        if not effective_recommendation.supporting_reasons:
            blockers.append("Supporting reasons are required.")
        if not effective_recommendation.risk_warnings:
            blockers.append("Risk warnings are required.")
        if not effective_recommendation.manual_buy_instructions:
            blockers.append("Manual buy instructions are required.")
        if not effective_recommendation.final_user_action_required:
            blockers.append("Final user buy action must be required.")
        if not effective_recommendation.safe_recommendation_draft_only():
            blockers.append("Recommendation must remain draft-only and non-executable.")
        if effective_recommendation.creates_buy_request:
            blockers.append("Buy request creation is forbidden in v6.13.")
        if effective_recommendation.connects_broker:
            blockers.append("Broker connection is forbidden in v6.13.")
        if effective_recommendation.places_order:
            blockers.append("Order placement is forbidden in v6.13.")
        if effective_recommendation.executes_trade:
            blockers.append("Trade execution is forbidden in v6.13.")

    safety_flags = {
        "autonomous_recommendation_ready": False,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v6.13 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v6.13 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v6.13 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.13 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))

    selected_candidate_id = ""
    selected_sleeve_id = ""
    recommendation_count = 0
    if effective_recommendation is not None:
        selected_candidate_id = effective_recommendation.selected_candidate_id
        selected_sleeve_id = effective_recommendation.selected_sleeve_id
        recommendation_count = 1

    return AutonomousWeeklyRecommendationDraftResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        analyzed_policy_id=shortlist_result.analyzed_policy_id,
        shortlist_candidate_count=shortlist_result.shortlist_candidate_count,
        recommendation_count=recommendation_count,
        selected_candidate_id=selected_candidate_id,
        selected_sleeve_id=selected_sleeve_id,
        investable_cash_eur=shortlist_result.investable_cash_eur,
        protected_cash_eur=shortlist_result.protected_cash_eur,
        recommendation=effective_recommendation,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "autonomous_recommendation_ready": not unique_blockers},
    )
