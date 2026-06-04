"""Exposure and concentration calculations for local fixture data."""

from __future__ import annotations

from .exposure_loader import AssetExposure


def _normalize_name(name: str) -> str:
    return " ".join(name.strip().lower().split())


def _exposure_map(exposures: dict[str, AssetExposure] | list[AssetExposure] | tuple[AssetExposure, ...]) -> dict[str, AssetExposure]:
    if isinstance(exposures, dict):
        return exposures
    return {asset.asset_id: asset for asset in exposures}


def _holding_weights(asset: AssetExposure) -> dict[str, float]:
    weights: dict[str, float] = {}
    for holding in asset.holdings:
        name = _normalize_name(holding.name)
        weights[name] = weights.get(name, 0.0) + holding.weight
    return weights


def calculate_pairwise_holding_overlap(asset_a: AssetExposure, asset_b: AssetExposure) -> float:
    weights_a = _holding_weights(asset_a)
    weights_b = _holding_weights(asset_b)
    overlap = 0.0
    for name, weight_a in weights_a.items():
        if name in weights_b:
            overlap += min(weight_a, weights_b[name])
    return round(overlap, 6)


def calculate_combined_top_holdings(
    asset_weights: dict[str, float],
    exposures: dict[str, AssetExposure] | list[AssetExposure] | tuple[AssetExposure, ...],
) -> list[tuple[str, float]]:
    exposure_by_id = _exposure_map(exposures)
    combined: dict[str, float] = {}
    for asset_id, portfolio_weight in asset_weights.items():
        asset = exposure_by_id.get(asset_id)
        if asset is None:
            continue
        for holding in asset.holdings:
            name = _normalize_name(holding.name)
            combined[name] = combined.get(name, 0.0) + portfolio_weight * holding.weight
    return sorted(((name, round(weight, 6)) for name, weight in combined.items()), key=lambda item: (-item[1], item[0]))


def calculate_country_exposure(
    asset_weights: dict[str, float],
    exposures: dict[str, AssetExposure] | list[AssetExposure] | tuple[AssetExposure, ...],
) -> dict[str, float]:
    exposure_by_id = _exposure_map(exposures)
    combined: dict[str, float] = {}
    for asset_id, portfolio_weight in asset_weights.items():
        asset = exposure_by_id.get(asset_id)
        if asset is None:
            continue
        for country, weight in asset.countries.items():
            combined[country] = combined.get(country, 0.0) + portfolio_weight * weight
    return dict(sorted((country, round(weight, 6)) for country, weight in combined.items()))


def calculate_sector_exposure(
    asset_weights: dict[str, float],
    exposures: dict[str, AssetExposure] | list[AssetExposure] | tuple[AssetExposure, ...],
) -> dict[str, float]:
    exposure_by_id = _exposure_map(exposures)
    combined: dict[str, float] = {}
    for asset_id, portfolio_weight in asset_weights.items():
        asset = exposure_by_id.get(asset_id)
        if asset is None:
            continue
        for sector, weight in asset.sectors.items():
            combined[sector] = combined.get(sector, 0.0) + portfolio_weight * weight
    return dict(sorted((sector, round(weight, 6)) for sector, weight in combined.items()))


def calculate_largest_single_holding_exposure(
    asset_weights: dict[str, float],
    exposures: dict[str, AssetExposure] | list[AssetExposure] | tuple[AssetExposure, ...],
) -> tuple[str | None, float]:
    holdings = calculate_combined_top_holdings(asset_weights, exposures)
    if not holdings:
        return None, 0.0
    return holdings[0]


def _value_for_key(exposure: dict[str, float], wanted: set[str]) -> float:
    total = 0.0
    for key, value in exposure.items():
        if _normalize_name(key) in wanted:
            total += value
    return round(total, 6)


def generate_concentration_warnings(
    asset_weights: dict[str, float],
    exposures: dict[str, AssetExposure] | list[AssetExposure] | tuple[AssetExposure, ...],
) -> list[str]:
    exposure_by_id = _exposure_map(exposures)
    warnings: list[str] = []
    for asset_id in sorted(asset_weights):
        asset = exposure_by_id.get(asset_id)
        if asset is None or (not asset.holdings and not asset.countries and not asset.sectors):
            warnings.append(f"{asset_id}: missing exposure data.")

    largest_name, largest_weight = calculate_largest_single_holding_exposure(asset_weights, exposure_by_id)
    if largest_name is not None and largest_weight > 0.10:
        warnings.append(f"largest single holding exposure is {largest_weight:.2%} in {largest_name}.")

    top_10_total = sum(weight for _, weight in calculate_combined_top_holdings(asset_weights, exposure_by_id)[:10])
    if top_10_total > 0.35:
        warnings.append(f"top 10 combined holdings exposure is {top_10_total:.2%}.")

    country_exposure = calculate_country_exposure(asset_weights, exposure_by_id)
    us_exposure = _value_for_key(country_exposure, {"us", "usa", "united states", "united states of america"})
    if us_exposure > 0.75:
        warnings.append(f"US country exposure is {us_exposure:.2%}.")

    sector_exposure = calculate_sector_exposure(asset_weights, exposure_by_id)
    technology_exposure = _value_for_key(sector_exposure, {"technology", "information technology", "tech"})
    if technology_exposure > 0.35:
        warnings.append(f"Technology sector exposure is {technology_exposure:.2%}.")

    return warnings
