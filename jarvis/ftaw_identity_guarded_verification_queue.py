"""Identity-guarded manual verification queue for FTAW source facts.

Automated structure. Manual trust.

This module combines source fact intake, source identity guard, and manual
verification readiness. It never verifies evidence, approves assets, mutates
registries, recommends allocations, creates orders, or trades.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .ftaw_draft_evidence_verification_queue import VERIFICATION_QUESTIONS
from .ftaw_public_source_research_pack import PUBLIC_RESEARCH_EVIDENCE_TYPES
from .ftaw_source_fact_intake import (
    MANUAL_EVIDENCE_TYPES,
    TARGET_ASSET_ID,
    FTAWSourceFactIntakeConfig,
    build_ftaw_source_fact_intake_pack,
    load_ftaw_source_fact_intake_config,
)
from .ftaw_source_identity_guard import (
    FTAWSourceIdentityGuardConfig,
    build_ftaw_source_identity_guard,
    load_ftaw_source_identity_guard_config,
)


QUEUE_STATUSES = {
    "eligible_for_manual_verification",
    "needs_source_facts",
    "needs_identity_confirmation",
    "blocked_source_identity_mismatch",
    "manual_only_skipped",
}


@dataclass(frozen=True)
class FTAWIdentityGuardedVerificationQueueConfig:
    target_asset_id: str = TARGET_ASSET_ID


@dataclass(frozen=True)
class FTAWIdentityGuardedVerificationQueueItem:
    asset_id: str
    evidence_type: str
    source_name: str
    source_quality: str
    url_reference: str
    queue_status: str
    reason: str
    verification_questions: tuple[str, ...]
    missing_facts: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    verified_by_user: bool = False


@dataclass(frozen=True)
class FTAWIdentityGuardedVerificationQueue:
    queue_status: str
    target_asset_id: str
    total_input_items: int
    queued_count: int
    eligible_for_manual_verification_count: int
    needs_source_facts_count: int
    needs_identity_confirmation_count: int
    blocked_source_identity_mismatch_count: int
    manual_only_skipped_count: int
    items: tuple[FTAWIdentityGuardedVerificationQueueItem, ...]
    identity_guard_status: str
    identity_guard_passed: bool
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


def load_ftaw_identity_guarded_verification_queue_config(
    path: str | Path,
) -> FTAWIdentityGuardedVerificationQueueConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "FTAW identity-guarded queue config")
    return FTAWIdentityGuardedVerificationQueueConfig(
        target_asset_id=_require_text(raw.get("target_asset_id", TARGET_ASSET_ID), "target_asset_id")
    )


def _item_for_result(result, identity_status: str, identity_passed: bool) -> FTAWIdentityGuardedVerificationQueueItem:
    draft = result.draft_record or {}
    source_name = str(draft.get("source_name", ""))
    source_quality = str(draft.get("source_quality", ""))
    url_reference = str(draft.get("url_reference", ""))
    warnings = tuple(result.warnings)
    blockers = tuple(result.blockers)

    if result.evidence_type in MANUAL_EVIDENCE_TYPES:
        status = "manual_only_skipped"
        reason = f"{result.evidence_type}: manual-only evidence type skipped by automated queue."
    elif result.intake_status != "processed" or result.draft_status == "needs_correction":
        status = "needs_source_facts"
        reason = f"{result.evidence_type}: source facts are incomplete or need correction."
    elif identity_status == "BLOCKED":
        status = "blocked_source_identity_mismatch"
        reason = f"{result.evidence_type}: source identity guard blocked due to mismatch."
    elif not identity_passed:
        status = "needs_identity_confirmation"
        reason = f"{result.evidence_type}: source identity guard has not passed."
    else:
        status = "eligible_for_manual_verification"
        reason = f"{result.evidence_type}: source facts are complete and source identity guard passed."

    questions = VERIFICATION_QUESTIONS.get(result.evidence_type, ())
    return FTAWIdentityGuardedVerificationQueueItem(
        asset_id=result.asset_id,
        evidence_type=result.evidence_type,
        source_name=source_name,
        source_quality=source_quality,
        url_reference=url_reference,
        queue_status=status,
        reason=reason,
        verification_questions=questions,
        missing_facts=tuple(result.missing_facts),
        blockers=blockers,
        warnings=warnings,
        verified_by_user=False,
    )


def build_ftaw_identity_guarded_verification_queue(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config: FTAWSourceFactIntakeConfig,
    identity_guard_config: FTAWSourceIdentityGuardConfig,
    queue_config: FTAWIdentityGuardedVerificationQueueConfig,
) -> FTAWIdentityGuardedVerificationQueue:
    fact_pack = build_ftaw_source_fact_intake_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config,
    )
    identity = build_ftaw_source_identity_guard(
        source_registry_path,
        reviewed_registry_copy_path,
        fact_intake_config,
        identity_guard_config,
    )
    target_results = tuple(result for result in fact_pack.results if result.asset_id == queue_config.target_asset_id)
    items = tuple(
        _item_for_result(result, identity.identity_guard_status, identity.identity_guard_passed)
        for result in target_results
        if result.evidence_type in PUBLIC_RESEARCH_EVIDENCE_TYPES or result.evidence_type in MANUAL_EVIDENCE_TYPES
    )
    queued_count = len(items)
    eligible_count = sum(item.queue_status == "eligible_for_manual_verification" for item in items)
    needs_source = sum(item.queue_status == "needs_source_facts" for item in items)
    needs_identity = sum(item.queue_status == "needs_identity_confirmation" for item in items)
    blocked_identity = sum(item.queue_status == "blocked_source_identity_mismatch" for item in items)
    manual_skipped = sum(item.queue_status == "manual_only_skipped" for item in items)
    blockers = tuple(dict.fromkeys([*fact_pack.blockers, *identity.blockers]))
    warnings = tuple(dict.fromkeys([*fact_pack.warnings, *identity.warnings]))
    if blocked_identity or blockers:
        status = "BLOCKED"
    elif eligible_count:
        status = "READY_FOR_MANUAL_VERIFICATION"
    elif needs_source or needs_identity or manual_skipped:
        status = "NOT_READY"
    else:
        status = "NO_ITEMS"
    return FTAWIdentityGuardedVerificationQueue(
        queue_status=status,
        target_asset_id=queue_config.target_asset_id,
        total_input_items=len(target_results),
        queued_count=queued_count,
        eligible_for_manual_verification_count=eligible_count,
        needs_source_facts_count=needs_source,
        needs_identity_confirmation_count=needs_identity,
        blocked_source_identity_mismatch_count=blocked_identity,
        manual_only_skipped_count=manual_skipped,
        items=items,
        identity_guard_status=identity.identity_guard_status,
        identity_guard_passed=identity.identity_guard_passed,
        warnings=warnings,
        blockers=blockers,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_identity_guarded_verification_queue_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
) -> FTAWIdentityGuardedVerificationQueue:
    return build_ftaw_identity_guarded_verification_queue(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        load_ftaw_source_fact_intake_config(fact_intake_config_path),
        load_ftaw_source_identity_guard_config(identity_guard_config_path),
        load_ftaw_identity_guarded_verification_queue_config(queue_config_path),
    )
