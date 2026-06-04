"""Local exposure fixture loader for the read-only J.A.R.V.I.S. kernel."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Any


class ExposureDataError(ValueError):
    """Raised when local exposure fixture input is malformed."""


@dataclass(frozen=True)
class ExposureHolding:
    name: str
    weight: float


@dataclass(frozen=True)
class AssetExposure:
    asset_id: str
    holdings: tuple[ExposureHolding, ...]
    countries: dict[str, float]
    sectors: dict[str, float]


@dataclass(frozen=True)
class ExposureSnapshot:
    as_of: date
    assets: tuple[AssetExposure, ...]
    warnings: tuple[str, ...]

    def by_asset_id(self) -> dict[str, AssetExposure]:
        return {asset.asset_id: asset for asset in self.assets}


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ExposureDataError(f"{label} must be an object.")
    return value


def _require_text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ExposureDataError(f"{label} exists and must be text.")
    return value.strip()


def _parse_iso_date(value: Any, label: str) -> date:
    text = _require_text(value, label)
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError as exc:
        raise ExposureDataError(f"{label} must be a parseable ISO date.") from exc


def _parse_non_negative_weight(value: Any, label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ExposureDataError(f"{label} must be a number.")
    if value < 0:
        raise ExposureDataError(f"{label} must be non-negative.")
    return float(value)


def _load_weight_dict(value: Any, label: str) -> dict[str, float]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ExposureDataError(f"{label} must be an object.")
    parsed: dict[str, float] = {}
    for key, weight in value.items():
        parsed[_require_text(key, f"{label} key")] = _parse_non_negative_weight(weight, f"{label} weight")
    return parsed


def _warn_if_sum_high(asset_id: str, label: str, total: float, warnings: list[str]) -> None:
    if total > 1.05:
        warnings.append(f"{asset_id}: {label} weights sum to {total:.4f}, materially above 1.05.")


def load_exposure_data(path: str | Path) -> ExposureSnapshot:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "exposure data")
    as_of = _parse_iso_date(raw.get("as_of"), "as_of")
    raw_assets = raw.get("assets")
    if not isinstance(raw_assets, list) or not raw_assets:
        raise ExposureDataError("assets must be a non-empty list.")

    warnings: list[str] = []
    assets: list[AssetExposure] = []
    seen_asset_ids: set[str] = set()
    for index, raw_asset_value in enumerate(raw_assets):
        raw_asset = _require_mapping(raw_asset_value, f"assets[{index}]")
        asset_id = _require_text(raw_asset.get("asset_id"), "asset_id")
        if asset_id in seen_asset_ids:
            raise ExposureDataError(f"duplicate asset_id {asset_id}.")
        seen_asset_ids.add(asset_id)

        raw_holdings = raw_asset.get("holdings", [])
        if raw_holdings is None:
            raw_holdings = []
        if not isinstance(raw_holdings, list):
            raise ExposureDataError(f"{asset_id} holdings must be a list.")
        holdings: list[ExposureHolding] = []
        for holding_index, raw_holding_value in enumerate(raw_holdings):
            raw_holding = _require_mapping(raw_holding_value, f"{asset_id} holdings[{holding_index}]")
            name = _require_text(raw_holding.get("name"), "holding name")
            weight = _parse_non_negative_weight(raw_holding.get("weight"), "holding weight")
            holdings.append(ExposureHolding(name, weight))

        countries = _load_weight_dict(raw_asset.get("countries"), f"{asset_id} countries")
        sectors = _load_weight_dict(raw_asset.get("sectors"), f"{asset_id} sectors")

        if not holdings:
            warnings.append(f"{asset_id}: missing holding exposure data.")
        elif len(holdings) < 3:
            warnings.append(f"{asset_id}: sparse holding exposure data.")
        if not countries:
            warnings.append(f"{asset_id}: missing country exposure data.")
        if not sectors:
            warnings.append(f"{asset_id}: missing sector exposure data.")

        _warn_if_sum_high(asset_id, "holding", sum(holding.weight for holding in holdings), warnings)
        _warn_if_sum_high(asset_id, "country", sum(countries.values()), warnings)
        _warn_if_sum_high(asset_id, "sector", sum(sectors.values()), warnings)
        assets.append(AssetExposure(asset_id, tuple(holdings), countries, sectors))

    return ExposureSnapshot(as_of, tuple(assets), tuple(warnings))
