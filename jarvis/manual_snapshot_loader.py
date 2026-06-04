"""Manual JSON snapshot intake for the read-only J.A.R.V.I.S. kernel."""

from __future__ import annotations

import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

from .portfolio_schema import Account, Holding, PortfolioSnapshot, ValidationWarning
from .portfolio_snapshot_engine import load_account_roles


class ManualSnapshotError(ValueError):
    """Raised when a manual snapshot cannot be loaded safely."""


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManualSnapshotError(f"{label} must be an object.")
    return value


def _require_non_empty_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManualSnapshotError(f"{label} exists and must be text.")
    return value.strip()


def _require_non_negative_number(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ManualSnapshotError(f"{label} must be a number.")
    if value < 0:
        raise ManualSnapshotError(f"{label} must be non-negative.")
    return float(value)


def _parse_snapshot_date(value: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ManualSnapshotError("snapshot_date must use YYYY-MM-DD format.") from exc


def load_manual_snapshot(
    path: str | Path,
    account_roles: dict[str, Any] | None = None,
    today: date | None = None,
) -> tuple[PortfolioSnapshot, list[ValidationWarning]]:
    """Load and validate a manually-entered portfolio snapshot JSON file."""
    account_roles = account_roles or load_account_roles()
    known_roles = {config.get("role") for config in account_roles.values()}
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "snapshot")

    snapshot_date_text = _require_non_empty_text(raw.get("snapshot_date"), "snapshot_date")
    snapshot_date = _parse_snapshot_date(snapshot_date_text)
    if raw.get("base_currency") != "EUR":
        raise ManualSnapshotError("base_currency must be EUR.")

    raw_accounts = raw.get("accounts")
    if not isinstance(raw_accounts, list):
        raise ManualSnapshotError("accounts must be a list.")

    accounts: list[Account] = []
    holdings: list[Holding] = []
    warnings: list[ValidationWarning] = []
    account_ids: set[str] = set()

    for index, raw_account_value in enumerate(raw_accounts):
        raw_account = _require_mapping(raw_account_value, f"accounts[{index}]")
        account_id = _require_non_empty_text(raw_account.get("account_id"), "account_id")
        platform = _require_non_empty_text(raw_account.get("platform"), "platform")
        role = _require_non_empty_text(raw_account.get("role"), "role")
        cash_eur = _require_non_negative_number(raw_account.get("cash_eur", 0.0), "cash_eur")

        if role not in known_roles:
            raise ManualSnapshotError(f"role {role} is not known.")
        if account_id in account_ids:
            raise ManualSnapshotError(f"account_id {account_id} is duplicated.")
        account_ids.add(account_id)

        configured = account_roles.get(account_id, {})
        include = configured.get("include_in_investable_by_default")
        protected = bool(configured.get("protected", False))
        accounts.append(
            Account(
                account_id=account_id,
                name=f"{platform} {account_id}",
                role=role,
                include_in_investable_by_default=include,
                protected=protected,
            )
        )
        if cash_eur > 0:
            holdings.append(Holding(account_id, "EUR", cash_eur, "cash"))

        raw_holdings = raw_account.get("holdings", [])
        if not isinstance(raw_holdings, list):
            raise ManualSnapshotError(f"holdings for {account_id} must be a list.")
        for holding_index, raw_holding_value in enumerate(raw_holdings):
            raw_holding = _require_mapping(raw_holding_value, f"holdings[{holding_index}]")
            asset_symbol = _require_non_empty_text(raw_holding.get("asset_symbol"), "asset_symbol")
            asset_class = _require_non_empty_text(raw_holding.get("asset_class"), "asset_class")
            market_value = _require_non_negative_number(
                raw_holding.get("market_value_eur"),
                "holding market_value_eur",
            )
            classification = raw_holding.get("classification")
            if classification is not None:
                classification = _require_non_empty_text(classification, "classification")
            holdings.append(Holding(account_id, asset_symbol, market_value, asset_class, classification))

    for raw_holding in raw.get("holdings", []):
        raw_holding = _require_mapping(raw_holding, "holding")
        account_id = _require_non_empty_text(raw_holding.get("account_id"), "holding account_id")
        if account_id not in account_ids:
            raise ManualSnapshotError(f"holding maps to unknown account_id {account_id}.")
        asset_symbol = _require_non_empty_text(raw_holding.get("asset_symbol"), "asset_symbol")
        asset_class = _require_non_empty_text(raw_holding.get("asset_class"), "asset_class")
        market_value = _require_non_negative_number(raw_holding.get("market_value_eur"), "holding market_value_eur")
        classification = raw_holding.get("classification")
        if classification is not None:
            classification = _require_non_empty_text(classification, "classification")
        holdings.append(Holding(account_id, asset_symbol, market_value, asset_class, classification))

    current_date = today or date.today()
    if (current_date - snapshot_date).days > 7:
        warnings.append(
            ValidationWarning(
                code="stale_snapshot",
                message=f"Snapshot date {snapshot_date_text} is older than 7 days.",
                severity="warning",
            )
        )

    return PortfolioSnapshot(snapshot_date_text, accounts, holdings), warnings
