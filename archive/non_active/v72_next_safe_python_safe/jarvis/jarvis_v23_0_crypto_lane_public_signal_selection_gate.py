"""J.A.R.V.I.S. v23.0 crypto-lane public signal selection gate.

v23 consumes the v22 multi-crypto public data quality pipeline and the current
allocation/risk/platform state to decide which crypto candidates are eligible for
the weekly crypto lane.

It does not mutate allocation scores, approval tickets, broker state, orders, or
trades. It is a selection/readiness gate only.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jarvis.jarvis_v22_0_multi_crypto_public_data_quality_pipeline import (
    DEFAULT_CANDIDATES,
    MultiCryptoPublicDataQualityPipelineResult,
    build_multi_crypto_public_data_quality_pipeline_result,
)

STATUS_READY = "JARVIS_V23_0_CRYPTO_LANE_PUBLIC_SIGNAL_SELECTION_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V23_0_CRYPTO_LANE_PUBLIC_SIGNAL_SELECTION_GATE_REVIEW_REQUIRED_SAFE"
GATE_READY = "CRYPTO_LANE_PUBLIC_SIGNAL_SELECTION_GATE_READY"
GATE_REVIEW_REQUIRED = "CRYPTO_LANE_PUBLIC_SIGNAL_SELECTION_GATE_REVIEW_REQUIRED"

DECISION_SELECTED = "SELECTED_FOR_CRYPTO_LANE_EVIDENCE"
DECISION_ELIGIBLE_NOT_SELECTED = "ELIGIBLE_NOT_SELECTED"
DECISION_BLOCKED_BY_SOURCE_QUALITY = "BLOCKED_BY_SOURCE_QUALITY"
DECISION_BLOCKED_BY_PLATFORM = "BLOCKED_BY_PLATFORM"
DECISION_BLOCKED_BY_ALLOCATION_RISK_OR_BUDGET = "BLOCKED_BY_ALLOCATION_RISK_OR_BUDGET"

DEFAULT_CONSTITUTION_PATH = "jarvis_constitution.json"
DEFAULT_PORTFOLIO_STATE_PATH = "portfolio_state.json"


@dataclass(frozen=True)
class CryptoLaneCandidateDecision:
    candidate_id: str
    source_id: str
    source_quality_ready: bool
    route: str
    platform_ready: bool
    ideal_amount_eur: float
    executable_amount_eur: float
    price_eur: float | None
    change_24h_pct: float | None
    market_cap_eur: float | None
    signal_age_days: int | None
    decision_status: str
    selected: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "source_id": self.source_id,
            "source_quality_ready": self.source_quality_ready,
            "route": self.route,
            "platform_ready": self.platform_ready,
            "ideal_amount_eur": self.ideal_amount_eur,
            "executable_amount_eur": self.executable_amount_eur,
            "price_eur": self.price_eur,
            "change_24h_pct": self.change_24h_pct,
            "market_cap_eur": self.market_cap_eur,
            "signal_age_days": self.signal_age_days,
            "decision_status": self.decision_status,
            "selected": self.selected,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class CryptoLanePublicSignalSelectionGateResult:
    status: str
    gate_status: str
    selected_crypto_candidate: str | None
    selected_crypto_amount_eur: float
    crypto_public_signal_universe_ready: bool
    candidate_count: int
    eligible_candidate_count: int
    blocked_candidate_count: int
    current_date: str
    recommended_next_stage: str
    candidate_decisions: tuple[CryptoLaneCandidateDecision, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    recommendation_quality_current_data: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "gate_status": self.gate_status,
            "selected_crypto_candidate": self.selected_crypto_candidate,
            "selected_crypto_amount_eur": self.selected_crypto_amount_eur,
            "crypto_public_signal_universe_ready": self.crypto_public_signal_universe_ready,
            "candidate_count": self.candidate_count,
            "eligible_candidate_count": self.eligible_candidate_count,
            "blocked_candidate_count": self.blocked_candidate_count,
            "current_date": self.current_date,
            "recommended_next_stage": self.recommended_next_stage,
            "candidate_decisions": [item.to_dict() for item in self.candidate_decisions],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _euros(cents: int | float | None) -> float:
    return round(float(cents or 0) / 100.0, 2)


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _route_is_ready(route: str, platform_status: dict[str, Any]) -> bool:
    if route in {"cash", "manual_review"}:
        return True
    return bool(platform_status.get(f"{route}_ready", False))


def _candidate_signal_map(
    public_signal_result: MultiCryptoPublicDataQualityPipelineResult,
) -> dict[str, Any]:
    return {item.candidate_id: item for item in public_signal_result.candidate_results}


def _build_allocation_result(
    constitution: dict[str, Any],
    portfolio_state: dict[str, Any],
) -> dict[str, Any]:
    from allocation_engine import allocate_weekly_budget

    return allocate_weekly_budget(constitution, portfolio_state)


def _candidate_blockers(
    *,
    candidate_id: str,
    source_quality_ready: bool,
    platform_ready: bool,
    executable_amount_eur: float,
) -> list[str]:
    blockers: list[str] = []
    if not source_quality_ready:
        blockers.append(f"{candidate_id} public signal is not source-quality ready.")
    if not platform_ready:
        blockers.append(f"{candidate_id} platform route is not ready.")
    if executable_amount_eur <= 0:
        blockers.append(
            f"{candidate_id} has no executable crypto-lane amount after allocation, platform, budget, and risk checks."
        )
    return blockers


def build_crypto_lane_public_signal_selection_gate_result(
    *,
    current_date: str | None = None,
    constitution_path: str | Path = DEFAULT_CONSTITUTION_PATH,
    portfolio_state_path: str | Path = DEFAULT_PORTFOLIO_STATE_PATH,
    public_signal_result: MultiCryptoPublicDataQualityPipelineResult | None = None,
    allocation_result: dict[str, Any] | None = None,
    constitution: dict[str, Any] | None = None,
    portfolio_state: dict[str, Any] | None = None,
) -> CryptoLanePublicSignalSelectionGateResult:
    constitution_data = constitution or _load_json(constitution_path)
    portfolio_state_data = portfolio_state or _load_json(portfolio_state_path)
    allocation_data = allocation_result or _build_allocation_result(constitution_data, portfolio_state_data)
    public_signals = public_signal_result or build_multi_crypto_public_data_quality_pipeline_result(
        current_date=current_date,
    )

    signal_by_candidate = _candidate_signal_map(public_signals)
    routes = constitution_data.get("asset_routes", {})
    platform_status = portfolio_state_data.get("platform_status", {})
    ideal_allocations_cents = allocation_data.get("ideal_allocations_cents", {})
    executable_allocations_cents = allocation_data.get("executable_allocations_cents", {})

    decisions: list[CryptoLaneCandidateDecision] = []
    warnings: list[str] = list(public_signals.warnings)
    blockers: list[str] = list(public_signals.blockers)

    for config in DEFAULT_CANDIDATES:
        candidate_id = config.candidate_id
        signal_result = signal_by_candidate.get(candidate_id)
        signal = signal_result.signal if signal_result else None
        source_quality_ready = bool(signal_result and signal_result.source_quality_ready)
        route = _text(routes.get(candidate_id))
        platform_ready = _route_is_ready(route, platform_status) if route else False
        ideal_amount_eur = _euros(ideal_allocations_cents.get(candidate_id, 0))
        executable_amount_eur = _euros(executable_allocations_cents.get(candidate_id, 0))

        candidate_blockers = _candidate_blockers(
            candidate_id=candidate_id,
            source_quality_ready=source_quality_ready,
            platform_ready=platform_ready,
            executable_amount_eur=executable_amount_eur,
        )

        if not source_quality_ready:
            decision_status = DECISION_BLOCKED_BY_SOURCE_QUALITY
        elif not platform_ready:
            decision_status = DECISION_BLOCKED_BY_PLATFORM
        elif executable_amount_eur <= 0:
            decision_status = DECISION_BLOCKED_BY_ALLOCATION_RISK_OR_BUDGET
        else:
            decision_status = DECISION_ELIGIBLE_NOT_SELECTED

        decisions.append(
            CryptoLaneCandidateDecision(
                candidate_id=candidate_id,
                source_id=signal_result.source_id if signal_result else config.source_id,
                source_quality_ready=source_quality_ready,
                route=route,
                platform_ready=platform_ready,
                ideal_amount_eur=ideal_amount_eur,
                executable_amount_eur=executable_amount_eur,
                price_eur=signal.price_eur if signal else None,
                change_24h_pct=signal.change_24h_pct if signal else None,
                market_cap_eur=signal.market_cap_eur if signal else None,
                signal_age_days=signal.signal_age_days if signal else None,
                decision_status=decision_status,
                selected=False,
                blockers=tuple(candidate_blockers),
                warnings=tuple(),
            )
        )

    eligible = [item for item in decisions if item.decision_status == DECISION_ELIGIBLE_NOT_SELECTED]
    selected_candidate: CryptoLaneCandidateDecision | None = None
    if eligible:
        selected_candidate = sorted(
            eligible,
            key=lambda item: (-item.executable_amount_eur, item.candidate_id),
        )[0]

    final_decisions: list[CryptoLaneCandidateDecision] = []
    for item in decisions:
        selected = bool(selected_candidate and item.candidate_id == selected_candidate.candidate_id)
        final_decisions.append(
            CryptoLaneCandidateDecision(
                candidate_id=item.candidate_id,
                source_id=item.source_id,
                source_quality_ready=item.source_quality_ready,
                route=item.route,
                platform_ready=item.platform_ready,
                ideal_amount_eur=item.ideal_amount_eur,
                executable_amount_eur=item.executable_amount_eur,
                price_eur=item.price_eur,
                change_24h_pct=item.change_24h_pct,
                market_cap_eur=item.market_cap_eur,
                signal_age_days=item.signal_age_days,
                decision_status=DECISION_SELECTED if selected else item.decision_status,
                selected=selected,
                blockers=item.blockers,
                warnings=item.warnings,
            )
        )

    selected_crypto_candidate = selected_candidate.candidate_id if selected_candidate else None
    selected_crypto_amount_eur = selected_candidate.executable_amount_eur if selected_candidate else 0.0
    eligible_count = sum(1 for item in final_decisions if item.selected or item.decision_status == DECISION_ELIGIBLE_NOT_SELECTED)
    blocked_count = len(final_decisions) - eligible_count

    if selected_crypto_candidate is None:
        blockers.append("No crypto candidate is selectable after public signal, platform, allocation, budget, and risk checks.")

    return CryptoLanePublicSignalSelectionGateResult(
        status=STATUS_READY if selected_crypto_candidate else STATUS_REVIEW_REQUIRED,
        gate_status=GATE_READY if selected_crypto_candidate else GATE_REVIEW_REQUIRED,
        selected_crypto_candidate=selected_crypto_candidate,
        selected_crypto_amount_eur=selected_crypto_amount_eur,
        crypto_public_signal_universe_ready=public_signals.all_crypto_public_signals_ready,
        candidate_count=len(final_decisions),
        eligible_candidate_count=eligible_count,
        blocked_candidate_count=blocked_count,
        current_date=public_signals.current_date,
        recommended_next_stage="crypto_lane_public_signal_scoring_integration",
        candidate_decisions=tuple(final_decisions),
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
        recommendation_quality_current_data=False,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
    )


def format_crypto_lane_public_signal_selection_gate(
    result: CryptoLanePublicSignalSelectionGateResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Crypto-Lane Public Signal Selection Gate",
        f"status: {result.status}",
        f"gate status: {result.gate_status}",
        f"selected crypto candidate: {result.selected_crypto_candidate or 'none'}",
        f"selected crypto amount: EUR {result.selected_crypto_amount_eur:,.2f}",
        f"crypto public signal universe ready: {result.crypto_public_signal_universe_ready}",
        f"candidate count: {result.candidate_count}",
        f"eligible candidate count: {result.eligible_candidate_count}",
        f"blocked candidate count: {result.blocked_candidate_count}",
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
        "Crypto candidates:",
    ]

    for item in result.candidate_decisions:
        lines.append(
            f"- {item.candidate_id}: {item.decision_status}; selected {item.selected}; "
            f"source_ready {item.source_quality_ready}; platform_ready {item.platform_ready}; "
            f"executable EUR {item.executable_amount_eur:,.2f}"
        )
        if item.price_eur is not None:
            lines.append(f"  price: EUR {item.price_eur:,.2f}; 24h change: {item.change_24h_pct:.4f}%")
        lines.append(f"  route: {item.route or 'none'}; signal_age_days: {item.signal_age_days}")
        for blocker in item.blockers:
            lines.append(f"  blocker: {blocker}")

    if result.blockers:
        lines.extend(["", "Blockers:"])
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("blockers: none")

    if result.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("warnings: none")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Select crypto-lane candidate from quality-gated public signals.")
    parser.add_argument("--current-date", default=None)
    args = parser.parse_args(argv)

    result = build_crypto_lane_public_signal_selection_gate_result(current_date=args.current_date)
    print(format_crypto_lane_public_signal_selection_gate(result))
    return 0 if result.status == STATUS_READY else 1


if __name__ == "__main__":
    raise SystemExit(main())