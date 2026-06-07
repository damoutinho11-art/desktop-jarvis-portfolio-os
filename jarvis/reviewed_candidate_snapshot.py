"""Reviewed candidate snapshot checks for a private registry copy.

This module compares the public seed registry with a private reviewed copy and
summarizes whether one safe candidate-review transition is present. It is
read-only by default and never mutates registry files.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evidence_freshness_policy import build_evidence_freshness_pack_from_files
from .verified_evidence_intake import build_verified_evidence_pack_from_files


ALLOWED_TRANSITION = ("candidate_unreviewed", "candidate_reviewed")
DEFAULT_TARGET_ASSET_ID = "vwce_global_core_candidate"
FUTURE_GATES_REQUIRED = (
    "approved_watchlist_review_required",
    "investable_approval_required",
    "portfolio_policy_check_required",
    "concentration_check_required",
    "contribution_plan_required",
    "manual_approval_required",
)


@dataclass(frozen=True)
class ReviewedCandidateSnapshotConfig:
    target_asset_id: str = DEFAULT_TARGET_ASSET_ID


@dataclass(frozen=True)
class RegistryDiff:
    asset_id: str
    field: str
    before: Any
    after: Any


@dataclass(frozen=True)
class ReviewedCandidateSnapshot:
    snapshot_status: str
    asset_id: str
    name: str | None
    asset_type: str | None
    previous_status: str | None
    current_status: str | None
    status_transition: str
    evidence_types_verified: tuple[str, ...]
    verified_evidence_count: int
    freshness_summary: tuple[str, ...]
    freshness_status: str
    source_count: int
    private_evidence_present: bool
    future_gates_required: tuple[str, ...]
    registry_diffs: tuple[RegistryDiff, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    not_approved_investable: bool
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    registry_mutation_performed: bool = False


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")
    return value.strip()


def load_reviewed_candidate_snapshot_config(path: str | Path) -> ReviewedCandidateSnapshotConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "reviewed candidate snapshot config")
    return ReviewedCandidateSnapshotConfig(
        target_asset_id=_require_text(raw.get("target_asset_id", DEFAULT_TARGET_ASSET_ID), "target_asset_id")
    )


def _load_registry_assets(path: str | Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "candidate registry")
    assets = raw.get("assets")
    if not isinstance(assets, list):
        raise ValueError("candidate registry must contain an assets list.")
    by_id: dict[str, dict[str, Any]] = {}
    for raw_asset in assets:
        asset = _require_mapping(raw_asset, "candidate asset")
        asset_id = _require_text(asset.get("asset_id"), "asset_id")
        if asset_id in by_id:
            raise ValueError(f"duplicate asset_id {asset_id}.")
        by_id[asset_id] = asset
    return raw, by_id


def _registry_diffs(
    source_assets: dict[str, dict[str, Any]],
    reviewed_assets: dict[str, dict[str, Any]],
) -> tuple[RegistryDiff, ...]:
    diffs: list[RegistryDiff] = []
    for asset_id in sorted(set(source_assets).union(reviewed_assets)):
        before_asset = source_assets.get(asset_id)
        after_asset = reviewed_assets.get(asset_id)
        if before_asset is None or after_asset is None:
            diffs.append(RegistryDiff(asset_id=asset_id, field="__asset__", before=before_asset, after=after_asset))
            continue
        for field in sorted(set(before_asset).union(after_asset)):
            before = before_asset.get(field)
            after = after_asset.get(field)
            if before != after:
                diffs.append(RegistryDiff(asset_id=asset_id, field=field, before=before, after=after))
    return tuple(diffs)


def _is_allowed_diff(diff: RegistryDiff, target_asset_id: str) -> bool:
    return (
        diff.asset_id == target_asset_id
        and diff.field == "approval_status"
        and diff.before == ALLOWED_TRANSITION[0]
        and diff.after == ALLOWED_TRANSITION[1]
    )


def _target_records(verified_pack: Any, target_asset_id: str) -> tuple[Any, ...]:
    return tuple(
        result.record
        for result in verified_pack.validation_results
        if result.record is not None and result.record.asset_id == target_asset_id and result.record.verified_by_user
    )


def build_reviewed_candidate_snapshot(
    source_registry_path: str | Path,
    reviewed_registry_path: str | Path,
    verified_evidence_intake_path: str | Path,
    freshness_policy_path: str | Path,
    config: ReviewedCandidateSnapshotConfig,
) -> ReviewedCandidateSnapshot:
    _, source_assets = _load_registry_assets(source_registry_path)
    _, reviewed_assets = _load_registry_assets(reviewed_registry_path)
    target_id = config.target_asset_id
    blockers: list[str] = []
    warnings: list[str] = []

    source_asset = source_assets.get(target_id)
    reviewed_asset = reviewed_assets.get(target_id)
    if source_asset is None:
        blockers.append(f"{target_id}: target asset missing from source registry.")
    if reviewed_asset is None:
        blockers.append(f"{target_id}: target asset missing from reviewed registry copy.")

    previous_status = source_asset.get("approval_status") if source_asset else None
    current_status = reviewed_asset.get("approval_status") if reviewed_asset else None
    name = reviewed_asset.get("name") if reviewed_asset else (source_asset.get("name") if source_asset else None)
    asset_type = reviewed_asset.get("asset_type") if reviewed_asset else (source_asset.get("asset_type") if source_asset else None)
    status_transition = f"{previous_status} -> {current_status}"
    if (previous_status, current_status) != ALLOWED_TRANSITION:
        blockers.append(f"{target_id}: only candidate_unreviewed -> candidate_reviewed is allowed.")
    if current_status == "approved_investable":
        blockers.append(f"{target_id}: approved_investable is forbidden in this snapshot layer.")

    diffs = _registry_diffs(source_assets, reviewed_assets)
    unexpected_diffs = tuple(diff for diff in diffs if not _is_allowed_diff(diff, target_id))
    blockers.extend(
        f"{diff.asset_id}: unexpected reviewed registry diff in {diff.field}."
        for diff in unexpected_diffs
    )

    verified_pack = build_verified_evidence_pack_from_files(reviewed_registry_path, verified_evidence_intake_path)
    freshness_pack = build_evidence_freshness_pack_from_files(
        reviewed_registry_path,
        verified_evidence_intake_path,
        freshness_policy_path,
    )
    target_records = _target_records(verified_pack, target_id)
    evidence_types_verified = tuple(sorted({record.evidence_type for record in target_records}))
    source_count = len({record.source_name for record in target_records})
    private_evidence_present = bool(target_records)
    if target_id not in verified_pack.assets_with_real_status_promotion_allowed:
        blockers.append(f"{target_id}: verified evidence missing or provenance gate not passed.")

    target_freshness = tuple(result for result in freshness_pack.results if result.asset_id == target_id)
    freshness_summary = tuple(
        f"{result.evidence_type}: {result.freshness_status}"
        for result in sorted(target_freshness, key=lambda item: item.evidence_type)
    )
    if not target_freshness:
        blockers.append(f"{target_id}: freshness evidence results are missing.")
        freshness_status = "missing"
    elif all(result.freshness_status == "fresh" for result in target_freshness):
        freshness_status = "fresh"
    else:
        freshness_status = "blocked"
        blockers.append(f"{target_id}: verified evidence is missing, stale, or invalid.")

    warnings.extend(
        warning
        for result in verified_pack.validation_results
        if result.asset_id == target_id
        for warning in result.warnings
    )
    warnings.extend(freshness_pack.summary.warnings)
    blockers.extend(
        blocker
        for result in verified_pack.validation_results
        if result.asset_id == target_id
        for blocker in result.blockers
    )
    blockers.extend(freshness_pack.summary.blockers)

    unique_blockers = tuple(dict.fromkeys(blockers))
    return ReviewedCandidateSnapshot(
        snapshot_status="READY" if not unique_blockers else "BLOCKED",
        asset_id=target_id,
        name=str(name) if name is not None else None,
        asset_type=str(asset_type) if asset_type is not None else None,
        previous_status=str(previous_status) if previous_status is not None else None,
        current_status=str(current_status) if current_status is not None else None,
        status_transition=status_transition,
        evidence_types_verified=evidence_types_verified,
        verified_evidence_count=len(target_records),
        freshness_summary=freshness_summary,
        freshness_status=freshness_status,
        source_count=source_count,
        private_evidence_present=private_evidence_present,
        future_gates_required=FUTURE_GATES_REQUIRED,
        registry_diffs=diffs,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        not_approved_investable=current_status != "approved_investable",
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
        registry_mutation_performed=False,
    )


def build_reviewed_candidate_snapshot_from_files(
    source_registry_path: str | Path,
    reviewed_registry_path: str | Path,
    verified_evidence_intake_path: str | Path,
    freshness_policy_path: str | Path,
    snapshot_config_path: str | Path,
) -> ReviewedCandidateSnapshot:
    return build_reviewed_candidate_snapshot(
        source_registry_path,
        reviewed_registry_path,
        verified_evidence_intake_path,
        freshness_policy_path,
        load_reviewed_candidate_snapshot_config(snapshot_config_path),
    )
