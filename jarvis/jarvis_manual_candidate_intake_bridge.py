"""Manual candidate intake bridge.

This read-only bridge converts v4.50 manual watchlist entries into a dry-run
v4.49-compatible candidate intake packet preview. It writes no files, mutates
no registry, starts no evidence work, creates no approvals, recommendations,
orders, trades, executor, broker/API access, credential handling, private
ingest, fetching, downloads, or extraction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .jarvis_manual_candidate_watchlist_entry import (
    INTENDED_ROUTE,
    PHASE1_ROUTE,
    validate_watchlist_entry,
)


TOP_LEVEL_FALSE_FIELDS = (
    "write_candidate_intake_file",
    "registry_mutation",
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
    "candidate_registry_write",
    "write_candidate_intake_file",
    "executor_created",
    "broker_api_used",
    "credentials_used",
    "automatic_source_fetching",
    "automatic_download",
    "private_file_ingested",
    "evidence_collection_started",
    "evidence_verification_started",
)


@dataclass(frozen=True)
class ManualCandidateIntakeBridgeEntry:
    watchlist_entry_id: str
    candidate_id: str
    display_name: str
    asset_type: str
    entry_status: str
    bridge_entry_status: str
    candidate_preview_created: bool
    candidate_preview: dict[str, Any] | None
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class ManualCandidateIntakeBridgePack:
    title: str
    version: str
    overall_status: str
    bridge_mode: str
    source_watchlist_entry_pack: str
    input_entry_count: int
    preview_candidate_count: int
    entries: tuple[ManualCandidateIntakeBridgeEntry, ...]
    candidate_intake_packet_preview: dict[str, Any] | None
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    dry_run_only: bool = True
    write_candidate_intake_file: bool = False
    registry_mutation: bool = False
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


def _candidate_preview_from_entry_preview(preview: dict[str, Any]) -> dict[str, Any]:
    safety_flags = {
        "approved_asset": False,
        "trusted_asset": False,
        "investable": False,
        "verified_evidence": False,
        "promoted_verified_evidence": False,
        "allocation_recommendation": False,
        "buy_signal": False,
        "sell_signal": False,
        "trade_executed": False,
        "registry_mutation": False,
        "executor_created": False,
    }
    return {
        "candidate_id": preview["candidate_id"],
        "display_name": preview["display_name"],
        "asset_type": preview["asset_type"],
        "symbol_or_identifier": preview["symbol_or_identifier"],
        "issuer_or_provider": preview["issuer_or_provider"],
        "market_or_region": preview["market_or_region"],
        "currency": preview["currency"],
        "source_context": preview["source_context"],
        "user_rationale": preview["user_rationale"],
        "intake_status": "candidate_intake_packet_preview_pending_manual_review",
        "created_by_manual_entry": True,
        "manual_entry_required": True,
        "evidence_pipeline_required": True,
        "phase1_route": PHASE1_ROUTE,
        "notes": preview.get("notes", ""),
        "safety_flags": safety_flags,
    }


def _top_level_blockers(data: dict[str, Any]) -> list[str]:
    blocked: list[str] = []
    if not _bool(data.get("dry_run_only")):
        blocked.append("dry_run_only must be true.")
    for field in TOP_LEVEL_FALSE_FIELDS:
        if data.get(field) is not False:
            blocked.append(f"{field} must be false.")
    for field in UNSAFE_TRUE_FIELDS:
        if _bool(data.get(field)):
            blocked.append(f"top-level {field} must be false or absent.")
    return blocked


def build_manual_candidate_intake_bridge_pack(data: dict[str, Any]) -> ManualCandidateIntakeBridgePack:
    top_blocked = _top_level_blockers(data)
    raw_entries = data.get("entries", [])
    if not isinstance(raw_entries, list):
        raise ValueError("manual candidate intake bridge data must contain entries list")

    entries: list[ManualCandidateIntakeBridgeEntry] = []
    previews: list[dict[str, Any]] = []
    for raw in raw_entries:
        if not isinstance(raw, dict):
            continue
        watch = validate_watchlist_entry(raw)
        blocked = list(watch.blocked_reasons)
        warnings = list(watch.warnings)
        if "v4.49" not in _text(raw.get("intended_route")) or "v4.27-v4.47" not in _text(raw.get("intended_route")):
            blocked.append("intended_route must include v4.49 candidate intake and v4.27-v4.47 pipeline.")
        for field in UNSAFE_TRUE_FIELDS:
            if _bool(raw.get(field)):
                blocked.append(f"{field} must be false or absent.")
        candidate_preview = None
        if not top_blocked and not blocked and watch.entry_status == "MANUAL_WATCHLIST_ENTRY_READY_FOR_CANDIDATE_INTAKE" and watch.candidate_intake_preview:
            candidate_preview = _candidate_preview_from_entry_preview(watch.candidate_intake_preview)
            previews.append(candidate_preview)
            status = "MANUAL_CANDIDATE_INTAKE_BRIDGE_READY_FOR_MANUAL_REVIEW"
        elif blocked:
            status = "MANUAL_CANDIDATE_INTAKE_BRIDGE_BLOCKED_SAFE"
        else:
            status = "MANUAL_CANDIDATE_INTAKE_BRIDGE_PARTIAL_SAFE"
        entries.append(
            ManualCandidateIntakeBridgeEntry(
                watchlist_entry_id=watch.watchlist_entry_id,
                candidate_id=watch.candidate_id,
                display_name=watch.display_name,
                asset_type=watch.asset_type,
                entry_status=watch.entry_status,
                bridge_entry_status=status,
                candidate_preview_created=candidate_preview is not None,
                candidate_preview=candidate_preview,
                blocked_reasons=tuple(dict.fromkeys(blocked)),
                warnings=tuple(warnings),
            )
        )

    blocked_reasons = tuple(
        dict.fromkeys(
            [f"bridge: {reason}" for reason in top_blocked]
            + [f"{entry.watchlist_entry_id}: {reason}" for entry in entries for reason in entry.blocked_reasons]
        )
    )
    warnings = tuple(f"{entry.watchlist_entry_id}: {warning}" for entry in entries for warning in entry.warnings)
    statuses = {entry.bridge_entry_status for entry in entries}
    if top_blocked or not entries or statuses == {"MANUAL_CANDIDATE_INTAKE_BRIDGE_BLOCKED_SAFE"}:
        overall = "MANUAL_CANDIDATE_INTAKE_BRIDGE_BLOCKED_SAFE"
    elif statuses == {"MANUAL_CANDIDATE_INTAKE_BRIDGE_READY_FOR_MANUAL_REVIEW"}:
        overall = "MANUAL_CANDIDATE_INTAKE_BRIDGE_READY_FOR_MANUAL_REVIEW"
    else:
        overall = "MANUAL_CANDIDATE_INTAKE_BRIDGE_PARTIAL_SAFE"

    packet = None
    if previews:
        packet = {
            "version": "v4.51_preview",
            "generated_from": "v4.50_manual_watchlist_entries",
            "dry_run_only": True,
            "write_candidate_intake_file": False,
            "registry_mutation": False,
            "candidate_registry_write": False,
            "candidate_count": len(previews),
            "candidates": previews,
        }

    return ManualCandidateIntakeBridgePack(
        title=_text(data.get("title")) or "J.A.R.V.I.S. Manual Candidate Intake Bridge",
        version=_text(data.get("version")) or "v4.51",
        overall_status=overall,
        bridge_mode=_text(data.get("bridge_mode")) or "dry_run_candidate_intake_packet_preview",
        source_watchlist_entry_pack=_text(data.get("source_watchlist_entry_pack")),
        input_entry_count=len(entries),
        preview_candidate_count=len(previews),
        entries=tuple(entries),
        candidate_intake_packet_preview=packet,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        dry_run_only=True,
        write_candidate_intake_file=False,
        registry_mutation=False,
        candidate_registry_write=False,
        evidence_collection_started=False,
        evidence_verification_started=False,
    )


def load_manual_candidate_intake_bridge_pack(path: str | Path) -> ManualCandidateIntakeBridgePack:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return build_manual_candidate_intake_bridge_pack(data)
