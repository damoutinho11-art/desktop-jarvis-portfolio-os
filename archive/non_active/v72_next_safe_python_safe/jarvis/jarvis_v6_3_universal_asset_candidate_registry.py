"""J.A.R.V.I.S. v6.3 universal asset candidate registry.

This stage defines the broad investable candidate universe J.A.R.V.I.S. may
evaluate later. It does not score, approve, recommend, create buy tickets, or
execute anything.

Report-only safety boundary:
- candidates only
- no approved policy assets
- no weekly buy candidates
- no broker/API execution
- no buy request creation
- no trades
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


STATUS_READY = "JARVIS_V6_3_UNIVERSAL_ASSET_CANDIDATE_REGISTRY_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_3_UNIVERSAL_ASSET_CANDIDATE_REGISTRY_BLOCKED_SAFE"

NEXT_STAGE = "v6.4_asset_quality_scoring_gate"

ASSET_TYPE_ETF = "ETF"
ASSET_TYPE_FUND = "FUND"
ASSET_TYPE_STOCK = "STOCK"
ASSET_TYPE_CRYPTO = "CRYPTO"
ASSET_TYPE_CASH_LIKE = "CASH_LIKE"
ASSET_TYPE_BOND_ETF = "BOND_ETF"
ASSET_TYPE_COMMODITY_ETF = "COMMODITY_ETF"

STATE_DISCOVERED = "DISCOVERED"
STATE_IDENTITY_READY = "IDENTITY_READY"
STATE_DATA_READY = "DATA_READY"
STATE_QUALITY_READY = "QUALITY_READY"
STATE_POLICY_CANDIDATE = "POLICY_CANDIDATE"
STATE_APPROVED_POLICY_ASSET = "APPROVED_POLICY_ASSET"
STATE_WEEKLY_BUY_CANDIDATE = "WEEKLY_BUY_CANDIDATE"
STATE_BLOCKED = "BLOCKED"
STATE_AVOID = "AVOID"

SLEEVE_EQUITY_CORE = "equity_core"
SLEEVE_EQUITY_SATELLITE = "equity_satellite"
SLEEVE_CRYPTO_CORE_BTC = "crypto_core_btc"
SLEEVE_CRYPTO_SPECULATIVE = "crypto_speculative"
SLEEVE_CASH_DEFENSIVE = "cash_defensive"
SLEEVE_BOND_DEFENSIVE = "bond_defensive"
SLEEVE_COMMODITY_DEFENSIVE = "commodity_defensive"


@dataclass(frozen=True)
class DataRequirement:
    requirement_id: str
    description: str
    required: bool
    satisfied: bool
    source_kind: str
    max_age_days: int | None
    issue_if_missing: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "requirement_id": self.requirement_id,
            "description": self.description,
            "required": self.required,
            "satisfied": self.satisfied,
            "source_kind": self.source_kind,
            "max_age_days": self.max_age_days,
            "issue_if_missing": self.issue_if_missing,
        }


@dataclass(frozen=True)
class EligibilityCheck:
    check_id: str
    passed: bool
    severity: str
    message: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "check_id": self.check_id,
            "passed": self.passed,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(frozen=True)
class AssetCandidate:
    candidate_id: str
    display_name: str
    asset_type: str
    candidate_state: str
    sleeve_ids: tuple[str, ...]
    currency: str
    region_or_network: str
    platform_options: tuple[str, ...]
    data_requirements: tuple[DataRequirement, ...]
    eligibility_checks: tuple[EligibilityCheck, ...]
    manually_reviewed: bool
    operator_approved: bool
    policy_asset_approved: bool
    weekly_buy_candidate: bool
    creates_buy_request: bool
    executes_trade: bool
    notes: tuple[str, ...]

    def required_data_ready(self) -> bool:
        return all(
            requirement.satisfied
            for requirement in self.data_requirements
            if requirement.required
        )

    def blocker_free(self) -> bool:
        return all(
            check.passed or check.severity != "BLOCKER"
            for check in self.eligibility_checks
        )

    def is_registry_candidate_only(self) -> bool:
        return (
            not self.operator_approved
            and not self.policy_asset_approved
            and not self.weekly_buy_candidate
            and not self.creates_buy_request
            and not self.executes_trade
        )

    def can_enter_quality_scoring_next(self) -> bool:
        return (
            self.candidate_state in {STATE_DATA_READY, STATE_QUALITY_READY, STATE_POLICY_CANDIDATE}
            and self.required_data_ready()
            and self.blocker_free()
            and self.is_registry_candidate_only()
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "display_name": self.display_name,
            "asset_type": self.asset_type,
            "candidate_state": self.candidate_state,
            "sleeve_ids": list(self.sleeve_ids),
            "currency": self.currency,
            "region_or_network": self.region_or_network,
            "platform_options": list(self.platform_options),
            "data_requirements": [item.to_dict() for item in self.data_requirements],
            "eligibility_checks": [item.to_dict() for item in self.eligibility_checks],
            "manually_reviewed": self.manually_reviewed,
            "operator_approved": self.operator_approved,
            "policy_asset_approved": self.policy_asset_approved,
            "weekly_buy_candidate": self.weekly_buy_candidate,
            "creates_buy_request": self.creates_buy_request,
            "executes_trade": self.executes_trade,
            "notes": list(self.notes),
            "required_data_ready": self.required_data_ready(),
            "blocker_free": self.blocker_free(),
            "can_enter_quality_scoring_next": self.can_enter_quality_scoring_next(),
        }


@dataclass(frozen=True)
class UniversalAssetCandidateRegistryResult:
    status: str
    recommended_next_stage: str
    candidate_count: int
    asset_types_covered: tuple[str, ...]
    candidate_states_present: tuple[str, ...]
    quality_scoring_ready_count: int
    approved_policy_asset_count: int
    weekly_buy_candidate_count: int
    candidates: tuple[AssetCandidate, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    broad_universe_registry_ready: bool
    candidates_only: bool
    exact_asset_scoring_deferred: bool
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
            "candidate_count": self.candidate_count,
            "asset_types_covered": list(self.asset_types_covered),
            "candidate_states_present": list(self.candidate_states_present),
            "quality_scoring_ready_count": self.quality_scoring_ready_count,
            "approved_policy_asset_count": self.approved_policy_asset_count,
            "weekly_buy_candidate_count": self.weekly_buy_candidate_count,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "broad_universe_registry_ready": self.broad_universe_registry_ready,
            "candidates_only": self.candidates_only,
            "exact_asset_scoring_deferred": self.exact_asset_scoring_deferred,
            "policy_approval_deferred": self.policy_approval_deferred,
            "weekly_buy_ticket_deferred": self.weekly_buy_ticket_deferred,
            "active_policy_mutated": self.active_policy_mutated,
            "automatic_approval_forbidden": self.automatic_approval_forbidden,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "creates_buy_request": self.creates_buy_request,
            "no_trades_executed": self.no_trades_executed,
        }


def _market_data_requirements(asset_type: str) -> tuple[DataRequirement, ...]:
    common = (
        DataRequirement(
            requirement_id="identity",
            description="Stable asset identity: ticker/ISIN/coin id or equivalent.",
            required=True,
            satisfied=True,
            source_kind="identity",
            max_age_days=None,
            issue_if_missing="Asset identity is missing or ambiguous.",
        ),
        DataRequirement(
            requirement_id="price_history",
            description="Sufficient price history for risk and trend analysis.",
            required=True,
            satisfied=True,
            source_kind="market_data",
            max_age_days=7,
            issue_if_missing="Fresh price history is missing.",
        ),
        DataRequirement(
            requirement_id="platform_availability",
            description="At least one plausible platform route is known.",
            required=True,
            satisfied=True,
            source_kind="operator_or_public",
            max_age_days=30,
            issue_if_missing="Platform availability is unknown.",
        ),
    )

    if asset_type in {ASSET_TYPE_ETF, ASSET_TYPE_FUND, ASSET_TYPE_BOND_ETF, ASSET_TYPE_COMMODITY_ETF}:
        return common + (
            DataRequirement(
                requirement_id="fees_and_structure",
                description="Fees, domicile/structure, and fund mechanics available.",
                required=True,
                satisfied=True,
                source_kind="fund_metadata",
                max_age_days=90,
                issue_if_missing="Fund fees or structure are missing.",
            ),
            DataRequirement(
                requirement_id="holdings_or_exposure",
                description="Holdings, index, or exposure definition available.",
                required=True,
                satisfied=True,
                source_kind="issuer_or_public",
                max_age_days=90,
                issue_if_missing="Fund holdings/exposure data is missing.",
            ),
        )

    if asset_type == ASSET_TYPE_STOCK:
        return common + (
            DataRequirement(
                requirement_id="fundamental_snapshot",
                description="Basic fundamentals and company identity available.",
                required=True,
                satisfied=True,
                source_kind="public_equity_data",
                max_age_days=90,
                issue_if_missing="Fundamental snapshot is missing.",
            ),
        )

    if asset_type == ASSET_TYPE_CRYPTO:
        return common + (
            DataRequirement(
                requirement_id="liquidity_and_exchange_identity",
                description="Coin identity, liquidity route, and custody/platform route available.",
                required=True,
                satisfied=True,
                source_kind="crypto_public_data",
                max_age_days=30,
                issue_if_missing="Crypto identity/liquidity/custody route is missing.",
            ),
        )

    if asset_type == ASSET_TYPE_CASH_LIKE:
        return common + (
            DataRequirement(
                requirement_id="yield_and_safety_terms",
                description="Yield, currency, access, and capital-risk terms available.",
                required=True,
                satisfied=True,
                source_kind="cash_product_metadata",
                max_age_days=30,
                issue_if_missing="Cash-like product terms are missing.",
            ),
        )

    return common


def _passing_checks() -> tuple[EligibilityCheck, ...]:
    return (
        EligibilityCheck(
            check_id="not_approved_yet",
            passed=True,
            severity="INFO",
            message="Candidate is not approved; quality scoring is deferred to v6.4.",
        ),
        EligibilityCheck(
            check_id="no_execution_route",
            passed=True,
            severity="INFO",
            message="Candidate has no broker execution route in J.A.R.V.I.S.",
        ),
    )


def _blocked_checks(reason: str) -> tuple[EligibilityCheck, ...]:
    return (
        EligibilityCheck(
            check_id="blocked_until_source_quality",
            passed=False,
            severity="BLOCKER",
            message=reason,
        ),
        EligibilityCheck(
            check_id="no_execution_route",
            passed=True,
            severity="INFO",
            message="Candidate has no broker execution route in J.A.R.V.I.S.",
        ),
    )


def build_example_universal_asset_candidates() -> tuple[AssetCandidate, ...]:
    return (
        AssetCandidate(
            candidate_id="global_all_world_etf_candidate",
            display_name="Global all-world ETF candidate",
            asset_type=ASSET_TYPE_ETF,
            candidate_state=STATE_POLICY_CANDIDATE,
            sleeve_ids=(SLEEVE_EQUITY_CORE,),
            currency="EUR",
            region_or_network="global",
            platform_options=("Lightyear", "LHV"),
            data_requirements=_market_data_requirements(ASSET_TYPE_ETF),
            eligibility_checks=_passing_checks(),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("Core equity ETF candidate; exact ticker selection deferred.",),
        ),
        AssetCandidate(
            candidate_id="sp_500_etf_candidate",
            display_name="S&P 500 ETF candidate",
            asset_type=ASSET_TYPE_ETF,
            candidate_state=STATE_DATA_READY,
            sleeve_ids=(SLEEVE_EQUITY_CORE, SLEEVE_EQUITY_SATELLITE),
            currency="EUR",
            region_or_network="United States",
            platform_options=("Lightyear",),
            data_requirements=_market_data_requirements(ASSET_TYPE_ETF),
            eligibility_checks=_passing_checks(),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("US equity ETF candidate; overlap with global core must be scored later.",),
        ),
        AssetCandidate(
            candidate_id="quality_factor_etf_candidate",
            display_name="Quality factor ETF candidate",
            asset_type=ASSET_TYPE_ETF,
            candidate_state=STATE_DATA_READY,
            sleeve_ids=(SLEEVE_EQUITY_SATELLITE,),
            currency="EUR",
            region_or_network="global_or_developed",
            platform_options=("Lightyear",),
            data_requirements=_market_data_requirements(ASSET_TYPE_ETF),
            eligibility_checks=_passing_checks(),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("Satellite ETF candidate; factor exposure and overlap scored later.",),
        ),
        AssetCandidate(
            candidate_id="global_equity_fund_candidate",
            display_name="Global equity fund candidate",
            asset_type=ASSET_TYPE_FUND,
            candidate_state=STATE_DATA_READY,
            sleeve_ids=(SLEEVE_EQUITY_CORE, SLEEVE_EQUITY_SATELLITE),
            currency="EUR",
            region_or_network="global",
            platform_options=("LHV", "Lightyear", "Manual"),
            data_requirements=_market_data_requirements(ASSET_TYPE_FUND),
            eligibility_checks=_passing_checks(),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("Fund candidate; fees, structure, overlap, and platform fit scored later.",),
        ),
        AssetCandidate(
            candidate_id="single_stock_candidate_large_cap",
            display_name="Large-cap stock candidate",
            asset_type=ASSET_TYPE_STOCK,
            candidate_state=STATE_DATA_READY,
            sleeve_ids=(SLEEVE_EQUITY_SATELLITE,),
            currency="EUR",
            region_or_network="global_equity",
            platform_options=("Lightyear",),
            data_requirements=_market_data_requirements(ASSET_TYPE_STOCK),
            eligibility_checks=_passing_checks(),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("Single-stock candidate requires concentration and thesis scoring later.",),
        ),
        AssetCandidate(
            candidate_id="btc_candidate",
            display_name="Bitcoin candidate",
            asset_type=ASSET_TYPE_CRYPTO,
            candidate_state=STATE_POLICY_CANDIDATE,
            sleeve_ids=(SLEEVE_CRYPTO_CORE_BTC,),
            currency="EUR",
            region_or_network="Bitcoin",
            platform_options=("ManualCrypto", "Kraken"),
            data_requirements=_market_data_requirements(ASSET_TYPE_CRYPTO),
            eligibility_checks=_passing_checks(),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("Core crypto candidate; weekly buying permission handled by policy and risk state.",),
        ),
        AssetCandidate(
            candidate_id="hype_candidate",
            display_name="HYPE candidate",
            asset_type=ASSET_TYPE_CRYPTO,
            candidate_state=STATE_DATA_READY,
            sleeve_ids=(SLEEVE_CRYPTO_SPECULATIVE,),
            currency="EUR",
            region_or_network="Hyperliquid",
            platform_options=("ManualCrypto",),
            data_requirements=_market_data_requirements(ASSET_TYPE_CRYPTO),
            eligibility_checks=_passing_checks(),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("Speculative crypto candidate; must remain bounded and manually reviewed.",),
        ),
        AssetCandidate(
            candidate_id="tao_candidate",
            display_name="TAO candidate",
            asset_type=ASSET_TYPE_CRYPTO,
            candidate_state=STATE_DATA_READY,
            sleeve_ids=(SLEEVE_CRYPTO_SPECULATIVE,),
            currency="EUR",
            region_or_network="Bittensor",
            platform_options=("ManualCrypto",),
            data_requirements=_market_data_requirements(ASSET_TYPE_CRYPTO),
            eligibility_checks=_passing_checks(),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("Speculative crypto candidate; must remain bounded and manually reviewed.",),
        ),
        AssetCandidate(
            candidate_id="money_market_candidate",
            display_name="EUR money-market candidate",
            asset_type=ASSET_TYPE_CASH_LIKE,
            candidate_state=STATE_DATA_READY,
            sleeve_ids=(SLEEVE_CASH_DEFENSIVE,),
            currency="EUR",
            region_or_network="Europe",
            platform_options=("Lightyear", "LHV", "Manual"),
            data_requirements=_market_data_requirements(ASSET_TYPE_CASH_LIKE),
            eligibility_checks=_passing_checks(),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("Cash-like candidate; must not consume emergency protected cash.",),
        ),
        AssetCandidate(
            candidate_id="short_duration_bond_etf_candidate",
            display_name="Short-duration bond ETF candidate",
            asset_type=ASSET_TYPE_BOND_ETF,
            candidate_state=STATE_DISCOVERED,
            sleeve_ids=(SLEEVE_BOND_DEFENSIVE, SLEEVE_CASH_DEFENSIVE),
            currency="EUR",
            region_or_network="Europe_or_global",
            platform_options=("Lightyear",),
            data_requirements=_market_data_requirements(ASSET_TYPE_BOND_ETF),
            eligibility_checks=_passing_checks(),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("Defensive candidate; duration and currency risk scored later.",),
        ),
        AssetCandidate(
            candidate_id="gold_or_commodity_etf_candidate",
            display_name="Gold or broad commodity ETF candidate",
            asset_type=ASSET_TYPE_COMMODITY_ETF,
            candidate_state=STATE_DISCOVERED,
            sleeve_ids=(SLEEVE_COMMODITY_DEFENSIVE,),
            currency="EUR",
            region_or_network="global_commodity",
            platform_options=("Lightyear",),
            data_requirements=_market_data_requirements(ASSET_TYPE_COMMODITY_ETF),
            eligibility_checks=_passing_checks(),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("Optional defensive candidate; commodity role scored later.",),
        ),
        AssetCandidate(
            candidate_id="unverified_microcap_crypto_blocked",
            display_name="Unverified microcap crypto example",
            asset_type=ASSET_TYPE_CRYPTO,
            candidate_state=STATE_BLOCKED,
            sleeve_ids=(SLEEVE_CRYPTO_SPECULATIVE,),
            currency="EUR",
            region_or_network="unknown",
            platform_options=("unknown",),
            data_requirements=(
                DataRequirement(
                    requirement_id="identity",
                    description="Coin identity and verified source mapping.",
                    required=True,
                    satisfied=False,
                    source_kind="crypto_public_data",
                    max_age_days=30,
                    issue_if_missing="Crypto identity is not verified.",
                ),
            ),
            eligibility_checks=_blocked_checks(
                "Blocked: identity/source quality not sufficient for the candidate registry."
            ),
            manually_reviewed=False,
            operator_approved=False,
            policy_asset_approved=False,
            weekly_buy_candidate=False,
            creates_buy_request=False,
            executes_trade=False,
            notes=("Example blocked candidate to prove registry does not promote weak assets.",),
        ),
    )


def audit_v6_3_universal_asset_candidate_registry(
    candidates: tuple[AssetCandidate, ...] | None = None,
) -> UniversalAssetCandidateRegistryResult:
    effective_candidates = candidates or build_example_universal_asset_candidates()

    required_asset_types = {
        ASSET_TYPE_ETF,
        ASSET_TYPE_FUND,
        ASSET_TYPE_STOCK,
        ASSET_TYPE_CRYPTO,
        ASSET_TYPE_CASH_LIKE,
        ASSET_TYPE_BOND_ETF,
        ASSET_TYPE_COMMODITY_ETF,
    }

    asset_types = tuple(sorted({candidate.asset_type for candidate in effective_candidates}))
    states = tuple(sorted({candidate.candidate_state for candidate in effective_candidates}))

    blockers: list[str] = []
    warnings: list[str] = [
        "v6.3 defines broad candidate registry only; quality scoring is deferred to v6.4.",
        "No asset is approved by this registry.",
        "No asset becomes a weekly buy candidate in this stage.",
        "Exact live/current data scanning requires later source adapters and operator configuration.",
    ]

    missing_asset_types = required_asset_types - set(asset_types)
    for asset_type in sorted(missing_asset_types):
        blockers.append(f"Required asset type missing from registry coverage: {asset_type}")

    candidate_ids = [candidate.candidate_id for candidate in effective_candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        blockers.append("Candidate IDs must be unique.")

    for candidate in effective_candidates:
        if candidate.asset_type not in required_asset_types:
            blockers.append(f"{candidate.candidate_id}: unsupported asset type {candidate.asset_type}")
        if not candidate.sleeve_ids:
            blockers.append(f"{candidate.candidate_id}: no sleeve routing defined.")
        if not candidate.currency:
            blockers.append(f"{candidate.candidate_id}: currency missing.")
        if not candidate.platform_options:
            blockers.append(f"{candidate.candidate_id}: platform options missing.")
        if candidate.operator_approved:
            blockers.append(f"{candidate.candidate_id}: operator approval is forbidden in v6.3.")
        if candidate.policy_asset_approved:
            blockers.append(f"{candidate.candidate_id}: policy asset approval is forbidden in v6.3.")
        if candidate.weekly_buy_candidate:
            blockers.append(f"{candidate.candidate_id}: weekly buy candidacy is forbidden in v6.3.")
        if candidate.creates_buy_request:
            blockers.append(f"{candidate.candidate_id}: buy request creation is forbidden in v6.3.")
        if candidate.executes_trade:
            blockers.append(f"{candidate.candidate_id}: trade execution is forbidden in v6.3.")
        if candidate.candidate_state in {STATE_APPROVED_POLICY_ASSET, STATE_WEEKLY_BUY_CANDIDATE}:
            blockers.append(
                f"{candidate.candidate_id}: state {candidate.candidate_state} is not allowed in v6.3."
            )
        if candidate.candidate_state == STATE_BLOCKED and candidate.blocker_free():
            blockers.append(f"{candidate.candidate_id}: blocked candidate lacks a blocker check.")
        if candidate.candidate_state != STATE_BLOCKED and not candidate.required_data_ready():
            blockers.append(f"{candidate.candidate_id}: non-blocked candidate has missing required data.")

    quality_scoring_ready_count = sum(
        1 for candidate in effective_candidates if candidate.can_enter_quality_scoring_next()
    )
    approved_policy_asset_count = sum(
        1 for candidate in effective_candidates if candidate.policy_asset_approved
    )
    weekly_buy_candidate_count = sum(
        1 for candidate in effective_candidates if candidate.weekly_buy_candidate
    )

    safety_flags = {
        "broad_universe_registry_ready": not blockers,
        "candidates_only": True,
        "exact_asset_scoring_deferred": True,
        "policy_approval_deferred": True,
        "weekly_buy_ticket_deferred": True,
        "active_policy_mutated": False,
        "automatic_approval_forbidden": True,
        "broker_execution_forbidden": True,
        "creates_buy_request": False,
        "no_trades_executed": True,
    }

    if not safety_flags["candidates_only"]:
        blockers.append("v6.3 must remain candidate-only.")
    if not safety_flags["exact_asset_scoring_deferred"]:
        blockers.append("v6.3 must defer scoring to v6.4.")
    if not safety_flags["policy_approval_deferred"]:
        blockers.append("v6.3 must defer policy approval.")
    if not safety_flags["weekly_buy_ticket_deferred"]:
        blockers.append("v6.3 must defer weekly buy tickets.")
    if safety_flags["active_policy_mutated"]:
        blockers.append("v6.3 must not mutate active policy.")
    if not safety_flags["automatic_approval_forbidden"]:
        blockers.append("v6.3 must forbid automatic approval.")
    if not safety_flags["broker_execution_forbidden"]:
        blockers.append("v6.3 must forbid broker execution.")
    if safety_flags["creates_buy_request"]:
        blockers.append("v6.3 must not create buy requests.")
    if not safety_flags["no_trades_executed"]:
        blockers.append("v6.3 must not execute trades.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    return UniversalAssetCandidateRegistryResult(
        status=STATUS_READY if not unique_blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        candidate_count=len(effective_candidates),
        asset_types_covered=asset_types,
        candidate_states_present=states,
        quality_scoring_ready_count=quality_scoring_ready_count,
        approved_policy_asset_count=approved_policy_asset_count,
        weekly_buy_candidate_count=weekly_buy_candidate_count,
        candidates=effective_candidates,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **{**safety_flags, "broad_universe_registry_ready": not unique_blockers},
    )
