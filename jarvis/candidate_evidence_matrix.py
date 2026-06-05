"""Evidence coverage matrix for candidate asset manual-review readiness."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .asset_registry import CRYPTO_REQUIRED_FIELDS, ETF_REQUIRED_FIELDS, CandidateAsset, load_asset_registry
from .asset_scoring_engine import clamp_score, score_registry
from .exposure_loader import load_exposure_data
from .market_data_loader import load_market_data
from .portfolio_policy import load_portfolio_policy


INCOMPLETE_TEXT = {"", "unknown", "UNKNOWN", "manual_placeholder", "n/a", "N/A"}
COMMON_METADATA_FIELDS = (
    "asset_id",
    "name",
    "asset_type",
    "sleeve",
    "ticker",
    "isin_or_symbol",
    "platforms",
    "currency",
    "domicile",
    "distribution_policy",
    "ter_or_fee",
    "data_source",
    "approval_status",
    "risk_level",
    "notes",
)


@dataclass(frozen=True)
class CandidateEvidenceRow:
    asset_id: str
    asset_type: str
    sleeve: str
    approval_status: str
    has_registry_metadata: bool
    has_scorecard: bool
    has_market_data: bool
    has_exposure_data: bool
    has_platform_data: bool
    has_tax_route_data: bool
    has_custody_data: bool
    evidence_score: float
    missing_evidence: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    eligible_for_manual_review: bool
    manual_approval_required: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "sleeve": self.sleeve,
            "approval_status": self.approval_status,
            "has_registry_metadata": self.has_registry_metadata,
            "has_scorecard": self.has_scorecard,
            "has_market_data": self.has_market_data,
            "has_exposure_data": self.has_exposure_data,
            "has_platform_data": self.has_platform_data,
            "has_tax_route_data": self.has_tax_route_data,
            "has_custody_data": self.has_custody_data,
            "evidence_score": self.evidence_score,
            "missing_evidence": list(self.missing_evidence),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "eligible_for_manual_review": self.eligible_for_manual_review,
            "manual_approval_required": self.manual_approval_required,
        }


@dataclass(frozen=True)
class CandidateEvidenceSummary:
    total_candidates: int
    eligible_for_manual_review_count: int
    blocked_count: int
    missing_market_data_count: int
    missing_exposure_data_count: int
    missing_platform_data_count: int
    by_sleeve: dict[str, int]
    by_asset_type: dict[str, int]

    def to_dict(self) -> dict[str, object]:
        return {
            "total_candidates": self.total_candidates,
            "eligible_for_manual_review_count": self.eligible_for_manual_review_count,
            "blocked_count": self.blocked_count,
            "missing_market_data_count": self.missing_market_data_count,
            "missing_exposure_data_count": self.missing_exposure_data_count,
            "missing_platform_data_count": self.missing_platform_data_count,
            "by_sleeve": self.by_sleeve,
            "by_asset_type": self.by_asset_type,
        }


@dataclass(frozen=True)
class CandidateEvidenceMatrix:
    status: str
    rows: tuple[CandidateEvidenceRow, ...]
    summary: CandidateEvidenceSummary
    manual_approval_required: bool = True
    registry_mutation_allowed: bool = False
    approvals_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "rows": [row.to_dict() for row in self.rows],
            "summary": self.summary.to_dict(),
            "manual_approval_required": self.manual_approval_required,
            "registry_mutation_allowed": self.registry_mutation_allowed,
            "approvals_created": self.approvals_created,
            "buy_sell_requests_created": self.buy_sell_requests_created,
            "trades_executed": self.trades_executed,
        }


def _raw_asset_lookup(path: str | Path) -> dict[str, dict[str, Any]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    assets = raw.get("assets") if isinstance(raw, dict) else []
    if not isinstance(assets, list):
        return {}
    return {str(asset.get("asset_id")): asset for asset in assets if isinstance(asset, dict)}


def _complete(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip() not in INCOMPLETE_TEXT
    if isinstance(value, (list, tuple)):
        return bool(value) and all(_complete(item) for item in value)
    return True


def _metadata_present(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple)):
        return bool(value) and all(_metadata_present(item) for item in value)
    return True


def _has_registry_metadata(asset: CandidateAsset, raw_asset: dict[str, Any] | None) -> bool:
    if raw_asset is None:
        return False
    fields = list(COMMON_METADATA_FIELDS)
    if asset.asset_type == "ETF":
        fields.extend(ETF_REQUIRED_FIELDS)
    if asset.asset_type == "crypto":
        fields.extend(CRYPTO_REQUIRED_FIELDS)
    return all(_metadata_present(raw_asset.get(field)) for field in fields)


def _has_platform_data(asset: CandidateAsset, policy_sleeves: dict[str, object]) -> bool:
    if not _complete(asset.platforms):
        return False
    sleeve_policy = policy_sleeves.get(asset.sleeve)
    return bool(sleeve_policy and asset.asset_type in getattr(sleeve_policy, "allowed_asset_types", ()))


def _has_tax_route_data(asset: CandidateAsset) -> bool:
    if asset.asset_type == "ETF":
        return all(_complete(value) for value in (asset.currency, asset.domicile, asset.distribution_policy))
    if asset.asset_type == "crypto":
        return asset.mica_route_possible is not None
    return True


def _has_custody_data(asset: CandidateAsset) -> bool:
    if asset.asset_type == "crypto":
        return _complete(asset.custody_platforms) and asset.transferable is not None
    return True


def _required_evidence(asset: CandidateAsset) -> tuple[str, ...]:
    if asset.asset_type == "ETF":
        return (
            "registry_metadata",
            "scorecard",
            "market_data",
            "exposure_data",
            "platform_data",
            "tax_route_data",
        )
    if asset.asset_type == "crypto":
        return (
            "registry_metadata",
            "scorecard",
            "market_data",
            "platform_data",
            "tax_route_data",
            "custody_data",
        )
    return ("registry_metadata", "scorecard", "platform_data")


def _evidence_value(name: str, values: dict[str, bool]) -> bool:
    return bool(values.get(name, False))


def build_candidate_evidence_matrix(
    registry_path: str | Path,
    market_data_path: str | Path,
    exposure_path: str | Path,
    policy_path: str | Path,
) -> CandidateEvidenceMatrix:
    registry = load_asset_registry(registry_path)
    raw_assets = _raw_asset_lookup(registry_path)
    scorecards = {scorecard.asset_id: scorecard for scorecard in score_registry(registry_path)}
    market_asset_ids = {series.asset_id for series in load_market_data(market_data_path).series}
    exposures = load_exposure_data(exposure_path).by_asset_id()
    policy = load_portfolio_policy(policy_path)
    policy_sleeves = policy.sleeve_by_id()

    rows: list[CandidateEvidenceRow] = []
    for asset in registry.assets:
        has_registry_metadata = _has_registry_metadata(asset, raw_assets.get(asset.asset_id))
        has_scorecard = asset.asset_id in scorecards
        has_market_data = asset.asset_id in market_asset_ids
        has_exposure_data = asset.asset_id in exposures
        has_platform_data = _has_platform_data(asset, policy_sleeves)
        has_tax_route_data = _has_tax_route_data(asset)
        has_custody_data = _has_custody_data(asset)
        values = {
            "registry_metadata": has_registry_metadata,
            "scorecard": has_scorecard,
            "market_data": has_market_data,
            "exposure_data": has_exposure_data,
            "platform_data": has_platform_data,
            "tax_route_data": has_tax_route_data,
            "custody_data": has_custody_data,
        }
        required = _required_evidence(asset)
        missing = tuple(name for name in required if not _evidence_value(name, values))
        blockers = tuple(f"{asset.asset_id}: missing {name} evidence." for name in missing)
        warnings: list[str] = []
        if asset.asset_type == "crypto" and not has_exposure_data:
            warnings.append(f"{asset.asset_id}: ETF-style exposure data not required for crypto review.")
        evidence_score = clamp_score(100.0 * (len(required) - len(missing)) / len(required))
        rows.append(
            CandidateEvidenceRow(
                asset_id=asset.asset_id,
                asset_type=asset.asset_type,
                sleeve=asset.sleeve,
                approval_status=asset.approval_status,
                has_registry_metadata=has_registry_metadata,
                has_scorecard=has_scorecard,
                has_market_data=has_market_data,
                has_exposure_data=has_exposure_data,
                has_platform_data=has_platform_data,
                has_tax_route_data=has_tax_route_data,
                has_custody_data=has_custody_data,
                evidence_score=evidence_score,
                missing_evidence=missing,
                blockers=blockers,
                warnings=tuple(warnings),
                eligible_for_manual_review=not blockers,
                manual_approval_required=True,
            )
        )

    by_sleeve: dict[str, int] = {}
    by_asset_type: dict[str, int] = {}
    for row in rows:
        by_sleeve[row.sleeve] = by_sleeve.get(row.sleeve, 0) + 1
        by_asset_type[row.asset_type] = by_asset_type.get(row.asset_type, 0) + 1

    summary = CandidateEvidenceSummary(
        total_candidates=len(rows),
        eligible_for_manual_review_count=sum(row.eligible_for_manual_review for row in rows),
        blocked_count=sum(not row.eligible_for_manual_review for row in rows),
        missing_market_data_count=sum("market_data" in row.missing_evidence for row in rows),
        missing_exposure_data_count=sum("exposure_data" in row.missing_evidence for row in rows),
        missing_platform_data_count=sum("platform_data" in row.missing_evidence for row in rows),
        by_sleeve=dict(sorted(by_sleeve.items())),
        by_asset_type=dict(sorted(by_asset_type.items())),
    )
    return CandidateEvidenceMatrix(
        status="REVIEW_ELIGIBLE" if summary.eligible_for_manual_review_count else "BLOCKED",
        rows=tuple(rows),
        summary=summary,
        manual_approval_required=True,
        registry_mutation_allowed=False,
        approvals_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )
