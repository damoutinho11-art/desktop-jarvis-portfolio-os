"""Manual verification queue for draft source evidence records."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .asset_registry import AssetRegistry, load_asset_registry
from .source_evidence_fetcher import SourceEvidenceFetchResult, run_source_evidence_fetcher


DECISIONS = {"accept", "reject", "needs_correction"}


@dataclass(frozen=True)
class EvidenceVerificationTask:
    task_id: str
    evidence_id: str
    asset_id: str
    evidence_type: str
    source_name: str
    source_quality: str
    extracted_facts: dict[str, object]
    url_reference: str | None
    file_reference: str | None
    verification_status: str
    verification_questions: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    draft_evidence_record: dict[str, object]

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "evidence_id": self.evidence_id,
            "asset_id": self.asset_id,
            "evidence_type": self.evidence_type,
            "source_name": self.source_name,
            "source_quality": self.source_quality,
            "extracted_facts": self.extracted_facts,
            "url_reference": self.url_reference,
            "file_reference": self.file_reference,
            "verification_status": self.verification_status,
            "verification_questions": list(self.verification_questions),
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }


@dataclass(frozen=True)
class EvidenceVerificationDecision:
    task_id: str
    decision: str
    decided_at: str
    decided_by: str
    notes: str


@dataclass(frozen=True)
class EvidenceVerificationDecisionResult:
    task_id: str
    decision: str
    status: str
    verified_evidence_preview: dict[str, object] | None
    correction_notes: str | None
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    registry_mutation_allowed: bool = False
    files_written: bool = False
    approvals_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


@dataclass(frozen=True)
class EvidenceVerificationQueue:
    tasks: tuple[EvidenceVerificationTask, ...]
    blocked_sources: tuple[SourceEvidenceFetchResult, ...]
    warnings: tuple[str, ...]
    approvals_created: bool = False
    registry_mutation_allowed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _questions(record: dict[str, object]) -> tuple[str, ...]:
    evidence_type = str(record.get("evidence_type", "evidence"))
    return (
        f"Does this source support the {evidence_type} evidence for {record.get('asset_id')}?",
        "Do the extracted facts match the source exactly?",
        "Is the source acceptable for manual evidence intake?",
    )


def _task_from_result(result: SourceEvidenceFetchResult) -> EvidenceVerificationTask | None:
    record = result.draft_evidence_record
    if record is None:
        return None
    evidence_id = str(record["evidence_id"])
    return EvidenceVerificationTask(
        task_id=f"verify_{evidence_id}",
        evidence_id=evidence_id,
        asset_id=str(record["asset_id"]),
        evidence_type=str(record["evidence_type"]),
        source_name=str(record["source_name"]),
        source_quality=str(record["source_quality"]),
        extracted_facts=dict(record.get("extracted_facts", {})),
        url_reference=record.get("url_reference") if isinstance(record.get("url_reference"), str) else None,
        file_reference=record.get("file_reference") if isinstance(record.get("file_reference"), str) else None,
        verification_status="pending_user_verification",
        verification_questions=_questions(record),
        warnings=result.warnings,
        blockers=result.blockers,
        draft_evidence_record=record,
    )


def build_evidence_verification_queue(
    registry_path: str | Path | AssetRegistry,
    sources_path: str | Path,
) -> EvidenceVerificationQueue:
    run = run_source_evidence_fetcher(registry_path, sources_path)
    tasks = tuple(task for task in (_task_from_result(result) for result in run.results) if task is not None)
    blocked = tuple(result for result in run.results if result.status == "BLOCKED")
    warnings = tuple(dict.fromkeys(warning for result in run.results for warning in result.warnings))
    return EvidenceVerificationQueue(
        tasks=tasks,
        blocked_sources=blocked,
        warnings=warnings,
        approvals_created=False,
        registry_mutation_allowed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def apply_verification_decision(
    task: EvidenceVerificationTask,
    decision: EvidenceVerificationDecision,
) -> EvidenceVerificationDecisionResult:
    blockers: list[str] = []
    warnings: list[str] = []
    if decision.task_id != task.task_id:
        blockers.append("decision task_id does not match verification task.")
    if decision.decision not in DECISIONS:
        blockers.append(f"decision {decision.decision} is not allowed.")
    if not decision.notes.strip():
        blockers.append("decision notes are required.")
    if blockers:
        return EvidenceVerificationDecisionResult(
            task_id=decision.task_id,
            decision=decision.decision,
            status="BLOCKED",
            verified_evidence_preview=None,
            correction_notes=None,
            warnings=tuple(warnings),
            blockers=tuple(blockers),
        )
    if decision.decision == "accept":
        preview = dict(task.draft_evidence_record)
        preview["verified_by_user"] = True
        preview["verification_notes"] = decision.notes
        return EvidenceVerificationDecisionResult(
            task_id=task.task_id,
            decision=decision.decision,
            status="ACCEPTED_PREVIEW_CREATED",
            verified_evidence_preview=preview,
            correction_notes=None,
            warnings=tuple(warnings),
            blockers=(),
        )
    if decision.decision == "needs_correction":
        return EvidenceVerificationDecisionResult(
            task_id=task.task_id,
            decision=decision.decision,
            status="NEEDS_CORRECTION",
            verified_evidence_preview=None,
            correction_notes=decision.notes,
            warnings=tuple(warnings),
            blockers=(),
        )
    return EvidenceVerificationDecisionResult(
        task_id=task.task_id,
        decision=decision.decision,
        status="REJECTED",
        verified_evidence_preview=None,
        correction_notes=None,
        warnings=tuple(warnings),
        blockers=(),
    )


def write_verified_evidence_preview(result: EvidenceVerificationDecisionResult, path: str | Path) -> Path:
    if result.verified_evidence_preview is None:
        raise ValueError("only accepted decisions with a verified evidence preview can be written.")
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"records": [result.verified_evidence_preview]}, indent=2, sort_keys=True), encoding="utf-8")
    return target
