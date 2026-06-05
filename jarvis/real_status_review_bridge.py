"""Bridge real status-review readiness into manual status request previews."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .asset_registry import AssetRegistry, CandidateAsset, load_asset_registry
from .asset_status_workflow import WATCHLIST_CONFIRMATIONS, AssetStatusChangeRequest, validate_asset_status_request
from .status_request_audit_pack import audit_status_request
from .verified_evidence_promotion import (
    EvidencePromotionPack,
    build_verified_evidence_promotion_pack_from_files,
)


BASE_CONFIRMATIONS = (
    "verified_evidence_reviewed",
    "provenance_gate_passed",
    "no_registry_mutation_without_manual_action",
    "manual_status_change_required",
)


@dataclass(frozen=True)
class RealStatusReviewBridgeLine:
    asset_id: str
    ready_for_real_status_review: bool
    valid: bool
    status_request: AssetStatusChangeRequest | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class RealStatusReviewBridgeResult:
    bridge_status: str
    ready_assets_count: int
    status_requests: tuple[AssetStatusChangeRequest, ...]
    blocked_assets: tuple[RealStatusReviewBridgeLine, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool = True
    approvals_created: bool = False
    registry_mutation_allowed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _next_status(asset: CandidateAsset, eligible_for_investable_review: bool = False) -> str | None:
    if asset.approval_status == "candidate_unreviewed":
        return "candidate_reviewed"
    if asset.approval_status == "candidate_reviewed":
        return "approved_watchlist"
    if asset.approval_status in {"test_position", "legacy_existing"}:
        return "candidate_reviewed"
    if asset.approval_status == "approved_watchlist" and eligible_for_investable_review:
        return "approved_investable"
    return None


def _confirmations_for_requested_status(requested_status: str) -> tuple[str, ...]:
    confirmations = list(BASE_CONFIRMATIONS)
    if requested_status == "approved_watchlist":
        confirmations.extend(sorted(WATCHLIST_CONFIRMATIONS))
    return tuple(dict.fromkeys(confirmations))


def _make_request(asset: CandidateAsset, requested_status: str) -> AssetStatusChangeRequest:
    return AssetStatusChangeRequest(
        request_id=f"real_status_review_{asset.asset_id}_{requested_status}",
        created_at="2026-06-05T12:00:00+00:00",
        asset_id=asset.asset_id,
        asset_type=asset.asset_type,
        current_status=asset.approval_status,
        requested_status=requested_status,
        rationale=f"Verified evidence provenance indicates {asset.asset_id} is ready for manual status review.",
        evidence_summary="verified_evidence_reviewed; provenance_gate_passed; manual status change required.",
        required_confirmations=_confirmations_for_requested_status(requested_status),
        manual_approval_required=True,
        auto_execute=False,
    )


def build_real_status_review_bridge(
    registry_path: str | Path | AssetRegistry,
    promotion_pack: EvidencePromotionPack,
) -> RealStatusReviewBridgeResult:
    registry = load_asset_registry(registry_path) if not isinstance(registry_path, AssetRegistry) else registry_path
    ready_assets = set(promotion_pack.assets_ready_for_real_status_review)
    requests: list[AssetStatusChangeRequest] = []
    blocked: list[RealStatusReviewBridgeLine] = []
    warnings: list[str] = list(promotion_pack.warnings)
    blockers: list[str] = list(promotion_pack.blockers)

    for asset in registry.assets:
        if asset.asset_id not in ready_assets:
            continue
        requested_status = _next_status(asset)
        if requested_status is None:
            line = RealStatusReviewBridgeLine(
                asset_id=asset.asset_id,
                ready_for_real_status_review=True,
                valid=False,
                status_request=None,
                blockers=(f"{asset.asset_id}: no safe next status transition.",),
                warnings=(),
            )
            blocked.append(line)
            blockers.extend(line.blockers)
            continue
        request = _make_request(asset, requested_status)
        validation = validate_asset_status_request(request)
        audit = audit_status_request(request, asset.sleeve)
        if validation.valid and audit.audit_ready:
            requests.append(request)
        else:
            line_blockers = tuple(dict.fromkeys((*validation.blockers, *audit.blockers)))
            line = RealStatusReviewBridgeLine(
                asset_id=asset.asset_id,
                ready_for_real_status_review=True,
                valid=False,
                status_request=request,
                blockers=line_blockers,
                warnings=tuple(dict.fromkeys((*validation.warnings, *audit.warnings))),
            )
            blocked.append(line)
            blockers.extend(line.blockers)
            warnings.extend(line.warnings)

    return RealStatusReviewBridgeResult(
        bridge_status="PREVIEW_READY" if requests else "BLOCKED",
        ready_assets_count=len(ready_assets),
        status_requests=tuple(requests),
        blocked_assets=tuple(blocked),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        manual_approval_required=True,
        approvals_created=False,
        registry_mutation_allowed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_real_status_review_bridge_from_files(
    registry_path: str | Path,
    sources_path: str | Path,
    promotion_path: str | Path,
) -> RealStatusReviewBridgeResult:
    pack = build_verified_evidence_promotion_pack_from_files(registry_path, sources_path, promotion_path)
    return build_real_status_review_bridge(registry_path, pack)


def write_status_request_previews(result: RealStatusReviewBridgeResult, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {"requests": [request.__dict__ for request in result.status_requests]}
    target.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return target
