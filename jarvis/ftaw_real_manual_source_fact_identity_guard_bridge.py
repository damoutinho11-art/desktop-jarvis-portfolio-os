"""FTAW real manual source fact identity guard bridge.

This read-only bridge checks whether manually entered public source facts are
ready for a future manual identity guard review. It does not run the identity
guard as an approval, create pass records, create queue eligibility, verify
evidence, approve assets, mutate registries, promote evidence, recommend
allocations, create orders, trade, or create an executor.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .ftaw_manual_source_fact_entry_pack import (
    FTAWManualSourceFactEntryPack,
    build_ftaw_manual_source_fact_entry_pack_from_files,
)


REQUIRED_PUBLIC_FACT_TYPES = ("fund_metadata", "fee_metadata", "distribution_policy", "market_data", "exposure_data")
IDENTITY_FIELDS = ("provider", "fund_name", "isin", "ticker_or_symbol_or_market_ticker")


@dataclass(frozen=True)
class FTAWIdentityFieldCoverage:
    field_name: str
    present: bool
    source_evidence_type: str
    value_preview: str


@dataclass(frozen=True)
class FTAWIdentityConsistencyCheck:
    check_name: str
    status: str
    reason: str


@dataclass(frozen=True)
class FTAWIdentityReviewPacketPreview:
    review_packet_created: bool
    review_packet_preview_only: bool = True
    identity_guard_pass_created: bool = False
    queue_eligibility_created: bool = False
    evidence_verified: bool = False
    approved_asset: bool = False
    buy_signal: bool = False


@dataclass(frozen=True)
class FTAWRealManualSourceFactIdentityGuardBridgePack:
    target_asset: str
    bridge_status: str
    upstream_manual_source_fact_status: str
    accepted_source_fact_count: int
    required_public_fact_type_count: int
    present_public_fact_type_count: int
    missing_public_fact_type_count: int
    present_public_fact_types: tuple[str, ...]
    missing_public_fact_types: tuple[str, ...]
    identity_field_coverage: tuple[FTAWIdentityFieldCoverage, ...]
    identity_consistency_status: str
    identity_consistency_checks: tuple[FTAWIdentityConsistencyCheck, ...]
    manual_private_outstanding_count: int
    manual_private_outstanding: tuple
    blocked_reasons: tuple[str, ...]
    next_manual_action: str
    identity_review_packet_preview: FTAWIdentityReviewPacketPreview
    evidence_verified: bool = False
    identity_guard_pass_records_created: bool = False
    queue_eligibility_created: bool = False
    verified_evidence_promotion: bool = False
    approved_asset: bool = False
    registry_mutation: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    executor_created: bool = False
    private_file_auto_ingest: bool = False
    automatic_source_fetching: bool = False
    automatic_downloads: bool = False
    automatic_fact_extraction: bool = False


def _facts_by_type(pack: FTAWManualSourceFactEntryPack) -> dict[str, dict]:
    return {record.evidence_type: record.facts for record in pack.accepted_source_fact_records}


def _coverage(pack: FTAWManualSourceFactEntryPack) -> tuple[FTAWIdentityFieldCoverage, ...]:
    facts = _facts_by_type(pack)
    fund = facts.get("fund_metadata", {})
    market = facts.get("market_data", {})
    ticker_value = fund.get("ticker_or_symbol") or market.get("market_ticker")
    return (
        FTAWIdentityFieldCoverage("provider", bool(fund.get("provider")), "fund_metadata", str(fund.get("provider", ""))),
        FTAWIdentityFieldCoverage("fund_name", bool(fund.get("fund_name")), "fund_metadata", str(fund.get("fund_name", ""))),
        FTAWIdentityFieldCoverage("isin", bool(fund.get("isin")), "fund_metadata", str(fund.get("isin", ""))),
        FTAWIdentityFieldCoverage(
            "ticker_or_symbol_or_market_ticker",
            bool(ticker_value),
            "fund_metadata/market_data",
            str(ticker_value or ""),
        ),
    )


def _consistency_checks(pack: FTAWManualSourceFactEntryPack) -> tuple[FTAWIdentityConsistencyCheck, ...]:
    facts = _facts_by_type(pack)
    fund_ticker = str(facts.get("fund_metadata", {}).get("ticker_or_symbol", "")).strip()
    market_ticker = str(facts.get("market_data", {}).get("market_ticker", "")).strip()
    if fund_ticker and market_ticker:
        if fund_ticker.casefold() == market_ticker.casefold():
            status = "consistent"
            reason = "ticker_or_symbol and market_ticker match"
        else:
            status = "inconsistent"
            reason = "ticker_or_symbol and market_ticker do not match"
    else:
        status = "not_applicable"
        reason = "ticker overlap requires both fund_metadata ticker_or_symbol and market_data market_ticker"
    return (FTAWIdentityConsistencyCheck("ticker_overlap", status, reason),)


def build_ftaw_real_manual_source_fact_identity_guard_bridge(
    fact_pack: FTAWManualSourceFactEntryPack,
) -> FTAWRealManualSourceFactIdentityGuardBridgePack:
    present_types = tuple(sorted({record.evidence_type for record in fact_pack.accepted_source_fact_records}))
    missing_types = tuple(evidence_type for evidence_type in REQUIRED_PUBLIC_FACT_TYPES if evidence_type not in present_types)
    coverage = _coverage(fact_pack)
    missing_identity = tuple(item.field_name for item in coverage if not item.present)
    consistency = _consistency_checks(fact_pack)
    inconsistent = tuple(check for check in consistency if check.status == "inconsistent")
    blocked = list(fact_pack.blocked_reasons)
    blocked.extend(f"missing public fact type {evidence_type}" for evidence_type in missing_types)
    blocked.extend(f"missing identity field {field_name}" for field_name in missing_identity)
    blocked.extend(check.reason for check in inconsistent)

    all_manual_flags_ok = all(
        record.manual_entry
        and not record.auto_extracted
        and not record.verified
        and not record.identity_guard_pass_created
        and not record.queue_eligibility_created
        for record in fact_pack.accepted_source_fact_records
    )
    if not all_manual_flags_ok:
        blocked.append("accepted source fact record safety flags are not identity-bridge safe")

    if fact_pack.source_fact_entry_status == "BLOCKED_NO_PUBLIC_SOURCE_REFERENCES" or fact_pack.accepted_source_fact_record_count == 0:
        status = "BLOCKED_NO_MANUAL_SOURCE_FACTS"
        packet_created = False
        next_action = "Enter manual source facts before preparing identity guard review."
    elif blocked:
        status = "PARTIAL_IDENTITY_GUARD_BRIDGE_READY"
        packet_created = False
        next_action = "Resolve missing or inconsistent identity facts before manual identity guard review."
    else:
        status = "READY_FOR_MANUAL_IDENTITY_GUARD_REVIEW"
        packet_created = True
        next_action = "Prepare a future manual identity guard review; do not create pass records automatically."

    return FTAWRealManualSourceFactIdentityGuardBridgePack(
        target_asset=fact_pack.target_asset,
        bridge_status=status,
        upstream_manual_source_fact_status=fact_pack.source_fact_entry_status,
        accepted_source_fact_count=fact_pack.accepted_source_fact_record_count,
        required_public_fact_type_count=len(REQUIRED_PUBLIC_FACT_TYPES),
        present_public_fact_type_count=len(present_types),
        missing_public_fact_type_count=len(missing_types),
        present_public_fact_types=present_types,
        missing_public_fact_types=missing_types,
        identity_field_coverage=coverage,
        identity_consistency_status="inconsistent" if inconsistent else "ready_for_review",
        identity_consistency_checks=consistency,
        manual_private_outstanding_count=fact_pack.manual_private_outstanding_count,
        manual_private_outstanding=fact_pack.manual_private_outstanding,
        blocked_reasons=tuple(dict.fromkeys(blocked)),
        next_manual_action=next_action,
        identity_review_packet_preview=FTAWIdentityReviewPacketPreview(review_packet_created=packet_created),
        evidence_verified=False,
        identity_guard_pass_records_created=False,
        queue_eligibility_created=False,
        verified_evidence_promotion=False,
        approved_asset=False,
        registry_mutation=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
        executor_created=False,
        private_file_auto_ingest=False,
        automatic_source_fetching=False,
        automatic_downloads=False,
        automatic_fact_extraction=False,
    )


def build_ftaw_real_manual_source_fact_identity_guard_bridge_from_files(
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
    public_source_reference_plan_config_path: str | Path,
    manual_public_source_reference_entry_config_path: str | Path,
    manual_source_fact_entry_config_path: str | Path,
    identity_guard_bridge_config_path: str | Path,
) -> FTAWRealManualSourceFactIdentityGuardBridgePack:
    Path(identity_guard_bridge_config_path).read_text(encoding="utf-8")
    fact_pack = build_ftaw_manual_source_fact_entry_pack_from_files(
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
        collection_checklist_config_path,
        public_source_reference_plan_config_path,
        manual_public_source_reference_entry_config_path,
        manual_source_fact_entry_config_path,
    )
    return build_ftaw_real_manual_source_fact_identity_guard_bridge(fact_pack)
