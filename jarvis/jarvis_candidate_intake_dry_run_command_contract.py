"""Explicit candidate intake dry-run packet command contract.

This read-only contract validates a human command before a future dry-run
candidate intake packet stage may be considered. It does not create candidate
intake packets, write files, mutate registries, collect or verify evidence,
approve assets, recommend allocations, place orders, trade, create executors,
use broker/authenticated APIs, use credentials, ingest private files, fetch,
download, or extract sources.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REQUIRED_EXACT_PHRASE = "AUTHORIZE_CANDIDATE_INTAKE_PACKET_DRY_RUN_ONLY_NO_WRITE_NO_MUTATION"
REQUIRED_SOURCE_STATUS = "MANUAL_CANDIDATE_INTAKE_REVIEW_ACCEPTED_FOR_DRY_RUN_SAFE"
REQUIRED_SOURCE_DECISION = "ACCEPT_FOR_CANDIDATE_INTAKE_DRY_RUN"
NEXT_ALLOWED_STEP = "future_candidate_intake_packet_dry_run_only"

TOP_LEVEL_FALSE_FIELDS = (
    "write_candidate_intake_file",
    "create_candidate_intake_packet",
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
    "create_candidate_intake_packet",
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
class CandidateIntakeDryRunCommandContract:
    command_id: str
    commander: str
    command_timestamp: str
    explicit_command: str
    required_exact_phrase: str
    command_scope: str
    candidate_ids_in_scope: tuple[str, ...]
    next_allowed_step: str
    manual_review_required: bool
    safety_acknowledgement: str
    contract_notes: str
    exact_phrase_present: bool
    blocked_reasons: tuple[str, ...]


@dataclass(frozen=True)
class CandidateIntakeDryRunCommandContractPack:
    title: str
    version: str
    overall_status: str
    source_review_decision_version: str
    source_review_decision_status: str
    source_decision_id: str
    source_decision: str
    reviewed_candidate_ids: tuple[str, ...]
    command_contract_mode: str
    command_contract: CandidateIntakeDryRunCommandContract | None
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    dry_run_only: bool = True
    write_candidate_intake_file: bool = False
    create_candidate_intake_packet: bool = False
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


def _top_level_blockers(data: dict[str, Any]) -> list[str]:
    blocked: list[str] = []
    if not _bool(data.get("dry_run_only")):
        blocked.append("dry_run_only must be true.")
    for field in TOP_LEVEL_FALSE_FIELDS:
        if data.get(field) is not False:
            blocked.append(f"{field} must be false.")
    for field in ("source_review_decision_version", "source_review_decision_status", "source_decision"):
        if not _text(data.get(field)):
            blocked.append(f"{field} is required.")
    if not _list_of_text(data.get("reviewed_candidate_ids")):
        blocked.append("reviewed_candidate_ids must be non-empty.")
    if _text(data.get("source_review_decision_status")) and _text(data.get("source_review_decision_status")) != REQUIRED_SOURCE_STATUS:
        blocked.append(f"source_review_decision_status must be {REQUIRED_SOURCE_STATUS}.")
    if _text(data.get("source_decision")) and _text(data.get("source_decision")) != REQUIRED_SOURCE_DECISION:
        blocked.append(f"source_decision must be {REQUIRED_SOURCE_DECISION}.")
    for field in UNSAFE_TRUE_FIELDS:
        if _bool(data.get(field)):
            blocked.append(f"top-level {field} must be false or absent.")
    return blocked


def _contract_from_data(raw: Any, reviewed_candidate_ids: tuple[str, ...]) -> CandidateIntakeDryRunCommandContract | None:
    if not isinstance(raw, dict):
        return None
    blocked: list[str] = []
    required_text_fields = (
        "command_id",
        "commander",
        "command_timestamp",
        "explicit_command",
        "required_exact_phrase",
        "command_scope",
        "next_allowed_step",
        "safety_acknowledgement",
    )
    for field in required_text_fields:
        if not _text(raw.get(field)):
            blocked.append(f"command_contract.{field} is required.")
    if raw.get("manual_review_required") is not True:
        blocked.append("command_contract.manual_review_required must be true.")
    candidate_ids = _list_of_text(raw.get("candidate_ids_in_scope"))
    if not candidate_ids:
        blocked.append("command_contract.candidate_ids_in_scope must be non-empty.")
    else:
        reviewed_set = set(reviewed_candidate_ids)
        outside = [candidate_id for candidate_id in candidate_ids if candidate_id not in reviewed_set]
        if outside:
            blocked.append("command_contract.candidate_ids_in_scope must be a subset of reviewed_candidate_ids.")
    explicit_command = _text(raw.get("explicit_command"))
    required_exact_phrase = _text(raw.get("required_exact_phrase"))
    exact_phrase_present = explicit_command == REQUIRED_EXACT_PHRASE or required_exact_phrase == REQUIRED_EXACT_PHRASE
    if not exact_phrase_present:
        blocked.append("command_contract exact dry-run authorization phrase is required.")
    if _text(raw.get("next_allowed_step")) and _text(raw.get("next_allowed_step")) != NEXT_ALLOWED_STEP:
        blocked.append(f"command_contract.next_allowed_step must be {NEXT_ALLOWED_STEP}.")
    for field in UNSAFE_TRUE_FIELDS:
        if _bool(raw.get(field)):
            blocked.append(f"command_contract.{field} must be false or absent.")

    return CandidateIntakeDryRunCommandContract(
        command_id=_text(raw.get("command_id")),
        commander=_text(raw.get("commander")),
        command_timestamp=_text(raw.get("command_timestamp")),
        explicit_command=explicit_command,
        required_exact_phrase=required_exact_phrase,
        command_scope=_text(raw.get("command_scope")),
        candidate_ids_in_scope=candidate_ids,
        next_allowed_step=_text(raw.get("next_allowed_step")),
        manual_review_required=_bool(raw.get("manual_review_required")),
        safety_acknowledgement=_text(raw.get("safety_acknowledgement")),
        contract_notes=_text(raw.get("contract_notes")),
        exact_phrase_present=exact_phrase_present,
        blocked_reasons=tuple(blocked),
    )


def build_candidate_intake_dry_run_command_contract_pack(data: dict[str, Any]) -> CandidateIntakeDryRunCommandContractPack:
    reviewed_candidate_ids = _list_of_text(data.get("reviewed_candidate_ids"))
    top_blocked = _top_level_blockers(data)
    contract = _contract_from_data(data.get("command_contract"), reviewed_candidate_ids)
    contract_blocked: list[str] = []
    if contract is None:
        contract_blocked.append("command_contract is required.")
    else:
        contract_blocked.extend(contract.blocked_reasons)

    blocked_reasons = tuple(dict.fromkeys(top_blocked + contract_blocked))
    if blocked_reasons or contract is None:
        if (
            _text(data.get("source_review_decision_status")) == REQUIRED_SOURCE_STATUS
            and _text(data.get("source_decision")) == REQUIRED_SOURCE_DECISION
            and reviewed_candidate_ids
            and contract is not None
        ):
            overall = "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_PARTIAL_SAFE"
        else:
            overall = "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_BLOCKED_SAFE"
    else:
        overall = "CANDIDATE_INTAKE_DRY_RUN_COMMAND_CONTRACT_READY_FOR_PACKET_DRY_RUN_SAFE"

    return CandidateIntakeDryRunCommandContractPack(
        title=_text(data.get("title")) or "J.A.R.V.I.S. Candidate Intake Dry-Run Command Contract",
        version=_text(data.get("version")) or "v4.53",
        overall_status=overall,
        source_review_decision_version=_text(data.get("source_review_decision_version")),
        source_review_decision_status=_text(data.get("source_review_decision_status")),
        source_decision_id=_text(data.get("source_decision_id")),
        source_decision=_text(data.get("source_decision")),
        reviewed_candidate_ids=reviewed_candidate_ids,
        command_contract_mode=_text(data.get("command_contract_mode")) or "explicit_candidate_intake_packet_dry_run_command_contract_only",
        command_contract=contract,
        blocked_reasons=blocked_reasons,
        warnings=(),
        dry_run_only=True,
        write_candidate_intake_file=False,
        create_candidate_intake_packet=False,
        registry_mutation=False,
        registry_file_written=False,
        candidate_registry_write=False,
        evidence_collection_started=False,
        evidence_verification_started=False,
    )


def load_candidate_intake_dry_run_command_contract_pack(path: str | Path) -> CandidateIntakeDryRunCommandContractPack:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return build_candidate_intake_dry_run_command_contract_pack(data)
