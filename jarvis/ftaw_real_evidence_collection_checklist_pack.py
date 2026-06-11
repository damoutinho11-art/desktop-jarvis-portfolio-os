"""FTAW real evidence collection checklist pack.

This read-only checklist describes which real-world evidence should be
collected next for the FTAW candidate. It does not fetch sources, ingest
private files, verify evidence, approve assets, mutate registries, promote
evidence, recommend allocations, create orders, trade, or create an executor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_real_evidence_intake_readiness_bridge import (
    FTAWRealEvidenceIntakeReadinessBridgePack,
    build_ftaw_real_evidence_intake_readiness_bridge_from_files,
)


@dataclass(frozen=True)
class FTAWRealEvidenceChecklistItem:
    evidence_type: str
    required: bool
    source_category: str
    public_or_private: str
    commit_safety: str
    source_identity_requirements: tuple[str, ...]
    required_source_fact_fields: tuple[str, ...]
    manual_collection_instructions: str
    auto_ingest_allowed: bool = False
    auto_verify_allowed: bool = False
    verified_by_user_default: bool = False
    approval_impact: str = "none"
    buy_signal: bool = False


@dataclass(frozen=True)
class FTAWRealEvidenceCollectionChecklistPack:
    target_asset: str
    checklist_status: str
    upstream_real_evidence_intake_readiness_status: str
    required_evidence_type_count: int
    checklist_item_count: int
    public_official_item_count: int
    private_manual_item_count: int
    commit_safe_public_reference_count: int
    do_not_commit_private_evidence_count: int
    manual_only_item_count: int
    checklist_items: tuple[FTAWRealEvidenceChecklistItem, ...]
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    evidence_collected: bool = False
    evidence_verified: bool = False
    queue_eligibility_created: bool = False
    approved_asset: bool = False
    registry_mutation: bool = False
    verified_evidence_promotion: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    executor_created: bool = False
    private_file_auto_ingest: bool = False


def _checklist_items() -> tuple[FTAWRealEvidenceChecklistItem, ...]:
    return (
        FTAWRealEvidenceChecklistItem(
            evidence_type="fund_metadata",
            required=True,
            source_category="official provider product page",
            public_or_private="public_official",
            commit_safety="commit_safe_public_reference",
            source_identity_requirements=(
                "official provider identity",
                "product page identity",
                "fund name / ISIN / ticker or symbol match",
            ),
            required_source_fact_fields=("provider", "fund name", "ISIN", "ticker/symbol", "domicile or equivalent where available"),
            manual_collection_instructions="Collect only public URL/text references from the official provider product page; do not claim facts here.",
        ),
        FTAWRealEvidenceChecklistItem(
            evidence_type="fee_metadata",
            required=True,
            source_category="official provider factsheet/KIID/KID",
            public_or_private="public_official",
            commit_safety="commit_safe_public_reference",
            source_identity_requirements=("official provider identity", "factsheet/KIID/KID product identity", "fund identifier match"),
            required_source_fact_fields=("TER/OCF/fee field", "fee source", "as-of date where available"),
            manual_collection_instructions="Collect the public provider factsheet/KIID/KID reference that contains the fee field; do not download private files.",
        ),
        FTAWRealEvidenceChecklistItem(
            evidence_type="distribution_policy",
            required=True,
            source_category="official provider product page or factsheet",
            public_or_private="public_official",
            commit_safety="commit_safe_public_reference",
            source_identity_requirements=("official provider identity", "product/factsheet identity", "fund identifier match"),
            required_source_fact_fields=("accumulating/distributing policy", "distribution policy source", "as-of date where available"),
            manual_collection_instructions="Collect the public provider source reference for accumulating or distributing policy only.",
        ),
        FTAWRealEvidenceChecklistItem(
            evidence_type="platform_availability",
            required=True,
            source_category="broker/account-specific availability confirmation",
            public_or_private="private_account_specific",
            commit_safety="do_not_commit_private_evidence",
            source_identity_requirements=("account-specific broker confirmation", "platform account context", "instrument identifier match"),
            required_source_fact_fields=("platform", "available instrument identifier", "account-specific availability confirmation date"),
            manual_collection_instructions="Confirm availability inside the account manually; do not commit screenshots, exports, or private account data.",
        ),
        FTAWRealEvidenceChecklistItem(
            evidence_type="market_data",
            required=True,
            source_category="official exchange or market data page",
            public_or_private="public_market",
            commit_safety="commit_safe_public_reference",
            source_identity_requirements=("public market source identity", "ticker/symbol match", "currency match where shown"),
            required_source_fact_fields=("ticker", "currency", "price source", "as-of date"),
            manual_collection_instructions="Collect a public market/exchange/provider quote reference and as-of context; do not treat it as a trading signal.",
        ),
        FTAWRealEvidenceChecklistItem(
            evidence_type="exposure_data",
            required=True,
            source_category="official holdings/exposure source",
            public_or_private="public_official",
            commit_safety="commit_safe_public_reference",
            source_identity_requirements=("official provider identity", "holdings/exposure source identity", "fund identifier match"),
            required_source_fact_fields=("holdings source", "country exposure source", "sector exposure source", "as-of date where available"),
            manual_collection_instructions="Collect public provider references for holdings, country exposure, and sector exposure; do not claim facts in the checklist.",
        ),
        FTAWRealEvidenceChecklistItem(
            evidence_type="tax_route",
            required=True,
            source_category="user/manual tax route confirmation",
            public_or_private="manual_user_confirmation",
            commit_safety="manual_summary_only",
            source_identity_requirements=("manual user confirmation", "jurisdiction/account context", "no automatic verification"),
            required_source_fact_fields=("manual tax route note", "confirmation date", "operator summary"),
            manual_collection_instructions="Record only a manual summary of the tax-route review; do not auto-verify or commit private tax documents.",
        ),
    )


def build_ftaw_real_evidence_collection_checklist_pack(
    readiness: FTAWRealEvidenceIntakeReadinessBridgePack,
) -> FTAWRealEvidenceCollectionChecklistPack:
    items = _checklist_items()
    blocked = list(readiness.blocked_reasons)
    if readiness.real_evidence_intake_readiness_status == "READY_FOR_REAL_EVIDENCE_INTAKE_PLANNING":
        status = "REAL_EVIDENCE_COLLECTION_PLAN_READY"
        next_action = "Manually collect real evidence references for each checklist item; do not auto-ingest private files."
    elif readiness.real_evidence_intake_readiness_status == "PARTIAL_READY_FOR_REAL_EVIDENCE_INTAKE":
        status = "PARTIAL_COLLECTION_PLAN_READY"
        if not blocked:
            blocked.append("upstream real evidence intake readiness is partial.")
        next_action = "Resolve partial upstream evidence coverage before treating the collection plan as complete."
    else:
        status = "BLOCKED_NOT_READY_FOR_COLLECTION"
        if not blocked:
            blocked.append(f"upstream readiness status is {readiness.real_evidence_intake_readiness_status}.")
        next_action = "Resolve upstream readiness blockers before collecting real evidence."

    return FTAWRealEvidenceCollectionChecklistPack(
        target_asset=readiness.target_asset,
        checklist_status=status,
        upstream_real_evidence_intake_readiness_status=readiness.real_evidence_intake_readiness_status,
        required_evidence_type_count=len(readiness.required_real_evidence_types),
        checklist_item_count=len(items),
        public_official_item_count=sum(1 for item in items if item.public_or_private == "public_official"),
        private_manual_item_count=sum(1 for item in items if item.public_or_private in {"private_account_specific", "manual_user_confirmation"}),
        commit_safe_public_reference_count=sum(1 for item in items if item.commit_safety == "commit_safe_public_reference"),
        do_not_commit_private_evidence_count=sum(1 for item in items if item.commit_safety == "do_not_commit_private_evidence"),
        manual_only_item_count=sum(1 for item in items if item.public_or_private in {"private_account_specific", "manual_user_confirmation"}),
        checklist_items=items,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        evidence_collected=False,
        evidence_verified=False,
        queue_eligibility_created=False,
        approved_asset=False,
        registry_mutation=False,
        verified_evidence_promotion=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
        executor_created=False,
        private_file_auto_ingest=False,
    )


def build_ftaw_real_evidence_collection_checklist_pack_from_files(
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
    collection_checklist_config_path: str | Path,
) -> FTAWRealEvidenceCollectionChecklistPack:
    Path(collection_checklist_config_path).read_text(encoding="utf-8")
    readiness = build_ftaw_real_evidence_intake_readiness_bridge_from_files(
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
        real_evidence_intake_readiness_config_path,
    )
    return build_ftaw_real_evidence_collection_checklist_pack(readiness)
