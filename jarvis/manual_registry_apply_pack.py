"""Manual approval pack for applying a safe registry status change to a copy."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .private_registry_dry_run_bridge import (
    PrivateRegistryDryRunBridgeResult,
    build_private_registry_dry_run_bridge_from_files,
    write_private_registry_copy_from_dry_run,
)


REQUIRED_CONFIRMATIONS = (
    "verified_evidence_reviewed",
    "freshness_reviewed",
    "dry_run_reviewed",
    "transition_is_candidate_review_only",
    "no_investable_approval",
    "no_buy_sell_request",
    "no_trade_execution",
    "write_copy_only",
)


@dataclass(frozen=True)
class ManualRegistryApplyConfig:
    target_asset_id: str
    output_path: str | None
    confirmations: tuple[str, ...]


@dataclass(frozen=True)
class ManualRegistryApplyApprovalPack:
    target_asset_id: str
    current_status: str | None
    requested_status: str | None
    dry_run_would_update: bool
    evidence_summary: str
    freshness_summary: str
    diff_summary: tuple[str, ...]
    required_confirmations: tuple[str, ...]
    apply_allowed: bool
    output_path_required: bool
    output_path: str | None
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")
    return value.strip()


def _optional_text(value: Any, field: str) -> str | None:
    if value is None:
        return None
    return _require_text(value, field)


def _require_text_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list.")
    return tuple(_require_text(item, field) for item in value)


def load_manual_registry_apply_config(path: str | Path) -> ManualRegistryApplyConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "manual registry apply pack config")
    return ManualRegistryApplyConfig(
        target_asset_id=_require_text(raw.get("target_asset_id"), "target_asset_id"),
        output_path=_optional_text(raw.get("output_path"), "output_path"),
        confirmations=_require_text_list(raw.get("confirmations", []), "confirmations"),
    )


def _same_path(left: str | Path, right: str | Path) -> bool:
    return Path(left).resolve() == Path(right).resolve()


def build_manual_registry_apply_pack(
    registry_path: str | Path,
    dry_run_result: PrivateRegistryDryRunBridgeResult,
    config: ManualRegistryApplyConfig,
) -> ManualRegistryApplyApprovalPack:
    matching_changes = [
        change for change in dry_run_result.dry_run.simulated_changes if change.asset_id == config.target_asset_id
    ]
    change = matching_changes[0] if matching_changes else None
    preview_by_asset = {
        preview.status_request.asset_id: preview
        for preview in dry_run_result.private_status_review.request_previews
    }
    preview = preview_by_asset.get(config.target_asset_id)
    blockers: list[str] = [*dry_run_result.blockers]
    warnings: list[str] = [*dry_run_result.warnings]

    current_status = change.current_status if change else None
    requested_status = change.requested_status if change else None
    dry_run_would_update = bool(change and change.would_update)
    diff_summary = change.diff_summary if change else ()
    evidence_summary = preview.status_request.evidence_summary if preview else ""
    freshness_summary = preview.freshness_summary if preview else ""

    missing_confirmations = tuple(sorted(set(REQUIRED_CONFIRMATIONS).difference(config.confirmations)))
    blockers.extend(f"missing confirmation: {confirmation}." for confirmation in missing_confirmations)
    if not dry_run_would_update:
        blockers.append(f"{config.target_asset_id}: dry-run did not produce an update.")
    if current_status != "candidate_unreviewed":
        blockers.append(f"{config.target_asset_id}: current_status must be candidate_unreviewed.")
    if requested_status != "candidate_reviewed":
        blockers.append(f"{config.target_asset_id}: requested_status must be candidate_reviewed.")
    if requested_status == "approved_investable":
        blockers.append(f"{config.target_asset_id}: approved_investable is forbidden in this layer.")
    if not config.output_path:
        blockers.append("explicit output_path is required.")
    elif _same_path(registry_path, config.output_path):
        blockers.append("output_path must not equal source registry path.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    return ManualRegistryApplyApprovalPack(
        target_asset_id=config.target_asset_id,
        current_status=current_status,
        requested_status=requested_status,
        dry_run_would_update=dry_run_would_update,
        evidence_summary=evidence_summary,
        freshness_summary=freshness_summary,
        diff_summary=diff_summary,
        required_confirmations=REQUIRED_CONFIRMATIONS,
        apply_allowed=not unique_blockers,
        output_path_required=True,
        output_path=config.output_path,
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=unique_blockers,
        approvals_created=False,
        registry_mutation_performed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_manual_registry_apply_pack_from_files(
    registry_path: str | Path,
    intake_path: str | Path,
    freshness_policy_path: str | Path,
    private_status_config_path: str | Path,
    private_registry_dry_run_config_path: str | Path,
    manual_apply_config_path: str | Path,
) -> ManualRegistryApplyApprovalPack:
    dry_run_result = build_private_registry_dry_run_bridge_from_files(
        registry_path,
        intake_path,
        freshness_policy_path,
        private_status_config_path,
        private_registry_dry_run_config_path,
    )
    return build_manual_registry_apply_pack(
        registry_path,
        dry_run_result,
        load_manual_registry_apply_config(manual_apply_config_path),
    )


def write_registry_copy_from_apply_pack(
    registry_path: str | Path,
    dry_run_result: PrivateRegistryDryRunBridgeResult,
    pack: ManualRegistryApplyApprovalPack,
    output_path: str | Path | None = None,
) -> Path:
    target = output_path or pack.output_path
    if not pack.apply_allowed:
        raise ValueError("manual registry apply pack is not apply_allowed.")
    if target is None:
        raise ValueError("explicit output path is required.")
    if _same_path(registry_path, target):
        raise ValueError("output path must not equal source registry path.")
    return write_private_registry_copy_from_dry_run(registry_path, dry_run_result, target)
