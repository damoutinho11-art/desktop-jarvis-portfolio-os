"""Expand global core evidence tasks into disabled public source templates.

This is a read-only preparation layer. It does not fetch network data, verify
evidence, approve assets, mutate registries, recommend allocations, or create
buy/sell requests.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .global_core_evidence_batch import EvidenceCollectionTask, build_global_core_evidence_batch_from_files


ALLOWED_SOURCE_TYPES = {
    "provider_product_page",
    "provider_factsheet_pdf",
    "provider_kiid_pdf",
    "public_platform_page",
    "public_market_data_page",
    "manual_url_reference",
    "local_source_fixture",
}
DEFAULT_URL_PLACEHOLDER = {
    "fund_metadata": "<provider_product_page_url_to_collect>",
    "fee_metadata": "<provider_factsheet_or_kiid_url_to_collect>",
    "distribution_policy": "<provider_product_or_factsheet_url_to_collect>",
    "platform_availability": "<account_specific_lightyear_screenshot_or_note_to_collect>",
    "tax_route": "<manual_tax_account_route_note_to_collect>",
    "exposure_data": "<provider_holdings_country_sector_url_to_collect>",
    "market_data": "<public_market_data_page_url_to_collect>",
}


@dataclass(frozen=True)
class GlobalCoreSourceTemplateExpanderConfig:
    candidate_source_guidance: dict[str, dict[str, dict[str, str]]]


@dataclass(frozen=True)
class GlobalCoreSourceTemplate:
    source_id: str
    asset_id: str
    evidence_type: str
    source_type: str
    source_name: str
    url_reference: str
    enabled: bool
    allow_network_fetch: bool
    local_fixture_content: str
    source_guidance: str
    fields_to_verify: tuple[str, ...]
    manual_verification_required: bool
    auto_verified: bool

    def to_dict(self) -> dict[str, object]:
        return {
            "source_id": self.source_id,
            "asset_id": self.asset_id,
            "evidence_type": self.evidence_type,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "url_reference": self.url_reference,
            "enabled": self.enabled,
            "allow_network_fetch": self.allow_network_fetch,
            "local_fixture_content": self.local_fixture_content,
            "source_guidance": self.source_guidance,
            "fields_to_verify": list(self.fields_to_verify),
            "manual_verification_required": self.manual_verification_required,
            "auto_verified": self.auto_verified,
        }


@dataclass(frozen=True)
class GlobalCoreSourceTemplateExpansion:
    expansion_status: str
    target_candidates: tuple[str, ...]
    already_reviewed_skipped: tuple[str, ...]
    templates: tuple[GlobalCoreSourceTemplate, ...]
    templates_by_candidate: dict[str, int]
    templates_by_evidence_type: dict[str, int]
    disabled_templates_count: int
    network_fetch_enabled_count: int
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    approvals_created: bool = False
    registry_mutation_performed: bool = False
    allocation_recommendation_created: bool = False
    buy_sell_requests_created: bool = False
    trades_executed: bool = False


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object.")
    return value


def _require_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be non-empty text.")
    return value.strip()


def load_global_core_source_template_expander_config(path: str | Path) -> GlobalCoreSourceTemplateExpanderConfig:
    raw = _require_mapping(json.loads(Path(path).read_text(encoding="utf-8")), "global core source template expander config")
    guidance = _require_mapping(raw.get("candidate_source_guidance", {}), "candidate_source_guidance")
    parsed: dict[str, dict[str, dict[str, str]]] = {}
    for asset_id, by_type_raw in guidance.items():
        by_type = _require_mapping(by_type_raw, f"candidate_source_guidance.{asset_id}")
        parsed[str(asset_id)] = {}
        for evidence_type, item_raw in by_type.items():
            item = _require_mapping(item_raw, f"candidate_source_guidance.{asset_id}.{evidence_type}")
            source_type = _require_text(item.get("source_type"), "source_type")
            if source_type not in ALLOWED_SOURCE_TYPES:
                raise ValueError(f"{asset_id}:{evidence_type} has unsupported source_type {source_type}.")
            parsed[str(asset_id)][str(evidence_type)] = {
                "source_type": source_type,
                "source_name": _require_text(item.get("source_name"), "source_name"),
                "url_reference": _require_text(item.get("url_reference"), "url_reference"),
                "source_guidance": _require_text(item.get("source_guidance"), "source_guidance"),
            }
    return GlobalCoreSourceTemplateExpanderConfig(candidate_source_guidance=parsed)


def _slug(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "_" for ch in value).strip("_")


def _config_for_task(
    task: EvidenceCollectionTask,
    config: GlobalCoreSourceTemplateExpanderConfig,
) -> dict[str, str]:
    item = config.candidate_source_guidance.get(task.asset_id, {}).get(task.evidence_type)
    if item:
        return item
    return {
        "source_type": task.suggested_source_type,
        "source_name": f"{task.asset_id} {task.evidence_type} source template",
        "url_reference": DEFAULT_URL_PLACEHOLDER[task.evidence_type],
        "source_guidance": task.source_guidance,
    }


def _validate_template(template: GlobalCoreSourceTemplate) -> tuple[str, ...]:
    blockers: list[str] = []
    if template.enabled:
        blockers.append(f"{template.source_id}: template must be disabled.")
    if template.allow_network_fetch:
        blockers.append(f"{template.source_id}: allow_network_fetch must be false.")
    if template.auto_verified:
        blockers.append(f"{template.source_id}: auto_verified must be false.")
    if not template.manual_verification_required:
        blockers.append(f"{template.source_id}: manual_verification_required must be true.")
    if not template.url_reference.strip():
        blockers.append(f"{template.source_id}: url_reference must be non-empty.")
    if template.source_type not in ALLOWED_SOURCE_TYPES:
        blockers.append(f"{template.source_id}: unsupported source_type {template.source_type}.")
    guidance = template.source_guidance.lower()
    fields = {field.lower() for field in template.fields_to_verify}
    if template.evidence_type == "platform_availability" and "account-specific" not in guidance:
        blockers.append(f"{template.source_id}: platform availability must require account-specific evidence.")
    if template.evidence_type == "tax_route" and "manual" not in guidance:
        blockers.append(f"{template.source_id}: tax route must require manual review.")
    if template.evidence_type == "market_data" and not {"price", "currency", "source"}.issubset(fields):
        blockers.append(f"{template.source_id}: market data must include price, currency, and source fields.")
    if template.evidence_type == "market_data" and not any(field in fields for field in ("as_of_date", "market_date")):
        blockers.append(f"{template.source_id}: market data must include an as_of date or market date field.")
    return tuple(blockers)


def build_global_core_source_template_expansion(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    config: GlobalCoreSourceTemplateExpanderConfig,
) -> GlobalCoreSourceTemplateExpansion:
    batch = build_global_core_evidence_batch_from_files(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
    )
    templates: list[GlobalCoreSourceTemplate] = []
    blockers: list[str] = [*batch.blockers]
    warnings: list[str] = [*batch.warnings]
    for task in batch.tasks:
        source = _config_for_task(task, config)
        template = GlobalCoreSourceTemplate(
            source_id=f"template_{_slug(task.asset_id)}_{_slug(task.evidence_type)}",
            asset_id=task.asset_id,
            evidence_type=task.evidence_type,
            source_type=source["source_type"],
            source_name=source["source_name"],
            url_reference=source["url_reference"],
            enabled=False,
            allow_network_fetch=False,
            local_fixture_content="",
            source_guidance=source["source_guidance"],
            fields_to_verify=task.fields_to_verify,
            manual_verification_required=True,
            auto_verified=False,
        )
        templates.append(template)
        blockers.extend(_validate_template(template))

    by_candidate: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for template in templates:
        by_candidate[template.asset_id] = by_candidate.get(template.asset_id, 0) + 1
        by_type[template.evidence_type] = by_type.get(template.evidence_type, 0) + 1
    return GlobalCoreSourceTemplateExpansion(
        expansion_status="READY" if templates and not blockers else "BLOCKED" if blockers else "NO_TEMPLATES",
        target_candidates=batch.target_candidates,
        already_reviewed_skipped=batch.already_reviewed_skipped,
        templates=tuple(templates),
        templates_by_candidate=dict(sorted(by_candidate.items())),
        templates_by_evidence_type=dict(sorted(by_type.items())),
        disabled_templates_count=sum(not template.enabled for template in templates),
        network_fetch_enabled_count=sum(template.allow_network_fetch for template in templates),
        warnings=tuple(dict.fromkeys(warnings)),
        blockers=tuple(dict.fromkeys(blockers)),
        approvals_created=False,
        registry_mutation_performed=False,
        allocation_recommendation_created=False,
        buy_sell_requests_created=False,
        trades_executed=False,
    )


def build_global_core_source_template_expansion_from_files(
    source_registry_path: str | Path,
    reviewed_registry_copy_path: str | Path | None,
    queue_config_path: str | Path,
    batch_config_path: str | Path,
    expander_config_path: str | Path,
) -> GlobalCoreSourceTemplateExpansion:
    return build_global_core_source_template_expansion(
        source_registry_path,
        reviewed_registry_copy_path,
        queue_config_path,
        batch_config_path,
        load_global_core_source_template_expander_config(expander_config_path),
    )
