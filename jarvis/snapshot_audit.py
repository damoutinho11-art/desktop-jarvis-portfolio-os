"""Deterministic text audit for manually-loaded J.A.R.V.I.S. snapshots."""

from __future__ import annotations

from pathlib import Path

from .manual_snapshot_loader import load_manual_snapshot
from .portfolio_schema import SnapshotValidationResult, ValidationWarning
from .portfolio_snapshot_engine import load_account_roles, load_constitution, validate_snapshot


def _money(value: float) -> str:
    return f"EUR {value:.2f}"


def build_snapshot_audit_report(
    result: SnapshotValidationResult,
    intake_warnings: list[ValidationWarning] | None = None,
) -> str:
    warnings = [*(intake_warnings or []), *result.warnings]
    totals = result.snapshot.classified_totals
    recommendations_blocked = not result.validation_passed
    lines = [
        "J.A.R.V.I.S. Snapshot Integrity Audit",
        f"status: {'valid' if result.validation_passed else 'blocked'}",
        f"as_of: {result.snapshot.as_of}",
        f"total cash: {_money(totals.get('total_cash', 0.0))}",
        f"protected cash: {_money(totals.get('protected_cash', 0.0))}",
        f"investable cash: {_money(totals.get('investable_cash', 0.0))}",
        f"legacy holdings: {_money(totals.get('legacy_holdings', 0.0))}",
        f"unapproved assets: {_money(totals.get('unapproved_assets', 0.0))}",
        f"recommendations blocked: {'yes' if recommendations_blocked else 'no'}",
        "warnings:",
    ]
    if warnings:
        for warning in warnings:
            lines.append(f"- {warning.code}: {warning.message}")
    else:
        lines.append("- none")
    lines.append("Manual approval required for all future actions.")
    lines.append("No trades executed.")
    return "\n".join(lines)


def audit_manual_snapshot(path: str | Path) -> str:
    constitution = load_constitution()
    account_roles = load_account_roles()
    snapshot, intake_warnings = load_manual_snapshot(path, account_roles)
    result = validate_snapshot(snapshot, constitution, account_roles)
    return build_snapshot_audit_report(result, intake_warnings)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Audit a manual J.A.R.V.I.S. portfolio snapshot.")
    parser.add_argument("snapshot_path", nargs="?", default="jarvis/data/manual_snapshot.example.json")
    args = parser.parse_args()
    print(audit_manual_snapshot(args.snapshot_path))


if __name__ == "__main__":
    main()
