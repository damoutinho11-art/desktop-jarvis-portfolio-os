"""J.A.R.V.I.S. v6.5 policy candidate generator.

This stage combines the v6 private snapshot concept with quality-ready assets
into manual-review portfolio policy candidates.

Report-only safety boundary:
- policy candidates only
- no active policy mutation
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
from .jarvis_v6_4_asset_quality_scoring_gate import (
    QUALITY_READY,
    QUALITY_WATCHLIST,
    AssetQualityAssessment,
    audit_v6_4_asset_quality_scoring_gate,
)


STATUS_READY = "JARVIS_V6_5_POLICY_CANDIDATE_GENERATOR_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_5_POLICY_CANDIDATE_GENERATOR_BLOCKED_SAFE"

NEXT_STAGE = "v6.6_manual_policy_review_queue"

POLICY_STATUS_MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
POLICY_STATUS_BLOCKED = "BLOCKED"

SLEEVE_EQUITY_CORE = "equity_core"
SLEEVE_EQUITY_SATELLITE = "equity_satellite"
SLEEVE_CRYPTO_CORE_BTC = "crypto_core_btc"
SLEEVE_CRYPTO_SPECULATIVE = "crypto_speculative"
SLEEVE_CASH_DEFENSIVE = "cash_defensive"
SLEEVE_BOND_DEFENSIVE = "bond_defensive"
SLEEVE_COMMODITY_DEFENSIVE = "commodity_defensive"


@dataclass(frozen=True)
class AllocationBand:
    sleeve_id: str
    min_pct: float
    preferred_low_pct: float
    preferred_high_pct: float
    max_pct: float
    rationale: str

    def valid(self) -> bool:
        return (
            0.0 <= self.min_pct
            <= self.preferred_low_pct
            <= self.preferred_high_pct
            <= self.max_pct
            <= 100.0
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sleeve_id": self.sleeve_id,
            "min_pct": self.min_pct,
            "preferred_low_pct": self.preferred_low_pct,
            "preferred_high_pct": self.preferred_high_pct,
            "max_pct": self.max_pct,
            "rationale": self.rationale,
            "valid": self.valid(),
        }


@dataclass(frozen=True)
class PolicyAssetSelection:
    candidate_id: str
    quality_status: str
    role: str
    sleeve_id: str
    max_candidate_weight_pct: float
    included_for_policy_generation: bool
    rationale: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "quality_status": self.quality_status,
            "role": self.role,
            "sleeve_id": self.sleeve_id,
            "max_candidate_weight_pct": self.max_candidate_weight_pct,
            "included_for_policy_generation": self.included_for_policy_generation,
            "rationale": self.rationale,
        }


@dataclass(frozen=True)
class PolicyCandidate:
    policy_id: str
    display_name: str
    policy_status: str
    aggressiveness_score: int
    suitability_reason: str
    allocation_bands: tuple[AllocationBand, ...]
    selected_assets: tuple[PolicyAssetSelection, ...]
    explicit_exclusions: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_review_required: bool
    operator_approved: bool
    active_policy_mutated: bool
    creates_weekly_buy_ticket: bool
    creates_buy_request: bool
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

    def min_cash_or_defensive_pct(self) -> float:
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

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "display_name": self.display_name,
            "policy_status": self.policy_status,
            "aggressiveness_score": self.aggressiveness_score,
            "suitability_reason": self.suitability_reason,
            "allocation_bands": [band.to_dict() for band in self.allocation_bands],
            "selected_assets": [selection.to_dict() for selection in self.selected_assets],
            "explicit_exclusions": list(self.explicit_exclusions),
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_review_required": self.manual_review_required,
            "operator_approved": self.operator_approved,
            "active_policy_mutated": self.active_policy_mutated,
            "creates_weekly_buy_ticket": self.creates_weekly_buy_ticket,
            "creates_buy_request": self.creates_buy_request,
            "executes_trade": self.executes_trade,
            "max_crypto_weight_pct": self.max_crypto_weight_pct(),
            "min_cash_or_defensive_pct": self.min_cash_or_defensive_pct(),
            "has_valid_bands": self.has_valid_bands(),
            "selected_candidate_ids": list(self.selected_candidate_ids()),
        }


@dataclass(frozen=True)
class PolicyCandidateGeneratorResult:
    status: str
    recommended_next_stage: str
    policy_candidate_count: int
    manual_review_candidate_count: int
    blocked_policy_candidate_count: int
    source_quality_ready_count: int
    source_watchlist_count: int
    private_snapshot_investable_cash_eur: float
    private_snapshot_protected_cash_eur: float
    policy_candidates: tuple[PolicyCandidate, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    policy_candidate_generation_ready: bool
    manual_review_required: bool
    active_policy_mutated: bool
    policy_approval_deferred: bool
    asset_approval_deferred: bool
    weekly_buy_ticket_deferred: bool
    buy_request_deferred: bool
    automatic_approval_forbidden: bool
    broker_execution_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "policy_candidate_count": self.policy_candidate_count,
            "manual_review_candidate_count": self.manual_review_candidate_count,
            "blocked_policy_candidate_count": self.blocked_policy_candidate_count,
            "source_quality_ready_count": self.source_quality_ready_count,
            "source_watchlist_count": self.source_watchlist_count,
            "private_snapshot_investable_cash_eur": self.private_snapshot_investable_cash_eur,
            "private_snapshot_protected_cash_eur": self.private_snapshot_protected_cash_eur,
            "policy_candidates": [candidate.to_dict() for candidate in self.policy_candidates],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "policy_candidate_generation_ready": self.policy_candidate_generation_ready,
            "manual_review_required": self.manual_review_required,
            "active_policy_mutated": self.active_policy_mutated,
            "policy_approval_deferred": self.policy_approval_deferred,
            "asset_approval_deferred": self.asset_approval_deferred,
            "weekly_buy_ticket_deferred": self.weekly_buy_ticket_deferred,
            "buy_request_deferred": self.buy_request_deferred,
            "automatic_approval_forbidden": self.automatic_approval_forbidden,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _selection(
    assessment: AssetQualityAssessment,
    role: str,
    sleeve_id: str,
    max_candidate_weight_pct: float,
    rationale: str,
) -> PolicyAssetSelection:
    return PolicyAssetSelection(
        candidate_id=assessment.candidate_id,
        quality_status=assessment.quality_status,
        role=role,
        sleeve_id=sleeve_id,
        max_candidate_weight_pct=max_candidate_weight_pct,
        included_for_policy_generation=True,
        rationale=rationale,
    )


def _quality_assets_by_id(
    assessments: tuple[AssetQualityAssessment, ...],
) -> dict[str, AssetQualityAssessment]:
    allowed = {QUALITY_READY, QUALITY_WATCHLIST}
    return {
        assessment.candidate_id: assessment
        for assessment in assessments
        if assessment.quality_status in allowed and assessment.can_enter_policy_generation_next
    }


def build_policy_candidates_from_quality_assessments(
    assessments: tuple[AssetQualityAssessment, ...],
) -> tuple[PolicyCandidate, ...]:
    assets = _quality_assets_by_id(assessments)

    required = {
        "global_all_world_etf_candidate",
        "btc_candidate",
        "money_market_candidate",
    }
    missing = sorted(required - set(assets))
    if missing:
        return (
            PolicyCandidate(
                policy_id="blocked_missing_core_quality_assets",
                display_name="Blocked: missing core quality assets",
                policy_status=POLICY_STATUS_BLOCKED,
                aggressiveness_score=0,
                suitability_reason="Core quality assets are missing.",
                allocation_bands=(),
                selected_assets=(),
                explicit_exclusions=tuple(missing),
                warnings=(),
                blockers=tuple(f"Missing quality-ready core asset: {item}" for item in missing),
                manual_review_required=True,
                operator_approved=False,
                active_policy_mutated=False,
                creates_weekly_buy_ticket=False,
                creates_buy_request=False,
                executes_trade=False,
            ),
        )

    global_core = assets["global_all_world_etf_candidate"]
    btc = assets["btc_candidate"]
    money_market = assets["money_market_candidate"]
    quality_factor = assets.get("quality_factor_etf_candidate")
    global_fund = assets.get("global_equity_fund_candidate")
    short_bond = assets.get("short_duration_bond_etf_candidate")

    balanced_assets = [
        _selection(global_core, "core_equity_anchor", SLEEVE_EQUITY_CORE, 70.0, "Primary diversified equity anchor."),
        _selection(btc, "core_crypto_anchor", SLEEVE_CRYPTO_CORE_BTC, 20.0, "Core crypto exposure, bounded."),
        _selection(money_market, "cash_defensive_buffer", SLEEVE_CASH_DEFENSIVE, 20.0, "Cash-like defensive liquidity."),
    ]
    if quality_factor:
        balanced_assets.append(
            _selection(quality_factor, "satellite_quality_factor", SLEEVE_EQUITY_SATELLITE, 10.0, "Optional satellite tilt.")
        )
    if short_bond:
        balanced_assets.append(
            _selection(short_bond, "defensive_bond_candidate", SLEEVE_BOND_DEFENSIVE, 15.0, "Optional defensive stabilizer.")
        )

    etf_heavy_assets = [
        _selection(global_core, "dominant_core_equity_anchor", SLEEVE_EQUITY_CORE, 85.0, "ETF-heavy core allocation."),
        _selection(btc, "bounded_crypto_allowance", SLEEVE_CRYPTO_CORE_BTC, 15.0, "BTC allowed but capped."),
        _selection(money_market, "cash_buffer", SLEEVE_CASH_DEFENSIVE, 15.0, "Liquidity and contribution buffer."),
    ]
    if quality_factor:
        etf_heavy_assets.append(
            _selection(quality_factor, "small_satellite_tilt", SLEEVE_EQUITY_SATELLITE, 8.0, "Small satellite only.")
        )

    core_btc_assets = [
        _selection(global_core, "core_equity_anchor", SLEEVE_EQUITY_CORE, 80.0, "Simple global equity base."),
        _selection(btc, "btc_accumulation_candidate", SLEEVE_CRYPTO_CORE_BTC, 25.0, "Aggressive but capped BTC policy sleeve."),
        _selection(money_market, "cash_buffer", SLEEVE_CASH_DEFENSIVE, 15.0, "Manual contribution and volatility buffer."),
    ]

    defensive_assets = [
        _selection(global_core, "reduced_core_equity_anchor", SLEEVE_EQUITY_CORE, 65.0, "Equity remains core but less dominant."),
        _selection(money_market, "defensive_cash_anchor", SLEEVE_CASH_DEFENSIVE, 30.0, "Cash-like defensive anchor."),
        _selection(btc, "small_btc_allowance", SLEEVE_CRYPTO_CORE_BTC, 10.0, "BTC allowed but smaller."),
    ]
    if short_bond:
        defensive_assets.append(
            _selection(short_bond, "bond_defensive_sleeve", SLEEVE_BOND_DEFENSIVE, 20.0, "Short-duration defensive sleeve.")
        )
    if global_fund:
        defensive_assets.append(
            _selection(global_fund, "fund_alternative_watchlist", SLEEVE_EQUITY_CORE, 20.0, "Fund alternative only if ETF route is inferior/unavailable.")
        )

    excluded = (
        "sp_500_etf_candidate excluded until concentration/overlap checks pass.",
        "single_stock_candidate_large_cap excluded until concentration/drawdown controls pass.",
        "hype_candidate excluded until speculative crypto quality improves.",
        "tao_candidate excluded until speculative crypto quality improves.",
        "gold_or_commodity_etf_candidate excluded until role/cost evidence improves.",
        "unverified_microcap_crypto_blocked excluded by quality blockers.",
    )

    return (
        PolicyCandidate(
            policy_id="balanced_aggressive_manual_review",
            display_name="Balanced aggressive manual-review policy",
            policy_status=POLICY_STATUS_MANUAL_REVIEW_REQUIRED,
            aggressiveness_score=82,
            suitability_reason="Aggressive growth orientation with bounded BTC, optional satellite ETF, and cash/bond defensive controls.",
            allocation_bands=(
                AllocationBand(SLEEVE_EQUITY_CORE, 55.0, 60.0, 70.0, 75.0, "Global equity remains the core engine."),
                AllocationBand(SLEEVE_EQUITY_SATELLITE, 0.0, 3.0, 8.0, 12.0, "Small satellite tilts only."),
                AllocationBand(SLEEVE_CRYPTO_CORE_BTC, 5.0, 8.0, 15.0, 20.0, "BTC can be accumulated weekly if risk/cash rules allow."),
                AllocationBand(SLEEVE_CRYPTO_SPECULATIVE, 0.0, 0.0, 3.0, 8.0, "Speculative crypto allowed only after quality improves."),
                AllocationBand(SLEEVE_CASH_DEFENSIVE, 5.0, 7.0, 12.0, 20.0, "Cash-like buffer protects flexibility."),
                AllocationBand(SLEEVE_BOND_DEFENSIVE, 0.0, 0.0, 8.0, 15.0, "Optional stabilizer."),
            ),
            selected_assets=tuple(balanced_assets),
            explicit_exclusions=excluded,
            warnings=("Manual review required before activation.", "No HYPE/TAO policy inclusion until quality improves."),
            blockers=(),
            manual_review_required=True,
            operator_approved=False,
            active_policy_mutated=False,
            creates_weekly_buy_ticket=False,
            creates_buy_request=False,
            executes_trade=False,
        ),
        PolicyCandidate(
            policy_id="etf_heavy_with_crypto_allowance",
            display_name="ETF-heavy policy with bounded crypto allowance",
            policy_status=POLICY_STATUS_MANUAL_REVIEW_REQUIRED,
            aggressiveness_score=76,
            suitability_reason="Simpler ETF-heavy policy with BTC allowance and minimal satellite complexity.",
            allocation_bands=(
                AllocationBand(SLEEVE_EQUITY_CORE, 65.0, 70.0, 82.0, 88.0, "Broad ETF dominates."),
                AllocationBand(SLEEVE_EQUITY_SATELLITE, 0.0, 0.0, 5.0, 10.0, "Satellite stays small."),
                AllocationBand(SLEEVE_CRYPTO_CORE_BTC, 3.0, 5.0, 12.0, 15.0, "BTC allowed but lower than balanced aggressive."),
                AllocationBand(SLEEVE_CRYPTO_SPECULATIVE, 0.0, 0.0, 0.0, 5.0, "Speculative crypto dormant until quality improves."),
                AllocationBand(SLEEVE_CASH_DEFENSIVE, 3.0, 5.0, 10.0, 15.0, "Liquidity reserve."),
            ),
            selected_assets=tuple(etf_heavy_assets),
            explicit_exclusions=excluded,
            warnings=("Lower complexity; may underuse opportunistic satellite assets.",),
            blockers=(),
            manual_review_required=True,
            operator_approved=False,
            active_policy_mutated=False,
            creates_weekly_buy_ticket=False,
            creates_buy_request=False,
            executes_trade=False,
        ),
        PolicyCandidate(
            policy_id="core_etf_btc_accumulation",
            display_name="Core ETF + BTC accumulation policy",
            policy_status=POLICY_STATUS_MANUAL_REVIEW_REQUIRED,
            aggressiveness_score=88,
            suitability_reason="Most aggressive simple candidate: global ETF core plus larger bounded BTC range.",
            allocation_bands=(
                AllocationBand(SLEEVE_EQUITY_CORE, 55.0, 60.0, 75.0, 82.0, "ETF core remains dominant."),
                AllocationBand(SLEEVE_CRYPTO_CORE_BTC, 8.0, 10.0, 20.0, 25.0, "BTC can be accumulated if portfolio state allows."),
                AllocationBand(SLEEVE_CRYPTO_SPECULATIVE, 0.0, 0.0, 3.0, 8.0, "Speculative crypto only after quality improves."),
                AllocationBand(SLEEVE_CASH_DEFENSIVE, 5.0, 7.0, 12.0, 15.0, "Cash-like buffer limits over-aggression."),
            ),
            selected_assets=tuple(core_btc_assets),
            explicit_exclusions=excluded,
            warnings=("Higher crypto ceiling requires strict manual review.",),
            blockers=(),
            manual_review_required=True,
            operator_approved=False,
            active_policy_mutated=False,
            creates_weekly_buy_ticket=False,
            creates_buy_request=False,
            executes_trade=False,
        ),
        PolicyCandidate(
            policy_id="defensive_cash_bond_aware",
            display_name="Defensive cash/bond-aware policy",
            policy_status=POLICY_STATUS_MANUAL_REVIEW_REQUIRED,
            aggressiveness_score=58,
            suitability_reason="Lower-volatility candidate using cash-like and short-duration defensive sleeves.",
            allocation_bands=(
                AllocationBand(SLEEVE_EQUITY_CORE, 40.0, 50.0, 62.0, 70.0, "Equity remains long-term core but reduced."),
                AllocationBand(SLEEVE_CRYPTO_CORE_BTC, 0.0, 3.0, 7.0, 10.0, "BTC allowed but conservative."),
                AllocationBand(SLEEVE_CASH_DEFENSIVE, 10.0, 15.0, 25.0, 35.0, "Cash-like resilience."),
                AllocationBand(SLEEVE_BOND_DEFENSIVE, 0.0, 5.0, 12.0, 20.0, "Optional defensive stabilizer."),
            ),
            selected_assets=tuple(defensive_assets),
            explicit_exclusions=excluded,
            warnings=("Less aggressive; may underperform in strong risk-on markets.",),
            blockers=(),
            manual_review_required=True,
            operator_approved=False,
            active_policy_mutated=False,
            creates_weekly_buy_ticket=False,
            creates_buy_request=False,
            executes_trade=False,
        ),
    )


def audit_v6_5_policy_candidate_generator(
    policy_candidates: tuple[PolicyCandidate, ...] | None = None,
) -> PolicyCandidateGeneratorResult:
    snapshot_result = audit_v6_2_private_portfolio_snapshot_v2()
    quality_result = audit_v6_4_asset_quality_scoring_gate()

    effective_candidates = policy_candidates or build_policy_candidates_from_quality_assessments(
        quality_result.assessments
    )

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.5 generates policy candidates only; manual review queue is deferred to v6.6.",
        "No policy candidate is active, approved, buy-ready, or executable.",
        "Weekly buy amounts are deferred until a later manual buy planning stage.",
    ]

    if snapshot_result.blockers:
        blockers.append("Private snapshot is blocked; policy candidates cannot be generated safely.")
    if quality_result.blockers:
        blockers.append("Asset quality gate is blocked; policy candidates cannot be generated safely.")
    if not effective_candidates:
        blockers.append("No policy candidates generated.")

    policy_ids = [candidate.policy_id for candidate in effective_candidates]
    if len(policy_ids) != len(set(policy_ids)):
        blockers.append("Policy candidate IDs must be unique.")

    manual_review_candidate_count = 0
    blocked_policy_candidate_count = 0

    for candidate in effective_candidates:
        if candidate.policy_status == POLICY_STATUS_MANUAL_REVIEW_REQUIRED:
            manual_review_candidate_count += 1
        if candidate.policy_status == POLICY_STATUS_BLOCKED:
            blocked_policy_candidate_count += 1

        if not candidate.manual_review_required:
            blockers.append(f"{candidate.policy_id}: manual review must be required.")
        if candidate.operator_approved:
            blockers.append(f"{candidate.policy_id}: operator approval is forbidden in v6.5.")
        if candidate.active_policy_mutated:
            blockers.append(f"{candidate.policy_id}: active policy mutation is forbidden in v6.5.")
        if candidate.creates_weekly_buy_ticket:
            blockers.append(f"{candidate.policy_id}: weekly buy ticket creation is forbidden in v6.5.")
        if candidate.creates_buy_request:
            blockers.append(f"{candidate.policy_id}: buy request creation is forbidden in v6.5.")
        if candidate.executes_trade:
            blockers.append(f"{candidate.policy_id}: trade execution is forbidden in v6.5.")
        if not candidate.has_valid_bands():
            blockers.append(f"{candidate.policy_id}: invalid allocation bands.")
        if candidate.max_crypto_weight_pct() > 35.0:
            blockers.append(f"{candidate.policy_id}: crypto max exceeds 35% safety ceiling.")
        if candidate.min_cash_or_defensive_pct() < 3.0:
            blockers.append(f"{candidate.policy_id}: minimum cash/defensive sleeve is too low.")
        if candidate.policy_status == POLICY_STATUS_MANUAL_REVIEW_REQUIRED and not candidate.selected_assets:
            blockers.append(f"{candidate.policy_id}: manual-review policy has no selected assets.")

    if manual_review_candidate_count < 3:
        blockers.append("At least three manual-review policy candidates are required.")

    source_quality_ready_count = quality_result.quality_ready_count
    source_watchlist_count = quality_result.watchlist_count

    safety_flags = {
        "policy_candidate_generation_ready": False,
        "manual_review_required": True,
        "active_policy_mutated": False,
        "policy_approval_deferred": True,
        "asset_approval_deferred": True,
        "weekly_buy_ticket_deferred": True,
        "buy_request_deferred": True,
        "automatic_approval_forbidden": True,
        "broker_execution_forbidden": True,
        "no_trades_executed": True,
    }

    if safety_flags["active_policy_mutated"]:
        blockers.append("v6.5 must not mutate active policy.")
    if not safety_flags["policy_approval_deferred"]:
        blockers.append("v6.5 must defer policy approval.")
    if not safety_flags["asset_approval_deferred"]:
        blockers.append("v6.5 must defer asset approval.")
    if not safety_flags["weekly_buy_ticket_deferred"]:
        blockers.append("v6.5 must defer weekly buy tickets.")
    if not safety_flags["buy_request_deferred"]:
        blockers.append("v6.5 must defer buy requests.")
    if not safety_flags["automatic_approval_forbidden"]:
        blockers.append("v6.5 must forbid automatic approval.")
    if not safety_flags["broker_execution_forbidden"]:
        blockers.append("v6.5 must forbid broker execution.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.5 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))

    return PolicyCandidateGeneratorResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        policy_candidate_count=len(effective_candidates),
        manual_review_candidate_count=manual_review_candidate_count,
        blocked_policy_candidate_count=blocked_policy_candidate_count,
        source_quality_ready_count=source_quality_ready_count,
        source_watchlist_count=source_watchlist_count,
        private_snapshot_investable_cash_eur=snapshot_result.investable_cash_eur,
        private_snapshot_protected_cash_eur=snapshot_result.protected_cash_eur,
        policy_candidates=effective_candidates,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "policy_candidate_generation_ready": not unique_blockers},
    )
