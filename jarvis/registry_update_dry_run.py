"""Dry-run simulator for manual candidate registry status updates."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .asset_registry import AssetRegistry, CandidateAsset, load_asset_registry
from .asset_status_workflow import AssetStatusChangeRequest, parse_asset_status_request, validate_asset_status_request
from .real_status_review_bridge import build_real_status_review_bridge_from_files
from .status_request_audit_pack import audit_status_request


@dataclass(frozen=True)
class SimulatedRegistryChange:
    asset_id: str
    current_status: str
    requested_status: str
    would_update: bool
    before_record: dict[str, Any] | None
    after_record: dict[str, Any] | None
    diff_summary: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "current_status": self.current_status,
            "requested_status": self.requested_status,
            "would_update": self.would_update,
            "before_record": self.before_record,
            "after_record": self.after_record,
            "diff_summary": list(self.diff_summary),
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class RegistryUpdateDryRunResult:
    dry_run_status: str
    total_request_previews: int
    simulated_changes: tuple[SimulatedRegistryChange, ...]
    blocked_changes: tuple[SimulatedRegistryChange, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    registry_mutation_performed: bool = False
    approvals_executed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "dry_run_status": self.dry_run_status,
            "total_request_previews": self.total_request_previews,
            "simulated_changes": [change.to_dict() for change in self.simulated_changes],
            "blocked_changes": [change.to_dict() for change in self.blocked_changes],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "registry_mutation_performed": self.registry_mutation_performed,
            "approvals_executed": self.approvals_executed,
            "buy_sell_requests_created": self.buy_sell_requests_created,
            "trades_executed": self.trades_executed,
        }


def _asset_record(asset: CandidateAsset) -> dict[str, Any]:
    record = asdict(asset)
    for key, value in list(record.items()):
        if isinstance(value, tuple):
            record[key] = list(value)
    return record


def _blocked_change(
    request: AssetStatusChangeRequest,
    blockers: tuple[str, ...],
    warnings: tuple[str, ...] = (),
    before_record: dict[str, Any] | None = None,
) -> SimulatedRegistryChange:
    return SimulatedRegistryChange(
        asset_id=request.asset_id,
        current_status=request.current_status,
        requested_status=request.requested_status,
        would_update=False,
        before_record=before_record,
        after_record=None,
        diff_summary=(),
        warnings=warnings,
        blockers=blockers,
    )


def load_request_previews_from_bridge_config(
    registry_path: str | Path,
    bridge_config_path: str | Path,
) -> tuple[AssetStatusChangeRequest, ...]:
    raw = json.loads(Path(bridge_config_path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("real status review bridge config must be an object.")
    if isinstance(raw.get("status_requests"), list):
        return tuple(parse_asset_status_request(item) for item in raw["status_requests"])

    sources_path = raw.get("source_evidence_path")
    promotion_path = raw.get("verified_evidence_promotion_path")
    if not isinstance(sources_path, str) or not isinstance(promotion_path, str):
        raise ValueError("bridge config must contain status_requests or source/promotion paths.")
    return build_real_status_review_bridge_from_files(registry_path, sources_path, promotion_path).status_requests


def simulate_registry_update(
    registry_path: str | Path | AssetRegistry,
    requests: tuple[AssetStatusChangeRequest, ...] | list[AssetStatusChangeRequest],
) -> RegistryUpdateDryRunResult:
    registry = load_asset_registry(registry_path) if not isinstance(registry_path, AssetRegistry) else registry_path
    assets_by_id = registry.by_id()
    simulated: list[SimulatedRegistryChange] = []
    blocked: list[SimulatedRegistryChange] = []
    warnings: list[str] = []
    blockers: list[str] = []

    for request in requests:
        asset = assets_by_id.get(request.asset_id)
        before_record = _asset_record(asset) if asset is not None else None
        line_blockers: list[str] = []
        if asset is None:
            line_blockers.append(f"{request.asset_id}: asset not found in registry.")
        elif asset.approval_status != request.current_status:
            line_blockers.append(
                f"{request.asset_id}: registry status {asset.approval_status} does not match request current_status {request.current_status}."
            )

        validation = validate_asset_status_request(request)
        audit = audit_status_request(request, asset.sleeve if asset is not None else "unknown")
        line_blockers.extend(validation.blockers)
        line_blockers.extend(audit.blockers)
        line_warnings = tuple(dict.fromkeys((*validation.warnings, *audit.warnings)))
        if line_blockers or not validation.valid or not audit.audit_ready or asset is None:
            unique_blockers = tuple(dict.fromkeys(line_blockers))
            blocked.append(_blocked_change(request, unique_blockers, line_warnings, before_record))
            blockers.extend(unique_blockers)
            warnings.extend(line_warnings)
            continue

        after_record = dict(before_record)
        after_record["approval_status"] = request.requested_status
        simulated.append(
            SimulatedRegistryChange(
                asset_id=request.asset_id,
                current_status=request.current_status,
                requested_status=request.requested_status,
                would_update=True,
                before_record=before_record,
                after_record=after_record,
                diff_summary=(f"approval_status: {request.current_status} -> {request.requested_status}",),
                warnings=line_warnings,
                blockers=(),
            )
        )
        warnings.extend(line_warnings)

    status = "DRY_RUN_READY" if simulated and not blocked else "PARTIAL" if simulated else "BLOCKED"
    return RegistryUpdateDryRunResult(
        dry_run_status=status,
        total_request_previews=len(tuple(requests)),
        simulated_changes=tuple(simulated),
        blocked_changes=tuple(blocked),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        registry_mutation_performed=False,
        approvals_executed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def simulate_registry_update_from_files(
    registry_path: str | Path,
    bridge_config_path: str | Path,
) -> RegistryUpdateDryRunResult:
    requests = load_request_previews_from_bridge_config(registry_path, bridge_config_path)
    return simulate_registry_update(registry_path, requests)


def write_registry_copy_from_dry_run(
    registry_path: str | Path,
    result: RegistryUpdateDryRunResult,
    output_path: str | Path,
) -> Path:
    if result.blocked_changes:
        raise ValueError("cannot write registry copy when dry-run contains blocked changes.")
    if not result.simulated_changes:
        raise ValueError("cannot write registry copy with no simulated changes.")

    updates = {change.asset_id: change.requested_status for change in result.simulated_changes if change.would_update}
    raw = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict) or not isinstance(raw.get("assets"), list):
        raise ValueError("registry must contain an assets list.")
    for asset in raw["assets"]:
        if isinstance(asset, dict) and asset.get("asset_id") in updates:
            asset["approval_status"] = updates[str(asset["asset_id"])]

    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(raw, indent=2, sort_keys=True), encoding="utf-8")
    return target
