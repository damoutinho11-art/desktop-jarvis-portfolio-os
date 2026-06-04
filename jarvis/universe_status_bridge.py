"""Bridge universe review results into asset status request previews."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

from .asset_status_workflow import (
    CRYPTO_INVESTABLE_CONFIRMATIONS,
    ETF_INVESTABLE_CONFIRMATIONS,
    INVESTABLE_BASE_CONFIRMATIONS,
    WATCHLIST_CONFIRMATIONS,
    AssetStatusChangeRequest,
    validate_asset_status_request,
)
from .universe_review_workflow import UniverseCandidateReview, UniverseReviewResult, build_universe_review


@dataclass(frozen=True)
class UniverseStatusBridgeLine:
    asset_id: str
    valid: bool
    blockers: tuple[str, ...]
    status_request: AssetStatusChangeRequest | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "asset_id": self.asset_id,
            "valid": self.valid,
            "blockers": list(self.blockers),
            "status_request": asdict(self.status_request) if self.status_request else None,
        }


@dataclass(frozen=True)
class UniverseStatusBridgeResult:
    status: str
    status_requests: tuple[AssetStatusChangeRequest, ...]
    blocked_candidates: tuple[UniverseStatusBridgeLine, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool
    registry_mutation_forbidden: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "status_requests": [asdict(request) for request in self.status_requests],
            "blocked_candidates": [candidate.to_dict() for candidate in self.blocked_candidates],
            "warnings": list(self.warnings),
            "blockers": list(self.blockers),
            "manual_approval_required": self.manual_approval_required,
            "registry_mutation_forbidden": self.registry_mutation_forbidden,
        }


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _requested_status(candidate: UniverseCandidateReview) -> str | None:
    if candidate.approval_status == "candidate_unreviewed" and candidate.suggested_next_status == "candidate_reviewed":
        return "candidate_reviewed"
    if candidate.approval_status == "candidate_reviewed" and candidate.suggested_next_status == "approved_watchlist":
        return "approved_watchlist"
    if (
        candidate.approval_status == "approved_watchlist"
        and candidate.suggested_next_status == "eligible_for_manual_investable_review"
    ):
        return "approved_investable"
    if candidate.approval_status in {"test_position", "legacy_existing"} and candidate.suggested_next_status == "candidate_reviewed":
        return "candidate_reviewed"
    return None


def _confirmations(candidate: UniverseCandidateReview, requested_status: str) -> tuple[str, ...]:
    confirmations: list[str] = ["candidate_review_pack_present"]
    if requested_status == "approved_watchlist":
        confirmations = sorted(WATCHLIST_CONFIRMATIONS)
    if requested_status == "approved_investable":
        required = set(INVESTABLE_BASE_CONFIRMATIONS)
        if candidate.asset_type == "ETF":
            required.update(ETF_INVESTABLE_CONFIRMATIONS)
        elif candidate.asset_type == "crypto":
            required.update(CRYPTO_INVESTABLE_CONFIRMATIONS)
        confirmations = sorted(required)
    return tuple(confirmations)


def build_status_request_from_candidate(
    candidate: UniverseCandidateReview,
    created_at: str | None = None,
) -> AssetStatusChangeRequest | None:
    requested_status = _requested_status(candidate)
    if requested_status is None:
        return None
    return AssetStatusChangeRequest(
        request_id=f"universe_status_{candidate.asset_id}_{requested_status}",
        created_at=created_at or _now_iso(),
        asset_id=candidate.asset_id,
        asset_type=candidate.asset_type,
        current_status=candidate.approval_status,
        requested_status=requested_status,
        rationale=f"Universe review indicates {candidate.asset_id} is ready for manual status review.",
        evidence_summary=(
            f"review_status={candidate.review_status}; "
            f"final_candidate_score={candidate.final_candidate_score}; "
            f"manual_approval_required={candidate.manual_approval_required}"
        ),
        required_confirmations=_confirmations(candidate, requested_status),
        manual_approval_required=True,
        auto_execute=False,
    )


def bridge_universe_review(review_result: UniverseReviewResult) -> UniverseStatusBridgeResult:
    valid_requests: list[AssetStatusChangeRequest] = []
    blocked: list[UniverseStatusBridgeLine] = []
    warnings: list[str] = list(review_result.summary.warnings)

    for candidate in review_result.candidates:
        if not candidate.can_submit_for_manual_approval:
            blocked.append(
                UniverseStatusBridgeLine(
                    asset_id=candidate.asset_id,
                    valid=False,
                    blockers=("candidate cannot submit for manual approval.",),
                )
            )
            continue
        request = build_status_request_from_candidate(candidate)
        if request is None:
            blocked.append(
                UniverseStatusBridgeLine(
                    asset_id=candidate.asset_id,
                    valid=False,
                    blockers=("no safe suggested next status.",),
                )
            )
            continue
        validation = validate_asset_status_request(request)
        if validation.valid:
            valid_requests.append(request)
            warnings.extend(validation.warnings)
        else:
            blocked.append(
                UniverseStatusBridgeLine(
                    asset_id=candidate.asset_id,
                    valid=False,
                    blockers=validation.blockers,
                )
            )

    status = "PREVIEW_READY" if valid_requests else "BLOCKED"
    return UniverseStatusBridgeResult(
        status=status,
        status_requests=tuple(valid_requests),
        blocked_candidates=tuple(blocked),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(blocker for line in blocked for blocker in line.blockers),
        manual_approval_required=True,
        registry_mutation_forbidden=True,
    )


def load_review_and_bridge(
    registry_path: str | Path,
    market_data_path: str | Path,
    exposure_path: str | Path,
    policy_path: str | Path,
) -> UniverseStatusBridgeResult:
    return bridge_universe_review(build_universe_review(registry_path, market_data_path, exposure_path, policy_path))


def write_status_requests(
    bridge_result: UniverseStatusBridgeResult,
    path: str | Path,
) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"requests": [asdict(request) for request in bridge_result.status_requests]}
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target
