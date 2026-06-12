"""J.A.R.V.I.S. candidate intake and watchlist expansion.

This module parses and validates manually entered candidate records and maps
them to the existing Phase 1 real-evidence pipeline. It is read-only: no
registry mutation, approval, trust/investable status, evidence verification,
evidence promotion, allocation recommendation, order, trade, executor, private
ingest, source fetching, download, or extraction is performed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUPPORTED_ASSET_TYPES = {
    "etf",
    "stock",
    "bond",
    "fund",
    "cash_equivalent",
    "crypto",
    "commodity",
    "other",
}

UNSAFE_TRUE_FIELDS = (
    "approved_asset",
    "trusted_asset",
    "investable",
    "allocation_recommendation",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "registry_mutation",
    "executor_created",
)

REQUIRED_FIELDS = (
    "candidate_id",
    "display_name",
    "asset_type",
    "symbol_or_identifier",
)

PHASE1_ROUTE_ID = "v4.27-v4.47-real-evidence-pipeline"

PHASE1_ROUTE = (
    "v4.27 real evidence intake readiness",
    "v4.28 evidence collection checklist",
    "v4.29 public source reference intake plan",
    "v4.30 manual public source reference entry recorder",
    "v4.31 manual source fact entry pack",
    "v4.32 source fact identity guard bridge",
    "v4.39 identity-guarded verification queue dry-run bridge",
    "v4.47 final real pipeline audit report",
)

EVIDENCE_CHECKLIST_BY_ASSET_TYPE = {
    "etf": (
        "instrument_identity",
        "issuer_or_provider_identity",
        "domicile_or_listing",
        "fee_or_cost_reference",
        "holdings_or_strategy_reference",
        "risk_reference",
        "official_product_page_or_document_reference",
    ),
    "fund": (
        "instrument_identity",
        "issuer_or_provider_identity",
        "domicile_or_listing",
        "fee_or_cost_reference",
        "holdings_or_strategy_reference",
        "risk_reference",
        "official_product_page_or_document_reference",
    ),
    "stock": (
        "instrument_identity",
        "issuer_identity",
        "listing_exchange",
        "financial_reporting_reference",
        "risk_reference",
        "official_investor_relations_or_exchange_reference",
    ),
    "bond": (
        "instrument_identity",
        "issuer_identity",
        "terms_and_maturity_reference",
        "credit_risk_reference",
        "official_issuer_or_exchange_reference",
        "manual_review_required",
    ),
    "cash_equivalent": (
        "instrument_identity",
        "issuer_or_provider_identity",
        "liquidity_terms_reference",
        "capital_risk_reference",
        "official_product_page_or_document_reference",
        "manual_review_required",
    ),
    "crypto": (
        "instrument_identity",
        "protocol_or_network_identity",
        "custody_route_reference",
        "market_data_reference",
        "risk_reference",
        "official_protocol_or_market_reference",
        "manual_review_required",
    ),
    "commodity": (
        "instrument_identity",
        "issuer_or_provider_identity",
        "underlying_exposure_reference",
        "storage_or_structure_reference",
        "risk_reference",
        "official_product_page_or_document_reference",
        "manual_review_required",
    ),
    "other": (
        "instrument_identity",
        "issuer_or_provider_identity",
        "official_source_identity_check",
        "risk_reference",
        "manual_review_required",
    ),
}


@dataclass(frozen=True)
class CandidateIntakeResult:
    candidate_id: str
    display_name: str
    asset_type: str
    symbol_or_identifier: str
    issuer_or_provider: str
    market_or_region: str
    currency: str
    source_context: str
    user_rationale: str
    intake_status: str
    created_by_manual_entry: bool
    manual_entry_required: bool
    evidence_pipeline_required: bool
    phase1_route: str
    notes: str
    evidence_checklist_categories: tuple[str, ...]
    route_summary: tuple[str, ...]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    approved_asset: bool = False
    trusted_asset: bool = False
    investable: bool = False
    allocation_recommendation: bool = False
    buy_signal: bool = False
    sell_signal: bool = False
    trade_executed: bool = False
    registry_mutation: bool = False
    executor_created: bool = False
    registry_file_written: bool = False
    evidence_verified: bool = False
    verified_evidence_promoted: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    private_file_auto_ingest: bool = False
    automatic_source_fetching: bool = False
    automatic_downloads: bool = False
    automatic_fact_extraction: bool = False


@dataclass(frozen=True)
class CandidateIntakePack:
    title: str
    version: str
    overall_status: str
    candidate_count: int
    candidates: tuple[CandidateIntakeResult, ...]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    phase1_route: tuple[str, ...]
    approved_asset: bool = False
    trusted_asset: bool = False
    investable: bool = False
    registry_mutation: bool = False
    registry_file_written: bool = False
    evidence_verified: bool = False
    verified_evidence_promoted: bool = False
    allocation_recommendation: bool = False
    buy_signal: bool = False
    sell_signal: bool = False
    trade_executed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False
    executor_created: bool = False
    broker_authenticated_api: bool = False
    credentials: bool = False
    private_file_auto_ingest: bool = False
    automatic_source_fetching: bool = False
    automatic_downloads: bool = False
    automatic_fact_extraction: bool = False


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _categories(asset_type: str) -> tuple[str, ...]:
    normalized = asset_type if asset_type in EVIDENCE_CHECKLIST_BY_ASSET_TYPE else "other"
    return EVIDENCE_CHECKLIST_BY_ASSET_TYPE[normalized]


def validate_candidate_record(raw: dict[str, Any]) -> CandidateIntakeResult:
    candidate_id = _text(raw.get("candidate_id"))
    display_name = _text(raw.get("display_name"))
    asset_type = _text(raw.get("asset_type")).lower()
    symbol = _text(raw.get("symbol_or_identifier"))
    blocked: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_FIELDS:
        if not _text(raw.get(field)):
            blocked.append(f"{field} is required.")

    if not _bool(raw.get("created_by_manual_entry")):
        blocked.append("created_by_manual_entry must be true.")
    if not _bool(raw.get("manual_entry_required")):
        blocked.append("manual_entry_required must be true.")
    if not _bool(raw.get("evidence_pipeline_required")):
        blocked.append("evidence_pipeline_required must be true.")
    if _text(raw.get("phase1_route")) != PHASE1_ROUTE_ID:
        blocked.append(f"phase1_route must be {PHASE1_ROUTE_ID}.")

    for field in UNSAFE_TRUE_FIELDS:
        if _bool(raw.get(field)):
            blocked.append(f"{field} must be false or absent.")

    if asset_type not in SUPPORTED_ASSET_TYPES:
        warnings.append(f"asset_type {asset_type or 'missing'} is not in supported list; treating as other/manual review.")
        asset_type = asset_type or "other"
    if asset_type == "other":
        warnings.append("other asset type requires manual review before Phase 1 evidence routing.")

    if blocked:
        status = "CANDIDATE_INTAKE_BLOCKED_SAFE"
    elif warnings:
        status = "CANDIDATE_INTAKE_PARTIAL_SAFE"
    else:
        status = "CANDIDATE_INTAKE_READY_FOR_PHASE1_EVIDENCE_PIPELINE"

    return CandidateIntakeResult(
        candidate_id=candidate_id or "unknown_candidate",
        display_name=display_name or "unknown display name",
        asset_type=asset_type or "other",
        symbol_or_identifier=symbol or "unknown",
        issuer_or_provider=_text(raw.get("issuer_or_provider")),
        market_or_region=_text(raw.get("market_or_region")),
        currency=_text(raw.get("currency")),
        source_context=_text(raw.get("source_context")),
        user_rationale=_text(raw.get("user_rationale")),
        intake_status=status,
        created_by_manual_entry=_bool(raw.get("created_by_manual_entry")),
        manual_entry_required=_bool(raw.get("manual_entry_required")),
        evidence_pipeline_required=_bool(raw.get("evidence_pipeline_required")),
        phase1_route=_text(raw.get("phase1_route")),
        notes=_text(raw.get("notes")),
        evidence_checklist_categories=_categories(asset_type or "other"),
        route_summary=PHASE1_ROUTE,
        blocked_reasons=tuple(blocked),
        warnings=tuple(warnings),
        approved_asset=False,
        trusted_asset=False,
        investable=False,
        allocation_recommendation=False,
        buy_signal=False,
        sell_signal=False,
        trade_executed=False,
        registry_mutation=False,
        executor_created=False,
    )


def build_candidate_intake_pack(data: dict[str, Any]) -> CandidateIntakePack:
    raw_candidates = data.get("candidates", [])
    if not isinstance(raw_candidates, list):
        raise ValueError("candidate intake data must contain a candidates list")

    candidates = tuple(validate_candidate_record(candidate) for candidate in raw_candidates if isinstance(candidate, dict))
    blocked_reasons = tuple(
        f"{candidate.candidate_id}: {reason}"
        for candidate in candidates
        for reason in candidate.blocked_reasons
    )
    warnings = tuple(
        f"{candidate.candidate_id}: {warning}"
        for candidate in candidates
        for warning in candidate.warnings
    )
    statuses = {candidate.intake_status for candidate in candidates}
    if not candidates or statuses == {"CANDIDATE_INTAKE_BLOCKED_SAFE"}:
        overall = "CANDIDATE_INTAKE_BLOCKED_SAFE"
    elif statuses == {"CANDIDATE_INTAKE_READY_FOR_PHASE1_EVIDENCE_PIPELINE"}:
        overall = "CANDIDATE_INTAKE_READY_FOR_PHASE1_EVIDENCE_PIPELINE"
    else:
        overall = "CANDIDATE_INTAKE_PARTIAL_SAFE"

    return CandidateIntakePack(
        title=_text(data.get("title")) or "J.A.R.V.I.S. Candidate Intake",
        version=_text(data.get("version")) or "v4.49",
        overall_status=overall,
        candidate_count=len(candidates),
        candidates=candidates,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        phase1_route=PHASE1_ROUTE,
    )


def load_candidate_intake(path: str | Path) -> CandidateIntakePack:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return build_candidate_intake_pack(data)
