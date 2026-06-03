"""Read-only status command for J.A.R.V.I.S. Portfolio OS."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import allocation_engine


STATUS_LINE = "Status only. No trades executed."


def format_eur(value: int | float) -> str:
    return f"EUR {float(value):,.2f}"


def build_status(
    state_path: str | Path = "portfolio_state.json",
    constitution_path: str | Path = "jarvis_constitution.json",
) -> str:
    state = allocation_engine.load_json(state_path)
    constitution = allocation_engine.load_json(constitution_path)
    result = allocation_engine.allocate_weekly_budget(constitution, state)

    lines = [
        "J.A.R.V.I.S. Portfolio Status",
        "=" * 31,
        f"as_of: {state.get('as_of', 'unknown')}",
        f"monthly_budget: {format_eur(state.get('monthly_investment_budget', 0.0))}",
        f"weekly_budget: {format_eur(state.get('weekly_investment_budget', 0.0))}",
        f"portfolio_mode: {result['portfolio_mode']['mode']}",
        "",
        "platform_readiness:",
    ]

    for key, value in sorted(state.get("platform_status", {}).items()):
        lines.append(f"- {key}: {value}")

    lines.append("")
    lines.append("current_holdings:")
    for key, value in sorted(state.get("holdings", {}).items()):
        lines.append(f"- {key}: {format_eur(value)}")

    lines.append("")
    lines.append("legacy_holdings:")
    for key, value in sorted(state.get("legacy_holdings", {}).items()):
        display = "unknown/pending" if value is None else format_eur(value)
        lines.append(f"- {key}: {display}")

    emergency = state.get("emergency_fund", {})
    lines.extend(
        [
            "",
            f"emergency_fund_excluded: {format_eur(emergency.get('amount', 0.0))}",
            STATUS_LINE,
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print read-only J.A.R.V.I.S. status.")
    parser.add_argument("--state-path", default="portfolio_state.json")
    parser.add_argument("--constitution-path", default="jarvis_constitution.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(build_status(args.state_path, args.constitution_path))


if __name__ == "__main__":
    main()
