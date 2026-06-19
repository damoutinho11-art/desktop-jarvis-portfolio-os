from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.dashboard_contract import build_dashboard_contract_result

STATUS_READY = "JARVIS_V102_0_CHAT_INTERFACE_CONTRACT_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V102_0_CHAT_INTERFACE_CONTRACT_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/chat_interface_contract_latest.json"

SUPPORTED_INTENTS = [
    "today_plan",
    "instrument_rationale",
    "safety",
    "blockers",
    "dashboard",
    "help",
]


@dataclass(frozen=True)
class ChatInterfaceContractResult:
    status: str
    current_date: str
    chat_contract_ready: bool
    query: str
    detected_intent: str
    response: str
    supported_intents: list[str]
    manual_only: bool
    dashboard_path: str
    open_dashboard_command: str
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _money(value: Any) -> str:
    try:
        return f"EUR {float(value or 0.0):.2f}"
    except Exception:
        return "EUR 0.00"


def _open_dashboard_command(path: str) -> str:
    backslash = chr(92)
    normalized = str(path).replace("/", backslash).lstrip(".\\/")
    return f"start .{backslash}{normalized}"


def _detect_intent(query: str) -> str:
    normalized = query.lower().strip()

    if not normalized:
        return "help"

    if any(word in normalized for word in ["today", "plan", "buy", "week", "allocation"]):
        return "today_plan"

    if any(word in normalized for word in ["why", "rationale", "reason", "btc", "eth", "msft", "instrument"]):
        return "instrument_rationale"

    if any(word in normalized for word in ["safe", "safety", "trade", "broker", "order", "credential", "execute"]):
        return "safety"

    if any(word in normalized for word in ["blocker", "blocked", "problem", "issue", "warning"]):
        return "blockers"

    if any(word in normalized for word in ["dashboard", "open", "html", "file"]):
        return "dashboard"

    return "help"


def _selected_summary(selections: list[dict[str, Any]], lane: str) -> str:
    items = [
        f"{item.get('symbol', '')} {_money(item.get('amount_eur'))}"
        for item in selections
        if str(item.get("lane", "")) == lane
    ]
    return ", ".join(items) if items else "none"


def _response_for_intent(intent: str, contract: Any, query: str) -> str:
    sections = contract.sections
    week = sections["week_plan"]
    news = sections["news"]
    safety = sections["safety"]
    status = sections["status"]
    selections = list(week.get("selected_instruments", []) or [])

    crypto = _selected_summary(selections, "crypto")
    etf_fund = _selected_summary(selections, "etf_fund")
    stock = _selected_summary(selections, "individual_stock")
    open_command = _open_dashboard_command(contract.dashboard_path)

    if intent == "today_plan":
        return (
            "Today’s manual plan is ready. "
            f"Emergency top-up: {_money(week.get('emergency_top_up_eur'))}. "
            f"Crypto: {_money(week.get('crypto_eur'))} split as {crypto}. "
            f"ETF/fund: {_money(week.get('etf_fund_eur'))} split as {etf_fund}. "
            f"Individual stock: {_money(week.get('individual_stock_eur'))} as {stock}. "
            "This is read-only guidance; Diogo must perform any real-world action manually outside J.A.R.V.I.S."
        )

    if intent == "instrument_rationale":
        return (
            "The current selections come from the validated product API and dynamic instrument summary. "
            f"Crypto is capped and split as {crypto}. "
            f"ETF/fund exposure is split as {etf_fund}. "
            f"Stock exposure is conservative and currently shown as {stock}. "
            f"News coverage ready: {news.get('news_coverage_ready')}; live news fetching remains disabled, so manual review is still required."
        )

    if intent == "safety":
        return (
            "Safety is active. "
            f"Safety-check blocked execution: {safety.get('safety_check_blocked_execution')}. "
            f"Manual approval required: {safety.get('manual_approval_required')}. "
            f"Execution forbidden: {safety.get('execution_forbidden')}. "
            f"Broker connection: {safety.get('broker_connection')}. "
            f"Credentials used: {safety.get('credentials_used')}. "
            f"Order created: {safety.get('order_created')}. "
            f"Trade executed: {safety.get('trade_executed')}."
        )

    if intent == "blockers":
        blockers = list(status.get("blockers", []) or contract.blockers or [])
        blocker_text = ", ".join(str(item) for item in blockers) if blockers else "none"
        return (
            f"Current blockers: {blocker_text}. "
            "Warnings may still exist for manual review, but blockers must be none before any manual action."
        )

    if intent == "dashboard":
        return (
            f"Dashboard file: {contract.dashboard_path}. "
            f"Open it with: {open_command}. "
            "The dashboard is a local static HTML file and does not start a web server."
        )

    return (
        "I can answer: what is today’s plan, why these instruments, is the system safe, "
        "what are the blockers, and how to open the dashboard. "
        "All answers are read-only and manual-only."
    )


def build_chat_interface_contract_result(
    *,
    query: str = "",
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> ChatInterfaceContractResult:
    dashboard_contract = build_dashboard_contract_result(current_date=current_date)
    intent = _detect_intent(query)
    response = _response_for_intent(intent, dashboard_contract, query)

    blockers: list[str] = []
    blockers.extend(str(item) for item in (dashboard_contract.blockers or []))
    if not dashboard_contract.dashboard_contract_ready:
        blockers.append("dashboard_contract_not_ready")
    if not dashboard_contract.manual_only:
        blockers.append("manual_only_safety_not_ready")
    blockers = list(dict.fromkeys(item for item in blockers if item))

    warnings = list(dict.fromkeys(
        ["chat interface is a read-only response contract and does not start a chat server"]
        + [str(item) for item in (dashboard_contract.warnings or []) if item]
    ))

    open_command = _open_dashboard_command(dashboard_contract.dashboard_path)
    ready = not blockers

    result = ChatInterfaceContractResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        chat_contract_ready=ready,
        query=query,
        detected_intent=intent,
        response=response,
        supported_intents=list(SUPPORTED_INTENTS),
        manual_only=bool(dashboard_contract.manual_only),
        dashboard_path=dashboard_contract.dashboard_path,
        open_dashboard_command=open_command,
        warnings=warnings,
        blockers=blockers,
        report_written=bool(write_report),
        report_path=str(output_path),
    )

    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return result


def format_chat_interface_contract(result: ChatInterfaceContractResult) -> str:
    lines = [
        "J.A.R.V.I.S. CHAT INTERFACE CONTRACT",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"chat contract ready: {result.chat_contract_ready}",
        f"manual-only safety: {result.manual_only}",
        f"query: {result.query or 'none'}",
        f"detected intent: {result.detected_intent}",
        "",
        "RESPONSE:",
        result.response,
        "",
        "SUPPORTED INTENTS:",
    ]
    lines.extend(f"- {item}" for item in result.supported_intents)
    lines.extend(
        [
            "",
            "DASHBOARD:",
            f"- path: {result.dashboard_path}",
            f"- open command: {result.open_dashboard_command}",
            "",
            "WARNINGS:",
        ]
    )
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    lines.append("")
    lines.append(f"report written: {result.report_written}")
    lines.append(f"report path: {result.report_path}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. chat interface contract.")
    parser.add_argument("--chat-interface", action="store_true")
    parser.add_argument("--chat-query", default="")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_chat_interface_contract_result(
        query=args.chat_query,
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_chat_interface_contract(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "SUPPORTED_INTENTS",
    "ChatInterfaceContractResult",
    "build_chat_interface_contract_result",
    "format_chat_interface_contract",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
