"""Read-only snapshot validation and recommendation blocking logic."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .portfolio_schema import (
    Account,
    Holding,
    PortfolioSnapshot,
    Recommendation,
    SnapshotValidationResult,
    ValidationWarning,
)


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if value == "true":
        return True
    if value == "false":
        return False
    try:
        return float(value) if "." in value else int(value)
    except ValueError:
        return value


def load_simple_yaml(path: str | Path) -> dict[str, Any]:
    """Parse the small YAML subset used by this kernel's config files."""
    lines: list[tuple[int, str]] = []
    for raw_line in Path(path).read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        lines.append((indent, raw_line.strip()))

    if not lines:
        return {}

    def parse_block(index: int, indent: int) -> tuple[Any, int]:
        is_list = lines[index][1].startswith("- ")
        if is_list:
            values: list[Any] = []
            while index < len(lines) and lines[index][0] == indent:
                text = lines[index][1]
                if not text.startswith("- "):
                    break
                values.append(_parse_scalar(text[2:]))
                index += 1
            return values, index

        values: dict[str, Any] = {}
        while index < len(lines) and lines[index][0] == indent:
            text = lines[index][1]
            if text.startswith("- "):
                break
            key, separator, raw_value = text.partition(":")
            if not separator:
                raise ValueError(f"Invalid YAML line: {text}")
            key = key.strip()
            raw_value = raw_value.strip()
            index += 1

            if raw_value:
                values[key] = _parse_scalar(raw_value)
            elif index < len(lines) and lines[index][0] > indent:
                values[key], index = parse_block(index, lines[index][0])
            else:
                values[key] = {}
        return values, index

    parsed, _ = parse_block(0, lines[0][0])
    if not isinstance(parsed, dict):
        raise ValueError("Top-level YAML document must be a mapping.")
    return parsed


def load_constitution(path: str | Path = "jarvis/jarvis_constitution.yaml") -> dict[str, Any]:
    return load_simple_yaml(path)


def load_account_roles(path: str | Path = "jarvis/account_roles.yaml") -> dict[str, Any]:
    return load_simple_yaml(path)["accounts"]


def _role_config(account: Account, account_roles: dict[str, Any]) -> dict[str, Any]:
    return account_roles.get(account.account_id, {})


def _effective_role(account: Account, account_roles: dict[str, Any]) -> str:
    return account.role or _role_config(account, account_roles).get("role", "unknown")


def _include_in_investable(account: Account, account_roles: dict[str, Any]) -> bool:
    if account.include_in_investable_by_default is not None:
        return account.include_in_investable_by_default
    return bool(_role_config(account, account_roles).get("include_in_investable_by_default", False))


def validate_snapshot(
    snapshot: PortfolioSnapshot,
    constitution: dict[str, Any] | None = None,
    account_roles: dict[str, Any] | None = None,
) -> SnapshotValidationResult:
    constitution = constitution or load_constitution()
    account_roles = account_roles or load_account_roles()
    approved_assets = set(constitution.get("approved_assets", []))
    account_by_id = {account.account_id: account for account in snapshot.accounts}
    warnings: list[ValidationWarning] = []
    totals = {
        "total_cash": 0.0,
        "protected_cash": float(snapshot.emergency_fund_amount),
        "investable_cash": 0.0,
        "legacy_holdings": 0.0,
        "unapproved_assets": 0.0,
        "investment_account_crypto": 0.0,
        "etf_engine": 0.0,
    }

    for account in snapshot.accounts:
        role = _effective_role(account, account_roles)
        if role == "unknown":
            warnings.append(
                ValidationWarning(
                    code="unknown_account",
                    message=f"Account {account.account_id} has no approved role.",
                    severity="error",
                    account_id=account.account_id,
                )
            )

    for holding in snapshot.holdings:
        account = account_by_id.get(holding.account_id)
        if account is None:
            warnings.append(
                ValidationWarning(
                    code="unknown_account",
                    message=f"Holding references unknown account {holding.account_id}.",
                    severity="error",
                    account_id=holding.account_id,
                    asset_symbol=holding.asset_symbol,
                )
            )
            totals["unapproved_assets"] += holding.amount
            continue

        role = _effective_role(account, account_roles)
        include = _include_in_investable(account, account_roles)
        if holding.asset_class == "cash":
            totals["total_cash"] += holding.amount
        if holding.asset_symbol not in approved_assets:
            if holding.classification == "legacy_existing":
                totals["legacy_holdings"] += holding.amount
                continue
            if holding.classification == "test_position":
                totals["unapproved_assets"] += holding.amount
                warnings.append(
                    ValidationWarning(
                        code="test_position",
                        message=f"Asset {holding.asset_symbol} is marked test_position and is not approved for new recommendations.",
                        severity="warning",
                        account_id=holding.account_id,
                        asset_symbol=holding.asset_symbol,
                    )
                )
                continue
            warnings.append(
                ValidationWarning(
                    code="candidate_unapproved",
                    message=f"Asset {holding.asset_symbol} is not approved; marked candidate_unapproved.",
                    severity="error",
                    account_id=holding.account_id,
                    asset_symbol=holding.asset_symbol,
                )
            )
            totals["unapproved_assets"] += holding.amount
            continue

        if role in {"protected_cash", "daily_spending", "spending_cash_rewards", "restricted_crypto_external"}:
            totals["protected_cash"] += holding.amount
        elif role == "legacy_cleanup":
            totals["legacy_holdings"] += holding.amount
        elif role == "investment_account_crypto":
            totals["investment_account_crypto"] += holding.amount
        elif role == "ETF_engine":
            totals["etf_engine"] += holding.amount
        elif include and holding.asset_class == "cash":
            totals["investable_cash"] += holding.amount
        elif not include:
            totals["protected_cash"] += holding.amount

    validation_passed = not any(warning.severity == "error" for warning in warnings)
    snapshot.validation_passed = validation_passed
    snapshot.classified_totals = totals
    return SnapshotValidationResult(snapshot, warnings, validation_passed)


def block_recommendation_until_validated(
    snapshot_result: SnapshotValidationResult,
    recommendation: Recommendation,
) -> Recommendation:
    if not snapshot_result.validation_passed:
        return Recommendation(
            action=recommendation.action,
            asset_symbol=recommendation.asset_symbol,
            amount=recommendation.amount,
            account_id=recommendation.account_id,
            manual_approval_required=True,
            status="blocked",
            block_reasons=("portfolio snapshot validation has not passed",),
        )
    return Recommendation(
        action=recommendation.action,
        asset_symbol=recommendation.asset_symbol,
        amount=recommendation.amount,
        account_id=recommendation.account_id,
        manual_approval_required=True,
        status="pending_manual_approval",
        block_reasons=(),
    )
