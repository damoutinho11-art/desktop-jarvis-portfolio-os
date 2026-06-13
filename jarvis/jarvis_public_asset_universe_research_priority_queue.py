"""Public asset universe research priority queue.

v4.68 builds a research-workflow queue from classified public asset records. It
is not investment ranking, screening, research scoring, recommendation,
approval, allocation, trading, registry mutation, or execution.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE"
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/public_asset_universe/research_queue")
ALLOWED_PRIORITY_BUCKETS = {
    "RESEARCH_QUEUE_HIGH_READY",
    "RESEARCH_QUEUE_MEDIUM_READY",
    "RESEARCH_QUEUE_LOW_READY",
    "RESEARCH_QUEUE_NEEDS_MORE_PUBLIC_DATA",
    "RESEARCH_QUEUE_NEEDS_MANUAL_SOURCE_REVIEW",
    "RESEARCH_QUEUE_BLOCKED_SAFE",
}
ALLOWED_NEXT_STEPS = {
    "draft_public_evidence_pack",
    "collect_more_public_identifiers",
    "rerun_source_refresh",
    "manual_source_review",
    "fix_classification_inputs",
    "do_not_research_until_safe",
}
VALID_NEXT_MANUAL_ACTIONS = {
    "review_research_priority_queue",
    "proceed_to_public_evidence_pack_draft_generator",
    "fix_classified_records",
    "rerun_classifier",
    "no_manual_asset_entry_required",
}
BLOCKED_NEXT_MANUAL_ACTIONS = {
    "evidence_verification",
    "approval",
    "registry_mutation",
    "allocation_recommendation",
    "trade_execution",
    "executor_creation",
}
FALSE_REQUIRED_SAFETY_FIELDS = (
    "network_calls",
    "fetching",
    "downloading",
    "scraping",
    "api_calls",
    "writes_without_explicit_authorization",
    "cache_mutation_without_explicit_authorization",
    "subprocess_execution",
    "scheduler_creation",
    "browser_automation",
    "broker_integration",
    "lightyear_integration",
    "lhv_integration",
    "crypto_exchange_integration",
    "credentials_used",
    "private_file_ingested",
    "automatic_private_data_ingest",
    "account_data_ingested",
    "source_parsing_as_evidence",
    "evidence_extraction",
    "evidence_verification",
    "verified_evidence_promotion",
    "investment_screening",
    "research_scoring",
    "ranking_by_investment_merit",
    "recommendation",
    "registry_mutation",
    "registry_file_written",
    "candidate_registry_write",
    "candidate_intake_file_written",
    "approved_asset",
    "trusted_asset",
    "investable",
    "allocation_recommendation",
    "portfolio_weight",
    "buy_signal",
    "sell_signal",
    "trade_executed",
    "executor_created",
)
TRUE_REQUIRED_SAFETY_FIELDS = (
    "public_data_only",
    "manual_trust_required",
    "manual_approval_required",
    "no_execution_invariant",
    "final_purchase_external_manual_only",
    "local_cache_only",
    "queue_data_unverified",
    "research_workflow_priority_only",
)


@dataclass(frozen=True)
class PublicAssetUniverseResearchPriorityQueueResult:
    title: str
    version: str
    status: str
    queue_mode: str
    classified_record_count: int
    queue_item_count: int
    high_ready_count: int
    medium_ready_count: int
    low_ready_count: int
    needs_more_public_data_count: int
    needs_manual_source_review_count: int
    blocked_safe_count: int
    skipped_record_count: int
    blocked_record_count: int
    duplicate_asset_id_count: int
    queue_items: tuple[dict[str, Any], ...]
    skipped_records: tuple[str, ...]
    blocked_records: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    next_safe_action: str
    no_network_called: bool = True
    no_fetch_executed: bool = True
    no_cache_mutated: bool = True
    no_evidence_extraction: bool = True
    no_evidence_verification: bool = True
    no_investment_screening: bool = True
    no_research_scoring: bool = True
    no_recommendation: bool = True
    no_approval: bool = True
    no_allocation: bool = True
    no_trade: bool = True
    no_executor: bool = True
    local_cache_only: bool = True
    queue_data_unverified: bool = True


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip()) if value is not None else ""


def _bool(value: Any) -> bool:
    return value is True


def _authorization_valid(config: dict[str, Any]) -> bool:
    policy = config.get("authorization_policy", {})
    if not isinstance(policy, dict):
        return False
    return (
        policy.get("explicit_authorization_required") is True
        and policy.get("required_authorization_phrase") == REQUIRED_AUTHORIZATION_PHRASE
        and policy.get("authorization_phrase") == REQUIRED_AUTHORIZATION_PHRASE
        and policy.get("authorization_phrase_valid") is True
        and policy.get("default_write_allowed") is False
        and policy.get("write_allowed_only_with_explicit_authorization") is True
    )


def validate_queue_config(config: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in (
        "report_only",
        "default_no_write",
        "read_only_by_default",
        "local_cache_only",
        "no_network",
        "no_fetching",
        "no_downloading",
        "no_scraping",
        "no_api_calls",
        "no_browser_automation",
        "no_subprocess",
        "no_scheduler_creation",
        "no_broker_integration",
        "no_private_data_ingest",
    ):
        if config.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in ("classified_input_policy", "queue_output_policy", "authorization_policy", "queue_schema", "priority_rules"):
        if not isinstance(config.get(field), dict):
            blocked.append(f"{field} must be an object.")
    safety = config.get("safety_controls", {})
    if not isinstance(safety, dict):
        blocked.append("safety_controls must be an object.")
        safety = {}
    for field in FALSE_REQUIRED_SAFETY_FIELDS:
        if _bool(safety.get(field)):
            blocked.append(f"safety_controls.{field} must be false.")
    for field in TRUE_REQUIRED_SAFETY_FIELDS:
        if safety.get(field) is not True:
            blocked.append(f"safety_controls.{field} must be true.")
    action = normalize_text(config.get("next_manual_action"))
    if action not in VALID_NEXT_MANUAL_ACTIONS:
        blocked.append("next_manual_action must be valid.")
    if action in BLOCKED_NEXT_MANUAL_ACTIONS:
        blocked.append(f"next_manual_action must not be {action}.")
    policy = config.get("authorization_policy", {})
    if isinstance(policy, dict):
        expected = {
            "explicit_authorization_required": True,
            "default_write_allowed": False,
            "write_allowed_only_with_explicit_authorization": True,
            "local_cache_only": True,
            "queue_data_unverified": True,
            "no_evidence_verification": True,
            "no_approval": True,
            "no_allocation": True,
            "no_trade": True,
            "no_executor": True,
        }
        for field, value in expected.items():
            if policy.get(field) is not value:
                blocked.append(f"authorization_policy.{field} must be {str(value).lower()}.")
        if policy.get("required_authorization_phrase") != REQUIRED_AUTHORIZATION_PHRASE:
            blocked.append("authorization_policy.required_authorization_phrase must match.")
    if not isinstance(config.get("classified_records", []), list):
        blocked.append("classified_records must be a list.")
    return tuple(dict.fromkeys(blocked))


def validate_classified_record_for_queue(record: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    required = (
        "asset_id",
        "display_name",
        "asset_type",
        "symbol_or_identifier",
        "source_id",
        "asset_class",
        "instrument_type",
        "region_bucket",
        "currency_bucket",
        "evidence_readiness_bucket",
        "data_completeness_bucket",
        "freshness_bucket",
        "classification_confidence_label",
        "missing_classification_fields",
    )
    for field in required:
        if field not in record:
            blocked.append(f"{field} is required.")
    expected = {
        "evidence_status": "UNVERIFIED_PUBLIC_DATA",
        "approval_status": "NOT_APPROVED",
        "investability_status": "NOT_INVESTABLE",
        "execution_status": "NO_EXECUTION",
        "screening_status": "NOT_SCREENED",
        "research_score_status": "NOT_SCORED",
        "recommendation_status": "NO_RECOMMENDATION",
        "classification_status": "CLASSIFIED_PUBLIC_DATA_ONLY",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            blocked.append(f"{field} must be {value}.")
    for field in ("manual_review_required", "manual_approval_required"):
        if record.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in ("approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "candidate_registry_write", "executor_created"):
        if record.get(field) is True:
            blocked.append(f"{field} must not be true.")
    if record.get("portfolio_weight") not in {None, False, 0, 0.0}:
        blocked.append("portfolio_weight must not be nonzero.")
    return tuple(blocked)


def build_queue_id(record: dict[str, Any]) -> str:
    asset_id = normalize_text(record.get("asset_id")) or "unknown"
    return f"research_queue::{asset_id}"


def classify_research_priority_bucket(record: dict[str, Any]) -> str:
    readiness = record.get("evidence_readiness_bucket")
    completeness = record.get("data_completeness_bucket")
    freshness = record.get("freshness_bucket")
    confidence = record.get("classification_confidence_label")
    if readiness == "BLOCKED_BY_MISSING_FIELDS" or completeness == "MISSING_CORE_FIELDS":
        return "RESEARCH_QUEUE_BLOCKED_SAFE"
    if readiness == "NEEDS_MORE_PUBLIC_DATA":
        return "RESEARCH_QUEUE_NEEDS_MORE_PUBLIC_DATA"
    if readiness == "NEEDS_MANUAL_SOURCE_REVIEW" or freshness in {"STALE_PUBLIC_DATA", "UNKNOWN_FRESHNESS"}:
        return "RESEARCH_QUEUE_NEEDS_MANUAL_SOURCE_REVIEW"
    if readiness == "READY_FOR_RESEARCH_QUEUE" and completeness == "COMPLETE_CORE_FIELDS" and freshness == "FRESH_PUBLIC_DATA" and confidence == "HIGH_STRUCTURAL_CONFIDENCE":
        return "RESEARCH_QUEUE_HIGH_READY"
    if readiness == "READY_FOR_RESEARCH_QUEUE" and completeness in {"COMPLETE_CORE_FIELDS", "PARTIAL_CORE_FIELDS"} and freshness in {"FRESH_PUBLIC_DATA", "MANUAL_REVIEW_PUBLIC_DATA"} and confidence in {"MEDIUM_STRUCTURAL_CONFIDENCE", "HIGH_STRUCTURAL_CONFIDENCE"}:
        return "RESEARCH_QUEUE_MEDIUM_READY"
    if readiness == "READY_FOR_RESEARCH_QUEUE":
        return "RESEARCH_QUEUE_LOW_READY"
    return "RESEARCH_QUEUE_BLOCKED_SAFE"


def suggest_next_research_step(record: dict[str, Any], priority_bucket: str) -> str:
    if priority_bucket in {"RESEARCH_QUEUE_HIGH_READY", "RESEARCH_QUEUE_MEDIUM_READY", "RESEARCH_QUEUE_LOW_READY"}:
        return "draft_public_evidence_pack"
    if priority_bucket == "RESEARCH_QUEUE_NEEDS_MORE_PUBLIC_DATA":
        return "collect_more_public_identifiers"
    if priority_bucket == "RESEARCH_QUEUE_NEEDS_MANUAL_SOURCE_REVIEW":
        freshness = record.get("freshness_bucket")
        return "rerun_source_refresh" if freshness in {"STALE_PUBLIC_DATA", "UNKNOWN_FRESHNESS"} else "manual_source_review"
    if priority_bucket == "RESEARCH_QUEUE_BLOCKED_SAFE":
        return "fix_classification_inputs"
    return "do_not_research_until_safe"


def build_research_priority_reason(record: dict[str, Any], priority_bucket: str) -> str:
    return (
        f"Workflow bucket {priority_bucket} from evidence_readiness={record.get('evidence_readiness_bucket')}, "
        f"completeness={record.get('data_completeness_bucket')}, freshness={record.get('freshness_bucket')}, "
        f"confidence={record.get('classification_confidence_label')}. This is workflow readiness only, not investment merit."
    )


def build_queue_item(record: dict[str, Any], current_date: Any) -> dict[str, Any]:
    bucket = classify_research_priority_bucket(record)
    next_step = suggest_next_research_step(record, bucket)
    return {
        "queue_id": build_queue_id(record),
        "asset_id": record.get("asset_id"),
        "display_name": record.get("display_name"),
        "asset_type": record.get("asset_type"),
        "symbol_or_identifier": record.get("symbol_or_identifier"),
        "source_id": record.get("source_id"),
        "asset_class": record.get("asset_class"),
        "instrument_type": record.get("instrument_type"),
        "region_bucket": record.get("region_bucket"),
        "currency_bucket": record.get("currency_bucket"),
        "evidence_readiness_bucket": record.get("evidence_readiness_bucket"),
        "data_completeness_bucket": record.get("data_completeness_bucket"),
        "freshness_bucket": record.get("freshness_bucket"),
        "classification_confidence_label": record.get("classification_confidence_label"),
        "missing_classification_fields": tuple(record.get("missing_classification_fields", ())),
        "research_priority_bucket": bucket,
        "research_priority_reason": build_research_priority_reason(record, bucket),
        "suggested_next_research_step": next_step,
        "required_manual_review": bucket in {"RESEARCH_QUEUE_NEEDS_MANUAL_SOURCE_REVIEW", "RESEARCH_QUEUE_BLOCKED_SAFE"},
        "evidence_pack_status": "NOT_GENERATED",
        "evidence_status": "UNVERIFIED_PUBLIC_DATA",
        "approval_status": "NOT_APPROVED",
        "investability_status": "NOT_INVESTABLE",
        "execution_status": "NO_EXECUTION",
        "recommendation_status": "NO_RECOMMENDATION",
        "allocation_status": "NO_ALLOCATION",
        "trade_status": "NO_TRADE",
        "queue_created_at": normalize_text(current_date),
        "safety_notes": (
            "Research workflow priority only.",
            "Not investment ranking, recommendation, approval, allocation, trading, or execution.",
        ),
    }


def validate_queue_item(item: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    required = (
        "queue_id",
        "asset_id",
        "research_priority_bucket",
        "suggested_next_research_step",
        "research_priority_reason",
        "queue_created_at",
    )
    for field in required:
        if not normalize_text(item.get(field)):
            blocked.append(f"{field} is required.")
    if item.get("research_priority_bucket") not in ALLOWED_PRIORITY_BUCKETS:
        blocked.append("research_priority_bucket is not allowed.")
    if item.get("suggested_next_research_step") not in ALLOWED_NEXT_STEPS:
        blocked.append("suggested_next_research_step is not allowed.")
    expected = {
        "evidence_pack_status": "NOT_GENERATED",
        "evidence_status": "UNVERIFIED_PUBLIC_DATA",
        "approval_status": "NOT_APPROVED",
        "investability_status": "NOT_INVESTABLE",
        "execution_status": "NO_EXECUTION",
        "recommendation_status": "NO_RECOMMENDATION",
        "allocation_status": "NO_ALLOCATION",
        "trade_status": "NO_TRADE",
    }
    for field, value in expected.items():
        if item.get(field) != value:
            blocked.append(f"{field} must be {value}.")
    return tuple(blocked)


def build_research_priority_queue(config: dict[str, Any]) -> tuple[tuple[dict[str, Any], ...], tuple[str, ...], tuple[str, ...]]:
    items: list[dict[str, Any]] = []
    skipped: list[str] = []
    blocked: list[str] = []
    for record in config.get("classified_records", []):
        if not isinstance(record, dict):
            blocked.append("classified record must be an object")
            continue
        asset_id = normalize_text(record.get("asset_id")) or "unknown"
        reasons = validate_classified_record_for_queue(record)
        if reasons:
            blocked.append(f"{asset_id}: {'; '.join(reasons)}")
            continue
        item = build_queue_item(record, config.get("current_date"))
        item_reasons = validate_queue_item(item)
        if item_reasons:
            blocked.append(f"{asset_id}: {'; '.join(item_reasons)}")
            continue
        items.append(item)
    return tuple(sorted(items, key=lambda item: (item["research_priority_bucket"], item["asset_id"]))), tuple(skipped), tuple(blocked)


def evaluate_public_asset_universe_research_priority_queue(config: dict[str, Any]) -> PublicAssetUniverseResearchPriorityQueueResult:
    config_blockers = list(validate_queue_config(config))
    if isinstance(config.get("classified_records"), list) and not config.get("classified_records"):
        config_blockers.append("classified_records must contain at least one record.")
    queue_items, skipped_records, blocked_records = build_research_priority_queue(config)
    ids = [item["asset_id"] for item in queue_items]
    duplicate_count = len(ids) - len(set(ids))
    record_blockers = ["duplicate asset_id detected."] if duplicate_count else []
    blockers = tuple(dict.fromkeys(config_blockers + list(blocked_records) + record_blockers))
    authorized = _authorization_valid(config)
    if config_blockers or (blockers and not queue_items):
        status = "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_BLOCKED_SAFE"
    elif blockers or skipped_records:
        status = "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_PARTIAL_SAFE"
    elif authorized:
        status = "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_READY_TO_WRITE_SAFE"
    else:
        status = "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_READY_SAFE"
    counts = {bucket: 0 for bucket in ALLOWED_PRIORITY_BUCKETS}
    for item in queue_items:
        counts[item["research_priority_bucket"]] += 1
    return PublicAssetUniverseResearchPriorityQueueResult(
        title=normalize_text(config.get("title")) or "J.A.R.V.I.S. Public Asset Universe Research Priority Queue",
        version=normalize_text(config.get("version")) or "v4.68",
        status=status,
        queue_mode=normalize_text(config.get("queue_mode")),
        classified_record_count=len(config.get("classified_records", [])) if isinstance(config.get("classified_records"), list) else 0,
        queue_item_count=len(queue_items),
        high_ready_count=counts["RESEARCH_QUEUE_HIGH_READY"],
        medium_ready_count=counts["RESEARCH_QUEUE_MEDIUM_READY"],
        low_ready_count=counts["RESEARCH_QUEUE_LOW_READY"],
        needs_more_public_data_count=counts["RESEARCH_QUEUE_NEEDS_MORE_PUBLIC_DATA"],
        needs_manual_source_review_count=counts["RESEARCH_QUEUE_NEEDS_MANUAL_SOURCE_REVIEW"],
        blocked_safe_count=counts["RESEARCH_QUEUE_BLOCKED_SAFE"],
        skipped_record_count=len(skipped_records),
        blocked_record_count=len(blocked_records),
        duplicate_asset_id_count=duplicate_count,
        queue_items=queue_items,
        skipped_records=skipped_records,
        blocked_records=tuple(blocked_records),
        warnings=(),
        blockers=blockers,
        next_safe_action=normalize_text(config.get("next_manual_action")),
    )


def _output_root_blockers(path: str | Path) -> tuple[str, ...]:
    text = normalize_text(path)
    if not text:
        return ("research queue output root is required.",)
    normalized = text.replace("\\", "/").rstrip("/")
    blocked_roots = {"docs", "templates", "jarvis/data", "."}
    if normalized in blocked_roots or normalized.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("research queue output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def _path_blockers(path: str | Path, root: str | Path) -> tuple[str, ...]:
    candidate = Path(path).resolve()
    root_path = Path(root).resolve()
    try:
        candidate.relative_to(root_path)
    except ValueError:
        return ("path must stay under the configured research queue output root.",)
    return ()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def execute_authorized_research_queue_cache_write(
    config: dict[str, Any],
    queue_items: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None:
        blockers.extend(_path_blockers(output_root, ALLOWED_OUTPUT_ROOT))
    for item in queue_items:
        blockers.extend(f"{item.get('asset_id', 'unknown')}: {reason}" for reason in validate_queue_item(item))
    if blockers:
        return {"status": "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    queue_created_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = {"queue_created_at": queue_created_at, "queue_data_unverified": True, "items": list(queue_items)}
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digest = _sha256_bytes(raw_bytes)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "public_asset_universe.research_queue.json"
    metadata_path = output_root / "public_asset_universe.research_queue.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "queue_created_at": queue_created_at,
        "queue_item_count": len(queue_items),
        "content_sha256": digest,
        "queue_data_unverified": True,
        "evidence_verified": False,
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
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {
        "status": "PUBLIC_ASSET_UNIVERSE_RESEARCH_QUEUE_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_public_asset_universe_research_priority_queue_summary(result: PublicAssetUniverseResearchPriorityQueueResult) -> str:
    return (
        f"status={result.status}; classified={result.classified_record_count}; queue_items={result.queue_item_count}; "
        f"high={result.high_ready_count}; medium={result.medium_ready_count}; low={result.low_ready_count}; "
        f"needs_more={result.needs_more_public_data_count}; manual_review={result.needs_manual_source_review_count}; "
        f"blocked_safe={result.blocked_safe_count}; blocked_records={result.blocked_record_count}"
    )


def load_public_asset_universe_research_priority_queue_result(path: str | Path) -> PublicAssetUniverseResearchPriorityQueueResult:
    return evaluate_public_asset_universe_research_priority_queue(load_json(path))
