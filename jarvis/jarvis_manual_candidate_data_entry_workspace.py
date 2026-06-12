"""Manual candidate data entry workspace validator.

This read-only v4.56 layer validates that manual candidate watchlist entry
templates and private-data guardrails are ready. It does not create
directories, copy templates, ingest private files, write registry or candidate
files, start evidence work, approve assets, recommend allocations, trade, or
create executors.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


NEXT_ACTION = "manual_candidate_watchlist_data_entry_only"
READY_STATUS = "MANUAL_CANDIDATE_DATA_ENTRY_WORKSPACE_READY_SAFE"
PARTIAL_STATUS = "MANUAL_CANDIDATE_DATA_ENTRY_WORKSPACE_PARTIAL_SAFE"
BLOCKED_STATUS = "MANUAL_CANDIDATE_DATA_ENTRY_WORKSPACE_BLOCKED_SAFE"

REQUIRED_TEMPLATE_FIELDS = (
    "watchlist_entry_id",
    "candidate_id",
    "display_name",
    "asset_type",
    "symbol_or_identifier",
    "issuer_or_provider",
    "market_or_region",
    "currency",
    "watchlist_reason",
    "watchlist_source_context",
    "manually_entered_by_user",
    "manual_entry_timestamp",
    "intended_route",
    "candidate_intake_required",
    "evidence_pipeline_required",
    "manual_review_required",
    "notes",
)

UNSAFE_TEMPLATE_FLAGS = (
    "approved_asset",
    "trusted_asset",
    "investable",
    "verified_evidence",
    "promoted_verified_evidence",
    "allocation_recommendation",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "registry_mutation",
    "candidate_registry_write",
    "executor_created",
    "broker_api_used",
    "credentials_used",
    "automatic_source_fetching",
    "automatic_download",
    "private_file_ingested",
)

UNSAFE_SAFETY_CONTROLS = (
    "registry_mutation",
    "registry_file_written",
    "candidate_registry_write",
    "candidate_intake_file_written",
    "persisted_packet_file",
    "executor_created",
    "approved_asset",
    "trusted_asset",
    "investable",
    "evidence_collection_started",
    "evidence_verification_started",
    "promoted_verified_evidence",
    "allocation_recommendation",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "broker_api_used",
    "credentials_used",
    "private_file_ingested",
    "automatic_source_fetching",
    "automatic_download",
)

BLOCKED_NEXT_ACTIONS = {
    "another_review_gate",
    "evidence_collection",
    "registry_mutation",
    "trade_execution",
}


@dataclass(frozen=True)
class ManualCandidateDataEntryWorkspacePack:
    title: str
    version: str
    overall_status: str
    workspace_mode: str
    template_path: str
    template_exists: bool
    recommended_local_paths: tuple[str, ...]
    gitignore_required_patterns: tuple[str, ...]
    missing_gitignore_patterns: tuple[str, ...]
    gitignore_guardrail_status: str
    committed_template_contains_private_data: bool
    local_private_data_expected: bool
    private_data_should_be_committed: bool
    stop_gate_building: bool
    next_action: str
    route_summary: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    safety_controls: dict[str, bool]
    registry_mutation: bool = False
    registry_file_written: bool = False
    candidate_registry_write: bool = False
    candidate_intake_file_written: bool = False
    persisted_packet_file: bool = False
    executor_created: bool = False
    approved_asset: bool = False
    trusted_asset: bool = False
    investable: bool = False
    evidence_collection_started: bool = False
    evidence_verification_started: bool = False
    promoted_verified_evidence: bool = False
    allocation_recommendation: bool = False
    portfolio_weight: bool = False
    buy_signal: bool = False
    sell_signal: bool = False
    trade_executed: bool = False
    broker_api_used: bool = False
    credentials_used: bool = False
    private_file_ingested: bool = False
    automatic_source_fetching: bool = False
    automatic_download: bool = False


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _list_of_text(value: Any) -> tuple[str, ...]:
    if isinstance(value, list):
        return tuple(_text(item) for item in value if _text(item))
    text = _text(value)
    return (text,) if text else ()


def _is_private_local_path(value: str) -> bool:
    normalized = value.replace("\\", "/").lower()
    return (
        normalized.startswith("jarvis/local/")
        or normalized.startswith("jarvis/private/")
        or normalized.startswith("local/")
        or normalized.startswith("private/")
        or normalized.endswith(".local.json")
        or normalized.endswith(".private.json")
        or normalized.endswith(".account.json")
    )


def _read_gitignore_patterns(root: Path) -> set[str]:
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        return set()
    return {line.strip() for line in gitignore.read_text(encoding="utf-8").splitlines() if line.strip() and not line.strip().startswith("#")}


def load_template(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def validate_template_safety(template: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    entries = template.get("entries")
    if not isinstance(entries, list) or len(entries) != 1 or not isinstance(entries[0], dict):
        return ("template must contain exactly one blank placeholder entry.",)
    entry = entries[0]
    for field in REQUIRED_TEMPLATE_FIELDS:
        if field not in entry:
            blocked.append(f"template entry missing {field}.")
    for field in ("watchlist_entry_id", "candidate_id", "display_name", "symbol_or_identifier", "issuer_or_provider", "watchlist_reason", "notes"):
        if _text(entry.get(field)):
            blocked.append(f"template placeholder field {field} must be blank.")
    for field in UNSAFE_TEMPLATE_FLAGS:
        if _bool(entry.get(field)):
            blocked.append(f"template unsafe flag {field} must be false.")
    return tuple(blocked)


def build_manual_candidate_data_entry_workspace_pack(
    data: dict[str, Any], root: str | Path = "."
) -> ManualCandidateDataEntryWorkspacePack:
    root_path = Path(root)
    blocked: list[str] = []
    warnings: list[str] = []

    template_path = _text(data.get("template_path"))
    template_exists = bool(template_path and (root_path / template_path).exists())
    if not template_path:
        blocked.append("template_path is required.")
    elif not template_exists:
        warnings.append("template_path is documented but does not exist in this workspace.")
    else:
        template_blocked = validate_template_safety(load_template(root_path / template_path))
        blocked.extend(template_blocked)

    recommended_local_paths = _list_of_text(data.get("recommended_local_paths"))
    if not recommended_local_paths:
        blocked.append("recommended_local_paths must include at least one local/private path.")
    for path in recommended_local_paths:
        if not _is_private_local_path(path):
            blocked.append(f"recommended local path must be private/local: {path}")

    gitignore_required_patterns = _list_of_text(data.get("gitignore_required_patterns"))
    gitignore_patterns = _read_gitignore_patterns(root_path)
    missing_gitignore_patterns = tuple(pattern for pattern in gitignore_required_patterns if pattern not in gitignore_patterns)
    if missing_gitignore_patterns:
        warnings.append("some recommended .gitignore guardrail patterns are missing.")
    gitignore_guardrail_status = "complete" if not missing_gitignore_patterns else "partial"

    if _bool(data.get("committed_template_contains_private_data")):
        blocked.append("committed_template_contains_private_data must be false.")
    if data.get("local_private_data_expected") is not True:
        warnings.append("local_private_data_expected should be true for the workspace template.")
    if data.get("private_data_should_be_committed") is not False:
        blocked.append("private_data_should_be_committed must be false.")
    if data.get("stop_gate_building") is not True:
        blocked.append("stop_gate_building must be true.")

    next_action = _text(data.get("next_action"))
    if next_action != NEXT_ACTION:
        blocked.append(f"next_action must be {NEXT_ACTION}.")
    if next_action in BLOCKED_NEXT_ACTIONS:
        blocked.append(f"next_action must not be {next_action}.")

    route = " -> ".join(_list_of_text(data.get("route_summary")))
    for required in ("v4.56", "v4.50", "v4.49", "v4.27-v4.47"):
        if required not in route:
            blocked.append(f"route_summary must include {required}.")

    raw_safety = data.get("safety_controls", {})
    if not isinstance(raw_safety, dict):
        blocked.append("safety_controls must be an object.")
        raw_safety = {}
    safety_controls = {field: _bool(raw_safety.get(field)) for field in UNSAFE_SAFETY_CONTROLS}
    for field, value in safety_controls.items():
        if value:
            blocked.append(f"safety_controls.{field} must be false.")

    if blocked:
        status = BLOCKED_STATUS
    elif warnings:
        status = PARTIAL_STATUS
    else:
        status = READY_STATUS

    return ManualCandidateDataEntryWorkspacePack(
        title=_text(data.get("title")) or "J.A.R.V.I.S. Manual Candidate Data Entry Workspace",
        version=_text(data.get("version")) or "v4.56",
        overall_status=status,
        workspace_mode=_text(data.get("workspace_mode")),
        template_path=template_path,
        template_exists=template_exists,
        recommended_local_paths=recommended_local_paths,
        gitignore_required_patterns=gitignore_required_patterns,
        missing_gitignore_patterns=missing_gitignore_patterns,
        gitignore_guardrail_status=gitignore_guardrail_status,
        committed_template_contains_private_data=_bool(data.get("committed_template_contains_private_data")),
        local_private_data_expected=_bool(data.get("local_private_data_expected")),
        private_data_should_be_committed=_bool(data.get("private_data_should_be_committed")),
        stop_gate_building=_bool(data.get("stop_gate_building")),
        next_action=next_action,
        route_summary=_list_of_text(data.get("route_summary")),
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        warnings=tuple(dict.fromkeys(warnings)),
        safety_controls=safety_controls,
        **safety_controls,
    )


def load_manual_candidate_data_entry_workspace_pack(
    path: str | Path, root: str | Path = "."
) -> ManualCandidateDataEntryWorkspacePack:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return build_manual_candidate_data_entry_workspace_pack(data, root=root)
