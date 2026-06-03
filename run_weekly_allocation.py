"""Run the local weekly allocation report."""

from __future__ import annotations

from allocation_engine import (
    append_decision_log,
    build_weekly_result,
    render_report,
    save_approval_ticket,
)
from voice_adapter import speak


def main() -> None:
    result = build_weekly_result()
    print(render_report(result))
    save_approval_ticket(result["approval_ticket"])
    log_path = append_decision_log(result["approval_ticket"])
    print(f"Decision log updated: {log_path}")
    speak("Weekly allocation report is ready.")


if __name__ == "__main__":
    main()
