"""Approval gate for future allocation eligibility."""

from __future__ import annotations

from dataclasses import dataclass

from .asset_registry import CandidateAsset


@dataclass(frozen=True)
class ApprovalGateResult:
    asset_id: str
    eligible_for_allocation: bool
    reason: str


def check_asset_approval(asset: CandidateAsset) -> ApprovalGateResult:
    if asset.approval_status == "approved_investable":
        return ApprovalGateResult(
            asset_id=asset.asset_id,
            eligible_for_allocation=True,
            reason=f"{asset.asset_id} is approved_investable and eligible for future allocation.",
        )
    return ApprovalGateResult(
        asset_id=asset.asset_id,
        eligible_for_allocation=False,
        reason=f"{asset.asset_id} blocked: approval_status is {asset.approval_status}, not approved_investable.",
    )
