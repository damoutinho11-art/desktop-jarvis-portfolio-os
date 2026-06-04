"""Run the local weekly allocation report."""

from __future__ import annotations

import argparse

from allocation_engine import (
    append_decision_log,
    build_weekly_result,
    render_report,
    save_approval_ticket,
)
from voice_adapter import speak


ASSET_LABELS = {
    "quality_etf": "Quality ETF",
    "growth_nasdaq_etf": "Growth/Nasdaq ETF",
    "global_core_etf": "Global Core ETF",
    "btc": "Bitcoin",
    "hype": "HYPE",
    "tao": "TAO",
    "discovery": "discovery",
    "tactical_reserve": "tactical reserve",
}


def format_eur(value: int | float) -> str:
    return f"€{float(value):,.2f}"


def mode_label(mode: str) -> str:
    return mode.removesuffix("_mode").replace("_", " ")


def asset_label(asset: str) -> str:
    return ASSET_LABELS.get(asset, asset.replace("_", " "))


def join_phrase(parts: list[str]) -> str:
    if not parts:
        return "none"
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + f" and {parts[-1]}"


def allocation_summary(allocations: dict[str, float]) -> str:
    if not allocations:
        return "none"
    return join_phrase(
        [
            f"{format_eur(amount)} to {asset_label(asset)}"
            for asset, amount in sorted(allocations.items())
        ]
    )


def blocked_platform_phrase(ticket: dict) -> str:
    blocked_actions = ticket.get("blocked_actions", [])
    if not blocked_actions:
        return "No platform route is blocking the ideal allocation."
    reason = blocked_actions[0].get("reason", "")
    if "Lightyear platform is not ready" in reason:
        return "Lightyear is not ready."
    return reason.rstrip(".") + "."


def build_weekly_voice_briefing(result: dict) -> str:
    ticket = result["approval_ticket"]
    return (
        f"Sir, portfolio mode is {mode_label(ticket['portfolio_mode'])}. "
        f"The ideal allocation is {allocation_summary(ticket['ideal_allocation'])}, "
        f"but {blocked_platform_phrase(ticket)} "
        f"My executable recommendation is {allocation_summary(ticket['executable_allocation'])}. "
        "Manual approval required. No trades executed."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run weekly J.A.R.V.I.S. allocation.")
    parser.add_argument("--speak", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_weekly_result()
    print(render_report(result))
    save_approval_ticket(result["approval_ticket"])
    log_path = append_decision_log(result["approval_ticket"])
    print(f"Decision log updated: {log_path}")
    if args.speak:
        speak(build_weekly_voice_briefing(result))


if __name__ == "__main__":
    main()
