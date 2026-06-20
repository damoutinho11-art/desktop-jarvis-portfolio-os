"""J.A.R.V.I.S. v133.0 user runbook command.

The runbook command is read-only. It prints the local user guide and verifies
that the essential app, holdings, and safety instructions are present.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

STATUS_READY = "JARVIS_V133_0_USER_RUNBOOK_APP_UX_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V133_0_USER_RUNBOOK_APP_UX_REVIEW_REQUIRED_SAFE"
DEFAULT_RUNBOOK_PATH = "JARVIS_USER_RUNBOOK.md"

REQUIRED_SNIPPETS = (
    "Start Jarvis.bat",
    "Start-Jarvis.ps1",
    "outputs\\dashboard_latest.html",
    "Manual Holdings",
    "python .\\jarvis_operator.py --write-holdings-template --current-date 2026-06-20",
    "python .\\jarvis_operator.py --holdings-status --current-date 2026-06-20",
    "manual_only",
    "source",
    "diogo_manual_entry",
    "no broker",
    "no credentials",
    "no orders",
    "no trades",
    "Do not commit files from `outputs/` or `jarvis/local/`.",
)


@dataclass(frozen=True)
class UserRunbookResult:
    status: str
    current_date: str
    runbook_ready: bool
    runbook_path: str
    runbook_exists: bool
    runbook_text: str
    missing_required_snippets: list[str]
    warnings: list[str]
    blockers: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _read_text(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, ""
    try:
        return True, path.read_text(encoding="utf-8")
    except OSError:
        return True, ""


def build_user_runbook_result(
    *,
    current_date: str = "2026-06-20",
    runbook_path: str | Path = DEFAULT_RUNBOOK_PATH,
) -> UserRunbookResult:
    path = Path(runbook_path)
    exists, text = _read_text(path)
    missing = [snippet for snippet in REQUIRED_SNIPPETS if snippet not in text]

    blockers: list[str] = []
    if not exists:
        blockers.append("user_runbook_missing")
    if exists and not text:
        blockers.append("user_runbook_unreadable_or_empty")
    if missing:
        blockers.append("user_runbook_missing_required_user_instructions")

    ready = not blockers
    warnings = [
        "runbook is user-facing and local; it does not create broker, order, trade, or auto-approval capability"
    ]

    return UserRunbookResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        runbook_ready=ready,
        runbook_path=str(path),
        runbook_exists=exists,
        runbook_text=text,
        missing_required_snippets=missing,
        warnings=warnings,
        blockers=list(dict.fromkeys(blockers)),
    )


def format_user_runbook(result: UserRunbookResult) -> str:
    lines = [
        "J.A.R.V.I.S. USER RUNBOOK",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"runbook ready: {result.runbook_ready}",
        f"runbook path: {result.runbook_path}",
        f"runbook exists: {result.runbook_exists}",
        "",
        "WARNINGS:",
        *[f"- {item}" for item in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
    ]
    if result.missing_required_snippets:
        lines.extend(["", "MISSING REQUIRED INSTRUCTIONS:"])
        lines.extend(f"- {item}" for item in result.missing_required_snippets)
    lines.extend(["", "RUNBOOK:", result.runbook_text or "not available"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Print the J.A.R.V.I.S. user runbook.")
    parser.add_argument("--user-runbook", action="store_true")
    parser.add_argument("--current-date", default="2026-06-20")
    parser.add_argument("--runbook-path", default=DEFAULT_RUNBOOK_PATH)
    args = parser.parse_args(argv)

    result = build_user_runbook_result(current_date=args.current_date, runbook_path=args.runbook_path)
    print(format_user_runbook(result))
    return 0 if result.runbook_ready else 1


__all__ = [
    "DEFAULT_RUNBOOK_PATH",
    "REQUIRED_SNIPPETS",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "UserRunbookResult",
    "build_user_runbook_result",
    "format_user_runbook",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
