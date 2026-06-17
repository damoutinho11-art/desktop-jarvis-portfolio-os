"""J.A.R.V.I.S. v82.0 stock-specific public evidence gate.

Reads existing local/public stock artifacts and decides whether the top stock
candidate has enough public evidence for manual review. No approval, no order,
no trade, no broker, no credentials.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V82_0_STOCK_SPECIFIC_PUBLIC_EVIDENCE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V82_0_STOCK_SPECIFIC_PUBLIC_EVIDENCE_REVIEW_REQUIRED_SAFE"
EVIDENCE_READY = "STOCK_SPECIFIC_PUBLIC_EVIDENCE_READY"
EVIDENCE_REVIEW_REQUIRED = "STOCK_SPECIFIC_PUBLIC_EVIDENCE_REVIEW_REQUIRED"

DEFAULT_APPROVAL_TICKET_PATH = "outputs/approval_ticket_latest.json"
DEFAULT_RANKED_CANDIDATES_PATH = "jarvis/local/individual_stock_ranked_candidates.local.json"
DEFAULT_STOCK_SIGNALS_PATH = "jarvis/local/individual_stock_signals.local.json"
DEFAULT_OUTPUT_PATH = "outputs/stock_specific_public_evidence_latest.json"


@dataclass(frozen=True)
class StockSpecificPublicEvidenceResult:
    status: str
    evidence_status: str
    current_date: str
    stock_specific_public_evidence_ready: bool
    top_stock_symbol: str | None
    top_stock_name: str | None
    public_price: float | None
    public_currency: str | None
    public_as_of: str | None
    public_source_ready: bool
    evidence_items: list[dict[str, Any]]
    evidence_quality: str
    stock_review_allowed: bool
    approved_for_purchase: bool
    manual_amount_required: bool
    remaining_full_allocation_blockers: list[str]
    safety_check_blocked_execution: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection: bool
    credentials_used: bool
    private_account_data_ingestion: bool
    order_created: bool
    trade_executed: bool
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _walk(value: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, Mapping):
        rows.append(dict(value))
        for child in value.values():
            rows.extend(_walk(child))
    elif isinstance(value, list):
        for child in value:
            rows.extend(_walk(child))
    return rows


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _first_text(row: Mapping[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def _extract_stock_rows(payloads: list[Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    for payload in payloads:
        for row in _walk(payload):
            symbol = _first_text(row, ("symbol", "ticker", "instrument_symbol", "stock_symbol"))
            name = _first_text(row, ("name", "asset_name", "instrument_name", "company_name", "id"))
            price = None
            for key in ("close_price", "price", "last_price", "market_price", "public_price"):
                price = _as_float(row.get(key))
                if price is not None:
                    break

            text = " ".join(str(row.get(k, "")) for k in row.keys()).upper()
            looks_like_stock = bool(symbol) and (
                symbol.upper() in text
                or "MSFT" in text
                or "STOCK" in text
                or "EQUITY" in text
                or "PUBLIC" in text
            )

            if not looks_like_stock:
                continue

            if symbol:
                rows.append(
                    {
                        "symbol": symbol.upper(),
                        "name": name,
                        "price": price,
                        "currency": _first_text(row, ("currency", "price_currency", "quote_currency")) or "USD",
                        "as_of": _first_text(row, ("as_of", "date", "timestamp", "quote_as_of")),
                        "source": _first_text(row, ("source", "provider", "public_source", "data_source")) or "local_public_stock_artifact",
                    }
                )

    deduped: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = row["symbol"]
        old = deduped.get(symbol)
        if old is None or (old.get("price") is None and row.get("price") is not None):
            deduped[symbol] = row

    return list(deduped.values())


def build_stock_specific_public_evidence_result(
    *,
    current_date: str = "2026-06-17",
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    ranked_candidates_path: str | Path = DEFAULT_RANKED_CANDIDATES_PATH,
    stock_signals_path: str | Path = DEFAULT_STOCK_SIGNALS_PATH,
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> StockSpecificPublicEvidenceResult:
    payloads = [
        _load_json(Path(ranked_candidates_path)),
        _load_json(Path(stock_signals_path)),
        _load_json(Path(approval_ticket_path)),
    ]
    rows = _extract_stock_rows(payloads)

    top = rows[0] if rows else None
    symbol = top.get("symbol") if top else None
    name = top.get("name") if top else None
    price = top.get("price") if top else None
    currency = top.get("currency") if top else None
    as_of = top.get("as_of") if top else None

    evidence_items: list[dict[str, Any]] = []
    if top:
        evidence_items.append(
            {
                "kind": "public_stock_quote_or_ranked_candidate",
                "symbol": symbol,
                "name": name,
                "price": price,
                "currency": currency,
                "as_of": as_of,
                "source": top.get("source"),
                "usable": bool(symbol and price),
            }
        )

    safety_output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output

    blockers: list[str] = []
    if not symbol:
        blockers.append("missing top stock symbol")
    if price is None:
        blockers.append("missing public stock price")
    if not safety_blocked:
        blockers.append("safety-check did not block execution")

    ready = not blockers

    result = StockSpecificPublicEvidenceResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        evidence_status=EVIDENCE_READY if ready else EVIDENCE_REVIEW_REQUIRED,
        current_date=current_date,
        stock_specific_public_evidence_ready=ready,
        top_stock_symbol=symbol,
        top_stock_name=name,
        public_price=round(float(price), 4) if price is not None else None,
        public_currency=currency,
        public_as_of=as_of,
        public_source_ready=ready,
        evidence_items=evidence_items,
        evidence_quality="CURRENT_PUBLIC_PRICE_AVAILABLE" if ready else "REVIEW_REQUIRED",
        stock_review_allowed=ready,
        approved_for_purchase=False,
        manual_amount_required=True,
        remaining_full_allocation_blockers=[] if ready else ["stock_specific_public_evidence"],
        safety_check_blocked_execution=safety_blocked,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection=False,
        credentials_used=False,
        private_account_data_ingestion=False,
        order_created=False,
        trade_executed=False,
        warnings=[
            "stock evidence is for manual review only",
            "v82 does not allocate money to individual stocks; v83 allocator decides sizing",
        ],
        blockers=blockers,
        report_written=False,
        report_path=str(output_path),
    )

    if write_report:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        payload["report_written"] = True
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = StockSpecificPublicEvidenceResult(**payload)

    return result


def format_stock_specific_public_evidence(result: StockSpecificPublicEvidenceResult) -> str:
    lines = [
        "J.A.R.V.I.S. STOCK-SPECIFIC PUBLIC EVIDENCE",
        f"status: {result.status}",
        f"evidence status: {result.evidence_status}",
        f"current date: {result.current_date}",
        f"stock-specific public evidence ready: {result.stock_specific_public_evidence_ready}",
        f"top stock symbol: {result.top_stock_symbol}",
        f"top stock name: {result.top_stock_name}",
        f"public price: {result.public_price}",
        f"public currency: {result.public_currency}",
        f"public as of: {result.public_as_of}",
        f"evidence quality: {result.evidence_quality}",
        f"stock review allowed: {result.stock_review_allowed}",
        f"approved for purchase: {result.approved_for_purchase}",
        f"manual amount required: {result.manual_amount_required}",
        "remaining full-allocation blockers:",
    ]
    lines.extend(f"- {item}" for item in result.remaining_full_allocation_blockers or ["none"])

    lines.extend(
        [
            "Safety:",
            "- manual approval required: True",
            "- execution forbidden: True",
            f"- safety-check blocked execution: {result.safety_check_blocked_execution}",
            f"- buy request created: {result.buy_request_created}",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            "blockers:",
        ]
    )
    lines.extend(f"- {blocker}" for blocker in result.blockers or ["none"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. stock-specific public evidence gate.")
    parser.add_argument("--stock-specific-public-evidence", action="store_true")
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--approval-ticket-path", default=DEFAULT_APPROVAL_TICKET_PATH)
    parser.add_argument("--ranked-candidates-path", default=DEFAULT_RANKED_CANDIDATES_PATH)
    parser.add_argument("--stock-signals-path", default=DEFAULT_STOCK_SIGNALS_PATH)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_stock_specific_public_evidence_result(
        current_date=args.current_date,
        approval_ticket_path=args.approval_ticket_path,
        ranked_candidates_path=args.ranked_candidates_path,
        stock_signals_path=args.stock_signals_path,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_stock_specific_public_evidence(result))
    return 0 if not result.blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
