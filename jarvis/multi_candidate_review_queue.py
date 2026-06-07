"""Multi-candidate review queue for manual evidence collection.

The queue is read-only. It does not approve assets, mutate registries, create
orders, or generate allocation recommendations.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .asset_registry import CandidateAsset, load_asset_registry
from .evidence_freshness_policy import build_evidence_freshness_pack_from_files
from .verified_evidence_intake import build_verified_evidence_pack_from_files, load_verified_evidence_intake


ETF_REQUIRED_EVIDENCE = (
    "fund_metadata",
    "fee_metadata",
    "distribution_policy",
    "platform_availability",
    "tax_route",
    "exposure_data",
    "market_data",
)
CRYPTO_REQUIRED_EVIDENCE = (
    "protocol_metadata",
    "market_data",
    "platform_availability",
    "custody_route",
    "tax_route",
    "crypto_risk_notes",
)
SLEEVE_PRIORITY = {
    "global_core": 0,
    "growth_innovation": 1,
    "quality_factor": 2,
    "crypto_core": 3,
    "speculative_crypto": 5,
}
QUEUE_STATUSES = {
    "already_reviewed",
    "ready_for_review",
    "needs_verified_evidence",
    "needs_freshness_check",
    "blocked",
}


@dataclass(frozen=True)
class MultiCandidateReviewQueueConfig:
    verified_evidence_intake_path: str | None = None
    freshness_policy_path: str | None = None
    top_next_candidates_limit: int = 5


@dataclass(frozen=True)
class CandidateReviewQueueItem:
    asset_id: str
    name: str
    asset_type: str
    sleeve: str
    current_status: str
    reviewed_status_if_private_copy: str | None
    review_queue_status: str
    missing_evidence_types: tuple[str, ...]
    stale_evidence_types: tuple[str, ...]
    verified_evidence_count: int
    freshness_status: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    next_manual_action: str
    evidence_completeness_score: float


@dataclass(frozen=True)
class MultiCandidateReviewQueueSummary:
    total_candidates: int
    already_reviewed_count: int
    ready_for_review_count: int
    blocked_count: int
    needs_evidence_count: int
    needs_freshness_check_count: int
    approved_investable_count: int
    by_status: dict[str, int]
    by_sleeve: dict[str, int]


@dataclass(frozen=True)
class MultiCandidateReviewQueue:
    queue_status: str
    items: tuple[CandidateReviewQueueItem, ...]
    top_next_evidence_candidates: tuple[CandidateReviewQueueItem, ...]
    reviewed_candidates: tuple[CandidateReviewQueueItem, ...]
    summary: MultiCandidateReviewQueueSummary
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


def load_multi_candidate_review_queue_config(path: str | Path) -> MultiCandidateReviewQueueConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "multi candidate review queue config")
    verified_path = raw.get("verified_evidence_intake_path")
    freshness_path = raw.get("freshness_policy_path")
    limit = raw.get("top_next_candidates_limit", 5)
    if verified_path is not None and not isinstance(verified_path, str):
        raise ValueError("verified_evidence_intake_path must be text when provided.")
    if freshness_path is not None and not isinstance(freshness_path, str):
        raise ValueError("freshness_policy_path must be text when provided.")
    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("top_next_candidates_limit must be a positive integer.")
    return MultiCandidateReviewQueueConfig(
        verified_evidence_intake_path=verified_path,
        freshness_policy_path=freshness_path,
        top_next_candidates_limit=limit,
    )


def _required_evidence(asset: CandidateAsset) -> tuple[str, ...]:
    if asset.asset_type == "ETF":
        return ETF_REQUIRED_EVIDENCE
    if asset.asset_type == "crypto":
        return CRYPTO_REQUIRED_EVIDENCE
    return ("platform_availability", "tax_route")


def _reviewed_statuses(reviewed_registry_copy_path: str | Path | None) -> dict[str, str]:
    if reviewed_registry_copy_path is None:
        return {}
    path_text = str(reviewed_registry_copy_path)
    if not path_text or path_text.lower() in {"none", "null", "-"}:
        return {}
    if not Path(reviewed_registry_copy_path).exists():
        return {}
    return {
        asset.asset_id: asset.approval_status
        for asset in load_asset_registry(reviewed_registry_copy_path).assets
    }


def _verified_evidence_by_asset(path: str | Path | None) -> tuple[dict[str, tuple[str, ...]], dict[str, int], tuple[str, ...]]:
    if path is None:
        return {}, {}, ()
    records = load_verified_evidence_intake(path)
    by_asset: dict[str, set[str]] = {}
    counts: dict[str, int] = {}
    warnings: list[str] = []
    for record in records:
        asset_id = str(record.get("asset_id", ""))
        evidence_type = str(record.get("evidence_type", ""))
        if record.get("verified_by_user") is True:
            by_asset.setdefault(asset_id, set()).add(evidence_type)
            counts[asset_id] = counts.get(asset_id, 0) + 1
        else:
            warnings.append(f"{asset_id}: unverified evidence {evidence_type} does not count for review.")
    return {asset_id: tuple(sorted(types)) for asset_id, types in by_asset.items()}, counts, tuple(warnings)


def _freshness_by_asset(
    registry_path: str | Path,
    verified_evidence_intake_path: str | Path | None,
    freshness_policy_path: str | Path | None,
) -> tuple[dict[str, tuple[str, ...]], dict[str, str], tuple[str, ...]]:
    if verified_evidence_intake_path is None or freshness_policy_path is None:
        return {}, {}, ()
    pack = build_evidence_freshness_pack_from_files(registry_path, verified_evidence_intake_path, freshness_policy_path)
    stale_or_bad: dict[str, list[str]] = {}
    statuses: dict[str, str] = {}
    for result in pack.results:
        if result.freshness_status != "fresh":
            stale_or_bad.setdefault(result.asset_id, []).append(result.evidence_type)
        current = statuses.get(result.asset_id, "fresh")
        if result.freshness_status in {"stale", "invalid_date"}:
            current = "stale"
        elif result.freshness_status == "missing" and current == "fresh":
            current = "missing"
        statuses[result.asset_id] = current
    return (
        {asset_id: tuple(sorted(types)) for asset_id, types in stale_or_bad.items()},
        statuses,
        tuple(pack.summary.warnings),
    )


def _next_action(status: str, missing: tuple[str, ...], stale: tuple[str, ...]) -> str:
    if status == "already_reviewed":
        return "No investment action. Candidate is reviewed only; future gates remain required."
    if status == "ready_for_review":
        return "Prepare manual status review request. No approval or investment action."
    if status == "needs_freshness_check":
        return "Refresh or manually reverify stale evidence: " + ", ".join(stale)
    if status == "needs_verified_evidence":
        return "Collect verified evidence: " + ", ".join(missing)
    return "Resolve safety blockers before any review."


def _priority_key(item: CandidateReviewQueueItem) -> tuple[int, int, float, int, str]:
    status_priority = {
        "ready_for_review": 0,
        "needs_verified_evidence": 1,
        "needs_freshness_check": 2,
        "blocked": 3,
        "already_reviewed": 4,
    }.get(item.review_queue_status, 9)
    return (
        status_priority,
        SLEEVE_PRIORITY.get(item.sleeve, 4),
        -item.evidence_completeness_score,
        len(item.blockers),
        item.asset_id,
    )


def build_multi_candidate_review_queue(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    config: MultiCandidateReviewQueueConfig,
) -> MultiCandidateReviewQueue:
    registry = load_asset_registry(source_registry_path)
    reviewed_status_by_id = _reviewed_statuses(reviewed_registry_copy_path)
    verified_by_asset, verified_counts, evidence_warnings = _verified_evidence_by_asset(config.verified_evidence_intake_path)
    stale_by_asset, freshness_status_by_asset, freshness_warnings = _freshness_by_asset(
        source_registry_path,
        config.verified_evidence_intake_path,
        config.freshness_policy_path,
    )
    items: list[CandidateReviewQueueItem] = []
    queue_warnings: list[str] = [*evidence_warnings, *freshness_warnings]
    queue_blockers: list[str] = []

    for asset in registry.assets:
        reviewed_status = reviewed_status_by_id.get(asset.asset_id)
        effective_status = reviewed_status or asset.approval_status
        required = _required_evidence(asset)
        verified_types = verified_by_asset.get(asset.asset_id, ())
        missing = tuple(evidence_type for evidence_type in required if evidence_type not in verified_types)
        stale = stale_by_asset.get(asset.asset_id, ())
        blockers: list[str] = []
        warnings: list[str] = []
        if asset.approval_status == "approved_investable" or reviewed_status == "approved_investable":
            blockers.append(f"{asset.asset_id}: approved_investable is forbidden in the review queue.")
        if effective_status not in {"candidate_unreviewed", "candidate_reviewed", "candidate_data_incomplete", "approved_watchlist", "rejected", "legacy_existing", "test_position"}:
            blockers.append(f"{asset.asset_id}: unsupported status {effective_status}.")

        if effective_status == "candidate_reviewed":
            status = "already_reviewed"
        elif blockers:
            status = "blocked"
        elif stale:
            status = "needs_freshness_check"
        elif missing:
            status = "needs_verified_evidence"
        else:
            status = "ready_for_review"
        if status not in QUEUE_STATUSES:
            raise ValueError(f"unsupported review queue status {status}.")
        evidence_score = 100.0 * (len(required) - len(missing)) / len(required)
        items.append(
            CandidateReviewQueueItem(
                asset_id=asset.asset_id,
                name=asset.name,
                asset_type=asset.asset_type,
                sleeve=asset.sleeve,
                current_status=asset.approval_status,
                reviewed_status_if_private_copy=reviewed_status,
                review_queue_status=status,
                missing_evidence_types=missing,
                stale_evidence_types=stale,
                verified_evidence_count=verified_counts.get(asset.asset_id, 0),
                freshness_status=freshness_status_by_asset.get(asset.asset_id, "not_checked"),
                blockers=tuple(blockers),
                warnings=tuple(warnings),
                next_manual_action=_next_action(status, missing, stale),
                evidence_completeness_score=evidence_score,
            )
        )
        queue_blockers.extend(blockers)

    sorted_items = tuple(sorted(items, key=lambda item: (SLEEVE_PRIORITY.get(item.sleeve, 4), item.asset_id)))
    top_next = tuple(
        sorted(
            (item for item in items if item.review_queue_status != "already_reviewed"),
            key=_priority_key,
        )[: config.top_next_candidates_limit]
    )
    reviewed = tuple(sorted((item for item in items if item.review_queue_status == "already_reviewed"), key=lambda item: item.asset_id))
    by_status: dict[str, int] = {}
    by_sleeve: dict[str, int] = {}
    for item in items:
        by_status[item.review_queue_status] = by_status.get(item.review_queue_status, 0) + 1
        by_sleeve[item.sleeve] = by_sleeve.get(item.sleeve, 0) + 1
    summary = MultiCandidateReviewQueueSummary(
        total_candidates=len(items),
        already_reviewed_count=by_status.get("already_reviewed", 0),
        ready_for_review_count=by_status.get("ready_for_review", 0),
        blocked_count=by_status.get("blocked", 0),
        needs_evidence_count=by_status.get("needs_verified_evidence", 0),
        needs_freshness_check_count=by_status.get("needs_freshness_check", 0),
        approved_investable_count=sum(
            item.current_status == "approved_investable" or item.reviewed_status_if_private_copy == "approved_investable"
            for item in items
        ),
        by_status=dict(sorted(by_status.items())),
        by_sleeve=dict(sorted(by_sleeve.items())),
    )
    if summary.approved_investable_count:
        queue_blockers.append("approved_investable candidates are forbidden in this queue.")
    if summary.blocked_count or summary.approved_investable_count:
        queue_status = "BLOCKED"
    elif summary.ready_for_review_count or summary.already_reviewed_count:
        queue_status = "ACTIVE"
    else:
        queue_status = "NEEDS_EVIDENCE"
    return MultiCandidateReviewQueue(
        queue_status=queue_status,
        items=sorted_items,
        top_next_evidence_candidates=top_next,
        reviewed_candidates=reviewed,
        summary=summary,
        warnings=tuple(dict.fromkeys(queue_warnings)),
        blockers=tuple(dict.fromkeys(queue_blockers)),
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_multi_candidate_review_queue_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    config_path: str | Path,
) -> MultiCandidateReviewQueue:
    return build_multi_candidate_review_queue(
        source_registry_path,
        reviewed_registry_copy_path,
        load_multi_candidate_review_queue_config(config_path),
    )
