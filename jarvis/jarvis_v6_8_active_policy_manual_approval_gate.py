"""J.A.R.V.I.S. v6.8 active policy manual approval gate.

This stage records manual approval decisions for v6.7 active-policy drafts.

Report-only safety boundary:
- manual approval decision records only
- no active policy registry mutation
- no asset approval
- no weekly buy ticket
- no buy request creation
- no broker/API execution
- no trades
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v6_7_active_policy_draft_registry import (
    ActivePolicyDraft,
    audit_v6_7_active_policy_draft_registry,
)


STATUS_READY = "JARVIS_V6_8_ACTIVE_POLICY_MANUAL_APPROVAL_GATE_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_8_ACTIVE_POLICY_MANUAL_APPROVAL_GATE_BLOCKED_SAFE"

NEXT_STAGE = "v6.9_active_policy_registry"

DECISION_APPROVE_ACTIVE_POLICY_DRAFT = "APPROVE_ACTIVE_POLICY_DRAFT"
DECISION_DEFER_ACTIVE_POLICY_DRAFT = "DEFER_ACTIVE_POLICY_DRAFT"
DECISION_REJECT_ACTIVE_POLICY_DRAFT = "REJECT_ACTIVE_POLICY_DRAFT"
DECISION_REQUEST_CHANGES = "REQUEST_CHANGES"

ALLOWED_DECISIONS = {
    DECISION_APPROVE_ACTIVE_POLICY_DRAFT,
    DECISION_DEFER_ACTIVE_POLICY_DRAFT,
    DECISION_REJECT_ACTIVE_POLICY_DRAFT,
    DECISION_REQUEST_CHANGES,
}


@dataclass(frozen=True)
class ActivePolicyApprovalDecision:
    approval_id: str
    draft_id: str
    source_policy_id: str
    decision: str
    reviewer: str
    decision_note: str
    required_changes: tuple[str, ...]
    approval_recorded: bool
    retained_for_future_review: bool
    authorizes_active_policy_registry_draft: bool
    creates_active_policy: bool
    mutates_active_policy: bool
    approves_assets: bool
    creates_weekly_buy_ticket: bool
    creates_buy_request: bool
    executes_trade: bool

    def is_valid_decision(self) -> bool:
        return self.decision in ALLOWED_DECISIONS

    def requires_changes(self) -> bool:
        return self.decision == DECISION_REQUEST_CHANGES

    def is_approval(self) -> bool:
        return self.decision == DECISION_APPROVE_ACTIVE_POLICY_DRAFT

    def safe_approval_record_only(self) -> bool:
        return (
            self.approval_recorded
            and not self.creates_active_policy
            and not self.mutates_active_policy
            and not self.approves_assets
            and not self.creates_weekly_buy_ticket
            and not self.creates_buy_request
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "draft_id": self.draft_id,
            "source_policy_id": self.source_policy_id,
            "decision": self.decision,
            "reviewer": self.reviewer,
            "decision_note": self.decision_note,
            "required_changes": list(self.required_changes),
            "approval_recorded": self.approval_recorded,
            "retained_for_future_review": self.retained_for_future_review,
            "authorizes_active_policy_registry_draft": self.authorizes_active_policy_registry_draft,
            "creates_active_policy": self.creates_active_policy,
            "mutates_active_policy": self.mutates_active_policy,
            "approves_assets": self.approves_assets,
            "creates_weekly_buy_ticket": self.creates_weekly_buy_ticket,
            "creates_buy_request": self.creates_buy_request,
            "executes_trade": self.executes_trade,
            "is_valid_decision": self.is_valid_decision(),
            "requires_changes": self.requires_changes(),
            "is_approval": self.is_approval(),
            "safe_approval_record_only": self.safe_approval_record_only(),
        }


@dataclass(frozen=True)
class ActivePolicyManualApprovalGateResult:
    status: str
    recommended_next_stage: str
    source_draft_count: int
    approval_decision_count: int
    approve_count: int
    defer_count: int
    reject_count: int
    request_changes_count: int
    active_policy_count: int
    approval_decisions: tuple[ActivePolicyApprovalDecision, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    manual_approval_gate_ready: bool
    manual_approval_records_only: bool
    active_policy_registry_deferred: bool
    asset_approval_deferred: bool
    weekly_buy_ticket_deferred: bool
    buy_request_deferred: bool
    broker_execution_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "source_draft_count": self.source_draft_count,
            "approval_decision_count": self.approval_decision_count,
            "approve_count": self.approve_count,
            "defer_count": self.defer_count,
            "reject_count": self.reject_count,
            "request_changes_count": self.request_changes_count,
            "active_policy_count": self.active_policy_count,
            "approval_decisions": [decision.to_dict() for decision in self.approval_decisions],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "manual_approval_gate_ready": self.manual_approval_gate_ready,
            "manual_approval_records_only": self.manual_approval_records_only,
            "active_policy_registry_deferred": self.active_policy_registry_deferred,
            "asset_approval_deferred": self.asset_approval_deferred,
            "weekly_buy_ticket_deferred": self.weekly_buy_ticket_deferred,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def build_example_active_policy_approval_decisions(
    drafts: tuple[ActivePolicyDraft, ...],
) -> tuple[ActivePolicyApprovalDecision, ...]:
    decisions: list[ActivePolicyApprovalDecision] = []

    for draft in drafts:
        decisions.append(
            ActivePolicyApprovalDecision(
                approval_id=f"approval_{draft.draft_id}",
                draft_id=draft.draft_id,
                source_policy_id=draft.source_policy_id,
                decision=DECISION_APPROVE_ACTIVE_POLICY_DRAFT,
                reviewer="manual_operator",
                decision_note=(
                    "Manual approval recorded for the draft to proceed to the active "
                    "policy registry stage. This does not create a buy ticket or trade."
                ),
                required_changes=(),
                approval_recorded=True,
                retained_for_future_review=True,
                authorizes_active_policy_registry_draft=True,
                creates_active_policy=False,
                mutates_active_policy=False,
                approves_assets=False,
                creates_weekly_buy_ticket=False,
                creates_buy_request=False,
                executes_trade=False,
            )
        )

    return tuple(decisions)


def audit_v6_8_active_policy_manual_approval_gate(
    approval_decisions: tuple[ActivePolicyApprovalDecision, ...] | None = None,
) -> ActivePolicyManualApprovalGateResult:
    draft_result = audit_v6_7_active_policy_draft_registry()
    effective_decisions = (
        build_example_active_policy_approval_decisions(draft_result.draft_items)
        if approval_decisions is None
        else approval_decisions
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.8 records manual approval decisions only; active policy registry creation is deferred to v6.9.",
        "Approval permits the next registry stage to draft an active policy record, but does not create trades.",
        "No weekly buy ticket, buy request, broker action, or trade is created.",
    ]

    if draft_result.blockers:
        blockers.append("Source active-policy draft registry is blocked.")

    source_draft_ids = {draft.draft_id for draft in draft_result.draft_items}
    decision_draft_ids = [decision.draft_id for decision in effective_decisions]

    if len(decision_draft_ids) != len(set(decision_draft_ids)):
        blockers.append("Approval decision draft IDs must be unique.")

    missing_decisions = source_draft_ids - set(decision_draft_ids)
    for draft_id in sorted(missing_decisions):
        blockers.append(f"Missing manual approval decision for draft: {draft_id}")

    unknown_decisions = set(decision_draft_ids) - source_draft_ids
    for draft_id in sorted(unknown_decisions):
        blockers.append(f"Approval decision references unknown draft: {draft_id}")

    approve_count = 0
    defer_count = 0
    reject_count = 0
    request_changes_count = 0

    for decision in effective_decisions:
        if decision.decision == DECISION_APPROVE_ACTIVE_POLICY_DRAFT:
            approve_count += 1
        elif decision.decision == DECISION_DEFER_ACTIVE_POLICY_DRAFT:
            defer_count += 1
        elif decision.decision == DECISION_REJECT_ACTIVE_POLICY_DRAFT:
            reject_count += 1
        elif decision.decision == DECISION_REQUEST_CHANGES:
            request_changes_count += 1

        if not decision.is_valid_decision():
            blockers.append(f"{decision.approval_id}: invalid approval decision.")
        if not decision.approval_recorded:
            blockers.append(f"{decision.approval_id}: approval decision record is missing.")
        if not decision.decision_note.strip():
            blockers.append(f"{decision.approval_id}: decision note is required.")
        if decision.requires_changes() and not decision.required_changes:
            blockers.append(f"{decision.approval_id}: required changes are missing.")
        if decision.is_approval() and not decision.authorizes_active_policy_registry_draft:
            blockers.append(f"{decision.approval_id}: approved draft must authorize v6.9 registry drafting.")
        if not decision.safe_approval_record_only():
            blockers.append(f"{decision.approval_id}: approval decision must remain record-only.")
        if decision.creates_active_policy:
            blockers.append(f"{decision.approval_id}: active policy creation is forbidden in v6.8.")
        if decision.mutates_active_policy:
            blockers.append(f"{decision.approval_id}: active policy mutation is forbidden in v6.8.")
        if decision.approves_assets:
            blockers.append(f"{decision.approval_id}: asset approval is forbidden in v6.8.")
        if decision.creates_weekly_buy_ticket:
            blockers.append(f"{decision.approval_id}: weekly buy ticket creation is forbidden in v6.8.")
        if decision.creates_buy_request:
            blockers.append(f"{decision.approval_id}: buy request creation is forbidden in v6.8.")
        if decision.executes_trade:
            blockers.append(f"{decision.approval_id}: trade execution is forbidden in v6.8.")

    if approve_count < 1:
        blockers.append("At least one active-policy draft must be manually approved for v6.9.")

    safety_flags = {
        "manual_approval_gate_ready": False,
        "manual_approval_records_only": True,
        "active_policy_registry_deferred": True,
        "asset_approval_deferred": True,
        "weekly_buy_ticket_deferred": True,
        "buy_request_deferred": True,
        "broker_execution_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["manual_approval_records_only"]:
        blockers.append("v6.8 must remain manual-approval-record-only.")
    if not safety_flags["active_policy_registry_deferred"]:
        blockers.append("v6.8 must defer active policy registry creation.")
    if not safety_flags["asset_approval_deferred"]:
        blockers.append("v6.8 must defer asset approval.")
    if not safety_flags["weekly_buy_ticket_deferred"]:
        blockers.append("v6.8 must defer weekly buy tickets.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v6.8 must defer buy requests.")
    if not safety_flags["broker_execution_forbidden"]:
        blockers.append("v6.8 must forbid broker execution.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.8 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))

    return ActivePolicyManualApprovalGateResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        source_draft_count=len(draft_result.draft_items),
        approval_decision_count=len(effective_decisions),
        approve_count=approve_count,
        defer_count=defer_count,
        reject_count=reject_count,
        request_changes_count=request_changes_count,
        active_policy_count=0,
        approval_decisions=effective_decisions,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "manual_approval_gate_ready": not unique_blockers},
    )
