"""J.A.R.V.I.S. v6.4 asset quality scoring gate.

This stage scores universal asset candidates for quality-readiness before they
can be used by later policy/weekly-buy planners.

Report-only safety boundary:
- quality scoring only
- no asset approval
- no policy activation
- no weekly buy candidates
- no buy request creation
- no broker/API execution
- no trades
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


STATUS_READY = "JARVIS_V6_4_ASSET_QUALITY_SCORING_GATE_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_4_ASSET_QUALITY_SCORING_GATE_BLOCKED_SAFE"

NEXT_STAGE = "v6.5_policy_candidate_generator"

QUALITY_READY = "QUALITY_READY"
QUALITY_WATCHLIST = "QUALITY_WATCHLIST"
QUALITY_NEEDS_MORE_DATA = "QUALITY_NEEDS_MORE_DATA"
QUALITY_BLOCKED = "QUALITY_BLOCKED"
QUALITY_AVOID = "QUALITY_AVOID"

ASSET_TYPE_ETF = "ETF"
ASSET_TYPE_FUND = "FUND"
ASSET_TYPE_STOCK = "STOCK"
ASSET_TYPE_CRYPTO = "CRYPTO"
ASSET_TYPE_CASH_LIKE = "CASH_LIKE"
ASSET_TYPE_BOND_ETF = "BOND_ETF"
ASSET_TYPE_COMMODITY_ETF = "COMMODITY_ETF"


@dataclass(frozen=True)
class QualityMetric:
    metric_id: str
    score: int
    max_score: int
    passed: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "score": self.score,
            "max_score": self.max_score,
            "passed": self.passed,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class AssetQualityAssessment:
    candidate_id: str
    asset_type: str
    display_name: str
    quality_status: str
    total_score: int
    max_score: int
    metrics: tuple[QualityMetric, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    can_enter_policy_generation_next: bool
    operator_approved: bool
    policy_asset_approved: bool
    weekly_buy_candidate: bool
    creates_buy_request: bool
    executes_trade: bool

    def score_pct(self) -> float:
        if self.max_score <= 0:
            return 0.0
        return round(self.total_score / self.max_score * 100.0, 2)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "asset_type": self.asset_type,
            "display_name": self.display_name,
            "quality_status": self.quality_status,
            "total_score": self.total_score,
            "max_score": self.max_score,
            "score_pct": self.score_pct(),
            "metrics": [metric.to_dict() for metric in self.metrics],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "can_enter_policy_generation_next": self.can_enter_policy_generation_next,
            "operator_approved": self.operator_approved,
            "policy_asset_approved": self.policy_asset_approved,
            "weekly_buy_candidate": self.weekly_buy_candidate,
            "creates_buy_request": self.creates_buy_request,
            "executes_trade": self.executes_trade,
        }


@dataclass(frozen=True)
class AssetQualityScoringGateResult:
    status: str
    recommended_next_stage: str
    assessment_count: int
    quality_ready_count: int
    watchlist_count: int
    needs_more_data_count: int
    blocked_count: int
    avoid_count: int
    assessments: tuple[AssetQualityAssessment, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    quality_scoring_ready: bool
    exact_policy_generation_deferred: bool
    policy_approval_deferred: bool
    weekly_buy_ticket_deferred: bool
    active_policy_mutated: bool
    automatic_approval_forbidden: bool
    broker_execution_forbidden: bool
    creates_buy_request: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "assessment_count": self.assessment_count,
            "quality_ready_count": self.quality_ready_count,
            "watchlist_count": self.watchlist_count,
            "needs_more_data_count": self.needs_more_data_count,
            "blocked_count": self.blocked_count,
            "avoid_count": self.avoid_count,
            "assessments": [assessment.to_dict() for assessment in self.assessments],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "quality_scoring_ready": self.quality_scoring_ready,
            "exact_policy_generation_deferred": self.exact_policy_generation_deferred,
            "policy_approval_deferred": self.policy_approval_deferred,
            "weekly_buy_ticket_deferred": self.weekly_buy_ticket_deferred,
            "active_policy_mutated": self.active_policy_mutated,
            "automatic_approval_forbidden": self.automatic_approval_forbidden,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "creates_buy_request": self.creates_buy_request,
            "no_trades_executed": self.no_trades_executed,
        }


def _metric(metric_id: str, score: int, max_score: int, threshold: int, reason: str) -> QualityMetric:
    return QualityMetric(
        metric_id=metric_id,
        score=score,
        max_score=max_score,
        passed=score >= threshold,
        reason=reason,
    )


def _status_from_score(
    total_score: int,
    max_score: int,
    blockers: tuple[str, ...],
    required_metric_failed: bool,
) -> str:
    if blockers:
        return QUALITY_BLOCKED
    if required_metric_failed:
        return QUALITY_NEEDS_MORE_DATA
    pct = total_score / max_score * 100.0
    if pct >= 80.0:
        return QUALITY_READY
    if pct >= 65.0:
        return QUALITY_WATCHLIST
    if pct >= 50.0:
        return QUALITY_NEEDS_MORE_DATA
    return QUALITY_AVOID


def _assessment(
    candidate_id: str,
    asset_type: str,
    display_name: str,
    metrics: tuple[QualityMetric, ...],
    blockers: tuple[str, ...] = (),
    warnings: tuple[str, ...] = (),
) -> AssetQualityAssessment:
    total_score = sum(metric.score for metric in metrics)
    max_score = sum(metric.max_score for metric in metrics)
    required_metric_failed = any(not metric.passed for metric in metrics)
    status = _status_from_score(total_score, max_score, blockers, required_metric_failed)
    return AssetQualityAssessment(
        candidate_id=candidate_id,
        asset_type=asset_type,
        display_name=display_name,
        quality_status=status,
        total_score=total_score,
        max_score=max_score,
        metrics=metrics,
        blockers=blockers,
        warnings=warnings,
        can_enter_policy_generation_next=status in {QUALITY_READY, QUALITY_WATCHLIST},
        operator_approved=False,
        policy_asset_approved=False,
        weekly_buy_candidate=False,
        creates_buy_request=False,
        executes_trade=False,
    )


def build_example_asset_quality_assessments() -> tuple[AssetQualityAssessment, ...]:
    return (
        _assessment(
            candidate_id="global_all_world_etf_candidate",
            asset_type=ASSET_TYPE_ETF,
            display_name="Global all-world ETF candidate",
            metrics=(
                _metric("identity_confidence", 10, 10, 8, "ETF identity route is clear."),
                _metric("data_freshness", 9, 10, 7, "Fresh market data is available in the example gate."),
                _metric("cost_and_fee_quality", 9, 10, 7, "Low-cost core ETF profile assumed for quality-gate fixture."),
                _metric("liquidity", 9, 10, 7, "Core ETF liquidity profile passes."),
                _metric("diversification", 10, 10, 8, "Broad global diversification."),
                _metric("overlap_risk", 8, 10, 6, "Overlap must be scored later against actual holdings."),
                _metric("platform_fit", 8, 10, 6, "Lightyear/LHV route exists in registry."),
                _metric("currency_fit", 8, 10, 6, "EUR-compatible route expected."),
            ),
            warnings=("Exact ticker selection remains deferred.",),
        ),
        _assessment(
            candidate_id="global_equity_fund_candidate",
            asset_type=ASSET_TYPE_FUND,
            display_name="Global equity fund candidate",
            metrics=(
                _metric("identity_confidence", 9, 10, 8, "Fund identity route is clear."),
                _metric("data_freshness", 8, 10, 7, "Fresh enough for policy generation fixture."),
                _metric("cost_and_fee_quality", 7, 10, 7, "Fees must be compared against ETF alternatives."),
                _metric("liquidity", 7, 10, 6, "Fund liquidity/access terms require later confirmation."),
                _metric("diversification", 9, 10, 8, "Broad equity fund exposure."),
                _metric("overlap_risk", 7, 10, 6, "Overlap must be compared with ETF core."),
                _metric("platform_fit", 7, 10, 6, "Platform route exists."),
                _metric("currency_fit", 8, 10, 6, "EUR-compatible route expected."),
            ),
            warnings=("Fund may be inferior to ETF if fees or access terms are worse.",),
        ),
        _assessment(
            candidate_id="sp_500_etf_candidate",
            asset_type=ASSET_TYPE_ETF,
            display_name="S&P 500 ETF candidate",
            metrics=(
                _metric("identity_confidence", 10, 10, 8, "ETF identity route is clear."),
                _metric("data_freshness", 9, 10, 7, "Fresh market data is available in fixture."),
                _metric("cost_and_fee_quality", 9, 10, 7, "Low-cost ETF profile."),
                _metric("liquidity", 10, 10, 7, "Very high liquidity profile."),
                _metric("diversification", 7, 10, 8, "Strong but US-concentrated exposure."),
                _metric("overlap_risk", 6, 10, 6, "Likely overlap with global all-world core."),
                _metric("platform_fit", 8, 10, 6, "Platform route exists."),
                _metric("currency_fit", 7, 10, 6, "Currency exposure requires policy treatment."),
            ),
            warnings=("US concentration and overlap require policy-level scoring.",),
        ),
        _assessment(
            candidate_id="quality_factor_etf_candidate",
            asset_type=ASSET_TYPE_ETF,
            display_name="Quality factor ETF candidate",
            metrics=(
                _metric("identity_confidence", 9, 10, 8, "ETF identity route is clear."),
                _metric("data_freshness", 8, 10, 7, "Fresh market data is available in fixture."),
                _metric("cost_and_fee_quality", 7, 10, 7, "Factor ETF fees require comparison."),
                _metric("liquidity", 7, 10, 7, "Liquidity acceptable but lower than broad core ETFs."),
                _metric("diversification", 7, 10, 7, "Factor diversification acceptable."),
                _metric("overlap_risk", 6, 10, 6, "Overlap with global core must be checked."),
                _metric("platform_fit", 8, 10, 6, "Platform route exists."),
                _metric("currency_fit", 7, 10, 6, "Currency route acceptable."),
            ),
            warnings=("Satellite ETF should remain bounded.",),
        ),
        _assessment(
            candidate_id="single_stock_candidate_large_cap",
            asset_type=ASSET_TYPE_STOCK,
            display_name="Large-cap stock candidate",
            metrics=(
                _metric("identity_confidence", 9, 10, 8, "Company identity is clear."),
                _metric("data_freshness", 8, 10, 7, "Market data fresh enough for fixture."),
                _metric("fundamental_quality", 7, 10, 7, "Fundamental snapshot passes minimum gate."),
                _metric("liquidity", 9, 10, 7, "Large-cap liquidity expected."),
                _metric("concentration_risk", 5, 10, 6, "Single-stock concentration risk is material."),
                _metric("drawdown_risk", 5, 10, 6, "Single-stock drawdown risk needs more policy control."),
                _metric("platform_fit", 8, 10, 6, "Platform route exists."),
            ),
            warnings=("Stock candidate remains watchlist until concentration rules are stronger.",),
        ),
        _assessment(
            candidate_id="btc_candidate",
            asset_type=ASSET_TYPE_CRYPTO,
            display_name="Bitcoin candidate",
            metrics=(
                _metric("identity_confidence", 10, 10, 8, "BTC identity is clear."),
                _metric("data_freshness", 9, 10, 7, "Fresh crypto market data fixture."),
                _metric("liquidity", 10, 10, 8, "BTC liquidity is strongest among crypto candidates."),
                _metric("custody_and_platform_fit", 7, 10, 6, "Manual crypto route exists, custody still requires review."),
                _metric("drawdown_risk", 5, 10, 5, "High drawdown risk but acceptable for bounded crypto sleeve."),
                _metric("portfolio_role", 8, 10, 7, "Core crypto role is clear."),
                _metric("speculation_penalty", 7, 10, 6, "Less speculative than alt crypto candidates."),
            ),
            warnings=("Weekly BTC buys remain bounded by policy and portfolio state.",),
        ),
        _assessment(
            candidate_id="hype_candidate",
            asset_type=ASSET_TYPE_CRYPTO,
            display_name="HYPE candidate",
            metrics=(
                _metric("identity_confidence", 8, 10, 8, "HYPE identity route passes fixture minimum."),
                _metric("data_freshness", 8, 10, 7, "Fresh crypto market data fixture."),
                _metric("liquidity", 6, 10, 7, "Liquidity needs stronger confirmation before policy use."),
                _metric("custody_and_platform_fit", 6, 10, 6, "Manual route exists."),
                _metric("drawdown_risk", 4, 10, 5, "High drawdown risk."),
                _metric("portfolio_role", 6, 10, 6, "Speculative role only."),
                _metric("speculation_penalty", 4, 10, 6, "Speculative crypto must remain small."),
            ),
            warnings=("Speculative crypto candidate requires strict sizing and more data.",),
        ),
        _assessment(
            candidate_id="tao_candidate",
            asset_type=ASSET_TYPE_CRYPTO,
            display_name="TAO candidate",
            metrics=(
                _metric("identity_confidence", 8, 10, 8, "TAO identity route passes fixture minimum."),
                _metric("data_freshness", 8, 10, 7, "Fresh crypto market data fixture."),
                _metric("liquidity", 6, 10, 7, "Liquidity needs stronger confirmation before policy use."),
                _metric("custody_and_platform_fit", 6, 10, 6, "Manual route exists."),
                _metric("drawdown_risk", 4, 10, 5, "High drawdown risk."),
                _metric("portfolio_role", 6, 10, 6, "Speculative role only."),
                _metric("speculation_penalty", 4, 10, 6, "Speculative crypto must remain small."),
            ),
            warnings=("Speculative crypto candidate requires strict sizing and more data.",),
        ),
        _assessment(
            candidate_id="money_market_candidate",
            asset_type=ASSET_TYPE_CASH_LIKE,
            display_name="EUR money-market candidate",
            metrics=(
                _metric("identity_confidence", 9, 10, 8, "Product identity route is clear."),
                _metric("data_freshness", 8, 10, 7, "Terms freshness passes fixture minimum."),
                _metric("yield_terms", 8, 10, 7, "Yield terms are usable for scoring."),
                _metric("capital_risk", 8, 10, 7, "Lower-risk cash-like sleeve candidate."),
                _metric("liquidity", 8, 10, 7, "Liquidity/access terms acceptable."),
                _metric("platform_fit", 8, 10, 6, "Platform route exists."),
                _metric("currency_fit", 10, 10, 8, "EUR fit is strong."),
            ),
            warnings=("Must not consume protected emergency cash.",),
        ),
        _assessment(
            candidate_id="short_duration_bond_etf_candidate",
            asset_type=ASSET_TYPE_BOND_ETF,
            display_name="Short-duration bond ETF candidate",
            metrics=(
                _metric("identity_confidence", 8, 10, 8, "ETF identity route passes."),
                _metric("data_freshness", 7, 10, 7, "Fresh enough for watchlist."),
                _metric("cost_and_fee_quality", 7, 10, 7, "Fees acceptable in fixture."),
                _metric("duration_risk", 7, 10, 6, "Short-duration profile controls rate risk."),
                _metric("liquidity", 7, 10, 6, "Liquidity acceptable."),
                _metric("platform_fit", 7, 10, 6, "Platform route exists."),
                _metric("currency_fit", 8, 10, 6, "EUR route expected."),
            ),
            warnings=("Bond ETF role depends on defensive policy need.",),
        ),
        _assessment(
            candidate_id="gold_or_commodity_etf_candidate",
            asset_type=ASSET_TYPE_COMMODITY_ETF,
            display_name="Gold or broad commodity ETF candidate",
            metrics=(
                _metric("identity_confidence", 8, 10, 8, "Commodity ETF identity route passes."),
                _metric("data_freshness", 7, 10, 7, "Fresh enough for watchlist."),
                _metric("cost_and_fee_quality", 6, 10, 7, "Commodity ETF fee/structure needs more review."),
                _metric("liquidity", 7, 10, 6, "Liquidity acceptable."),
                _metric("portfolio_role", 6, 10, 6, "Defensive/hedge role only."),
                _metric("drawdown_risk", 6, 10, 5, "Commodity drawdown risk acceptable for watchlist."),
                _metric("platform_fit", 7, 10, 6, "Platform route exists."),
            ),
            warnings=("Commodity role requires policy-level justification.",),
        ),
        _assessment(
            candidate_id="unverified_microcap_crypto_blocked",
            asset_type=ASSET_TYPE_CRYPTO,
            display_name="Unverified microcap crypto example",
            metrics=(
                _metric("identity_confidence", 2, 10, 8, "Identity/source route is weak."),
                _metric("data_freshness", 2, 10, 7, "Fresh reliable data missing."),
                _metric("liquidity", 1, 10, 8, "Liquidity route is insufficient."),
                _metric("custody_and_platform_fit", 1, 10, 6, "Custody/platform route unknown."),
                _metric("drawdown_risk", 1, 10, 5, "Unbounded drawdown risk."),
                _metric("portfolio_role", 1, 10, 6, "No justified role in bounded policy."),
                _metric("speculation_penalty", 0, 10, 6, "Speculation risk blocks candidate."),
            ),
            blockers=("Identity/source quality is insufficient.", "Liquidity/custody route is insufficient."),
            warnings=("Blocked example proves weak assets do not advance.",),
        ),
    )


def audit_v6_4_asset_quality_scoring_gate(
    assessments: tuple[AssetQualityAssessment, ...] | None = None,
) -> AssetQualityScoringGateResult:
    effective_assessments = assessments or build_example_asset_quality_assessments()

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.4 scores quality only; policy generation is deferred to v6.5.",
        "Scores are deterministic local fixtures, not live market recommendations.",
        "No quality-ready candidate is approved or buy-ready in this stage.",
    ]

    if not effective_assessments:
        blockers.append("No asset quality assessments supplied.")

    candidate_ids = [assessment.candidate_id for assessment in effective_assessments]
    if len(candidate_ids) != len(set(candidate_ids)):
        blockers.append("Assessment candidate IDs must be unique.")

    for assessment in effective_assessments:
        if assessment.operator_approved:
            blockers.append(f"{assessment.candidate_id}: operator approval is forbidden in v6.4.")
        if assessment.policy_asset_approved:
            blockers.append(f"{assessment.candidate_id}: policy asset approval is forbidden in v6.4.")
        if assessment.weekly_buy_candidate:
            blockers.append(f"{assessment.candidate_id}: weekly buy candidacy is forbidden in v6.4.")
        if assessment.creates_buy_request:
            blockers.append(f"{assessment.candidate_id}: buy request creation is forbidden in v6.4.")
        if assessment.executes_trade:
            blockers.append(f"{assessment.candidate_id}: trade execution is forbidden in v6.4.")
        if not assessment.metrics:
            blockers.append(f"{assessment.candidate_id}: quality metrics missing.")
        if assessment.quality_status == QUALITY_READY and assessment.blockers:
            blockers.append(f"{assessment.candidate_id}: quality-ready candidate has blockers.")
        if assessment.quality_status == QUALITY_BLOCKED and not assessment.blockers:
            blockers.append(f"{assessment.candidate_id}: blocked candidate lacks blocker reasons.")
        if assessment.can_enter_policy_generation_next and assessment.quality_status not in {
            QUALITY_READY,
            QUALITY_WATCHLIST,
        }:
            blockers.append(
                f"{assessment.candidate_id}: non-ready status cannot enter policy generation."
            )

    quality_ready_count = sum(
        1 for assessment in effective_assessments if assessment.quality_status == QUALITY_READY
    )
    watchlist_count = sum(
        1 for assessment in effective_assessments if assessment.quality_status == QUALITY_WATCHLIST
    )
    needs_more_data_count = sum(
        1 for assessment in effective_assessments if assessment.quality_status == QUALITY_NEEDS_MORE_DATA
    )
    blocked_count = sum(
        1 for assessment in effective_assessments if assessment.quality_status == QUALITY_BLOCKED
    )
    avoid_count = sum(
        1 for assessment in effective_assessments if assessment.quality_status == QUALITY_AVOID
    )

    if quality_ready_count < 3:
        blockers.append("At least three candidates should be quality-ready for v6.5 policy generation.")
    if blocked_count < 1:
        blockers.append("At least one blocked candidate should prove the quality gate blocks weak assets.")

    safety_flags = {
        "quality_scoring_ready": False,
        "exact_policy_generation_deferred": True,
        "policy_approval_deferred": True,
        "weekly_buy_ticket_deferred": True,
        "active_policy_mutated": False,
        "automatic_approval_forbidden": True,
        "broker_execution_forbidden": True,
        "creates_buy_request": False,
        "no_trades_executed": True,
    }

    if not safety_flags["exact_policy_generation_deferred"]:
        blockers.append("v6.4 must defer exact policy generation.")
    if not safety_flags["policy_approval_deferred"]:
        blockers.append("v6.4 must defer policy approval.")
    if not safety_flags["weekly_buy_ticket_deferred"]:
        blockers.append("v6.4 must defer weekly buy tickets.")
    if safety_flags["active_policy_mutated"]:
        blockers.append("v6.4 must not mutate active policy.")
    if not safety_flags["automatic_approval_forbidden"]:
        blockers.append("v6.4 must forbid automatic approval.")
    if not safety_flags["broker_execution_forbidden"]:
        blockers.append("v6.4 must forbid broker execution.")
    if safety_flags["creates_buy_request"]:
        blockers.append("v6.4 must not create buy requests.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.4 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    return AssetQualityScoringGateResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        assessment_count=len(effective_assessments),
        quality_ready_count=quality_ready_count,
        watchlist_count=watchlist_count,
        needs_more_data_count=needs_more_data_count,
        blocked_count=blocked_count,
        avoid_count=avoid_count,
        assessments=effective_assessments,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "quality_scoring_ready": not unique_blockers},
    )
