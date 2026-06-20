"""J.A.R.V.I.S. v131.0 manual holdings update workflow.

This runtime records only what Diogo manually says he already bought outside
J.A.R.V.I.S. It never connects to brokers, requests credentials, creates buy
requests, mutates allocation, creates orders, executes trades, or auto-approves
anything.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_BLOCKED_SAFE"

DEFAULT_MANUAL_HOLDINGS_PATH = "jarvis/local/manual_holdings.local.json"
MANUAL_SOURCE = "diogo_manual_entry"
SCHEMA = "JARVIS_MANUAL_HOLDINGS_V1"

REQUIRED_POSITION_FIELDS = (
    "symbol",
    "name",
    "lane",
    "quantity",
    "average_price_eur",
    "cost_basis_eur",
    "market_value_eur",
    "platform",
    "purchase_date",
    "notes",
)

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
class ManualHoldingsUpdateResult:
    status: str
    current_date: str
    holdings_ready: bool
    holdings_path: str
    file_exists: bool
    file_loaded: bool
    is_template: bool
    manual_only: bool
    source: str | None
    holdings_confirmed: bool
    positions: list[dict[str, Any]]
    positions_count: int
    confirmed_positions_count: int
    total_cost_basis_eur: float
    total_market_value_eur: float | None
    total_market_value_available: bool
    template_requested: bool
    template_written: bool
    warnings: list[str]
    blockers: list[str]
    safety_flags: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _today_iso() -> str:
    return date.today().isoformat()


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


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
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        return True, False, {}, str(exc)
    if not isinstance(payload, dict):
        return True, False, {}, "JSON root is not an object"
    return True, True, payload, None


def _find_forbidden_keys(payload: Any, prefix: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_text = str(key)
            current = f"{prefix}.{key_text}" if prefix else key_text
            if any(fragment in key_text.lower() for fragment in FORBIDDEN_KEY_FRAGMENTS):
                found.append(current)
            found.extend(_find_forbidden_keys(value, current))
    elif isinstance(payload, list):
        for idx, value in enumerate(payload):
            found.extend(_find_forbidden_keys(value, f"{prefix}[{idx}]"))
    return _dedupe(found)


def build_manual_holdings_template(*, current_date: str | None = None) -> dict[str, Any]:
    current_date_text = current_date or _today_iso()
    seeds = [
        ("BTC", "Bitcoin", "crypto"),
        ("ETH", "Ethereum", "crypto"),
        ("VWCE", "Vanguard FTSE All-World UCITS ETF", "etf_fund"),
        ("IS3Q.DE", "iShares Edge MSCI World Quality Factor UCITS ETF", "etf_fund"),
        ("MSFT", "Microsoft", "individual_stock"),
    ]
    return {
        "schema": SCHEMA,
        "as_of": current_date_text,
        "is_template": True,
        "manual_only": True,
        "source": MANUAL_SOURCE,
        "holdings_confirmed": False,
        "currency": "EUR",
        "positions": [
            {
                "symbol": symbol,
                "name": name,
                "lane": lane,
                "quantity": None,
                "average_price_eur": None,
                "cost_basis_eur": None,
                "market_value_eur": None,
                "platform": "",
                "purchase_date": "",
                "notes": "",
            }
            for symbol, name, lane in seeds
        ],
        "policy_notes": [
            "Keep this file local only and do not commit it.",
            "Only enter purchases Diogo already made manually outside J.A.R.V.I.S.",
            "Set is_template to false and holdings_confirmed to true after filling real data.",
            "Do not add passwords, API keys, broker tokens, account numbers, or credentials.",
        ],
    }


def write_manual_holdings_template(
    path: str | Path = DEFAULT_MANUAL_HOLDINGS_PATH,
    *,
    current_date: str | None = None,
) -> Path:
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    resolved.write_text(
        json.dumps(build_manual_holdings_template(current_date=current_date), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return resolved


def _safety_flags() -> dict[str, Any]:
    safety_output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output
    return {
        "manual_only": True,
        "source_required": MANUAL_SOURCE,
        "safety_check_blocked_execution": safety_blocked,
        "execution_forbidden": True,
        "allocation_mutation": False,
        "approval_ticket_mutation": False,
        "portfolio_state_mutation": False,
        "buy_request_created": False,
        "auto_approval": False,
        "broker_connection": False,
        "credentials_used": False,
        "private_account_data_ingestion": False,
        "order_created": False,
        "trade_executed": False,
    }


def _position_symbol(position: Mapping[str, Any]) -> str:
    return str(position.get("symbol") or "").strip().upper()


def _position_is_confirmed(position: Mapping[str, Any], *, holdings_confirmed: bool, is_template: bool) -> bool:
    if not holdings_confirmed or is_template:
        return False
    quantity = _round2(position.get("quantity"))
    cost_basis = _round2(position.get("cost_basis_eur"))
    return bool(_position_symbol(position)) and quantity is not None and quantity > 0 and cost_basis is not None and cost_basis > 0


def _normalize_position(position: Mapping[str, Any], *, confirmed: bool) -> dict[str, Any]:
    row = {field: position.get(field) for field in REQUIRED_POSITION_FIELDS}
    row["symbol"] = str(row.get("symbol") or "").strip().upper()
    row["quantity"] = _round2(row.get("quantity"))
    row["average_price_eur"] = _round2(row.get("average_price_eur"))
    row["cost_basis_eur"] = _round2(row.get("cost_basis_eur"))
    row["market_value_eur"] = _round2(row.get("market_value_eur"))
    row["confirmed"] = confirmed
    return row


def _extract_positions(payload: Mapping[str, Any], *, holdings_confirmed: bool, is_template: bool) -> list[dict[str, Any]]:
    raw_positions = payload.get("positions", [])
    if not isinstance(raw_positions, list):
        return []
    rows: list[dict[str, Any]] = []
    for item in raw_positions:
        if not isinstance(item, Mapping):
            continue
        confirmed = _position_is_confirmed(item, holdings_confirmed=holdings_confirmed, is_template=is_template)
        rows.append(_normalize_position(item, confirmed=confirmed))
    return rows


def build_manual_holdings_update_result(
    *,
    current_date: str | None = None,
    holdings_path: str | Path = DEFAULT_MANUAL_HOLDINGS_PATH,
    template_requested: bool = False,
    write_template: bool = False,
) -> ManualHoldingsUpdateResult:
    current_date_text = current_date or _today_iso()
    path = Path(holdings_path)
    template_written = False
    warnings: list[str] = []
    blockers: list[str] = []

    if write_template:
        write_manual_holdings_template(path, current_date=current_date_text)
        template_written = True
        template_requested = True

    file_exists, file_loaded, payload, error = _read_json(path)
    if error:
        warnings.append(f"manual_holdings_file_unreadable: {error}")

    forbidden_keys = _find_forbidden_keys(payload) if file_loaded else []
    if forbidden_keys:
        blockers.append("manual_holdings_file_contains_forbidden_credential_like_keys")

    is_template = bool(payload.get("is_template")) if file_loaded else False
    manual_only = bool(payload.get("manual_only")) if file_loaded else False
    source = str(payload.get("source")) if file_loaded and payload.get("source") is not None else None
    holdings_confirmed = bool(payload.get("holdings_confirmed")) if file_loaded else False
    positions = _extract_positions(payload, holdings_confirmed=holdings_confirmed, is_template=is_template) if file_loaded else []
    confirmed_positions = [item for item in positions if item.get("confirmed")]

    if not file_exists:
        warnings.append("manual holdings file is missing; holdings not entered yet")
    elif not file_loaded:
        warnings.append("manual holdings file could not be loaded; check JSON formatting")
    else:
        if manual_only is not True:
            blockers.append("manual_only_must_be_true")
        if source != MANUAL_SOURCE:
            blockers.append("source_must_be_diogo_manual_entry")
        if is_template:
            warnings.append("manual holdings file is still a blank template; fill real values before using it")
        if not holdings_confirmed:
            warnings.append("holdings_confirmed is not true; positions remain review-required")
        if not positions:
            warnings.append("positions list is missing or empty")
        missing_fields: list[str] = []
        for index, item in enumerate(positions):
            for field in REQUIRED_POSITION_FIELDS:
                if field not in item:
                    missing_fields.append(f"positions[{index}].{field}")
        if missing_fields:
            warnings.append("positions are missing required fields: " + ", ".join(missing_fields[:8]))
        if holdings_confirmed and not confirmed_positions and not is_template:
            warnings.append("no confirmed positions with positive quantity and cost basis were found")

    total_cost_basis = round(sum(float(item.get("cost_basis_eur") or 0.0) for item in confirmed_positions), 2)
    market_values = [item.get("market_value_eur") for item in confirmed_positions]
    market_value_available = bool(confirmed_positions) and all(value is not None for value in market_values)
    total_market_value = round(sum(float(value or 0.0) for value in market_values), 2) if market_value_available else None

    safety = _safety_flags()
    if not safety.get("safety_check_blocked_execution"):
        blockers.append("safety_check_did_not_block_execution")

    holdings_ready = bool(
        file_loaded
        and not is_template
        and manual_only
        and source == MANUAL_SOURCE
        and holdings_confirmed
        and confirmed_positions
        and not blockers
    )

    if blockers:
        status = STATUS_BLOCKED
    elif holdings_ready:
        status = STATUS_READY
    else:
        status = STATUS_REVIEW_REQUIRED

    return ManualHoldingsUpdateResult(
        status=status,
        current_date=current_date_text,
        holdings_ready=holdings_ready,
        holdings_path=str(path),
        file_exists=file_exists,
        file_loaded=file_loaded,
        is_template=is_template,
        manual_only=manual_only,
        source=source,
        holdings_confirmed=holdings_confirmed,
        positions=positions,
        positions_count=len(positions),
        confirmed_positions_count=len(confirmed_positions),
        total_cost_basis_eur=total_cost_basis,
        total_market_value_eur=total_market_value,
        total_market_value_available=market_value_available,
        template_requested=template_requested,
        template_written=template_written,
        warnings=_dedupe(warnings),
        blockers=_dedupe(blockers),
        safety_flags=safety,
    )


def format_manual_holdings_update(result: ManualHoldingsUpdateResult) -> str:
    lines = [
        "J.A.R.V.I.S. MANUAL HOLDINGS",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"holdings ready: {result.holdings_ready}",
        f"file exists: {result.file_exists}",
        f"file loaded: {result.file_loaded}",
        f"holdings path: {result.holdings_path}",
        f"template requested: {result.template_requested}",
        f"template written: {result.template_written}",
        f"is template: {result.is_template}",
        f"manual only: {result.manual_only}",
        f"source: {result.source}",
        f"holdings confirmed: {result.holdings_confirmed}",
        f"positions: {result.positions_count}",
        f"confirmed positions: {result.confirmed_positions_count}",
        f"total cost basis EUR: {result.total_cost_basis_eur:.2f}",
        f"total market value EUR: {result.total_market_value_eur:.2f}" if result.total_market_value_available else "total market value EUR: not available",
        "",
        "POSITIONS:",
    ]
    if result.positions:
        for item in result.positions:
            cost = item.get("cost_basis_eur")
            market = item.get("market_value_eur")
            lines.append(
                "- "
                f"{item.get('symbol') or 'UNKNOWN'} | {item.get('name') or ''} | {item.get('lane') or ''} | "
                f"quantity {item.get('quantity')} | cost basis EUR {cost if cost is not None else 'n/a'} | "
                f"market value EUR {market if market is not None else 'n/a'} | confirmed {item.get('confirmed')}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "SAFETY FLAGS:",
            f"- manual-only: {result.safety_flags.get('manual_only')}",
            f"- execution forbidden: {result.safety_flags.get('execution_forbidden')}",
            f"- safety-check blocked execution: {result.safety_flags.get('safety_check_blocked_execution')}",
            f"- allocation mutation: {result.safety_flags.get('allocation_mutation')}",
            f"- approval ticket mutation: {result.safety_flags.get('approval_ticket_mutation')}",
            f"- buy request created: {result.safety_flags.get('buy_request_created')}",
            f"- auto approval: {result.safety_flags.get('auto_approval')}",
            f"- broker connection: {result.safety_flags.get('broker_connection')}",
            f"- credentials used: {result.safety_flags.get('credentials_used')}",
            f"- order created: {result.safety_flags.get('order_created')}",
            f"- trade executed: {result.safety_flags.get('trade_executed')}",
            "",
            "WARNINGS:",
        ]
    )
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    lines.append("")
    lines.append("Safety: record-only. Diogo buys manually outside J.A.R.V.I.S.; no broker, credential, order, trade, or auto-approval path is enabled.")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Record or review local manual holdings.")
    parser.add_argument("--holdings-template", action="store_true")
    parser.add_argument("--write-holdings-template", action="store_true")
    parser.add_argument("--holdings-status", action="store_true")
    parser.add_argument("--holdings-path", default=DEFAULT_MANUAL_HOLDINGS_PATH)
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_manual_holdings_update_result(
        current_date=args.current_date,
        holdings_path=args.holdings_path,
        template_requested=args.holdings_template,
        write_template=args.write_holdings_template,
    )
    print(format_manual_holdings_update(result))
    if args.holdings_template and not args.write_holdings_template:
        print("")
        print("TEMPLATE PREVIEW:")
        print(json.dumps(build_manual_holdings_template(current_date=result.current_date), indent=2, sort_keys=True))
    return 0 if result.status != STATUS_BLOCKED else 1


__all__ = [
    "DEFAULT_MANUAL_HOLDINGS_PATH",
    "MANUAL_SOURCE",
    "REQUIRED_POSITION_FIELDS",
    "STATUS_BLOCKED",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "ManualHoldingsUpdateResult",
    "build_manual_holdings_template",
    "build_manual_holdings_update_result",
    "format_manual_holdings_update",
    "main",
    "write_manual_holdings_template",
]


if __name__ == "__main__":
    raise SystemExit(main())
