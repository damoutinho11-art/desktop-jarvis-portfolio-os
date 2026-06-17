"""J.A.R.V.I.S. v10.0 autonomous public data refresh runtime.

This stage orchestrates existing public-data components. It does not introduce a
new fetcher, source-selection plan, provider registry, dry-run planner, broker
connection, order path, or execution path.

It wraps:
- v9.1 capability map and roadmap lock;
- the existing jarvis_public_data_fetcher local-cache boundary.

Default mode is safe dry-run planning. Real public fetching is available only
through the existing explicit local-cache-only authorization phrase and still
writes only raw, unverified public data under jarvis/local.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .jarvis_public_data_fetcher import (
    AUTHORIZATION_PHRASE,
    UNSAFE_SAFETY_CONTROLS,
    PublicDataFetcherEvaluation,
    evaluate_public_data_fetcher,
    fetch_public_sources,
)
from .jarvis_v9_1_capability_map_and_roadmap_lock import (
    STATUS_READY as V9_1_STATUS_READY,
    audit_v9_1_capability_map_and_roadmap_lock,
)


STATUS_READY = "JARVIS_V10_0_AUTONOMOUS_PUBLIC_DATA_REFRESH_RUNTIME_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V10_0_AUTONOMOUS_PUBLIC_DATA_REFRESH_RUNTIME_BLOCKED_SAFE"

RUNTIME_READY = "AUTONOMOUS_PUBLIC_DATA_REFRESH_RUNTIME_READY"
RUNTIME_BLOCKED = "AUTONOMOUS_PUBLIC_DATA_REFRESH_RUNTIME_BLOCKED"

NEXT_STAGE = "v10_1_unified_operator_runtime"

DEFAULT_LOCAL_MANIFEST_PATH = "jarvis/local/public_data_sources.local.json"
DEFAULT_OUTPUT_DIRECTORY = "jarvis/local/public_data/v10_raw"


@dataclass(frozen=True)
class AutonomousPublicDataRefreshRuntimeResult:
    status: str
    runtime_status: str
    recommended_next_stage: str
    roadmap_lock_status: str
    source_manifest_path: str
    source_manifest_loaded: bool
    demo_manifest_used: bool
    execute_fetch_requested: bool
    authorization_phrase_valid: bool
    fetcher_overall_status: str
    source_count: int
    valid_source_count: int
    blocked_source_count: int
    update_plan_count: int
    fetched_file_count: int
    fetched_files: tuple[str, ...]
    output_directory: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    runtime_contract_ready: bool
    autonomous_refresh_ready: bool
    raw_public_data_refreshed: bool
    ready_for_downstream_normalization: bool
    ready_for_downstream_source_quality_gate: bool
    recommendation_quality_current_data: bool
    local_cache_only: bool
    raw_data_unverified: bool
    source_selection_not_repeated: bool
    dry_run_planner_not_rebuilt: bool
    provider_registry_not_rebuilt: bool
    final_user_buy_action_required: bool
    buy_request_deferred: bool
    broker_connection_forbidden: bool
    order_placement_forbidden: bool
    no_trades_executed: bool
    live_adapter_record_emission_deferred: bool
    private_account_data_ingestion_forbidden: bool
    credentials_forbidden: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "runtime_status": self.runtime_status,
            "recommended_next_stage": self.recommended_next_stage,
            "roadmap_lock_status": self.roadmap_lock_status,
            "source_manifest_path": self.source_manifest_path,
            "source_manifest_loaded": self.source_manifest_loaded,
            "demo_manifest_used": self.demo_manifest_used,
            "execute_fetch_requested": self.execute_fetch_requested,
            "authorization_phrase_valid": self.authorization_phrase_valid,
            "fetcher_overall_status": self.fetcher_overall_status,
            "source_count": self.source_count,
            "valid_source_count": self.valid_source_count,
            "blocked_source_count": self.blocked_source_count,
            "update_plan_count": self.update_plan_count,
            "fetched_file_count": self.fetched_file_count,
            "fetched_files": list(self.fetched_files),
            "output_directory": self.output_directory,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "runtime_contract_ready": self.runtime_contract_ready,
            "autonomous_refresh_ready": self.autonomous_refresh_ready,
            "raw_public_data_refreshed": self.raw_public_data_refreshed,
            "ready_for_downstream_normalization": self.ready_for_downstream_normalization,
            "ready_for_downstream_source_quality_gate": self.ready_for_downstream_source_quality_gate,
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "local_cache_only": self.local_cache_only,
            "raw_data_unverified": self.raw_data_unverified,
            "source_selection_not_repeated": self.source_selection_not_repeated,
            "dry_run_planner_not_rebuilt": self.dry_run_planner_not_rebuilt,
            "provider_registry_not_rebuilt": self.provider_registry_not_rebuilt,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "buy_request_deferred": self.buy_request_deferred,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "order_placement_forbidden": self.order_placement_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "live_adapter_record_emission_deferred": self.live_adapter_record_emission_deferred,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
        }


def build_demo_public_data_source_manifest() -> dict[str, Any]:
    """Build a safe demo manifest for report smoke tests.

    This manifest proves the runtime contract without performing a network call.
    Operational use should supply jarvis/local/public_data_sources.local.json.
    """

    return {
        "title": "JARVIS v10.0 Demo Public Data Source Manifest",
        "version": "v10.0-demo",
        "update_frequency": "daily",
        "sources": [
            {
                "source_id": "demo_public_crypto_price_btc_eur",
                "candidate_id": "btc_candidate",
                "display_name": "Bitcoin EUR public price demo",
                "source_type": "public_market_data_json",
                "source_url": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=eur",
                "update_frequency": "daily",
                "public_source_only": True,
                "requires_authentication": False,
                "requires_credentials": False,
                "broker_or_trading_api": False,
                "contains_private_data": False,
                "expected_content_type": "application/json",
            }
        ],
    }


def load_public_data_source_manifest(path: str | Path) -> dict[str, Any]:
    raw = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(raw, dict):
        raise ValueError("public data source manifest must be a JSON object.")
    return raw


def build_v10_0_public_data_fetcher_config(
    manifest: dict[str, Any],
    *,
    execute_fetch: bool = False,
    authorization_phrase: str = "",
    fetch_date: str = "1970-01-01",
    output_directory: str = DEFAULT_OUTPUT_DIRECTORY,
) -> dict[str, Any]:
    update_frequency = str(manifest.get("update_frequency") or "daily").strip()
    sources = manifest.get("sources", [])
    if not isinstance(sources, list):
        sources = []

    return {
        "title": "JARVIS v10.0 Autonomous Public Data Refresh Runtime",
        "version": "v10.0",
        "fetcher_mode": "autonomous_refresh_runtime",
        "dry_run_only": not execute_fetch,
        "execute_fetch": execute_fetch,
        "write_local_cache": execute_fetch,
        "authorization_phrase": authorization_phrase,
        "authorization_phrase_required": AUTHORIZATION_PHRASE,
        "update_frequency": update_frequency,
        "fetch_date": fetch_date,
        "output_directory": output_directory,
        "safety_controls": {field: False for field in UNSAFE_SAFETY_CONTROLS},
        "sources": sources,
    }


def _load_manifest_for_runtime(
    manifest: dict[str, Any] | None,
    manifest_path: str | Path | None,
) -> tuple[dict[str, Any], str, bool, bool, tuple[str, ...], tuple[str, ...]]:
    blockers: list[str] = []
    warnings: list[str] = []

    if manifest is not None:
        return manifest, "<in_memory_manifest>", True, False, tuple(blockers), tuple(warnings)

    path = Path(manifest_path or DEFAULT_LOCAL_MANIFEST_PATH)
    if path.is_file():
        return load_public_data_source_manifest(path), str(path), True, False, tuple(blockers), tuple(warnings)

    if manifest_path is not None:
        blockers.append(f"public data source manifest not found: {path}")
        return {"sources": []}, str(path), False, False, tuple(blockers), tuple(warnings)

    warnings.append(
        "No local public data source manifest found; using demo manifest for runtime contract smoke only."
    )
    warnings.append(
        f"Create {DEFAULT_LOCAL_MANIFEST_PATH} to activate autonomous public data refresh with real sources."
    )
    return build_demo_public_data_source_manifest(), str(path), False, True, tuple(blockers), tuple(warnings)


def _evaluate_or_fetch(
    config: dict[str, Any],
    manifest: dict[str, Any],
    *,
    execute_fetch: bool,
    fetch_func: Callable[[str], bytes] | None,
    root: str | Path,
) -> PublicDataFetcherEvaluation:
    if execute_fetch:
        return fetch_public_sources(config, manifest, fetch_func=fetch_func, root=root)
    return evaluate_public_data_fetcher(config, manifest)


def audit_v10_0_autonomous_public_data_refresh_runtime(
    *,
    manifest: dict[str, Any] | None = None,
    manifest_path: str | Path | None = None,
    execute_fetch: bool = False,
    authorization_phrase: str = "",
    fetch_date: str = "1970-01-01",
    output_directory: str = DEFAULT_OUTPUT_DIRECTORY,
    fetch_func: Callable[[str], bytes] | None = None,
    root: str | Path = ".",
) -> AutonomousPublicDataRefreshRuntimeResult:
    roadmap = audit_v9_1_capability_map_and_roadmap_lock()

    loaded_manifest, effective_manifest_path, source_manifest_loaded, demo_manifest_used, manifest_blockers, manifest_warnings = (
        _load_manifest_for_runtime(manifest, manifest_path)
    )

    config = build_v10_0_public_data_fetcher_config(
        loaded_manifest,
        execute_fetch=execute_fetch,
        authorization_phrase=authorization_phrase,
        fetch_date=fetch_date,
        output_directory=output_directory,
    )

    fetcher = _evaluate_or_fetch(
        config,
        loaded_manifest,
        execute_fetch=execute_fetch,
        fetch_func=fetch_func,
        root=root,
    )

    blockers: list[str] = list(manifest_blockers)
    warnings: list[str] = list(manifest_warnings)

    if roadmap.status != V9_1_STATUS_READY:
        blockers.append(f"v9.1 roadmap lock is not ready: {roadmap.status}")
        blockers.extend(roadmap.blockers)

    blockers.extend(fetcher.blocked_reasons)
    warnings.extend(fetcher.warnings)

    if execute_fetch and fetch_func is None:
        warnings.append(
            "Real network fetch was requested through the existing public-data fetcher boundary."
        )

    source_validations = fetcher.source_validations
    valid_source_count = sum(1 for item in source_validations if item.valid)
    blocked_source_count = sum(1 for item in source_validations if not item.valid)

    if fetcher.source_count == 0:
        blockers.append("No public data sources are configured.")
    if blocked_source_count:
        blockers.append("At least one public data source is blocked by safety validation.")

    unique_blockers = tuple(dict.fromkeys(blockers))
    unique_warnings = tuple(dict.fromkeys(warnings))

    raw_refreshed = len(fetcher.fetched_files) > 0 and not unique_blockers
    runtime_contract_ready = not unique_blockers
    autonomous_refresh_ready = (
        runtime_contract_ready
        and source_manifest_loaded
        and not demo_manifest_used
        and valid_source_count > 0
    )

    return AutonomousPublicDataRefreshRuntimeResult(
        status=STATUS_READY if runtime_contract_ready else STATUS_BLOCKED,
        runtime_status=RUNTIME_READY if runtime_contract_ready else RUNTIME_BLOCKED,
        recommended_next_stage=NEXT_STAGE,
        roadmap_lock_status=roadmap.status,
        source_manifest_path=effective_manifest_path,
        source_manifest_loaded=source_manifest_loaded,
        demo_manifest_used=demo_manifest_used,
        execute_fetch_requested=execute_fetch,
        authorization_phrase_valid=authorization_phrase == AUTHORIZATION_PHRASE,
        fetcher_overall_status=fetcher.overall_status,
        source_count=fetcher.source_count,
        valid_source_count=valid_source_count,
        blocked_source_count=blocked_source_count,
        update_plan_count=len(fetcher.update_plan),
        fetched_file_count=len(fetcher.fetched_files),
        fetched_files=fetcher.fetched_files,
        output_directory=fetcher.output_directory,
        blockers=unique_blockers,
        warnings=unique_warnings,
        runtime_contract_ready=runtime_contract_ready,
        autonomous_refresh_ready=autonomous_refresh_ready,
        raw_public_data_refreshed=raw_refreshed,
        ready_for_downstream_normalization=runtime_contract_ready and valid_source_count > 0,
        ready_for_downstream_source_quality_gate=raw_refreshed,
        recommendation_quality_current_data=False,
        local_cache_only=True,
        raw_data_unverified=True,
        source_selection_not_repeated=roadmap.source_selection_not_repeated,
        dry_run_planner_not_rebuilt=roadmap.dry_run_planner_not_rebuilt,
        provider_registry_not_rebuilt=roadmap.provider_registry_not_rebuilt,
        final_user_buy_action_required=True,
        buy_request_deferred=True,
        broker_connection_forbidden=True,
        order_placement_forbidden=True,
        no_trades_executed=True,
        live_adapter_record_emission_deferred=True,
        private_account_data_ingestion_forbidden=True,
        credentials_forbidden=True,
    )
