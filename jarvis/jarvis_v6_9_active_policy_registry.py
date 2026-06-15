"""J.A.R.V.I.S. v6.9 active policy registry.

This stage creates the active policy registry record from a manually approved
v6.8 active-policy draft.

Safety boundary:
- active policy record is allowed
- no asset approval
- no weekly buy ticket
- no buy request creation
- no broker/API execution
- no trades
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v6_5_policy_candidate_generator import AllocationBand, PolicyAssetSelection
from .jarvis_v6_7_active_policy_draft_registry import (
    ActivePolicyDraft,
    audit_v6_7_active_policy_draft_registry,
)
from .jarvis_v6_8_active_policy_manual_approval_gate import (
    DECISION_APPROVE_ACTIVE_POLICY_DRAFT,
    ActivePolicyApprovalDecision,
    audit_v6_8_active_policy_manual_approval_gate,
)


STATUS_READY = "JARVIS_V6_9_ACTIVE_POLICY_REGISTRY_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_9_ACTIVE_POLICY_REGISTRY_BLOCKED_SAFE"

NEXT_STAGE = "v6.10_active_policy_snapshot_gap_analyzer"

ACTIVE_POLICY_STATUS_ACTIVE_MANUAL_ONLY = "ACTIVE_POLICY_MANUAL_ONLY"
ACTIVE_POLICY_STATUS_BLOCKED = "ACTIVE_POLICY_BLOCKED"

SLEEVE_CRYPTO_CORE_BTC = "crypto_core_btc"
SLEEVE_CRYPTO_SPECULATIVE = "crypto_speculative"
SLEEVE_CASH_DEFENSIVE = "cash_defensive"
SLEEVE_BOND_DEFENSIVE = "bond_defensive"
SLEEVE_COMMODITY_DEFENSIVE = "commodity_defensive"


@dataclass(frozen=True)
class ActivePolicyRecord:
    active_policy_id: str
    source_approval_id: str
    source_draft_id: str
    source_policy_id: str
    display_name: str
    policy_status: str
    policy_version: str
    aggressiveness_score: int
    suitability_reason: str
    allocation_bands: tuple[AllocationBand, ...]
    selected_assets: tuple[PolicyAssetSelection, ...]
    policy_constraints: tuple[str, ...]
    monitoring_rules: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manually_approved: bool
    active_policy_created: bool
    automatic_policy_change_allowed: bool
    assets_individually_approved: bool
    creates_weekly_buy_ticket: bool
    creates_buy_request: bool
    connects_broker: bool
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

    def selected_candidate_ids(self) -> tuple[str, ...]:
        return tuple(selection.candidate_id for selection in self.selected_assets)

    def safe_active_policy_record_only(self) -> bool:
        return (
            self.manually_approved
            and self.active_policy_created
            and not self.automatic_policy_change_allowed
            and not self.assets_individually_approved
            and not self.creates_weekly_buy_ticket
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "active_policy_id": self.active_policy_id,
            "source_approval_id": self.source_approval_id,
            "source_draft_id": self.source_draft_id,
            "source_policy_id": self.source_policy_id,
            "display_name": self.display_name,
            "policy_status": self.policy_status,
            "policy_version": self.policy_version,
            "aggressiveness_score": self.aggressiveness_score,
            "suitability_reason": self.suitability_reason,
            "allocation_bands": [band.to_dict() for band in self.allocation_bands],
            "selected_assets": [selection.to_dict() for selection in self.selected_assets],
            "policy_constraints": list(self.policy_constraints),
            "monitoring_rules": list(self.monitoring_rules),
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manually_approved": self.manually_approved,
            "active_policy_created": self.active_policy_created,
            "automatic_policy_change_allowed": self.automatic_policy_change_allowed,
            "assets_individually_approved": self.assets_individually_approved,
            "creates_weekly_buy_ticket": self.creates_weekly_buy_ticket,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "executes_trade": self.executes_trade,
            "max_crypto_weight_pct": self.max_crypto_weight_pct(),
            "min_defensive_weight_pct": self.min_defensive_weight_pct(),
            "has_valid_bands": self.has_valid_bands(),
            "selected_candidate_ids": list(self.selected_candidate_ids()),
            "safe_active_policy_record_only": self.safe_active_policy_record_only(),
        }


@dataclass(frozen=True)
class ActivePolicyRegistryResult:
    status: str
    recommended_next_stage: str
    source_draft_count: int
    source_approval_decision_count: int
    approved_draft_count: int
    active_policy_count: int
    active_policies: tuple[ActivePolicyRecord, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    active_policy_registry_ready: bool
    active_policy_record_created: bool
    manual_approval_satisfied: bool
    automatic_policy_change_forbidden: bool
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
            "source_approval_decision_count": self.source_approval_decision_count,
            "approved_draft_count": self.approved_draft_count,
            "active_policy_count": self.active_policy_count,
            "active_policies": [policy.to_dict() for policy in self.active_policies],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "active_policy_registry_ready": self.active_policy_registry_ready,
            "active_policy_record_created": self.active_policy_record_created,
            "manual_approval_satisfied": self.manual_approval_satisfied,
            "automatic_policy_change_forbidden": self.automatic_policy_change_forbidden,
            "asset_approval_deferred": self.asset_approval_deferred,
            "weekly_buy_ticket_deferred": self.weekly_buy_ticket_deferred,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _active_policy_from_draft_and_approval(
    draft: ActivePolicyDraft,
    approval: ActivePolicyApprovalDecision,
) -> ActivePolicyRecord:
    return ActivePolicyRecord(
        active_policy_id=f"active_{draft.source_policy_id}",
        source_approval_id=approval.approval_id,
        source_draft_id=draft.draft_id,
        source_policy_id=draft.source_policy_id,
        display_name=draft.display_name.replace("Draft: ", "Active manual policy: "),
        policy_status=ACTIVE_POLICY_STATUS_ACTIVE_MANUAL_ONLY,
        policy_version="v6.9.0",
        aggressiveness_score=draft.aggressiveness_score,
        suitability_reason=draft.suitability_reason,
        allocation_bands=draft.allocation_bands,
        selected_assets=draft.selected_assets,
        policy_constraints=(
            "This active policy is manually approved and manual-use-only.",
            "No asset is individually approved by this registry record.",
            "Protected cash remains non-investable.",
            "Crypto maximum must remain at or below 35%.",
            "Speculative crypto remains excluded until quality improves and manual approval is repeated.",
            "Policy changes require a new manual approval path.",
        ),
        monitoring_rules=(
            "Monitor portfolio sleeve weights against allocation bands.",
            "Monitor investable cash separately from protected cash.",
            "Monitor source quality before any later weekly planning stage.",
            "Monitor crypto risk ceiling before any later weekly crypto recommendation.",
            "Generate only analysis until a later manual buy-planning stage exists.",
        ),
        warnings=(
            "Active policy exists for monitoring and planning context only.",
            "No weekly buy ticket or buy request is created by v6.9.",
            "No broker or execution route is attached.",
        ),
        blockers=(),
        manually_approved=True,
        active_policy_created=True,
        automatic_policy_change_allowed=False,
        assets_individually_approved=False,
        creates_weekly_buy_ticket=False,
        creates_buy_request=False,
        connects_broker=False,
        executes_trade=False,
    )


def build_active_policy_records_from_approvals(
    drafts: tuple[ActivePolicyDraft, ...],
    approvals: tuple[ActivePolicyApprovalDecision, ...],
) -> tuple[ActivePolicyRecord, ...]:
    drafts_by_id = {draft.draft_id: draft for draft in drafts}
    active_policies: list[ActivePolicyRecord] = []

    for approval in approvals:
        if approval.decision != DECISION_APPROVE_ACTIVE_POLICY_DRAFT:
            continue
        if not approval.authorizes_active_policy_registry_draft:
            continue
        draft = drafts_by_id.get(approval.draft_id)
        if draft is None:
            continue
        active_policies.append(_active_policy_from_draft_and_approval(draft, approval))

    return tuple(active_policies)


def audit_v6_9_active_policy_registry(
    active_policies: tuple[ActivePolicyRecord, ...] | None = None,
) -> ActivePolicyRegistryResult:
    draft_result = audit_v6_7_active_policy_draft_registry()
    approval_result = audit_v6_8_active_policy_manual_approval_gate()

    effective_active_policies = (
        build_active_policy_records_from_approvals(
            draft_result.draft_items,
            approval_result.approval_decisions,
        )
        if active_policies is None
        else active_policies
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.9 creates the active policy registry record for monitoring/planning context only.",
        "No weekly buy ticket, buy request, broker action, or trade is created.",
        "Policy changes require a later manual approval path.",
    ]

    if draft_result.blockers:
        blockers.append("Source active-policy draft registry is blocked.")
    if approval_result.blockers:
        blockers.append("Source manual approval gate is blocked.")

    approved_decisions = tuple(
        decision
        for decision in approval_result.approval_decisions
        if decision.decision == DECISION_APPROVE_ACTIVE_POLICY_DRAFT
        and decision.authorizes_active_policy_registry_draft
    )
    approved_draft_ids = {decision.draft_id for decision in approved_decisions}

    if not approved_decisions:
        blockers.append("No approved active-policy draft is available for registry creation.")
    if not effective_active_policies:
        blockers.append("No active policy registry record was created.")

    active_policy_ids = [policy.active_policy_id for policy in effective_active_policies]
    if len(active_policy_ids) != len(set(active_policy_ids)):
        blockers.append("Active policy IDs must be unique.")

    if len(effective_active_policies) > 1:
        blockers.append("Only one active policy record is allowed in v6.9.")

    policy_source_draft_ids = {policy.source_draft_id for policy in effective_active_policies}
    missing_active_records = approved_draft_ids - policy_source_draft_ids
    for draft_id in sorted(missing_active_records):
        blockers.append(f"Missing active policy record for approved draft: {draft_id}")

    for policy in effective_active_policies:
        if policy.source_draft_id not in approved_draft_ids:
            blockers.append(f"{policy.active_policy_id}: active policy must come from an approved draft.")
        if policy.policy_status != ACTIVE_POLICY_STATUS_ACTIVE_MANUAL_ONLY:
            blockers.append(f"{policy.active_policy_id}: invalid active policy status.")
        if not policy.manually_approved:
            blockers.append(f"{policy.active_policy_id}: manual approval is required.")
        if not policy.active_policy_created:
            blockers.append(f"{policy.active_policy_id}: active policy record must be created.")
        if policy.automatic_policy_change_allowed:
            blockers.append(f"{policy.active_policy_id}: automatic policy change is forbidden.")
        if policy.assets_individually_approved:
            blockers.append(f"{policy.active_policy_id}: asset approval is forbidden in v6.9.")
        if policy.creates_weekly_buy_ticket:
            blockers.append(f"{policy.active_policy_id}: weekly buy ticket creation is forbidden in v6.9.")
        if policy.creates_buy_request:
            blockers.append(f"{policy.active_policy_id}: buy request creation is forbidden in v6.9.")
        if policy.connects_broker:
            blockers.append(f"{policy.active_policy_id}: broker connection is forbidden in v6.9.")
        if policy.executes_trade:
            blockers.append(f"{policy.active_policy_id}: trade execution is forbidden in v6.9.")
        if not policy.safe_active_policy_record_only():
            blockers.append(f"{policy.active_policy_id}: policy must remain registry-record-only.")
        if not policy.has_valid_bands():
            blockers.append(f"{policy.active_policy_id}: invalid allocation bands.")
        if not policy.selected_assets:
            blockers.append(f"{policy.active_policy_id}: selected assets are required.")
        if policy.max_crypto_weight_pct() > 35.0:
            blockers.append(f"{policy.active_policy_id}: crypto max exceeds 35% safety ceiling.")
        if policy.min_defensive_weight_pct() < 3.0:
            blockers.append(f"{policy.active_policy_id}: minimum defensive allocation is too low.")
        if not policy.policy_constraints:
            blockers.append(f"{policy.active_policy_id}: policy constraints are required.")
        if not policy.monitoring_rules:
            blockers.append(f"{policy.active_policy_id}: monitoring rules are required.")

    safety_flags = {
        "active_policy_registry_ready": False,
        "active_policy_record_created": bool(effective_active_policies),
        "manual_approval_satisfied": bool(approved_decisions),
        "automatic_policy_change_forbidden": True,
        "asset_approval_deferred": True,
        "weekly_buy_ticket_deferred": True,
        "buy_request_deferred": True,
        "broker_execution_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["automatic_policy_change_forbidden"]:
        blockers.append("v6.9 must forbid automatic policy changes.")
    if not safety_flags["asset_approval_deferred"]:
        blockers.append("v6.9 must defer asset approval.")
    if not safety_flags["weekly_buy_ticket_deferred"]:
        blockers.append("v6.9 must defer weekly buy tickets.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v6.9 must defer buy requests.")
    if not safety_flags["broker_execution_forbidden"]:
        blockers.append("v6.9 must forbid broker execution.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.9 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))

    return ActivePolicyRegistryResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        source_draft_count=len(draft_result.draft_items),
        source_approval_decision_count=len(approval_result.approval_decisions),
        approved_draft_count=len(approved_decisions),
        active_policy_count=len(effective_active_policies),
        active_policies=effective_active_policies,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "active_policy_registry_ready": not unique_blockers},
    )
