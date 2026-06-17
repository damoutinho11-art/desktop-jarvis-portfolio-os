"""J.A.R.V.I.S. v26.0 manual buy outcome portfolio-state recorder.

v26 is the missing local-state step after the user performs a real-world manual
buy outside J.A.R.V.I.S.

It can record an explicit manual-buy confirmation against the current local
approval ticket, update local portfolio_state.json, and append a local audit
record. It cannot create buy requests, connect to brokers, place orders, or
execute trades.
"""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

STATUS_READY = "JARVIS_V26_0_MANUAL_BUY_OUTCOME_PORTFOLIO_STATE_RECORDER_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V26_0_MANUAL_BUY_OUTCOME_PORTFOLIO_STATE_RECORDER_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V26_0_MANUAL_BUY_OUTCOME_PORTFOLIO_STATE_RECORDER_BLOCKED_SAFE"

RECORDER_READY = "MANUAL_BUY_OUTCOME_PORTFOLIO_STATE_RECORDER_READY"
RECORDER_REVIEW_REQUIRED = "MANUAL_BUY_OUTCOME_PORTFOLIO_STATE_RECORDER_REVIEW_REQUIRED"
RECORDER_BLOCKED = "MANUAL_BUY_OUTCOME_PORTFOLIO_STATE_RECORDER_BLOCKED"

DEFAULT_PORTFOLIO_STATE_PATH = "portfolio_state.json"
DEFAULT_APPROVAL_TICKET_PATH = "outputs/approval_ticket_latest.json"
DEFAULT_CONFIRMATION_LOG_PATH = "outputs/manual_buy_confirmations.jsonl"
CONFIRMATION_PHRASE = "I_CONFIRM_MANUAL_BUY_COMPLETED_OUTSIDE_JARVIS_NO_BROKER_API"


