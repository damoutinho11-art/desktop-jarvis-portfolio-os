"""Phase 2 candidate-intake chain integration audit.

This read-only audit evaluates whether v4.49-v4.54 form a coherent, safe
candidate-intake dry-run chain. It is an audit/stop report only: no files are
written, no registry is mutated, no packet is persisted, no evidence work is
started, no approvals or recommendations are created, and no trades or
executors are created.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXPECTED_STAGE_IDS = ("v4.49", "v4.50", "v4.51", "v4.52", "v4.53", "v4.54")
NEXT_ACTION = "manual_candidate_watchlist_data_entry_only"

FALSE_SAFETY_FIELDS = (
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

STAGE_FALSE_FIELDS = (
    "writes_files",
    "mutates_registry",
    "creates_executor",
    "approves_asset",
    "trusts_asset",
    "marks_investable",
    "starts_evidence_collection",
    "verifies_evidence",
    "promotes_verified_evidence",
    "recommends_allocation",
    "creates_buy_or_sell_signal",
    "executes_trade",
)

REQUIRED_DEPENDENCIES = {
    "v4.50": "v4.49",
    "v4.51": "v4.50",
    "v4.52": "v4.51",
    "v4.53": "v4.52",
    "v4.54": "v4.53",
}


@dataclass(frozen=True)
class Phase2CandidateIntakeStageAudit:
    stage_id: str
    stage_name: str
    purpose: str
    report_command: str
    expected_safe_status: str
    blocked_reasons: tuple[str, ...]
    writes_files: bool = False
    mutates_registry: bool = False
    creates_executor: bool = False
    approves_asset: bool = False
    trusts_asset: bool = False
    marks_investable: bool = False
    starts_evidence_collection: bool = False
    verifies_evidence: bool = False
    promotes_verified_evidence: bool = False
    recommends_allocation: bool = False
    creates_buy_or_sell_signal: bool = False
    executes_trade: bool = False


@dataclass(frozen=True)
class Phase2CandidateIntakeChainAuditPack:
    title: str
    version: str
    overall_status: str
    audit_mode: str
    report_only: bool
    phase2_candidate_intake_chain_complete: bool
    stop_gate_building: bool
    next_action: str
    stages: tuple[Phase2CandidateIntakeStageAudit, ...]
    expected_statuses: tuple[str, ...]
    safety_controls: dict[str, bool]
    prohibited_actions: tuple[str, ...]
    route_summary: tuple[str, ...]
    notes: tuple[str, ...]
    chain_coherent: bool
    redundancy_verdict: str
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
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


def _top_level_blockers(data: dict[str, Any]) -> list[str]:
    blocked: list[str] = []
    if data.get("report_only") is not True:
        blocked.append("report_only must be true.")
    if data.get("stop_gate_building") is not True:
        blocked.append("stop_gate_building must be true.")
    if _text(data.get("next_action")) != NEXT_ACTION:
        blocked.append(f"next_action must be {NEXT_ACTION}.")
    for unsafe_action in ("another_review_gate", "registry_mutation", "evidence_collection", "approval", "trade_execution"):
        if _text(data.get("next_action")) == unsafe_action:
            blocked.append(f"next_action must not be {unsafe_action}.")
    for field in FALSE_SAFETY_FIELDS:
        if _bool(data.get(field)):
            blocked.append(f"top-level {field} must be false or absent.")
    safety_controls = data.get("safety_controls", {})
    if isinstance(safety_controls, dict):
        for field in FALSE_SAFETY_FIELDS:
            if _bool(safety_controls.get(field)):
                blocked.append(f"safety_controls.{field} must be false.")
    else:
        blocked.append("safety_controls must be an object.")
    return blocked


def _stage_from_raw(raw: Any) -> Phase2CandidateIntakeStageAudit | None:
    if not isinstance(raw, dict):
        return None
    blocked: list[str] = []
    for field in ("stage_id", "stage_name", "purpose", "report_command", "expected_safe_status"):
        if not _text(raw.get(field)):
            blocked.append(f"{field} is required.")
    for field in STAGE_FALSE_FIELDS:
        if _bool(raw.get(field)):
            blocked.append(f"{field} must be false.")
    return Phase2CandidateIntakeStageAudit(
        stage_id=_text(raw.get("stage_id")),
        stage_name=_text(raw.get("stage_name")),
        purpose=_text(raw.get("purpose")),
        report_command=_text(raw.get("report_command")),
        expected_safe_status=_text(raw.get("expected_safe_status")),
        blocked_reasons=tuple(blocked),
        writes_files=_bool(raw.get("writes_files")),
        mutates_registry=_bool(raw.get("mutates_registry")),
        creates_executor=_bool(raw.get("creates_executor")),
        approves_asset=_bool(raw.get("approves_asset")),
        trusts_asset=_bool(raw.get("trusts_asset")),
        marks_investable=_bool(raw.get("marks_investable")),
        starts_evidence_collection=_bool(raw.get("starts_evidence_collection")),
        verifies_evidence=_bool(raw.get("verifies_evidence")),
        promotes_verified_evidence=_bool(raw.get("promotes_verified_evidence")),
        recommends_allocation=_bool(raw.get("recommends_allocation")),
        creates_buy_or_sell_signal=_bool(raw.get("creates_buy_or_sell_signal")),
        executes_trade=_bool(raw.get("executes_trade")),
    )


def _chain_blockers(stages: tuple[Phase2CandidateIntakeStageAudit, ...], data: dict[str, Any]) -> list[str]:
    blocked: list[str] = []
    stage_ids = tuple(stage.stage_id for stage in stages)
    if stage_ids != EXPECTED_STAGE_IDS:
        blocked.append("stage list must include exactly v4.49 through v4.54, in order.")
    for stage in stages:
        blocked.extend(f"{stage.stage_id}: {reason}" for reason in stage.blocked_reasons)
    stage_id_set = set(stage_ids)
    for stage_id, dependency in REQUIRED_DEPENDENCIES.items():
        if stage_id in stage_id_set and dependency not in stage_id_set:
            blocked.append(f"{stage_id} depends on {dependency}.")
    route = " -> ".join(_list_of_text(data.get("route_summary"))).lower()
    if "v4.27" not in route or "v4.47" not in route:
        blocked.append("route_summary must include v4.27-v4.47 Phase 1 real evidence pipeline.")
    notes = " ".join(_list_of_text(data.get("notes"))).lower()
    if "vwce" not in notes or "ftaw" not in notes or "pilot anchor" not in notes:
        blocked.append("notes must state VWCE and FTAW are pilot anchors only.")
    if not data.get("phase2_candidate_intake_chain_complete"):
        blocked.append("phase2_candidate_intake_chain_complete must be true for complete audit.")
    expected_statuses = _list_of_text(data.get("expected_statuses"))
    if len(expected_statuses) < len(EXPECTED_STAGE_IDS):
        blocked.append("expected_statuses must document every v4.49-v4.54 stage.")
    return blocked


def build_phase2_candidate_intake_chain_audit_pack(data: dict[str, Any]) -> Phase2CandidateIntakeChainAuditPack:
    raw_stages = data.get("stages", [])
    if not isinstance(raw_stages, list):
        raise ValueError("phase2 candidate intake chain audit data must contain stages list")
    stages = tuple(stage for stage in (_stage_from_raw(raw) for raw in raw_stages) if stage is not None)
    top_blocked = _top_level_blockers(data)
    chain_blocked = _chain_blockers(stages, data)
    blocked_reasons = tuple(dict.fromkeys(top_blocked + chain_blocked))
    stage_ids = tuple(stage.stage_id for stage in stages)
    chain_coherent = not blocked_reasons and stage_ids == EXPECTED_STAGE_IDS

    if not stages or not set(stage_ids).intersection(EXPECTED_STAGE_IDS):
        overall = "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_BLOCKED_SAFE"
    elif blocked_reasons:
        if stage_ids == EXPECTED_STAGE_IDS:
            overall = "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_PARTIAL_SAFE"
        else:
            overall = "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_BLOCKED_SAFE"
    else:
        overall = "PHASE2_CANDIDATE_INTAKE_CHAIN_AUDIT_COMPLETE_SAFE"

    safety_controls = {field: False for field in FALSE_SAFETY_FIELDS}
    raw_safety = data.get("safety_controls", {})
    if isinstance(raw_safety, dict):
        safety_controls.update({field: _bool(raw_safety.get(field)) for field in FALSE_SAFETY_FIELDS})

    return Phase2CandidateIntakeChainAuditPack(
        title=_text(data.get("title")) or "J.A.R.V.I.S. Phase 2 Candidate Intake Chain Audit",
        version=_text(data.get("version")) or "v4.55",
        overall_status=overall,
        audit_mode=_text(data.get("audit_mode")) or "phase2_candidate_intake_chain_integration_audit",
        report_only=_bool(data.get("report_only")),
        phase2_candidate_intake_chain_complete=_bool(data.get("phase2_candidate_intake_chain_complete")),
        stop_gate_building=_bool(data.get("stop_gate_building")),
        next_action=_text(data.get("next_action")),
        stages=stages,
        expected_statuses=_list_of_text(data.get("expected_statuses")),
        safety_controls=safety_controls,
        prohibited_actions=_list_of_text(data.get("prohibited_actions")),
        route_summary=_list_of_text(data.get("route_summary")),
        notes=_list_of_text(data.get("notes")),
        chain_coherent=chain_coherent,
        redundancy_verdict="no more candidate-intake gates recommended now" if _bool(data.get("stop_gate_building")) else "blocked: stop_gate_building must be true",
        blocked_reasons=blocked_reasons,
        warnings=(),
        **safety_controls,
    )


def load_phase2_candidate_intake_chain_audit_pack(path: str | Path) -> Phase2CandidateIntakeChainAuditPack:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return build_phase2_candidate_intake_chain_audit_pack(data)
