"""Read-only universe review workflow for candidate status readiness."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .approved_universe import build_approved_universe
from .candidate_review_engine import build_candidate_review_packs
from .portfolio_policy import load_portfolio_policy, validate_policy_against_approved_universe


@dataclass(frozen=True)
class UniverseCandidateReview:
    asset_id: str
    asset_type: str
    sleeve: str
    approval_status: str
    final_candidate_score: float | None
    review_status: str
    can_submit_for_manual_approval: bool
    suggested_next_status: str | None
    missing_evidence: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "sleeve": self.sleeve,
            "approval_status": self.approval_status,
            "final_candidate_score": self.final_candidate_score,
            "review_status": self.review_status,
            "can_submit_for_manual_approval": self.can_submit_for_manual_approval,
            "suggested_next_status": self.suggested_next_status,
            "missing_evidence": list(self.missing_evidence),
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
        }


@dataclass(frozen=True)
class UniverseReviewSummary:
    total_candidates: int
    review_ready_count: int
    blocked_count: int
    by_sleeve: dict[str, int]
    by_status: dict[str, int]
    approved_universe_count: int
    allocation_ready: bool
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class UniverseReviewResult:
    candidates: tuple[UniverseCandidateReview, ...]
    summary: UniverseReviewSummary
    manual_approval_required: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "candidates": [candidate.to_dict() for candidate in self.candidates],
            "summary": {
                "total_candidates": self.summary.total_candidates,
                "review_ready_count": self.summary.review_ready_count,
                "blocked_count": self.summary.blocked_count,
                "by_sleeve": self.summary.by_sleeve,
                "by_status": self.summary.by_status,
                "approved_universe_count": self.summary.approved_universe_count,
                "allocation_ready": self.summary.allocation_ready,
                "warnings": list(self.summary.warnings),
                "blockers": list(self.summary.blockers),
            },
            "manual_approval_required": self.manual_approval_required,
        }


def _suggested_next_status(approval_status: str, review_status: str) -> str | None:
    if review_status != "review_ready":
        return None
    if approval_status == "candidate_unreviewed":
        return "candidate_reviewed"
    if approval_status == "candidate_reviewed":
        return "approved_watchlist"
    if approval_status == "approved_watchlist":
        return "eligible_for_manual_investable_review"
    if approval_status in {"test_position", "legacy_existing"}:
        return "candidate_reviewed"
    return None


def _missing_evidence(review_status: str) -> tuple[str, ...]:
    if review_status == "blocked_missing_registry_data":
        return ("registry_data",)
    if review_status == "blocked_missing_scorecard":
        return ("scorecard",)
    if review_status == "blocked_missing_market_data":
        return ("market_data",)
    if review_status == "blocked_missing_exposure_data":
        return ("exposure_data",)
    return ()


def build_universe_review(
    registry_path: str | Path,
    market_data_path: str | Path,
    exposure_path: str | Path,
    policy_path: str | Path,
) -> UniverseReviewResult:
    packs = build_candidate_review_packs(registry_path, market_data_path, exposure_path)
    approved_universe = build_approved_universe(registry_path, etf_universe_expected=False, crypto_universe_expected=False)
    policy = load_portfolio_policy(policy_path)
    coverage = validate_policy_against_approved_universe(policy, approved_universe)

    candidates: list[UniverseCandidateReview] = []
    by_sleeve: dict[str, int] = {}
    by_status: dict[str, int] = {}
    for pack in packs:
        by_sleeve[pack.sleeve] = by_sleeve.get(pack.sleeve, 0) + 1
        by_status[pack.approval_status] = by_status.get(pack.approval_status, 0) + 1
        candidates.append(
            UniverseCandidateReview(
                asset_id=pack.asset_id,
                asset_type=pack.asset_type,
                sleeve=pack.sleeve,
                approval_status=pack.approval_status,
                final_candidate_score=pack.final_candidate_score,
                review_status=pack.review_status,
                can_submit_for_manual_approval=pack.can_submit_for_manual_approval,
                suggested_next_status=_suggested_next_status(pack.approval_status, pack.review_status),
                missing_evidence=_missing_evidence(pack.review_status),
                warnings=pack.warnings,
                blockers=pack.blockers,
                manual_approval_required=True,
            )
        )

    summary = UniverseReviewSummary(
        total_candidates=len(candidates),
        review_ready_count=sum(candidate.review_status == "review_ready" for candidate in candidates),
        blocked_count=sum(candidate.review_status.startswith("blocked_") for candidate in candidates),
        by_sleeve=dict(sorted(by_sleeve.items())),
        by_status=dict(sorted(by_status.items())),
        approved_universe_count=approved_universe.total_approved_assets,
        allocation_ready=coverage.allocation_ready,
        warnings=coverage.warnings,
        blockers=coverage.blockers,
    )
    return UniverseReviewResult(tuple(candidates), summary, manual_approval_required=True)
