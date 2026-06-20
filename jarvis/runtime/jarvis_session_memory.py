"""J.A.R.V.I.S. v142.0 safe local session memory."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.product_api import build_product_api_result
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V142_0_JARVIS_SESSION_MEMORY_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V142_0_JARVIS_SESSION_MEMORY_REVIEW_REQUIRED_SAFE"
DEFAULT_SESSION_MEMORY_PATH = "jarvis/local/jarvis_session_memory.local.json"

FORBIDDEN_MEMORY_KEYS: tuple[str, ...] = (
    "credential",
    "password",
    "token",
    "secret",
    "broker",
    "private_account_feed",
    "private_account_ingestion",
    "order_intent",
    "buy_sell_request",
    "buy_request",
    "sell_request",
    "order_ticket",
    "order_created",
    "trade_created",
    "trade_executed",
    "auto_approval",
    "allocation_mutation",
    "approval_mutation",
    "approval_ticket_mutation",
    "executable",
)


@dataclass(frozen=True)
class JarvisSessionMemoryResult:
    status: str
    current_date: str
    mode: str
    session_memory_ready: bool
    first_run: bool
    memory_path: str
    memory_exists: bool
    snapshot_written: bool
    summary_text: str
    safe_derived_summary_only: bool
    forbidden_fields_absent: bool
    safety_check_blocks_execution: bool
    manual_only: bool
    broker_connection_enabled: bool
    credentials_required: bool
    order_created: bool
    trade_created: bool
    auto_approval_enabled: bool
    private_account_ingestion_enabled: bool
    allocation_mutation: bool
    approval_mutation: bool
    blockers: list[str]
    warnings: list[str]
    snapshot: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "__dict__"):
        return dict(value.__dict__)
    return {}


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _money(value: Any) -> str:
    try:
        return f"EUR {float(value or 0.0):.2f}"
    except Exception:
        return "EUR 0.00"


def _manual_plan_summary(week_plan: Mapping[str, Any]) -> str:
    return (
        f"emergency {_money(week_plan.get('emergency_top_up_eur'))}, "
        f"crypto {_money(week_plan.get('crypto_eur'))}, "
        f"ETF/fund {_money(week_plan.get('etf_fund_eur'))}, "
        f"stock {_money(week_plan.get('individual_stock_eur'))}"
    )


def _selected_instruments_summary(week_plan: Mapping[str, Any]) -> str:
    selected = week_plan.get("selected_instruments") or []
    if not selected:
        return "selected instruments unavailable"
    parts = []
    for item in selected:
        if isinstance(item, Mapping):
            parts.append(f"{item.get('symbol')} {_money(item.get('amount_eur'))}")
    return ", ".join(parts) if parts else "selected instruments unavailable"


def _news_summary(live_news: Mapping[str, Any]) -> str:
    headlines = live_news.get("top_headlines") or []
    if not headlines:
        return "News unavailable - not blocking today's manual plan."
    titles = []
    for item in headlines[:3]:
        if isinstance(item, Mapping) and item.get("title"):
            titles.append(str(item.get("title")))
    return "; ".join(titles) if titles else "News unavailable - not blocking today's manual plan."


def _holdings_summary(holdings: Mapping[str, Any]) -> str:
    if not holdings.get("file_exists"):
        return "Holdings not entered yet; this is a warning, not a blocker."
    return (
        f"{holdings.get('positions_count', 0)} positions, "
        f"{holdings.get('confirmed_positions_count', 0)} confirmed, "
        f"cost basis {_money(holdings.get('total_cost_basis_eur'))}"
    )


def _safe_text(value: str) -> str:
    text = str(value or "").strip()
    lowered = text.lower()
    if any(token in lowered for token in ("password", "credential", "token", "secret")):
        return "[redacted unsafe memory text]"
    return text[:500]


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            lowered = str(key).lower()
            if any(token in lowered for token in FORBIDDEN_MEMORY_KEYS):
                return True
            if _contains_forbidden_key(item):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def _safety_check_ready() -> bool:
    text = build_safety_check_console_output()
    return "BLOCKED:" in text and "No execution action was taken" in text


def build_safe_session_snapshot(
    *,
    current_date: str = "2026-06-20",
    product_api_result: Any | None = None,
    last_assistant_summary_text: str = "",
) -> dict[str, Any]:
    product = _plain(product_api_result or build_product_api_result(current_date=current_date))
    week_plan = product.get("week_plan") or {}
    live_news = product.get("live_news_context") or {}
    holdings = product.get("manual_holdings") or {}
    safety = product.get("safety_status") or {}
    blockers = list(product.get("blockers") or [])
    warnings = list(product.get("warnings") or [])

    return {
        "schema_version": 1,
        "timestamp": current_date,
        "current_date": current_date,
        "dashboard_ready_label": "READY FOR MANUAL USE" if product.get("dashboard_ready") else "REVIEW REQUIRED",
        "manual_plan_summary": _manual_plan_summary(week_plan),
        "selected_instruments_summary": _selected_instruments_summary(week_plan),
        "market_movement_summary": "Use the dashboard Market Movement section; source freshness must be reviewed manually.",
        "news_headline_summary": _news_summary(live_news),
        "holdings_status_summary": _holdings_summary(holdings),
        "safety_status": {
            "manual_only": True,
            "safety_check_blocked_execution": bool(safety.get("safety_check_blocked_execution", True)),
            "execution_forbidden": True,
            "summary": "Manual-only safety is active: no broker, no credentials, no orders, no trades, and no auto-approval.",
        },
        "blockers_count": len(blockers),
        "warnings_count": len(warnings),
        "last_assistant_summary_text": _safe_text(last_assistant_summary_text),
    }


def load_session_memory(path: str | Path = DEFAULT_SESSION_MEMORY_PATH) -> dict[str, Any] | None:
    memory_path = Path(path)
    if not memory_path.exists():
        return None
    try:
        data = json.loads(memory_path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def write_session_memory_snapshot(
    snapshot: Mapping[str, Any],
    path: str | Path = DEFAULT_SESSION_MEMORY_PATH,
) -> None:
    memory_path = Path(path)
    memory_path.parent.mkdir(parents=True, exist_ok=True)
    memory_path.write_text(json.dumps(dict(snapshot), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def summarize_session_memory(snapshot: Mapping[str, Any] | None) -> str:
    if not snapshot:
        return "First run: no previous J.A.R.V.I.S. session memory exists yet. This is safe and not a blocker."
    return (
        f"Last memory: {snapshot.get('dashboard_ready_label', 'unknown')}; "
        f"manual plan {snapshot.get('manual_plan_summary', 'unavailable')}; "
        f"news {snapshot.get('news_headline_summary', 'unavailable')}; "
        f"holdings {snapshot.get('holdings_status_summary', 'unavailable')}; "
        f"safety remains manual-only."
    )


def build_jarvis_session_memory_result(
    *,
    mode: str = "status",
    current_date: str = "2026-06-20",
    memory_path: str | Path = DEFAULT_SESSION_MEMORY_PATH,
    last_assistant_summary_text: str = "",
) -> JarvisSessionMemoryResult:
    blockers: list[str] = []
    warnings: list[str] = [
        "session memory stores safe derived summaries only",
        "session memory path is local/ignored and does not require credentials",
    ]
    snapshot_written = False
    existing = load_session_memory(memory_path)
    snapshot: dict[str, Any] = dict(existing or {})

    if mode == "write_snapshot":
        snapshot = build_safe_session_snapshot(
            current_date=current_date,
            last_assistant_summary_text=last_assistant_summary_text,
        )
        write_session_memory_snapshot(snapshot, memory_path)
        snapshot_written = True
        existing = snapshot
    elif mode not in {"status", "summary"}:
        blockers.append("unsupported_session_memory_mode")

    forbidden_absent = not _contains_forbidden_key(snapshot)
    if not forbidden_absent:
        blockers.append("forbidden_memory_fields_found")

    safety_ready = _safety_check_ready()
    if not safety_ready:
        blockers.append("safety_check_did_not_block_execution")

    first_run = not bool(existing)
    summary_text = summarize_session_memory(existing)
    ready = not blockers

    return JarvisSessionMemoryResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        mode=mode,
        session_memory_ready=ready,
        first_run=first_run,
        memory_path=str(memory_path),
        memory_exists=bool(existing),
        snapshot_written=snapshot_written,
        summary_text=summary_text,
        safe_derived_summary_only=True,
        forbidden_fields_absent=forbidden_absent,
        safety_check_blocks_execution=safety_ready,
        manual_only=True,
        broker_connection_enabled=False,
        credentials_required=False,
        order_created=False,
        trade_created=False,
        auto_approval_enabled=False,
        private_account_ingestion_enabled=False,
        allocation_mutation=False,
        approval_mutation=False,
        blockers=_dedupe(blockers),
        warnings=_dedupe(warnings),
        snapshot=snapshot if mode in {"write_snapshot", "summary"} else {},
    )


def format_jarvis_session_memory(result: JarvisSessionMemoryResult) -> str:
    lines = [
        "J.A.R.V.I.S. SESSION MEMORY",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"mode: {result.mode}",
        f"session memory ready: {result.session_memory_ready}",
        f"first run: {result.first_run}",
        f"memory path: {result.memory_path}",
        f"memory exists: {result.memory_exists}",
        f"snapshot written: {result.snapshot_written}",
        "",
        "SUMMARY:",
        result.summary_text,
        "",
        "SAFETY ASSERTIONS:",
        f"- safe derived summaries only: {result.safe_derived_summary_only}",
        f"- forbidden fields absent: {result.forbidden_fields_absent}",
        f"- safety check blocks execution: {result.safety_check_blocks_execution}",
        f"- manual_only: {result.manual_only}",
        f"- broker_connection_enabled: {result.broker_connection_enabled}",
        f"- credentials_required: {result.credentials_required}",
        f"- order_created: {result.order_created}",
        f"- trade_created: {result.trade_created}",
        f"- auto_approval_enabled: {result.auto_approval_enabled}",
        f"- private_account_ingestion_enabled: {result.private_account_ingestion_enabled}",
        f"- allocation_mutation: {result.allocation_mutation}",
        f"- approval_mutation: {result.approval_mutation}",
        "",
        "WARNINGS:",
        *[f"- {item}" for item in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. safe local session memory.")
    parser.add_argument("--session-memory-status", action="store_true")
    parser.add_argument("--session-memory-write-snapshot", action="store_true")
    parser.add_argument("--session-memory-summary", action="store_true")
    parser.add_argument("--current-date", default="2026-06-20")
    parser.add_argument("--session-memory-path", default=DEFAULT_SESSION_MEMORY_PATH)
    parser.add_argument("--assistant-summary", default="")
    args = parser.parse_args(argv)

    mode = "status"
    if args.session_memory_write_snapshot:
        mode = "write_snapshot"
    elif args.session_memory_summary:
        mode = "summary"

    result = build_jarvis_session_memory_result(
        mode=mode,
        current_date=args.current_date,
        memory_path=args.session_memory_path,
        last_assistant_summary_text=args.assistant_summary,
    )
    print(format_jarvis_session_memory(result))
    return 0 if result.session_memory_ready else 1


__all__ = [
    "DEFAULT_SESSION_MEMORY_PATH",
    "FORBIDDEN_MEMORY_KEYS",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "JarvisSessionMemoryResult",
    "build_safe_session_snapshot",
    "build_jarvis_session_memory_result",
    "format_jarvis_session_memory",
    "load_session_memory",
    "summarize_session_memory",
    "write_session_memory_snapshot",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
