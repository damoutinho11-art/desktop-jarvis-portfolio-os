"""Manual verification queue for FTAW public draft evidence records.

This queue previews accept/reject/needs_correction decisions. It never marks
evidence verified or writes files by default.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ftaw_public_source_research_pack import build_ftaw_public_source_research_pack_from_files


DEFAULT_TARGET_ASSET_ID = "ftaw_global_core_candidate"
ALLOWED_DECISIONS = {"accept", "reject", "needs_correction"}
REQUIRED_FACT_FIELDS = {
    "fund_metadata": ("name", "ticker", "isin_or_symbol", "provider", "index_tracked", "replication_method"),
    "fee_metadata": ("ter_or_fee", "fee_source", "as_of_date"),
    "distribution_policy": ("distribution_policy", "accumulating_or_distributing", "as_of_date"),
    "exposure_data": ("top_holdings_source", "country_exposure_source", "sector_exposure_source", "as_of_date"),
    "market_data": ("price", "currency", "source", "market_date"),
}
VERIFICATION_QUESTIONS = {
    "fund_metadata": (
        "Does the source identify the exact FTAW instrument?",
        "Are name, ticker, ISIN, provider, index, and replication method captured?",
    ),
    "fee_metadata": (
        "Is the fee/TER captured from a provider factsheet or KIID?",
        "Is the source date or document date captured?",
    ),
    "distribution_policy": (
        "Does the source show the exact distribution policy?",
        "Does the policy apply to the exact FTAW instrument?",
    ),
    "exposure_data": (
        "Are holdings, country, and sector exposure source references captured?",
        "Is the exposure as-of date captured when available?",
    ),
    "market_data": (
        "Are price, currency, source, and market/as-of date captured?",
        "Does the market data match the exact FTAW ticker or ISIN?",
    ),
}


@dataclass(frozen=True)
class FTAWDraftEvidenceVerificationConfig:
    target_asset_id: str = DEFAULT_TARGET_ASSET_ID
    preview_decisions: dict[str, str] | None = None
    preview_decision_notes: dict[str, str] | None = None


@dataclass(frozen=True)
class FTAWDraftEvidenceVerificationTask:
    task_id: str
    asset_id: str
    evidence_type: str
    source_name: str
    source_quality: str
    url_reference: str
    extracted_facts: dict[str, object]
    verification_questions: tuple[str, ...]
    recommended_decision: str
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    verification_status: str = "pending_user_verification"


@dataclass(frozen=True)
class FTAWDraftEvidenceVerificationQueue:
    queue_status: str
    target_asset_id: str
    draft_records_count: int
    verification_tasks: tuple[FTAWDraftEvidenceVerificationTask, ...]
    recommended_decisions_by_evidence_type: dict[str, str]
    accepted_preview_records: tuple[dict[str, object], ...]
    accepted_preview_count: int
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")
    return value.strip()


def load_ftaw_draft_evidence_verification_config(path: str | Path) -> FTAWDraftEvidenceVerificationConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "FTAW draft evidence verification config")
    decisions_raw = raw.get("preview_decisions", {})
    notes_raw = raw.get("preview_decision_notes", {})
    decisions: dict[str, str] = {}
    if decisions_raw is not None:
        for evidence_type, decision in _require_mapping(decisions_raw, "preview_decisions").items():
            parsed = _require_text(decision, f"preview_decisions.{evidence_type}")
            if parsed not in ALLOWED_DECISIONS:
                raise ValueError(f"preview decision {parsed} is not allowed.")
            decisions[str(evidence_type)] = parsed
    notes: dict[str, str] = {}
    if notes_raw is not None:
        for evidence_type, note in _require_mapping(notes_raw, "preview_decision_notes").items():
            notes[str(evidence_type)] = _require_text(note, f"preview_decision_notes.{evidence_type}")
    return FTAWDraftEvidenceVerificationConfig(
        target_asset_id=_require_text(raw.get("target_asset_id", DEFAULT_TARGET_ASSET_ID), "target_asset_id"),
        preview_decisions=decisions,
        preview_decision_notes=notes,
    )


def _is_placeholder(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        stripped = value.strip()
        return not stripped or stripped.startswith("<") or stripped.endswith("_to_capture>")
    if isinstance(value, dict):
        return any(_is_placeholder(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return any(_is_placeholder(item) for item in value)
    return False


def _record_blockers(record: dict[str, object]) -> tuple[str, ...]:
    evidence_type = str(record.get("evidence_type", ""))
    facts = record.get("extracted_facts")
    blockers: list[str] = []
    if _is_placeholder(record.get("url_reference")):
        blockers.append(f"{evidence_type}: url_reference is a placeholder.")
    if _is_placeholder(record.get("source_quality")):
        blockers.append(f"{evidence_type}: source_quality is a placeholder.")
    if not isinstance(facts, dict):
        blockers.append(f"{evidence_type}: extracted_facts must be an object.")
        return tuple(blockers)
    required = REQUIRED_FACT_FIELDS.get(evidence_type, ())
    for field in required:
        if field not in facts or _is_placeholder(facts.get(field)):
            blockers.append(f"{evidence_type}: extracted fact {field} is missing or placeholder.")
    return tuple(blockers)


def _recommended_decision(blockers: tuple[str, ...]) -> str:
    return "needs_correction" if blockers else "accept"


def _task_from_record(record: dict[str, object]) -> FTAWDraftEvidenceVerificationTask:
    evidence_type = str(record["evidence_type"])
    blockers = _record_blockers(record)
    warnings = tuple(str(warning) for warning in record.get("warnings", []) if warning)
    return FTAWDraftEvidenceVerificationTask(
        task_id=f"verify_draft_ftaw_{evidence_type}",
        asset_id=str(record["asset_id"]),
        evidence_type=evidence_type,
        source_name=str(record.get("source_name", "")),
        source_quality=str(record.get("source_quality", "")),
        url_reference=str(record.get("url_reference", "")),
        extracted_facts=dict(record.get("extracted_facts", {})),
        verification_questions=VERIFICATION_QUESTIONS[evidence_type],
        recommended_decision=_recommended_decision(blockers),
        warnings=warnings,
        blockers=blockers,
        verification_status="pending_user_verification",
    )


def preview_verified_evidence_record(
    task: FTAWDraftEvidenceVerificationTask,
    decision: str,
    verification_notes: str | None = None,
) -> dict[str, object] | None:
    if decision not in ALLOWED_DECISIONS:
        raise ValueError(f"decision {decision} is not allowed.")
    if decision != "accept":
        return None
    if task.blockers:
        raise ValueError(f"{task.evidence_type}: cannot accept draft with blockers.")
    if not verification_notes or not verification_notes.strip():
        raise ValueError(f"{task.evidence_type}: explicit accept requires verification_notes.")
    return {
        "evidence_id": f"accepted_preview_{task.evidence_type}",
        "asset_id": task.asset_id,
        "evidence_type": task.evidence_type,
        "source_quality": task.source_quality,
        "source_name": task.source_name,
        "as_of": "<YYYY-MM-DD>",
        "verified_by_user": True,
        "verification_notes": verification_notes.strip(),
        "file_reference": None,
        "url_reference": task.url_reference,
        "extracted_facts": dict(task.extracted_facts),
        "warnings": ["Accepted preview only. No approvals, registry mutation, allocation, orders, or trades."],
    }


def build_ftaw_draft_evidence_verification_queue(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    planner_config_path: str | Path,
    source_collection_pack_config_path: str | Path,
    public_research_config_path: str | Path,
    config: FTAWDraftEvidenceVerificationConfig,
) -> FTAWDraftEvidenceVerificationQueue:
    research_pack = build_ftaw_public_source_research_pack_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
        planner_config_path,
        source_collection_pack_config_path,
        public_research_config_path,
    )
    tasks = tuple(_task_from_record(record) for record in research_pack.draft_evidence_records)
    warnings = [*research_pack.warnings]
    blockers = [*research_pack.blockers]
    decisions = config.preview_decisions or {}
    decision_notes = config.preview_decision_notes or {}
    accepted_previews: list[dict[str, object]] = []
    for task in tasks:
        decision = decisions.get(task.evidence_type, task.recommended_decision)
        if decision == "accept":
            try:
                preview = preview_verified_evidence_record(task, decision, decision_notes.get(task.evidence_type))
            except ValueError as exc:
                blockers.append(str(exc))
                continue
            if preview is not None:
                accepted_previews.append(preview)
    by_type = {task.evidence_type: task.recommended_decision for task in tasks}
    unique_blockers = tuple(dict.fromkeys(blockers))
    return FTAWDraftEvidenceVerificationQueue(
        queue_status="READY" if tasks and not unique_blockers else "BLOCKED" if unique_blockers else "NO_TASKS",
        target_asset_id=config.target_asset_id,
        draft_records_count=research_pack.public_research_tasks_count,
        verification_tasks=tasks,
        recommended_decisions_by_evidence_type=dict(sorted(by_type.items())),
        accepted_preview_records=tuple(accepted_previews),
        accepted_preview_count=len(accepted_previews),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=unique_blockers,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_draft_evidence_verification_queue_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
    planner_config_path: str | Path,
    source_collection_pack_config_path: str | Path,
    public_research_config_path: str | Path,
    verification_config_path: str | Path,
) -> FTAWDraftEvidenceVerificationQueue:
    return build_ftaw_draft_evidence_verification_queue(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        expander_config_path,
        planner_config_path,
        source_collection_pack_config_path,
        public_research_config_path,
        load_ftaw_draft_evidence_verification_config(verification_config_path),
    )
