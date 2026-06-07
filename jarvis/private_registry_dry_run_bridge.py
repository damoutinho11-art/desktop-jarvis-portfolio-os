"""Bridge private status review previews into registry update dry-runs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .private_status_review_bridge import (
    PrivateStatusReviewBridgeResult,
    build_private_status_review_bridge_from_files,
)
from .registry_update_dry_run import RegistryUpdateDryRunResult, simulate_registry_update, write_registry_copy_from_dry_run


@dataclass(frozen=True)
class PrivateRegistryDryRunConfig:
    allow_write_helper: bool = False


@dataclass(frozen=True)
class PrivateRegistryDryRunBridgeResult:
    bridge_status: str
    private_status_review: PrivateStatusReviewBridgeResult
    dry_run: RegistryUpdateDryRunResult
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    registry_mutation_performed: bool = False
    approvals_executed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    return value


def load_private_registry_dry_run_config(path: str | Path) -> PrivateRegistryDryRunConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "private registry dry-run bridge config")
    allow_write_helper = raw.get("allow_write_helper", False)
    if not isinstance(allow_write_helper, bool):
        raise ValueError("allow_write_helper must be true or false.")
    return PrivateRegistryDryRunConfig(allow_write_helper=allow_write_helper)


def build_private_registry_dry_run_bridge(
    registry_path: str | Path,
    private_status_result: PrivateStatusReviewBridgeResult,
) -> PrivateRegistryDryRunBridgeResult:
    dry_run = simulate_registry_update(registry_path, private_status_result.status_requests)
    blockers = tuple(dict.fromkeys((*private_status_result.blockers, *dry_run.blockers)))
    warnings = tuple(dict.fromkeys((*private_status_result.warnings, *dry_run.warnings)))
    status = "DRY_RUN_READY" if dry_run.simulated_changes and not dry_run.blocked_changes else "BLOCKED"
    return PrivateRegistryDryRunBridgeResult(
        bridge_status=status,
        private_status_review=private_status_result,
        dry_run=dry_run,
        warnings=warnings,
        blockers=blockers,
        registry_mutation_performed=False,
        approvals_executed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_private_registry_dry_run_bridge_from_files(
    registry_path: str | Path,
    intake_path: str | Path,
    freshness_policy_path: str | Path,
    private_status_config_path: str | Path,
    private_registry_dry_run_config_path: str | Path,
) -> PrivateRegistryDryRunBridgeResult:
    load_private_registry_dry_run_config(private_registry_dry_run_config_path)
    private_status = build_private_status_review_bridge_from_files(
        registry_path,
        intake_path,
        freshness_policy_path,
        private_status_config_path,
    )
    return build_private_registry_dry_run_bridge(registry_path, private_status)


def write_private_registry_copy_from_dry_run(
    registry_path: str | Path,
    result: PrivateRegistryDryRunBridgeResult,
    output_path: str | Path,
) -> Path:
    return write_registry_copy_from_dry_run(registry_path, result.dry_run, output_path)
