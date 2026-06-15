"""J.A.R.V.I.S. v6.6 manual policy review queue.

This stage converts v6.5 policy candidates into manual review records.

Report-only safety boundary:
- manual decision records only
- no active policy creation
- no policy approval automation
- no asset approval
- no weekly buy ticket
- no buy request creation
- no broker/API execution
- no trades
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v6_5_policy_candidate_generator import (
    PolicyCandidate,
    audit_v6_5_policy_candidate_generator,
)


STATUS_READY = "JARVIS_V6_6_MANUAL_POLICY_REVIEW_QUEUE_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_6_MANUAL_POLICY_REVIEW_QUEUE_BLOCKED_SAFE"

NEXT_STAGE = "v6.7_active_policy_draft_registry"

DECISION_ACCEPT_FOR_ACTIVE_POLICY_REVIEW = "ACCEPT_FOR_ACTIVE_POLICY_REVIEW"
DECISION_DEFER = "DEFER"
DECISION_REJECT = "REJECT"
DECISION_NEEDS_CORRECTION = "NEEDS_CORRECTION"

ALLOWED_DECISIONS = {
    DECISION_ACCEPT_FOR_ACTIVE_POLICY_REVIEW,
    DECISION_DEFER,
    DECISION_REJECT,
    DECISION_NEEDS_CORRECTION,
}


@dataclass(frozen=True)
class PolicyReviewQueueItem:
    review_id: str
    policy_id: str
    policy_display_name: str
    decision: str
    reviewer: str
    review_note: str
    required_corrections: tuple[str, ...]
    retained_for_future_review: bool
    manual_review_recorded: bool
    creates_active_policy: bool
    operator_approved_active_policy: bool
    creates_weekly_buy_ticket: bool
    creates_buy_request: bool
    executes_trade: bool

    def is_valid_decision(self) -> bool:
        return self.decision in ALLOWED_DECISIONS

    def requires_corrections(self) -> bool:
        return self.decision == DECISION_NEEDS_CORRECTION

    def safe_record_only(self) -> bool:
        return (
            self.manual_review_recorded
            and not self.creates_active_policy
            and not self.operator_approved_active_policy
            and not self.creates_weekly_buy_ticket
            and not self.creates_buy_request
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "review_id": self.review_id,
            "policy_id": self.policy_id,
            "policy_display_name": self.policy_display_name,
            "decision": self.decision,
            "reviewer": self.reviewer,
            "review_note": self.review_note,
            "required_corrections": list(self.required_corrections),
            "retained_for_future_review": self.retained_for_future_review,
            "manual_review_recorded": self.manual_review_recorded,
            "creates_active_policy": self.creates_active_policy,
            "operator_approved_active_policy": self.operator_approved_active_policy,
            "creates_weekly_buy_ticket": self.creates_weekly_buy_ticket,
            "creates_buy_request": self.creates_buy_request,
            "executes_trade": self.executes_trade,
            "is_valid_decision": self.is_valid_decision(),
            "requires_corrections": self.requires_corrections(),
            "safe_record_only": self.safe_record_only(),
        }


@dataclass(frozen=True)
class ManualPolicyReviewQueueResult:
    status: str
    recommended_next_stage: str
    source_policy_candidate_count: int
    review_item_count: int
    accept_for_active_policy_review_count: int
    defer_count: int
    reject_count: int
    needs_correction_count: int
    review_items: tuple[PolicyReviewQueueItem, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    manual_policy_review_queue_ready: bool
    manual_review_records_only: bool
    active_policy_creation_deferred: bool
    policy_approval_deferred: bool
    asset_approval_deferred: bool
    weekly_buy_ticket_deferred: bool
    buy_request_deferred: bool
    broker_execution_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "source_policy_candidate_count": self.source_policy_candidate_count,
            "review_item_count": self.review_item_count,
            "accept_for_active_policy_review_count": self.accept_for_active_policy_review_count,
            "defer_count": self.defer_count,
            "reject_count": self.reject_count,
            "needs_correction_count": self.needs_correction_count,
            "review_items": [item.to_dict() for item in self.review_items],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "manual_policy_review_queue_ready": self.manual_policy_review_queue_ready,
            "manual_review_records_only": self.manual_review_records_only,
            "active_policy_creation_deferred": self.active_policy_creation_deferred,
            "policy_approval_deferred": self.policy_approval_deferred,
            "asset_approval_deferred": self.asset_approval_deferred,
            "weekly_buy_ticket_deferred": self.weekly_buy_ticket_deferred,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def build_example_manual_policy_review_items(
    policy_candidates: tuple[PolicyCandidate, ...],
) -> tuple[PolicyReviewQueueItem, ...]:
    by_policy_id = {candidate.policy_id: candidate for candidate in policy_candidates}

    def item(
        policy_id: str,
        decision: str,
        note: str,
        corrections: tuple[str, ...] = (),
        retained: bool = True,
    ) -> PolicyReviewQueueItem:
        candidate = by_policy_id[policy_id]
        return PolicyReviewQueueItem(
            review_id=f"review_{policy_id}",
            policy_id=policy_id,
            policy_display_name=candidate.display_name,
            decision=decision,
            reviewer="manual_operator",
            review_note=note,
            required_corrections=corrections,
            retained_for_future_review=retained,
            manual_review_recorded=True,
            creates_active_policy=False,
            operator_approved_active_policy=False,
            creates_weekly_buy_ticket=False,
            creates_buy_request=False,
            executes_trade=False,
        )

    return (
        item(
            "balanced_aggressive_manual_review",
            DECISION_ACCEPT_FOR_ACTIVE_POLICY_REVIEW,
            "Best current candidate for next active-policy draft review because it balances aggressive growth, BTC allowance, and defensive liquidity.",
        ),
        item(
            "etf_heavy_with_crypto_allowance",
            DECISION_DEFER,
            "Useful simpler alternative, but less aligned with the user's desired aggressive policy intelligence.",
        ),
        item(
            "core_etf_btc_accumulation",
            DECISION_NEEDS_CORRECTION,
            "Promising but crypto ceiling and defensive buffers need an extra review before active-policy drafting.",
            corrections=(
                "Re-check BTC maximum band against private portfolio drawdown tolerance.",
                "Add clearer rule for when weekly BTC buys pause.",
                "Clarify how speculative crypto remains excluded until quality improves.",
            ),
        ),
        item(
            "defensive_cash_bond_aware",
            DECISION_REJECT,
            "Too defensive for the user's stated aggressive long-term portfolio intent.",
            retained=False,
        ),
    )


def audit_v6_6_manual_policy_review_queue(
    review_items: tuple[PolicyReviewQueueItem, ...] | None = None,
) -> ManualPolicyReviewQueueResult:
    source_result = audit_v6_5_policy_candidate_generator()
    effective_items = review_items or build_example_manual_policy_review_items(
        source_result.policy_candidates
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.6 records manual review decisions only; active policy drafting is deferred to v6.7.",
        "Accepting a policy for active-policy review does not activate or approve it.",
        "No weekly buy ticket, buy request, broker action, or trade is created.",
    ]

    if source_result.blockers:
        blockers.append("Source policy candidate generator is blocked.")

    source_policy_ids = {candidate.policy_id for candidate in source_result.policy_candidates}
    review_policy_ids = [item.policy_id for item in effective_items]

    if len(review_policy_ids) != len(set(review_policy_ids)):
        blockers.append("Review queue policy IDs must be unique.")

    missing_reviews = source_policy_ids - set(review_policy_ids)
    for policy_id in sorted(missing_reviews):
        blockers.append(f"Missing manual review item for policy candidate: {policy_id}")

    unknown_reviews = set(review_policy_ids) - source_policy_ids
    for policy_id in sorted(unknown_reviews):
        blockers.append(f"Review item references unknown policy candidate: {policy_id}")

    accept_count = 0
    defer_count = 0
    reject_count = 0
    needs_correction_count = 0

    for item in effective_items:
        if item.decision == DECISION_ACCEPT_FOR_ACTIVE_POLICY_REVIEW:
            accept_count += 1
        elif item.decision == DECISION_DEFER:
            defer_count += 1
        elif item.decision == DECISION_REJECT:
            reject_count += 1
        elif item.decision == DECISION_NEEDS_CORRECTION:
            needs_correction_count += 1

        if not item.is_valid_decision():
            blockers.append(f"{item.review_id}: invalid manual review decision.")
        if not item.manual_review_recorded:
            blockers.append(f"{item.review_id}: manual review record is missing.")
        if not item.review_note.strip():
            blockers.append(f"{item.review_id}: review note is required.")
        if item.requires_corrections() and not item.required_corrections:
            blockers.append(f"{item.review_id}: required corrections are missing.")
        if not item.safe_record_only():
            blockers.append(f"{item.review_id}: review item must remain a safe record only.")
        if item.creates_active_policy:
            blockers.append(f"{item.review_id}: active policy creation is forbidden in v6.6.")
        if item.operator_approved_active_policy:
            blockers.append(f"{item.review_id}: active policy approval is forbidden in v6.6.")
        if item.creates_weekly_buy_ticket:
            blockers.append(f"{item.review_id}: weekly buy ticket creation is forbidden in v6.6.")
        if item.creates_buy_request:
            blockers.append(f"{item.review_id}: buy request creation is forbidden in v6.6.")
        if item.executes_trade:
            blockers.append(f"{item.review_id}: trade execution is forbidden in v6.6.")

    if accept_count < 1:
        blockers.append("At least one policy must be accepted for active-policy review.")
    if needs_correction_count < 1:
        blockers.append("At least one needs-correction example is required.")
    if defer_count < 1:
        blockers.append("At least one deferred example is required.")
    if reject_count < 1:
        blockers.append("At least one rejected example is required.")

    safety_flags = {
        "manual_policy_review_queue_ready": False,
        "manual_review_records_only": True,
        "active_policy_creation_deferred": True,
        "policy_approval_deferred": True,
        "asset_approval_deferred": True,
        "weekly_buy_ticket_deferred": True,
        "buy_request_deferred": True,
        "broker_execution_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["manual_review_records_only"]:
        blockers.append("v6.6 must remain review-record-only.")
    if not safety_flags["active_policy_creation_deferred"]:
        blockers.append("v6.6 must defer active policy creation.")
    if not safety_flags["policy_approval_deferred"]:
        blockers.append("v6.6 must defer policy approval.")
    if not safety_flags["asset_approval_deferred"]:
        blockers.append("v6.6 must defer asset approval.")
    if not safety_flags["weekly_buy_ticket_deferred"]:
        blockers.append("v6.6 must defer weekly buy tickets.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v6.6 must defer buy requests.")
    if not safety_flags["broker_execution_forbidden"]:
        blockers.append("v6.6 must forbid broker execution.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.6 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))

    return ManualPolicyReviewQueueResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        source_policy_candidate_count=len(source_result.policy_candidates),
        review_item_count=len(effective_items),
        accept_for_active_policy_review_count=accept_count,
        defer_count=defer_count,
        reject_count=reject_count,
        needs_correction_count=needs_correction_count,
        review_items=effective_items,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "manual_policy_review_queue_ready": not unique_blockers},
    )
