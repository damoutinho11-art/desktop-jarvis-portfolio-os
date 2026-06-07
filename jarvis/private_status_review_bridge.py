"""Bridge private verified evidence and freshness into manual status request previews."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from .asset_registry import AssetRegistry, CandidateAsset, load_asset_registry
from .asset_status_workflow import WATCHLIST_CONFIRMATIONS, AssetStatusChangeRequest, validate_asset_status_request
from .evidence_freshness_policy import EvidenceFreshnessPack, build_evidence_freshness_pack_from_files
from .status_request_audit_pack import audit_status_request
from .verified_evidence_intake import VerifiedEvidencePack, build_verified_evidence_pack_from_files


BASE_CONFIRMATIONS = (
    "verified_evidence_reviewed",
    "evidence_freshness_passed",
    "provenance_gate_passed",
    "no_registry_mutation_without_manual_action",
    "manual_status_change_required",
)


@dataclass(frozen=True)
class PrivateStatusReviewConfig:
    target_asset_ids: tuple[str, ...]


@dataclass(frozen=True)
class PrivateStatusRequestPreview:
    status_request: AssetStatusChangeRequest
    freshness_summary: str

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self.status_request)
        payload["required_confirmations"] = list(self.status_request.required_confirmations)
        payload["freshness_summary"] = self.freshness_summary
        return payload


@dataclass(frozen=True)
class PrivateStatusReviewBlockedAsset:
    asset_id: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class PrivateStatusReviewBridgeResult:
    bridge_status: str
    verified_eligible_assets_count: int
    freshness_passing_assets_count: int
    request_previews: tuple[PrivateStatusRequestPreview, ...]
    blocked_assets: tuple[PrivateStatusReviewBlockedAsset, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    manual_approval_required: bool = True
    approvals_created: bool = False
    registry_mutation_allowed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False

    @property
    def status_requests(self) -> tuple[AssetStatusChangeRequest, ...]:
        return tuple(preview.status_request for preview in self.request_previews)


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")
    return value.strip()


def _require_text_list(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list.")
    return tuple(_require_text(item, field) for item in value)


def load_private_status_review_config(path: str | Path) -> PrivateStatusReviewConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "private status review bridge config")
    return PrivateStatusReviewConfig(
        target_asset_ids=_require_text_list(raw.get("target_asset_ids", ["vwce_global_core_candidate"]), "target_asset_ids")
    )


def _next_status(asset: CandidateAsset) -> str | None:
    if asset.approval_status == "candidate_unreviewed":
        return "candidate_reviewed"
    if asset.approval_status == "candidate_reviewed":
        return "approved_watchlist"
    if asset.approval_status in {"test_position", "legacy_existing"}:
        return "candidate_reviewed"
    return None


def _confirmations_for_requested_status(requested_status: str) -> tuple[str, ...]:
    confirmations = list(BASE_CONFIRMATIONS)
    if requested_status == "approved_watchlist":
        confirmations.extend(sorted(WATCHLIST_CONFIRMATIONS))
    return tuple(dict.fromkeys(confirmations))


def _freshness_by_asset(pack: EvidenceFreshnessPack) -> dict[str, tuple[bool, str, tuple[str, ...]]]:
    by_asset: dict[str, list[str]] = {}
    blockers: dict[str, list[str]] = {}
    for result in pack.results:
        by_asset.setdefault(result.asset_id, []).append(f"{result.evidence_type}={result.freshness_status}")
        if result.freshness_status != "fresh":
            blockers.setdefault(result.asset_id, []).append(
                f"{result.evidence_type}: freshness_status {result.freshness_status}; recommended_action {result.recommended_action}."
            )
    output: dict[str, tuple[bool, str, tuple[str, ...]]] = {}
    for asset_id, parts in by_asset.items():
        output[asset_id] = (asset_id not in blockers, "; ".join(parts), tuple(blockers.get(asset_id, ())))
    return output


def _make_request(asset: CandidateAsset, requested_status: str, evidence_summary: str) -> AssetStatusChangeRequest:
    return AssetStatusChangeRequest(
        request_id=f"private_status_review_{asset.asset_id}_{requested_status}",
        created_at="2026-06-07T12:00:00+00:00",
        asset_id=asset.asset_id,
        asset_type=asset.asset_type,
        current_status=asset.approval_status,
        requested_status=requested_status,
        rationale=f"Private verified evidence and freshness checks indicate {asset.asset_id} is ready for manual status review.",
        evidence_summary=evidence_summary,
        required_confirmations=_confirmations_for_requested_status(requested_status),
        manual_approval_required=True,
        auto_execute=False,
    )


def build_private_status_review_bridge(
    registry_path: str | Path | AssetRegistry,
    verified_pack: VerifiedEvidencePack,
    freshness_pack: EvidenceFreshnessPack,
    config: PrivateStatusReviewConfig,
) -> PrivateStatusReviewBridgeResult:
    registry = load_asset_registry(registry_path) if not isinstance(registry_path, AssetRegistry) else registry_path
    assets_by_id = registry.by_id()
    verified_assets = set(verified_pack.assets_with_real_status_promotion_allowed).intersection(config.target_asset_ids)
    freshness_lookup = _freshness_by_asset(freshness_pack)
    freshness_passing_assets = {
        asset_id for asset_id, (passes, _summary, _blockers) in freshness_lookup.items() if passes
    }.intersection(config.target_asset_ids)

    previews: list[PrivateStatusRequestPreview] = []
    blocked: list[PrivateStatusReviewBlockedAsset] = []
    warnings: list[str] = [*verified_pack.summary.warnings, *freshness_pack.summary.warnings]
    blockers: list[str] = [*freshness_pack.summary.blockers]

    for asset_id in config.target_asset_ids:
        asset = assets_by_id.get(asset_id)
        line_blockers: list[str] = []
        if asset is None:
            line_blockers.append(f"{asset_id}: target asset not found in registry.")
        if asset_id not in verified_assets:
            line_blockers.append(f"{asset_id}: verified evidence provenance gate has not passed.")
        passes_freshness, freshness_summary, freshness_blockers = freshness_lookup.get(
            asset_id,
            (False, "no freshness results", (f"{asset_id}: freshness check has not passed.",)),
        )
        if not passes_freshness:
            line_blockers.extend(freshness_blockers)
        if asset is not None and not line_blockers:
            requested_status = _next_status(asset)
            if requested_status is None:
                line_blockers.append(f"{asset_id}: no safe next status transition.")
            else:
                request = _make_request(
                    asset,
                    requested_status,
                    "verified_evidence_reviewed; provenance_gate_passed; evidence_freshness_passed.",
                )
                validation = validate_asset_status_request(request)
                audit = audit_status_request(request, asset.sleeve)
                if validation.valid and audit.audit_ready:
                    previews.append(PrivateStatusRequestPreview(request, freshness_summary))
                else:
                    line_blockers.extend((*validation.blockers, *audit.blockers))
                    warnings.extend((*validation.warnings, *audit.warnings))
        if line_blockers:
            unique = tuple(dict.fromkeys(line_blockers))
            blocked.append(PrivateStatusReviewBlockedAsset(asset_id, unique, ()))
            blockers.extend(unique)

    return PrivateStatusReviewBridgeResult(
        bridge_status="PREVIEW_READY" if previews else "BLOCKED",
        verified_eligible_assets_count=len(verified_assets),
        freshness_passing_assets_count=len(freshness_passing_assets),
        request_previews=tuple(previews),
        blocked_assets=tuple(blocked),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        manual_approval_required=True,
        approvals_created=False,
        registry_mutation_allowed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_private_status_review_bridge_from_files(
    registry_path: str | Path,
    intake_path: str | Path,
    freshness_policy_path: str | Path,
    config_path: str | Path,
) -> PrivateStatusReviewBridgeResult:
    return build_private_status_review_bridge(
        registry_path,
        build_verified_evidence_pack_from_files(registry_path, intake_path),
        build_evidence_freshness_pack_from_files(registry_path, intake_path, freshness_policy_path),
        load_private_status_review_config(config_path),
    )


def write_private_status_request_previews(result: PrivateStatusReviewBridgeResult, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps({"requests": [preview.to_dict() for preview in result.request_previews]}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return target
