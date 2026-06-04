"""Candidate review pack model for manual evidence review."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


REVIEW_STATUSES = {
    "blocked_missing_registry_data",
    "blocked_missing_scorecard",
    "blocked_missing_market_data",
    "blocked_missing_exposure_data",
    "blocked_by_approval_gate",
    "review_ready",
    "manual_decision_required",
}


@dataclass(frozen=True)
class CandidateReviewPack:
    asset_id: str
    asset_type: str
    sleeve: str
    approval_status: str
    approved_for_allocation: bool
    final_candidate_score: float | None
    market_metrics_summary: dict[str, Any] | None
    exposure_summary: dict[str, Any] | None
    warnings: tuple[str, ...] = field(default_factory=tuple)
    blockers: tuple[str, ...] = field(default_factory=tuple)
    review_status: str = "blocked_missing_registry_data"
    can_submit_for_manual_approval: bool = False
    manual_approval_required: bool = True

    def __post_init__(self) -> None:
        if self.review_status not in REVIEW_STATUSES:
            raise ValueError(f"review_status {self.review_status} is not supported.")
        if not self.manual_approval_required:
            raise ValueError("manual_approval_required must always be true.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "sleeve": self.sleeve,
            "approval_status": self.approval_status,
            "approved_for_allocation": self.approved_for_allocation,
            "final_candidate_score": self.final_candidate_score,
            "market_metrics_summary": self.market_metrics_summary,
            "exposure_summary": self.exposure_summary,
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "review_status": self.review_status,
            "can_submit_for_manual_approval": self.can_submit_for_manual_approval,
            "manual_approval_required": self.manual_approval_required,
        }
