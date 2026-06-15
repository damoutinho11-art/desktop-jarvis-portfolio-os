"""J.A.R.V.I.S. v6.10 active policy snapshot gap analyzer.

This stage compares the active manual-only policy against the private portfolio
snapshot concept and reports sleeve gaps.

Safety boundary:
- gap analysis only
- warnings/planning context only
- no asset approval
- no weekly buy ticket
- no buy request creation
- no broker/API execution
- no trades
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .jarvis_v6_2_private_portfolio_snapshot_v2 import (
    audit_v6_2_private_portfolio_snapshot_v2,
)
from .jarvis_v6_9_active_policy_registry import (
    ActivePolicyRecord,
    audit_v6_9_active_policy_registry,
)


STATUS_READY = "JARVIS_V6_10_ACTIVE_POLICY_SNAPSHOT_GAP_ANALYZER_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_10_ACTIVE_POLICY_SNAPSHOT_GAP_ANALYZER_BLOCKED_SAFE"

NEXT_STAGE = "v6.11_manual_weekly_planning_context_builder"

GAP_UNDER_MIN = "UNDER_MIN"
GAP_BELOW_PREFERRED = "BELOW_PREFERRED"
GAP_WITHIN_PREFERRED = "WITHIN_PREFERRED"
GAP_ABOVE_PREFERRED = "ABOVE_PREFERRED"
GAP_OVER_MAX = "OVER_MAX"
GAP_UNMAPPED_CURRENT_SLEEVE = "UNMAPPED_CURRENT_SLEEVE"

SLEEVE_CASH_DEFENSIVE = "cash_defensive"
SLEEVE_CRYPTO_CORE_BTC = "crypto_core_btc"
SLEEVE_CRYPTO_SPECULATIVE = "crypto_speculative"


@dataclass(frozen=True)
class CurrentSleeveSnapshot:
    sleeve_id: str
    current_weight_pct: float
    current_value_eur: float
    source: str
    freshness_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "sleeve_id": self.sleeve_id,
            "current_weight_pct": self.current_weight_pct,
            "current_value_eur": self.current_value_eur,
            "source": self.source,
            "freshness_status": self.freshness_status,
        }


@dataclass(frozen=True)
class ActivePolicySleeveGap:
    sleeve_id: str
    current_weight_pct: float
    min_pct: float
    preferred_low_pct: float
    preferred_high_pct: float
    max_pct: float
    gap_status: str
    distance_to_min_pct: float
    distance_to_preferred_low_pct: float
    distance_to_preferred_high_pct: float
    distance_to_max_pct: float
    attention_required: bool
    future_planning_hint: str
    creates_weekly_buy_ticket: bool
    creates_buy_request: bool
    executes_trade: bool

    def within_hard_bounds(self) -> bool:
        return self.min_pct <= self.current_weight_pct <= self.max_pct

    def within_preferred_band(self) -> bool:
        return self.preferred_low_pct <= self.current_weight_pct <= self.preferred_high_pct

    def safe_gap_record_only(self) -> bool:
        return (
            not self.creates_weekly_buy_ticket
            and not self.creates_buy_request
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sleeve_id": self.sleeve_id,
            "current_weight_pct": self.current_weight_pct,
            "min_pct": self.min_pct,
            "preferred_low_pct": self.preferred_low_pct,
            "preferred_high_pct": self.preferred_high_pct,
            "max_pct": self.max_pct,
            "gap_status": self.gap_status,
            "distance_to_min_pct": self.distance_to_min_pct,
            "distance_to_preferred_low_pct": self.distance_to_preferred_low_pct,
            "distance_to_preferred_high_pct": self.distance_to_preferred_high_pct,
            "distance_to_max_pct": self.distance_to_max_pct,
            "attention_required": self.attention_required,
            "future_planning_hint": self.future_planning_hint,
            "creates_weekly_buy_ticket": self.creates_weekly_buy_ticket,
            "creates_buy_request": self.creates_buy_request,
            "executes_trade": self.executes_trade,
            "within_hard_bounds": self.within_hard_bounds(),
            "within_preferred_band": self.within_preferred_band(),
            "safe_gap_record_only": self.safe_gap_record_only(),
        }


@dataclass(frozen=True)
class UnmappedSleeveExposure:
    sleeve_id: str
    current_weight_pct: float
    current_value_eur: float
    reason: str
    creates_weekly_buy_ticket: bool
    creates_buy_request: bool
    executes_trade: bool

    def safe_gap_record_only(self) -> bool:
        return (
            not self.creates_weekly_buy_ticket
            and not self.creates_buy_request
            and not self.executes_trade
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sleeve_id": self.sleeve_id,
            "current_weight_pct": self.current_weight_pct,
            "current_value_eur": self.current_value_eur,
            "reason": self.reason,
            "creates_weekly_buy_ticket": self.creates_weekly_buy_ticket,
            "creates_buy_request": self.creates_buy_request,
            "executes_trade": self.executes_trade,
            "safe_gap_record_only": self.safe_gap_record_only(),
        }


@dataclass(frozen=True)
class ActivePolicySnapshotGapAnalyzerResult:
    status: str
    recommended_next_stage: str
    active_policy_count: int
    analyzed_policy_id: str
    sleeve_gap_count: int
    under_min_count: int
    below_preferred_count: int
    within_preferred_count: int
    above_preferred_count: int
    over_max_count: int
    unmapped_sleeve_count: int
    investable_cash_eur: float
    protected_cash_eur: float
    current_sleeve_weight_total_pct: float
    sleeve_gaps: tuple[ActivePolicySleeveGap, ...]
    unmapped_sleeves: tuple[UnmappedSleeveExposure, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    gap_analyzer_ready: bool
    analysis_only: bool
    asset_approval_deferred: bool
    weekly_buy_ticket_deferred: bool
    buy_request_deferred: bool
    broker_execution_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "active_policy_count": self.active_policy_count,
            "analyzed_policy_id": self.analyzed_policy_id,
            "sleeve_gap_count": self.sleeve_gap_count,
            "under_min_count": self.under_min_count,
            "below_preferred_count": self.below_preferred_count,
            "within_preferred_count": self.within_preferred_count,
            "above_preferred_count": self.above_preferred_count,
            "over_max_count": self.over_max_count,
            "unmapped_sleeve_count": self.unmapped_sleeve_count,
            "investable_cash_eur": self.investable_cash_eur,
            "protected_cash_eur": self.protected_cash_eur,
            "current_sleeve_weight_total_pct": self.current_sleeve_weight_total_pct,
            "sleeve_gaps": [gap.to_dict() for gap in self.sleeve_gaps],
            "unmapped_sleeves": [sleeve.to_dict() for sleeve in self.unmapped_sleeves],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "gap_analyzer_ready": self.gap_analyzer_ready,
            "analysis_only": self.analysis_only,
            "asset_approval_deferred": self.asset_approval_deferred,
            "weekly_buy_ticket_deferred": self.weekly_buy_ticket_deferred,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def build_example_current_sleeve_snapshot() -> tuple[CurrentSleeveSnapshot, ...]:
    return (
        CurrentSleeveSnapshot("equity_core", 58.0, 5800.0, "local_private_snapshot_contract", "SYNTHETIC_CURRENT"),
        CurrentSleeveSnapshot("equity_satellite", 0.0, 0.0, "local_private_snapshot_contract", "SYNTHETIC_CURRENT"),
        CurrentSleeveSnapshot(SLEEVE_CRYPTO_CORE_BTC, 4.0, 400.0, "local_private_snapshot_contract", "SYNTHETIC_CURRENT"),
        CurrentSleeveSnapshot(SLEEVE_CRYPTO_SPECULATIVE, 2.0, 200.0, "local_private_snapshot_contract", "SYNTHETIC_CURRENT"),
        CurrentSleeveSnapshot(SLEEVE_CASH_DEFENSIVE, 26.0, 2600.0, "local_private_snapshot_contract", "SYNTHETIC_CURRENT"),
        CurrentSleeveSnapshot("bond_defensive", 10.0, 1000.0, "local_private_snapshot_contract", "SYNTHETIC_CURRENT"),
    )


def _classify_gap(
    current_weight_pct: float,
    min_pct: float,
    preferred_low_pct: float,
    preferred_high_pct: float,
    max_pct: float,
) -> str:
    if current_weight_pct < min_pct:
        return GAP_UNDER_MIN
    if current_weight_pct < preferred_low_pct:
        return GAP_BELOW_PREFERRED
    if current_weight_pct <= preferred_high_pct:
        return GAP_WITHIN_PREFERRED
    if current_weight_pct <= max_pct:
        return GAP_ABOVE_PREFERRED
    return GAP_OVER_MAX


def _future_planning_hint(sleeve_id: str, gap_status: str) -> str:
    if gap_status == GAP_UNDER_MIN:
        return f"{sleeve_id} is under its hard minimum; future manual planning may prioritize this sleeve."
    if gap_status == GAP_BELOW_PREFERRED:
        return f"{sleeve_id} is below preferred range; future manual planning may consider adding exposure."
    if gap_status == GAP_WITHIN_PREFERRED:
        return f"{sleeve_id} is within preferred range; future manual planning can maintain discipline."
    if gap_status == GAP_ABOVE_PREFERRED:
        return f"{sleeve_id} is above preferred range but inside hard max; future planning may slow additions."
    if gap_status == GAP_OVER_MAX:
        return f"{sleeve_id} is above hard max; future planning should avoid adding until back inside bounds."
    return f"{sleeve_id} needs review."


def analyze_active_policy_snapshot_gaps(
    active_policy: ActivePolicyRecord,
    current_sleeves: tuple[CurrentSleeveSnapshot, ...],
) -> tuple[tuple[ActivePolicySleeveGap, ...], tuple[UnmappedSleeveExposure, ...]]:
    current_by_sleeve = {sleeve.sleeve_id: sleeve for sleeve in current_sleeves}
    policy_sleeve_ids = {band.sleeve_id for band in active_policy.allocation_bands}

    gaps: list[ActivePolicySleeveGap] = []
    for band in active_policy.allocation_bands:
        current = current_by_sleeve.get(
            band.sleeve_id,
            CurrentSleeveSnapshot(
                band.sleeve_id,
                0.0,
                0.0,
                "missing_from_current_snapshot",
                "MISSING",
            ),
        )
        gap_status = _classify_gap(
            current.current_weight_pct,
            band.min_pct,
            band.preferred_low_pct,
            band.preferred_high_pct,
            band.max_pct,
        )
        gaps.append(
            ActivePolicySleeveGap(
                sleeve_id=band.sleeve_id,
                current_weight_pct=current.current_weight_pct,
                min_pct=band.min_pct,
                preferred_low_pct=band.preferred_low_pct,
                preferred_high_pct=band.preferred_high_pct,
                max_pct=band.max_pct,
                gap_status=gap_status,
                distance_to_min_pct=round(current.current_weight_pct - band.min_pct, 2),
                distance_to_preferred_low_pct=round(current.current_weight_pct - band.preferred_low_pct, 2),
                distance_to_preferred_high_pct=round(current.current_weight_pct - band.preferred_high_pct, 2),
                distance_to_max_pct=round(current.current_weight_pct - band.max_pct, 2),
                attention_required=gap_status in {GAP_UNDER_MIN, GAP_OVER_MAX},
                future_planning_hint=_future_planning_hint(band.sleeve_id, gap_status),
                creates_weekly_buy_ticket=False,
                creates_buy_request=False,
                executes_trade=False,
            )
        )

    unmapped = tuple(
        UnmappedSleeveExposure(
            sleeve_id=sleeve.sleeve_id,
            current_weight_pct=sleeve.current_weight_pct,
            current_value_eur=sleeve.current_value_eur,
            reason="Current sleeve exists in snapshot but has no active policy band.",
            creates_weekly_buy_ticket=False,
            creates_buy_request=False,
            executes_trade=False,
        )
        for sleeve in current_sleeves
        if sleeve.sleeve_id not in policy_sleeve_ids
    )

    return tuple(gaps), unmapped


def audit_v6_10_active_policy_snapshot_gap_analyzer(
    current_sleeves: tuple[CurrentSleeveSnapshot, ...] | None = None,
) -> ActivePolicySnapshotGapAnalyzerResult:
    active_policy_result = audit_v6_9_active_policy_registry()
    private_snapshot_result = audit_v6_2_private_portfolio_snapshot_v2()

    effective_current_sleeves = (
        build_example_current_sleeve_snapshot()
        if current_sleeves is None
        else current_sleeves
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.10 reports active-policy sleeve gaps only.",
        "Gap analysis may inform future manual planning but creates no weekly buy ticket.",
        "No buy request, broker action, or trade is created.",
    ]

    if active_policy_result.blockers:
        blockers.append("Source active policy registry is blocked.")
    if not active_policy_result.active_policies:
        blockers.append("No active policy is available for snapshot gap analysis.")
        active_policy = None
    else:
        active_policy = active_policy_result.active_policies[0]

    if not effective_current_sleeves:
        blockers.append("Current sleeve snapshot is empty.")

    total_weight = round(sum(sleeve.current_weight_pct for sleeve in effective_current_sleeves), 2)
    if total_weight <= 0:
        blockers.append("Current sleeve snapshot weight total must be positive.")
    if abs(total_weight - 100.0) > 0.25:
        warnings.append(f"Current sleeve weight total is {total_weight}%, not exactly 100%.")

    if active_policy is None:
        sleeve_gaps: tuple[ActivePolicySleeveGap, ...] = ()
        unmapped_sleeves: tuple[UnmappedSleeveExposure, ...] = ()
        analyzed_policy_id = ""
    else:
        sleeve_gaps, unmapped_sleeves = analyze_active_policy_snapshot_gaps(
            active_policy,
            effective_current_sleeves,
        )
        analyzed_policy_id = active_policy.active_policy_id

    under_min_count = sum(1 for gap in sleeve_gaps if gap.gap_status == GAP_UNDER_MIN)
    below_preferred_count = sum(1 for gap in sleeve_gaps if gap.gap_status == GAP_BELOW_PREFERRED)
    within_preferred_count = sum(1 for gap in sleeve_gaps if gap.gap_status == GAP_WITHIN_PREFERRED)
    above_preferred_count = sum(1 for gap in sleeve_gaps if gap.gap_status == GAP_ABOVE_PREFERRED)
    over_max_count = sum(1 for gap in sleeve_gaps if gap.gap_status == GAP_OVER_MAX)

    if not sleeve_gaps:
        blockers.append("No policy sleeve gaps were produced.")

    if under_min_count < 1:
        warnings.append("No under-min sleeve detected in the default gap scenario.")
    if over_max_count < 1:
        warnings.append("No over-max sleeve detected in the default gap scenario.")

    for gap in sleeve_gaps:
        if not gap.safe_gap_record_only():
            blockers.append(f"{gap.sleeve_id}: sleeve gap must remain record-only.")
        if gap.creates_weekly_buy_ticket:
            blockers.append(f"{gap.sleeve_id}: weekly buy ticket creation is forbidden in v6.10.")
        if gap.creates_buy_request:
            blockers.append(f"{gap.sleeve_id}: buy request creation is forbidden in v6.10.")
        if gap.executes_trade:
            blockers.append(f"{gap.sleeve_id}: trade execution is forbidden in v6.10.")
        if gap.min_pct > gap.max_pct:
            blockers.append(f"{gap.sleeve_id}: invalid policy bounds.")
        if gap.gap_status == GAP_OVER_MAX and gap.distance_to_max_pct <= 0:
            blockers.append(f"{gap.sleeve_id}: over-max gap distance must be positive.")
        if gap.gap_status == GAP_UNDER_MIN and gap.distance_to_min_pct >= 0:
            blockers.append(f"{gap.sleeve_id}: under-min gap distance must be negative.")

    for sleeve in unmapped_sleeves:
        if not sleeve.safe_gap_record_only():
            blockers.append(f"{sleeve.sleeve_id}: unmapped sleeve must remain record-only.")

    safety_flags = {
        "gap_analyzer_ready": False,
        "analysis_only": True,
        "asset_approval_deferred": True,
        "weekly_buy_ticket_deferred": True,
        "buy_request_deferred": True,
        "broker_execution_forbidden": True,
        "no_trades_executed": True,
    }

    if not safety_flags["analysis_only"]:
        blockers.append("v6.10 must remain analysis-only.")
    if not safety_flags["asset_approval_deferred"]:
        blockers.append("v6.10 must defer asset approval.")
    if not safety_flags["weekly_buy_ticket_deferred"]:
        blockers.append("v6.10 must defer weekly buy tickets.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v6.10 must defer buy requests.")
    if not safety_flags["broker_execution_forbidden"]:
        blockers.append("v6.10 must forbid broker execution.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.10 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))

    return ActivePolicySnapshotGapAnalyzerResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        active_policy_count=active_policy_result.active_policy_count,
        analyzed_policy_id=analyzed_policy_id,
        sleeve_gap_count=len(sleeve_gaps),
        under_min_count=under_min_count,
        below_preferred_count=below_preferred_count,
        within_preferred_count=within_preferred_count,
        above_preferred_count=above_preferred_count,
        over_max_count=over_max_count,
        unmapped_sleeve_count=len(unmapped_sleeves),
        investable_cash_eur=private_snapshot_result.investable_cash_eur,
        protected_cash_eur=private_snapshot_result.protected_cash_eur,
        current_sleeve_weight_total_pct=total_weight,
        sleeve_gaps=sleeve_gaps,
        unmapped_sleeves=unmapped_sleeves,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "gap_analyzer_ready": not unique_blockers},
    )
