"""Dry-run promotion planner for FTAW verified evidence previews.

This layer plans what would be promoted from preview-ready records. It never
writes to the verified evidence store, promotes evidence, approves assets,
mutates registries, recommends allocations, creates orders, or trades.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_verified_evidence_preview_bridge import (
    FTAWVerifiedEvidencePreviewBridgePack,
    FTAWVerifiedEvidencePreviewRecord,
    build_ftaw_verified_evidence_preview_bridge_from_files,
)


@dataclass(frozen=True)
class FTAWVerifiedEvidencePromotionDryRunRecord:
    asset_id: str
    evidence_type: str
    source_name: str
    source_quality: str
    extracted_facts: dict[str, object]
    preview_record_reference: str
    preview_status: str
    planned_promotion_status: str
    reason: str
    promotion_mode: str = "dry_run"
    verified_by_user: bool = False
    no_verified_evidence_promotion: bool = True
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


@dataclass(frozen=True)
class FTAWVerifiedEvidencePromotionDryRunPack:
    dry_run_status: str
    target_asset: str
    preview_records_count: int
    planned_for_promotion_count: int
    blocked_or_excluded_count: int
    plan_records: tuple[FTAWVerifiedEvidencePromotionDryRunRecord, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    no_verified_evidence_promotion: bool = True
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _plan_record(record: FTAWVerifiedEvidencePreviewRecord) -> FTAWVerifiedEvidencePromotionDryRunRecord:
    if record.preview_status == "preview_ready":
        status = "planned_for_promotion"
        reason = "Preview record is ready; dry-run plans promotion only."
    else:
        status = f"excluded_{record.preview_status}"
        reason = "Preview record is not preview_ready; dry-run excludes it."
    return FTAWVerifiedEvidencePromotionDryRunRecord(
        asset_id=record.asset_id,
        evidence_type=record.evidence_type,
        source_name=record.source_name,
        source_quality=record.source_quality,
        extracted_facts=dict(record.extracted_facts),
        preview_record_reference=record.queue_item_reference,
        preview_status=record.preview_status,
        planned_promotion_status=status,
        reason=reason,
        promotion_mode="dry_run",
        verified_by_user=False,
        no_verified_evidence_promotion=True,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_verified_evidence_promotion_dry_run(
    preview_pack: FTAWVerifiedEvidencePreviewBridgePack,
) -> FTAWVerifiedEvidencePromotionDryRunPack:
    plan_records = tuple(_plan_record(record) for record in preview_pack.preview_records)
    planned = sum(record.planned_promotion_status == "planned_for_promotion" for record in plan_records)
    excluded = len(plan_records) - planned
    if planned:
        status = "DRY_RUN_PLANNED"
    elif plan_records:
        status = "NO_PROMOTIONS_PLANNED"
    else:
        status = "NO_PREVIEW_RECORDS"
    return FTAWVerifiedEvidencePromotionDryRunPack(
        dry_run_status=status,
        target_asset=preview_pack.target_asset,
        preview_records_count=len(preview_pack.preview_records),
        planned_for_promotion_count=planned,
        blocked_or_excluded_count=excluded,
        plan_records=plan_records,
        warnings=preview_pack.warnings,
        blockers=preview_pack.blockers,
        no_verified_evidence_promotion=True,
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_ftaw_verified_evidence_promotion_dry_run_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
    preview_bridge_config_path: str | Path,
    promotion_dry_run_config_path: str | Path,
) -> FTAWVerifiedEvidencePromotionDryRunPack:
    Path(promotion_dry_run_config_path).read_text(encoding="utf-8")
    preview_pack = build_ftaw_verified_evidence_preview_bridge_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
    )
    return build_ftaw_verified_evidence_promotion_dry_run(preview_pack)
