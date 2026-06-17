"""J.A.R.V.I.S. v83.0 data freshness acquisition gate.

Checks whether available local/public evidence is fresh enough to allow the
future dynamic allocator. This module does not fetch data, approve buys,
connect brokers, create orders, or trade.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.correlation_risk_model import build_correlation_risk_model_result
from jarvis.runtime.stock_specific_public_evidence import build_stock_specific_public_evidence_result
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V83_0_DATA_FRESHNESS_ACQUISITION_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V83_0_DATA_FRESHNESS_ACQUISITION_GATE_REVIEW_REQUIRED_SAFE"

DEFAULT_CACHE_PATH = "jarvis/local/free_research_api_cache.local.json"
DEFAULT_EVIDENCE_PACK_PATH = "outputs/free_research_evidence_pack_latest.json"
DEFAULT_APPROVAL_TICKET_PATH = "outputs/approval_ticket_latest.json"
DEFAULT_COST_BASIS_PATH = "jarvis/local/manual_cost_basis.local.json"
DEFAULT_EXPENSES_PATH = "jarvis/local/monthly_expenses.local.json"
DEFAULT_OUTPUT_PATH = "outputs/data_freshness_acquisition_gate_latest.json"


@dataclass(frozen=True)
class DataFreshnessAcquisitionGateResult:
    status: str
    current_date: str
    freshness_gate_ready: bool
    dynamic_allocator_allowed: bool
    crypto_data_fresh: bool
    fx_data_fresh: bool
    etf_fund_data_fresh: bool
    stock_data_fresh: bool
    portfolio_data_fresh: bool
    monthly_expenses_data_fresh: bool
    evidence_summary: dict[str, Any]
    missing_freshness: list[str]
    warnings: list[str]
    blockers: list[str]
    safety_check_blocked_execution: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection: bool
    credentials_used: bool
    private_account_data_ingestion: bool
    order_created: bool
    trade_executed: bool
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_json(path: str | Path) -> Any | None:
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8-sig"))
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


def _text(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str).lower()


def _has_usable_lane(rows: list[dict[str, Any]], lane_terms: list[str], ready_terms: list[str]) -> bool:
    for row in rows:
        joined = _text(row)
        if any(term in joined for term in lane_terms) and any(term in joined for term in ready_terms):
            return True
    return False


def _has_positive_number(rows: list[dict[str, Any]], keys: list[str]) -> bool:
    for row in rows:
        for key in keys:
            value = row.get(key)
            if isinstance(value, bool) or value is None:
                continue
            try:
                if float(value) > 0:
                    return True
            except (TypeError, ValueError):
                pass
    return False


def _stock_has_symbol_price_and_as_of(rows: list[dict[str, Any]]) -> tuple[bool, bool, bool]:
    has_symbol = False
    has_price = False
    has_as_of = False

    for row in rows:
        joined = _text(row)
        if "msft" in joined or "microsoft" in joined or "stock" in joined:
            if any(row.get(k) for k in ("symbol", "ticker", "stock_symbol", "instrument_symbol")) or "msft" in joined:
                has_symbol = True
            if _has_positive_number([row], ["price", "public_price", "close_price", "last_price", "market_price"]):
                has_price = True
            if any(row.get(k) for k in ("as_of", "date", "timestamp", "quote_as_of")):
                has_as_of = True

    return has_symbol, has_price, has_as_of


def build_data_freshness_acquisition_gate_result(
    *,
    current_date: str = "2026-06-18",
    cache_path: str | Path = DEFAULT_CACHE_PATH,
    evidence_pack_path: str | Path = DEFAULT_EVIDENCE_PACK_PATH,
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    cost_basis_path: str | Path = DEFAULT_COST_BASIS_PATH,
    expenses_path: str | Path = DEFAULT_EXPENSES_PATH,
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> DataFreshnessAcquisitionGateResult:
    cache = _load_json(cache_path)
    evidence_pack = _load_json(evidence_pack_path)
    approval_ticket = _load_json(approval_ticket_path)
    cost_basis = _load_json(cost_basis_path)
    expenses = _load_json(expenses_path)

    evidence_rows = _walk(cache) + _walk(evidence_pack)
    ticket_rows = _walk(approval_ticket)
    cost_rows = _walk(cost_basis)
    expense_rows = _walk(expenses)

    ready_terms = ["ready", "usable", "true", "official_free_source_ready", "public_crypto_source_ready"]

    crypto_fresh = _has_usable_lane(evidence_rows, ["crypto", "coingecko", "coin"], ready_terms)
    fx_fresh = _has_usable_lane(evidence_rows, ["fx", "ecb", "eur_usd"], ready_terms)

    etf_fresh = _has_usable_lane(evidence_rows + ticket_rows, ["etf", "fund", "is3q", "sxr8", "iemm"], ready_terms)
    if not etf_fresh:
        etf_fresh = fx_fresh and ("is3q" in _text(approval_ticket) or "etf" in _text(approval_ticket))

    stock_evidence = build_stock_specific_public_evidence_result(
        current_date=current_date,
        approval_ticket_path=approval_ticket_path,
    )
    stock_symbol = bool(stock_evidence.top_stock_symbol)
    stock_price = stock_evidence.public_price is not None
    stock_as_of = bool(stock_evidence.public_as_of)
    stock_fresh = stock_symbol and stock_price and stock_as_of

    correlation_result = build_correlation_risk_model_result(
        current_date=current_date,
        cost_basis_path=cost_basis_path,
    )
    portfolio_fresh = correlation_result.correlation_model_ready or _has_positive_number(
        cost_rows,
        [
            "market_value_eur",
            "current_value_eur",
            "value_eur",
            "market_value",
            "current_value",
            "cost_basis_eur",
            "cost_eur",
            "cost",
        ],
    )
    expenses_fresh = _has_positive_number(
        expense_rows,
        ["planned_monthly_contribution_eur", "normal_monthly_expenses_eur", "survival_monthly_expenses_eur"],
    )

    missing: list[str] = []
    if not crypto_fresh:
        missing.append("crypto_data_freshness")
    if not fx_fresh:
        missing.append("fx_data_freshness")
    if not etf_fresh:
        missing.append("etf_fund_data_freshness")
    if not stock_fresh:
        missing.append("stock_data_freshness_with_as_of")
    if not portfolio_fresh:
        missing.append("portfolio_cost_basis_freshness")
    if not expenses_fresh:
        missing.append("monthly_expenses_freshness")

    safety_output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output

    blockers = list(missing)
    if not safety_blocked:
        blockers.append("safety_check_did_not_block_execution")

    ready = not blockers

    warnings = [
        "this gate only checks available local/public evidence; it does not fetch missing provider data",
        "dynamic allocation remains blocked unless every freshness lane is ready",
    ]
    if stock_symbol and stock_price and not stock_as_of:
        warnings.append("stock symbol and price exist, but stock freshness timestamp/as_of is missing")

    result = DataFreshnessAcquisitionGateResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        freshness_gate_ready=ready,
        dynamic_allocator_allowed=ready,
        crypto_data_fresh=crypto_fresh,
        fx_data_fresh=fx_fresh,
        etf_fund_data_fresh=etf_fresh,
        stock_data_fresh=stock_fresh,
        portfolio_data_fresh=portfolio_fresh,
        monthly_expenses_data_fresh=expenses_fresh,
        evidence_summary={
            "cache_path": str(cache_path),
            "evidence_pack_path": str(evidence_pack_path),
            "approval_ticket_path": str(approval_ticket_path),
            "cost_basis_path": str(cost_basis_path),
            "expenses_path": str(expenses_path),
            "evidence_row_count": len(evidence_rows),
            "approval_ticket_row_count": len(ticket_rows),
            "cost_basis_row_count": len(cost_rows),
            "expense_row_count": len(expense_rows),
            "stock_symbol_found": stock_symbol,
            "stock_price_found": stock_price,
            "stock_as_of_found": stock_as_of,
        },
        missing_freshness=missing,
        warnings=warnings,
        blockers=blockers,
        safety_check_blocked_execution=safety_blocked,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection=False,
        credentials_used=False,
        private_account_data_ingestion=False,
        order_created=False,
        trade_executed=False,
        report_written=False,
        report_path=str(output_path),
    )

    if write_report:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        payload["report_written"] = True
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = DataFreshnessAcquisitionGateResult(**payload)

    return result


def format_data_freshness_acquisition_gate(result: DataFreshnessAcquisitionGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. DATA FRESHNESS ACQUISITION GATE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"freshness gate ready: {result.freshness_gate_ready}",
        f"dynamic allocator allowed: {result.dynamic_allocator_allowed}",
        "freshness lanes:",
        f"- crypto data fresh: {result.crypto_data_fresh}",
        f"- FX data fresh: {result.fx_data_fresh}",
        f"- ETF/fund data fresh: {result.etf_fund_data_fresh}",
        f"- stock data fresh: {result.stock_data_fresh}",
        f"- portfolio data fresh: {result.portfolio_data_fresh}",
        f"- monthly expenses data fresh: {result.monthly_expenses_data_fresh}",
        "missing freshness:",
    ]
    lines.extend(f"- {item}" for item in result.missing_freshness or ["none"])
    lines.append("warnings:")
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.extend(
        [
            "Safety:",
            "- manual approval required: True",
            "- execution forbidden: True",
            f"- safety-check blocked execution: {result.safety_check_blocked_execution}",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
            f"- buy request created: {result.buy_request_created}",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            "blockers:",
        ]
    )
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. data freshness acquisition gate.")
    parser.add_argument("--data-freshness-acquisition-gate", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--cache-path", default=DEFAULT_CACHE_PATH)
    parser.add_argument("--evidence-pack-path", default=DEFAULT_EVIDENCE_PACK_PATH)
    parser.add_argument("--approval-ticket-path", default=DEFAULT_APPROVAL_TICKET_PATH)
    parser.add_argument("--cost-basis-path", default=DEFAULT_COST_BASIS_PATH)
    parser.add_argument("--expenses-path", default=DEFAULT_EXPENSES_PATH)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_data_freshness_acquisition_gate_result(
        current_date=args.current_date,
        cache_path=args.cache_path,
        evidence_pack_path=args.evidence_pack_path,
        approval_ticket_path=args.approval_ticket_path,
        cost_basis_path=args.cost_basis_path,
        expenses_path=args.expenses_path,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_data_freshness_acquisition_gate(result))
    return 0 if not result.blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
