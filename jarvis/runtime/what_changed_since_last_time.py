"""J.A.R.V.I.S. v146.0 what changed since last time."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.jarvis_session_memory import (
    DEFAULT_SESSION_MEMORY_PATH,
    build_safe_session_snapshot,
    load_session_memory,
)
from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V146_0_WHAT_CHANGED_SINCE_LAST_TIME_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V146_0_WHAT_CHANGED_SINCE_LAST_TIME_REVIEW_REQUIRED_SAFE"


@dataclass(frozen=True)
class WhatChangedSinceLastTimeResult:
    status: str
    current_date: str
    what_changed_ready: bool
    first_run: bool
    memory_path: str
    previous_snapshot_exists: bool
    comparison_available: bool
    summary_text: str
    changes: list[str]
    safety_check_blocks_execution: bool
    manual_only: bool
    broker_connection_enabled: bool
    credentials_required: bool
    buy_sell_request_created: bool
    order_created: bool
    trade_created: bool
    auto_approval_enabled: bool
    private_account_ingestion_enabled: bool
    allocation_mutation: bool
    approval_mutation: bool
    blockers: list[str]
    warnings: list[str]
    proof: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _safety_check_ready() -> bool:
    text = build_safety_check_console_output()
    return "BLOCKED:" in text and "No execution action was taken" in text


def _changed_line(label: str, old: Any, new: Any) -> str | None:
    if old == new:
        return f"{label} unchanged"
    return f"{label} changed from {old or 'unavailable'} to {new or 'unavailable'}"


def _compare_snapshots(previous: Mapping[str, Any], current: Mapping[str, Any]) -> list[str]:
    fields = [
        ("dashboard", "dashboard_ready_label"),
        ("manual plan", "manual_plan_summary"),
        ("selected instruments", "selected_instruments_summary"),
        ("market movement", "market_movement_summary"),
        ("news", "news_headline_summary"),
        ("holdings", "holdings_status_summary"),
        ("blockers count", "blockers_count"),
        ("warnings count", "warnings_count"),
    ]
    changes = [_changed_line(label, previous.get(key), current.get(key)) for label, key in fields]
    prev_safety = previous.get("safety_status") if isinstance(previous.get("safety_status"), Mapping) else {}
    current_safety = current.get("safety_status") if isinstance(current.get("safety_status"), Mapping) else {}
    if prev_safety.get("manual_only") == current_safety.get("manual_only") == True:
        changes.append("safety remains manual-only")
    else:
        changes.append("safety status needs review")
    return [str(item) for item in changes if item]


def _calm_summary(changes: list[str], *, first_run: bool) -> str:
    if first_run:
        return "Since last time: first run. No previous safe snapshot exists yet, so no comparison is available."
    unchanged = [item for item in changes if item.endswith("unchanged")]
    changed = [item for item in changes if " changed from " in item]
    safety = next((item for item in changes if item.startswith("safety ")), "safety remains manual-only")
    if not changed:
        return f"Since last time: dashboard remains ready, manual plan is unchanged, no blockers appeared, and {safety}."
    return "Since last time: " + "; ".join(changed[:5] + [safety]) + "."


def _forbidden_language_absent(text: str) -> bool:
    lowered = text.lower()
    forbidden = ("bought", "sold", "order created", "trade executed", "place order", "liquidate")
    return not any(item in lowered for item in forbidden)


def build_what_changed_since_last_time_result(
    *,
    current_date: str = "2026-06-20",
    memory_path: str | Path = DEFAULT_SESSION_MEMORY_PATH,
    current_snapshot: Mapping[str, Any] | None = None,
) -> WhatChangedSinceLastTimeResult:
    blockers: list[str] = []
    warnings: list[str] = [
        "what-changed compares safe derived local summaries only",
        "it does not infer private account changes or claim real-world transactions happened",
    ]
    previous = load_session_memory(memory_path)
    first_run = previous is None
    if current_snapshot is None and not first_run:
        current = build_safe_session_snapshot(current_date=current_date)
    else:
        current = dict(current_snapshot or {})

    if first_run:
        changes: list[str] = []
        summary = _calm_summary(changes, first_run=True)
    else:
        changes = _compare_snapshots(previous or {}, current)
        summary = _calm_summary(changes, first_run=False)

    safety_ready = _safety_check_ready()
    if not safety_ready:
        blockers.append("safety_check_did_not_block_execution")
    if not _forbidden_language_absent(summary):
        blockers.append("what_changed_summary_contains_execution_language")

    blockers = _dedupe(blockers)
    ready = not blockers
    return WhatChangedSinceLastTimeResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        what_changed_ready=ready,
        first_run=first_run,
        memory_path=str(memory_path),
        previous_snapshot_exists=not first_run,
        comparison_available=not first_run,
        summary_text=summary,
        changes=changes,
        safety_check_blocks_execution=safety_ready,
        manual_only=True,
        broker_connection_enabled=False,
        credentials_required=False,
        buy_sell_request_created=False,
        order_created=False,
        trade_created=False,
        auto_approval_enabled=False,
        private_account_ingestion_enabled=False,
        allocation_mutation=False,
        approval_mutation=False,
        blockers=blockers,
        warnings=_dedupe(warnings),
        proof={
            "memory_exists": not first_run,
            "current_snapshot_built": bool(current),
            "change_count": len(changes),
            "safety_blocked": safety_ready,
        },
    )


def format_what_changed_since_last_time(result: WhatChangedSinceLastTimeResult) -> str:
    lines = [
        "J.A.R.V.I.S. WHAT CHANGED SINCE LAST TIME",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"what changed ready: {result.what_changed_ready}",
        f"first run: {result.first_run}",
        f"memory path: {result.memory_path}",
        f"comparison available: {result.comparison_available}",
        "",
        "SUMMARY:",
        result.summary_text,
        "",
        "CHANGES:",
        *[f"- {item}" for item in result.changes or ["none"]],
        "",
        "SAFETY ASSERTIONS:",
        f"- safety check blocks execution: {result.safety_check_blocks_execution}",
        f"- manual_only: {result.manual_only}",
        f"- broker_connection_enabled: {result.broker_connection_enabled}",
        f"- credentials_required: {result.credentials_required}",
        f"- buy_sell_request_created: {result.buy_sell_request_created}",
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
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. what changed since last time.")
    parser.add_argument("--what-changed", action="store_true")
    parser.add_argument("--current-date", default="2026-06-20")
    parser.add_argument("--session-memory-path", default=DEFAULT_SESSION_MEMORY_PATH)
    args = parser.parse_args(argv)

    result = build_what_changed_since_last_time_result(
        current_date=args.current_date,
        memory_path=args.session_memory_path,
    )
    print(format_what_changed_since_last_time(result))
    return 0 if result.what_changed_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "WhatChangedSinceLastTimeResult",
    "build_what_changed_since_last_time_result",
    "format_what_changed_since_last_time",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
