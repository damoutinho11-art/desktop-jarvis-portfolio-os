"""J.A.R.V.I.S. v28.0 expanded crypto ranking daily operator bridge.

v28 connects the completed v27 10-asset crypto public-data/ranking engine to the
active daily operator path.

The bridge keeps the final crypto recommendation constrained by:
- v27 public-data/source-quality coverage;
- platform readiness;
- allocation/risk/budget executable amounts;
- daily readiness/stale-data gates;
- no broker, no credentials, no orders, no trades.

It does not mutate allocation, approval tickets, broker state, orders, or trades.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import (
    RealDailyReadinessGateResult,
    build_real_daily_readiness_console_output,
    build_real_daily_readiness_gate,
    build_safety_check_console_output,
)
from .jarvis_v27_0_expanded_crypto_universe_data_engine import (
    ExpandedCryptoUniverseDataEngineResult,
    build_expanded_crypto_universe_data_engine_result,
    format_expanded_crypto_universe_data_engine,
)

STATUS_READY = "JARVIS_V28_0_EXPANDED_CRYPTO_RANKING_DAILY_OPERATOR_BRIDGE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V28_0_EXPANDED_CRYPTO_RANKING_DAILY_OPERATOR_BRIDGE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V28_0_EXPANDED_CRYPTO_RANKING_DAILY_OPERATOR_BRIDGE_BLOCKED_SAFE"

BRIDGE_READY = "EXPANDED_CRYPTO_RANKING_DAILY_OPERATOR_BRIDGE_READY"
BRIDGE_REVIEW_REQUIRED = "EXPANDED_CRYPTO_RANKING_DAILY_OPERATOR_BRIDGE_REVIEW_REQUIRED"
BRIDGE_BLOCKED = "EXPANDED_CRYPTO_RANKING_DAILY_OPERATOR_BRIDGE_BLOCKED"

NEXT_STAGE = "expanded_crypto_ranking_approval_ticket_refresh"

DECISION_SELECTED = "SELECTED_FOR_WEEKLY_CRYPTO_MANUAL_BUY"
DECISION_RANKED_NOT_SELECTED = "RANKED_NOT_SELECTED"
DECISION_BLOCKED_BY_SOURCE_QUALITY = "BLOCKED_BY_SOURCE_QUALITY"
DECISION_BLOCKED_BY_PLATFORM = "BLOCKED_BY_PLATFORM"
DECISION_BLOCKED_BY_ALLOCATION_RISK_OR_BUDGET = "BLOCKED_BY_ALLOCATION_RISK_OR_BUDGET"
DECISION_BLOCKED_BY_RANKING_ENGINE = "BLOCKED_BY_EXPANDED_CRYPTO_RANKING_ENGINE"

DEFAULT_CONSTITUTION_PATH = "jarvis_constitution.json"
DEFAULT_PORTFOLIO_STATE_PATH = "portfolio_state.json"


@dataclass(frozen=True)
class ExpandedCryptoDailyCandidateDecision:
    candidate_id: str
    rank: int
    score: float
    source_quality_ready: bool
    platform_ready: bool
    platform_route: str
    ideal_amount_eur: float
    executable_amount_eur: float
    decision_status: str
    selected: bool
    price_eur: float | None
    market_cap_eur: float | None
    volume_24h_eur: float | None
    change_24h_pct: float | None
    signal_age_days: int | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "rank": self.rank,
            "score": self.score,
            "source_quality_ready": self.source_quality_ready,
            "platform_ready": self.platform_ready,
            "platform_route": self.platform_route,
            "ideal_amount_eur": self.ideal_amount_eur,
            "executable_amount_eur": self.executable_amount_eur,
            "decision_status": self.decision_status,
            "selected": self.selected,
            "price_eur": self.price_eur,
            "market_cap_eur": self.market_cap_eur,
            "volume_24h_eur": self.volume_24h_eur,
            "change_24h_pct": self.change_24h_pct,
            "signal_age_days": self.signal_age_days,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class ExpandedCryptoRankingDailyOperatorBridgeResult:
    status: str
    bridge_status: str
    recommended_next_stage: str
    daily_readiness_result: Any
    crypto_ranking_result: Any
    selected_crypto_candidate: str | None
    selected_crypto_amount_eur: float
    selected_crypto_rank: int | None
    selected_crypto_score: float
    expanded_crypto_ranking_ready: bool
    full_public_data_coverage: bool
    source_quality_ready_count: int
    source_quality_blocked_count: int
    ranked_candidate_count: int
    candidate_decisions: tuple[ExpandedCryptoDailyCandidateDecision, ...]
    recommendation_quality_current_data: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
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
        daily = self.daily_readiness_result
        ranking = self.crypto_ranking_result
        return {
            "status": self.status,
            "bridge_status": self.bridge_status,
            "recommended_next_stage": self.recommended_next_stage,
            "daily_readiness_result": daily.to_dict() if hasattr(daily, "to_dict") else dict(getattr(daily, "__dict__", {})),
            "crypto_ranking_result": ranking.to_dict() if hasattr(ranking, "to_dict") else dict(getattr(ranking, "__dict__", {})),
            "selected_crypto_candidate": self.selected_crypto_candidate,
            "selected_crypto_amount_eur": self.selected_crypto_amount_eur,
            "selected_crypto_rank": self.selected_crypto_rank,
            "selected_crypto_score": self.selected_crypto_score,
            "expanded_crypto_ranking_ready": self.expanded_crypto_ranking_ready,
            "full_public_data_coverage": self.full_public_data_coverage,
            "source_quality_ready_count": self.source_quality_ready_count,
            "source_quality_blocked_count": self.source_quality_blocked_count,
            "ranked_candidate_count": self.ranked_candidate_count,
            "candidate_decisions": [item.to_dict() for item in self.candidate_decisions],
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
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


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _euros(cents: int | float | None) -> float:
    return round(float(cents or 0) / 100.0, 2)


def _daily_status_requires_review(daily_readiness_result: Any) -> bool:
    daily_status = str(getattr(daily_readiness_result, "status", ""))
    return "REVIEW_REQUIRED" in daily_status or bool(getattr(daily_readiness_result, "stale_data_review_required", False))


def _ranking_status_requires_review(crypto_ranking_result: Any) -> bool:
    ranking_status = str(getattr(crypto_ranking_result, "status", ""))
    return "READY_SAFE" not in ranking_status


def _build_allocation_result(
    constitution: dict[str, Any],
    portfolio_state: dict[str, Any],
) -> dict[str, Any]:
    from allocation_engine import allocate_weekly_budget

    return allocate_weekly_budget(constitution, portfolio_state)


def _candidate_scores(crypto_ranking_result: Any) -> list[Any]:
    return list(getattr(crypto_ranking_result, "candidate_scores", ()) or ())


def _candidate_id(score: Any) -> str:
    return str(getattr(score, "candidate_id", ""))


def _candidate_blockers(
    *,
    candidate_id: str,
    source_quality_ready: bool,
    platform_ready: bool,
    executable_amount_eur: float,
    ranking_decision_status: str,
) -> list[str]:
    blockers: list[str] = []
    if not source_quality_ready:
        blockers.append(f"{candidate_id} expanded crypto public signal is not source-quality ready.")
    if ranking_decision_status != "RANKED_FOR_CRYPTO_LANE":
        blockers.append(f"{candidate_id} is not ranked for the crypto lane by the expanded crypto ranking engine.")
    if not platform_ready:
        blockers.append(f"{candidate_id} platform route is not ready.")
    if executable_amount_eur <= 0:
        blockers.append(
            f"{candidate_id} has no executable crypto-lane amount after allocation, platform, budget, and risk checks."
        )
    return blockers


def _build_candidate_decisions(
    *,
    crypto_ranking_result: Any,
    allocation_result: dict[str, Any],
) -> tuple[ExpandedCryptoDailyCandidateDecision, ...]:
    ideal_allocations_cents = allocation_result.get("ideal_allocations_cents", {})
    executable_allocations_cents = allocation_result.get("executable_allocations_cents", {})

    preliminary: list[ExpandedCryptoDailyCandidateDecision] = []

    for rank, score in enumerate(_candidate_scores(crypto_ranking_result), start=1):
        candidate_id = _candidate_id(score)
        source_quality_ready = bool(getattr(score, "source_quality_ready", False))
        platform_ready = bool(getattr(score, "platform_ready", False))
        ranking_decision_status = str(getattr(score, "decision_status", ""))
        executable_amount_eur = _euros(executable_allocations_cents.get(candidate_id, 0))
        ideal_amount_eur = _euros(ideal_allocations_cents.get(candidate_id, 0))
        blockers = _candidate_blockers(
            candidate_id=candidate_id,
            source_quality_ready=source_quality_ready,
            platform_ready=platform_ready,
            executable_amount_eur=executable_amount_eur,
            ranking_decision_status=ranking_decision_status,
        )

        if not source_quality_ready:
            decision_status = DECISION_BLOCKED_BY_SOURCE_QUALITY
        elif ranking_decision_status != "RANKED_FOR_CRYPTO_LANE":
            decision_status = DECISION_BLOCKED_BY_RANKING_ENGINE
        elif not platform_ready:
            decision_status = DECISION_BLOCKED_BY_PLATFORM
        elif executable_amount_eur <= 0:
            decision_status = DECISION_BLOCKED_BY_ALLOCATION_RISK_OR_BUDGET
        else:
            decision_status = DECISION_RANKED_NOT_SELECTED

        preliminary.append(
            ExpandedCryptoDailyCandidateDecision(
                candidate_id=candidate_id,
                rank=rank,
                score=float(getattr(score, "total_score", 0.0) or 0.0),
                source_quality_ready=source_quality_ready,
                platform_ready=platform_ready,
                platform_route=str(getattr(score, "platform_route", "")),
                ideal_amount_eur=ideal_amount_eur,
                executable_amount_eur=executable_amount_eur,
                decision_status=decision_status,
                selected=False,
                price_eur=getattr(score, "price_eur", None),
                market_cap_eur=getattr(score, "market_cap_eur", None),
                volume_24h_eur=getattr(score, "volume_24h_eur", None),
                change_24h_pct=getattr(score, "change_24h_pct", None),
                signal_age_days=getattr(score, "signal_age_days", None),
                blockers=tuple(blockers),
                warnings=tuple(getattr(score, "warnings", ()) or ()),
            )
        )

    selectable = [item for item in preliminary if item.decision_status == DECISION_RANKED_NOT_SELECTED]
    selected_candidate = selectable[0] if selectable else None

    final_decisions: list[ExpandedCryptoDailyCandidateDecision] = []
    for item in preliminary:
        selected = bool(selected_candidate and item.candidate_id == selected_candidate.candidate_id)
        final_decisions.append(
            ExpandedCryptoDailyCandidateDecision(
                candidate_id=item.candidate_id,
                rank=item.rank,
                score=item.score,
                source_quality_ready=item.source_quality_ready,
                platform_ready=item.platform_ready,
                platform_route=item.platform_route,
                ideal_amount_eur=item.ideal_amount_eur,
                executable_amount_eur=item.executable_amount_eur,
                decision_status=DECISION_SELECTED if selected else item.decision_status,
                selected=selected,
                price_eur=item.price_eur,
                market_cap_eur=item.market_cap_eur,
                volume_24h_eur=item.volume_24h_eur,
                change_24h_pct=item.change_24h_pct,
                signal_age_days=item.signal_age_days,
                blockers=item.blockers,
                warnings=item.warnings,
            )
        )

    return tuple(final_decisions)


def build_expanded_crypto_ranking_daily_operator_bridge(
    *,
    current_date: str | None = None,
    daily_readiness_result: RealDailyReadinessGateResult | None = None,
    crypto_ranking_result: ExpandedCryptoUniverseDataEngineResult | None = None,
    allocation_result: dict[str, Any] | None = None,
    constitution: dict[str, Any] | None = None,
    portfolio_state: dict[str, Any] | None = None,
    constitution_path: str | Path = DEFAULT_CONSTITUTION_PATH,
    portfolio_state_path: str | Path = DEFAULT_PORTFOLIO_STATE_PATH,
    write_local_signals: bool = False,
    daily_readiness_builder: Callable[..., RealDailyReadinessGateResult] = build_real_daily_readiness_gate,
    crypto_ranking_builder: Callable[..., ExpandedCryptoUniverseDataEngineResult] = build_expanded_crypto_universe_data_engine_result,
) -> ExpandedCryptoRankingDailyOperatorBridgeResult:
    parsed_current_date = _parse_date(current_date)
    blockers: list[str] = []
    warnings: list[str] = []

    if current_date is not None and parsed_current_date is None:
        blockers.append("current_date must use YYYY-MM-DD format when provided.")

    readiness = daily_readiness_result if daily_readiness_result is not None else daily_readiness_builder(current_date=parsed_current_date)
    ranking = crypto_ranking_result if crypto_ranking_result is not None else crypto_ranking_builder(
        current_date=current_date,
        write_local_signals=write_local_signals,
    )

    blockers.extend(getattr(readiness, "blockers", ()) or ())
    warnings.extend(getattr(readiness, "warnings", ()) or ())
    blockers.extend(getattr(ranking, "blockers", ()) or ())
    warnings.extend(getattr(ranking, "warnings", ()) or ())

    if allocation_result is None:
        constitution_data = constitution or _load_json(constitution_path)
        portfolio_state_data = portfolio_state or _load_json(portfolio_state_path)
        allocation_data = _build_allocation_result(constitution_data, portfolio_state_data)
    else:
        allocation_data = allocation_result

    candidate_decisions = _build_candidate_decisions(
        crypto_ranking_result=ranking,
        allocation_result=allocation_data,
    )
    selected = next((item for item in candidate_decisions if item.selected), None)

    full_public_data_coverage = bool(getattr(ranking, "full_public_data_coverage", False))
    source_ready_count = int(getattr(ranking, "source_quality_ready_count", 0) or 0)
    source_blocked_count = int(getattr(ranking, "source_quality_blocked_count", 0) or 0)
    ranked_candidate_count = int(getattr(ranking, "ranked_candidate_count", 0) or 0)
    expanded_crypto_ranking_ready = (
        full_public_data_coverage
        and source_blocked_count == 0
        and ranked_candidate_count > 0
        and not _ranking_status_requires_review(ranking)
    )

    if not expanded_crypto_ranking_ready:
        warnings.append("Expanded crypto ranking is not fully ready for daily selection.")
    if selected is None:
        warnings.append("No expanded crypto candidate has an executable crypto-lane amount after allocation/risk/budget checks.")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
        bridge_status = BRIDGE_BLOCKED
    elif _daily_status_requires_review(readiness) or not expanded_crypto_ranking_ready or selected is None:
        status = STATUS_REVIEW_REQUIRED
        bridge_status = BRIDGE_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        bridge_status = BRIDGE_READY

    return ExpandedCryptoRankingDailyOperatorBridgeResult(
        status=status,
        bridge_status=bridge_status,
        recommended_next_stage=NEXT_STAGE,
        daily_readiness_result=readiness,
        crypto_ranking_result=ranking,
        selected_crypto_candidate=selected.candidate_id if selected else None,
        selected_crypto_amount_eur=selected.executable_amount_eur if selected else 0.0,
        selected_crypto_rank=selected.rank if selected else None,
        selected_crypto_score=selected.score if selected else 0.0,
        expanded_crypto_ranking_ready=expanded_crypto_ranking_ready,
        full_public_data_coverage=full_public_data_coverage,
        source_quality_ready_count=source_ready_count,
        source_quality_blocked_count=source_blocked_count,
        ranked_candidate_count=ranked_candidate_count,
        candidate_decisions=candidate_decisions,
        recommendation_quality_current_data=False,
        allocation_mutation=False,
        approval_ticket_mutation=False,
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


def _daily_readiness_console_output(daily_readiness_result: Any) -> str:
    if hasattr(daily_readiness_result, "allocation_result"):
        return build_real_daily_readiness_console_output(daily_readiness_result)

    blockers = getattr(daily_readiness_result, "blockers", ()) or ()
    warnings = getattr(daily_readiness_result, "warnings", ()) or ()
    return "\n".join(
        [
            "J.A.R.V.I.S. Real Allocation Daily Operator",
            f"status: {getattr(daily_readiness_result, 'status', 'unknown')}",
            f"data readiness: {getattr(daily_readiness_result, 'readiness_status', 'unknown')}",
            f"blockers: {', '.join(str(item) for item in blockers) if blockers else 'none'}",
            f"warnings: {', '.join(str(item) for item in warnings) if warnings else 'none'}",
        ]
    )


def _format_daily_candidate_decisions(result: ExpandedCryptoRankingDailyOperatorBridgeResult) -> str:
    lines = ["Expanded crypto daily candidates:"]
    for item in result.candidate_decisions:
        selected_marker = "SELECTED" if item.selected else "not selected"
        lines.append(
            f"- #{item.rank} {item.candidate_id}: {item.decision_status}; {selected_marker}; "
            f"score {item.score:,.2f}; executable EUR {item.executable_amount_eur:,.2f}; "
            f"source_ready {item.source_quality_ready}; platform_ready {item.platform_ready}; route {item.platform_route or 'none'}"
        )
        if item.price_eur is not None:
            change = f"{item.change_24h_pct:.4f}%" if item.change_24h_pct is not None else "unknown"
            lines.append(
                f"  price EUR {item.price_eur:,.2f}; market cap EUR {item.market_cap_eur:,.2f}; "
                f"24h volume EUR {item.volume_24h_eur:,.2f}; 24h change {change}"
            )
        for blocker in item.blockers:
            lines.append(f"  blocker: {blocker}")
    return "\n".join(lines)


def _crypto_ranking_console_output(crypto_ranking_result: Any) -> str:
    required_attrs = ("engine_status", "current_date", "universe_candidate_count", "manifest_path")
    if all(hasattr(crypto_ranking_result, attr) for attr in required_attrs):
        return format_expanded_crypto_universe_data_engine(crypto_ranking_result)

    lines = [
        "J.A.R.V.I.S. Expanded Crypto Universe Data Engine",
        f"status: {getattr(crypto_ranking_result, 'status', 'unknown')}",
        f"full public data coverage: {getattr(crypto_ranking_result, 'full_public_data_coverage', False)}",
        f"source quality ready count: {getattr(crypto_ranking_result, 'source_quality_ready_count', 0)}",
        f"source quality blocked count: {getattr(crypto_ranking_result, 'source_quality_blocked_count', 0)}",
        f"ranked candidate count: {getattr(crypto_ranking_result, 'ranked_candidate_count', 0)}",
    ]
    blockers = getattr(crypto_ranking_result, "blockers", ()) or ()
    warnings = getattr(crypto_ranking_result, "warnings", ()) or ()
    lines.append(f"blockers: {', '.join(str(item) for item in blockers) if blockers else 'none'}")
    lines.append(f"warnings: {', '.join(str(item) for item in warnings) if warnings else 'none'}")
    return "\n".join(lines)


def build_expanded_crypto_ranking_daily_operator_console_output(
    result: ExpandedCryptoRankingDailyOperatorBridgeResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Daily Operator with Expanded Crypto Ranking",
        f"status: {result.status}",
        f"bridge status: {result.bridge_status}",
        f"selected crypto candidate: {result.selected_crypto_candidate or 'none'}",
        f"selected crypto amount: EUR {result.selected_crypto_amount_eur:,.2f}",
        f"selected crypto rank: {result.selected_crypto_rank if result.selected_crypto_rank is not None else 'none'}",
        f"selected crypto score: {result.selected_crypto_score:,.2f}",
        f"expanded crypto ranking ready: {result.expanded_crypto_ranking_ready}",
        f"full public data coverage: {result.full_public_data_coverage}",
        f"source quality ready count: {result.source_quality_ready_count}",
        f"source quality blocked count: {result.source_quality_blocked_count}",
        f"ranked candidate count: {result.ranked_candidate_count}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
        "",
        _format_daily_candidate_decisions(result),
        "",
        "Expanded crypto ranking engine:",
        _crypto_ranking_console_output(result.crypto_ranking_result),
        "",
        "Daily allocation/readiness:",
        _daily_readiness_console_output(result.daily_readiness_result),
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
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. daily operator with expanded crypto ranking.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run daily readiness with expanded crypto ranking.")
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

    result = build_expanded_crypto_ranking_daily_operator_bridge(
        current_date=args.current_date,
        write_local_signals=args.write_local_signals,
    )
    print(build_expanded_crypto_ranking_daily_operator_console_output(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())