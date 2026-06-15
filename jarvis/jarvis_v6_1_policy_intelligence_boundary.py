"""J.A.R.V.I.S. v6.1 policy intelligence boundary.

This stage defines how J.A.R.V.I.S. may recommend aggressive-but-bounded
candidate portfolio policies without silently changing the active policy.

Report-only safety boundary:
- no active policy mutation
- no automatic approval
- no broker execution
- no buy request creation
- no trades
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


STATUS_READY = "JARVIS_V6_1_POLICY_INTELLIGENCE_BOUNDARY_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_1_POLICY_INTELLIGENCE_BOUNDARY_BLOCKED_SAFE"

POLICY_CANDIDATE = "CANDIDATE_POLICY"
POLICY_RECOMMENDED_FOR_REVIEW = "RECOMMENDED_FOR_MANUAL_REVIEW"
POLICY_NEEDS_REVIEW = "NEEDS_REVIEW_POLICY"
POLICY_NOT_RECOMMENDED = "NOT_RECOMMENDED_POLICY"

TICKET_POLICY_CHANGE_REVIEW_ONLY = "POLICY_CHANGE_REVIEW_ONLY"


@dataclass(frozen=True)
class PolicyBand:
    sleeve_id: str
    name: str
    min_weight_pct: float
    preferred_min_weight_pct: float
    preferred_max_weight_pct: float
    max_weight_pct: float
    weekly_buy_allowed: bool
    asset_universe: tuple[str, ...]
    purpose: str
    risk_notes: tuple[str, ...]

    def is_flexible(self) -> bool:
        return (
            self.min_weight_pct < self.preferred_min_weight_pct
            and self.preferred_min_weight_pct < self.preferred_max_weight_pct
            and self.preferred_max_weight_pct < self.max_weight_pct
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "sleeve_id": self.sleeve_id,
            "name": self.name,
            "min_weight_pct": self.min_weight_pct,
            "preferred_min_weight_pct": self.preferred_min_weight_pct,
            "preferred_max_weight_pct": self.preferred_max_weight_pct,
            "max_weight_pct": self.max_weight_pct,
            "weekly_buy_allowed": self.weekly_buy_allowed,
            "asset_universe": list(self.asset_universe),
            "purpose": self.purpose,
            "risk_notes": list(self.risk_notes),
            "is_flexible": self.is_flexible(),
        }


@dataclass(frozen=True)
class CandidatePolicy:
    policy_id: str
    name: str
    status: str
    risk_profile: str
    score_total: int
    score_breakdown: dict[str, int]
    bands: tuple[PolicyBand, ...]
    rationale: tuple[str, ...]
    counterarguments: tuple[str, ...]
    manual_policy_change_ticket_required: bool
    active_policy_mutated: bool
    automatic_approval_granted: bool
    creates_buy_request: bool
    executes_trade: bool

    def crypto_weekly_buy_allowed(self) -> bool:
        return any(
            band.weekly_buy_allowed
            for band in self.bands
            if "crypto" in band.sleeve_id
        )

    def uses_flexible_bands(self) -> bool:
        return all(band.is_flexible() for band in self.bands)

    def has_broad_etf_universe(self) -> bool:
        etf_assets: set[str] = set()
        for band in self.bands:
            if "equity" in band.sleeve_id or "defensive" in band.sleeve_id:
                etf_assets.update(band.asset_universe)
        return len(etf_assets) >= 6 and "global_all_world_etf" in etf_assets

    def max_crypto_weight_pct(self) -> float:
        return sum(
            band.max_weight_pct
            for band in self.bands
            if "crypto" in band.sleeve_id
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "status": self.status,
            "risk_profile": self.risk_profile,
            "score_total": self.score_total,
            "score_breakdown": dict(self.score_breakdown),
            "bands": [band.to_dict() for band in self.bands],
            "rationale": list(self.rationale),
            "counterarguments": list(self.counterarguments),
            "manual_policy_change_ticket_required": self.manual_policy_change_ticket_required,
            "active_policy_mutated": self.active_policy_mutated,
            "automatic_approval_granted": self.automatic_approval_granted,
            "creates_buy_request": self.creates_buy_request,
            "executes_trade": self.executes_trade,
            "crypto_weekly_buy_allowed": self.crypto_weekly_buy_allowed(),
            "uses_flexible_bands": self.uses_flexible_bands(),
            "has_broad_etf_universe": self.has_broad_etf_universe(),
            "max_crypto_weight_pct": self.max_crypto_weight_pct(),
        }


@dataclass(frozen=True)
class PolicyChangeTicket:
    ticket_type: str
    candidate_policy_id: str
    manual_approval_required: bool
    approved: bool
    active_policy_mutated: bool
    creates_buy_request: bool
    executes_trade: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "ticket_type": self.ticket_type,
            "candidate_policy_id": self.candidate_policy_id,
            "manual_approval_required": self.manual_approval_required,
            "approved": self.approved,
            "active_policy_mutated": self.active_policy_mutated,
            "creates_buy_request": self.creates_buy_request,
            "executes_trade": self.executes_trade,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class PolicyIntelligenceBoundaryResult:
    status: str
    recommended_next_stage: str
    candidate_policy_count: int
    recommended_policy_id: str
    candidate_policies: tuple[CandidatePolicy, ...]
    policy_change_tickets: tuple[PolicyChangeTicket, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    policy_intelligence_enabled: bool
    flexible_bands_required: bool
    broad_etf_universe_required: bool
    weekly_crypto_buy_allowed_if_within_risk_bands: bool
    active_policy_mutated: bool
    automatic_policy_change_forbidden: bool
    automatic_approval_forbidden: bool
    manual_policy_approval_required: bool
    broker_execution_forbidden: bool
    creates_buy_request: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "candidate_policy_count": self.candidate_policy_count,
            "recommended_policy_id": self.recommended_policy_id,
            "candidate_policies": [policy.to_dict() for policy in self.candidate_policies],
            "policy_change_tickets": [ticket.to_dict() for ticket in self.policy_change_tickets],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "policy_intelligence_enabled": self.policy_intelligence_enabled,
            "flexible_bands_required": self.flexible_bands_required,
            "broad_etf_universe_required": self.broad_etf_universe_required,
            "weekly_crypto_buy_allowed_if_within_risk_bands": (
                self.weekly_crypto_buy_allowed_if_within_risk_bands
            ),
            "active_policy_mutated": self.active_policy_mutated,
            "automatic_policy_change_forbidden": self.automatic_policy_change_forbidden,
            "automatic_approval_forbidden": self.automatic_approval_forbidden,
            "manual_policy_approval_required": self.manual_policy_approval_required,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "creates_buy_request": self.creates_buy_request,
            "no_trades_executed": self.no_trades_executed,
        }


def _equity_core_band(min_pct: float, low_pct: float, high_pct: float, max_pct: float) -> PolicyBand:
    return PolicyBand(
        sleeve_id="equity_core",
        name="Equity core",
        min_weight_pct=min_pct,
        preferred_min_weight_pct=low_pct,
        preferred_max_weight_pct=high_pct,
        max_weight_pct=max_pct,
        weekly_buy_allowed=True,
        asset_universe=(
            "global_all_world_etf",
            "developed_world_etf",
            "sp_500_etf",
            "europe_equity_etf",
            "emerging_markets_etf",
            "global_ex_us_etf",
        ),
        purpose="Long-term diversified equity engine.",
        risk_notes=(
            "Global ETF is the anchor, not the only ETF J.A.R.V.I.S. may evaluate.",
            "Regional and broad index ETFs may be compared for cost, overlap, currency, and platform fit.",
        ),
    )


def _equity_satellite_band(min_pct: float, low_pct: float, high_pct: float, max_pct: float) -> PolicyBand:
    return PolicyBand(
        sleeve_id="equity_satellite",
        name="Equity satellite",
        min_weight_pct=min_pct,
        preferred_min_weight_pct=low_pct,
        preferred_max_weight_pct=high_pct,
        max_weight_pct=max_pct,
        weekly_buy_allowed=True,
        asset_universe=(
            "quality_factor_etf",
            "momentum_factor_etf",
            "growth_etf",
            "small_cap_etf",
            "sector_etf",
            "single_stock_candidate",
        ),
        purpose="Optional higher-conviction equity tilt after core diversification is protected.",
        risk_notes=(
            "Satellite exposure must be penalized for overlap with equity core.",
            "Single stocks require stronger quality, liquidity, concentration, and thesis checks.",
        ),
    )


def _btc_crypto_band(min_pct: float, low_pct: float, high_pct: float, max_pct: float) -> PolicyBand:
    return PolicyBand(
        sleeve_id="crypto_core_btc",
        name="Crypto core BTC",
        min_weight_pct=min_pct,
        preferred_min_weight_pct=low_pct,
        preferred_max_weight_pct=high_pct,
        max_weight_pct=max_pct,
        weekly_buy_allowed=True,
        asset_universe=("btc",),
        purpose="Core crypto exposure with stronger liquidity and longer history than speculative crypto.",
        risk_notes=(
            "BTC may be bought weekly when inside risk, cash, and portfolio-state rules.",
            "BTC buying is reduced or blocked near the upper risk band.",
        ),
    )


def _speculative_crypto_band(min_pct: float, low_pct: float, high_pct: float, max_pct: float) -> PolicyBand:
    return PolicyBand(
        sleeve_id="crypto_speculative",
        name="Speculative crypto",
        min_weight_pct=min_pct,
        preferred_min_weight_pct=low_pct,
        preferred_max_weight_pct=high_pct,
        max_weight_pct=max_pct,
        weekly_buy_allowed=True,
        asset_universe=("hype", "tao", "future_approved_speculative_crypto"),
        purpose="Small aggressive sleeve for approved high-conviction crypto only.",
        risk_notes=(
            "Speculative crypto must remain small and explicitly bounded.",
            "No unapproved token may become buy-ready without manual review.",
        ),
    )


def _cash_defensive_band(min_pct: float, low_pct: float, high_pct: float, max_pct: float) -> PolicyBand:
    return PolicyBand(
        sleeve_id="cash_defensive",
        name="Cash and defensive",
        min_weight_pct=min_pct,
        preferred_min_weight_pct=low_pct,
        preferred_max_weight_pct=high_pct,
        max_weight_pct=max_pct,
        weekly_buy_allowed=False,
        asset_universe=(
            "cash",
            "money_market_fund",
            "short_duration_bond_etf",
            "treasury_bill_like_fund",
            "gold_or_commodity_etf",
        ),
        purpose="Liquidity, emergency protection, and optional defensive ballast.",
        risk_notes=(
            "Emergency cash is protected and not investable cash.",
            "Defensive assets may be evaluated, but not used to bypass cash protection rules.",
        ),
    )


def build_candidate_policies() -> tuple[CandidatePolicy, ...]:
    return (
        CandidatePolicy(
            policy_id="balanced_aggressive_flexible_bands",
            name="Balanced aggressive flexible bands",
            status=POLICY_RECOMMENDED_FOR_REVIEW,
            risk_profile="aggressive_but_bounded",
            score_total=91,
            score_breakdown={
                "diversification": 18,
                "risk_boundary": 19,
                "crypto_permission": 17,
                "flexibility": 14,
                "operability": 12,
                "simplicity": 11,
            },
            bands=(
                _equity_core_band(45.0, 55.0, 75.0, 85.0),
                _equity_satellite_band(0.0, 5.0, 15.0, 25.0),
                _btc_crypto_band(2.5, 5.0, 12.5, 20.0),
                _speculative_crypto_band(0.0, 1.0, 5.0, 10.0),
                _cash_defensive_band(0.0, 2.5, 10.0, 20.0),
            ),
            rationale=(
                "Keeps the equity core dominant while allowing ETF/fund/stock satellites.",
                "Allows weekly crypto buys when inside portfolio, cash, and risk bands.",
                "Keeps speculative crypto explicitly small.",
                "Uses flexible ranges instead of strict fixed allocations.",
            ),
            counterarguments=(
                "Requires better private portfolio data before weekly buy sizing.",
                "Requires universal asset quality scoring before choosing exact ETFs, stocks, or tokens.",
            ),
            manual_policy_change_ticket_required=True,
            active_policy_mutated=False,
            automatic_approval_granted=False,
            creates_buy_request=False,
            executes_trade=False,
        ),
        CandidatePolicy(
            policy_id="simple_core_plus_crypto",
            name="Simple core plus crypto",
            status=POLICY_CANDIDATE,
            risk_profile="simple_aggressive",
            score_total=84,
            score_breakdown={
                "diversification": 15,
                "risk_boundary": 18,
                "crypto_permission": 16,
                "flexibility": 12,
                "operability": 13,
                "simplicity": 10,
            },
            bands=(
                _equity_core_band(55.0, 65.0, 82.5, 90.0),
                _equity_satellite_band(0.0, 2.5, 7.5, 15.0),
                _btc_crypto_band(2.5, 5.0, 12.5, 17.5),
                _speculative_crypto_band(0.0, 0.5, 4.0, 7.5),
                _cash_defensive_band(0.0, 2.5, 7.5, 15.0),
            ),
            rationale=(
                "Simpler than the recommended candidate.",
                "Still allows weekly crypto buying inside controlled limits.",
                "Keeps ETF core very dominant.",
            ),
            counterarguments=(
                "May be too conservative for the desired aggressive policy intelligence layer.",
                "Equity satellites may be underused.",
            ),
            manual_policy_change_ticket_required=True,
            active_policy_mutated=False,
            automatic_approval_granted=False,
            creates_buy_request=False,
            executes_trade=False,
        ),
        CandidatePolicy(
            policy_id="high_crypto_aggressive_review",
            name="High crypto aggressive review",
            status=POLICY_NEEDS_REVIEW,
            risk_profile="aggressive_high_crypto",
            score_total=73,
            score_breakdown={
                "diversification": 13,
                "risk_boundary": 10,
                "crypto_permission": 19,
                "flexibility": 13,
                "operability": 9,
                "simplicity": 9,
            },
            bands=(
                _equity_core_band(35.0, 45.0, 65.0, 75.0),
                _equity_satellite_band(0.0, 5.0, 20.0, 30.0),
                _btc_crypto_band(5.0, 10.0, 17.5, 25.0),
                _speculative_crypto_band(0.0, 2.5, 7.5, 15.0),
                _cash_defensive_band(0.0, 2.5, 7.5, 15.0),
            ),
            rationale=(
                "Allows the most crypto upside among the candidate policies.",
                "May fit only if income stability, emergency cash, and drawdown tolerance are strong.",
            ),
            counterarguments=(
                "Crypto concentration can become too high for a professional bounded policy.",
                "Speculative crypto ceiling requires stricter review before approval.",
                "Not recommended as default until private cash and drawdown tolerance are validated.",
            ),
            manual_policy_change_ticket_required=True,
            active_policy_mutated=False,
            automatic_approval_granted=False,
            creates_buy_request=False,
            executes_trade=False,
        ),
    )


def build_policy_change_tickets(
    candidate_policies: tuple[CandidatePolicy, ...],
) -> tuple[PolicyChangeTicket, ...]:
    return tuple(
        PolicyChangeTicket(
            ticket_type=TICKET_POLICY_CHANGE_REVIEW_ONLY,
            candidate_policy_id=policy.policy_id,
            manual_approval_required=True,
            approved=False,
            active_policy_mutated=False,
            creates_buy_request=False,
            executes_trade=False,
            reason=(
                "Candidate policy may be reviewed by Diogo, but cannot become active "
                "without manual approval."
            ),
        )
        for policy in candidate_policies
    )


def audit_v6_1_policy_intelligence_boundary() -> PolicyIntelligenceBoundaryResult:
    candidate_policies = build_candidate_policies()
    tickets = build_policy_change_tickets(candidate_policies)
    recommended_policy = next(
        policy
        for policy in candidate_policies
        if policy.status == POLICY_RECOMMENDED_FOR_REVIEW
    )

    blockers: list[str] = []
    warnings = [
        "v6.1 defines policy intelligence boundaries only; it does not scan live assets.",
        "Exact weekly buy sizing requires v6.2 private portfolio snapshot v2.",
        "Exact asset selection requires v6.3/v6.4 universal asset registry and quality scoring.",
        "Weekly crypto buying is allowed only inside bounded risk, cash, and portfolio-state rules.",
        "Global ETF exposure is a core sleeve, not the full ETF universe.",
    ]

    if not recommended_policy.uses_flexible_bands():
        blockers.append("recommended policy does not use flexible bands.")
    if not recommended_policy.crypto_weekly_buy_allowed():
        blockers.append("recommended policy does not allow bounded weekly crypto buying.")
    if not recommended_policy.has_broad_etf_universe():
        blockers.append("recommended policy does not include broad ETF/fund universe coverage.")
    if recommended_policy.max_crypto_weight_pct() > 35.0:
        blockers.append("recommended policy crypto ceiling is too high for bounded default review.")

    for policy in candidate_policies:
        if policy.active_policy_mutated:
            blockers.append(f"{policy.policy_id} mutates active policy.")
        if policy.automatic_approval_granted:
            blockers.append(f"{policy.policy_id} grants automatic approval.")
        if policy.creates_buy_request:
            blockers.append(f"{policy.policy_id} creates a buy request.")
        if policy.executes_trade:
            blockers.append(f"{policy.policy_id} executes a trade.")
        if not policy.manual_policy_change_ticket_required:
            blockers.append(f"{policy.policy_id} lacks required manual policy-change ticket.")

    for ticket in tickets:
        if not ticket.manual_approval_required:
            blockers.append(f"{ticket.candidate_policy_id} ticket does not require manual approval.")
        if ticket.approved:
            blockers.append(f"{ticket.candidate_policy_id} ticket is already approved.")
        if ticket.active_policy_mutated:
            blockers.append(f"{ticket.candidate_policy_id} ticket mutates active policy.")
        if ticket.creates_buy_request:
            blockers.append(f"{ticket.candidate_policy_id} ticket creates a buy request.")
        if ticket.executes_trade:
            blockers.append(f"{ticket.candidate_policy_id} ticket executes a trade.")

    safety_flags = {
        "active_policy_mutated": False,
        "automatic_policy_change_forbidden": True,
        "automatic_approval_forbidden": True,
        "manual_policy_approval_required": True,
        "broker_execution_forbidden": True,
        "creates_buy_request": False,
        "no_trades_executed": True,
    }

    if safety_flags["active_policy_mutated"]:
        blockers.append("audit mutates active policy.")
    if not safety_flags["automatic_policy_change_forbidden"]:
        blockers.append("automatic policy changes are not forbidden.")
    if not safety_flags["automatic_approval_forbidden"]:
        blockers.append("automatic approvals are not forbidden.")
    if not safety_flags["manual_policy_approval_required"]:
        blockers.append("manual policy approval is not required.")
    if not safety_flags["broker_execution_forbidden"]:
        blockers.append("broker execution is not forbidden.")
    if safety_flags["creates_buy_request"]:
        blockers.append("audit creates a buy request.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("audit executed a trade.")

    return PolicyIntelligenceBoundaryResult(
        status=STATUS_READY if not blockers else STATUS_BLOCKED,
        recommended_next_stage="v6.2_private_portfolio_snapshot_v2",
        candidate_policy_count=len(candidate_policies),
        recommended_policy_id=recommended_policy.policy_id,
        candidate_policies=candidate_policies,
        policy_change_tickets=tickets,
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        policy_intelligence_enabled=True,
        flexible_bands_required=True,
        broad_etf_universe_required=True,
        weekly_crypto_buy_allowed_if_within_risk_bands=True,
        **safety_flags,
    )
