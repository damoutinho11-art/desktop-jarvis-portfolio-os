"""Route public-source draft evidence into specific verification categories."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from .asset_registry import AssetRegistry, CandidateAsset, load_asset_registry
from .evidence_verification_queue import EvidenceVerificationTask
from .public_source_fetcher import PublicSourceFetchResult, run_public_source_fetcher


ETF_ROUTE_FACTS = {
    "fund_metadata": ("fund_name", "isin", "provider", "benchmark", "domicile", "replication_method"),
    "fee_metadata": ("ter_or_fee",),
    "distribution_policy": ("distribution_policy",),
    "platform_availability": ("platform_name", "availability_status"),
    "market_data": ("ticker", "price_currency", "market_price", "price_source", "as_of_market_date"),
    "exposure_data": ("holdings_source", "country_exposure_source", "sector_exposure_source"),
    "tax_route": ("tax_route_summary", "tax_wrapper"),
}
CRYPTO_ROUTE_FACTS = {
    "protocol_metadata": ("fund_name", "provider", "ticker"),
    "market_data": ("ticker", "price_currency", "market_price", "price_source", "as_of_market_date"),
    "platform_availability": ("platform_name", "availability_status"),
    "custody_route": (),
    "tax_route": ("tax_route_summary", "tax_wrapper"),
    "crypto_risk_notes": (),
}
MARKET_SOURCE_TYPES = {"public_market_data_page", "public_crypto_market_api"}
REFERENCE_DATE = "2026-06-05"


@dataclass(frozen=True)
class PublicDraftEvidenceRouteResult:
    asset_id: str
    source_id: str
    source_evidence_type: str
    routed_evidence_records: tuple[dict[str, object], ...]
    missing_routes: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class PublicDraftEvidenceRouterSummary:
    total_public_source_results: int
    routed_draft_records_count: int
    routed_records_by_asset: dict[str, int]
    routed_records_by_evidence_type: dict[str, int]
    missing_routes_count: int
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class PublicDraftEvidenceRouterPack:
    router_status: str
    route_results: tuple[PublicDraftEvidenceRouteResult, ...]
    summary: PublicDraftEvidenceRouterSummary
    approvals_created: bool = False
    registry_mutation_allowed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _supported_facts(facts: dict[str, object], keys: tuple[str, ...]) -> dict[str, object]:
    return {key: facts[key] for key in keys if key in facts}


def _route_map(asset: CandidateAsset) -> dict[str, tuple[str, ...]]:
    return CRYPTO_ROUTE_FACTS if asset.asset_type == "crypto" else ETF_ROUTE_FACTS


def _evidence_id(source_id: str, evidence_type: str) -> str:
    return f"routed_public_{source_id}_{evidence_type}"


def _routed_record(
    result: PublicSourceFetchResult,
    evidence_type: str,
    facts: dict[str, object],
) -> dict[str, object]:
    source_record = result.draft_evidence_record or {}
    return {
        "evidence_id": _evidence_id(result.source_id, evidence_type),
        "asset_id": result.asset_id,
        "evidence_type": evidence_type,
        "source_quality": source_record.get("source_quality", "manual_research"),
        "source_name": source_record.get("source_name", result.source_id),
        "as_of": source_record.get("as_of", REFERENCE_DATE),
        "verified_by_user": False,
        "verification_notes": "Routed public draft evidence. User verification required.",
        "url_reference": source_record.get("url_reference"),
        "extracted_facts": facts,
        "warnings": list(result.warnings),
    }


def route_public_source_result(
    result: PublicSourceFetchResult,
    asset: CandidateAsset | None,
) -> PublicDraftEvidenceRouteResult:
    warnings = list(result.warnings)
    blockers = list(result.blockers)
    if result.draft_evidence_record is None:
        return PublicDraftEvidenceRouteResult(
            asset_id=result.asset_id,
            source_id=result.source_id,
            source_evidence_type="unknown",
            routed_evidence_records=(),
            missing_routes=(),
            warnings=tuple(warnings),
            blockers=tuple(blockers or (f"{result.source_id}: no draft evidence record to route.",)),
        )
    if asset is None:
        return PublicDraftEvidenceRouteResult(
            asset_id=result.asset_id,
            source_id=result.source_id,
            source_evidence_type=str(result.draft_evidence_record.get("evidence_type", "unknown")),
            routed_evidence_records=(),
            missing_routes=(),
            warnings=tuple(warnings),
            blockers=tuple(blockers or (f"{result.source_id}: unknown asset_id {result.asset_id}.",)),
        )

    records: list[dict[str, object]] = []
    missing: list[str] = []
    source_type = str(result.draft_evidence_record.get("source_type", ""))
    # public_source_fetcher draft records intentionally do not persist source_type, so infer from source quality
    source_name = str(result.draft_evidence_record.get("source_name", ""))
    for evidence_type, required_keys in _route_map(asset).items():
        if evidence_type == "market_data":
            is_market_source = result.draft_evidence_record.get("source_quality") == "verified_api_snapshot" or "market" in source_name.lower()
            if not is_market_source:
                missing.append(f"{result.source_id}: missing route for {evidence_type}; source is not a public market source.")
                continue
        facts = _supported_facts(result.extracted_facts, required_keys)
        if not facts:
            missing.append(f"{result.source_id}: missing route for {evidence_type}; insufficient extracted facts.")
            continue
        records.append(_routed_record(result, evidence_type, facts))

    return PublicDraftEvidenceRouteResult(
        asset_id=result.asset_id,
        source_id=result.source_id,
        source_evidence_type=str(result.draft_evidence_record.get("evidence_type", "unknown")),
        routed_evidence_records=tuple(records),
        missing_routes=tuple(missing),
        warnings=tuple(dict.fromkeys((*warnings, *missing))),
        blockers=tuple(blockers),
    )


def build_public_draft_evidence_router_pack(
    registry_path: str | Path | AssetRegistry,
    public_sources_path: str | Path,
) -> PublicDraftEvidenceRouterPack:
    registry = load_asset_registry(registry_path) if not isinstance(registry_path, AssetRegistry) else registry_path
    assets_by_id = registry.by_id()
    public_run = run_public_source_fetcher(registry, public_sources_path)
    route_results = tuple(route_public_source_result(result, assets_by_id.get(result.asset_id)) for result in public_run.results)
    by_asset: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for route in route_results:
        for record in route.routed_evidence_records:
            asset_id = str(record["asset_id"])
            evidence_type = str(record["evidence_type"])
            by_asset[asset_id] = by_asset.get(asset_id, 0) + 1
            by_type[evidence_type] = by_type.get(evidence_type, 0) + 1
    warnings = tuple(dict.fromkeys(warning for route in route_results for warning in route.warnings))
    blockers = tuple(dict.fromkeys(blocker for route in route_results for blocker in route.blockers))
    routed_count = sum(len(route.routed_evidence_records) for route in route_results)
    missing_count = sum(len(route.missing_routes) for route in route_results)
    summary = PublicDraftEvidenceRouterSummary(
        total_public_source_results=len(public_run.results),
        routed_draft_records_count=routed_count,
        routed_records_by_asset=dict(sorted(by_asset.items())),
        routed_records_by_evidence_type=dict(sorted(by_type.items())),
        missing_routes_count=missing_count,
        warnings=warnings,
        blockers=blockers,
    )
    status = "BLOCKED" if blockers and not routed_count else "WARNING" if warnings else "ROUTED_DRAFTS_CREATED"
    return PublicDraftEvidenceRouterPack(
        router_status=status,
        route_results=route_results,
        summary=summary,
        approvals_created=False,
        registry_mutation_allowed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def _questions(record: dict[str, object]) -> tuple[str, ...]:
    evidence_type = str(record.get("evidence_type", "evidence"))
    return (
        f"Does this routed public source support the {evidence_type} evidence for {record.get('asset_id')}?",
        "Do the routed facts match the public source exactly?",
        "Is the source acceptable for manual evidence intake?",
    )


def routed_records_to_verification_tasks(records: tuple[dict[str, object], ...] | list[dict[str, object]]) -> tuple[EvidenceVerificationTask, ...]:
    tasks: list[EvidenceVerificationTask] = []
    for record in records:
        evidence_id = str(record["evidence_id"])
        tasks.append(
            EvidenceVerificationTask(
                task_id=f"verify_{evidence_id}",
                evidence_id=evidence_id,
                asset_id=str(record["asset_id"]),
                evidence_type=str(record["evidence_type"]),
                source_name=str(record["source_name"]),
                source_quality=str(record["source_quality"]),
                extracted_facts=dict(record.get("extracted_facts", {})),
                url_reference=record.get("url_reference") if isinstance(record.get("url_reference"), str) else None,
                file_reference=record.get("file_reference") if isinstance(record.get("file_reference"), str) else None,
                verification_status="pending_user_verification",
                verification_questions=_questions(record),
                warnings=tuple(str(warning) for warning in record.get("warnings", [])),
                blockers=(),
                draft_evidence_record=record,
            )
        )
    return tuple(tasks)


def write_routed_draft_records(pack: PublicDraftEvidenceRouterPack, path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    records = [record for route in pack.route_results for record in route.routed_evidence_records]
    target.write_text(json.dumps({"records": records}, indent=2, sort_keys=True), encoding="utf-8")
    return target
