"""J.A.R.V.I.S. v29.0 expanded crypto allocation eligibility bridge.

v29 consumes the v28 daily operator output and separates two concepts:

1. crypto-lane budget amount produced by the existing allocation/risk/budget engine;
2. best eligible crypto asset from the completed v27 expanded ranking.

This lets J.A.R.V.I.S. propose the weekly crypto manual-buy candidate from the
expanded ranked crypto universe instead of blindly keeping the old BTC allocation
basis. It does not mutate allocation, approval tickets, portfolio state, broker
state, orders, or trades.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from .jarvis_v28_0_expanded_crypto_ranking_daily_operator_bridge import (
    DECISION_BLOCKED_BY_PLATFORM,
    DECISION_BLOCKED_BY_RANKING_ENGINE,
    DECISION_BLOCKED_BY_SOURCE_QUALITY,
    build_expanded_crypto_ranking_daily_operator_bridge,
    build_expanded_crypto_ranking_daily_operator_console_output,
)

STATUS_READY = "JARVIS_V29_0_EXPANDED_CRYPTO_ALLOCATION_ELIGIBILITY_BRIDGE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V29_0_EXPANDED_CRYPTO_ALLOCATION_ELIGIBILITY_BRIDGE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V29_0_EXPANDED_CRYPTO_ALLOCATION_ELIGIBILITY_BRIDGE_BLOCKED_SAFE"

BRIDGE_READY = "EXPANDED_CRYPTO_ALLOCATION_ELIGIBILITY_BRIDGE_READY"
BRIDGE_REVIEW_REQUIRED = "EXPANDED_CRYPTO_ALLOCATION_ELIGIBILITY_BRIDGE_REVIEW_REQUIRED"
BRIDGE_BLOCKED = "EXPANDED_CRYPTO_ALLOCATION_ELIGIBILITY_BRIDGE_BLOCKED"

NEXT_STAGE = "expanded_crypto_approval_ticket_refresh"

DECISION_SELECTED = "SELECTED_FOR_CRYPTO_LANE_MANUAL_BUY"
DECISION_ELIGIBLE_NOT_SELECTED = "ELIGIBLE_NOT_SELECTED"
DECISION_BLOCKED_NO_CRYPTO_LANE_BUDGET = "BLOCKED_NO_CRYPTO_LANE_BUDGET"
DECISION_BLOCKED_BY_SOURCE_OR_RANKING = "BLOCKED_BY_SOURCE_OR_RANKING"
DECISION_BLOCKED_BY_PLATFORM_ROUTE = "BLOCKED_BY_PLATFORM_ROUTE"

DEFAULT_CRYPTO_MIN_SCORE = 1.0


@dataclass(frozen=True)
class CryptoAllocationEligibilityDecision:
    candidate_id: str
    rank: int
    score: float
    eligible: bool
    selected: bool
    proposed_amount_eur: float
    allocation_basis_amount_eur: float
    source_quality_ready: bool
    platform_ready: bool
    platform_route: str
    prior_daily_decision_status: str
    decision_status: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "rank": self.rank,
            "score": self.score,
            "eligible": self.eligible,
            "selected": self.selected,
            "proposed_amount_eur": self.proposed_amount_eur,
            "allocation_basis_amount_eur": self.allocation_basis_amount_eur,
            "source_quality_ready": self.source_quality_ready,
            "platform_ready": self.platform_ready,
            "platform_route": self.platform_route,
            "prior_daily_decision_status": self.prior_daily_decision_status,
            "decision_status": self.decision_status,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class ExpandedCryptoAllocationEligibilityBridgeResult:
    status: str
    bridge_status: str
    recommended_next_stage: str
    upstream_daily_result: Any
    allocation_basis_candidate: str | None
    allocation_basis_amount_eur: float
    selected_crypto_candidate: str | None
    selected_crypto_amount_eur: float
    selected_crypto_rank: int | None
    selected_crypto_score: float
    reassigned_from_allocation_basis: bool
    approval_ticket_refresh_required: bool
    full_public_data_coverage: bool
    expanded_crypto_ranking_ready: bool
    candidate_decisions: tuple[CryptoAllocationEligibilityDecision, ...]
    recommendation_quality_current_data: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    portfolio_state_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    final_user_buy_action_required: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        upstream = self.upstream_daily_result
        return {
            "status": self.status,
            "bridge_status": self.bridge_status,
            "recommended_next_stage": self.recommended_next_stage,
            "upstream_daily_result": upstream.to_dict() if hasattr(upstream, "to_dict") else dict(getattr(upstream, "__dict__", {})),
            "allocation_basis_candidate": self.allocation_basis_candidate,
            "allocation_basis_amount_eur": self.allocation_basis_amount_eur,
            "selected_crypto_candidate": self.selected_crypto_candidate,
            "selected_crypto_amount_eur": self.selected_crypto_amount_eur,
            "selected_crypto_rank": self.selected_crypto_rank,
            "selected_crypto_score": self.selected_crypto_score,
            "reassigned_from_allocation_basis": self.reassigned_from_allocation_basis,
            "approval_ticket_refresh_required": self.approval_ticket_refresh_required,
            "full_public_data_coverage": self.full_public_data_coverage,
            "expanded_crypto_ranking_ready": self.expanded_crypto_ranking_ready,
            "candidate_decisions": [item.to_dict() for item in self.candidate_decisions],
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "portfolio_state_mutation": self.portfolio_state_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def _dedupe(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _upstream_requires_review(upstream_daily_result: Any) -> bool:
    status = str(getattr(upstream_daily_result, "status", ""))
    return "REVIEW_REQUIRED" in status


def _upstream_blocked(upstream_daily_result: Any) -> bool:
    status = str(getattr(upstream_daily_result, "status", ""))
    return "BLOCKED" in status


def _is_source_or_ranking_blocked(prior_status: str) -> bool:
    return prior_status in {
        DECISION_BLOCKED_BY_SOURCE_QUALITY,
        DECISION_BLOCKED_BY_RANKING_ENGINE,
    }


def _is_platform_blocked(prior_status: str, platform_ready: bool) -> bool:
    return prior_status == DECISION_BLOCKED_BY_PLATFORM or not platform_ready


def _build_candidate_decisions(
    *,
    upstream_daily_result: Any,
    crypto_lane_budget_eur: float,
    min_score: float,
) -> tuple[CryptoAllocationEligibilityDecision, ...]:
    preliminary: list[CryptoAllocationEligibilityDecision] = []

    for item in tuple(getattr(upstream_daily_result, "candidate_decisions", ()) or ()):
        candidate_id = str(getattr(item, "candidate_id", ""))
        rank = int(getattr(item, "rank", 0) or 0)
        score = float(getattr(item, "score", 0.0) or 0.0)
        source_quality_ready = bool(getattr(item, "source_quality_ready", False))
        platform_ready = bool(getattr(item, "platform_ready", False))
        platform_route = str(getattr(item, "platform_route", ""))
        prior_status = str(getattr(item, "decision_status", ""))
        prior_warnings = tuple(getattr(item, "warnings", ()) or ())
        blockers: list[str] = []

        if crypto_lane_budget_eur <= 0:
            decision_status = DECISION_BLOCKED_NO_CRYPTO_LANE_BUDGET
            blockers.append("No executable weekly crypto-lane budget is available from allocation/risk/budget checks.")
        elif not source_quality_ready or _is_source_or_ranking_blocked(prior_status) or score < min_score:
            decision_status = DECISION_BLOCKED_BY_SOURCE_OR_RANKING
            blockers.append(f"{candidate_id} is not eligible from source-quality or expanded-ranking gates.")
        elif _is_platform_blocked(prior_status, platform_ready):
            decision_status = DECISION_BLOCKED_BY_PLATFORM_ROUTE
            blockers.append(f"{candidate_id} platform route is not ready.")
        else:
            decision_status = DECISION_ELIGIBLE_NOT_SELECTED

        preliminary.append(
            CryptoAllocationEligibilityDecision(
                candidate_id=candidate_id,
                rank=rank,
                score=score,
                eligible=decision_status == DECISION_ELIGIBLE_NOT_SELECTED,
                selected=False,
                proposed_amount_eur=0.0,
                allocation_basis_amount_eur=float(getattr(item, "executable_amount_eur", 0.0) or 0.0),
                source_quality_ready=source_quality_ready,
                platform_ready=platform_ready,
                platform_route=platform_route,
                prior_daily_decision_status=prior_status,
                decision_status=decision_status,
                blockers=tuple(blockers),
                warnings=prior_warnings,
            )
        )

    selected = next((item for item in preliminary if item.eligible), None)
    final: list[CryptoAllocationEligibilityDecision] = []
    for item in preliminary:
        is_selected = bool(selected and item.candidate_id == selected.candidate_id)
        final.append(
            CryptoAllocationEligibilityDecision(
                candidate_id=item.candidate_id,
                rank=item.rank,
                score=item.score,
                eligible=item.eligible,
                selected=is_selected,
                proposed_amount_eur=round(crypto_lane_budget_eur, 2) if is_selected else 0.0,
                allocation_basis_amount_eur=item.allocation_basis_amount_eur,
                source_quality_ready=item.source_quality_ready,
                platform_ready=item.platform_ready,
                platform_route=item.platform_route,
                prior_daily_decision_status=item.prior_daily_decision_status,
                decision_status=DECISION_SELECTED if is_selected else item.decision_status,
                blockers=item.blockers,
                warnings=item.warnings,
            )
        )
    return tuple(final)


def build_expanded_crypto_allocation_eligibility_bridge(
    *,
    current_date: str | None = None,
    upstream_daily_result: Any | None = None,
    write_local_signals: bool = False,
    min_score: float = DEFAULT_CRYPTO_MIN_SCORE,
    upstream_builder: Callable[..., Any] = build_expanded_crypto_ranking_daily_operator_bridge,
) -> ExpandedCryptoAllocationEligibilityBridgeResult:
    parsed_current_date = _parse_date(current_date)
    blockers: list[str] = []
    warnings: list[str] = []

    if current_date is not None and parsed_current_date is None:
        blockers.append("current_date must use YYYY-MM-DD format when provided.")

    upstream = upstream_daily_result if upstream_daily_result is not None else upstream_builder(
        current_date=current_date,
        write_local_signals=write_local_signals,
    )

    blockers.extend(getattr(upstream, "blockers", ()) or ())
    warnings.extend(getattr(upstream, "warnings", ()) or ())

    allocation_basis_candidate = getattr(upstream, "selected_crypto_candidate", None)
    allocation_basis_amount_eur = round(float(getattr(upstream, "selected_crypto_amount_eur", 0.0) or 0.0), 2)
    candidate_decisions = _build_candidate_decisions(
        upstream_daily_result=upstream,
        crypto_lane_budget_eur=allocation_basis_amount_eur,
        min_score=min_score,
    )
    selected = next((item for item in candidate_decisions if item.selected), None)

    full_public_data_coverage = bool(getattr(upstream, "full_public_data_coverage", False))
    expanded_crypto_ranking_ready = bool(getattr(upstream, "expanded_crypto_ranking_ready", False))

    if not full_public_data_coverage:
        warnings.append("Expanded crypto public-data coverage is incomplete.")
    if not expanded_crypto_ranking_ready:
        warnings.append("Expanded crypto ranking is not ready.")
    if allocation_basis_amount_eur <= 0:
        warnings.append("No executable crypto-lane budget exists to reassign.")
    if selected is None:
        warnings.append("No eligible expanded crypto candidate is available for the crypto-lane budget.")

    selected_candidate = selected.candidate_id if selected else None
    reassigned = bool(selected_candidate and allocation_basis_candidate and selected_candidate != allocation_basis_candidate)
    approval_ticket_refresh_required = bool(reassigned or _upstream_requires_review(upstream))

    if reassigned:
        warnings.append(
            f"Crypto-lane candidate changed from allocation basis {allocation_basis_candidate} to {selected_candidate}; approval ticket refresh is required before manual action."
        )

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers or _upstream_blocked(upstream):
        status = STATUS_BLOCKED
        bridge_status = BRIDGE_BLOCKED
    elif _upstream_requires_review(upstream) or selected is None or not expanded_crypto_ranking_ready or allocation_basis_amount_eur <= 0:
        status = STATUS_REVIEW_REQUIRED
        bridge_status = BRIDGE_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        bridge_status = BRIDGE_READY

    return ExpandedCryptoAllocationEligibilityBridgeResult(
        status=status,
        bridge_status=bridge_status,
        recommended_next_stage=NEXT_STAGE,
        upstream_daily_result=upstream,
        allocation_basis_candidate=allocation_basis_candidate,
        allocation_basis_amount_eur=allocation_basis_amount_eur,
        selected_crypto_candidate=selected_candidate,
        selected_crypto_amount_eur=round(selected.proposed_amount_eur, 2) if selected else 0.0,
        selected_crypto_rank=selected.rank if selected else None,
        selected_crypto_score=selected.score if selected else 0.0,
        reassigned_from_allocation_basis=reassigned,
        approval_ticket_refresh_required=approval_ticket_refresh_required,
        full_public_data_coverage=full_public_data_coverage,
        expanded_crypto_ranking_ready=expanded_crypto_ranking_ready,
        candidate_decisions=candidate_decisions,
        recommendation_quality_current_data=False,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        portfolio_state_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        final_user_buy_action_required=True,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )


def _format_candidate_decisions(result: ExpandedCryptoAllocationEligibilityBridgeResult) -> str:
    lines = ["Expanded crypto allocation eligibility candidates:"]
    for item in result.candidate_decisions:
        selected_marker = "SELECTED" if item.selected else "not selected"
        lines.append(
            f"- #{item.rank} {item.candidate_id}: {item.decision_status}; {selected_marker}; "
            f"score {item.score:,.2f}; proposed EUR {item.proposed_amount_eur:,.2f}; "
            f"allocation-basis executable EUR {item.allocation_basis_amount_eur:,.2f}; "
            f"source_ready {item.source_quality_ready}; platform_ready {item.platform_ready}; route {item.platform_route or 'none'}"
        )
        for blocker in item.blockers:
            lines.append(f"  blocker: {blocker}")
    return "\n".join(lines)


def _upstream_daily_console_output(upstream_daily_result: Any) -> str:
    required_attrs = ("bridge_status", "selected_crypto_candidate", "candidate_decisions")
    if all(hasattr(upstream_daily_result, attr) for attr in required_attrs):
        return build_expanded_crypto_ranking_daily_operator_console_output(upstream_daily_result)

    candidate_decisions = tuple(getattr(upstream_daily_result, "candidate_decisions", ()) or ())
    lines = [
        "J.A.R.V.I.S. Daily Operator with Expanded Crypto Ranking",
        f"status: {getattr(upstream_daily_result, 'status', 'unknown')}",
        f"selected crypto candidate: {getattr(upstream_daily_result, 'selected_crypto_candidate', 'none') or 'none'}",
        f"selected crypto amount: EUR {float(getattr(upstream_daily_result, 'selected_crypto_amount_eur', 0.0) or 0.0):,.2f}",
        f"expanded crypto ranking ready: {getattr(upstream_daily_result, 'expanded_crypto_ranking_ready', False)}",
        f"full public data coverage: {getattr(upstream_daily_result, 'full_public_data_coverage', False)}",
        f"candidate decision count: {len(candidate_decisions)}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
    ]
    blockers = getattr(upstream_daily_result, "blockers", ()) or ()
    warnings = getattr(upstream_daily_result, "warnings", ()) or ()
    lines.append(f"blockers: {', '.join(str(item) for item in blockers) if blockers else 'none'}")
    lines.append(f"warnings: {', '.join(str(item) for item in warnings) if warnings else 'none'}")
    return "\n".join(lines)


def build_expanded_crypto_allocation_eligibility_console_output(
    result: ExpandedCryptoAllocationEligibilityBridgeResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Daily Operator with Expanded Crypto Allocation Eligibility",
        f"status: {result.status}",
        f"bridge status: {result.bridge_status}",
        f"allocation basis candidate: {result.allocation_basis_candidate or 'none'}",
        f"allocation basis amount: EUR {result.allocation_basis_amount_eur:,.2f}",
        f"selected crypto candidate: {result.selected_crypto_candidate or 'none'}",
        f"selected crypto amount: EUR {result.selected_crypto_amount_eur:,.2f}",
        f"selected crypto rank: {result.selected_crypto_rank if result.selected_crypto_rank is not None else 'none'}",
        f"selected crypto score: {result.selected_crypto_score:,.2f}",
        f"reassigned from allocation basis: {result.reassigned_from_allocation_basis}",
        f"approval ticket refresh required: {result.approval_ticket_refresh_required}",
        f"expanded crypto ranking ready: {result.expanded_crypto_ranking_ready}",
        f"full public data coverage: {result.full_public_data_coverage}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"portfolio state mutation: {result.portfolio_state_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
        "",
        _format_candidate_decisions(result),
        "",
        "Upstream expanded crypto daily operator:",
        _upstream_daily_console_output(result.upstream_daily_result),
    ]

    if result.blockers:
        lines.extend(["", "Bridge blockers:"])
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("bridge blockers: none")

    if result.warnings:
        lines.extend(["", "Bridge warnings:"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("bridge warnings: none")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. daily operator with expanded crypto allocation eligibility.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run daily operator with expanded crypto allocation eligibility.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--write-local-signals", action="store_true", help="Write normalized local public crypto signals under jarvis/local.")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    if args.voice_command:
        print(build_safety_check_console_output(args.voice_command))
        return 0

    if args.demo:
        print("Available typed Jarvis commands:")
        for command in DEFAULT_COMMAND_SAMPLES:
            print(f"- {command}")
        return 0

    result = build_expanded_crypto_allocation_eligibility_bridge(
        current_date=args.current_date,
        write_local_signals=args.write_local_signals,
    )
    print(build_expanded_crypto_allocation_eligibility_console_output(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())