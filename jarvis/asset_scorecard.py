"""Scorecard models for read-only candidate asset scoring."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class AssetScorecard:
    asset_id: str
    asset_type: str
    approval_status: str
    approved_for_allocation: bool
    manual_approval_required: bool
    final_candidate_score: float
    score_breakdown: dict[str, float]
    reasons: tuple[str, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    blockers: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "approval_status": self.approval_status,
            "approved_for_allocation": self.approved_for_allocation,
            "manual_approval_required": self.manual_approval_required,
            "final_candidate_score": self.final_candidate_score,
            "score_breakdown": self.score_breakdown,
            "reasons": list(self.reasons),
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
        }
