"""J.A.R.V.I.S. v9.1 capability map and roadmap lock.

Prevents the roadmap from circling back into already-built public-data planning
stages.

This stage does not add a new planner.
This stage does not select sources again.
This stage does not enable live fetching.

Safety boundary:
- capability map and roadmap lock only
- no live public fetch
- no network calls
- no raw response storage
- no live adapter record emission
- no buy request creation
- no broker/API connection
- no order placement
- no trade execution
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


STATUS_READY = "JARVIS_V9_1_CAPABILITY_MAP_AND_ROADMAP_LOCK_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V9_1_CAPABILITY_MAP_AND_ROADMAP_LOCK_BLOCKED_SAFE"

ROADMAP_LOCK_READY = "CAPABILITY_MAP_AND_ROADMAP_LOCK_READY"
ROADMAP_LOCK_BLOCKED = "CAPABILITY_MAP_AND_ROADMAP_LOCK_BLOCKED"

NEXT_STAGE = "v10_0_autonomous_public_data_refresh_runtime"

CURRENT_STAGE = "v9_1_capability_map_and_roadmap_lock"

REDUNDANT_SOURCE_SELECTION_STAGE = "v9_0_public_market_data" + "_source_selection_plan"
REDUNDANT_DRY_RUN_ENABLEMENT_STAGE = "v9_1_controlled_public_data" + "_dry_run_enablement_plan"

_ACTIVE_V8_4_NEXT_STAGE = "v9_0_public_market_data_enablement_decision_layer"
_ACTIVE_V9_0_NEXT_STAGE = CURRENT_STAGE


@dataclass(frozen=True)
class CapabilityMapEntry:
    capability_id: str
    group: str
    stage_or_module: str
    file_path: str
    purpose: str
    exists: bool
    makes_redundant: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability_id": self.capability_id,
            "group": self.group,
            "stage_or_module": self.stage_or_module,
            "file_path": self.file_path,
            "purpose": self.purpose,
            "exists": self.exists,
            "makes_redundant": list(self.makes_redundant),
        }


@dataclass(frozen=True)
class RoadmapReference:
    file_path: str
    expected_reference: str
    found: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "expected_reference": self.expected_reference,
            "found": self.found,
        }


@dataclass(frozen=True)
class StaleRoadmapReference:
    file_path: str
    stale_reference: str
    occurrence_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "stale_reference": self.stale_reference,
            "occurrence_count": self.occurrence_count,
        }


@dataclass(frozen=True)
class CapabilityMapAndRoadmapLockResult:
    status: str
    roadmap_lock_status: str
    recommended_next_stage: str
    capability_count: int
    existing_capability_count: int
    missing_capability_count: int
    stale_roadmap_reference_count: int
    active_roadmap_reference_count: int
    redundant_stage_count: int
    capability_map_entries: tuple[CapabilityMapEntry, ...]
    active_roadmap_references: tuple[RoadmapReference, ...]
    stale_roadmap_references: tuple[StaleRoadmapReference, ...]
    redundant_stage_slugs: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    capability_map_ready: bool
    roadmap_lock_ready: bool
    source_selection_not_repeated: bool
    dry_run_planner_not_rebuilt: bool
    provider_registry_not_rebuilt: bool
    public_data_enablement_decision_preserved: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool
    live_fetch_deferred: bool
    network_calls_deferred: bool
    raw_response_storage_deferred: bool
    live_adapter_record_emission_deferred: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "roadmap_lock_status": self.roadmap_lock_status,
            "recommended_next_stage": self.recommended_next_stage,
            "capability_count": self.capability_count,
            "existing_capability_count": self.existing_capability_count,
            "missing_capability_count": self.missing_capability_count,
            "stale_roadmap_reference_count": self.stale_roadmap_reference_count,
            "active_roadmap_reference_count": self.active_roadmap_reference_count,
            "redundant_stage_count": self.redundant_stage_count,
            "capability_map_entries": [entry.to_dict() for entry in self.capability_map_entries],
            "active_roadmap_references": [ref.to_dict() for ref in self.active_roadmap_references],
            "stale_roadmap_references": [ref.to_dict() for ref in self.stale_roadmap_references],
            "redundant_stage_slugs": list(self.redundant_stage_slugs),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "capability_map_ready": self.capability_map_ready,
            "roadmap_lock_ready": self.roadmap_lock_ready,
            "source_selection_not_repeated": self.source_selection_not_repeated,
            "dry_run_planner_not_rebuilt": self.dry_run_planner_not_rebuilt,
            "provider_registry_not_rebuilt": self.provider_registry_not_rebuilt,
            "public_data_enablement_decision_preserved": self.public_data_enablement_decision_preserved,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "live_fetch_deferred": self.live_fetch_deferred,
            "network_calls_deferred": self.network_calls_deferred,
            "raw_response_storage_deferred": self.raw_response_storage_deferred,
            "live_adapter_record_emission_deferred": self.live_adapter_record_emission_deferred,
        }


def _repo_root(repo_root: Path | None = None) -> Path:
    if repo_root is not None:
        return repo_root
    return Path(__file__).resolve().parents[1]


def _exists(root: Path, relative_path: str) -> bool:
    return (root / relative_path).is_file()


def build_capability_map_entries(repo_root: Path | None = None) -> tuple[CapabilityMapEntry, ...]:
    root = _repo_root(repo_root)

    specs = (
        (
            "v7_4_live_public_dry_run_planner",
            "public-market-intelligence",
            "v7.4",
            "jarvis/jarvis_v7_4_live_public_market_intelligence_dry_run_planner.py",
            "Existing live-public-market-intelligence dry-run planner.",
            (REDUNDANT_DRY_RUN_ENABLEMENT_STAGE,),
        ),
        (
            "v7_7_enablement_preflight",
            "public-market-intelligence",
            "v7.7",
            "jarvis/jarvis_v7_7_live_public_market_intelligence_enablement_preflight.py",
            "Existing live-fetch enablement preflight.",
            (REDUNDANT_DRY_RUN_ENABLEMENT_STAGE,),
        ),
        (
            "v7_8_provider_configuration_registry",
            "providers",
            "v7.8",
            "jarvis/jarvis_v7_8_public_provider_configuration_registry.py",
            "Existing public provider configuration registry.",
            (REDUNDANT_SOURCE_SELECTION_STAGE, "new_provider_registry_stage"),
        ),
        (
            "v7_9_provider_skeleton_binding_audit",
            "providers",
            "v7.9",
            "jarvis/jarvis_v7_9_public_provider_skeleton_binding_audit.py",
            "Existing provider-to-skeleton binding audit.",
            ("new_provider_binding_stage",),
        ),
        (
            "v7_10_readiness_closeout",
            "readiness",
            "v7.10",
            "jarvis/jarvis_v7_10_live_public_market_intelligence_readiness_closeout_audit.py",
            "Existing public-market-intelligence readiness closeout.",
            ("new_readiness_closeout_stage",),
        ),
        (
            "dynamic_market_source_binding",
            "dynamic-market-data",
            "dynamic_market_source_binding",
            "jarvis/dynamic_market_source_binding.py",
            "Existing dynamic market source binding layer.",
            (REDUNDANT_SOURCE_SELECTION_STAGE,),
        ),
        (
            "dynamic_market_import_plan",
            "dynamic-market-data",
            "dynamic_market_import_plan",
            "jarvis/dynamic_market_import_plan.py",
            "Existing dynamic market import plan.",
            (REDUNDANT_DRY_RUN_ENABLEMENT_STAGE,),
        ),
        (
            "dynamic_market_data_source_quality_gate",
            "dynamic-market-data",
            "dynamic_market_data_source_quality_gate",
            "jarvis/dynamic_market_data_source_quality_gate.py",
            "Existing dynamic market data source quality gate.",
            ("new_source_quality_gate_stage",),
        ),
        (
            "dynamic_operator_status_dashboard",
            "dynamic-market-data",
            "dynamic_operator_status_dashboard",
            "jarvis/dynamic_operator_status_dashboard.py",
            "Existing dynamic operator status dashboard.",
            ("new_dynamic_dashboard_stage",),
        ),
        (
            "v8_4_operator_command_center_closeout",
            "operator-command-center",
            "v8.4",
            "jarvis/jarvis_v8_4_operator_command_center_closeout.py",
            "Existing operator command-center product-layer closeout.",
            ("new_v8_closeout_stage",),
        ),
        (
            "v9_0_enablement_decision_layer",
            "enablement-decision",
            "v9.0",
            "jarvis/jarvis_v9_0_public_market_data_enablement_decision_layer.py",
            "Existing public market data enablement decision layer.",
            (REDUNDANT_SOURCE_SELECTION_STAGE, REDUNDANT_DRY_RUN_ENABLEMENT_STAGE),
        ),
    )

    return tuple(
        CapabilityMapEntry(
            capability_id=capability_id,
            group=group,
            stage_or_module=stage_or_module,
            file_path=file_path,
            purpose=purpose,
            exists=_exists(root, file_path),
            makes_redundant=makes_redundant,
        )
        for capability_id, group, stage_or_module, file_path, purpose, makes_redundant in specs
    )


def _stale_reference_targets() -> tuple[str, ...]:
    return (
        "v9_0_public_market_data" + "_source_selection_plan",
        "v9_1_controlled_public_data" + "_dry_run_enablement_plan",
    )


def _scan_paths(root: Path) -> tuple[Path, ...]:
    paths: list[Path] = []
    for pattern in ("jarvis/*.py", "jarvis/tests/*.py", "docs/*.md"):
        paths.extend(root.glob(pattern))
    return tuple(sorted(path for path in paths if path.is_file()))


def scan_stale_roadmap_references(repo_root: Path | None = None) -> tuple[StaleRoadmapReference, ...]:
    root = _repo_root(repo_root)
    stale_targets = _stale_reference_targets()
    stale_refs: list[StaleRoadmapReference] = []

    for path in _scan_paths(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        relative_path = path.relative_to(root).as_posix()
        for stale_target in stale_targets:
            count = text.count(stale_target)
            if count:
                stale_refs.append(
                    StaleRoadmapReference(
                        file_path=relative_path,
                        stale_reference=stale_target,
                        occurrence_count=count,
                    )
                )

    return tuple(stale_refs)


def scan_active_roadmap_references(repo_root: Path | None = None) -> tuple[RoadmapReference, ...]:
    root = _repo_root(repo_root)

    specs = (
        ("jarvis/jarvis_v8_4_operator_command_center_closeout.py", _ACTIVE_V8_4_NEXT_STAGE),
        ("docs/JARVIS_V8_4_OPERATOR_COMMAND_CENTER_CLOSEOUT.md", _ACTIVE_V8_4_NEXT_STAGE),
        ("jarvis/jarvis_v9_0_public_market_data_enablement_decision_layer.py", _ACTIVE_V9_0_NEXT_STAGE),
        ("docs/JARVIS_V9_0_PUBLIC_MARKET_DATA_ENABLEMENT_DECISION_LAYER.md", _ACTIVE_V9_0_NEXT_STAGE),
    )

    refs: list[RoadmapReference] = []
    for relative_path, expected in specs:
        path = root / relative_path
        text = path.read_text(encoding="utf-8", errors="ignore") if path.is_file() else ""
        refs.append(
            RoadmapReference(
                file_path=relative_path,
                expected_reference=expected,
                found=expected in text,
            )
        )
    return tuple(refs)


def audit_v9_1_capability_map_and_roadmap_lock(
    repo_root: Path | None = None,
) -> CapabilityMapAndRoadmapLockResult:
    entries = build_capability_map_entries(repo_root)
    stale_refs = scan_stale_roadmap_references(repo_root)
    active_refs = scan_active_roadmap_references(repo_root)

    blockers: list[str] = []
    warnings: list[str] = [
        "v9.1 is a capability map and roadmap lock only.",
        "It prevents source-selection and dry-run-planner loops.",
        "It does not enable live public data.",
        "It does not make network calls.",
        "It does not create buy requests or execution actions.",
    ]

    missing_entries = [entry for entry in entries if not entry.exists]
    for entry in missing_entries:
        blockers.append(f"Expected existing capability file is missing: {entry.file_path}.")

    for ref in stale_refs:
        blockers.append(f"Stale roadmap reference remains in {ref.file_path}: {ref.stale_reference}.")

    for ref in active_refs:
        if not ref.found:
            blockers.append(f"Expected active roadmap reference missing in {ref.file_path}: {ref.expected_reference}.")

    redundant_slugs = tuple(
        sorted({slug for entry in entries if entry.exists for slug in entry.makes_redundant})
    )

    existing_count = sum(1 for entry in entries if entry.exists)
    missing_count = len(entries) - existing_count
    stale_count = sum(ref.occurrence_count for ref in stale_refs)
    active_count = sum(1 for ref in active_refs if ref.found)

    flags = {
        "capability_map_ready": missing_count == 0,
        "roadmap_lock_ready": stale_count == 0 and active_count == len(active_refs),
        "source_selection_not_repeated": "v9_0_public_market_data" + "_source_selection_plan" in redundant_slugs,
        "dry_run_planner_not_rebuilt": "v9_1_controlled_public_data" + "_dry_run_enablement_plan" in redundant_slugs,
        "provider_registry_not_rebuilt": "new_provider_registry_stage" in redundant_slugs,
        "public_data_enablement_decision_preserved": any(
            entry.capability_id == "v9_0_enablement_decision_layer" and entry.exists for entry in entries
        ),
        "final_user_buy_action_required": True,
        "buy_request_deferred": True,
        "broker_connection_forbidden": True,
        "order_placement_forbidden": True,
        "no_trades_executed": True,
        "live_fetch_deferred": True,
        "network_calls_deferred": True,
        "raw_response_storage_deferred": True,
        "live_adapter_record_emission_deferred": True,
    }

    if not flags["source_selection_not_repeated"]:
        blockers.append("Capability map must mark source selection as already covered.")
    if not flags["dry_run_planner_not_rebuilt"]:
        blockers.append("Capability map must mark dry-run planner work as already covered.")
    if not flags["provider_registry_not_rebuilt"]:
        blockers.append("Capability map must mark provider registry work as already covered.")
    if not flags["public_data_enablement_decision_preserved"]:
        blockers.append("Capability map must preserve the v9.0 enablement decision layer.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    ready = not unique_blockers

    return CapabilityMapAndRoadmapLockResult(
        status=STATUS_READY if ready else STATUS_BLOCKED,
        roadmap_lock_status=ROADMAP_LOCK_READY if ready else ROADMAP_LOCK_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        capability_count=len(entries),
        existing_capability_count=existing_count,
        missing_capability_count=missing_count,
        stale_roadmap_reference_count=stale_count,
        active_roadmap_reference_count=active_count,
        redundant_stage_count=len(redundant_slugs),
        capability_map_entries=entries,
        active_roadmap_references=active_refs,
        stale_roadmap_references=stale_refs,
        redundant_stage_slugs=redundant_slugs,
        blockers=unique_blockers,
        warnings=tuple(dict.fromkeys(warnings)),
        **flags,
    )


