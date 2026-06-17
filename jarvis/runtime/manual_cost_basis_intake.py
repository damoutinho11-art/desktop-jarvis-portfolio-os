"""J.A.R.V.I.S. v61.0 manual cost basis intake.

Creates and validates a local-only manual cost basis file. This removes no
execution safeguards and never connects to brokers.

Safety invariant: Automated research. Manual trust. Manual approval. No execution.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V61_0_MANUAL_COST_BASIS_INTAKE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V61_0_MANUAL_COST_BASIS_INTAKE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V61_0_MANUAL_COST_BASIS_INTAKE_BLOCKED_SAFE"

INTAKE_READY = "MANUAL_COST_BASIS_READY_FOR_FULL_ALLOCATION_DATA_COVERAGE"
INTAKE_REVIEW_REQUIRED = "MANUAL_COST_BASIS_INTAKE_REVIEW_REQUIRED"
INTAKE_BLOCKED = "MANUAL_COST_BASIS_INTAKE_BLOCKED"

DEFAULT_MANUAL_COST_BASIS_PATH = "jarvis/local/manual_cost_basis.local.json"


def _today_iso() -> str:
    return date.today().isoformat()


def _round2(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _read_json(path: str | Path) -> tuple[bool, bool, dict[str, Any], str | None]:
    resolved = Path(path)
    if not resolved.exists():
        return False, False, {}, None
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return True, False, {}, str(exc)
    if not isinstance(payload, dict):
        return True, False, {}, "JSON root is not an object"
    return True, True, payload, None


def _template_payload(current_date: str) -> dict[str, Any]:
    return {
        "schema": "JARVIS_MANUAL_COST_BASIS_V1",
        "as_of": current_date,
        "is_template": True,
        "cost_basis_confirmed": False,
        "currency": "EUR",
        "manual_only": True,
        "broker_api_used": False,
        "credentials_used": False,
        "private_account_ingestion_used": False,
        "positions": [
            {
                "position_id": "example_position_id_replace_me",
                "asset_name": "Example ETF or crypto position",
                "symbol": "EXAMPLE",
                "platform": "LHV_or_Lightyear_or_Kraken",
                "lane": "stock_fund_etf_or_crypto",
                "current_market_value_eur": None,
                "total_cost_basis_eur": None,
                "unrealized_gain_loss_eur": None,
                "cost_basis_source": "manual_user_entry",
                "confirmed": False,
                "notes": "Replace this example with real manually entered data, or leave unconfirmed."
            }
        ],
        "policy_notes": [
            "Local-only manual cost basis file.",
            "Do not include account numbers, IBANs, card numbers, login details, or credentials.",
            "This file is for risk/tax-aware research only.",
            "This file does not approve selling, migration, orders, or trades."
        ]
    }


def write_manual_cost_basis_template(path: str | Path = DEFAULT_MANUAL_COST_BASIS_PATH, *, current_date: str | None = None) -> Path:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(
        json.dumps(_template_payload(current_date or _today_iso()), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return resolved


def _position_has_cost_basis(position: Mapping[str, Any]) -> bool:
    if not bool(position.get("confirmed")):
        return False
    market_value = _round2(position.get("current_market_value_eur"))
    cost_basis = _round2(position.get("total_cost_basis_eur"))
    return market_value is not None and cost_basis is not None


def build_manual_cost_basis_intake_result(
    *,
    current_date: str | None = None,
    manual_cost_basis_path: str | Path = DEFAULT_MANUAL_COST_BASIS_PATH,
    write_template: bool = False,
) -> dict[str, Any]:
    effective_date = current_date or _today_iso()
    if write_template:
        write_manual_cost_basis_template(manual_cost_basis_path, current_date=effective_date)

    present, loaded, payload, error = _read_json(manual_cost_basis_path)
    template = bool(payload.get("is_template")) if loaded else False
    confirmed = bool(payload.get("cost_basis_confirmed")) and not template if loaded else False

    blockers: list[str] = []
    warnings: list[str] = []

    if error:
        blockers.append("manual_cost_basis_file_unreadable")
    if not present:
        blockers.append("manual_cost_basis_file_missing")
    elif not loaded:
        blockers.append("manual_cost_basis_file_not_loaded")
    elif template:
        blockers.append("manual_cost_basis_file_is_template")
    elif not confirmed:
        blockers.append("manual_cost_basis_not_confirmed")

    raw_positions = payload.get("positions") if loaded else []
    positions = [item for item in raw_positions if isinstance(item, Mapping)] if isinstance(raw_positions, list) else []
    confirmed_positions = [item for item in positions if _position_has_cost_basis(item)]
    missing_positions = []
    for item in positions:
        position_id = str(item.get("position_id") or item.get("symbol") or item.get("asset_name") or "unknown_position")
        if not _position_has_cost_basis(item):
            missing_positions.append(position_id)

    if confirmed and not positions:
        blockers.append("manual_cost_basis_positions_missing")
    if confirmed and missing_positions:
        blockers.append("manual_cost_basis_positions_incomplete")
    if confirmed_positions:
        warnings.append("manual cost basis manually confirmed; still no selling, migration, orders, or trades")

    cost_basis_ready = not blockers
    status = STATUS_READY if cost_basis_ready else STATUS_REVIEW_REQUIRED if present and loaded else STATUS_BLOCKED
    intake_status = INTAKE_READY if cost_basis_ready else INTAKE_REVIEW_REQUIRED if present and loaded else INTAKE_BLOCKED

    total_market_value = round(sum(_round2(item.get("current_market_value_eur")) or 0.0 for item in confirmed_positions), 2)
    total_cost_basis = round(sum(_round2(item.get("total_cost_basis_eur")) or 0.0 for item in confirmed_positions), 2)
    total_unrealized = round(total_market_value - total_cost_basis, 2)

    return {
        "status": status,
        "intake_status": intake_status,
        "current_date": effective_date,
        "manual_cost_basis_path": str(manual_cost_basis_path),
        "template_write_requested": write_template,
        "present": present,
        "loaded": loaded,
        "template": template,
        "confirmed": confirmed,
        "cost_basis_ready_for_full_allocation_data_gate": cost_basis_ready,
        "positions_count": len(positions),
        "confirmed_positions_count": len(confirmed_positions),
        "missing_or_incomplete_positions": missing_positions,
        "total_market_value_eur": total_market_value,
        "total_cost_basis_eur": total_cost_basis,
        "total_unrealized_gain_loss_eur": total_unrealized,
        "blockers": list(dict.fromkeys(blockers)),
        "warnings": list(dict.fromkeys(warnings)),
        "allocation_mutation": False,
        "approval_ticket_mutation": False,
        "portfolio_state_mutation": False,
        "buy_request_created": False,
        "auto_sell_allowed": False,
        "auto_migration_allowed": False,
        "broker_connection_forbidden": True,
        "credentials_forbidden": True,
        "private_account_data_ingestion_forbidden": True,
        "order_creation_forbidden": True,
        "no_trades_executed": True,
    }


def format_manual_cost_basis_intake(result: Mapping[str, Any]) -> str:
    lines = [
        "J.A.R.V.I.S. MANUAL COST BASIS INTAKE",
        f"status: {result['status']}",
        f"intake status: {result['intake_status']}",
        f"current date: {result['current_date']}",
        f"manual cost basis path: {result['manual_cost_basis_path']}",
        f"template write requested: {result['template_write_requested']}",
        "",
        "Cost basis file:",
        f"- present: {result['present']}",
        f"- loaded: {result['loaded']}",
        f"- template: {result['template']}",
        f"- confirmed: {result['confirmed']}",
        f"- ready for full allocation data gate: {result['cost_basis_ready_for_full_allocation_data_gate']}",
        "",
        "Positions:",
        f"- positions count: {result['positions_count']}",
        f"- confirmed positions count: {result['confirmed_positions_count']}",
        f"- missing/incomplete positions: {', '.join(result['missing_or_incomplete_positions']) if result['missing_or_incomplete_positions'] else 'none'}",
        f"- total market value EUR: {result['total_market_value_eur']}",
        f"- total cost basis EUR: {result['total_cost_basis_eur']}",
        f"- total unrealized gain/loss EUR: {result['total_unrealized_gain_loss_eur']}",
        "",
        "Safety:",
        f"- allocation mutation: {result['allocation_mutation']}",
        f"- approval ticket mutation: {result['approval_ticket_mutation']}",
        f"- portfolio state mutation: {result['portfolio_state_mutation']}",
        f"- buy request created: {result['buy_request_created']}",
        f"- auto sell allowed: {result['auto_sell_allowed']}",
        f"- auto migration allowed: {result['auto_migration_allowed']}",
        "- no broker connection",
        "- no credentials",
        "- no private account data ingestion",
        "- no orders created",
        "- no trades executed",
    ]
    if result["blockers"]:
        lines.extend(["", "Blockers:"] + [f"- {item}" for item in result["blockers"]])
    else:
        lines.append("blockers: none")
    if result["warnings"]:
        lines.extend(["", "Warnings:"] + [f"- {item}" for item in result["warnings"]])
    else:
        lines.append("warnings: none")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. v61 manual cost basis intake")
    parser.add_argument("--manual-cost-basis-intake", action="store_true")
    parser.add_argument("--write-manual-cost-basis-template", action="store_true")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--manual-cost-basis-path", default=DEFAULT_MANUAL_COST_BASIS_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)
    if args.safety_check:
        print(build_safety_check_console_output())
        return 0
    result = build_manual_cost_basis_intake_result(
        current_date=args.current_date,
        manual_cost_basis_path=args.manual_cost_basis_path,
        write_template=args.write_manual_cost_basis_template,
    )
    print(format_manual_cost_basis_intake(result))
    return 0


__all__ = [
    "DEFAULT_MANUAL_COST_BASIS_PATH",
    "STATUS_BLOCKED",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "build_manual_cost_basis_intake_result",
    "format_manual_cost_basis_intake",
    "main",
    "write_manual_cost_basis_template",
]
