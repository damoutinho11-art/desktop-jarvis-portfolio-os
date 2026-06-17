"""J.A.R.V.I.S. v52.0 manual portfolio snapshot intake.

This module creates and validates a brokerless local portfolio snapshot.

It is intentionally manual-only. It does not connect to brokers, request
credentials, ingest private broker data automatically, mutate allocation, create
buy requests, create orders, or execute trades.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from jarvis.runtime.safety import build_safety_check_console_output
from jarvis.runtime.allocation_strategy_audit import DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH

STATUS_READY = "JARVIS_V52_0_MANUAL_PORTFOLIO_SNAPSHOT_INTAKE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V52_0_MANUAL_PORTFOLIO_SNAPSHOT_INTAKE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V52_0_MANUAL_PORTFOLIO_SNAPSHOT_INTAKE_BLOCKED_SAFE"

INTAKE_READY = "MANUAL_PORTFOLIO_SNAPSHOT_READY_FOR_DATA_COVERAGE"
INTAKE_TEMPLATE_READY = "MANUAL_PORTFOLIO_SNAPSHOT_TEMPLATE_READY_FOR_FILLING"
INTAKE_TEMPLATE_WRITTEN = "MANUAL_PORTFOLIO_SNAPSHOT_TEMPLATE_WRITTEN_REVIEW_REQUIRED"
INTAKE_REVIEW_REQUIRED = "MANUAL_PORTFOLIO_SNAPSHOT_REVIEW_REQUIRED"
INTAKE_BLOCKED = "MANUAL_PORTFOLIO_SNAPSHOT_BLOCKED"

NEXT_STAGE = "manual_snapshot_to_allocation_audit_bridge"

FORBIDDEN_KEY_FRAGMENTS = (
    "password",
    "passwd",
    "api_key",
    "apikey",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "private_key",
    "broker_credentials",
    "credential",
)


@dataclass(frozen=True)
class ManualPortfolioSnapshotIntakeResult:
    status: str
    intake_status: str
    recommended_next_stage: str
    current_date: str
    snapshot_path: str
    template_requested: bool
    template_written: bool
    snapshot_present: bool
    snapshot_loaded: bool
    snapshot_is_template: bool
    brokerless_manual_snapshot: bool
    holdings_count: int
    cash_eur_available: bool
    cash_eur: float | None
    cost_basis_available: bool
    forbidden_credential_keys_found: tuple[str, ...]
    valid_for_allocation_data_gate: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "intake_status": self.intake_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "snapshot_path": self.snapshot_path,
            "template_requested": self.template_requested,
            "template_written": self.template_written,
            "snapshot_present": self.snapshot_present,
            "snapshot_loaded": self.snapshot_loaded,
            "snapshot_is_template": self.snapshot_is_template,
            "brokerless_manual_snapshot": self.brokerless_manual_snapshot,
            "holdings_count": self.holdings_count,
            "cash_eur_available": self.cash_eur_available,
            "cash_eur": self.cash_eur,
            "cost_basis_available": self.cost_basis_available,
            "forbidden_credential_keys_found": list(self.forbidden_credential_keys_found),
            "valid_for_allocation_data_gate": self.valid_for_allocation_data_gate,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def _today_iso() -> str:
    return date.today().isoformat()


def _dedupe(items: Sequence[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _safe_path(path: str | Path) -> Path:
    return Path(path)


def _is_under_jarvis_local(path: Path) -> bool:
    normalized = path if path.is_absolute() else Path.cwd() / path
    local_root = (Path.cwd() / "jarvis" / "local").resolve()
    try:
        normalized.resolve().relative_to(local_root)
        return True
    except ValueError:
        return False


def _load_json(path: Path) -> Mapping[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


def _find_forbidden_keys(payload: Any, prefix: str = "") -> tuple[str, ...]:
    found: list[str] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_text = str(key)
            lower = key_text.lower()
            current = f"{prefix}.{key_text}" if prefix else key_text
            if any(fragment in lower for fragment in FORBIDDEN_KEY_FRAGMENTS):
                found.append(current)
            found.extend(_find_forbidden_keys(value, current))
    elif isinstance(payload, list):
        for idx, value in enumerate(payload):
            found.extend(_find_forbidden_keys(value, f"{prefix}[{idx}]"))
    return _dedupe(found)


def build_manual_portfolio_snapshot_template(*, current_date: str | None = None) -> dict[str, Any]:
    current_date_text = current_date or _today_iso()
    return {
        "schema": "JARVIS_MANUAL_PORTFOLIO_SNAPSHOT_V1",
        "snapshot_date": current_date_text,
        "is_template": True,
        "brokerless_manual_snapshot": True,
        "cash_eur": 0.0,
        "holdings": [
            {
                "lane": "stock_fund_etf",
                "symbol": "IS3Q.DE",
                "instrument_id": "ishares_world_quality_is3q_de",
                "quantity": 0.0,
                "market_value_eur": 0.0,
                "cost_basis_eur": 0.0,
                "platform": "manual_entry",
                "notes": "replace this example with your real holding or delete it",
            },
            {
                "lane": "crypto",
                "symbol": "HYPE",
                "instrument_id": "hype",
                "quantity": 0.0,
                "market_value_eur": 0.0,
                "cost_basis_eur": 0.0,
                "platform": "manual_entry",
                "notes": "replace this example with your real holding or delete it",
            },
        ],
        "cost_basis": {
            "IS3Q.DE": 0.0,
            "HYPE": 0.0,
        },
        "notes": [
            "Keep this file local only.",
            "Do not add passwords, API keys, broker tokens, or credentials.",
            "Do not commit this file.",
            "Set is_template to false after filling real data.",
        ],
    }


def _snapshot_metrics(payload: Mapping[str, Any] | None) -> tuple[bool, bool, int, bool, float | None, bool, tuple[str, ...]]:
    if payload is None:
        return False, False, 0, False, None, False, ()

    is_template = bool(payload.get("is_template", False))
    brokerless = bool(payload.get("brokerless_manual_snapshot", False))
    holdings = payload.get("holdings")
    holdings_count = len(holdings) if isinstance(holdings, list) else 0
    cash = payload.get("cash_eur")
    cash_ready = isinstance(cash, (int, float)) and cash >= 0
    cash_value = round(float(cash), 2) if cash_ready else None
    cost_basis = payload.get("cost_basis")
    cost_basis_ready = isinstance(cost_basis, (dict, list)) and len(cost_basis) > 0
    forbidden = _find_forbidden_keys(payload)
    return is_template, brokerless, holdings_count, cash_ready, cash_value, cost_basis_ready, forbidden


def build_manual_portfolio_snapshot_intake_result(
    *,
    current_date: str | None = None,
    snapshot_path: str | Path = DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH,
    template_requested: bool = False,
    write_template: bool = False,
    enforce_local_path: bool = True,
) -> ManualPortfolioSnapshotIntakeResult:
    current_date_text = current_date or _today_iso()
    path = _safe_path(snapshot_path)
    blockers: list[str] = []
    warnings: list[str] = []
    template_written = False

    if enforce_local_path and not _is_under_jarvis_local(path):
        blockers.append("manual portfolio snapshot path must remain under jarvis/local.")

    if write_template and not blockers:
        path.parent.mkdir(parents=True, exist_ok=True)
        template = build_manual_portfolio_snapshot_template(current_date=current_date_text)
        path.write_text(json.dumps(template, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        template_written = True
        template_requested = True

    payload = _load_json(path)
    snapshot_present = path.exists()
    snapshot_loaded = payload is not None
    is_template, brokerless, holdings_count, cash_ready, cash_value, cost_basis_ready, forbidden = _snapshot_metrics(payload)

    if forbidden:
        blockers.append("snapshot contains forbidden credential-like keys.")
    if not snapshot_present:
        warnings.append("manual portfolio snapshot file is missing.")
    elif not snapshot_loaded:
        warnings.append("manual portfolio snapshot file is unreadable or invalid JSON.")
    elif is_template:
        warnings.append("manual portfolio snapshot is still marked as a template; fill real values and set is_template to false.")
    else:
        if not brokerless:
            warnings.append("brokerless_manual_snapshot must be true.")
        if holdings_count <= 0:
            warnings.append("holdings list is missing or empty.")
        if not cash_ready:
            warnings.append("cash_eur is missing or invalid.")
        if not cost_basis_ready:
            warnings.append("cost_basis is missing or empty.")

    valid_for_gate = (
        snapshot_loaded
        and not is_template
        and brokerless
        and holdings_count > 0
        and cash_ready
        and cost_basis_ready
        and not forbidden
        and not blockers
    )

    if template_written:
        intake_status = INTAKE_TEMPLATE_WRITTEN
    elif template_requested:
        intake_status = INTAKE_TEMPLATE_READY
    elif valid_for_gate:
        intake_status = INTAKE_READY
    elif blockers:
        intake_status = INTAKE_BLOCKED
    else:
        intake_status = INTAKE_REVIEW_REQUIRED

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    if unique_blockers:
        status = STATUS_BLOCKED
    elif valid_for_gate:
        status = STATUS_READY
    else:
        status = STATUS_REVIEW_REQUIRED

    return ManualPortfolioSnapshotIntakeResult(
        status=status,
        intake_status=intake_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        snapshot_path=str(path),
        template_requested=template_requested,
        template_written=template_written,
        snapshot_present=snapshot_present,
        snapshot_loaded=snapshot_loaded,
        snapshot_is_template=is_template,
        brokerless_manual_snapshot=brokerless,
        holdings_count=holdings_count,
        cash_eur_available=cash_ready,
        cash_eur=cash_value,
        cost_basis_available=cost_basis_ready,
        forbidden_credential_keys_found=forbidden,
        valid_for_allocation_data_gate=valid_for_gate,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )


def format_manual_portfolio_snapshot_intake(result: ManualPortfolioSnapshotIntakeResult) -> str:
    lines = [
        "J.A.R.V.I.S. MANUAL PORTFOLIO SNAPSHOT INTAKE",
        f"status: {result.status}",
        f"intake status: {result.intake_status}",
        f"current date: {result.current_date}",
        f"snapshot path: {result.snapshot_path}",
        f"template requested: {result.template_requested}",
        f"template written: {result.template_written}",
        f"snapshot present: {result.snapshot_present}",
        f"snapshot loaded: {result.snapshot_loaded}",
        f"snapshot is template: {result.snapshot_is_template}",
        f"brokerless manual snapshot: {result.brokerless_manual_snapshot}",
        f"holdings count: {result.holdings_count}",
        f"cash EUR available: {result.cash_eur_available}",
        f"cash EUR: {result.cash_eur}",
        f"cost basis available: {result.cost_basis_available}",
        f"valid for allocation data gate: {result.valid_for_allocation_data_gate}",
        "",
        "Manual snapshot policy:",
        "- local JSON file only",
        "- no broker API",
        "- no credentials",
        "- no automatic private account ingestion",
        "- do not commit the snapshot file",
        "- use this only to improve allocation-audit data coverage",
        "",
        "Safety:",
        f"- allocation mutation: {result.allocation_mutation}",
        f"- approval ticket mutation: {result.approval_ticket_mutation}",
        f"- buy request created: {result.buy_request_created}",
        "- no broker connection",
        "- no credentials",
        "- no private account data ingestion",
        "- no orders created",
        "- no trades executed",
    ]

    if result.forbidden_credential_keys_found:
        lines.extend(["", "Forbidden credential-like keys found:"])
        lines.extend(f"- {key}" for key in result.forbidden_credential_keys_found)

    if result.blockers:
        lines.extend(["", "Blockers:"])
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("blockers: none")

    if result.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("warnings: none")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create or audit the manual portfolio snapshot.")
    parser.add_argument("--manual-portfolio-snapshot-intake", action="store_true")
    parser.add_argument("--manual-portfolio-snapshot-template", action="store_true")
    parser.add_argument("--write-manual-portfolio-snapshot-template", action="store_true")
    parser.add_argument("--manual-portfolio-snapshot-path", default=DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH)
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_manual_portfolio_snapshot_intake_result(
        current_date=args.current_date,
        snapshot_path=args.manual_portfolio_snapshot_path,
        template_requested=args.manual_portfolio_snapshot_template,
        write_template=args.write_manual_portfolio_snapshot_template,
    )
    print(format_manual_portfolio_snapshot_intake(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())