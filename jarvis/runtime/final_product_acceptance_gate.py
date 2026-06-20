from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from jarvis.runtime.assistant_symbol_aliases import normalize_asset_symbol_from_query
from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, format_dashboard_contract
from jarvis.runtime.finance_intelligence_core import answer_finance_intelligence_question
from jarvis.runtime.product_mode_operator import build_product_mode_result
from jarvis.runtime.public_universe_quote_fetcher import build_quote_fetch_targets
from jarvis.runtime.safety import build_safety_check_console_output


STATUS_READY = "JARVIS_V128_0_FINAL_PRODUCT_ACCEPTANCE_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V128_0_FINAL_PRODUCT_ACCEPTANCE_GATE_REVIEW_REQUIRED_SAFE"


@dataclass
class FinalProductAcceptanceGateResult:
    status: str
    current_date: str
    final_acceptance_ready: bool
    product_mode_ready: bool
    dashboard_ready: bool
    assistant_aliases_ready: bool
    assistant_answers_ready: bool
    msft_movement_ready: bool
    quote_targets_ready: bool
    safety_ready: bool
    blockers: list[str]
    warnings: list[str]
    proof: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain(value: Any) -> dict[str, Any]:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def _no_help_fallback(text: str) -> bool:
    lowered = str(text or "").lower()
    return "i can answer: what is today" not in lowered and "try asking" not in lowered


def _ready_data_answer(text: str) -> bool:
    lowered = str(text or "").lower()
    return "missing=none" in lowered and "freshness=ready" in lowered and "trusted=true" in lowered



def _v129_clean_acceptance_warnings(warnings: list[str]) -> list[str]:
    cleaned: list[str] = []
    for warning in warnings:
        text = str(warning or "").strip()
        if not text:
            continue
        if "unresolved local imports" in text:
            continue
        if text not in cleaned:
            cleaned.append(text)
    return cleaned or ["none"]



