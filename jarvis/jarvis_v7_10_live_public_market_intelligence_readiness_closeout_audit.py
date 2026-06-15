"""J.A.R.V.I.S. v7.10 live public market intelligence readiness closeout audit.

This stage closes out the v7 public market-intelligence preparation chain:

- v7.0 autonomous market intelligence expansion
- v7.1 public market intelligence adapter contract
- v7.2 fixture ingestion
- v7.3 live fetch boundary
- v7.4 dry-run planner
- v7.5 response normalizer contract
- v7.6 disabled live fetch adapter skeleton
- v7.7 enablement preflight
- v7.8 public provider configuration registry
- v7.9 provider skeleton binding audit

It does not enable live fetching.

Safety boundary:
- readiness closeout audit only
- live fetching remains disabled
- providers and adapters remain disabled by default
- no network calls attempted
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

from .jarvis_v7_0_autonomous_market_intelligence_expansion import (
    STATUS_READY as V7_0_STATUS_READY,
    audit_v7_0_autonomous_market_intelligence_expansion,
)
from .jarvis_v7_1_public_market_intelligence_adapter_contract import (
    STATUS_READY as V7_1_STATUS_READY,
    audit_v7_1_public_market_intelligence_adapter_contract,
)
from .jarvis_v7_2_public_market_intelligence_fixture_ingestion import (
    STATUS_READY as V7_2_STATUS_READY,
    audit_v7_2_public_market_intelligence_fixture_ingestion,
)
from .jarvis_v7_3_live_public_market_intelligence_fetcher_boundary import (
    STATUS_READY as V7_3_STATUS_READY,
    audit_v7_3_live_public_market_intelligence_fetcher_boundary,
)
from .jarvis_v7_4_live_public_market_intelligence_dry_run_planner import (
    STATUS_READY as V7_4_STATUS_READY,
    audit_v7_4_live_public_market_intelligence_dry_run_planner,
)
from .jarvis_v7_5_live_public_market_intelligence_response_normalizer_contract import (
    STATUS_READY as V7_5_STATUS_READY,
    audit_v7_5_live_public_market_intelligence_response_normalizer_contract,
)
from .jarvis_v7_6_disabled_live_public_market_fetch_adapter_skeleton import (
    STATUS_READY as V7_6_STATUS_READY,
    audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton,
)
from .jarvis_v7_7_live_public_market_intelligence_enablement_preflight import (
    STATUS_READY as V7_7_STATUS_READY,
    audit_v7_7_live_public_market_intelligence_enablement_preflight,
)
from .jarvis_v7_8_public_provider_configuration_registry import (
    STATUS_READY as V7_8_STATUS_READY,
    audit_v7_8_public_provider_configuration_registry,
)
from .jarvis_v7_9_public_provider_skeleton_binding_audit import (
    STATUS_READY as V7_9_STATUS_READY,
    audit_v7_9_public_provider_skeleton_binding_audit,
)


STATUS_READY = "JARVIS_V7_10_LIVE_PUBLIC_MARKET_INTELLIGENCE_READINESS_CLOSEOUT_AUDIT_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V7_10_LIVE_PUBLIC_MARKET_INTELLIGENCE_READINESS_CLOSEOUT_AUDIT_BLOCKED_SAFE"

NEXT_STAGE = "v8_0_public_market_intelligence_operator_dashboard"

CLOSEOUT_STATUS_READY = "LIVE_PUBLIC_MARKET_INTELLIGENCE_READINESS_CLOSEOUT_AUDIT_READY"
CLOSEOUT_STATUS_BLOCKED = "LIVE_PUBLIC_MARKET_INTELLIGENCE_READINESS_CLOSEOUT_AUDIT_BLOCKED"

CHECK_PASS = "PASS"
CHECK_FAIL = "FAIL"


@dataclass(frozen=True)
class LivePublicMarketReadinessCloseoutCheck:
    check_id: str
    stage_id: str
    title: str
    expected_status: str
    observed_status: str
    status: str
    evidence: str
    required_for_closeout: bool
    live_fetch_enabled: bool
    network_call_attempted: bool
    raw_response_stored: bool
    live_adapter_record_emitted: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def passed(self) -> bool:
        return self.status == CHECK_PASS

    def safe_closeout_check_only(self) -> bool:
        return (
            self.required_for_closeout
            and not self.live_fetch_enabled
            and not self.network_call_attempted
            and not self.raw_response_stored
            and not self.live_adapter_record_emitted
            and not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "stage_id": self.stage_id,
            "title": self.title,
            "expected_status": self.expected_status,
            "observed_status": self.observed_status,
            "status": self.status,
            "evidence": self.evidence,
            "required_for_closeout": self.required_for_closeout,
            "live_fetch_enabled": self.live_fetch_enabled,
            "network_call_attempted": self.network_call_attempted,
            "raw_response_stored": self.raw_response_stored,
            "live_adapter_record_emitted": self.live_adapter_record_emitted,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "passed": self.passed(),
            "safe_closeout_check_only": self.safe_closeout_check_only(),
        }


@dataclass(frozen=True)
class LivePublicMarketReadinessCloseoutAuditResult:
    status: str
    closeout_status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    check_count: int
    passed_check_count: int
    failed_check_count: int
    required_check_count: int
    chain_stage_count: int
    ready_chain_stage_count: int
    live_fetch_enablement_allowed: bool
    v7_chain_closeout_complete: bool
    checks: tuple[LivePublicMarketReadinessCloseoutCheck, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    readiness_closeout_ready: bool
    closeout_audit_only: bool
    providers_disabled_by_default: bool
    adapters_disabled_by_default: bool
    live_fetch_deferred: bool
    network_calls_deferred: bool
    raw_response_storage_deferred: bool
    live_adapter_record_emission_deferred: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "closeout_status": self.closeout_status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "check_count": self.check_count,
            "passed_check_count": self.passed_check_count,
            "failed_check_count": self.failed_check_count,
            "required_check_count": self.required_check_count,
            "chain_stage_count": self.chain_stage_count,
            "ready_chain_stage_count": self.ready_chain_stage_count,
            "live_fetch_enablement_allowed": self.live_fetch_enablement_allowed,
            "v7_chain_closeout_complete": self.v7_chain_closeout_complete,
            "checks": [check.to_dict() for check in self.checks],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "readiness_closeout_ready": self.readiness_closeout_ready,
            "closeout_audit_only": self.closeout_audit_only,
            "providers_disabled_by_default": self.providers_disabled_by_default,
            "adapters_disabled_by_default": self.adapters_disabled_by_default,
            "live_fetch_deferred": self.live_fetch_deferred,
            "network_calls_deferred": self.network_calls_deferred,
            "raw_response_storage_deferred": self.raw_response_storage_deferred,
            "live_adapter_record_emission_deferred": self.live_adapter_record_emission_deferred,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _blocker_count(result: object) -> int:
    blockers = getattr(result, "blockers", ())
    return len(blockers) if blockers is not None else 0


def _check(
    check_id: str,
    stage_id: str,
    title: str,
    expected_status: str,
    observed_status: str,
    evidence: str,
    condition: bool,
) -> LivePublicMarketReadinessCloseoutCheck:
    return LivePublicMarketReadinessCloseoutCheck(
        check_id=check_id,
        stage_id=stage_id,
        title=title,
        expected_status=expected_status,
        observed_status=observed_status,
        status=CHECK_PASS if condition else CHECK_FAIL,
        evidence=evidence,
        required_for_closeout=True,
        live_fetch_enabled=False,
        network_call_attempted=False,
        raw_response_stored=False,
        live_adapter_record_emitted=False,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_live_public_market_readiness_closeout_checks() -> tuple[
    LivePublicMarketReadinessCloseoutCheck, ...
]:
    v7_0 = audit_v7_0_autonomous_market_intelligence_expansion()
    v7_1 = audit_v7_1_public_market_intelligence_adapter_contract()
    v7_2 = audit_v7_2_public_market_intelligence_fixture_ingestion()
    v7_3 = audit_v7_3_live_public_market_intelligence_fetcher_boundary()
    v7_4 = audit_v7_4_live_public_market_intelligence_dry_run_planner()
    v7_5 = audit_v7_5_live_public_market_intelligence_response_normalizer_contract()
    v7_6 = audit_v7_6_disabled_live_public_market_fetch_adapter_skeleton()
    v7_7 = audit_v7_7_live_public_market_intelligence_enablement_preflight()
    v7_8 = audit_v7_8_public_provider_configuration_registry()
    v7_9 = audit_v7_9_public_provider_skeleton_binding_audit()

    return (
        _check(
            "v7_0_market_intelligence_ready",
            "v7.0",
            "Autonomous market intelligence expansion is ready",
            V7_0_STATUS_READY,
            v7_0.status,
            f"blocker_count={_blocker_count(v7_0)}",
            v7_0.status == V7_0_STATUS_READY and _blocker_count(v7_0) == 0,
        ),
        _check(
            "v7_1_adapter_contract_ready",
            "v7.1",
            "Public market intelligence adapter contract is ready",
            V7_1_STATUS_READY,
            v7_1.status,
            f"blocker_count={_blocker_count(v7_1)}",
            v7_1.status == V7_1_STATUS_READY and _blocker_count(v7_1) == 0,
        ),
        _check(
            "v7_2_fixture_ingestion_ready",
            "v7.2",
            "Public market intelligence fixture ingestion is ready",
            V7_2_STATUS_READY,
            v7_2.status,
            f"selected_candidate_id={v7_2.selected_candidate_id}; blocker_count={_blocker_count(v7_2)}",
            v7_2.status == V7_2_STATUS_READY and _blocker_count(v7_2) == 0,
        ),
        _check(
            "v7_3_fetch_boundary_ready",
            "v7.3",
            "Live public market fetch boundary is ready",
            V7_3_STATUS_READY,
            v7_3.status,
            f"fetch_boundary_request_count={v7_3.fetch_boundary_request_count}; network_call_attempt_count={v7_3.network_call_attempt_count}",
            v7_3.status == V7_3_STATUS_READY
            and v7_3.live_fetch_disabled_by_default
            and v7_3.network_calls_deferred
            and _blocker_count(v7_3) == 0,
        ),
        _check(
            "v7_4_dry_run_planner_ready",
            "v7.4",
            "Live public market dry-run planner is ready",
            V7_4_STATUS_READY,
            v7_4.status,
            f"dry_run_plan_count={v7_4.dry_run_plan_count}; planned_network_call_count={v7_4.planned_network_call_count}",
            v7_4.status == V7_4_STATUS_READY
            and v7_4.dry_run_only
            and v7_4.network_calls_deferred
            and _blocker_count(v7_4) == 0,
        ),
        _check(
            "v7_5_response_normalizer_ready",
            "v7.5",
            "Response normalizer contract is ready",
            V7_5_STATUS_READY,
            v7_5.status,
            f"normalized_adapter_record_count={v7_5.normalized_adapter_record_count}; raw_response_storage_count={v7_5.raw_response_storage_count}",
            v7_5.status == V7_5_STATUS_READY
            and v7_5.contract_only
            and v7_5.raw_response_storage_deferred
            and _blocker_count(v7_5) == 0,
        ),
        _check(
            "v7_6_disabled_adapter_skeleton_ready",
            "v7.6",
            "Disabled live public market fetch adapter skeleton is ready",
            V7_6_STATUS_READY,
            v7_6.status,
            f"skeleton_count={v7_6.skeleton_count}; enabled_adapter_count={v7_6.enabled_adapter_count}",
            v7_6.status == V7_6_STATUS_READY
            and v7_6.adapter_disabled_by_default
            and v7_6.live_adapter_record_emission_deferred
            and _blocker_count(v7_6) == 0,
        ),
        _check(
            "v7_7_enablement_preflight_ready",
            "v7.7",
            "Live public market enablement preflight is ready but does not enable live fetch",
            V7_7_STATUS_READY,
            v7_7.status,
            f"requirement_count={v7_7.requirement_count}; live_fetch_enablement_allowed={v7_7.live_fetch_enablement_allowed}",
            v7_7.status == V7_7_STATUS_READY
            and not v7_7.live_fetch_enablement_allowed
            and v7_7.preflight_only
            and _blocker_count(v7_7) == 0,
        ),
        _check(
            "v7_8_provider_registry_ready",
            "v7.8",
            "Public provider configuration registry is ready",
            V7_8_STATUS_READY,
            v7_8.status,
            f"provider_count={v7_8.provider_count}; enabled_provider_count={v7_8.enabled_provider_count}",
            v7_8.status == V7_8_STATUS_READY
            and v7_8.providers_disabled_by_default
            and v7_8.network_calls_deferred
            and _blocker_count(v7_8) == 0,
        ),
        _check(
            "v7_9_binding_audit_ready",
            "v7.9",
            "Public provider skeleton binding audit is ready",
            V7_9_STATUS_READY,
            v7_9.status,
            f"binding_count={v7_9.binding_count}; unbound_skeleton_count={v7_9.unbound_skeleton_count}",
            v7_9.status == V7_9_STATUS_READY
            and v7_9.unbound_skeleton_count == 0
            and v7_9.providers_disabled_by_default
            and v7_9.adapters_disabled_by_default
            and _blocker_count(v7_9) == 0,
        ),
        _check(
            "v7_chain_no_live_fetch_closeout",
            "v7.10",
            "Full v7 chain remains non-live and non-executable",
            CHECK_PASS,
            CHECK_PASS,
            (
                f"v7_7_live_fetch_enablement_allowed={v7_7.live_fetch_enablement_allowed}; "
                f"v7_9_live_fetch_enabled_count={v7_9.live_fetch_enabled_count}; "
                f"v7_9_network_call_allowed_count={v7_9.network_call_allowed_count}; "
                f"v7_9_raw_response_storage_allowed_count={v7_9.raw_response_storage_allowed_count}; "
                f"v7_9_live_adapter_record_emission_allowed_count={v7_9.live_adapter_record_emission_allowed_count}"
            ),
            not v7_7.live_fetch_enablement_allowed
            and v7_9.live_fetch_enabled_count == 0
            and v7_9.network_call_allowed_count == 0
            and v7_9.raw_response_storage_allowed_count == 0
            and v7_9.live_adapter_record_emission_allowed_count == 0
            and v7_9.buy_request_deferred
            and v7_9.broker_connection_forbidden
            and v7_9.order_placement_forbidden
            and v7_9.no_trades_executed,
        ),
    )


def audit_v7_10_live_public_market_intelligence_readiness_closeout_audit(
    checks: tuple[LivePublicMarketReadinessCloseoutCheck, ...] | None | object = None,
) -> LivePublicMarketReadinessCloseoutAuditResult:
    v7_9 = audit_v7_9_public_provider_skeleton_binding_audit()

    if checks is None:
        effective_checks = build_live_public_market_readiness_closeout_checks()
        invalid_override = False
    elif isinstance(checks, tuple):
        effective_checks = checks
        invalid_override = False
    else:
        effective_checks = ()
        invalid_override = True

    blockers: list[str] = []
    warnings: list[str] = [
        "v7.10 is a readiness closeout audit only.",
        "Passing v7.10 means the live-public-intelligence preparation chain is closed out, not that live fetching is enabled.",
        "No live public network call is attempted in v7.10.",
        "No raw public response payload is stored in v7.10.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if invalid_override:
        blockers.append("Closeout check override must be a tuple of LivePublicMarketReadinessCloseoutCheck.")

    if v7_9.status != V7_9_STATUS_READY or v7_9.blockers:
        blockers.append("Source v7.9 public provider skeleton binding audit is blocked.")

    if not effective_checks:
        blockers.append("No live public market readiness closeout checks were produced.")

    check_ids: list[str] = []
    clean_checks: list[LivePublicMarketReadinessCloseoutCheck] = []

    for index, check in enumerate(effective_checks):
        if not isinstance(check, LivePublicMarketReadinessCloseoutCheck):
            blockers.append(f"Closeout check at index {index} must be a LivePublicMarketReadinessCloseoutCheck.")
            continue

        clean_checks.append(check)
        check_ids.append(check.check_id)

        if not check.check_id.strip():
            blockers.append("Closeout check ID is required.")
        if not check.stage_id.strip():
            blockers.append(f"{check.check_id}: stage ID is required.")
        if not check.title.strip():
            blockers.append(f"{check.check_id}: title is required.")
        if not check.expected_status.strip():
            blockers.append(f"{check.check_id}: expected status is required.")
        if not check.observed_status.strip():
            blockers.append(f"{check.check_id}: observed status is required.")
        if check.status not in {CHECK_PASS, CHECK_FAIL}:
            blockers.append(f"{check.check_id}: status must be PASS or FAIL.")
        if not check.evidence.strip():
            blockers.append(f"{check.check_id}: evidence is required.")
        if not check.required_for_closeout:
            blockers.append(f"{check.check_id}: check must be required for closeout.")
        if not check.passed():
            blockers.append(f"{check.check_id}: closeout check failed.")
        if not check.safe_closeout_check_only():
            blockers.append(f"{check.check_id}: closeout check must remain audit-only and non-executable.")
        if check.live_fetch_enabled:
            blockers.append(f"{check.check_id}: live fetching is forbidden in v7.10.")
        if check.network_call_attempted:
            blockers.append(f"{check.check_id}: network calls are forbidden in v7.10.")
        if check.raw_response_stored:
            blockers.append(f"{check.check_id}: raw response storage is forbidden in v7.10.")
        if check.live_adapter_record_emitted:
            blockers.append(f"{check.check_id}: live adapter record emission is forbidden in v7.10.")
        if check.creates_buy_request:
            blockers.append(f"{check.check_id}: buy request creation is forbidden.")
        if check.connects_broker:
            blockers.append(f"{check.check_id}: broker connection is forbidden.")
        if check.places_order:
            blockers.append(f"{check.check_id}: order placement is forbidden.")
        if check.executes_trade:
            blockers.append(f"{check.check_id}: trade execution is forbidden.")

    if len(check_ids) != len(set(check_ids)):
        blockers.append("Live public market readiness closeout check IDs must be unique.")

    clean_check_tuple = tuple(clean_checks)
    passed_count = sum(1 for check in clean_check_tuple if check.passed())
    failed_count = len(clean_check_tuple) - passed_count
    required_count = sum(1 for check in clean_check_tuple if check.required_for_closeout)

    stage_ids = {check.stage_id for check in clean_check_tuple if check.stage_id.startswith("v7.")}
    chain_stage_count = len(stage_ids)
    ready_chain_stage_count = sum(
        1
        for check in clean_check_tuple
        if check.stage_id.startswith("v7.")
        and check.passed()
        and check.observed_status == check.expected_status
    )

    required_stage_ids = {
        "v7.0",
        "v7.1",
        "v7.2",
        "v7.3",
        "v7.4",
        "v7.5",
        "v7.6",
        "v7.7",
        "v7.8",
        "v7.9",
    }
    missing_stage_ids = sorted(required_stage_ids - stage_ids)
    if missing_stage_ids:
        blockers.append("Closeout audit must cover every v7.0-v7.9 stage.")

    live_fetch_enablement_allowed = False

    v7_chain_closeout_complete = (
        not missing_stage_ids
        and failed_count == 0
        and chain_stage_count >= 10
        and ready_chain_stage_count >= 10
        and not live_fetch_enablement_allowed
    )

    safety_flags = {
        "readiness_closeout_ready": False,
        "closeout_audit_only": True,
        "providers_disabled_by_default": v7_9.providers_disabled_by_default,
        "adapters_disabled_by_default": v7_9.adapters_disabled_by_default,
        "live_fetch_deferred": v7_9.live_fetch_deferred and not live_fetch_enablement_allowed,
        "network_calls_deferred": v7_9.network_calls_deferred,
        "raw_response_storage_deferred": v7_9.raw_response_storage_deferred,
        "live_adapter_record_emission_deferred": v7_9.live_adapter_record_emission_deferred,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if live_fetch_enablement_allowed:
        blockers.append("v7.10 must not allow live fetch enablement.")
    if not v7_chain_closeout_complete:
        blockers.append("v7 live-public-intelligence preparation chain closeout is incomplete.")
    if not safety_flags["closeout_audit_only"]:
        blockers.append("v7.10 must remain closeout-audit-only.")
    if not safety_flags["providers_disabled_by_default"]:
        blockers.append("v7.10 must keep all providers disabled by default.")
    if not safety_flags["adapters_disabled_by_default"]:
        blockers.append("v7.10 must keep all adapters disabled by default.")
    if not safety_flags["live_fetch_deferred"]:
        blockers.append("v7.10 must defer live fetching.")
    if not safety_flags["network_calls_deferred"]:
        blockers.append("v7.10 must defer network calls.")
    if not safety_flags["raw_response_storage_deferred"]:
        blockers.append("v7.10 must defer raw response storage.")
    if not safety_flags["live_adapter_record_emission_deferred"]:
        blockers.append("v7.10 must defer live adapter record emission.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v7.10 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v7.10 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v7.10 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v7.10 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return LivePublicMarketReadinessCloseoutAuditResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        closeout_status=CLOSEOUT_STATUS_READY if ready else CLOSEOUT_STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=v7_9.selected_candidate_id,
        selected_sleeve_id=v7_9.selected_sleeve_id,
        check_count=len(clean_check_tuple),
        passed_check_count=passed_count,
        failed_check_count=failed_count,
        required_check_count=required_count,
        chain_stage_count=chain_stage_count,
        ready_chain_stage_count=ready_chain_stage_count,
        live_fetch_enablement_allowed=live_fetch_enablement_allowed,
        v7_chain_closeout_complete=v7_chain_closeout_complete,
        checks=clean_check_tuple,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "readiness_closeout_ready": ready},
    )
