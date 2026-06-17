"""J.A.R.V.I.S. v32.0 stock/fund/ETF data freshness engine.

v32 is a read-only data-quality layer for the stock/fund/ETF lane.

The crypto lane is product-connected through v31. The remaining daily warning is
that the ETF universe has no dated metadata and is treated as manually maintained
local scores. v32 turns that warning into a structured freshness/source-quality
gate for the stock/fund/ETF lane.

It does not fetch network data, write tickets, mutate portfolio state, create buy
requests, connect to brokers, create orders, or execute trades.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from .jarvis_v30_0_expanded_crypto_approval_ticket_refresh import DEFAULT_OUTPUT_PATH
from .jarvis_v31_0_approval_ticket_consumption_closeout import (
    ApprovalTicketConsumptionCloseoutResult,
    build_approval_ticket_consumption_closeout_result,
    format_approval_ticket_consumption_closeout,
)

STATUS_READY = "JARVIS_V32_0_STOCK_FUND_ETF_DATA_FRESHNESS_ENGINE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V32_0_STOCK_FUND_ETF_DATA_FRESHNESS_ENGINE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V32_0_STOCK_FUND_ETF_DATA_FRESHNESS_ENGINE_BLOCKED_SAFE"

ENGINE_READY = "STOCK_FUND_ETF_DATA_FRESHNESS_ENGINE_READY"
ENGINE_REVIEW_REQUIRED = "STOCK_FUND_ETF_DATA_FRESHNESS_ENGINE_REVIEW_REQUIRED"
ENGINE_BLOCKED = "STOCK_FUND_ETF_DATA_FRESHNESS_ENGINE_BLOCKED"

NEXT_STAGE = "stock_fund_etf_public_data_source_manifest"

ITEM_READY = "ETF_SOURCE_METADATA_READY"
ITEM_MISSING = "ETF_SOURCE_METADATA_MISSING"
ITEM_STALE = "ETF_SOURCE_METADATA_STALE"
ITEM_INVALID = "ETF_SOURCE_METADATA_INVALID"

DATE_FIELDS = (
    "as_of",
    "updated_at",
    "data_as_of",
    "source_as_of",
    "factsheet_as_of",
    "price_as_of",
    "last_updated",
    "last_updated_at",
)


@dataclass(frozen=True)
class StockFundEtfFreshnessItem:
    candidate_id: str
    selected: bool
    score: float | None
    metadata_date_field: str | None
    metadata_date: str | None
    metadata_age_days: int | None
    freshness_status: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "selected": self.selected,
            "score": self.score,
            "metadata_date_field": self.metadata_date_field,
            "metadata_date": self.metadata_date,
            "metadata_age_days": self.metadata_age_days,
            "freshness_status": self.freshness_status,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class StockFundEtfDataFreshnessEngineResult:
    status: str
    engine_status: str
    recommended_next_stage: str
    current_date: str
    ticket_path: str
    ticket_loaded: bool
    manual_action_result: Any
    selected_stock_fund_etf_candidate: str | None
    selected_stock_fund_etf_amount_eur: float
    etf_candidate_count: int
    metadata_ready_count: int
    metadata_missing_count: int
    metadata_stale_count: int
    selected_candidate_metadata_status: str
    stock_fund_etf_metadata_ready: bool
    stock_fund_etf_metadata_missing_or_stale: bool
    freshness_items: tuple[StockFundEtfFreshnessItem, ...]
    recommendation_quality_current_data: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    portfolio_state_mutation: bool
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
        manual = self.manual_action_result
        return {
            "status": self.status,
            "engine_status": self.engine_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "ticket_path": self.ticket_path,
            "ticket_loaded": self.ticket_loaded,
            "manual_action_result": manual.to_dict() if hasattr(manual, "to_dict") else dict(getattr(manual, "__dict__", {})),
            "selected_stock_fund_etf_candidate": self.selected_stock_fund_etf_candidate,
            "selected_stock_fund_etf_amount_eur": self.selected_stock_fund_etf_amount_eur,
            "etf_candidate_count": self.etf_candidate_count,
            "metadata_ready_count": self.metadata_ready_count,
            "metadata_missing_count": self.metadata_missing_count,
            "metadata_stale_count": self.metadata_stale_count,
            "selected_candidate_metadata_status": self.selected_candidate_metadata_status,
            "stock_fund_etf_metadata_ready": self.stock_fund_etf_metadata_ready,
            "stock_fund_etf_metadata_missing_or_stale": self.stock_fund_etf_metadata_missing_or_stale,
            "freshness_items": [item.to_dict() for item in self.freshness_items],
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "portfolio_state_mutation": self.portfolio_state_mutation,
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


def _dedupe(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    text = str(value).strip()
    if len(text) >= 10:
        text = text[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _today_iso() -> str:
    return date.today().isoformat()


def _resolve_ticket_path(path: str | Path, root: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return Path(root) / candidate


def _is_under_outputs(path: Path, root: str | Path) -> bool:
    resolved = path.resolve()
    outputs_root = (Path(root) / "outputs").resolve()
    try:
        resolved.relative_to(outputs_root)
        return True
    except ValueError:
        return False


def _load_ticket(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _amount(value: Any) -> float:
    return round(float(value or 0.0), 2)


def _candidate_id(record: dict[str, Any]) -> str | None:
    for key in ("candidate_id", "asset", "sleeve_id", "id", "symbol", "ticker", "name"):
        value = record.get(key)
        if value:
            return str(value)
    return None


def _candidate_score(record: dict[str, Any]) -> float | None:
    for key in ("score", "total_score", "etf_score", "rank_score"):
        value = record.get(key)
        if value is not None:
            try:
                return float(value)
            except (TypeError, ValueError):
                return None
    return None


def _date_field(record: dict[str, Any]) -> tuple[str | None, str | None, date | None]:
    for key in DATE_FIELDS:
        value = record.get(key)
        if value:
            parsed = _parse_date(str(value))
            return key, str(value)[:10], parsed
    return None, None, None


def _candidate_records_from_ticket(ticket: dict[str, Any]) -> list[dict[str, Any]]:
    selected = str(ticket.get("selected_stock_fund_etf_candidate") or "")
    records: list[dict[str, Any]] = []

    verdict = ticket.get("etf_scoring_verdict") or {}
    if isinstance(verdict, dict):
        sleeves = verdict.get("sleeves") or verdict.get("ranked_candidates") or []
        if isinstance(sleeves, list):
            for item in sleeves:
                if isinstance(item, dict):
                    records.append(dict(item))

    weekly_dual_lane = ticket.get("weekly_dual_lane_mandate") or {}
    if isinstance(weekly_dual_lane, dict):
        lane = weekly_dual_lane.get("stock_fund_etf_lane") or {}
        if isinstance(lane, dict) and lane.get("asset"):
            lane_record = dict(lane)
            lane_record.setdefault("candidate_id", lane.get("asset"))
            records.append(lane_record)

    if selected and not any(_candidate_id(item) == selected for item in records):
        records.append({"candidate_id": selected, "selected": True})

    deduped: dict[str, dict[str, Any]] = {}
    for record in records:
        cid = _candidate_id(record)
        if not cid:
            continue
        if cid not in deduped:
            deduped[cid] = dict(record)
        else:
            deduped[cid].update({key: value for key, value in record.items() if value is not None})
        if cid == selected:
            deduped[cid]["selected"] = True

    return list(deduped.values())


def _build_freshness_items(
    *,
    ticket: dict[str, Any],
    current_date_text: str,
    max_age_days: int,
) -> tuple[StockFundEtfFreshnessItem, ...]:
    current = _parse_date(current_date_text) or date.today()
    selected = str(ticket.get("selected_stock_fund_etf_candidate") or "")
    items: list[StockFundEtfFreshnessItem] = []

    for record in _candidate_records_from_ticket(ticket):
        cid = _candidate_id(record)
        if not cid:
            continue
        field, date_text, parsed = _date_field(record)
        warnings: list[str] = []
        blockers: list[str] = []
        age_days: int | None = None

        if not field:
            status = ITEM_MISSING
            warnings.append(f"{cid} has no dated source metadata field such as as_of or updated_at.")
        elif parsed is None:
            status = ITEM_INVALID
            warnings.append(f"{cid} has invalid dated source metadata in field {field}.")
        else:
            age_days = max(0, (current - parsed).days)
            if age_days > max_age_days:
                status = ITEM_STALE
                warnings.append(f"{cid} stock/fund/ETF data is {age_days} days old; refresh required.")
            else:
                status = ITEM_READY

        items.append(
            StockFundEtfFreshnessItem(
                candidate_id=cid,
                selected=bool(record.get("selected") or cid == selected),
                score=_candidate_score(record),
                metadata_date_field=field,
                metadata_date=date_text,
                metadata_age_days=age_days,
                freshness_status=status,
                blockers=tuple(blockers),
                warnings=tuple(warnings),
            )
        )

    return tuple(items)


def build_stock_fund_etf_data_freshness_engine_result(
    *,
    current_date: str | None = None,
    ticket_path: str | Path = DEFAULT_OUTPUT_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    manual_action_result: ApprovalTicketConsumptionCloseoutResult | None = None,
    manual_action_builder: Callable[..., ApprovalTicketConsumptionCloseoutResult] = build_approval_ticket_consumption_closeout_result,
    write_local_signals: bool = False,
) -> StockFundEtfDataFreshnessEngineResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")
    if max_age_days < 0:
        blockers.append("max_age_days must be non-negative.")

    resolved_ticket = _resolve_ticket_path(ticket_path, root)
    if not _is_under_outputs(resolved_ticket, root):
        blockers.append("approval ticket path must remain under outputs/.")

    ticket: dict[str, Any] = {}
    ticket_loaded = False
    if not blockers:
        if not resolved_ticket.exists():
            warnings.append("approval ticket is missing; stock/fund/ETF freshness cannot be checked.")
        else:
            ticket = _load_ticket(resolved_ticket)
            ticket_loaded = True

    manual = None
    if not blockers:
        manual = manual_action_result if manual_action_result is not None else manual_action_builder(
            current_date=current_date_text,
            ticket_path=ticket_path,
            root=root,
            write_local_signals=write_local_signals,
        )
        blockers.extend(getattr(manual, "blockers", ()) or [])
        warnings.extend(getattr(manual, "warnings", ()) or [])

    freshness_items = _build_freshness_items(
        ticket=ticket,
        current_date_text=current_date_text,
        max_age_days=max_age_days,
    ) if ticket else tuple()

    if not freshness_items:
        warnings.append("No stock/fund/ETF candidate records found in approval ticket.")

    metadata_ready_count = sum(1 for item in freshness_items if item.freshness_status == ITEM_READY)
    metadata_missing_count = sum(1 for item in freshness_items if item.freshness_status in {ITEM_MISSING, ITEM_INVALID})
    metadata_stale_count = sum(1 for item in freshness_items if item.freshness_status == ITEM_STALE)
    selected_item = next((item for item in freshness_items if item.selected), None)
    selected_status = selected_item.freshness_status if selected_item else ITEM_MISSING

    for item in freshness_items:
        warnings.extend(item.warnings)
        blockers.extend(item.blockers)

    if selected_item is None:
        warnings.append("Selected stock/fund/ETF candidate is missing from freshness candidate records.")

    stock_metadata_ready = bool(
        freshness_items
        and metadata_missing_count == 0
        and metadata_stale_count == 0
        and selected_status == ITEM_READY
    )
    missing_or_stale = not stock_metadata_ready

    if missing_or_stale:
        warnings.append("Stock/fund/ETF lane has missing or stale dated source metadata.")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    manual_status = str(getattr(manual, "status", "")) if manual is not None else ""
    manual_requires_review = "REVIEW_REQUIRED" in manual_status
    manual_blocked = "BLOCKED" in manual_status

    if unique_blockers or manual_blocked:
        status = STATUS_BLOCKED
        engine_status = ENGINE_BLOCKED
    elif unique_warnings or manual_requires_review or missing_or_stale:
        status = STATUS_REVIEW_REQUIRED
        engine_status = ENGINE_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        engine_status = ENGINE_READY

    return StockFundEtfDataFreshnessEngineResult(
        status=status,
        engine_status=engine_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        ticket_path=str(resolved_ticket),
        ticket_loaded=ticket_loaded,
        manual_action_result=manual,
        selected_stock_fund_etf_candidate=ticket.get("selected_stock_fund_etf_candidate") if ticket else None,
        selected_stock_fund_etf_amount_eur=_amount(ticket.get("selected_stock_fund_etf_amount_eur")) if ticket else 0.0,
        etf_candidate_count=len(freshness_items),
        metadata_ready_count=metadata_ready_count,
        metadata_missing_count=metadata_missing_count,
        metadata_stale_count=metadata_stale_count,
        selected_candidate_metadata_status=selected_status,
        stock_fund_etf_metadata_ready=stock_metadata_ready,
        stock_fund_etf_metadata_missing_or_stale=missing_or_stale,
        freshness_items=freshness_items,
        recommendation_quality_current_data=False,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        portfolio_state_mutation=False,
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


def _format_freshness_items(result: StockFundEtfDataFreshnessEngineResult) -> str:
    lines = ["Stock/Fund/ETF freshness candidates:"]
    for item in result.freshness_items:
        selected = "SELECTED" if item.selected else "not selected"
        score = f"{item.score:,.2f}" if item.score is not None else "unknown"
        age = f"{item.metadata_age_days} days" if item.metadata_age_days is not None else "unknown"
        lines.append(
            f"- {item.candidate_id}: {item.freshness_status}; {selected}; score {score}; "
            f"metadata {item.metadata_date_field or 'none'}={item.metadata_date or 'none'}; age {age}"
        )
        for warning in item.warnings:
            lines.append(f"  warning: {warning}")
    return "\n".join(lines)


def _manual_action_console_output(manual_action_result: Any) -> str:
    required_attrs = ("closeout_status", "ticket_loaded", "selected_crypto_candidate")
    if all(hasattr(manual_action_result, attr) for attr in required_attrs):
        return format_approval_ticket_consumption_closeout(manual_action_result)

    blockers = getattr(manual_action_result, "blockers", ()) or ()
    warnings = getattr(manual_action_result, "warnings", ()) or ()
    return "\n".join(
        [
            "J.A.R.V.I.S. Daily Manual Action Brief",
            f"status: {getattr(manual_action_result, 'status', 'unknown')}",
            "ticket loaded: unknown",
            "ticket matches current preview: unknown",
            "Current refreshed approval ticket:",
            "- Crypto lane manual buy candidate: unknown EUR 0.00",
            "- Stock/Fund/ETF lane manual buy candidate: unknown EUR 0.00",
            "- Final real-world buy remains manual outside J.A.R.V.I.S.",
            "no broker connection",
            "no credentials",
            "no private account data ingestion",
            "no orders created",
            "no trades executed",
            f"blockers: {', '.join(str(item) for item in blockers) if blockers else 'none'}",
            f"warnings: {', '.join(str(item) for item in warnings) if warnings else 'none'}",
        ]
    )


def format_stock_fund_etf_data_freshness_engine(
    result: StockFundEtfDataFreshnessEngineResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Stock/Fund/ETF Data Freshness Engine",
        f"status: {result.status}",
        f"engine status: {result.engine_status}",
        f"current date: {result.current_date}",
        f"ticket path: {result.ticket_path}",
        f"ticket loaded: {result.ticket_loaded}",
        f"selected stock/fund/ETF candidate: {result.selected_stock_fund_etf_candidate or 'none'}",
        f"selected stock/fund/ETF amount: EUR {result.selected_stock_fund_etf_amount_eur:,.2f}",
        f"ETF candidate count: {result.etf_candidate_count}",
        f"metadata ready count: {result.metadata_ready_count}",
        f"metadata missing count: {result.metadata_missing_count}",
        f"metadata stale count: {result.metadata_stale_count}",
        f"selected candidate metadata status: {result.selected_candidate_metadata_status}",
        f"stock/fund/ETF metadata ready: {result.stock_fund_etf_metadata_ready}",
        f"stock/fund/ETF metadata missing or stale: {result.stock_fund_etf_metadata_missing_or_stale}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"portfolio state mutation: {result.portfolio_state_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
        "",
        _format_freshness_items(result),
        "",
        "Daily manual action brief:",
        _manual_action_console_output(result.manual_action_result) if result.manual_action_result is not None else "none",
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
    parser = argparse.ArgumentParser(description="Check stock/fund/ETF lane dated metadata freshness.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run stock/fund/ETF freshness checks.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--ticket-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    parser.add_argument("--write-local-signals", action="store_true", help="Write normalized local public crypto signals while building the manual brief preview.")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    if args.voice_command:
        print(build_safety_check_console_output(args.voice_command))
        return 0

    if args.demo:
        print("Available typed Jarvis commands:")
        for command in DEFAULT_COMMAND_SAMPLES:
            print(f"- {command}")
        return 0

    result = build_stock_fund_etf_data_freshness_engine_result(
        current_date=args.current_date,
        ticket_path=args.ticket_path,
        max_age_days=args.max_age_days,
        write_local_signals=args.write_local_signals,
    )
    print(format_stock_fund_etf_data_freshness_engine(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())