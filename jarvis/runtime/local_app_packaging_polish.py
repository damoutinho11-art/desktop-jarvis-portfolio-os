"""J.A.R.V.I.S. v147.0 local app packaging polish gate."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V147_0_LOCAL_APP_PACKAGING_POLISH_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V147_0_LOCAL_APP_PACKAGING_POLISH_REVIEW_REQUIRED_SAFE"

LAUNCHER_FILES = ("Start Jarvis.bat", "Start-Jarvis.ps1")
RUNBOOK_PATH = "JARVIS_USER_RUNBOOK.md"
REQUIRED_MARKERS = (
    "Manual approval required",
    "No broker",
    "No credentials",
    "No orders",
    "No trades",
    "No auto-approval",
    "--local-server",
    "127.0.0.1:8765",
    "/dashboard",
    "/chat",
)
RUNBOOK_REQUIRED_MARKERS = (
    "How Diogo Uses J.A.R.V.I.S. Daily",
    "What J.A.R.V.I.S. Cannot Do",
    "Manual Buy Workflow",
    "Market Headlines",
    "--voice-briefing-text",
    "--what-changed",
)
FORBIDDEN_PACKAGING_PHRASES = (
    "place order",
    "execute trade",
    "auto rebalance",
    "connect broker",
    "broker password",
)


@dataclass(frozen=True)
class LocalAppPackagingPolishResult:
    status: str
    local_app_packaging_ready: bool
    launcher_files_exist: bool
    launchers_have_safety_markers: bool
    optional_chat_helper_present: bool
    runbook_ready: bool
    referenced_commands_exist: bool
    safety_check_blocks_execution: bool
    manual_only: bool
    broker_connection_enabled: bool
    credentials_required: bool
    order_created: bool
    trade_created: bool
    auto_approval_enabled: bool
    blockers: list[str]
    warnings: list[str]
    proof: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _read(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError:
        return ""


def _safety_check_ready() -> bool:
    text = build_safety_check_console_output()
    return "BLOCKED:" in text and "No execution action was taken" in text


def build_local_app_packaging_polish_result() -> LocalAppPackagingPolishResult:
    blockers: list[str] = []
    warnings = [
        "local app packaging uses repo-local launchers only; no installer, admin permission, broker login, or credentials required",
    ]
    launcher_texts = {name: _read(name) for name in LAUNCHER_FILES}
    launcher_files_exist = all(bool(text) for text in launcher_texts.values())
    if not launcher_files_exist:
        blockers.append("launcher_files_missing")

    combined_launchers = "\n".join(launcher_texts.values())
    missing_launcher_markers = [marker for marker in REQUIRED_MARKERS if marker not in combined_launchers]
    launchers_have_safety = not missing_launcher_markers
    if missing_launcher_markers:
        blockers.append("launcher_safety_markers_missing")

    optional_chat_helper = (
        "127.0.0.1:8765/dashboard" in combined_launchers
        and "127.0.0.1:8765/chat" in combined_launchers
        and "JARVIS_OPEN_CHAT" not in combined_launchers
    )
    if not optional_chat_helper:
        blockers.append("local_app_dashboard_chat_launch_missing")

    runbook_text = _read(RUNBOOK_PATH)
    missing_runbook_markers = [marker for marker in RUNBOOK_REQUIRED_MARKERS if marker not in runbook_text]
    runbook_ready = bool(runbook_text) and not missing_runbook_markers
    if not runbook_ready:
        blockers.append("runbook_packaging_sections_missing")

    operator_text = _read("jarvis/runtime/operator.py")
    commands = ["--daily-operator", "--dashboard-contract", "--local-server", "--voice-briefing-text", "--what-changed", "--holdings-status"]
    missing_commands = [command for command in commands if command not in operator_text]
    commands_exist = not missing_commands
    if missing_commands:
        blockers.append("referenced_operator_commands_missing")

    forbidden_found = [phrase for phrase in FORBIDDEN_PACKAGING_PHRASES if phrase in combined_launchers.lower()]
    if forbidden_found:
        blockers.append("forbidden_packaging_phrase_found")

    safety_ready = _safety_check_ready()
    if not safety_ready:
        blockers.append("safety_check_did_not_block_execution")

    blockers = _dedupe(blockers)
    ready = not blockers
    return LocalAppPackagingPolishResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        local_app_packaging_ready=ready,
        launcher_files_exist=launcher_files_exist,
        launchers_have_safety_markers=launchers_have_safety,
        optional_chat_helper_present=optional_chat_helper,
        runbook_ready=runbook_ready,
        referenced_commands_exist=commands_exist,
        safety_check_blocks_execution=safety_ready,
        manual_only=True,
        broker_connection_enabled=False,
        credentials_required=False,
        order_created=False,
        trade_created=False,
        auto_approval_enabled=False,
        blockers=blockers,
        warnings=warnings,
        proof={
            "missing_launcher_markers": missing_launcher_markers,
            "missing_runbook_markers": missing_runbook_markers,
            "missing_commands": missing_commands,
            "forbidden_found": forbidden_found,
            "safety_blocked": safety_ready,
        },
    )


def format_local_app_packaging_polish(result: LocalAppPackagingPolishResult) -> str:
    lines = [
        "J.A.R.V.I.S. LOCAL APP PACKAGING POLISH",
        f"status: {result.status}",
        f"local app packaging ready: {result.local_app_packaging_ready}",
        "",
        "CHECKS:",
        f"- launcher files exist: {result.launcher_files_exist}",
        f"- launchers have safety markers: {result.launchers_have_safety_markers}",
        f"- optional chat helper present: {result.optional_chat_helper_present}",
        f"- runbook ready: {result.runbook_ready}",
        f"- referenced commands exist: {result.referenced_commands_exist}",
        f"- safety check blocks execution: {result.safety_check_blocks_execution}",
        "",
        "SAFETY ASSERTIONS:",
        f"- manual_only: {result.manual_only}",
        f"- broker_connection_enabled: {result.broker_connection_enabled}",
        f"- credentials_required: {result.credentials_required}",
        f"- order_created: {result.order_created}",
        f"- trade_created: {result.trade_created}",
        f"- auto_approval_enabled: {result.auto_approval_enabled}",
        "",
        "WARNINGS:",
        *[f"- {item}" for item in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the J.A.R.V.I.S. local app packaging polish gate.")
    parser.add_argument("--local-app-packaging-polish", action="store_true")
    parser.parse_args(argv)

    result = build_local_app_packaging_polish_result()
    print(format_local_app_packaging_polish(result))
    return 0 if result.local_app_packaging_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "LocalAppPackagingPolishResult",
    "build_local_app_packaging_polish_result",
    "format_local_app_packaging_polish",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
