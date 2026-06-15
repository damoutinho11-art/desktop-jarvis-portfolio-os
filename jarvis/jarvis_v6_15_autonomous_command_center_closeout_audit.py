"""J.A.R.V.I.S. v6.15 autonomous command center closeout audit.

This stage audits the complete v6 autonomous intelligence chain:

active policy -> snapshot gaps -> planning context -> shortlist ->
autonomous weekly recommendation -> dashboard visibility.

Safety boundary:
- closeout audit only
- no manual review queue
- no buy request creation
- no broker/API connection
- no order placement
- no trade execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v6_10_active_policy_snapshot_gap_analyzer import (
    audit_v6_10_active_policy_snapshot_gap_analyzer,
)
from .jarvis_v6_11_manual_weekly_planning_context_builder import (
    audit_v6_11_manual_weekly_planning_context_builder,
)
from .jarvis_v6_12_manual_weekly_candidate_shortlist_builder import (
    audit_v6_12_manual_weekly_candidate_shortlist_builder,
)
from .jarvis_v6_13_autonomous_weekly_recommendation_draft_builder import (
    audit_v6_13_autonomous_weekly_recommendation_draft_builder,
)
from .jarvis_v6_14_recommendation_dashboard_integration import (
    audit_v6_14_recommendation_dashboard_integration,
)


STATUS_READY = "JARVIS_V6_15_AUTONOMOUS_COMMAND_CENTER_CLOSEOUT_AUDIT_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_15_AUTONOMOUS_COMMAND_CENTER_CLOSEOUT_AUDIT_BLOCKED_SAFE"

NEXT_STAGE = "v7_0_autonomous_market_intelligence_expansion"

CHECK_PASS = "PASS"
CHECK_FAIL = "FAIL"


@dataclass(frozen=True)
class AutonomousCommandCenterCloseoutCheck:
    check_id: str
    title: str
    status: str
    evidence: str
    blocker_if_failed: str
    no_buy_request: bool
    no_broker_connection: bool
    no_order_placement: bool
    no_trade_execution: bool

    def passed(self) -> bool:
        return self.status == CHECK_PASS

    def safe_check_only(self) -> bool:
        return (
            self.no_buy_request
            and self.no_broker_connection
            and self.no_order_placement
            and self.no_trade_execution
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "title": self.title,
            "status": self.status,
            "evidence": self.evidence,
            "blocker_if_failed": self.blocker_if_failed,
            "no_buy_request": self.no_buy_request,
            "no_broker_connection": self.no_broker_connection,
            "no_order_placement": self.no_order_placement,
            "no_trade_execution": self.no_trade_execution,
            "passed": self.passed(),
            "safe_check_only": self.safe_check_only(),
        }


@dataclass(frozen=True)
class AutonomousCommandCenterCloseoutAuditResult:
    status: str
    recommended_next_stage: str
    analyzed_policy_id: str
    selected_candidate_id: str
    selected_sleeve_id: str
    check_count: int
    passed_check_count: int
    failed_check_count: int
    v6_chain_complete: bool
    autonomous_intelligence_ready: bool
    command_center_ready: bool
    final_user_buy_action_required: bool
    checks: tuple[AutonomousCommandCenterCloseoutCheck, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    closeout_audit_ready: bool
    no_manual_review_queue_added: bool
    no_buy_request_created: bool
    no_broker_connection_created: bool
    no_order_placement_created: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "analyzed_policy_id": self.analyzed_policy_id,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "check_count": self.check_count,
            "passed_check_count": self.passed_check_count,
            "failed_check_count": self.failed_check_count,
            "v6_chain_complete": self.v6_chain_complete,
            "autonomous_intelligence_ready": self.autonomous_intelligence_ready,
            "command_center_ready": self.command_center_ready,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "checks": [check.to_dict() for check in self.checks],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "closeout_audit_ready": self.closeout_audit_ready,
            "no_manual_review_queue_added": self.no_manual_review_queue_added,
            "no_buy_request_created": self.no_buy_request_created,
            "no_broker_connection_created": self.no_broker_connection_created,
            "no_order_placement_created": self.no_order_placement_created,
            "no_trades_executed": self.no_trades_executed,
        }


def _check(
    check_id: str,
    title: str,
    condition: bool,
    evidence: str,
    blocker_if_failed: str,
) -> AutonomousCommandCenterCloseoutCheck:
    return AutonomousCommandCenterCloseoutCheck(
        check_id=check_id,
        title=title,
        status=CHECK_PASS if condition else CHECK_FAIL,
        evidence=evidence,
        blocker_if_failed=blocker_if_failed,
        no_buy_request=True,
        no_broker_connection=True,
        no_order_placement=True,
        no_trade_execution=True,
    )


def build_v6_15_closeout_checks() -> tuple[AutonomousCommandCenterCloseoutCheck, ...]:
    gap_result = audit_v6_10_active_policy_snapshot_gap_analyzer()
    planning_result = audit_v6_11_manual_weekly_planning_context_builder()
    shortlist_result = audit_v6_12_manual_weekly_candidate_shortlist_builder()
    recommendation_result = audit_v6_13_autonomous_weekly_recommendation_draft_builder()
    dashboard_result = audit_v6_14_recommendation_dashboard_integration()

    return (
        _check(
            "active_policy_gap_analysis_ready",
            "Active policy can be compared with snapshot gaps",
            gap_result.gap_analyzer_ready and gap_result.sleeve_gap_count > 0,
            f"sleeve_gap_count={gap_result.sleeve_gap_count}; analyzed_policy_id={gap_result.analyzed_policy_id}",
            "Active policy snapshot gap analysis is not ready.",
        ),
        _check(
            "weekly_planning_context_ready",
            "Weekly planning context is available",
            planning_result.weekly_planning_context_ready
            and planning_result.planning_context_item_count > 0,
            f"planning_context_item_count={planning_result.planning_context_item_count}",
            "Manual weekly planning context is not ready.",
        ),
        _check(
            "weekly_shortlist_ready",
            "Weekly candidate shortlist is available",
            shortlist_result.manual_weekly_shortlist_ready
            and shortlist_result.shortlist_candidate_count > 0,
            f"shortlist_candidate_count={shortlist_result.shortlist_candidate_count}",
            "Manual weekly candidate shortlist is not ready.",
        ),
        _check(
            "autonomous_recommendation_ready",
            "Autonomous weekly recommendation draft is available",
            recommendation_result.autonomous_recommendation_ready
            and recommendation_result.recommendation_count == 1,
            f"selected_candidate_id={recommendation_result.selected_candidate_id}; selected_sleeve_id={recommendation_result.selected_sleeve_id}",
            "Autonomous weekly recommendation draft is not ready.",
        ),
        _check(
            "dashboard_integration_ready",
            "Recommendation is visible in command-center dashboard payload",
            dashboard_result.dashboard_integration_ready
            and dashboard_result.dashboard_card_count == 3
            and dashboard_result.autonomous_recommendation_displayed,
            f"dashboard_card_count={dashboard_result.dashboard_card_count}; selected_candidate_id={dashboard_result.selected_candidate_id}",
            "Recommendation dashboard integration is not ready.",
        ),
        _check(
            "only_final_buy_is_manual",
            "Only final real-world buy remains manual",
            recommendation_result.final_user_buy_action_required
            and dashboard_result.final_user_buy_action_required,
            "final_user_buy_action_required=True",
            "Final user buy action boundary is not explicit.",
        ),
        _check(
            "no_execution_path_exists",
            "No executable trading path exists",
            recommendation_result.buy_request_deferred
            and recommendation_result.broker_connection_forbidden
            and recommendation_result.order_placement_forbidden
            and recommendation_result.no_trades_executed
            and dashboard_result.buy_request_deferred
            and dashboard_result.broker_connection_forbidden
            and dashboard_result.order_placement_forbidden
            and dashboard_result.no_trades_executed,
            "buy_request=False; broker=False; order=False; trade=False",
            "An execution path was detected.",
        ),
    )


def audit_v6_15_autonomous_command_center_closeout_audit(
    checks: tuple[AutonomousCommandCenterCloseoutCheck, ...] | None = None,
) -> AutonomousCommandCenterCloseoutAuditResult:
    dashboard_result = audit_v6_14_recommendation_dashboard_integration()
    effective_checks = build_v6_15_closeout_checks() if checks is None else checks

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.15 is a closeout audit, not another manual review queue.",
        "J.A.R.V.I.S. is autonomous intelligence up to the user's final real-world buy.",
        "Next work should expand autonomous market intelligence, not add redundant approval gates.",
    ]

    if dashboard_result.blockers:
        blockers.append("Source recommendation dashboard integration is blocked.")
    if not effective_checks:
        blockers.append("No closeout audit checks were produced.")

    check_ids = [check.check_id for check in effective_checks]
    if len(check_ids) != len(set(check_ids)):
        blockers.append("Closeout audit check IDs must be unique.")

    for check in effective_checks:
        if not check.safe_check_only():
            blockers.append(f"{check.check_id}: closeout check must remain non-executable.")
        if not check.passed():
            blockers.append(check.blocker_if_failed)
        if not check.evidence.strip():
            blockers.append(f"{check.check_id}: evidence is required.")
        if check.no_buy_request is not True:
            blockers.append(f"{check.check_id}: buy request path is forbidden.")
        if check.no_broker_connection is not True:
            blockers.append(f"{check.check_id}: broker connection path is forbidden.")
        if check.no_order_placement is not True:
            blockers.append(f"{check.check_id}: order placement path is forbidden.")
        if check.no_trade_execution is not True:
            blockers.append(f"{check.check_id}: trade execution path is forbidden.")

    passed_count = sum(1 for check in effective_checks if check.passed())
    failed_count = len(effective_checks) - passed_count

    safety_flags = {
        "closeout_audit_ready": False,
        "no_manual_review_queue_added": True,
        "no_buy_request_created": True,
        "no_broker_connection_created": True,
        "no_order_placement_created": True,
        "no_trades_executed": True,
    }

    if not safety_flags["no_manual_review_queue_added"]:
        blockers.append("v6.15 must not add another manual review queue.")
    if not safety_flags["no_buy_request_created"]:
        blockers.append("v6.15 must not create buy requests.")
    if not safety_flags["no_broker_connection_created"]:
        blockers.append("v6.15 must not create broker connections.")
    if not safety_flags["no_order_placement_created"]:
        blockers.append("v6.15 must not create order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.15 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return AutonomousCommandCenterCloseoutAuditResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        analyzed_policy_id=dashboard_result.analyzed_policy_id,
        selected_candidate_id=dashboard_result.selected_candidate_id,
        selected_sleeve_id=dashboard_result.selected_sleeve_id,
        check_count=len(effective_checks),
        passed_check_count=passed_count,
        failed_check_count=failed_count,
        v6_chain_complete=ready,
        autonomous_intelligence_ready=ready,
        command_center_ready=ready,
        final_user_buy_action_required=True,
        checks=effective_checks,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "closeout_audit_ready": ready},
    )
