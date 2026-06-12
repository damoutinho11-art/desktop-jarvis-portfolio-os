"""Candidate intake packet dry-run builder.

This read-only builder consumes a valid v4.53 command contract and builds an
in-memory/report-only v4.49-compatible candidate intake packet preview. It
writes no files, persists no packet, mutates no registry, starts no evidence
work, creates no approvals, recommendations, orders, trades, executor,
broker/API access, credential handling, private ingest, fetching, downloads,
or extraction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .jarvis_candidate_intake import EVIDENCE_CHECKLIST_BY_ASSET_TYPE, PHASE1_ROUTE_ID
from .jarvis_candidate_intake_dry_run_command_contract import REQUIRED_EXACT_PHRASE


REQUIRED_SOURCE_STATUS = "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_READY_FOR_PACKET_DRY_RUN_SAFE"

TOP_LEVEL_FALSE_FIELDS = (
    "write_candidate_intake_file",
    "persist_packet_file",
    "registry_mutation",
    "registry_file_written",
    "candidate_registry_write",
    "evidence_collection_started",
    "evidence_verification_started",
)

UNSAFE_TRUE_FIELDS = (
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
    "registry_file_written",
    "candidate_registry_write",
    "write_candidate_intake_file",
    "persist_packet_file",
    "executor_created",
    "broker_api_used",
    "credentials_used",
    "automatic_source_fetching",
    "automatic_download",
    "private_file_ingested",
    "evidence_collection_started",
    "evidence_verification_started",
)

REQUIRED_CANDIDATE_FIELDS = (
    "candidate_id",
    "display_name",
    "asset_type",
    "symbol_or_identifier",
    "issuer_or_provider",
    "market_or_region",
    "currency",
    "source_context",
    "user_rationale",
    "intake_status",
    "phase1_route",
)

SAFETY_FLAGS = {
    "approved_asset": False,
    "trusted_asset": False,
    "investable": False,
    "verified_evidence": False,
    "promoted_verified_evidence": False,
    "allocation_recommendation": False,
    "portfolio_weight": False,
    "buy_signal": False,
    "sell_signal": False,
    "trade_executed": False,
    "registry_mutation": False,
    "registry_file_written": False,
    "candidate_registry_write": False,
    "executor_created": False,
}


@dataclass(frozen=True)
class CandidatePacketPreviewResult:
    candidate_id: str
    candidate_preview_created: bool
    packet_candidate: dict[str, Any] | None
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class CandidateIntakePacketDryRunBuilderPack:
    title: str
    version: str
    overall_status: str
    source_command_contract_version: str
    source_command_contract_status: str
    source_command_id: str
    source_explicit_command: str
    explicit_command_phrase_present: bool
    command_candidate_ids_in_scope: tuple[str, ...]
    source_preview_candidate_count: int
    built_preview_candidate_count: int
    candidate_results: tuple[CandidatePacketPreviewResult, ...]
    candidate_intake_packet_preview: dict[str, Any] | None
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    builder_mode: str
    dry_run_only: bool = True
    write_candidate_intake_file: bool = False
    persist_packet_file: bool = False
    registry_mutation: bool = False
    registry_file_written: bool = False
    candidate_registry_write: bool = False
    evidence_collection_started: bool = False
    evidence_verification_started: bool = False
    approved_asset: bool = False
    trusted_asset: bool = False
    investable: bool = False
    verified_evidence: bool = False
    promoted_verified_evidence: bool = False
    allocation_recommendation: bool = False
    portfolio_weight: bool = False
    buy_signal: bool = False
    sell_signal: bool = False
    trade_executed: bool = False
    executor_created: bool = False
    broker_api_used: bool = False
    credentials_used: bool = False
    private_file_ingested: bool = False
    automatic_source_fetching: bool = False
    automatic_download: bool = False
    automatic_fact_extraction: bool = False


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _list_of_text(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, list):
        return tuple(_text(item) for item in value if _text(item))
    text = _text(value)
    return (text,) if text else ()


def _categories(asset_type: str) -> tuple[str, ...]:
    return EVIDENCE_CHECKLIST_BY_ASSET_TYPE.get(asset_type, EVIDENCE_CHECKLIST_BY_ASSET_TYPE["other"])


def _top_level_blockers(data: dict[str, Any]) -> list[str]:
    blocked: list[str] = []
    if not _bool(data.get("dry_run_only")):
        blocked.append("dry_run_only must be true.")
    for field in TOP_LEVEL_FALSE_FIELDS:
        if data.get(field) is not False:
            blocked.append(f"{field} must be false.")
    if _text(data.get("source_command_contract_status")) != REQUIRED_SOURCE_STATUS:
        blocked.append(f"source_command_contract_status must be {REQUIRED_SOURCE_STATUS}.")
    if _text(data.get("source_explicit_command")) != REQUIRED_EXACT_PHRASE:
        blocked.append("source_explicit_command must contain the exact dry-run authorization phrase.")
    if not _list_of_text(data.get("command_candidate_ids_in_scope")):
        blocked.append("command_candidate_ids_in_scope must be non-empty.")
    raw_previews = data.get("source_candidate_previews")
    if not isinstance(raw_previews, list) or not raw_previews:
        blocked.append("source_candidate_previews must be a non-empty list.")
    for field in UNSAFE_TRUE_FIELDS:
        if _bool(data.get(field)):
            blocked.append(f"top-level {field} must be false or absent.")
    return blocked


def _candidate_blockers(raw: dict[str, Any], in_scope: set[str]) -> list[str]:
    blocked: list[str] = []
    for field in REQUIRED_CANDIDATE_FIELDS:
        if not _text(raw.get(field)):
            blocked.append(f"{field} is required.")
    candidate_id = _text(raw.get("candidate_id"))
    if candidate_id not in in_scope:
        blocked.append("candidate_id is outside command_candidate_ids_in_scope.")
    if raw.get("created_by_manual_entry") is not True:
        blocked.append("created_by_manual_entry must be true.")
    if raw.get("manual_entry_required") is not True:
        blocked.append("manual_entry_required must be true.")
    if raw.get("evidence_pipeline_required") is not True:
        blocked.append("evidence_pipeline_required must be true.")
    if _text(raw.get("phase1_route")) != PHASE1_ROUTE_ID:
        blocked.append(f"phase1_route must be {PHASE1_ROUTE_ID}.")
    intake_status = _text(raw.get("intake_status")).lower()
    if any(word in intake_status for word in ("approved", "trusted", "investable")):
        blocked.append("intake_status must remain pending/manual/dry-run only.")
    for field in UNSAFE_TRUE_FIELDS:
        if _bool(raw.get(field)):
            blocked.append(f"{field} must be false or absent.")
    safety_flags = raw.get("safety_flags", {})
    if isinstance(safety_flags, dict):
        for field in UNSAFE_TRUE_FIELDS:
            if _bool(safety_flags.get(field)):
                blocked.append(f"safety_flags.{field} must be false or absent.")
    return blocked


def _packet_candidate(raw: dict[str, Any]) -> dict[str, Any]:
    asset_type = _text(raw.get("asset_type")).lower() or "other"
    return {
        "candidate_id": _text(raw.get("candidate_id")),
        "display_name": _text(raw.get("display_name")),
        "asset_type": asset_type,
        "symbol_or_identifier": _text(raw.get("symbol_or_identifier")),
        "issuer_or_provider": _text(raw.get("issuer_or_provider")),
        "market_or_region": _text(raw.get("market_or_region")),
        "currency": _text(raw.get("currency")),
        "source_context": _text(raw.get("source_context")),
        "user_rationale": _text(raw.get("user_rationale")),
        "intake_status": _text(raw.get("intake_status")) or "candidate_intake_packet_preview_pending_manual_review",
        "created_by_manual_entry": True,
        "manual_entry_required": True,
        "evidence_pipeline_required": True,
        "phase1_route": PHASE1_ROUTE_ID,
        "notes": _text(raw.get("notes")),
        "required_evidence_categories": _categories(asset_type),
        "safety_flags": dict(SAFETY_FLAGS),
    }


def build_candidate_intake_packet_dry_run_builder_pack(data: dict[str, Any]) -> CandidateIntakePacketDryRunBuilderPack:
    top_blocked = _top_level_blockers(data)
    in_scope_ids = _list_of_text(data.get("command_candidate_ids_in_scope"))
    in_scope = set(in_scope_ids)
    raw_previews = data.get("source_candidate_previews") if isinstance(data.get("source_candidate_previews"), list) else []

    results: list[CandidatePacketPreviewResult] = []
    built: list[dict[str, Any]] = []
    for raw in raw_previews:
        if not isinstance(raw, dict):
            continue
        blocked = _candidate_blockers(raw, in_scope)
        candidate_id = _text(raw.get("candidate_id")) or "unknown_candidate"
        packet_candidate = None
        if not top_blocked and not blocked:
            packet_candidate = _packet_candidate(raw)
            built.append(packet_candidate)
        results.append(
            CandidatePacketPreviewResult(
                candidate_id=candidate_id,
                candidate_preview_created=packet_candidate is not None,
                packet_candidate=packet_candidate,
                blocked_reasons=tuple(dict.fromkeys(blocked)),
                warnings=(),
            )
        )

    blocked_reasons = tuple(
        dict.fromkeys(
            [f"builder: {reason}" for reason in top_blocked]
            + [f"{result.candidate_id}: {reason}" for result in results for reason in result.blocked_reasons]
        )
    )
    if top_blocked or not results or not built:
        overall = "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_BLOCKED_SAFE"
    elif len(built) == len(results) and all(result.candidate_id in in_scope for result in results):
        overall = "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_READY_SAFE"
    else:
        overall = "CANDIDATE_INTAKE_PACKET_DRY_RUN_BUILDER_PARTIAL_SAFE"

    packet = None
    if built:
        packet = {
            "version": "v4.54_preview",
            "title": _text(data.get("title")) or "J.A.R.V.I.S. Candidate Intake Packet Dry-Run Builder",
            "generated_from": "v4.53_candidate_intake_dry_run_command_contract",
            "dry_run_only": True,
            "write_candidate_intake_file": False,
            "persist_packet_file": False,
            "registry_mutation": False,
            "registry_file_written": False,
            "candidate_registry_write": False,
            "evidence_collection_started": False,
            "evidence_verification_started": False,
            "candidate_count": len(built),
            "candidates": built,
        }

    return CandidateIntakePacketDryRunBuilderPack(
        title=_text(data.get("title")) or "J.A.R.V.I.S. Candidate Intake Packet Dry-Run Builder",
        version=_text(data.get("version")) or "v4.54",
        overall_status=overall,
        source_command_contract_version=_text(data.get("source_command_contract_version")),
        source_command_contract_status=_text(data.get("source_command_contract_status")),
        source_command_id=_text(data.get("source_command_id")),
        source_explicit_command=_text(data.get("source_explicit_command")),
        explicit_command_phrase_present=_text(data.get("source_explicit_command")) == REQUIRED_EXACT_PHRASE,
        command_candidate_ids_in_scope=in_scope_ids,
        source_preview_candidate_count=len(raw_previews),
        built_preview_candidate_count=len(built),
        candidate_results=tuple(results),
        candidate_intake_packet_preview=packet,
        blocked_reasons=blocked_reasons,
        warnings=(),
        builder_mode=_text(data.get("builder_mode")) or "candidate_intake_packet_preview_dry_run_only",
        dry_run_only=True,
        write_candidate_intake_file=False,
        persist_packet_file=False,
        registry_mutation=False,
        registry_file_written=False,
        candidate_registry_write=False,
        evidence_collection_started=False,
        evidence_verification_started=False,
    )


def load_candidate_intake_packet_dry_run_builder_pack(path: str | Path) -> CandidateIntakePacketDryRunBuilderPack:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return build_candidate_intake_packet_dry_run_builder_pack(data)
