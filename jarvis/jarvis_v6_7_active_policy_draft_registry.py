"""J.A.R.V.I.S. v6.7 active policy draft registry.

This stage creates draft policy records only from manually accepted v6.6
review decisions.

Report-only safety boundary:
- active-policy drafts only
- no active policy approval
- no active policy activation
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
    AllocationBand,
    PolicyAssetSelection,
    PolicyCandidate,
    audit_v6_5_policy_candidate_generator,
)
from .jarvis_v6_6_manual_policy_review_queue import (
    DECISION_ACCEPT_FOR_ACTIVE_POLICY_REVIEW,
    PolicyReviewQueueItem,
    audit_v6_6_manual_policy_review_queue,
)


STATUS_READY = "JARVIS_V6_7_ACTIVE_POLICY_DRAFT_REGISTRY_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_7_ACTIVE_POLICY_DRAFT_REGISTRY_BLOCKED_SAFE"

NEXT_STAGE = "v6.8_active_policy_manual_approval_gate"

DRAFT_STATUS_MANUAL_APPROVAL_REQUIRED = "DRAFT_MANUAL_APPROVAL_REQUIRED"
DRAFT_STATUS_BLOCKED = "DRAFT_BLOCKED"

SLEEVE_CRYPTO_CORE_BTC = "crypto_core_btc"
SLEEVE_CRYPTO_SPECULATIVE = "crypto_speculative"
SLEEVE_CASH_DEFENSIVE = "cash_defensive"
SLEEVE_BOND_DEFENSIVE = "bond_defensive"
SLEEVE_COMMODITY_DEFENSIVE = "commodity_defensive"


@dataclass(frozen=True)
class ActivePolicyDraft:
    draft_id: str
    source_review_id: str
    source_policy_id: str
    display_name: str
    draft_status: str
    aggressiveness_score: int
    suitability_reason: str
    allocation_bands: tuple[AllocationBand, ...]
    selected_assets: tuple[PolicyAssetSelection, ...]
    risk_constraints: tuple[str, ...]
    activation_requirements: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    operator_approved_active_policy: bool
    active_policy_created: bool
    active_policy_mutated: bool
    asset_approval_created: bool
    creates_weekly_buy_ticket: bool
    creates_buy_request: bool
    executes_trade: bool

    def max_crypto_weight_pct(self) -> float:
        return round(
            sum(
                band.max_pct
                for band in self.allocation_bands
                if band.sleeve_id in {SLEEVE_CRYPTO_CORE_BTC, SLEEVE_CRYPTO_SPECULATIVE}
            ),
            2,
        )

    def min_defensive_weight_pct(self) -> float:
        return round(
            sum(
                band.min_pct
                for band in self.allocation_bands
                if band.sleeve_id in {
                    SLEEVE_CASH_DEFENSIVE,
                    SLEEVE_BOND_DEFENSIVE,
                    SLEEVE_COMMODITY_DEFENSIVE,
                }
            ),
            2,
        )

    def has_valid_bands(self) -> bool:
        return all(band.valid() for band in self.allocation_bands)

    def safe_draft_only(self) -> bool:
        return (
            self.manual_approval_required
            and not self.operator_approved_active_policy
            and not self.active_policy_created
            and not self.active_policy_mutated
            and not self.asset_approval_created
            and not self.creates_weekly_buy_ticket
            and not self.creates_buy_request
            and not self.executes_trade
        )

    def selected_candidate_ids(self) -> tuple[str, ...]:
        return tuple(selection.candidate_id for selection in self.selected_assets)

    def to_dict(self) -> dict[str, Any]:
        return {
            "draft_id": self.draft_id,
            "source_review_id": self.source_review_id,
            "source_policy_id": self.source_policy_id,
            "display_name": self.display_name,
            "draft_status": self.draft_status,
            "aggressiveness_score": self.aggressiveness_score,
            "suitability_reason": self.suitability_reason,
            "allocation_bands": [band.to_dict() for band in self.allocation_bands],
            "selected_assets": [selection.to_dict() for selection in self.selected_assets],
            "risk_constraints": list(self.risk_constraints),
            "activation_requirements": list(self.activation_requirements),
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "operator_approved_active_policy": self.operator_approved_active_policy,
            "active_policy_created": self.active_policy_created,
            "active_policy_mutated": self.active_policy_mutated,
            "asset_approval_created": self.asset_approval_created,
            "creates_weekly_buy_ticket": self.creates_weekly_buy_ticket,
            "creates_buy_request": self.creates_buy_request,
            "executes_trade": self.executes_trade,
            "max_crypto_weight_pct": self.max_crypto_weight_pct(),
            "min_defensive_weight_pct": self.min_defensive_weight_pct(),
            "has_valid_bands": self.has_valid_bands(),
            "safe_draft_only": self.safe_draft_only(),
            "selected_candidate_ids": list(self.selected_candidate_ids()),
        }


@dataclass(frozen=True)
class ActivePolicyDraftRegistryResult:
    status: str
    recommended_next_stage: str
    source_review_item_count: int
    accepted_review_count: int
    active_policy_draft_count: int
    active_policy_count: int
    draft_items: tuple[ActivePolicyDraft, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    active_policy_draft_registry_ready: bool
    draft_only: bool
    manual_approval_required: bool
    active_policy_approval_deferred: bool
    active_policy_activation_deferred: bool
    asset_approval_deferred: bool
    weekly_buy_ticket_deferred: bool
    buy_request_deferred: bool
    broker_execution_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "source_review_item_count": self.source_review_item_count,
            "accepted_review_count": self.accepted_review_count,
            "active_policy_draft_count": self.active_policy_draft_count,
            "active_policy_count": self.active_policy_count,
            "draft_items": [item.to_dict() for item in self.draft_items],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "active_policy_draft_registry_ready": self.active_policy_draft_registry_ready,
            "draft_only": self.draft_only,
            "manual_approval_required": self.manual_approval_required,
            "active_policy_approval_deferred": self.active_policy_approval_deferred,
            "active_policy_activation_deferred": self.active_policy_activation_deferred,
            "asset_approval_deferred": self.asset_approval_deferred,
            "weekly_buy_ticket_deferred": self.weekly_buy_ticket_deferred,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _draft_from_policy_and_review(
    policy: PolicyCandidate,
    review_item: PolicyReviewQueueItem,
) -> ActivePolicyDraft:
    return ActivePolicyDraft(
        draft_id=f"draft_{policy.policy_id}",
        source_review_id=review_item.review_id,
        source_policy_id=policy.policy_id,
        display_name=f"Draft: {policy.display_name}",
        draft_status=DRAFT_STATUS_MANUAL_APPROVAL_REQUIRED,
        aggressiveness_score=policy.aggressiveness_score,
        suitability_reason=policy.suitability_reason,
        allocation_bands=policy.allocation_bands,
        selected_assets=policy.selected_assets,
        risk_constraints=(
            "Manual approval required before this draft can become active.",
            "Crypto maximum must remain at or below 35%.",
            "Speculative crypto remains excluded until quality improves.",
            "Protected emergency cash must not be investable.",
            "Weekly buy tickets require a later planning stage.",
        ),
        activation_requirements=(
            "Operator must review and approve the active-policy draft in v6.8+.",
            "Private snapshot must be fresh at approval time.",
            "Asset quality gate must remain unblocked.",
            "No broker or execution route may be attached.",
        ),
        warnings=(
            "Draft is not active.",
            "Draft is not approved.",
            "No weekly buy ticket or buy request is created.",
        ),
        blockers=(),
        manual_approval_required=True,
        operator_approved_active_policy=False,
        active_policy_created=False,
        active_policy_mutated=False,
        asset_approval_created=False,
        creates_weekly_buy_ticket=False,
        creates_buy_request=False,
        executes_trade=False,
    )


def build_active_policy_drafts_from_reviews(
    policy_candidates: tuple[PolicyCandidate, ...],
    review_items: tuple[PolicyReviewQueueItem, ...],
) -> tuple[ActivePolicyDraft, ...]:
    policies_by_id = {policy.policy_id: policy for policy in policy_candidates}
    drafts: list[ActivePolicyDraft] = []

    for item in review_items:
        if item.decision != DECISION_ACCEPT_FOR_ACTIVE_POLICY_REVIEW:
            continue
        policy = policies_by_id.get(item.policy_id)
        if policy is None:
            continue
        drafts.append(_draft_from_policy_and_review(policy, item))

    return tuple(drafts)


def audit_v6_7_active_policy_draft_registry(
    draft_items: tuple[ActivePolicyDraft, ...] | None = None,
) -> ActivePolicyDraftRegistryResult:
    policy_result = audit_v6_5_policy_candidate_generator()
    review_result = audit_v6_6_manual_policy_review_queue()

    effective_drafts = draft_items or build_active_policy_drafts_from_reviews(
        policy_result.policy_candidates,
        review_result.review_items,
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.7 creates active-policy draft records only; approval is deferred to v6.8.",
        "A draft policy is not an active policy.",
        "No weekly buy ticket, buy request, broker action, or trade is created.",
    ]

    if policy_result.blockers:
        blockers.append("Source policy candidate generator is blocked.")
    if review_result.blockers:
        blockers.append("Manual policy review queue is blocked.")

    accepted_review_items = tuple(
        item
        for item in review_result.review_items
        if item.decision == DECISION_ACCEPT_FOR_ACTIVE_POLICY_REVIEW
    )
    accepted_review_ids = {item.review_id for item in accepted_review_items}
    accepted_policy_ids = {item.policy_id for item in accepted_review_items}

    if not accepted_review_items:
        blockers.append("No policy review item was accepted for active-policy draft review.")
    if not effective_drafts:
        blockers.append("No active-policy draft records were created.")

    draft_ids = [draft.draft_id for draft in effective_drafts]
    if len(draft_ids) != len(set(draft_ids)):
        blockers.append("Active-policy draft IDs must be unique.")

    draft_policy_ids = {draft.source_policy_id for draft in effective_drafts}
    missing_drafts = accepted_policy_ids - draft_policy_ids
    for policy_id in sorted(missing_drafts):
        blockers.append(f"Missing active-policy draft for accepted policy: {policy_id}")

    for draft in effective_drafts:
        if draft.source_review_id not in accepted_review_ids:
            blockers.append(
                f"{draft.draft_id}: draft must come from an accepted manual review item."
            )
        if draft.draft_status != DRAFT_STATUS_MANUAL_APPROVAL_REQUIRED:
            blockers.append(f"{draft.draft_id}: draft status must require manual approval.")
        if not draft.manual_approval_required:
            blockers.append(f"{draft.draft_id}: manual approval must be required.")
        if draft.operator_approved_active_policy:
            blockers.append(f"{draft.draft_id}: active policy approval is forbidden in v6.7.")
        if draft.active_policy_created:
            blockers.append(f"{draft.draft_id}: active policy creation is forbidden in v6.7.")
        if draft.active_policy_mutated:
            blockers.append(f"{draft.draft_id}: active policy mutation is forbidden in v6.7.")
        if draft.asset_approval_created:
            blockers.append(f"{draft.draft_id}: asset approval is forbidden in v6.7.")
        if draft.creates_weekly_buy_ticket:
            blockers.append(f"{draft.draft_id}: weekly buy ticket creation is forbidden in v6.7.")
        if draft.creates_buy_request:
            blockers.append(f"{draft.draft_id}: buy request creation is forbidden in v6.7.")
        if draft.executes_trade:
            blockers.append(f"{draft.draft_id}: trade execution is forbidden in v6.7.")
        if not draft.safe_draft_only():
            blockers.append(f"{draft.draft_id}: draft must remain safe draft-only.")
        if not draft.has_valid_bands():
            blockers.append(f"{draft.draft_id}: invalid allocation bands.")
        if not draft.selected_assets:
            blockers.append(f"{draft.draft_id}: selected assets are required.")
        if draft.max_crypto_weight_pct() > 35.0:
            blockers.append(f"{draft.draft_id}: crypto max exceeds 35% safety ceiling.")
        if draft.min_defensive_weight_pct() < 3.0:
            blockers.append(f"{draft.draft_id}: minimum defensive allocation is too low.")
        if not draft.activation_requirements:
            blockers.append(f"{draft.draft_id}: activation requirements are required.")

    safety_flags = {
        "active_policy_draft_registry_ready": False,
        "draft_only": True,
        "manual_approval_required": True,
        "active_policy_approval_deferred": True,
        "active_policy_activation_deferred": True,
        "asset_approval_deferred": True,
        "weekly_buy_ticket_deferred": True,
        "buy_request_deferred": True,
        "broker_execution_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["draft_only"]:
        blockers.append("v6.7 must remain draft-only.")
    if not safety_flags["manual_approval_required"]:
        blockers.append("v6.7 must require manual approval.")
    if not safety_flags["active_policy_approval_deferred"]:
        blockers.append("v6.7 must defer active policy approval.")
    if not safety_flags["active_policy_activation_deferred"]:
        blockers.append("v6.7 must defer active policy activation.")
    if not safety_flags["asset_approval_deferred"]:
        blockers.append("v6.7 must defer asset approval.")
    if not safety_flags["weekly_buy_ticket_deferred"]:
        blockers.append("v6.7 must defer weekly buy tickets.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v6.7 must defer buy requests.")
    if not safety_flags["broker_execution_forbidden"]:
        blockers.append("v6.7 must forbid broker execution.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.7 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))

    return ActivePolicyDraftRegistryResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        source_review_item_count=len(review_result.review_items),
        accepted_review_count=len(accepted_review_items),
        active_policy_draft_count=len(effective_drafts),
        active_policy_count=0,
        draft_items=effective_drafts,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "active_policy_draft_registry_ready": not unique_blockers},
    )
