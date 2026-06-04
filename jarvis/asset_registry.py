"""Candidate asset registry for the read-only J.A.R.V.I.S. kernel."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ASSET_TYPES = {"ETF", "crypto", "cash", "fund", "stock", "bond", "other"}
APPROVAL_STATUSES = {
    "candidate_unreviewed",
    "candidate_data_incomplete",
    "candidate_reviewed",
    "approved_watchlist",
    "approved_investable",
    "rejected",
    "legacy_existing",
    "test_position",
}
COMMON_REQUIRED_FIELDS = (
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
)
ETF_REQUIRED_FIELDS = ("provider", "index_tracked", "replication_method")
CRYPTO_REQUIRED_FIELDS = ("network_or_protocol", "custody_platforms", "transferable", "mica_route_possible")


class AssetRegistryError(ValueError):
    """Raised when a candidate asset registry is unsafe or malformed."""


@dataclass(frozen=True)
class CandidateAsset:
    asset_id: str
    name: str
    asset_type: str
    sleeve: str
    ticker: str | None
    isin_or_symbol: str
    platforms: tuple[str, ...]
    currency: str
    domicile: str
    distribution_policy: str
    ter_or_fee: float
    data_source: str
    approval_status: str
    risk_level: str
    provider: str | None = None
    index_tracked: str | None = None
    replication_method: str | None = None
    network_or_protocol: str | None = None
    custody_platforms: tuple[str, ...] = ()
    transferable: bool | None = None
    mica_route_possible: bool | None = None
    multi_asset_allowed: bool = False


@dataclass(frozen=True)
class RegistryWarning:
    code: str
    message: str
    asset_id: str | None = None


@dataclass(frozen=True)
class AssetRegistry:
    assets: tuple[CandidateAsset, ...]
    warnings: tuple[RegistryWarning, ...]

    def by_id(self) -> dict[str, CandidateAsset]:
        return {asset.asset_id: asset for asset in self.assets}


def _require_field(raw: dict[str, Any], field: str, asset_label: str) -> Any:
    if field not in raw:
        raise AssetRegistryError(f"{asset_label} missing required field {field}.")
    return raw[field]


def _require_text(value: Any, field: str, asset_label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AssetRegistryError(f"{asset_label} field {field} must be non-empty text.")
    return value.strip()


def _optional_text(value: Any, field: str, asset_label: str) -> str | None:
    if value is None:
        return None
    return _require_text(value, field, asset_label)


def _require_string_list(value: Any, field: str, asset_label: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not value:
        raise AssetRegistryError(f"{asset_label} field {field} must be a non-empty list.")
    values = []
    for item in value:
        values.append(_require_text(item, field, asset_label))
    return tuple(values)


def _require_non_negative_number(value: Any, field: str, asset_label: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise AssetRegistryError(f"{asset_label} field {field} must be a number.")
    if value < 0:
        raise AssetRegistryError(f"{asset_label} field {field} must be non-negative.")
    return float(value)


def _require_bool(value: Any, field: str, asset_label: str) -> bool:
    if not isinstance(value, bool):
        raise AssetRegistryError(f"{asset_label} field {field} must be true or false.")
    return value


def _parse_asset(raw: dict[str, Any], seen_asset_ids: set[str], warnings: list[RegistryWarning]) -> CandidateAsset:
    asset_label = str(raw.get("asset_id", "<unknown asset>"))
    for field in COMMON_REQUIRED_FIELDS:
        _require_field(raw, field, asset_label)

    asset_id = _require_text(raw["asset_id"], "asset_id", asset_label)
    if asset_id in seen_asset_ids:
        raise AssetRegistryError(f"duplicate asset_id {asset_id}.")
    seen_asset_ids.add(asset_id)

    asset_type = _require_text(raw["asset_type"], "asset_type", asset_id)
    if asset_type not in ASSET_TYPES:
        raise AssetRegistryError(f"{asset_id} asset_type {asset_type} is invalid.")

    approval_status = _require_text(raw["approval_status"], "approval_status", asset_id)
    if approval_status not in APPROVAL_STATUSES:
        raise AssetRegistryError(f"{asset_id} approval_status {approval_status} is invalid.")

    ter_or_fee = _require_non_negative_number(raw["ter_or_fee"], "ter_or_fee", asset_id)
    currency = _require_text(raw["currency"], "currency", asset_id)
    if currency != "EUR":
        warnings.append(
            RegistryWarning(
                code="non_eur_currency",
                message=f"{asset_id} currency is {currency}; EUR base currency review required.",
                asset_id=asset_id,
            )
        )

    provider = index_tracked = replication_method = None
    network_or_protocol = None
    custody_platforms: tuple[str, ...] = ()
    transferable = mica_route_possible = None

    if asset_type == "ETF":
        for field in ETF_REQUIRED_FIELDS:
            _require_field(raw, field, asset_id)
        provider = _require_text(raw["provider"], "provider", asset_id)
        index_tracked = _require_text(raw["index_tracked"], "index_tracked", asset_id)
        replication_method = _require_text(raw["replication_method"], "replication_method", asset_id)

    if asset_type == "crypto":
        for field in CRYPTO_REQUIRED_FIELDS:
            _require_field(raw, field, asset_id)
        network_or_protocol = _require_text(raw["network_or_protocol"], "network_or_protocol", asset_id)
        custody_platforms = _require_string_list(raw["custody_platforms"], "custody_platforms", asset_id)
        transferable = _require_bool(raw["transferable"], "transferable", asset_id)
        mica_route_possible = _require_bool(raw["mica_route_possible"], "mica_route_possible", asset_id)

    return CandidateAsset(
        asset_id=asset_id,
        name=_require_text(raw["name"], "name", asset_id),
        asset_type=asset_type,
        sleeve=_require_text(raw["sleeve"], "sleeve", asset_id),
        ticker=_optional_text(raw["ticker"], "ticker", asset_id),
        isin_or_symbol=_require_text(raw["isin_or_symbol"], "isin_or_symbol", asset_id),
        platforms=_require_string_list(raw["platforms"], "platforms", asset_id),
        currency=currency,
        domicile=_require_text(raw["domicile"], "domicile", asset_id),
        distribution_policy=_require_text(raw["distribution_policy"], "distribution_policy", asset_id),
        ter_or_fee=ter_or_fee,
        data_source=_require_text(raw["data_source"], "data_source", asset_id),
        approval_status=approval_status,
        risk_level=_require_text(raw["risk_level"], "risk_level", asset_id),
        provider=provider,
        index_tracked=index_tracked,
        replication_method=replication_method,
        network_or_protocol=network_or_protocol,
        custody_platforms=custody_platforms,
        transferable=transferable,
        mica_route_possible=mica_route_possible,
        multi_asset_allowed=bool(raw.get("multi_asset_allowed", False)),
    )


def load_asset_registry(path: str | Path) -> AssetRegistry:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise AssetRegistryError("asset registry must be an object.")
    raw_assets = raw.get("assets")
    if not isinstance(raw_assets, list):
        raise AssetRegistryError("asset registry must contain an assets list.")

    warnings: list[RegistryWarning] = []
    seen_asset_ids: set[str] = set()
    assets: list[CandidateAsset] = []
    for raw_asset in raw_assets:
        if not isinstance(raw_asset, dict):
            raise AssetRegistryError("each asset must be an object.")
        assets.append(_parse_asset(raw_asset, seen_asset_ids, warnings))

    return AssetRegistry(tuple(assets), tuple(warnings))


def registry_summary(registry: AssetRegistry) -> dict[str, dict[str, int]]:
    summary = {"asset_type": {}, "approval_status": {}}
    for asset in registry.assets:
        summary["asset_type"][asset.asset_type] = summary["asset_type"].get(asset.asset_type, 0) + 1
        summary["approval_status"][asset.approval_status] = (
            summary["approval_status"].get(asset.approval_status, 0) + 1
        )
    return summary
