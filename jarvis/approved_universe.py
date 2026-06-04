"""Approved universe builder for already-approved investable assets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .asset_approval_gate import check_asset_approval
from .asset_registry import CandidateAsset, load_asset_registry


@dataclass(frozen=True)
class ApprovedUniverse:
    approved_assets: tuple[CandidateAsset, ...]
    assets_by_sleeve: dict[str, tuple[CandidateAsset, ...]]
    assets_by_type: dict[str, int]
    warnings: tuple[str, ...]
    blocked_non_approved_count: int

    @property
    def total_approved_assets(self) -> int:
        return len(self.approved_assets)

    def to_dict(self) -> dict[str, object]:
        return {
            "total_approved_assets": self.total_approved_assets,
            "assets_by_sleeve": {
                sleeve: [asset.asset_id for asset in assets]
                for sleeve, assets in sorted(self.assets_by_sleeve.items())
            },
            "assets_by_type": dict(sorted(self.assets_by_type.items())),
            "warnings": list(self.warnings),
            "blocked_non_approved_count": self.blocked_non_approved_count,
            "manual_approval_required_for_future_actions": True,
        }


def _has_flag(asset: CandidateAsset, flag: str) -> bool:
    return bool(getattr(asset, flag, False))


def _validate_approved_asset(asset: CandidateAsset, warnings: list[str]) -> None:
    for field in ("asset_id", "asset_type", "sleeve", "currency", "risk_level"):
        if not getattr(asset, field):
            warnings.append(f"{asset.asset_id}: missing {field}.")
    if asset.ter_or_fee is None:
        warnings.append(f"{asset.asset_id}: missing ter_or_fee.")
    if not asset.platforms:
        warnings.append(f"{asset.asset_id}: missing platform.")
    if asset.currency != "EUR":
        warnings.append(f"{asset.asset_id}: currency is {asset.currency}; EUR base currency review required.")
    if asset.risk_level == "high":
        warnings.append(f"{asset.asset_id}: high risk asset.")
    if asset.risk_level == "very_high":
        warnings.append(f"{asset.asset_id}: very_high risk asset.")


def build_approved_universe(
    registry_path: str | Path,
    etf_universe_expected: bool = True,
    crypto_universe_expected: bool = True,
) -> ApprovedUniverse:
    registry = load_asset_registry(registry_path)
    approved: list[CandidateAsset] = []
    blocked_count = 0
    warnings: list[str] = []

    for asset in registry.assets:
        gate = check_asset_approval(asset)
        if gate.eligible_for_allocation:
            approved.append(asset)
            _validate_approved_asset(asset, warnings)
        else:
            blocked_count += 1

    assets_by_sleeve_lists: dict[str, list[CandidateAsset]] = {}
    assets_by_type: dict[str, int] = {}
    for asset in approved:
        assets_by_sleeve_lists.setdefault(asset.sleeve, []).append(asset)
        assets_by_type[asset.asset_type] = assets_by_type.get(asset.asset_type, 0) + 1

    if not approved:
        warnings.append("no approved assets in universe.")
    if etf_universe_expected and "global_core" not in assets_by_sleeve_lists and "global_core_etf" not in assets_by_sleeve_lists:
        warnings.append("missing global_core sleeve while ETF universe is expected.")
    if crypto_universe_expected and "crypto_core" not in assets_by_sleeve_lists and "btc" not in assets_by_sleeve_lists:
        warnings.append("missing crypto_core sleeve while crypto universe is expected.")

    for sleeve, assets in sorted(assets_by_sleeve_lists.items()):
        if len(assets) > 1 and not any(_has_flag(asset, "multi_asset_allowed") for asset in assets):
            warnings.append(f"{sleeve}: multiple approved assets without explicit multi_asset_allowed flag.")

    return ApprovedUniverse(
        approved_assets=tuple(sorted(approved, key=lambda asset: asset.asset_id)),
        assets_by_sleeve={
            sleeve: tuple(sorted(assets, key=lambda asset: asset.asset_id))
            for sleeve, assets in sorted(assets_by_sleeve_lists.items())
        },
        assets_by_type=dict(sorted(assets_by_type.items())),
        warnings=tuple(dict.fromkeys(warnings)),
        blocked_non_approved_count=blocked_count,
    )


def write_approved_universe_example(
    universe: ApprovedUniverse,
    path: str | Path = "jarvis/data/approved_universe.example.json",
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(universe.to_dict(), indent=2, sort_keys=True), encoding="utf-8")
    return target
