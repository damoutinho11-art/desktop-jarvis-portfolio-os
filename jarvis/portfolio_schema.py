"""Dataclasses for the J.A.R.V.I.S. read-only portfolio kernel."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Account:
    account_id: str
    name: str
    role: str | None = None
    include_in_investable_by_default: bool | None = None
    protected: bool = False


@dataclass(frozen=True)
class Holding:
    account_id: str
    asset_symbol: str
    amount: float
    asset_class: str
    classification: str | None = None


@dataclass
class PortfolioSnapshot:
    as_of: str
    accounts: list[Account]
    holdings: list[Holding]
    emergency_fund_amount: float = 0.0
    validation_passed: bool = False
    classified_totals: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class Recommendation:
    action: str
    asset_symbol: str
    amount: float
    account_id: str
    manual_approval_required: bool = True
    status: str = "pending_validation"
    block_reasons: tuple[str, ...] = ()


@dataclass(frozen=True)
class ValidationWarning:
    code: str
    message: str
    severity: str = "warning"
    account_id: str | None = None
    asset_symbol: str | None = None


@dataclass(frozen=True)
class SnapshotValidationResult:
    snapshot: PortfolioSnapshot
    warnings: list[ValidationWarning]
    validation_passed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "as_of": self.snapshot.as_of,
            "validation_passed": self.validation_passed,
            "classified_totals": self.snapshot.classified_totals,
            "warnings": [warning.__dict__ for warning in self.warnings],
        }

