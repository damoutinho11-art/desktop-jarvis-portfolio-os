"""J.A.R.V.I.S. operator status dashboard evaluator.

v4.59 is dashboard/report-only. It reads one explicit JSON input and does not
run subprocesses, scan local/private folders, fetch, write, verify evidence,
approve assets, mutate registries, recommend allocation, trade, or create an
executor.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_COMPONENT_IDS = (
    "phase1_real_pipeline",
    "phase2_candidate_intake_chain",
    "manual_candidate_workspace",
    "public_data_fetcher",
    "public_data_freshness_monitor",
)

VALID_NEXT_MANUAL_ACTIONS = {
    "enter_real_manual_candidate_watchlist_data",
    "configure_local_public_source_manifest",
    "run_explicit_public_fetch_local_cache_only",
    "review_stale_or_missing_public_cache",
    "run_status_dashboard",
}

BLOCKED_NEXT_MANUAL_ACTIONS = {
    "another_gate",
    "another_review_layer",
    "registry_mutation",
    "evidence_verification",
    "approval",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_execution",
    "executor_creation",
}

FALSE_REQUIRED_SAFETY_FIELDS = (
    "network_calls",
    "fetching",
    "downloading",
    "writes",
    "source_parsing_as_evidence",
    "evidence_extraction",
    "evidence_verification",
    "verified_evidence_promotion",
    "registry_mutation",
    "registry_file_written",
    "candidate_registry_write",
    "candidate_intake_file_written",
    "persisted_packet_file",
    "executor_created",
    "approved_asset",
    "trusted_asset",
    "investable",
    "allocation_recommendation",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "broker_api_used",
    "credentials_used",
    "private_file_ingested",
    "automatic_private_data_ingest",
    "fetched_data_committed",
)

TRUE_REQUIRED_SAFETY_FIELDS = (
    "manual_trust_required",
    "manual_approval_required",
    "no_execution_invariant",
)

V5_PROGRESS_FIELDS = (
    "phase1_complete",
    "candidate_intake_chain_complete",
    "manual_workspace_ready",
    "public_fetch_control_ready",
    "freshness_monitor_ready",
    "dashboard_ready",
    "remaining_before_v5",
)


@dataclass(frozen=True)
class OperatorDashboardComponent:
    component_id: str
    component_name: str
    stage_range_or_version: str
    report_command: str
    latest_known_status: str
    status_class: str
    capability_summary: str
    current_blockers: tuple[str, ...]
    next_safe_action: str
    redundant_next_steps_to_avoid: tuple[str, ...]
    safety_notes: tuple[str, ...]
    component_status: str
    blocked_reasons: tuple[str, ...]


@dataclass(frozen=True)
class OperatorStatusDashboardResult:
    title: str
    version: str
    overall_status: str
    dashboard_mode: str
    report_only: bool
    no_network: bool
    no_writes: bool
    no_private_file_auto_ingest: bool
    current_project_phase: str
    current_head_note: str
    components: tuple[OperatorDashboardComponent, ...]
    blockers: tuple[str, ...]
    next_manual_action: str
    v5_progress: dict[str, Any]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    network_calls: bool = False
    fetching: bool = False
    downloading: bool = False
    writes: bool = False
    source_parsing_as_evidence: bool = False
    evidence_extraction: bool = False
    evidence_verification: bool = False
    verified_evidence_promotion: bool = False
    registry_mutation: bool = False
    registry_file_written: bool = False
    candidate_registry_write: bool = False
    candidate_intake_file_written: bool = False
    persisted_packet_file: bool = False
    approved_asset: bool = False
    trusted_asset: bool = False
    investable: bool = False
    allocation_recommendation: bool = False
    portfolio_weight: bool = False
    buy_signal: bool = False
    sell_signal: bool = False
    trade_executed: bool = False
    executor_created: bool = False
    broker_api_used: bool = False
    credentials_used: bool = False
    private_file_ingested: bool = False
    automatic_private_data_ingest: bool = False
    fetched_data_committed: bool = False
    manual_trust_required: bool = True
    manual_approval_required: bool = True
    no_execution_invariant: bool = True


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _list(value: Any) -> tuple[str, ...]:
    if isinstance(value, list):
        return tuple(_text(item) for item in value if _text(item))
    text = _text(value)
    return (text,) if text else ()


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def evaluate_component(component: dict[str, Any]) -> OperatorDashboardComponent:
    blocked: list[str] = []
    for field in ("component_id", "component_name", "report_command", "latest_known_status", "capability_summary", "next_safe_action"):
        if not _text(component.get(field)):
            blocked.append(f"{field} is required.")
    status = _text(component.get("latest_known_status"))
    if status and not (status.endswith("_SAFE") or status in {"FINAL_REAL_PIPELINE_DRY_RUN_READY_SAFE"}):
        blocked.append("latest_known_status must be a safe status.")
    redundant = _list(component.get("redundant_next_steps_to_avoid"))
    if not any("no_more_candidate_intake_gates" in item or "no_more" in item for item in redundant):
        blocked.append("redundant_next_steps_to_avoid must include no_more_candidate_intake_gates or equivalent.")
    component_status = "COMPONENT_READY_SAFE" if not blocked else "COMPONENT_BLOCKED_SAFE"
    return OperatorDashboardComponent(
        component_id=_text(component.get("component_id")),
        component_name=_text(component.get("component_name")),
        stage_range_or_version=_text(component.get("stage_range_or_version")),
        report_command=_text(component.get("report_command")),
        latest_known_status=status,
        status_class=_text(component.get("status_class")),
        capability_summary=_text(component.get("capability_summary")),
        current_blockers=_list(component.get("current_blockers")),
        next_safe_action=_text(component.get("next_safe_action")),
        redundant_next_steps_to_avoid=redundant,
        safety_notes=_list(component.get("safety_notes")),
        component_status=component_status,
        blocked_reasons=tuple(blocked),
    )


def validate_dashboard_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    if config.get("report_only") is not True:
        blocked.append("report_only must be true.")
    if config.get("no_network") is not True:
        blocked.append("no_network must be true.")
    if config.get("no_writes") is not True:
        blocked.append("no_writes must be true.")
    if config.get("no_private_file_auto_ingest") is not True:
        blocked.append("no_private_file_auto_ingest must be true.")
    safety = config.get("safety_controls", {})
    if not isinstance(safety, dict):
        blocked.append("safety_controls must be an object.")
        safety = {}
    for field in FALSE_REQUIRED_SAFETY_FIELDS:
        if _bool(safety.get(field)) or _bool(config.get(field)):
            blocked.append(f"{field} must be false.")
    for field in TRUE_REQUIRED_SAFETY_FIELDS:
        if safety.get(field) is not True:
            blocked.append(f"{field} must be true.")
    components = config.get("component_statuses", [])
    if not isinstance(components, list):
        blocked.append("component_statuses must be a list.")
        components = []
    component_ids = {_text(component.get("component_id")) for component in components if isinstance(component, dict)}
    for required in REQUIRED_COMPONENT_IDS:
        if required not in component_ids:
            blocked.append(f"missing required component: {required}")
    blockers = config.get("blockers", [])
    if not isinstance(blockers, list):
        blocked.append("blockers must be a list.")
    next_manual_action = _text(config.get("next_manual_action"))
    if next_manual_action not in VALID_NEXT_MANUAL_ACTIONS:
        blocked.append("next_manual_action must be an allowed manual action.")
    if next_manual_action in BLOCKED_NEXT_MANUAL_ACTIONS:
        blocked.append(f"next_manual_action must not be {next_manual_action}.")
    v5_progress = config.get("v5_progress", {})
    if not isinstance(v5_progress, dict):
        blocked.append("v5_progress must be an object.")
        v5_progress = {}
    for field in V5_PROGRESS_FIELDS:
        if field not in v5_progress:
            blocked.append(f"v5_progress.{field} is required.")
    return tuple(blocked)


def evaluate_operator_dashboard(config: dict[str, Any]) -> OperatorStatusDashboardResult:
    config_blocked = list(validate_dashboard_config(config))
    raw_components = config.get("component_statuses", [])
    components = tuple(
        sorted(
            (evaluate_component(component) for component in raw_components if isinstance(component, dict)),
            key=lambda item: item.component_id,
        )
    )
    component_blocked = [f"{component.component_id}: {reason}" for component in components for reason in component.blocked_reasons]
    blocked = tuple(dict.fromkeys(config_blocked + component_blocked))
    warnings: list[str] = []
    if not components:
        warnings.append("dashboard has no component summaries.")
    if blocked:
        overall = "OPERATOR_STATUS_DASHBOARD_BLOCKED_SAFE"
    elif len(components) < len(REQUIRED_COMPONENT_IDS):
        overall = "OPERATOR_STATUS_DASHBOARD_PARTIAL_SAFE"
    else:
        overall = "OPERATOR_STATUS_DASHBOARD_READY_SAFE"
    safety = config.get("safety_controls", {}) if isinstance(config.get("safety_controls"), dict) else {}
    return OperatorStatusDashboardResult(
        title=_text(config.get("title")) or "J.A.R.V.I.S. Operator Status Dashboard",
        version=_text(config.get("version")) or "v4.59",
        overall_status=overall,
        dashboard_mode=_text(config.get("dashboard_mode")),
        report_only=_bool(config.get("report_only")),
        no_network=_bool(config.get("no_network")),
        no_writes=_bool(config.get("no_writes")),
        no_private_file_auto_ingest=_bool(config.get("no_private_file_auto_ingest")),
        current_project_phase=_text(config.get("current_project_phase")),
        current_head_note=_text(config.get("current_head_note")),
        components=components,
        blockers=_list(config.get("blockers")),
        next_manual_action=_text(config.get("next_manual_action")),
        v5_progress=config.get("v5_progress", {}) if isinstance(config.get("v5_progress"), dict) else {},
        blocked_reasons=blocked,
        warnings=tuple(warnings),
        **{field: _bool(safety.get(field)) for field in FALSE_REQUIRED_SAFETY_FIELDS},
        **{field: _bool(safety.get(field)) for field in TRUE_REQUIRED_SAFETY_FIELDS},
    )


def render_dashboard_summary(result: OperatorStatusDashboardResult) -> str:
    return (
        f"status={result.overall_status}; components={len(result.components)}; "
        f"next_manual_action={result.next_manual_action}; blockers={len(result.blockers)}"
    )


def load_operator_dashboard_result(path: str | Path) -> OperatorStatusDashboardResult:
    return evaluate_operator_dashboard(load_json(path))
