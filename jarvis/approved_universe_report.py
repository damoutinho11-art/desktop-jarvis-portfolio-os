"""Readable approved universe report."""

from __future__ import annotations

from pathlib import Path

from .approved_universe import build_approved_universe


def build_approved_universe_report(registry_path: str | Path) -> str:
    universe = build_approved_universe(registry_path)
    lines = [
        "J.A.R.V.I.S. Approved Universe Report",
        "Read-only registry view. No recommendations generated.",
        f"total approved assets: {universe.total_approved_assets}",
        f"blocked/non-approved assets count: {universe.blocked_non_approved_count}",
        "assets by sleeve:",
    ]
    if universe.assets_by_sleeve:
        for sleeve, assets in universe.assets_by_sleeve.items():
            lines.append(f"- {sleeve}: {', '.join(asset.asset_id for asset in assets)}")
    else:
        lines.append("- none")
    lines.append("assets by type:")
    if universe.assets_by_type:
        for asset_type, count in universe.assets_by_type.items():
            lines.append(f"- {asset_type}: {count}")
    else:
        lines.append("- none")
    lines.append("warnings:")
    if universe.warnings:
        lines.extend(f"- {warning}" for warning in universe.warnings)
    else:
        lines.append("- none")
    lines.append("Manual approval remains required for all future actions.")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Build a read-only approved universe report.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.example.json")
    args = parser.parse_args()
    print(build_approved_universe_report(args.registry_path))


if __name__ == "__main__":
    main()
