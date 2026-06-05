"""Read-only data quality report for enriched candidate asset registries."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .asset_registry import CRYPTO_REQUIRED_FIELDS, ETF_REQUIRED_FIELDS, load_asset_registry, registry_summary


COMMON_METADATA_FIELDS = (
    "asset_id",
    "name",
    "asset_type",
    "sleeve",
    "ticker",
    "isin_or_symbol",
    "platforms",
    "currency",
    "domicile",
    "distribution_policy",
    "ter_or_fee",
    "data_source",
    "approval_status",
    "risk_level",
    "notes",
)


def _raw_assets(path: str | Path) -> list[dict[str, Any]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    assets = raw.get("assets") if isinstance(raw, dict) else None
    if not isinstance(assets, list):
        return []
    return [asset for asset in assets if isinstance(asset, dict)]


def _count_by_sleeve(raw_assets: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for asset in raw_assets:
        sleeve = str(asset.get("sleeve", "<missing>"))
        counts[sleeve] = counts.get(sleeve, 0) + 1
    return dict(sorted(counts.items()))


def _missing_metadata_warnings(raw_assets: list[dict[str, Any]]) -> tuple[str, ...]:
    warnings: list[str] = []
    for asset in raw_assets:
        asset_id = str(asset.get("asset_id", "<unknown asset>"))
        required = list(COMMON_METADATA_FIELDS)
        if asset.get("asset_type") == "ETF":
            required.extend(ETF_REQUIRED_FIELDS)
        if asset.get("asset_type") == "crypto":
            required.extend(CRYPTO_REQUIRED_FIELDS)
        for field in required:
            value = asset.get(field)
            if value is None or value == "" or value == []:
                warnings.append(f"{asset_id}: missing metadata field {field}.")
    return tuple(warnings)


def build_candidate_data_quality_report(path: str | Path) -> str:
    registry = load_asset_registry(path)
    raw_assets = _raw_assets(path)
    summary = registry_summary(registry)
    by_sleeve = _count_by_sleeve(raw_assets)
    approval_counts = summary["approval_status"]
    approved_investable_count = approval_counts.get("approved_investable", 0)
    missing_warnings = _missing_metadata_warnings(raw_assets)
    non_eur_warnings = tuple(warning.message for warning in registry.warnings if warning.code == "non_eur_currency")

    lines = [
        "J.A.R.V.I.S. Candidate Data Quality Report",
        "Read-only candidate registry audit. No approvals, recommendations, or trades created.",
        f"total candidates: {len(registry.assets)}",
        "count by sleeve:",
    ]
    lines.extend(f"- {sleeve}: {count}" for sleeve, count in by_sleeve.items())
    lines.append("count by asset_type:")
    lines.extend(f"- {asset_type}: {count}" for asset_type, count in sorted(summary["asset_type"].items()))
    lines.append("count by approval_status:")
    lines.extend(f"- {status}: {count}" for status, count in sorted(approval_counts.items()))
    lines.extend(
        [
            "registry validation status: valid",
            "missing metadata warnings:",
        ]
    )
    lines.extend(f"- {warning}" for warning in missing_warnings) if missing_warnings else lines.append("- none")
    lines.append("non-EUR warnings:")
    lines.extend(f"- {warning}" for warning in non_eur_warnings) if non_eur_warnings else lines.append("- none")
    lines.extend(
        [
            f"approved_investable count: {approved_investable_count}",
            "allocation allowed: false",
            "Manual approval required for all future actions.",
            "No broker APIs.",
            "No buy/sell requests created.",
            "No trades executed.",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Report candidate registry data quality without approvals.")
    parser.add_argument("registry_path", nargs="?", default="jarvis/data/candidate_assets.v2.example.json")
    args = parser.parse_args()
    print(build_candidate_data_quality_report(args.registry_path))


if __name__ == "__main__":
    main()
