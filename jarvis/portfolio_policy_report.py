"""Readable portfolio policy coverage report."""

from __future__ import annotations

from pathlib import Path

from .portfolio_policy import load_policy_and_validate_universe


def _percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def build_portfolio_policy_report(policy_path: str | Path, registry_path: str | Path) -> str:
    result = load_policy_and_validate_universe(policy_path, registry_path)
    policy = result.policy
    universe = result.approved_universe
    lines = [
        "J.A.R.V.I.S. Portfolio Target Policy Report",
        "Read-only policy coverage check. No recommendations generated.",
        f"policy: {policy.name}",
        f"version: {policy.version}",
        f"base_currency: {policy.base_currency}",
        "sleeve targets and bands:",
    ]
    for sleeve in policy.sleeves:
        lines.append(
            f"- {sleeve.sleeve_id}: target={_percent(sleeve.target_weight)}, "
            f"band={_percent(sleeve.min_weight)}-{_percent(sleeve.max_weight)}, "
            f"required={sleeve.required}, max_assets={sleeve.max_assets}"
        )
    lines.append("constraints:")
    for key in sorted(policy.constraints):
        lines.append(f"- {key}: {policy.constraints[key]}")
    lines.append("approved universe coverage:")
    lines.append(f"- total approved assets: {universe.total_approved_assets}")
    for sleeve_id, assets in universe.assets_by_sleeve.items():
        lines.append(f"- {sleeve_id}: {', '.join(asset.asset_id for asset in assets)}")
    if not universe.assets_by_sleeve:
        lines.append("- none")
    lines.append("warnings:")
    if result.warnings:
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("- none")
    lines.append(f"allocation_ready: {result.allocation_ready}")
    lines.append(f"manual_approval_required: {policy.manual_approval_required}")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Validate portfolio policy against the approved universe.")
    parser.add_argument("policy_path", nargs="?", default="jarvis/data/portfolio_policy.example.json")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.example.json")
    args = parser.parse_args()
    print(build_portfolio_policy_report(args.policy_path, args.registry_path))


if __name__ == "__main__":
    main()
