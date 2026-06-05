"""Human evidence collection pack generator for candidate review readiness."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .asset_registry import AssetRegistry, CandidateAsset, load_asset_registry
from .evidence_collection_checklist import (
    EvidenceChecklistItem,
    build_evidence_collection_checklist_from_files,
)


ETF_SOURCE_GUIDANCE = {
    "provider_factsheet": ("provider_factsheet",),
    "fund_metadata": ("provider_factsheet",),
    "fee_metadata": ("provider_factsheet",),
    "distribution_policy": ("provider_factsheet",),
    "exposure_data": ("provider_factsheet",),
    "platform_availability": ("platform_screenshot",),
    "tax_route": ("manual_research",),
    "market_data": ("provider_factsheet", "broker_export"),
}
CRYPTO_SOURCE_GUIDANCE = {
    "protocol_metadata": ("manual_research", "provider_factsheet"),
    "platform_availability": ("platform_screenshot",),
    "custody_route": ("platform_screenshot", "broker_export"),
    "tax_route": ("manual_research",),
    "crypto_risk_notes": ("manual_research",),
    "market_data": ("broker_export", "verified_api_snapshot"),
}
SOURCE_NAMES = {
    "provider_factsheet": ("Provider factsheet",),
    "fund_metadata": ("Provider factsheet",),
    "fee_metadata": ("Provider factsheet fee section",),
    "distribution_policy": ("Provider factsheet distribution section",),
    "platform_availability": ("Platform screenshot",),
    "tax_route": ("Manual tax route note",),
    "exposure_data": ("Provider factsheet holdings/exposure section",),
    "market_data": ("Broker export", "Provider factsheet"),
    "protocol_metadata": ("Protocol documentation", "Manual research note"),
    "custody_route": ("Platform screenshot", "Broker export"),
    "crypto_risk_notes": ("Manual crypto risk note", "Protocol documentation"),
}
REQUIRED_FIELDS = {
    "provider_factsheet": ("asset name", "provider", "isin_or_symbol", "as_of date"),
    "fund_metadata": ("provider", "index_tracked", "replication_method", "domicile"),
    "fee_metadata": ("ter_or_fee", "fee source date"),
    "distribution_policy": ("distribution_policy", "accumulating_or_distributing"),
    "platform_availability": ("platform", "ticker_or_symbol", "availability_status", "screenshot_date"),
    "tax_route": ("tax_route_summary", "jurisdiction_notes", "review_date"),
    "exposure_data": ("top holdings", "country exposure", "sector exposure", "as_of date"),
    "market_data": ("currency", "latest_price", "as_of date", "source"),
    "protocol_metadata": ("network_or_protocol", "token_symbol", "source_date"),
    "custody_route": ("custody_platform", "transferability", "account_route"),
    "crypto_risk_notes": ("volatility_notes", "custody_risk_notes", "tax_event_notes"),
}


@dataclass(frozen=True)
class EvidenceCollectionTask:
    task_id: str
    asset_id: str
    asset_name: str
    asset_type: str
    sleeve: str
    evidence_type: str
    priority: str
    suggested_source_quality_options: tuple[str, ...]
    suggested_source_names: tuple[str, ...]
    required_fields_to_verify: tuple[str, ...]
    acceptable_reference_types: tuple[str, ...]
    collection_instructions: str
    intake_record_template: dict[str, object]
    blocking_for_real_review: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "asset_id": self.asset_id,
            "asset_name": self.asset_name,
            "asset_type": self.asset_type,
            "sleeve": self.sleeve,
            "evidence_type": self.evidence_type,
            "priority": self.priority,
            "suggested_source_quality_options": list(self.suggested_source_quality_options),
            "suggested_source_names": list(self.suggested_source_names),
            "required_fields_to_verify": list(self.required_fields_to_verify),
            "acceptable_reference_types": list(self.acceptable_reference_types),
            "collection_instructions": self.collection_instructions,
            "intake_record_template": self.intake_record_template,
            "blocking_for_real_review": self.blocking_for_real_review,
        }


@dataclass(frozen=True)
class EvidenceCollectionPackSummary:
    total_candidates: int
    total_collection_tasks: int
    high_priority_tasks: int
    medium_priority_tasks: int
    low_priority_tasks: int
    tasks_by_asset: dict[str, int]
    tasks_by_evidence_type: dict[str, int]
    ready_without_collection_count: int


@dataclass(frozen=True)
class EvidenceCollectionPack:
    collection_pack_status: str
    tasks: tuple[EvidenceCollectionTask, ...]
    summary: EvidenceCollectionPackSummary
    approvals_created: bool = False
    registry_mutation_allowed: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _source_options(asset: CandidateAsset, evidence_type: str) -> tuple[str, ...]:
    if asset.asset_type == "ETF":
        return ETF_SOURCE_GUIDANCE.get(evidence_type, ("manual_research",))
    if asset.asset_type == "crypto":
        return CRYPTO_SOURCE_GUIDANCE.get(evidence_type, ("manual_research",))
    return ("manual_research",)


def _acceptable_reference_types(source_options: tuple[str, ...]) -> tuple[str, ...]:
    references = ["file_reference"]
    if "provider_factsheet" in source_options or "manual_research" in source_options or "verified_api_snapshot" in source_options:
        references.append("url_reference")
    return tuple(dict.fromkeys(references))


def _template_evidence_type(evidence_type: str) -> str:
    return "protocol_metadata" if evidence_type == "crypto_risk_notes" else evidence_type


def _priority(asset: CandidateAsset, item: EvidenceChecklistItem, blocking_count: int) -> str:
    if not item.blocking_for_real_review or asset.approval_status == "rejected":
        return "low"
    if asset.sleeve == "global_core":
        return "high"
    if blocking_count <= 2:
        return "high"
    return "medium"


def _make_task(asset: CandidateAsset, item: EvidenceChecklistItem, blocking_count: int) -> EvidenceCollectionTask:
    source_options = _source_options(asset, item.evidence_type)
    template_type = _template_evidence_type(item.evidence_type)
    task_id = f"collect_{asset.asset_id}_{item.evidence_type}"
    return EvidenceCollectionTask(
        task_id=task_id,
        asset_id=asset.asset_id,
        asset_name=asset.name,
        asset_type=asset.asset_type,
        sleeve=asset.sleeve,
        evidence_type=item.evidence_type,
        priority=_priority(asset, item, blocking_count),
        suggested_source_quality_options=source_options,
        suggested_source_names=SOURCE_NAMES.get(item.evidence_type, ("Manual research note",)),
        required_fields_to_verify=REQUIRED_FIELDS.get(item.evidence_type, ("asset_id", "as_of date", "source")),
        acceptable_reference_types=_acceptable_reference_types(source_options),
        collection_instructions=(
            f"Collect verified {item.evidence_type} evidence for {asset.name}. "
            "Record the evidence manually in verified_evidence_intake format. "
            "Do not approve the asset or create any trade action."
        ),
        intake_record_template={
            "evidence_id": f"<{task_id}_evidence_id>",
            "asset_id": asset.asset_id,
            "evidence_type": template_type,
            "source_quality": "<choose one suggested_source_quality_option>",
            "source_name": "<human-readable source name>",
            "as_of": "<YYYY-MM-DD>",
            "verified_by_user": "<true|false>",
            "verification_notes": "<required when verified_by_user is true>",
            "file_reference": "<optional local file reference>",
            "url_reference": "<optional URL reference>",
            "extracted_facts": {field: "<verify>" for field in REQUIRED_FIELDS.get(item.evidence_type, ())},
            "warnings": [],
        },
        blocking_for_real_review=item.blocking_for_real_review,
    )


def build_evidence_collection_pack(
    registry_path: str | Path,
    intake_path: str | Path,
) -> EvidenceCollectionPack:
    registry = load_asset_registry(registry_path)
    assets_by_id = registry.by_id()
    checklist_result = build_evidence_collection_checklist_from_files(registry_path, intake_path)
    tasks: list[EvidenceCollectionTask] = []
    for checklist in checklist_result.checklists:
        asset = assets_by_id[checklist.asset_id]
        blocking_items = tuple(item for item in checklist.items if item.blocking_for_real_review)
        for item in blocking_items:
            tasks.append(_make_task(asset, item, len(blocking_items)))

    tasks_by_asset: dict[str, int] = {}
    tasks_by_evidence_type: dict[str, int] = {}
    for task in tasks:
        tasks_by_asset[task.asset_id] = tasks_by_asset.get(task.asset_id, 0) + 1
        tasks_by_evidence_type[task.evidence_type] = tasks_by_evidence_type.get(task.evidence_type, 0) + 1

    summary = EvidenceCollectionPackSummary(
        total_candidates=len(registry.assets),
        total_collection_tasks=len(tasks),
        high_priority_tasks=sum(task.priority == "high" for task in tasks),
        medium_priority_tasks=sum(task.priority == "medium" for task in tasks),
        low_priority_tasks=sum(task.priority == "low" for task in tasks),
        tasks_by_asset=dict(sorted(tasks_by_asset.items())),
        tasks_by_evidence_type=dict(sorted(tasks_by_evidence_type.items())),
        ready_without_collection_count=sum(checklist.collection_complete for checklist in checklist_result.checklists),
    )
    return EvidenceCollectionPack(
        collection_pack_status="TASKS_READY" if tasks else "NO_TASKS",
        tasks=tuple(tasks),
        summary=summary,
        approvals_created=False,
        registry_mutation_allowed=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )
