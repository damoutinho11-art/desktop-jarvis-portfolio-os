"""Readable portfolio drift report."""

from __future__ import annotations

from pathlib import Path

from .portfolio_drift import analyze_portfolio_drift


def _money(value: float) -> str:
    return f"EUR {value:.2f}"


def _percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def build_portfolio_drift_report(
    snapshot_path: str | Path,
    policy_path: str | Path,
    registry_path: str | Path,
) -> str:
    result = analyze_portfolio_drift(snapshot_path, policy_path, registry_path)
    lines = [
        "J.A.R.V.I.S. Portfolio Drift Report",
        "Read-only drift diagnostics. No recommendations generated.",
        f"total portfolio value: {_money(result.total_portfolio_value_eur)}",
        f"investable value: {_money(result.total_investable_value_eur)}",
        f"protected cash: {_money(result.protected_cash_eur)}",
        f"legacy value: {_money(result.legacy_value_eur)}",
        f"unapproved value: {_money(result.unapproved_value_eur)}",
        f"test position value: {_money(result.test_position_value_eur)}",
        "sleeve drift table:",
    ]
    for sleeve_id in sorted(result.sleeve_target_weights):
        lines.append(
            f"- {sleeve_id}: current={_percent(result.sleeve_current_weights[sleeve_id])}, "
            f"target={_percent(result.sleeve_target_weights[sleeve_id])}, "
            f"drift={_percent(result.sleeve_drift[sleeve_id])}, "
            f"status={result.sleeve_band_status[sleeve_id]}"
        )
    lines.append("blockers:")
    if result.blockers:
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("- none")
    lines.append("warnings:")
    if result.warnings:
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("- none")
    lines.append(f"allocation_ready: {result.allocation_ready}")
    lines.append("Manual approval still required.")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Analyze read-only portfolio drift against policy.")
    parser.add_argument("snapshot_path", nargs="?", default="jarvis/data/manual_snapshot.example.json")
    parser.add_argument("policy_path", nargs="?", default="jarvis/data/portfolio_policy.example.json")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.example.json")
    args = parser.parse_args()
    print(build_portfolio_drift_report(args.snapshot_path, args.policy_path, args.registry_path))


if __name__ == "__main__":
    main()
