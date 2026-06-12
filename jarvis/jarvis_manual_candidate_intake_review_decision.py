"""Manual candidate intake review decision recorder.

This read-only layer records a human decision about a v4.51 manual
candidate-intake bridge preview. It writes no candidate intake files, mutates
no registry, starts no evidence work, creates no approvals, recommendations,
orders, trades, executor, broker/API access, credential handling, private
ingest, fetching, downloads, or extraction.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_DECISIONS = (
    "DEFER",
    "REJECT",
    "ACCEPT_FOR_CANDIDATE_INTAKE_DRY_RUN",
)

ACCEPTABLE_ACCEPT_SOURCE_STATUSES = (
    "MANUAL_CANDIDATE_INTAKE_BRIDGE_READY_FOR_MANUAL_REVIEW",
    "MANUAL_CANDIDATE_INTAKE_BRIDGE_PARTIAL_SAFE",
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

FUTURE_DRY_RUN_STEPS = (
    "future_explicit_dry_run_candidate_intake_packet_command_review",
    "future_explicit_dry_run_candidate_intake_packet_stage_only",
)


@dataclass(frozen=True)
class ManualCandidateIntakeReviewDecisionRecord:
    decision_id: str
    reviewer: str
    review_timestamp: str
    decision: str
    decision_scope: str
    reviewed_candidate_ids: tuple[str, ...]
    rationale: str
    required_followups: tuple[str, ...]
    manual_review_required: bool
    next_allowed_step: str
    safety_acknowledgement: str
    blocked_reasons: tuple[str, ...]


@dataclass(frozen=True)
class ManualCandidateIntakeReviewDecisionPack:
    title: str
    version: str
    overall_status: str
    source_bridge_version: str
    source_bridge_status: str
    source_preview_candidate_count: int | None
    decision_mode: str
    decision_record: ManualCandidateIntakeReviewDecisionRecord | None
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


def _list_of_text(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, list):
        return tuple(_text(item) for item in value if _text(item))
    text = _text(value)
    return (text,) if text else ()


def _preview_count(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    return None


def _top_level_blockers(data: dict[str, Any]) -> list[str]:
    blocked: list[str] = []
    if not _bool(data.get("dry_run_only")):
        blocked.append("dry_run_only must be true.")
    for field in TOP_LEVEL_FALSE_FIELDS:
        if data.get(field) is not False:
            blocked.append(f"{field} must be false.")
    for field in ("source_bridge_version", "source_bridge_status"):
        if not _text(data.get(field)):
            blocked.append(f"{field} is required.")
    if _preview_count(data.get("source_preview_candidate_count")) is None:
        blocked.append("source_preview_candidate_count is required.")
    for field in UNSAFE_TRUE_FIELDS:
        if _bool(data.get(field)):
            blocked.append(f"top-level {field} must be false or absent.")
    return blocked


def _decision_record_from_data(raw: Any) -> ManualCandidateIntakeReviewDecisionRecord | None:
    if not isinstance(raw, dict):
        return None
    blocked: list[str] = []
    required_text_fields = (
        "decision_id",
        "reviewer",
        "review_timestamp",
        "decision",
        "decision_scope",
        "rationale",
        "safety_acknowledgement",
    )
    for field in required_text_fields:
        if not _text(raw.get(field)):
            blocked.append(f"decision_record.{field} is required.")
    if raw.get("manual_review_required") is not True:
        blocked.append("decision_record.manual_review_required must be true.")
    for field in UNSAFE_TRUE_FIELDS:
        if _bool(raw.get(field)):
            blocked.append(f"decision_record.{field} must be false or absent.")

    decision = _text(raw.get("decision"))
    if decision and decision not in ALLOWED_DECISIONS:
        blocked.append("decision_record.decision is not allowed.")

    return ManualCandidateIntakeReviewDecisionRecord(
        decision_id=_text(raw.get("decision_id")),
        reviewer=_text(raw.get("reviewer")),
        review_timestamp=_text(raw.get("review_timestamp")),
        decision=decision,
        decision_scope=_text(raw.get("decision_scope")),
        reviewed_candidate_ids=_list_of_text(raw.get("reviewed_candidate_ids")),
        rationale=_text(raw.get("rationale")),
        required_followups=_list_of_text(raw.get("required_followups")),
        manual_review_required=_bool(raw.get("manual_review_required")),
        next_allowed_step=_text(raw.get("next_allowed_step")),
        safety_acknowledgement=_text(raw.get("safety_acknowledgement")),
        blocked_reasons=tuple(blocked),
    )


def _decision_specific_blockers(
    record: ManualCandidateIntakeReviewDecisionRecord,
    source_bridge_status: str,
    preview_count: int | None,
) -> list[str]:
    blocked: list[str] = []
    if record.decision == "ACCEPT_FOR_CANDIDATE_INTAKE_DRY_RUN":
        if source_bridge_status not in ACCEPTABLE_ACCEPT_SOURCE_STATUSES:
            blocked.append("ACCEPT requires a bridge status ready or partial with preview candidates.")
        if preview_count is None or preview_count <= 0:
            blocked.append("ACCEPT requires source_preview_candidate_count greater than 0.")
        if not record.reviewed_candidate_ids:
            blocked.append("ACCEPT requires reviewed_candidate_ids.")
        if record.next_allowed_step not in FUTURE_DRY_RUN_STEPS:
            blocked.append("ACCEPT next_allowed_step must be a future explicit dry-run candidate intake packet stage.")
    elif record.decision == "DEFER":
        if record.next_allowed_step != "manual_followup_or_more_review_only":
            blocked.append("DEFER next_allowed_step must be manual_followup_or_more_review_only.")
    elif record.decision == "REJECT":
        if record.next_allowed_step != "candidate_intake_rejected_no_action":
            blocked.append("REJECT next_allowed_step must be candidate_intake_rejected_no_action.")
    return blocked


def build_manual_candidate_intake_review_decision_pack(data: dict[str, Any]) -> ManualCandidateIntakeReviewDecisionPack:
    top_blocked = _top_level_blockers(data)
    record = _decision_record_from_data(data.get("decision_record"))
    record_blocked: list[str] = []
    if record is None:
        record_blocked.append("decision_record is required.")
    else:
        record_blocked.extend(record.blocked_reasons)
        record_blocked.extend(
            _decision_specific_blockers(
                record,
                _text(data.get("source_bridge_status")),
                _preview_count(data.get("source_preview_candidate_count")),
            )
        )

    blocked_reasons = tuple(dict.fromkeys(top_blocked + record_blocked))
    if blocked_reasons or record is None:
        overall = "MANUAL_CANDIDATE_INTAKE_REVIEW_BLOCKED_SAFE"
    elif record.decision == "DEFER":
        overall = "MANUAL_CANDIDATE_INTAKE_REVIEW_DEFERRED_SAFE"
    elif record.decision == "REJECT":
        overall = "MANUAL_CANDIDATE_INTAKE_REVIEW_REJECTED_SAFE"
    elif record.decision == "ACCEPT_FOR_CANDIDATE_INTAKE_DRY_RUN":
        overall = "MANUAL_CANDIDATE_INTAKE_REVIEW_ACCEPTED_FOR_DRY_RUN_SAFE"
    else:
        overall = "MANUAL_CANDIDATE_INTAKE_REVIEW_BLOCKED_SAFE"

    return ManualCandidateIntakeReviewDecisionPack(
        title=_text(data.get("title")) or "J.A.R.V.I.S. Manual Candidate Intake Review Decision",
        version=_text(data.get("version")) or "v4.52",
        overall_status=overall,
        source_bridge_version=_text(data.get("source_bridge_version")),
        source_bridge_status=_text(data.get("source_bridge_status")),
        source_preview_candidate_count=_preview_count(data.get("source_preview_candidate_count")),
        decision_mode=_text(data.get("decision_mode")) or "manual_candidate_intake_review_decision_record_only",
        decision_record=record,
        blocked_reasons=blocked_reasons,
        warnings=(),
        dry_run_only=True,
        write_candidate_intake_file=False,
        registry_mutation=False,
        candidate_registry_write=False,
        evidence_collection_started=False,
        evidence_verification_started=False,
    )


def load_manual_candidate_intake_review_decision_pack(path: str | Path) -> ManualCandidateIntakeReviewDecisionPack:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return build_manual_candidate_intake_review_decision_pack(data)