@dataclass(frozen=True)
class ManualBuyOutcomePortfolioStateRecorderResult:
    status: str
    recorder_status: str
    execution_date: str
    asset: str
    lane: str
    amount_eur: float
    approval_ticket_path: str
    portfolio_state_path: str
    confirmation_log_path: str
    approval_ticket_loaded: bool
    portfolio_state_loaded: bool
    confirmation_phrase_valid: bool
    ticket_match: bool
    portfolio_state_written: bool
    confirmation_logged: bool
    previous_portfolio_as_of: str
    updated_portfolio_as_of: str
    previous_asset_value_eur: float
    updated_asset_value_eur: float
    portfolio_state_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    final_user_buy_action_required: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "recorder_status": self.recorder_status,
            "execution_date": self.execution_date,
            "asset": self.asset,
            "lane": self.lane,
            "amount_eur": self.amount_eur,
            "approval_ticket_path": self.approval_ticket_path,
            "portfolio_state_path": self.portfolio_state_path,
            "confirmation_log_path": self.confirmation_log_path,
            "approval_ticket_loaded": self.approval_ticket_loaded,
            "portfolio_state_loaded": self.portfolio_state_loaded,
            "confirmation_phrase_valid": self.confirmation_phrase_valid,
            "ticket_match": self.ticket_match,
            "portfolio_state_written": self.portfolio_state_written,
            "confirmation_logged": self.confirmation_logged,
            "previous_portfolio_as_of": self.previous_portfolio_as_of,
            "updated_portfolio_as_of": self.updated_portfolio_as_of,
            "previous_asset_value_eur": self.previous_asset_value_eur,
            "updated_asset_value_eur": self.updated_asset_value_eur,
            "portfolio_state_mutation": self.portfolio_state_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def _load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def _write_json(path: str | Path, payload: dict[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: str | Path, payload: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _today_iso() -> str:
    return date.today().isoformat()


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _amount(value: Any) -> float:
    return round(float(value or 0.0), 2)


def _same_amount(left: float, right: float) -> bool:
    return abs(_amount(left) - _amount(right)) <= 0.01


def _dedupe(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _selected_ticket_asset_amount(ticket: dict[str, Any], lane: str) -> tuple[str | None, float]:
    if lane == "crypto":
        return (
            ticket.get("selected_crypto_candidate"),
            _amount(ticket.get("selected_crypto_amount_eur")),
        )
    if lane == "stock_fund_etf":
        return (
            ticket.get("selected_stock_fund_etf_candidate"),
            _amount(ticket.get("selected_stock_fund_etf_amount_eur")),
        )
    return None, 0.0


def _validate_ticket_match(
    ticket: dict[str, Any],
    *,
    asset: str,
    lane: str,
    amount_eur: float,
) -> tuple[bool, list[str]]:
    blockers: list[str] = []

    if ticket.get("buy_request_created") is True:
        blockers.append("approval ticket must not contain buy_request_created=True.")
    if ticket.get("trades_executed") is True:
        blockers.append("approval ticket must not contain trades_executed=True.")
    if ticket.get("broker_connection_forbidden") is not True:
        blockers.append("approval ticket must preserve broker_connection_forbidden=True.")
    if ticket.get("order_creation_forbidden") is not True:
        blockers.append("approval ticket must preserve order_creation_forbidden=True.")

    ticket_asset, ticket_amount = _selected_ticket_asset_amount(ticket, lane)
    if not ticket_asset:
        blockers.append(f"approval ticket does not contain a selected asset for lane {lane}.")
    elif str(ticket_asset) != asset:
        blockers.append(f"confirmed asset {asset} does not match approval ticket asset {ticket_asset}.")

    if not _same_amount(ticket_amount, amount_eur):
        blockers.append(
            f"confirmed amount EUR {amount_eur:.2f} does not match approval ticket amount EUR {ticket_amount:.2f}."
        )

    return not blockers, blockers


def _build_updated_portfolio_state(
    portfolio_state: dict[str, Any],
    *,
    asset: str,
    lane: str,
    amount_eur: float,
    execution_date: str,
    approval_ticket_id: str,
) -> tuple[dict[str, Any], float, float]:
    updated = deepcopy(portfolio_state)
    holdings = dict(updated.get("holdings") or {})
    if asset not in holdings:
        raise KeyError(f"asset {asset} is not present in portfolio_state holdings.")

    previous_value = _amount(holdings.get(asset))
    updated_value = _amount(previous_value + amount_eur)
    holdings[asset] = updated_value
    updated["holdings"] = holdings
    updated["as_of"] = execution_date
    updated["last_manual_buy_confirmation"] = {
        "asset": asset,
        "lane": lane,
        "amount_eur": _amount(amount_eur),
        "execution_date": execution_date,
        "approval_ticket_id": approval_ticket_id,
        "recorded_at": _now_utc_iso(),
        "source": "JARVIS_V26_0_MANUAL_BUY_OUTCOME_PORTFOLIO_STATE_RECORDER",
        "broker_connection_used": False,
        "order_created_by_jarvis": False,
        "trade_executed_by_jarvis": False,
    }
    return updated, previous_value, updated_value


def _confirmation_record(
    *,
    asset: str,
    lane: str,
    amount_eur: float,
    execution_date: str,
    approval_ticket: dict[str, Any],
    previous_asset_value_eur: float,
    updated_asset_value_eur: float,
) -> dict[str, Any]:
    return {
        "record_type": "manual_buy_confirmation",
        "recorded_at": _now_utc_iso(),
        "execution_date": execution_date,
        "asset": asset,
        "lane": lane,
        "amount_eur": _amount(amount_eur),
        "approval_ticket_id": approval_ticket.get("ticket_id"),
        "approval_ticket_as_of": approval_ticket.get("as_of"),
        "approval_ticket_generated_at": approval_ticket.get("generated_at"),
        "previous_asset_value_eur": previous_asset_value_eur,
        "updated_asset_value_eur": updated_asset_value_eur,
        "explicit_user_confirmation_required": True,
        "confirmation_phrase_used": CONFIRMATION_PHRASE,
        "broker_connection_used": False,
        "buy_request_created": False,
        "order_created_by_jarvis": False,
        "trade_executed_by_jarvis": False,
    }


def _iter_confirmation_records(path: str | Path) -> list[dict[str, Any]]:
    output = Path(path)
    if not output.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in output.read_text(encoding="utf-8-sig").splitlines():
        if not line.strip():
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)
    return records


def _confirmation_already_recorded(
    log_path: str | Path,
    *,
    approval_ticket: dict[str, Any],
    asset: str,
    lane: str,
    amount_eur: float,
    execution_date: str,
) -> bool:
    approval_ticket_id = str(approval_ticket.get("ticket_id") or "")
    for record in _iter_confirmation_records(log_path):
        if str(record.get("approval_ticket_id") or "") != approval_ticket_id:
            continue
        if str(record.get("asset") or "") != asset:
            continue
        if str(record.get("lane") or "") != lane:
            continue
        if str(record.get("execution_date") or "") != execution_date:
            continue
        if not _same_amount(float(record.get("amount_eur") or 0.0), amount_eur):
            continue
        return True
    return False


def build_manual_buy_outcome_portfolio_state_recorder_result(
    *,
    asset: str,
    lane: str,
    amount_eur: float,
    execution_date: str | None = None,
    confirmation_phrase: str = "",
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    portfolio_state_path: str | Path = DEFAULT_PORTFOLIO_STATE_PATH,
    confirmation_log_path: str | Path = DEFAULT_CONFIRMATION_LOG_PATH,
    write_state: bool = False,
) -> ManualBuyOutcomePortfolioStateRecorderResult:
    execution_date_text = execution_date or _today_iso()
    asset_text = str(asset).strip()
    lane_text = str(lane).strip()
    amount = _amount(amount_eur)

    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(execution_date_text) is None:
        blockers.append("execution_date must use YYYY-MM-DD format.")
    if lane_text not in {"crypto", "stock_fund_etf"}:
        blockers.append("lane must be crypto or stock_fund_etf.")
    if not asset_text:
        blockers.append("asset is required.")
    if amount <= 0:
        blockers.append("amount_eur must be positive.")

    confirmation_valid = confirmation_phrase == CONFIRMATION_PHRASE
    if not confirmation_valid:
        blockers.append("explicit manual-buy confirmation phrase is required.")

    approval_ticket_loaded = False
    portfolio_state_loaded = False
    ticket: dict[str, Any] = {}
    portfolio_state: dict[str, Any] = {}

    try:
        ticket = _load_json(approval_ticket_path)
        approval_ticket_loaded = True
    except Exception as exc:  # noqa: BLE001
        blockers.append(f"approval ticket could not be loaded: {exc.__class__.__name__}: {exc}")

    try:
        portfolio_state = _load_json(portfolio_state_path)
        portfolio_state_loaded = True
    except Exception as exc:  # noqa: BLE001
        blockers.append(f"portfolio_state could not be loaded: {exc.__class__.__name__}: {exc}")

    ticket_match = False
    if approval_ticket_loaded and not blockers:
        ticket_match, ticket_blockers = _validate_ticket_match(
            ticket,
            asset=asset_text,
            lane=lane_text,
            amount_eur=amount,
        )
        blockers.extend(ticket_blockers)

    if approval_ticket_loaded and not blockers and _confirmation_already_recorded(
        confirmation_log_path,
        approval_ticket=ticket,
        asset=asset_text,
        lane=lane_text,
        amount_eur=amount,
        execution_date=execution_date_text,
    ):
        blockers.append(
            "manual buy confirmation is already recorded for this approval ticket, asset, lane, amount, and execution date."
        )

    previous_as_of = str(portfolio_state.get("as_of", "")) if portfolio_state_loaded else ""
    updated_as_of = execution_date_text
    previous_value = 0.0
    updated_value = 0.0
    updated_portfolio: dict[str, Any] = {}

    if portfolio_state_loaded and approval_ticket_loaded and not blockers:
        try:
            updated_portfolio, previous_value, updated_value = _build_updated_portfolio_state(
                portfolio_state,
                asset=asset_text,
                lane=lane_text,
                amount_eur=amount,
                execution_date=execution_date_text,
                approval_ticket_id=str(ticket.get("ticket_id") or ""),
            )
        except Exception as exc:  # noqa: BLE001
            blockers.append(f"portfolio_state update failed: {exc.__class__.__name__}: {exc}")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    wrote_state = False
    logged = False
    if write_state and not unique_blockers:
        _write_json(portfolio_state_path, updated_portfolio)
        record = _confirmation_record(
            asset=asset_text,
            lane=lane_text,
            amount_eur=amount,
            execution_date=execution_date_text,
            approval_ticket=ticket,
            previous_asset_value_eur=previous_value,
            updated_asset_value_eur=updated_value,
        )
        _append_jsonl(confirmation_log_path, record)
        wrote_state = True
        logged = True

    status = STATUS_BLOCKED if unique_blockers else STATUS_READY
    recorder_status = RECORDER_BLOCKED if unique_blockers else RECORDER_READY

    return ManualBuyOutcomePortfolioStateRecorderResult(
        status=status,
        recorder_status=recorder_status,
        execution_date=execution_date_text,
        asset=asset_text,
        lane=lane_text,
        amount_eur=amount,
        approval_ticket_path=str(approval_ticket_path),
        portfolio_state_path=str(portfolio_state_path),
        confirmation_log_path=str(confirmation_log_path),
        approval_ticket_loaded=approval_ticket_loaded,
        portfolio_state_loaded=portfolio_state_loaded,
        confirmation_phrase_valid=confirmation_valid,
        ticket_match=ticket_match,
        portfolio_state_written=wrote_state,
        confirmation_logged=logged,
        previous_portfolio_as_of=previous_as_of,
        updated_portfolio_as_of=updated_as_of if not unique_blockers else previous_as_of,
        previous_asset_value_eur=previous_value,
        updated_asset_value_eur=updated_value,
        portfolio_state_mutation=wrote_state,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        final_user_buy_action_required=True,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )


def format_manual_buy_outcome_portfolio_state_recorder(
    result: ManualBuyOutcomePortfolioStateRecorderResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Manual Buy Outcome Portfolio-State Recorder",
        f"status: {result.status}",
        f"recorder status: {result.recorder_status}",
        f"execution date: {result.execution_date}",
        f"asset: {result.asset}",
        f"lane: {result.lane}",
        f"amount: EUR {result.amount_eur:,.2f}",
        f"approval ticket loaded: {result.approval_ticket_loaded}",
        f"portfolio state loaded: {result.portfolio_state_loaded}",
        f"confirmation phrase valid: {result.confirmation_phrase_valid}",
        f"ticket match: {result.ticket_match}",
        f"portfolio state written: {result.portfolio_state_written}",
        f"confirmation logged: {result.confirmation_logged}",
        f"previous portfolio as_of: {result.previous_portfolio_as_of or 'none'}",
        f"updated portfolio as_of: {result.updated_portfolio_as_of or 'none'}",
        f"previous {result.asset} value: EUR {result.previous_asset_value_eur:,.2f}",
        f"updated {result.asset} value: EUR {result.updated_asset_value_eur:,.2f}",
        f"portfolio state mutation: {result.portfolio_state_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
    ]

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
    parser = argparse.ArgumentParser(description="Record a completed manual buy into local portfolio_state.json.")
    parser.add_argument("--asset", required=True)
    parser.add_argument("--lane", required=True, choices=["crypto", "stock_fund_etf"])
    parser.add_argument("--amount-eur", required=True, type=float)
    parser.add_argument("--execution-date", default=None)
    parser.add_argument("--confirmation-phrase", default="")
    parser.add_argument("--approval-ticket-path", default=DEFAULT_APPROVAL_TICKET_PATH)
    parser.add_argument("--portfolio-state-path", default=DEFAULT_PORTFOLIO_STATE_PATH)
    parser.add_argument("--confirmation-log-path", default=DEFAULT_CONFIRMATION_LOG_PATH)
    parser.add_argument("--write-state", action="store_true")
    args = parser.parse_args(argv)

    result = build_manual_buy_outcome_portfolio_state_recorder_result(
        asset=args.asset,
        lane=args.lane,
        amount_eur=args.amount_eur,
        execution_date=args.execution_date,
        confirmation_phrase=args.confirmation_phrase,
        approval_ticket_path=args.approval_ticket_path,
        portfolio_state_path=args.portfolio_state_path,
        confirmation_log_path=args.confirmation_log_path,
        write_state=args.write_state,
    )
    print(format_manual_buy_outcome_portfolio_state_recorder(result))
    return 0 if result.status == STATUS_READY else 1


if __name__ == "__main__":
    raise SystemExit(main())