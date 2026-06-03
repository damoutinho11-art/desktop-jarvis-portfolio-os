"""Safe local updater for J.A.R.V.I.S. portfolio_state.json."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any


VALID_HOLDINGS = {
    "global_core_etf",
    "growth_nasdaq_etf",
    "quality_etf",
    "btc",
    "hype",
    "tao",
    "discovery",
    "tactical_reserve",
}
VALID_LEGACY_KEYS = {
    "lhv_growth_sxr8",
    "lhv_growth_iemm",
    "lhv_growth_xcha",
    "lhv_growth_cash_pending_settlement",
}
VALID_PLATFORM_KEYS = {
    "lightyear_ready",
    "lhv_crypto_ready",
    "kraken_ready",
    "trade_republic_ready",
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, sort_keys=True)
        file.write("\n")


def parse_assignment(value: str) -> tuple[str, str]:
    if "=" not in value:
        raise ValueError(f"Expected key=value assignment: {value}")
    key, raw_value = value.split("=", 1)
    if not key or raw_value == "":
        raise ValueError(f"Expected non-empty key=value assignment: {value}")
    return key, raw_value


def parse_number(raw_value: str) -> float:
    try:
        return float(raw_value)
    except ValueError as exc:
        raise ValueError(f"Expected numeric value, got: {raw_value}") from exc


def parse_bool(raw_value: str) -> bool:
    normalized = raw_value.strip().lower()
    if normalized == "true":
        return True
    if normalized == "false":
        return False
    raise ValueError(f"Expected true or false, got: {raw_value}")


def parse_legacy_value(raw_value: str) -> float | None:
    if raw_value.strip().lower() == "null":
        return None
    return parse_number(raw_value)


def make_backup(state_path: Path, state: dict[str, Any]) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = state_path.with_name(f"portfolio_state_backup_{timestamp}.json")
    counter = 1
    while backup_path.exists():
        backup_path = state_path.with_name(
            f"portfolio_state_backup_{timestamp}_{counter}.json"
        )
        counter += 1
    save_json(backup_path, state)
    return backup_path


def apply_updates(
    state: dict[str, Any],
    weekly_budget: float | None = None,
    monthly_budget: float | None = None,
    holdings: list[str] | None = None,
    legacy: list[str] | None = None,
    platforms: list[str] | None = None,
) -> dict[str, Any]:
    updated = deepcopy(state)

    if weekly_budget is not None:
        updated["weekly_investment_budget"] = weekly_budget
    if monthly_budget is not None:
        updated["monthly_investment_budget"] = monthly_budget

    for assignment in holdings or []:
        key, raw_value = parse_assignment(assignment)
        if key not in VALID_HOLDINGS:
            raise ValueError(f"Invalid holding asset: {key}")
        updated.setdefault("holdings", {})[key] = parse_number(raw_value)

    for assignment in legacy or []:
        key, raw_value = parse_assignment(assignment)
        if key not in VALID_LEGACY_KEYS:
            raise ValueError(f"Invalid legacy key: {key}")
        updated.setdefault("legacy_holdings", {})[key] = parse_legacy_value(raw_value)

    for assignment in platforms or []:
        key, raw_value = parse_assignment(assignment)
        if key not in VALID_PLATFORM_KEYS:
            raise ValueError(f"Invalid platform key: {key}")
        updated.setdefault("platform_status", {})[key] = parse_bool(raw_value)

    return updated


def changed_lines(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    lines = []
    keys = [
        "weekly_investment_budget",
        "monthly_investment_budget",
    ]
    for key in keys:
        if before.get(key) != after.get(key):
            lines.append(f"- {key}: {before.get(key)} -> {after.get(key)}")

    for section in ["holdings", "legacy_holdings", "platform_status"]:
        before_section = before.get(section, {})
        after_section = after.get(section, {})
        for key in sorted(set(before_section) | set(after_section)):
            if before_section.get(key) != after_section.get(key):
                lines.append(
                    f"- {section}.{key}: {before_section.get(key)} -> {after_section.get(key)}"
                )

    return lines or ["- No changes."]


def update_state_file(
    state_path: Path,
    weekly_budget: float | None = None,
    monthly_budget: float | None = None,
    holdings: list[str] | None = None,
    legacy: list[str] | None = None,
    platforms: list[str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    before = load_json(state_path)
    after = apply_updates(
        before,
        weekly_budget=weekly_budget,
        monthly_budget=monthly_budget,
        holdings=holdings,
        legacy=legacy,
        platforms=platforms,
    )
    backup_path = make_backup(state_path, before)
    save_json(state_path, after)
    return before, after, backup_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safely update portfolio_state.json.")
    parser.add_argument("--state-path", default="portfolio_state.json")
    parser.add_argument("--weekly-budget", type=float)
    parser.add_argument("--monthly-budget", type=float)
    parser.add_argument("--set-holding", action="append", default=[])
    parser.add_argument("--set-legacy", action="append", default=[])
    parser.add_argument("--set-platform", action="append", default=[])
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        before, after, backup_path = update_state_file(
            Path(args.state_path),
            weekly_budget=args.weekly_budget,
            monthly_budget=args.monthly_budget,
            holdings=args.set_holding,
            legacy=args.set_legacy,
            platforms=args.set_platform,
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print(f"Backup created: {backup_path}")
    print("Before/after summary:")
    for line in changed_lines(before, after):
        print(line)
    print("portfolio_state.json updated locally. No trades executed.")


if __name__ == "__main__":
    main()