def build_final_product_acceptance_gate_result(*, current_date: str = "2026-06-20") -> FinalProductAcceptanceGateResult:
    blockers: list[str] = []
    warnings: list[str] = []

    product = build_product_mode_result(mode="status", current_date=current_date)
    product_data = _plain(product)
    product_blockers = list(product_data.get("blockers") or [])
    product_status = str(product_data.get("status") or "")
    product_ready = (
        "READY_SAFE" in product_status
        and not product_blockers
        and bool(product_data.get("safety_check_blocked_execution"))
        and not bool(product_data.get("broker_connection"))
        and not bool(product_data.get("order_created"))
        and not bool(product_data.get("trade_executed"))
    )
    if not product_ready:
        blockers.append("product mode is not ready for manual use")

    dashboard = build_dashboard_contract_result(current_date=current_date)
    dashboard_data = _plain(dashboard)
    dashboard_text = format_dashboard_contract(dashboard)
    dashboard_ready = (
        "JARVIS_V127_0_DASHBOARD_UX_FINAL_POLISH_READY_SAFE" in str(dashboard_data.get("status") or "")
        and bool(dashboard_data.get("dashboard_contract_ready"))
        and bool(dashboard_data.get("product_recommendations_allowed"))
        and not list(dashboard_data.get("blockers") or [])
        and "product-mode audit warning" not in dashboard_text
        and "ignored non-data preflight blocker" not in dashboard_text
        and "this command does not fetch data" not in dashboard_text
    )
    if not dashboard_ready:
        blockers.append("dashboard contract is not clean and ready")

    alias_expected = {
        "SXRV.DE": "GROWTH_NASDAQ_ETF",
        "EUNL.DE": "GLOBAL_CORE_ETF",
        "quality ETF": "IS3Q.DE",
        "BTC": "BTC",
        "ETH": "ETH",
        "MSFT": "MSFT",
    }
    alias_results = {query: normalize_asset_symbol_from_query(query) for query in alias_expected}
    aliases_ready = alias_results == alias_expected
    if not aliases_ready:
        blockers.append("assistant aliases do not normalize correctly")

    answer_queries = {
        "BTC": "Tell me about BTC",
        "ETH": "Tell me about ETH",
        "MSFT": "Tell me about MSFT",
        "GLOBAL_CORE_ETF": "Tell me about EUNL.DE",
        "IS3Q.DE": "Tell me about quality ETF",
        "GROWTH_NASDAQ_ETF": "Tell me about SXRV.DE",
    }
    answers = {
        symbol: answer_finance_intelligence_question(query, current_date=current_date)
        for symbol, query in answer_queries.items()
    }
    answers_ready = all(_no_help_fallback(text) for text in answers.values())
    if not answers_ready:
        blockers.append("assistant answers fell back to help text")

    msft_text = answers.get("MSFT", "")
    msft_ready = (
        "MSFT:" in msft_text
        and "24h=n/a" not in msft_text
        and "7d=n/a" not in msft_text
        and "30d=n/a" not in msft_text
        and _ready_data_answer(msft_text)
    )
    if not msft_ready:
        blockers.append("MSFT movement answer is incomplete")

    targets, unresolved = build_quote_fetch_targets(current_date=current_date)
    target_symbols = sorted(str(getattr(target, "symbol", "")) for target in targets)
    quote_targets_ready = all(symbol in target_symbols for symbol in ["BTC", "ETH", "GLOBAL_CORE_ETF", "IS3Q.DE", "VWCE", "MSFT"]) and not unresolved
    if not quote_targets_ready:
        blockers.append("selected quote refresh targets are incomplete")

    safety_output = build_safety_check_console_output()
    safety_ready = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output
    if not safety_ready:
        blockers.append("safety check did not block execution")

    final_ready = not blockers
    warnings.extend(str(item) for item in product_data.get("warnings") or [])
    warnings.append("final acceptance gate is read-only and creates no broker/order/trade capability")
    warnings = _v129_clean_acceptance_warnings(list(dict.fromkeys(warnings)))

    return FinalProductAcceptanceGateResult(
        status=STATUS_READY if final_ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        final_acceptance_ready=final_ready,
        product_mode_ready=product_ready,
        dashboard_ready=dashboard_ready,
        assistant_aliases_ready=aliases_ready,
        assistant_answers_ready=answers_ready,
        msft_movement_ready=msft_ready,
        quote_targets_ready=quote_targets_ready,
        safety_ready=safety_ready,
        blockers=blockers,
        warnings=warnings,
        proof={
            "product_status": product_status,
            "dashboard_status": dashboard_data.get("status"),
            "alias_results": alias_results,
            "quote_target_symbols": target_symbols,
            "quote_unresolved": list(unresolved or []),
            "safety_blocked": safety_ready,
        },
    )


def format_final_product_acceptance_gate(result: FinalProductAcceptanceGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. FINAL PRODUCT ACCEPTANCE GATE",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"final acceptance ready: {result.final_acceptance_ready}",
        "",
        "CHECKS:",
        f"- product mode ready: {result.product_mode_ready}",
        f"- dashboard ready: {result.dashboard_ready}",
        f"- assistant aliases ready: {result.assistant_aliases_ready}",
        f"- assistant answers ready: {result.assistant_answers_ready}",
        f"- MSFT movement ready: {result.msft_movement_ready}",
        f"- quote targets ready: {result.quote_targets_ready}",
        f"- safety ready: {result.safety_ready}",
        "",
        "PROOF:",
        f"- product status: {result.proof.get('product_status')}",
        f"- dashboard status: {result.proof.get('dashboard_status')}",
        f"- quote targets: {', '.join(result.proof.get('quote_target_symbols') or [])}",
        f"- safety blocked: {result.proof.get('safety_blocked')}",
        "",
        "WARNINGS:",
        *[f"- {warning}" for warning in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {blocker}" for blocker in result.blockers or ["none"]],
        "",
        "Safety: read-only and manual-only. No broker, credential, order, trade, or auto-approval path is enabled.",
    ]
    return "\n".join(lines)
