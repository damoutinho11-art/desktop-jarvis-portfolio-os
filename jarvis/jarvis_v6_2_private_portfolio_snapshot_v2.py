"""J.A.R.V.I.S. v6.2 private portfolio snapshot v2.

This stage defines the private portfolio state contract required before
J.A.R.V.I.S. can size weekly/day-by-day manual buy recommendations.

Report-only safety boundary:
- local private snapshot only
- no broker/API connection
- no policy activation
- no buy request creation
- no trades
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


STATUS_READY = "JARVIS_V6_2_PRIVATE_PORTFOLIO_SNAPSHOT_V2_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V6_2_PRIVATE_PORTFOLIO_SNAPSHOT_V2_BLOCKED_SAFE"

NEXT_STAGE = "v6.3_universal_asset_candidate_registry"

ACCOUNT_DAILY_BANK = "daily_bank"
ACCOUNT_EMERGENCY_FUND = "emergency_fund"
ACCOUNT_INVESTMENT_BROKERAGE = "investment_brokerage"
ACCOUNT_CRYPTO_EXCHANGE = "crypto_exchange"
ACCOUNT_CASH_BUFFER = "cash_buffer"

CASH_EMERGENCY_PROTECTED = "emergency_protected_cash"
CASH_PENDING_BILLS = "pending_bills_cash"
CASH_WEEKLY_CONTRIBUTION = "weekly_contribution_cash"
CASH_INVESTABLE_EXTRA = "investable_extra_cash"

ASSET_EQUITY_ETF = "equity_etf"
ASSET_CRYPTO = "crypto"
ASSET_CASH = "cash"

SLEEVE_EQUITY_CORE = "equity_core"
SLEEVE_EQUITY_SATELLITE = "equity_satellite"
SLEEVE_CRYPTO_CORE_BTC = "crypto_core_btc"
SLEEVE_CRYPTO_SPECULATIVE = "crypto_speculative"
SLEEVE_CASH_DEFENSIVE = "cash_defensive"


@dataclass(frozen=True)
class AccountRole:
    account_id: str
    platform: str
    role: str
    currency: str
    read_only: bool
    execution_enabled: bool
    private_data_local_only: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "account_id": self.account_id,
            "platform": self.platform,
            "role": self.role,
            "currency": self.currency,
            "read_only": self.read_only,
            "execution_enabled": self.execution_enabled,
            "private_data_local_only": self.private_data_local_only,
        }


@dataclass(frozen=True)
class CashBucket:
    bucket_id: str
    account_id: str
    amount_eur: float
    protected: bool
    investable: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "bucket_id": self.bucket_id,
            "account_id": self.account_id,
            "amount_eur": self.amount_eur,
            "protected": self.protected,
            "investable": self.investable,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class Holding:
    asset_id: str
    display_name: str
    asset_class: str
    sleeve_id: str
    account_id: str
    platform: str
    currency: str
    quantity: float
    market_value_eur: float
    manually_entered: bool
    source_fresh: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "display_name": self.display_name,
            "asset_class": self.asset_class,
            "sleeve_id": self.sleeve_id,
            "account_id": self.account_id,
            "platform": self.platform,
            "currency": self.currency,
            "quantity": self.quantity,
            "market_value_eur": self.market_value_eur,
            "manually_entered": self.manually_entered,
            "source_fresh": self.source_fresh,
        }


@dataclass(frozen=True)
class PrivatePortfolioSnapshotV2:
    snapshot_id: str
    as_of_date: str
    base_currency: str
    snapshot_age_hours: float
    max_allowed_snapshot_age_hours: float
    accounts: tuple[AccountRole, ...]
    cash_buckets: tuple[CashBucket, ...]
    holdings: tuple[Holding, ...]
    operator_confirmed: bool
    private_data_local_only: bool
    broker_api_connected: bool
    broker_execution_enabled: bool
    automatic_import_enabled: bool

    def total_cash_eur(self) -> float:
        return round(sum(bucket.amount_eur for bucket in self.cash_buckets), 2)

    def protected_cash_eur(self) -> float:
        return round(
            sum(bucket.amount_eur for bucket in self.cash_buckets if bucket.protected),
            2,
        )

    def investable_cash_eur(self) -> float:
        return round(
            sum(bucket.amount_eur for bucket in self.cash_buckets if bucket.investable),
            2,
        )

    def holdings_value_eur(self) -> float:
        return round(sum(holding.market_value_eur for holding in self.holdings), 2)

    def total_portfolio_value_eur(self) -> float:
        return round(self.total_cash_eur() + self.holdings_value_eur(), 2)

    def is_fresh(self) -> bool:
        return self.snapshot_age_hours <= self.max_allowed_snapshot_age_hours

    def account_roles(self) -> set[str]:
        return {account.role for account in self.accounts}

    def sleeve_values_eur(self) -> dict[str, float]:
        values: dict[str, float] = {}
        for holding in self.holdings:
            values[holding.sleeve_id] = round(
                values.get(holding.sleeve_id, 0.0) + holding.market_value_eur,
                2,
            )
        cash_defensive = sum(
            bucket.amount_eur
            for bucket in self.cash_buckets
            if bucket.bucket_id in {CASH_EMERGENCY_PROTECTED, CASH_PENDING_BILLS}
        )
        values[SLEEVE_CASH_DEFENSIVE] = round(
            values.get(SLEEVE_CASH_DEFENSIVE, 0.0) + cash_defensive,
            2,
        )
        return values

    def sleeve_weights_pct(self) -> dict[str, float]:
        total = self.total_portfolio_value_eur()
        if total <= 0:
            return {}
        return {
            sleeve: round(value / total * 100.0, 4)
            for sleeve, value in self.sleeve_values_eur().items()
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "as_of_date": self.as_of_date,
            "base_currency": self.base_currency,
            "snapshot_age_hours": self.snapshot_age_hours,
            "max_allowed_snapshot_age_hours": self.max_allowed_snapshot_age_hours,
            "accounts": [account.to_dict() for account in self.accounts],
            "cash_buckets": [bucket.to_dict() for bucket in self.cash_buckets],
            "holdings": [holding.to_dict() for holding in self.holdings],
            "operator_confirmed": self.operator_confirmed,
            "private_data_local_only": self.private_data_local_only,
            "broker_api_connected": self.broker_api_connected,
            "broker_execution_enabled": self.broker_execution_enabled,
            "automatic_import_enabled": self.automatic_import_enabled,
            "total_cash_eur": self.total_cash_eur(),
            "protected_cash_eur": self.protected_cash_eur(),
            "investable_cash_eur": self.investable_cash_eur(),
            "holdings_value_eur": self.holdings_value_eur(),
            "total_portfolio_value_eur": self.total_portfolio_value_eur(),
            "sleeve_values_eur": self.sleeve_values_eur(),
            "sleeve_weights_pct": self.sleeve_weights_pct(),
            "is_fresh": self.is_fresh(),
        }


@dataclass(frozen=True)
class SnapshotValidationIssue:
    issue_id: str
    severity: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return {
            "issue_id": self.issue_id,
            "severity": self.severity,
            "message": self.message,
        }


@dataclass(frozen=True)
class PrivatePortfolioSnapshotV2AuditResult:
    status: str
    recommended_next_stage: str
    snapshot: PrivatePortfolioSnapshotV2
    issues: tuple[SnapshotValidationIssue, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    required_account_roles: tuple[str, ...]
    account_roles_present: tuple[str, ...]
    investable_cash_eur: float
    protected_cash_eur: float
    holdings_value_eur: float
    total_portfolio_value_eur: float
    sleeve_weights_pct: dict[str, float]
    private_snapshot_v2_ready: bool
    local_private_data_only: bool
    operator_confirmation_required: bool
    automatic_import_forbidden_at_this_stage: bool
    broker_api_forbidden: bool
    broker_execution_forbidden: bool
    active_policy_mutated: bool
    creates_buy_request: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recommended_next_stage": self.recommended_next_stage,
            "snapshot": self.snapshot.to_dict(),
            "issues": [issue.to_dict() for issue in self.issues],
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "required_account_roles": list(self.required_account_roles),
            "account_roles_present": list(self.account_roles_present),
            "investable_cash_eur": self.investable_cash_eur,
            "protected_cash_eur": self.protected_cash_eur,
            "holdings_value_eur": self.holdings_value_eur,
            "total_portfolio_value_eur": self.total_portfolio_value_eur,
            "sleeve_weights_pct": dict(self.sleeve_weights_pct),
            "private_snapshot_v2_ready": self.private_snapshot_v2_ready,
            "local_private_data_only": self.local_private_data_only,
            "operator_confirmation_required": self.operator_confirmation_required,
            "automatic_import_forbidden_at_this_stage": (
                self.automatic_import_forbidden_at_this_stage
            ),
            "broker_api_forbidden": self.broker_api_forbidden,
            "broker_execution_forbidden": self.broker_execution_forbidden,
            "active_policy_mutated": self.active_policy_mutated,
            "creates_buy_request": self.creates_buy_request,
            "no_trades_executed": self.no_trades_executed,
        }


def build_example_private_portfolio_snapshot_v2() -> PrivatePortfolioSnapshotV2:
    return PrivatePortfolioSnapshotV2(
        snapshot_id="example_private_snapshot_v2_manual_local",
        as_of_date="2026-06-15",
        base_currency="EUR",
        snapshot_age_hours=6.0,
        max_allowed_snapshot_age_hours=72.0,
        accounts=(
            AccountRole(
                account_id="lhv_daily_bank",
                platform="LHV",
                role=ACCOUNT_DAILY_BANK,
                currency="EUR",
                read_only=True,
                execution_enabled=False,
                private_data_local_only=True,
            ),
            AccountRole(
                account_id="emergency_cash_buffer",
                platform="Manual",
                role=ACCOUNT_EMERGENCY_FUND,
                currency="EUR",
                read_only=True,
                execution_enabled=False,
                private_data_local_only=True,
            ),
            AccountRole(
                account_id="lightyear_brokerage",
                platform="Lightyear",
                role=ACCOUNT_INVESTMENT_BROKERAGE,
                currency="EUR",
                read_only=True,
                execution_enabled=False,
                private_data_local_only=True,
            ),
            AccountRole(
                account_id="crypto_manual_wallet_or_exchange",
                platform="ManualCrypto",
                role=ACCOUNT_CRYPTO_EXCHANGE,
                currency="EUR",
                read_only=True,
                execution_enabled=False,
                private_data_local_only=True,
            ),
            AccountRole(
                account_id="weekly_cash_buffer",
                platform="Manual",
                role=ACCOUNT_CASH_BUFFER,
                currency="EUR",
                read_only=True,
                execution_enabled=False,
                private_data_local_only=True,
            ),
        ),
        cash_buckets=(
            CashBucket(
                bucket_id=CASH_EMERGENCY_PROTECTED,
                account_id="emergency_cash_buffer",
                amount_eur=5000.0,
                protected=True,
                investable=False,
                reason="Emergency fund protected from investment recommendations.",
            ),
            CashBucket(
                bucket_id=CASH_PENDING_BILLS,
                account_id="lhv_daily_bank",
                amount_eur=900.0,
                protected=True,
                investable=False,
                reason="Pending monthly expenses and relocation/life buffer.",
            ),
            CashBucket(
                bucket_id=CASH_WEEKLY_CONTRIBUTION,
                account_id="weekly_cash_buffer",
                amount_eur=250.0,
                protected=False,
                investable=True,
                reason="Planned weekly contribution available for manual investing.",
            ),
            CashBucket(
                bucket_id=CASH_INVESTABLE_EXTRA,
                account_id="weekly_cash_buffer",
                amount_eur=100.0,
                protected=False,
                investable=True,
                reason="Extra discretionary investable cash after protections.",
            ),
        ),
        holdings=(
            Holding(
                asset_id="global_all_world_etf_placeholder",
                display_name="Global all-world ETF placeholder",
                asset_class=ASSET_EQUITY_ETF,
                sleeve_id=SLEEVE_EQUITY_CORE,
                account_id="lightyear_brokerage",
                platform="Lightyear",
                currency="EUR",
                quantity=10.0,
                market_value_eur=1000.0,
                manually_entered=True,
                source_fresh=True,
            ),
            Holding(
                asset_id="btc",
                display_name="Bitcoin",
                asset_class=ASSET_CRYPTO,
                sleeve_id=SLEEVE_CRYPTO_CORE_BTC,
                account_id="crypto_manual_wallet_or_exchange",
                platform="ManualCrypto",
                currency="EUR",
                quantity=0.01,
                market_value_eur=600.0,
                manually_entered=True,
                source_fresh=True,
            ),
            Holding(
                asset_id="hype",
                display_name="HYPE",
                asset_class=ASSET_CRYPTO,
                sleeve_id=SLEEVE_CRYPTO_SPECULATIVE,
                account_id="crypto_manual_wallet_or_exchange",
                platform="ManualCrypto",
                currency="EUR",
                quantity=20.0,
                market_value_eur=200.0,
                manually_entered=True,
                source_fresh=True,
            ),
            Holding(
                asset_id="tao",
                display_name="TAO",
                asset_class=ASSET_CRYPTO,
                sleeve_id=SLEEVE_CRYPTO_SPECULATIVE,
                account_id="crypto_manual_wallet_or_exchange",
                platform="ManualCrypto",
                currency="EUR",
                quantity=1.0,
                market_value_eur=200.0,
                manually_entered=True,
                source_fresh=True,
            ),
        ),
        operator_confirmed=True,
        private_data_local_only=True,
        broker_api_connected=False,
        broker_execution_enabled=False,
        automatic_import_enabled=False,
    )


def validate_private_portfolio_snapshot_v2(
    snapshot: PrivatePortfolioSnapshotV2,
) -> tuple[SnapshotValidationIssue, ...]:
    issues: list[SnapshotValidationIssue] = []

    required_roles = {
        ACCOUNT_DAILY_BANK,
        ACCOUNT_EMERGENCY_FUND,
        ACCOUNT_INVESTMENT_BROKERAGE,
        ACCOUNT_CRYPTO_EXCHANGE,
        ACCOUNT_CASH_BUFFER,
    }
    missing_roles = required_roles - snapshot.account_roles()
    for role in sorted(missing_roles):
        issues.append(
            SnapshotValidationIssue(
                issue_id=f"missing_account_role_{role}",
                severity="BLOCKER",
                message=f"Required account role missing: {role}",
            )
        )

    if snapshot.base_currency != "EUR":
        issues.append(
            SnapshotValidationIssue(
                issue_id="base_currency_not_eur",
                severity="BLOCKER",
                message="v6.2 expects EUR as the private snapshot base currency.",
            )
        )

    if not snapshot.operator_confirmed:
        issues.append(
            SnapshotValidationIssue(
                issue_id="operator_confirmation_missing",
                severity="BLOCKER",
                message="Private snapshot must be manually confirmed by the operator.",
            )
        )

    if not snapshot.private_data_local_only:
        issues.append(
            SnapshotValidationIssue(
                issue_id="private_data_not_local_only",
                severity="BLOCKER",
                message="Private snapshot data must remain local-only at this stage.",
            )
        )

    if snapshot.automatic_import_enabled:
        issues.append(
            SnapshotValidationIssue(
                issue_id="automatic_import_enabled",
                severity="BLOCKER",
                message="Automatic private imports are forbidden in v6.2.",
            )
        )

    if snapshot.broker_api_connected:
        issues.append(
            SnapshotValidationIssue(
                issue_id="broker_api_connected",
                severity="BLOCKER",
                message="Broker/API connections are forbidden in v6.2.",
            )
        )

    if snapshot.broker_execution_enabled:
        issues.append(
            SnapshotValidationIssue(
                issue_id="broker_execution_enabled",
                severity="BLOCKER",
                message="Broker execution is forbidden.",
            )
        )

    if not snapshot.is_fresh():
        issues.append(
            SnapshotValidationIssue(
                issue_id="snapshot_stale",
                severity="BLOCKER",
                message="Private snapshot is older than the allowed freshness window.",
            )
        )

    for account in snapshot.accounts:
        if account.execution_enabled:
            issues.append(
                SnapshotValidationIssue(
                    issue_id=f"account_execution_enabled_{account.account_id}",
                    severity="BLOCKER",
                    message=f"Account has execution enabled: {account.account_id}",
                )
            )
        if not account.read_only:
            issues.append(
                SnapshotValidationIssue(
                    issue_id=f"account_not_read_only_{account.account_id}",
                    severity="BLOCKER",
                    message=f"Account is not read-only: {account.account_id}",
                )
            )
        if not account.private_data_local_only:
            issues.append(
                SnapshotValidationIssue(
                    issue_id=f"account_private_data_not_local_{account.account_id}",
                    severity="BLOCKER",
                    message=f"Account is not local-private-only: {account.account_id}",
                )
            )

    if any(bucket.amount_eur < 0 for bucket in snapshot.cash_buckets):
        issues.append(
            SnapshotValidationIssue(
                issue_id="negative_cash_bucket",
                severity="BLOCKER",
                message="Cash buckets cannot be negative.",
            )
        )

    for bucket in snapshot.cash_buckets:
        if bucket.protected and bucket.investable:
            issues.append(
                SnapshotValidationIssue(
                    issue_id=f"protected_cash_marked_investable_{bucket.bucket_id}",
                    severity="BLOCKER",
                    message=f"Protected cash cannot be investable: {bucket.bucket_id}",
                )
            )

    if snapshot.protected_cash_eur() <= 0:
        issues.append(
            SnapshotValidationIssue(
                issue_id="protected_cash_missing",
                severity="BLOCKER",
                message="Snapshot must identify protected cash before recommendations.",
            )
        )

    if snapshot.investable_cash_eur() <= 0:
        issues.append(
            SnapshotValidationIssue(
                issue_id="investable_cash_missing",
                severity="WARNING",
                message="No investable cash is available for this snapshot.",
            )
        )

    account_ids = {account.account_id for account in snapshot.accounts}
    for holding in snapshot.holdings:
        if holding.account_id not in account_ids:
            issues.append(
                SnapshotValidationIssue(
                    issue_id=f"holding_account_missing_{holding.asset_id}",
                    severity="BLOCKER",
                    message=f"Holding references unknown account: {holding.asset_id}",
                )
            )
        if holding.market_value_eur < 0:
            issues.append(
                SnapshotValidationIssue(
                    issue_id=f"negative_holding_value_{holding.asset_id}",
                    severity="BLOCKER",
                    message=f"Holding market value cannot be negative: {holding.asset_id}",
                )
            )
        if not holding.manually_entered:
            issues.append(
                SnapshotValidationIssue(
                    issue_id=f"holding_not_manual_{holding.asset_id}",
                    severity="BLOCKER",
                    message=f"Holding must be manually entered/local at v6.2: {holding.asset_id}",
                )
            )
        if not holding.source_fresh:
            issues.append(
                SnapshotValidationIssue(
                    issue_id=f"holding_source_stale_{holding.asset_id}",
                    severity="BLOCKER",
                    message=f"Holding source is stale: {holding.asset_id}",
                )
            )

    return tuple(issues)


def audit_v6_2_private_portfolio_snapshot_v2(
    snapshot: PrivatePortfolioSnapshotV2 | None = None,
) -> PrivatePortfolioSnapshotV2AuditResult:
    effective_snapshot = snapshot or build_example_private_portfolio_snapshot_v2()
    issues = validate_private_portfolio_snapshot_v2(effective_snapshot)

    blockers = tuple(issue.message for issue in issues if issue.severity == "BLOCKER")
    warnings = tuple(
        dict.fromkeys(
            [issue.message for issue in issues if issue.severity == "WARNING"]
            + [
                "v6.2 validates private portfolio state only; it does not generate buy tickets.",
                "Exact buy recommendations require v6.3+ asset registry and quality scoring.",
                "Private data remains local/operator-owned.",
            ]
        )
    )

    required_roles = (
        ACCOUNT_DAILY_BANK,
        ACCOUNT_EMERGENCY_FUND,
        ACCOUNT_INVESTMENT_BROKERAGE,
        ACCOUNT_CRYPTO_EXCHANGE,
        ACCOUNT_CASH_BUFFER,
    )

    safety_flags = {
        "local_private_data_only": effective_snapshot.private_data_local_only,
        "operator_confirmation_required": True,
        "automatic_import_forbidden_at_this_stage": True,
        "broker_api_forbidden": True,
        "broker_execution_forbidden": True,
        "active_policy_mutated": False,
        "creates_buy_request": False,
        "no_trades_executed": True,
    }

    if not safety_flags["local_private_data_only"]:
        blockers = blockers + ("Private snapshot is not local-only.",)
    if not safety_flags["broker_api_forbidden"]:
        blockers = blockers + ("Broker/API access is not forbidden.",)
    if not safety_flags["broker_execution_forbidden"]:
        blockers = blockers + ("Broker execution is not forbidden.",)
    if safety_flags["active_policy_mutated"]:
        blockers = blockers + ("v6.2 must not mutate active policy.",)
    if safety_flags["creates_buy_request"]:
        blockers = blockers + ("v6.2 must not create buy requests.",)
    if not safety_flags["no_trades_executed"]:
        blockers = blockers + ("v6.2 must not execute trades.",)

    return PrivatePortfolioSnapshotV2AuditResult(
        status=STATUS_READY if not blockers else STATUS_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        snapshot=effective_snapshot,
        issues=issues,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=warnings,
        required_account_roles=required_roles,
        account_roles_present=tuple(sorted(effective_snapshot.account_roles())),
        investable_cash_eur=effective_snapshot.investable_cash_eur(),
        protected_cash_eur=effective_snapshot.protected_cash_eur(),
        holdings_value_eur=effective_snapshot.holdings_value_eur(),
        total_portfolio_value_eur=effective_snapshot.total_portfolio_value_eur(),
        sleeve_weights_pct=effective_snapshot.sleeve_weights_pct(),
        private_snapshot_v2_ready=not blockers,
        **safety_flags,
    )
