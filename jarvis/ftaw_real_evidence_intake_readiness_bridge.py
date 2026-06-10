"""FTAW real evidence intake readiness bridge.

This read-only bridge answers whether the FTAW candidate is ready to begin
planning real evidence intake. It does not ingest private files, verify
evidence, approve assets, mutate registries, recommend allocations, create
orders, trade, or create an executor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_full_pipeline_audit_report import FTAWFullPipelineAuditPack, build_ftaw_full_pipeline_audit_pack


REQUIRED_REAL_EVIDENCE_TYPES = (
    "fund_metadata",
    "fee_metadata",
    "distribution_policy",
    "platform_availability",
    "market_data",
    "exposure_data",
    "tax_route",
)
RECOMMENDED_SOURCE_CATEGORIES = (
    "official provider product page",
    "official provider factsheet/KIID/KID",
    "official exchange or market data page",
    "broker/account-specific availability confirmation",
    "official holdings/exposure source",
    "user/manual tax route confirmation",
)
PRIVATE_MANUAL_EVIDENCE_REQUIREMENTS = (
    "broker/account-specific availability confirmation must remain private/manual and never be committed",
    "user/manual tax route confirmation must remain manual-only and never be auto-verified",
)
ACCOUNT_SPECIFIC_EVIDENCE_REQUIREMENTS = (
    "platform_availability requires account-specific confirmation, not public visibility",
)
MANUAL_ONLY_EVIDENCE_TYPES = ("platform_availability", "tax_route")


@dataclass(frozen=True)
class FTAWRealEvidenceIntakeReadinessBridgePack:
    target_asset: str
    real_evidence_intake_readiness_status: str
    upstream_audit_status: str
    final_preflight_ready: bool
    required_real_evidence_types_count: int
    required_real_evidence_types: tuple[str, ...]
    recommended_source_categories: tuple[str, ...]
    private_manual_evidence_requirements: tuple[str, ...]
    account_specific_evidence_requirements: tuple[str, ...]
    manual_only_evidence_types: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    real_evidence_collected: bool = False
    evidence_verified: bool = False
    real_evidence_queue_eligibility_created: bool = False
    approved_asset: bool = False
    registry_mutation: bool = False
    verified_evidence_promotion: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    executor_created: bool = False


def build_ftaw_real_evidence_intake_readiness_bridge(
    audit: FTAWFullPipelineAuditPack,
) -> FTAWRealEvidenceIntakeReadinessBridgePack:
    blocked: list[str] = []
    if audit.audit_status == "FINAL_PREFLIGHT_READY_SAFE" and audit.final_preflight_ready:
        status = "READY_FOR_REAL_EVIDENCE_INTAKE_PLANNING"
        next_action = "Prepare real evidence collection manually; do not ingest private files automatically."
    elif audit.audit_status == "PARTIAL_SAFE":
        status = "PARTIAL_READY_FOR_REAL_EVIDENCE_INTAKE"
        blocked.append("synthetic pipeline coverage is partial; complete required evidence planning before real intake.")
        next_action = "Collect missing real evidence categories manually; keep account-specific evidence private."
    else:
        status = "NOT_READY_FOR_REAL_EVIDENCE_INTAKE"
        blocked.append(f"upstream audit status is {audit.audit_status}.")
        if audit.earliest_blocked_stage:
            blocked.append(f"earliest blocked stage is {audit.earliest_blocked_stage}.")
        next_action = "Resolve upstream audit blockers before planning real evidence intake."
    return FTAWRealEvidenceIntakeReadinessBridgePack(
        target_asset=audit.target_asset,
        real_evidence_intake_readiness_status=status,
        upstream_audit_status=audit.audit_status,
        final_preflight_ready=audit.final_preflight_ready,
        required_real_evidence_types_count=len(REQUIRED_REAL_EVIDENCE_TYPES),
        required_real_evidence_types=REQUIRED_REAL_EVIDENCE_TYPES,
        recommended_source_categories=RECOMMENDED_SOURCE_CATEGORIES,
        private_manual_evidence_requirements=PRIVATE_MANUAL_EVIDENCE_REQUIREMENTS,
        account_specific_evidence_requirements=ACCOUNT_SPECIFIC_EVIDENCE_REQUIREMENTS,
        manual_only_evidence_types=MANUAL_ONLY_EVIDENCE_TYPES,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        real_evidence_collected=False,
        evidence_verified=False,
        real_evidence_queue_eligibility_created=False,
        approved_asset=False,
        registry_mutation=False,
        verified_evidence_promotion=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
        executor_created=False,
    )


def build_ftaw_real_evidence_intake_readiness_bridge_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    url_fetch_config_path: str | Path,
    fact_intake_config_path: str | Path,
    identity_guard_config_path: str | Path,
    queue_config_path: str | Path,
    decision_config_path: str | Path,
    preview_bridge_config_path: str | Path,
    promotion_dry_run_config_path: str | Path,
    readiness_config_path: str | Path,
    approval_review_gate_config_path: str | Path,
    human_decision_config_path: str | Path,
    registry_update_dry_run_config_path: str | Path,
    registry_update_apply_gate_config_path: str | Path,
    explicit_manual_apply_command_config_path: str | Path,
    execution_review_config_path: str | Path,
    full_pipeline_audit_config_path: str | Path,
    real_evidence_intake_readiness_config_path: str | Path,
) -> FTAWRealEvidenceIntakeReadinessBridgePack:
    Path(real_evidence_intake_readiness_config_path).read_text(encoding="utf-8")
    audit = build_ftaw_full_pipeline_audit_pack(
        source_registry_path,
        reviewed_registry_copy_path,
        url_fetch_config_path,
        fact_intake_config_path,
        identity_guard_config_path,
        queue_config_path,
        decision_config_path,
        preview_bridge_config_path,
        promotion_dry_run_config_path,
        readiness_config_path,
        approval_review_gate_config_path,
        human_decision_config_path,
        registry_update_dry_run_config_path,
        registry_update_apply_gate_config_path,
        explicit_manual_apply_command_config_path,
        execution_review_config_path,
        full_pipeline_audit_config_path,
    )
    return build_ftaw_real_evidence_intake_readiness_bridge(audit)
