"""Readable exposure and concentration report for local fixture data."""

from __future__ import annotations

from pathlib import Path

from .concentration_engine import (
    calculate_combined_top_holdings,
    calculate_country_exposure,
    calculate_largest_single_holding_exposure,
    calculate_pairwise_holding_overlap,
    calculate_sector_exposure,
    generate_concentration_warnings,
)
from .exposure_loader import AssetExposure, load_exposure_data


def _format_percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def _equal_asset_weights(assets: tuple[AssetExposure, ...]) -> dict[str, float]:
    if not assets:
        return {}
    weight = 1.0 / len(assets)
    return {asset.asset_id: weight for asset in assets}


def build_exposure_report(path: str | Path) -> str:
    snapshot = load_exposure_data(path)
    asset_weights = _equal_asset_weights(snapshot.assets)
    exposure_by_id = snapshot.by_asset_id()
    combined_holdings = calculate_combined_top_holdings(asset_weights, exposure_by_id)
    country_exposure = calculate_country_exposure(asset_weights, exposure_by_id)
    sector_exposure = calculate_sector_exposure(asset_weights, exposure_by_id)
    largest_holding, largest_weight = calculate_largest_single_holding_exposure(asset_weights, exposure_by_id)
    concentration_warnings = generate_concentration_warnings(asset_weights, exposure_by_id)

    lines = [
        "J.A.R.V.I.S. Exposure & Concentration Fixture Report",
        "Read-only local fixture. No recommendations generated.",
        f"as_of: {snapshot.as_of.isoformat()}",
        "",
        "asset weights used for report:",
    ]
    for asset_id, weight in sorted(asset_weights.items()):
        lines.append(f"- {asset_id}: {_format_percent(weight)}")

    lines.extend(["", "pairwise holding overlap:"])
    for index, asset_a in enumerate(snapshot.assets):
        for asset_b in snapshot.assets[index + 1 :]:
            overlap = calculate_pairwise_holding_overlap(asset_a, asset_b)
            lines.append(f"- {asset_a.asset_id} / {asset_b.asset_id}: {_format_percent(overlap)}")
    if len(snapshot.assets) < 2:
        lines.append("- n/a")

    lines.extend(["", "combined top holdings:"])
    for name, weight in combined_holdings[:10]:
        lines.append(f"- {name}: {_format_percent(weight)}")
    if not combined_holdings:
        lines.append("- none")

    lines.extend(["", "country exposure:"])
    for country, weight in country_exposure.items():
        lines.append(f"- {country}: {_format_percent(weight)}")
    if not country_exposure:
        lines.append("- none")

    lines.extend(["", "sector exposure:"])
    for sector, weight in sector_exposure.items():
        lines.append(f"- {sector}: {_format_percent(weight)}")
    if not sector_exposure:
        lines.append("- none")

    lines.extend(
        [
            "",
            f"largest single holding: {largest_holding or 'none'} at {_format_percent(largest_weight)}",
            "",
            "warnings:",
        ]
    )
    all_warnings = [*snapshot.warnings, *concentration_warnings]
    if all_warnings:
        lines.extend(f"- {warning}" for warning in all_warnings)
    else:
        lines.append("- none")
    lines.append("No trades executed.")
    return "\n".join(lines)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Report deterministic exposure metrics from local fixtures.")
    parser.add_argument("exposure_path", nargs="?", default="jarvis/data/asset_exposure.example.json")
    args = parser.parse_args()
    print(build_exposure_report(args.exposure_path))


if __name__ == "__main__":
    main()
