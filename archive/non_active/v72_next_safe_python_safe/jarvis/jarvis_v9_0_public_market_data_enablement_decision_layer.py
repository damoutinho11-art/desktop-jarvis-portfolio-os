"""J.A.R.V.I.S. v9.0 public market data enablement decision layer.

Uses the completed v7 readiness chain and v8 operator command-center closeout
to decide what is allowed next for public market data.

This does not select sources again.
This does not enable live fetching.
This does not make network calls.

Safety boundary:
- enablement decision only
- dry-run planning may be marked allowed
- live mode remains blocked
- explicit operator authorization remains required before any future live-public-data stage
- no raw response storage
- no live adapter record emission
- no buy request creation
- no broker/API connection
- no order placement
- no trade execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v7_10_live_public_market_intelligence_readiness_closeout_audit import (
    STATUS_READY as V7_10_STATUS_READY,
    audit_v7_10_live_public_market_intelligence_readiness_closeout_audit,
)
from .jarvis_v8_4_operator_command_center_closeout import (
    STATUS_READY as V8_4_STATUS_READY,
    audit_v8_4_operator_command_center_closeout,
)


STATUS_READY = "JARVIS_V9_0_PUBLIC_MARKET_DATA_ENABLEMENT_DECISION_LAYER_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V9_0_PUBLIC_MARKET_DATA_ENABLEMENT_DECISION_LAYER_BLOCKED_SAFE"

DECISION_LAYER_READY = "PUBLIC_MARKET_DATA_ENABLEMENT_DECISION_LAYER_READY"
DECISION_LAYER_BLOCKED = "PUBLIC_MARKET_DATA_ENABLEMENT_DECISION_LAYER_BLOCKED"

NEXT_STAGE = "v9_1_capability_map_and_roadmap_lock"

DECISION_DRY_RUN_ALLOWED = "DRY_RUN_ONLY_ALLOWED"
DECISION_LIVE_BLOCKED = "LIVE_MODE_BLOCKED"
DECISION_AUTH_REQUIRED = "EXPLICIT_OPERATOR_AUTHORIZATION_REQUIRED"
DECISION_READY_FOR_NEXT_PLAN = "READY_FOR_NEXT_ENABLEMENT_PLAN"


@dataclass(frozen=True)
class PublicMarketDataEnablementDecision:
    decision_id: str
    title: str
    decision: str
    reason: str
    evidence: str
    allowed_in_dry_run: bool
    live_mode_allowed: bool
    requires_explicit_operator_authorization: bool
    blocks_live_fetch: bool
    user_visible: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool
    network_call_enabled: bool
    raw_response_storage_enabled: bool
    live_adapter_record_emission_enabled: bool

    def safe_decision_only(self) -> bool:
        return (
            self.user_visible
            and not self.live_mode_allowed
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
            and not self.network_call_enabled
            and not self.raw_response_storage_enabled
            and not self.live_adapter_record_emission_enabled
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "title": self.title,
            "decision": self.decision,
            "reason": self.reason,
            "evidence": self.evidence,
            "allowed_in_dry_run": self.allowed_in_dry_run,
            "live_mode_allowed": self.live_mode_allowed,
            "requires_explicit_operator_authorization": self.requires_explicit_operator_authorization,
            "blocks_live_fetch": self.blocks_live_fetch,
            "user_visible": self.user_visible,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "network_call_enabled": self.network_call_enabled,
            "raw_response_storage_enabled": self.raw_response_storage_enabled,
            "live_adapter_record_emission_enabled": self.live_adapter_record_emission_enabled,
            "safe_decision_only": self.safe_decision_only(),
        }


@dataclass(frozen=True)
class PublicMarketDataEnablementDecisionLayerResult:
    status: str
    decision_layer_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    decision_count: int
    dry_run_allowed_decision_count: int
    live_allowed_decision_count: int
    authorization_required_decision_count: int
    live_blocking_decision_count: int
    compatible_with_v7_10_readiness_closeout: bool
    compatible_with_v8_4_command_center_closeout: bool
    decisions: tuple[PublicMarketDataEnablementDecision, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    enablement_decision_layer_ready: bool
    source_selection_not_repeated: bool
    dry_run_planning_allowed: bool
    live_mode_blocked: bool
    explicit_operator_authorization_required: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool
    network_calls_deferred: bool
    raw_response_storage_deferred: bool
    live_adapter_record_emission_deferred: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "decision_layer_status": self.decision_layer_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "decision_count": self.decision_count,
            "dry_run_allowed_decision_count": self.dry_run_allowed_decision_count,
            "live_allowed_decision_count": self.live_allowed_decision_count,
            "authorization_required_decision_count": self.authorization_required_decision_count,
            "live_blocking_decision_count": self.live_blocking_decision_count,
            "compatible_with_v7_10_readiness_closeout": self.compatible_with_v7_10_readiness_closeout,
            "compatible_with_v8_4_command_center_closeout": self.compatible_with_v8_4_command_center_closeout,
            "decisions": [decision.to_dict() for decision in self.decisions],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "enablement_decision_layer_ready": self.enablement_decision_layer_ready,
            "source_selection_not_repeated": self.source_selection_not_repeated,
            "dry_run_planning_allowed": self.dry_run_planning_allowed,
            "live_mode_blocked": self.live_mode_blocked,
            "explicit_operator_authorization_required": self.explicit_operator_authorization_required,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "network_calls_deferred": self.network_calls_deferred,
            "raw_response_storage_deferred": self.raw_response_storage_deferred,
            "live_adapter_record_emission_deferred": self.live_adapter_record_emission_deferred,
        }


def _decision(
    decision_id: str,
    title: str,
    decision: str,
    reason: str,
    evidence: str,
    allowed_in_dry_run: bool,
    requires_explicit_operator_authorization: bool,
    blocks_live_fetch: bool,
) -> PublicMarketDataEnablementDecision:
    return PublicMarketDataEnablementDecision(
        decision_id=decision_id,
        title=title,
        decision=decision,
        reason=reason,
        evidence=evidence,
        allowed_in_dry_run=allowed_in_dry_run,
        live_mode_allowed=False,
        requires_explicit_operator_authorization=requires_explicit_operator_authorization,
        blocks_live_fetch=blocks_live_fetch,
        user_visible=True,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
        network_call_enabled=False,
        raw_response_storage_enabled=False,
        live_adapter_record_emission_enabled=False,
    )


def build_public_market_data_enablement_decisions() -> tuple[
    PublicMarketDataEnablementDecision, ...
]:
    readiness = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()
    closeout = audit_v8_4_operator_command_center_closeout()

    return (
        _decision(
            "existing_readiness_chain_accepted",
            "Existing readiness chain accepted",
            DECISION_READY_FOR_NEXT_PLAN,
            "v7.10 readiness and v8.4 command-center closeout are complete, so J.A.R.V.I.S. can move to controlled dry-run planning.",
            (
                f"v7_10_status={readiness.status}; "
                f"v8_4_status={closeout.status}; "
                f"v8_product_layer_complete={closeout.v8_product_layer_complete}"
            ),
            True,
            False,
            True,
        ),
        _decision(
            "source_selection_not_repeated",
            "Source selection is not repeated",
            DECISION_READY_FOR_NEXT_PLAN,
            "Prior source/provider work already exists; v9.0 uses readiness evidence instead of creating another source matrix.",
            (
                f"chain_stage_count={readiness.chain_stage_count}; "
                f"check_count={readiness.check_count}; "
                f"passed_check_count={readiness.passed_check_count}"
            ),
            True,
            False,
            True,
        ),
        _decision(
            "dry_run_public_data_path_allowed",
            "Dry-run public data path allowed",
            DECISION_DRY_RUN_ALLOWED,
            "Dry-run planning is allowed because providers and adapters remain disabled and no network calls are enabled.",
            (
                f"providers_disabled_by_default={readiness.providers_disabled_by_default}; "
                f"adapters_disabled_by_default={readiness.adapters_disabled_by_default}; "
                f"network_calls_deferred={readiness.network_calls_deferred}"
            ),
            True,
            True,
            True,
        ),
        _decision(
            "live_public_fetch_blocked",
            "Live public fetch remains blocked",
            DECISION_LIVE_BLOCKED,
            "Live fetching is still blocked until a future explicit operator-authorized stage.",
            (
                f"live_fetch_enablement_allowed={readiness.live_fetch_enablement_allowed}; "
                f"live_fetch_deferred={readiness.live_fetch_deferred}; "
                f"raw_response_storage_deferred={readiness.raw_response_storage_deferred}"
            ),
            False,
            True,
            True,
        ),
        _decision(
            "live_adapter_emission_blocked",
            "Live adapter record emission remains blocked",
            DECISION_LIVE_BLOCKED,
            "Live adapter records cannot be emitted before controlled dry-run planning and explicit live authorization.",
            (
                f"live_adapter_record_emission_deferred={readiness.live_adapter_record_emission_deferred}; "
                f"selected_candidate_id={readiness.selected_candidate_id}; "
                f"selected_sleeve_id={readiness.selected_sleeve_id}"
            ),
            False,
            True,
            True,
        ),
        _decision(
            "execution_boundary_preserved",
            "Execution boundary preserved",
            DECISION_AUTH_REQUIRED,
            "Market data enablement decisions cannot create investment execution actions.",
            (
                f"buy_request_deferred={readiness.buy_request_deferred}; "
                f"broker_connection_forbidden={readiness.broker_connection_forbidden}; "
                f"order_placement_forbidden={readiness.order_placement_forbidden}; "
                f"no_trades_executed={readiness.no_trades_executed}"
            ),
            False,
            True,
            True,
        ),
    )


def audit_v9_0_public_market_data_enablement_decision_layer(
    decisions: tuple[PublicMarketDataEnablementDecision, ...] | None | object = None,
) -> PublicMarketDataEnablementDecisionLayerResult:
    readiness = audit_v7_10_live_public_market_intelligence_readiness_closeout_audit()
    closeout = audit_v8_4_operator_command_center_closeout()

    if decisions is None:
        effective_decisions = build_public_market_data_enablement_decisions()
        invalid_override = False
    elif isinstance(decisions, tuple):
        effective_decisions = decisions
        invalid_override = False
    else:
        effective_decisions = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v9.0 is an enablement decision layer only.",
        "v9.0 does not repeat source selection.",
        "Dry-run public-data planning may be allowed.",
        "Live public fetching remains blocked.",
        "Explicit operator authorization is required before any future live-public-data stage.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Decision override must be a tuple of PublicMarketDataEnablementDecision.")

    if readiness.status != V7_10_STATUS_READY or readiness.blockers:
        blockers.append("Source v7.10 readiness closeout is blocked.")
    if closeout.status != V8_4_STATUS_READY or closeout.blockers:
        blockers.append("Source v8.4 command-center closeout is blocked.")
    if not effective_decisions:
        blockers.append("No public market data enablement decisions were produced.")

    clean_decisions: list[PublicMarketDataEnablementDecision] = []
    decision_ids: list[str] = []

    allowed_decisions = {
        DECISION_DRY_RUN_ALLOWED,
        DECISION_LIVE_BLOCKED,
        DECISION_AUTH_REQUIRED,
        DECISION_READY_FOR_NEXT_PLAN,
    }

    for index, decision in enumerate(effective_decisions):
        if not isinstance(decision, PublicMarketDataEnablementDecision):
            blockers.append(f"Decision at index {index} must be a PublicMarketDataEnablementDecision.")
            continue

        clean_decisions.append(decision)
        decision_ids.append(decision.decision_id)

        if not decision.decision_id.strip():
            blockers.append("Decision ID is required.")
        if not decision.title.strip():
            blockers.append(f"{decision.decision_id}: title is required.")
        if decision.decision not in allowed_decisions:
            blockers.append(f"{decision.decision_id}: decision value is not allowed.")
        if not decision.reason.strip():
            blockers.append(f"{decision.decision_id}: reason is required.")
        if not decision.evidence.strip():
            blockers.append(f"{decision.decision_id}: evidence is required.")
        if not decision.user_visible:
            blockers.append(f"{decision.decision_id}: decision must be user-visible.")
        if decision.live_mode_allowed:
            blockers.append(f"{decision.decision_id}: live mode must not be allowed in v9.0.")
        if not decision.safe_decision_only():
            blockers.append(f"{decision.decision_id}: decision must remain visible, non-live, and non-executable.")
        if decision.creates_buy_request:
            blockers.append(f"{decision.decision_id}: buy request creation is forbidden.")
        if decision.connects_broker:
            blockers.append(f"{decision.decision_id}: broker connection is forbidden.")
        if decision.places_order:
            blockers.append(f"{decision.decision_id}: order placement is forbidden.")
        if decision.executes_trade:
            blockers.append(f"{decision.decision_id}: trade execution is forbidden.")
        if decision.network_call_enabled:
            blockers.append(f"{decision.decision_id}: network calls are forbidden.")
        if decision.raw_response_storage_enabled:
            blockers.append(f"{decision.decision_id}: raw response storage is forbidden.")
        if decision.live_adapter_record_emission_enabled:
            blockers.append(f"{decision.decision_id}: live adapter record emission is forbidden.")

    if len(decision_ids) != len(set(decision_ids)):
        blockers.append("Public market data enablement decision IDs must be unique.")

    required_ids = {
        "existing_readiness_chain_accepted",
        "source_selection_not_repeated",
        "dry_run_public_data_path_allowed",
        "live_public_fetch_blocked",
        "live_adapter_emission_blocked",
        "execution_boundary_preserved",
    }
    if required_ids - set(decision_ids):
        blockers.append("Decision layer must include all required enablement decisions.")

    clean_tuple = tuple(clean_decisions)

    dry_run_allowed_count = sum(1 for decision in clean_tuple if decision.allowed_in_dry_run)
    live_allowed_count = sum(1 for decision in clean_tuple if decision.live_mode_allowed)
    auth_required_count = sum(
        1 for decision in clean_tuple if decision.requires_explicit_operator_authorization
    )
    live_blocking_count = sum(1 for decision in clean_tuple if decision.blocks_live_fetch)

    safety_flags = {
        "enablement_decision_layer_ready": False,
        "source_selection_not_repeated": "source_selection_not_repeated" in set(decision_ids),
        "dry_run_planning_allowed": dry_run_allowed_count > 0,
        "live_mode_blocked": live_allowed_count == 0 and live_blocking_count > 0,
        "explicit_operator_authorization_required": auth_required_count > 0,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
        "network_calls_deferred": True,
        "raw_response_storage_deferred": True,
        "live_adapter_record_emission_deferred": True,
    }

    if not safety_flags["source_selection_not_repeated"]:
        blockers.append("v9.0 must not repeat source selection.")
    if not safety_flags["dry_run_planning_allowed"]:
        blockers.append("v9.0 must allow only controlled dry-run planning.")
    if not safety_flags["live_mode_blocked"]:
        blockers.append("v9.0 must keep live mode blocked.")
    if not safety_flags["explicit_operator_authorization_required"]:
        blockers.append("v9.0 must require explicit operator authorization before any future live stage.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return PublicMarketDataEnablementDecisionLayerResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        decision_layer_status=DECISION_LAYER_READY if ready else DECISION_LAYER_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=readiness.selected_candidate_id,
        selected_sleeve_id=readiness.selected_sleeve_id,
        decision_count=len(clean_tuple),
        dry_run_allowed_decision_count=dry_run_allowed_count,
        live_allowed_decision_count=live_allowed_count,
        authorization_required_decision_count=auth_required_count,
        live_blocking_decision_count=live_blocking_count,
        compatible_with_v7_10_readiness_closeout=readiness.status == V7_10_STATUS_READY,
        compatible_with_v8_4_command_center_closeout=closeout.status == V8_4_STATUS_READY,
        decisions=clean_tuple,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "enablement_decision_layer_ready": ready},
    )

