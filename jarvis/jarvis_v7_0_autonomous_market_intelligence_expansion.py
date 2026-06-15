"""J.A.R.V.I.S. v7.0 autonomous market intelligence expansion.

This stage adds autonomous market-intelligence context behind the weekly
recommendation.

Safety boundary:
- market intelligence only
- signal/risk context only
- no buy request creation
- no broker/API connection
- no order placement
- no trade execution
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v6_15_autonomous_command_center_closeout_audit import (
    audit_v6_15_autonomous_command_center_closeout_audit,
)


STATUS_READY = "JARVIS_V7_0_AUTONOMOUS_MARKET_INTELLIGENCE_EXPANSION_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V7_0_AUTONOMOUS_MARKET_INTELLIGENCE_EXPANSION_BLOCKED_SAFE"

NEXT_STAGE = "v7_1_public_market_intelligence_adapter_contract"

SIGNAL_SUPPORTIVE = "SUPPORTIVE"
SIGNAL_CAUTION = "CAUTION"
SIGNAL_BLOCKING = "BLOCKING"
SIGNAL_NEUTRAL = "NEUTRAL"

MARKET_STATE_SUPPORTIVE_WITH_CAUTION = "SUPPORTIVE_WITH_CAUTION"
MARKET_STATE_NEUTRAL_MONITOR = "NEUTRAL_MONITOR"
MARKET_STATE_BLOCKED = "BLOCKED"

SOURCE_LOCAL_MARKET_INTELLIGENCE_FIXTURE = "local_autonomous_market_intelligence_fixture"


@dataclass(frozen=True)
class AutonomousMarketSignal:
    signal_id: str
    candidate_id: str
    signal_type: str
    signal_value: str
    severity: str
    confidence_score: int
    summary: str
    freshness_status: str
    source_label: str
    supports_recommendation: bool
    blocks_recommendation: bool
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_signal_only(self) -> bool:
        return (
            not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "signal_id": self.signal_id,
            "candidate_id": self.candidate_id,
            "signal_type": self.signal_type,
            "signal_value": self.signal_value,
            "severity": self.severity,
            "confidence_score": self.confidence_score,
            "summary": self.summary,
            "freshness_status": self.freshness_status,
            "source_label": self.source_label,
            "supports_recommendation": self.supports_recommendation,
            "blocks_recommendation": self.blocks_recommendation,
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_signal_only": self.safe_signal_only(),
        }


@dataclass(frozen=True)
class CandidateMarketIntelligenceCard:
    candidate_id: str
    sleeve_id: str
    selected_by_weekly_recommendation: bool
    market_state: str
    market_intelligence_score: int
    signal_count: int
    supportive_signal_count: int
    caution_signal_count: int
    blocking_signal_count: int
    intelligence_summary: str
    signals: tuple[AutonomousMarketSignal, ...]
    creates_buy_request: bool
    connects_broker: bool
    places_order: bool
    executes_trade: bool

    def safe_card_only(self) -> bool:
        return (
            not self.creates_buy_request
            and not self.connects_broker
            and not self.places_order
            and not self.executes_trade
            and all(signal.safe_signal_only() for signal in self.signals)
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "sleeve_id": self.sleeve_id,
            "selected_by_weekly_recommendation": self.selected_by_weekly_recommendation,
            "market_state": self.market_state,
            "market_intelligence_score": self.market_intelligence_score,
            "signal_count": self.signal_count,
            "supportive_signal_count": self.supportive_signal_count,
            "caution_signal_count": self.caution_signal_count,
            "blocking_signal_count": self.blocking_signal_count,
            "intelligence_summary": self.intelligence_summary,
            "signals": [signal.to_dict() for signal in self.signals],
            "creates_buy_request": self.creates_buy_request,
            "connects_broker": self.connects_broker,
            "places_order": self.places_order,
            "executes_trade": self.executes_trade,
            "safe_card_only": self.safe_card_only(),
        }


@dataclass(frozen=True)
class AutonomousMarketIntelligenceExpansionResult:
    status: str
    recommended_next_stage: str
    selected_candidate_id: str
    selected_sleeve_id: str
    candidate_card_count: int
    total_signal_count: int
    selected_candidate_market_state: str
    selected_candidate_market_score: int
    selected_candidate_supported: bool
    selected_candidate_blocked: bool
    candidate_cards: tuple[CandidateMarketIntelligenceCard, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    autonomous_market_intelligence_ready: bool
    market_intelligence_only: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "selected_candidate_id": self.selected_candidate_id,
            "selected_sleeve_id": self.selected_sleeve_id,
            "candidate_card_count": self.candidate_card_count,
            "total_signal_count": self.total_signal_count,
            "selected_candidate_market_state": self.selected_candidate_market_state,
            "selected_candidate_market_score": self.selected_candidate_market_score,
            "selected_candidate_supported": self.selected_candidate_supported,
            "selected_candidate_blocked": self.selected_candidate_blocked,
            "candidate_cards": [card.to_dict() for card in self.candidate_cards],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "autonomous_market_intelligence_ready": self.autonomous_market_intelligence_ready,
            "market_intelligence_only": self.market_intelligence_only,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _signal(
    signal_id: str,
    candidate_id: str,
    signal_type: str,
    signal_value: str,
    severity: str,
    confidence_score: int,
    summary: str,
    supports_recommendation: bool,
    blocks_recommendation: bool = False,
) -> AutonomousMarketSignal:
    return AutonomousMarketSignal(
        signal_id=signal_id,
        candidate_id=candidate_id,
        signal_type=signal_type,
        signal_value=signal_value,
        severity=severity,
        confidence_score=confidence_score,
        summary=summary,
        freshness_status="LOCAL_FIXTURE_READY_FOR_PUBLIC_ADAPTER",
        source_label=SOURCE_LOCAL_MARKET_INTELLIGENCE_FIXTURE,
        supports_recommendation=supports_recommendation,
        blocks_recommendation=blocks_recommendation,
        creates_buy_request=False,
        connects_broker=False,
        places_order=False,
        executes_trade=False,
    )


def build_example_market_signals(
    selected_candidate_id: str,
) -> tuple[AutonomousMarketSignal, ...]:
    return (
        _signal(
            "btc_policy_gap_signal",
            "btc_candidate",
            "POLICY_GAP_ALIGNMENT",
            "BTC sleeve is under hard minimum in current v6 fixture.",
            SIGNAL_SUPPORTIVE,
            92,
            "Market intelligence supports keeping BTC visible because it is policy-underweight.",
            True,
        ),
        _signal(
            "btc_volatility_caution_signal",
            "btc_candidate",
            "VOLATILITY_RISK",
            "Crypto volatility caution active.",
            SIGNAL_CAUTION,
            85,
            "BTC can remain the top recommendation only with modest amount logic and ceiling discipline.",
            selected_candidate_id == "btc_candidate",
        ),
        _signal(
            "global_core_stability_signal",
            "global_all_world_etf_candidate",
            "CORE_DIVERSIFICATION",
            "Global all-world ETF remains core-diversification candidate.",
            SIGNAL_SUPPORTIVE,
            88,
            "Global equity core remains a strong alternative if crypto risk is paused.",
            True,
        ),
        _signal(
            "quality_factor_secondary_signal",
            "quality_factor_etf_candidate",
            "SATELLITE_QUALITY",
            "Quality factor ETF remains secondary satellite candidate.",
            SIGNAL_NEUTRAL,
            71,
            "Quality factor exposure is useful, but lower priority than under-min core BTC in this fixture.",
            False,
        ),
    )


def _score_signals(signals: tuple[AutonomousMarketSignal, ...]) -> int:
    base = 50
    for signal in signals:
        if signal.severity == SIGNAL_SUPPORTIVE:
            base += 12
        elif signal.severity == SIGNAL_CAUTION:
            base -= 4
        elif signal.severity == SIGNAL_BLOCKING:
            base -= 35
        elif signal.severity == SIGNAL_NEUTRAL:
            base += 2

    return max(0, min(base, 100))


def _market_state_for_signals(signals: tuple[AutonomousMarketSignal, ...]) -> str:
    if any(signal.blocks_recommendation or signal.severity == SIGNAL_BLOCKING for signal in signals):
        return MARKET_STATE_BLOCKED
    if any(signal.severity == SIGNAL_SUPPORTIVE for signal in signals):
        return MARKET_STATE_SUPPORTIVE_WITH_CAUTION
    return MARKET_STATE_NEUTRAL_MONITOR


def build_candidate_market_intelligence_cards(
    selected_candidate_id: str,
    selected_sleeve_id: str,
    signals: tuple[AutonomousMarketSignal, ...],
) -> tuple[CandidateMarketIntelligenceCard, ...]:
    candidate_ids = tuple(dict.fromkeys(signal.candidate_id for signal in signals))

    cards: list[CandidateMarketIntelligenceCard] = []
    for candidate_id in candidate_ids:
        candidate_signals = tuple(signal for signal in signals if signal.candidate_id == candidate_id)
        supportive_count = sum(1 for signal in candidate_signals if signal.severity == SIGNAL_SUPPORTIVE)
        caution_count = sum(1 for signal in candidate_signals if signal.severity == SIGNAL_CAUTION)
        blocking_count = sum(
            1
            for signal in candidate_signals
            if signal.severity == SIGNAL_BLOCKING or signal.blocks_recommendation
        )
        market_state = _market_state_for_signals(candidate_signals)
        sleeve_id = selected_sleeve_id if candidate_id == selected_candidate_id else "watchlist_context"

        cards.append(
            CandidateMarketIntelligenceCard(
                candidate_id=candidate_id,
                sleeve_id=sleeve_id,
                selected_by_weekly_recommendation=candidate_id == selected_candidate_id,
                market_state=market_state,
                market_intelligence_score=_score_signals(candidate_signals),
                signal_count=len(candidate_signals),
                supportive_signal_count=supportive_count,
                caution_signal_count=caution_count,
                blocking_signal_count=blocking_count,
                intelligence_summary=(
                    f"{candidate_id} market intelligence state is {market_state} "
                    f"with {len(candidate_signals)} signal(s)."
                ),
                signals=candidate_signals,
                creates_buy_request=False,
                connects_broker=False,
                places_order=False,
                executes_trade=False,
            )
        )

    return tuple(cards)


def audit_v7_0_autonomous_market_intelligence_expansion(
    signals: tuple[AutonomousMarketSignal, ...] | None = None,
) -> AutonomousMarketIntelligenceExpansionResult:
    closeout_result = audit_v6_15_autonomous_command_center_closeout_audit()

    effective_signals = (
        build_example_market_signals(closeout_result.selected_candidate_id)
        if signals is None
        else signals
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v7.0 expands autonomous market intelligence only.",
        "Current v7.0 signals are local fixture intelligence and prepare the public adapter contract.",
        "No buy request, broker connection, order placement, or trade is created.",
    ]

    if closeout_result.blockers:
        blockers.append("Source v6 autonomous command-center closeout audit is blocked.")
    if not closeout_result.v6_chain_complete:
        blockers.append("v6 autonomous chain must be complete before v7.0 market intelligence.")
    if not effective_signals:
        blockers.append("No autonomous market intelligence signals were produced.")

    signal_ids = [signal.signal_id for signal in effective_signals]
    if len(signal_ids) != len(set(signal_ids)):
        blockers.append("Autonomous market signal IDs must be unique.")

    for signal in effective_signals:
        if not signal.summary.strip():
            blockers.append(f"{signal.signal_id}: summary is required.")
        if signal.confidence_score < 0 or signal.confidence_score > 100:
            blockers.append(f"{signal.signal_id}: confidence score must be 0..100.")
        if not signal.safe_signal_only():
            blockers.append(f"{signal.signal_id}: signal must remain non-executable.")
        if signal.creates_buy_request:
            blockers.append(f"{signal.signal_id}: buy request creation is forbidden.")
        if signal.connects_broker:
            blockers.append(f"{signal.signal_id}: broker connection is forbidden.")
        if signal.places_order:
            blockers.append(f"{signal.signal_id}: order placement is forbidden.")
        if signal.executes_trade:
            blockers.append(f"{signal.signal_id}: trade execution is forbidden.")

    candidate_cards = build_candidate_market_intelligence_cards(
        closeout_result.selected_candidate_id,
        closeout_result.selected_sleeve_id,
        effective_signals,
    )

    selected_cards = tuple(
        card for card in candidate_cards if card.candidate_id == closeout_result.selected_candidate_id
    )
    if len(selected_cards) != 1:
        blockers.append("Exactly one selected candidate market intelligence card is required.")
        selected_card = None
    else:
        selected_card = selected_cards[0]

    for card in candidate_cards:
        if not card.safe_card_only():
            blockers.append(f"{card.candidate_id}: market intelligence card must remain non-executable.")
        if card.signal_count <= 0:
            blockers.append(f"{card.candidate_id}: market intelligence card requires signals.")
        if card.creates_buy_request:
            blockers.append(f"{card.candidate_id}: card buy request creation is forbidden.")
        if card.connects_broker:
            blockers.append(f"{card.candidate_id}: card broker connection is forbidden.")
        if card.places_order:
            blockers.append(f"{card.candidate_id}: card order placement is forbidden.")
        if card.executes_trade:
            blockers.append(f"{card.candidate_id}: card trade execution is forbidden.")

    selected_market_state = ""
    selected_market_score = 0
    selected_supported = False
    selected_blocked = False

    if selected_card is not None:
        selected_market_state = selected_card.market_state
        selected_market_score = selected_card.market_intelligence_score
        selected_supported = selected_card.supportive_signal_count > 0
        selected_blocked = selected_card.blocking_signal_count > 0

        if selected_blocked:
            blockers.append("Selected candidate is blocked by market intelligence.")

    safety_flags = {
        "autonomous_market_intelligence_ready": False,
        "market_intelligence_only": True,
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["market_intelligence_only"]:
        blockers.append("v7.0 must remain market-intelligence-only.")
    if not safety_flags["final_user_buy_action_required"]:
        blockers.append("The final user buy action must remain manual.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v7.0 must defer buy requests.")
    if not safety_flags["broker_connection_forbidden"]:
        blockers.append("v7.0 must forbid broker connection.")
    if not safety_flags["order_placement_forbidden"]:
        blockers.append("v7.0 must forbid order placement.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v7.0 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return AutonomousMarketIntelligenceExpansionResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        selected_candidate_id=closeout_result.selected_candidate_id,
        selected_sleeve_id=closeout_result.selected_sleeve_id,
        candidate_card_count=len(candidate_cards),
        total_signal_count=len(effective_signals),
        selected_candidate_market_state=selected_market_state,
        selected_candidate_market_score=selected_market_score,
        selected_candidate_supported=selected_supported,
        selected_candidate_blocked=selected_blocked,
        candidate_cards=candidate_cards,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "autonomous_market_intelligence_ready": ready},
    )
