"""Manual candidate watchlist entry pack.

This read-only layer validates manually entered watchlist records and previews
candidate-intake records for v4.49. It does not mutate registries, approve or
trust assets, verify or promote evidence, recommend allocations, create orders,
trade, create an executor, use broker APIs, handle credentials, ingest private
files, fetch sources, download sources, or extract facts.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_ASSET_TYPES = {
    "etf",
    "stock",
    "bond",
    "fund",
    "cash_equivalent",
    "crypto",
    "commodity",
    "other",
}

INTENDED_ROUTE = "v4.50-manual-watchlist-entry->v4.49-candidate-intake->v4.27-v4.47-real-evidence-pipeline"
PHASE1_ROUTE = "v4.27-v4.47-real-evidence-pipeline"

REQUIRED_FIELDS = (
    "watchlist_entry_id",
    "candidate_id",
    "display_name",
    "asset_type",
    "symbol_or_identifier",
    "watchlist_reason",
)

UNSAFE_TRUE_FIELDS = (
    "approved_asset",
    "trusted_asset",
    "investable",
    "verified_evidence",
    "promoted_verified_evidence",
    "allocation_recommendation",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "registry_mutation",
    "executor_created",
    "broker_api_used",
    "credentials_used",
    "automatic_source_fetching",
    "automatic_download",
    "private_file_ingested",
)


@dataclass(frozen=True)
class ManualCandidateWatchlistEntryResult:
    watchlist_entry_id: str
    candidate_id: str
    display_name: str
    asset_type: str
    symbol_or_identifier: str
    issuer_or_provider: str
    market_or_region: str
    currency: str
    watchlist_reason: str
    watchlist_source_context: str
    manually_entered_by_user: bool
    manual_entry_timestamp: str
    intended_route: str
    candidate_intake_required: bool
    evidence_pipeline_required: bool
    manual_review_required: bool
    notes: str
    entry_status: str
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    candidate_intake_preview_available: bool
    candidate_intake_preview: dict[str, Any] | None
    approved_asset: bool = False
    trusted_asset: bool = False
    investable: bool = False
    verified_evidence: bool = False
    promoted_verified_evidence: bool = False
    allocation_recommendation: bool = False
    portfolio_weight: bool = False
    buy_signal: bool = False
    sell_signal: bool = False
    trade_executed: bool = False
    registry_mutation: bool = False
    registry_file_written: bool = False
    executor_created: bool = False
    broker_api_used: bool = False
    credentials_used: bool = False
    private_file_ingested: bool = False
    automatic_source_fetching: bool = False
    automatic_download: bool = False
    automatic_fact_extraction: bool = False


@dataclass(frozen=True)
class ManualCandidateWatchlistEntryPack:
    title: str
    version: str
    overall_status: str
    watchlist_entry_count: int
    entries: tuple[ManualCandidateWatchlistEntryResult, ...]
    blocked_reasons: tuple[str, ...]
    warnings: tuple[str, ...]
    approved_asset: bool = False
    trusted_asset: bool = False
    investable: bool = False
    verified_evidence: bool = False
    promoted_verified_evidence: bool = False
    allocation_recommendation: bool = False
    portfolio_weight: bool = False
    buy_signal: bool = False
    sell_signal: bool = False
    trade_executed: bool = False
    registry_mutation: bool = False
    registry_file_written: bool = False
    executor_created: bool = False
    broker_api_used: bool = False
    credentials_used: bool = False
    private_file_ingested: bool = False
    automatic_source_fetching: bool = False
    automatic_download: bool = False
    automatic_fact_extraction: bool = False


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def preview_candidate_intake_record(entry: ManualCandidateWatchlistEntryResult) -> dict[str, Any]:
    return {
        "candidate_id": entry.candidate_id,
        "display_name": entry.display_name,
        "asset_type": entry.asset_type,
        "symbol_or_identifier": entry.symbol_or_identifier,
        "issuer_or_provider": entry.issuer_or_provider,
        "market_or_region": entry.market_or_region,
        "currency": entry.currency,
        "source_context": entry.watchlist_source_context,
        "user_rationale": entry.watchlist_reason,
        "intake_status": "candidate_intake_required_pending",
        "created_by_manual_entry": True,
        "manual_entry_required": True,
        "evidence_pipeline_required": True,
        "phase1_route": PHASE1_ROUTE,
        "notes": entry.notes,
        "approved_asset": False,
        "trusted_asset": False,
        "investable": False,
        "allocation_recommendation": False,
        "buy_signal": False,
        "sell_signal": False,
        "trade_executed": False,
        "registry_mutation": False,
        "executor_created": False,
    }


def validate_watchlist_entry(raw: dict[str, Any]) -> ManualCandidateWatchlistEntryResult:
    asset_type = _text(raw.get("asset_type")).lower()
    blocked: list[str] = []
    warnings: list[str] = []

    for field in REQUIRED_FIELDS:
        if not _text(raw.get(field)):
            blocked.append(f"{field} is required.")
    if not _bool(raw.get("manually_entered_by_user")):
        blocked.append("manually_entered_by_user must be true.")
    if not _bool(raw.get("candidate_intake_required")):
        blocked.append("candidate_intake_required must be true.")
    if not _bool(raw.get("evidence_pipeline_required")):
        blocked.append("evidence_pipeline_required must be true.")
    if not _bool(raw.get("manual_review_required")):
        blocked.append("manual_review_required must be true.")
    if _text(raw.get("intended_route")) != INTENDED_ROUTE:
        blocked.append(f"intended_route must be {INTENDED_ROUTE}.")
    for field in UNSAFE_TRUE_FIELDS:
        if _bool(raw.get(field)):
            blocked.append(f"{field} must be false or absent.")

    if asset_type not in ALLOWED_ASSET_TYPES:
        warnings.append(f"asset_type {asset_type or 'missing'} is not allowed; treating as other/manual review.")
        asset_type = asset_type or "other"
    if asset_type == "other":
        warnings.append("other asset type requires manual review before candidate intake.")

    if blocked:
        status = "MANUAL_WATCHLIST_ENTRY_BLOCKED_SAFE"
    elif warnings:
        status = "MANUAL_WATCHLIST_ENTRY_PARTIAL_SAFE"
    else:
        status = "MANUAL_WATCHLIST_ENTRY_READY_FOR_CANDIDATE_INTAKE"

    result = ManualCandidateWatchlistEntryResult(
        watchlist_entry_id=_text(raw.get("watchlist_entry_id")) or "unknown_watchlist_entry",
        candidate_id=_text(raw.get("candidate_id")) or "unknown_candidate",
        display_name=_text(raw.get("display_name")) or "unknown display name",
        asset_type=asset_type or "other",
        symbol_or_identifier=_text(raw.get("symbol_or_identifier")) or "unknown",
        issuer_or_provider=_text(raw.get("issuer_or_provider")),
        market_or_region=_text(raw.get("market_or_region")),
        currency=_text(raw.get("currency")),
        watchlist_reason=_text(raw.get("watchlist_reason")),
        watchlist_source_context=_text(raw.get("watchlist_source_context")),
        manually_entered_by_user=_bool(raw.get("manually_entered_by_user")),
        manual_entry_timestamp=_text(raw.get("manual_entry_timestamp")),
        intended_route=_text(raw.get("intended_route")),
        candidate_intake_required=_bool(raw.get("candidate_intake_required")),
        evidence_pipeline_required=_bool(raw.get("evidence_pipeline_required")),
        manual_review_required=_bool(raw.get("manual_review_required")),
        notes=_text(raw.get("notes")),
        entry_status=status,
        blocked_reasons=tuple(blocked),
        warnings=tuple(warnings),
        candidate_intake_preview_available=False,
        candidate_intake_preview=None,
    )
    if status == "MANUAL_WATCHLIST_ENTRY_READY_FOR_CANDIDATE_INTAKE":
        preview = preview_candidate_intake_record(result)
        return ManualCandidateWatchlistEntryResult(
            **{**result.__dict__, "candidate_intake_preview_available": True, "candidate_intake_preview": preview}
        )
    return result


def build_watchlist_entry_pack(data: dict[str, Any]) -> ManualCandidateWatchlistEntryPack:
    raw_entries = data.get("watchlist_entries", [])
    if not isinstance(raw_entries, list):
        raise ValueError("manual candidate watchlist data must contain watchlist_entries list")
    entries = tuple(validate_watchlist_entry(entry) for entry in raw_entries if isinstance(entry, dict))
    blocked_reasons = tuple(f"{entry.watchlist_entry_id}: {reason}" for entry in entries for reason in entry.blocked_reasons)
    warnings = tuple(f"{entry.watchlist_entry_id}: {warning}" for entry in entries for warning in entry.warnings)
    statuses = {entry.entry_status for entry in entries}
    if not entries or statuses == {"MANUAL_WATCHLIST_ENTRY_BLOCKED_SAFE"}:
        overall = "MANUAL_WATCHLIST_ENTRY_BLOCKED_SAFE"
    elif statuses == {"MANUAL_WATCHLIST_ENTRY_READY_FOR_CANDIDATE_INTAKE"}:
        overall = "MANUAL_WATCHLIST_ENTRY_READY_FOR_CANDIDATE_INTAKE"
    else:
        overall = "MANUAL_WATCHLIST_ENTRY_PARTIAL_SAFE"
    return ManualCandidateWatchlistEntryPack(
        title=_text(data.get("title")) or "J.A.R.V.I.S. Manual Candidate Watchlist Entry",
        version=_text(data.get("version")) or "v4.50",
        overall_status=overall,
        watchlist_entry_count=len(entries),
        entries=entries,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
    )


def load_watchlist_entry_pack(path: str | Path) -> ManualCandidateWatchlistEntryPack:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return build_watchlist_entry_pack(data)
