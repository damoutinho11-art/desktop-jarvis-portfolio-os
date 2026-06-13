"""Public evidence pack draft generator.

v4.69 turns public research queue items into draft evidence-pack checklists.
It is not evidence extraction, evidence verification, verified evidence
promotion, approval, recommendation, allocation, trading, registry mutation, or
execution.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_PUBLIC_EVIDENCE_PACK_DRAFT_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE"
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/public_asset_universe/evidence_pack_drafts")
ALLOWED_REQUIRED_PUBLIC_EVIDENCE_SECTIONS = (
    "identity_and_identifier_check",
    "issuer_or_provider_check",
    "instrument_structure_check",
    "listing_or_venue_check",
    "currency_and_region_check",
    "public_documentation_check",
    "fee_or_cost_public_data_check",
    "liquidity_public_data_check",
    "risk_public_data_check",
    "freshness_and_source_date_check",
    "manual_verification_decision",
    "manual_approval_decision",
)
ALLOWED_NEXT_MANUAL_RESEARCH_STEPS = {
    "collect_public_evidence",
    "verify_public_identifiers_manually",
    "refresh_public_cache_before_pack",
    "fix_queue_or_classification_inputs",
    "hold_until_safe",
    "no_action_until_manual_review",
}
READY_PRIORITY_BUCKETS = {
    "RESEARCH_QUEUE_HIGH_READY",
    "RESEARCH_QUEUE_MEDIUM_READY",
    "RESEARCH_QUEUE_LOW_READY",
}
VALID_NEXT_MANUAL_ACTIONS = {
    "review_public_evidence_pack_drafts",
    "proceed_to_operator_research_dashboard_integration",
    "fix_research_queue_items",
    "rerun_research_priority_queue",
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
FORBIDDEN_RESEARCH_STEPS = {
    "trade",
    "trade_execution",
    "allocation",
    "allocation_recommendation",
    "approval",
    "registry_mutation",
    "executor",
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
    "draft_pack_data_unverified",
    "draft_generation_only",
)


@dataclass(frozen=True)
class PublicEvidencePackDraftGeneratorResult:
    title: str
    version: str
    status: str
    draft_generator_mode: str
    queue_item_count: int
    draft_pack_count: int
    ready_draft_count: int
    needs_more_public_data_count: int
    manual_source_review_count: int
    blocked_safe_count: int
    skipped_item_count: int
    blocked_item_count: int
    duplicate_draft_pack_id_count: int
    draft_packs: tuple[dict[str, Any], ...]
    skipped_items: tuple[str, ...]
    blocked_items: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    next_safe_action: str
    no_network_called: bool = True
    no_fetch_executed: bool = True
    no_cache_mutated: bool = True
    no_evidence_extraction: bool = True
    no_evidence_verification: bool = True
    no_verified_evidence_promotion: bool = True
    no_investment_screening: bool = True
    no_research_scoring: bool = True
    no_recommendation: bool = True
    no_approval: bool = True
    no_allocation: bool = True
    no_trade: bool = True
    no_executor: bool = True
    local_cache_only: bool = True
    draft_pack_data_unverified: bool = True


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


def validate_draft_generator_config(config: dict[str, Any]) -> tuple[str, ...]:
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
    for field in ("research_queue_input_policy", "evidence_pack_draft_policy", "authorization_policy", "evidence_pack_schema", "draft_rules"):
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
            "draft_pack_data_unverified": True,
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
    if not isinstance(config.get("research_queue_items", []), list):
        blocked.append("research_queue_items must be a list.")
    return tuple(dict.fromkeys(blocked))


def validate_research_queue_item_for_draft(item: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    required = (
        "queue_id",
        "asset_id",
        "display_name",
        "asset_type",
        "symbol_or_identifier",
        "source_id",
        "asset_class",
        "instrument_type",
        "region_bucket",
        "currency_bucket",
        "research_priority_bucket",
        "research_priority_reason",
        "suggested_next_research_step",
    )
    for field in required:
        if field not in item:
            blocked.append(f"{field} is required.")
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
    if item.get("required_manual_review") is not True:
        blocked.append("required_manual_review must be true.")
    step = normalize_text(item.get("suggested_next_research_step"))
    if step in FORBIDDEN_RESEARCH_STEPS:
        blocked.append(f"suggested_next_research_step must not be {step}.")
    for field in ("approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "candidate_registry_write", "executor_created"):
        if item.get(field) is True:
            blocked.append(f"{field} must not be true.")
    if item.get("portfolio_weight") not in {None, False, 0, 0.0}:
        blocked.append("portfolio_weight must not be nonzero.")
    return tuple(blocked)


def build_draft_pack_id(queue_item: dict[str, Any]) -> str:
    asset_id = normalize_text(queue_item.get("asset_id")) or "unknown"
    return f"public_evidence_pack_draft::{asset_id}"


def build_required_public_evidence_sections(queue_item: dict[str, Any]) -> tuple[str, ...]:
    return ALLOWED_REQUIRED_PUBLIC_EVIDENCE_SECTIONS


def build_required_public_source_categories(queue_item: dict[str, Any]) -> tuple[str, ...]:
    asset_type = normalize_text(queue_item.get("asset_type")).upper()
    categories = [
        "public_identifier_reference",
        "official_issuer_or_provider_reference",
        "public_listing_or_venue_reference",
        "public_documentation_reference",
        "public_market_data_reference",
        "public_source_date_reference",
    ]
    if asset_type in {"ETF", "FUND_OR_ETP"}:
        categories.extend(("official_fund_factsheet_or_kid_reference", "public_fee_or_cost_reference", "public_holdings_or_exposure_reference"))
    elif asset_type == "CRYPTO_ASSET":
        categories.extend(("public_protocol_documentation_reference", "public_crypto_market_reference", "manual_custody_risk_review_reference"))
    elif asset_type == "EQUITY":
        categories.extend(("public_issuer_profile_reference", "public_exchange_listing_reference"))
    else:
        categories.append("manual_public_source_review_reference")
    categories.append("manual_verification_reference")
    return tuple(dict.fromkeys(categories))


def build_missing_information_checklist(queue_item: dict[str, Any]) -> tuple[str, ...]:
    missing = [f"missing_classification_field::{field}" for field in queue_item.get("missing_classification_fields", ()) if normalize_text(field)]
    bucket = queue_item.get("research_priority_bucket")
    if bucket == "RESEARCH_QUEUE_NEEDS_MORE_PUBLIC_DATA":
        missing.append("collect_more_public_identifiers_before_manual_trust_review")
    elif bucket == "RESEARCH_QUEUE_NEEDS_MANUAL_SOURCE_REVIEW":
        missing.append("refresh_or_review_public_source_freshness_before_manual_trust_review")
    elif bucket == "RESEARCH_QUEUE_BLOCKED_SAFE":
        missing.append("fix_queue_or_classification_inputs_before_public_evidence_pack_work")
    if not missing:
        missing.append("no_missing_public_fields_identified_by_queue")
    return tuple(missing)


def build_manual_verification_checklist(queue_item: dict[str, Any]) -> tuple[str, ...]:
    return (
        "manual_confirm_asset_identity_and_identifier",
        "manual_confirm_issuer_or_provider_name",
        "manual_confirm_instrument_structure",
        "manual_confirm_listing_or_venue",
        "manual_confirm_currency_and_region",
        "manual_confirm_public_documentation_source_dates",
        "manual_confirm_fee_or_cost_public_data_if_applicable",
        "manual_confirm_liquidity_public_data_if_applicable",
        "manual_confirm_risk_notes_before_any_later_trust_decision",
    )


def build_manual_decision_placeholders(queue_item: dict[str, Any]) -> tuple[str, ...]:
    return (
        "manual_verification_decision_pending",
        "manual_approval_decision_pending",
        "manual_researcher_notes_pending",
    )


def build_risk_review_placeholders(queue_item: dict[str, Any]) -> tuple[str, ...]:
    return (
        "risk_notes_pending_manual_review",
        "structure_risk_pending_manual_review",
        "source_freshness_risk_pending_manual_review",
        "liquidity_risk_pending_manual_review",
    )


def choose_next_manual_research_step(queue_item: dict[str, Any]) -> str:
    bucket = queue_item.get("research_priority_bucket")
    if bucket in READY_PRIORITY_BUCKETS:
        return "collect_public_evidence"
    if bucket == "RESEARCH_QUEUE_NEEDS_MORE_PUBLIC_DATA":
        return "verify_public_identifiers_manually"
    if bucket == "RESEARCH_QUEUE_NEEDS_MANUAL_SOURCE_REVIEW":
        return "refresh_public_cache_before_pack"
    if bucket == "RESEARCH_QUEUE_BLOCKED_SAFE":
        return "hold_until_safe"
    return "fix_queue_or_classification_inputs"


def build_evidence_pack_draft(queue_item: dict[str, Any], current_date: Any) -> dict[str, Any]:
    return {
        "draft_pack_id": build_draft_pack_id(queue_item),
        "asset_id": queue_item.get("asset_id"),
        "display_name": queue_item.get("display_name"),
        "asset_type": queue_item.get("asset_type"),
        "symbol_or_identifier": queue_item.get("symbol_or_identifier"),
        "source_id": queue_item.get("source_id"),
        "asset_class": queue_item.get("asset_class"),
        "instrument_type": queue_item.get("instrument_type"),
        "region_bucket": queue_item.get("region_bucket"),
        "currency_bucket": queue_item.get("currency_bucket"),
        "research_priority_bucket": queue_item.get("research_priority_bucket"),
        "research_priority_reason": queue_item.get("research_priority_reason"),
        "draft_created_at": normalize_text(current_date),
        "draft_status": "DRAFT_PUBLIC_EVIDENCE_PACK_UNVERIFIED",
        "evidence_status": "UNVERIFIED_PUBLIC_DATA",
        "verification_status": "NOT_VERIFIED",
        "approval_status": "NOT_APPROVED",
        "investability_status": "NOT_INVESTABLE",
        "recommendation_status": "NO_RECOMMENDATION",
        "allocation_status": "NO_ALLOCATION",
        "execution_status": "NO_EXECUTION",
        "trade_status": "NO_TRADE",
        "required_public_evidence_sections": build_required_public_evidence_sections(queue_item),
        "required_public_source_categories": build_required_public_source_categories(queue_item),
        "missing_information_checklist": build_missing_information_checklist(queue_item),
        "manual_verification_checklist": build_manual_verification_checklist(queue_item),
        "manual_decision_placeholders": build_manual_decision_placeholders(queue_item),
        "risk_review_placeholders": build_risk_review_placeholders(queue_item),
        "next_manual_research_step": choose_next_manual_research_step(queue_item),
        "safety_notes": (
            "Draft public evidence pack only.",
            "No evidence extraction, verification, promotion, approval, recommendation, allocation, trading, registry mutation, or execution.",
        ),
    }


def validate_evidence_pack_draft(draft_pack: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    required = (
        "draft_pack_id",
        "asset_id",
        "display_name",
        "asset_type",
        "symbol_or_identifier",
        "source_id",
        "asset_class",
        "instrument_type",
        "research_priority_bucket",
        "draft_created_at",
        "required_public_evidence_sections",
        "required_public_source_categories",
        "manual_verification_checklist",
        "next_manual_research_step",
    )
    for field in required:
        if field not in draft_pack:
            blocked.append(f"{field} is required.")
    expected = {
        "draft_status": "DRAFT_PUBLIC_EVIDENCE_PACK_UNVERIFIED",
        "evidence_status": "UNVERIFIED_PUBLIC_DATA",
        "verification_status": "NOT_VERIFIED",
        "approval_status": "NOT_APPROVED",
        "investability_status": "NOT_INVESTABLE",
        "recommendation_status": "NO_RECOMMENDATION",
        "allocation_status": "NO_ALLOCATION",
        "execution_status": "NO_EXECUTION",
        "trade_status": "NO_TRADE",
    }
    for field, value in expected.items():
        if draft_pack.get(field) != value:
            blocked.append(f"{field} must be {value}.")
    sections = tuple(draft_pack.get("required_public_evidence_sections", ()))
    for section in sections:
        if section not in ALLOWED_REQUIRED_PUBLIC_EVIDENCE_SECTIONS:
            blocked.append(f"required_public_evidence_sections contains unsupported {section}.")
    if draft_pack.get("next_manual_research_step") not in ALLOWED_NEXT_MANUAL_RESEARCH_STEPS:
        blocked.append("next_manual_research_step is not allowed.")
    for field in ("evidence_verified", "approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "candidate_registry_write", "executor_created"):
        if draft_pack.get(field) is True:
            blocked.append(f"{field} must not be true.")
    if draft_pack.get("portfolio_weight") not in {None, False, 0, 0.0}:
        blocked.append("portfolio_weight must not be nonzero.")
    if draft_pack.get("recommendation_status") in {"BUY", "SELL", "HOLD"}:
        blocked.append("recommendation_status must not be BUY, SELL, or HOLD.")
    return tuple(blocked)


def generate_public_evidence_pack_drafts(config: dict[str, Any]) -> tuple[tuple[dict[str, Any], ...], tuple[str, ...], tuple[str, ...]]:
    drafts: list[dict[str, Any]] = []
    skipped: list[str] = []
    blocked: list[str] = []
    for item in config.get("research_queue_items", []):
        if not isinstance(item, dict):
            blocked.append("research queue item must be an object")
            continue
        asset_id = normalize_text(item.get("asset_id")) or "unknown"
        reasons = validate_research_queue_item_for_draft(item)
        if reasons:
            blocked.append(f"{asset_id}: {'; '.join(reasons)}")
            continue
        draft = build_evidence_pack_draft(item, config.get("current_date"))
        draft_reasons = validate_evidence_pack_draft(draft)
        if draft_reasons:
            blocked.append(f"{asset_id}: {'; '.join(draft_reasons)}")
            continue
        drafts.append(draft)
    return tuple(sorted(drafts, key=lambda draft: (draft["next_manual_research_step"], draft["asset_id"]))), tuple(skipped), tuple(blocked)


def evaluate_public_evidence_pack_draft_generator(config: dict[str, Any]) -> PublicEvidencePackDraftGeneratorResult:
    config_blockers = list(validate_draft_generator_config(config))
    if isinstance(config.get("research_queue_items"), list) and not config.get("research_queue_items"):
        config_blockers.append("research_queue_items must contain at least one item.")
    draft_packs, skipped_items, blocked_items = generate_public_evidence_pack_drafts(config)
    ids = [draft["draft_pack_id"] for draft in draft_packs]
    duplicate_count = len(ids) - len(set(ids))
    record_blockers = ["duplicate draft_pack_id detected."] if duplicate_count else []
    blockers = tuple(dict.fromkeys(config_blockers + list(blocked_items) + record_blockers))
    authorized = _authorization_valid(config)
    if config_blockers or (blockers and not draft_packs):
        status = "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_BLOCKED_SAFE"
    elif blockers or skipped_items:
        status = "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_PARTIAL_SAFE"
    elif authorized:
        status = "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_READY_TO_WRITE_SAFE"
    else:
        status = "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_READY_SAFE"
    next_step_counts = {step: 0 for step in ALLOWED_NEXT_MANUAL_RESEARCH_STEPS}
    for draft in draft_packs:
        next_step_counts[draft["next_manual_research_step"]] += 1
    return PublicEvidencePackDraftGeneratorResult(
        title=normalize_text(config.get("title")) or "J.A.R.V.I.S. Public Evidence Pack Draft Generator",
        version=normalize_text(config.get("version")) or "v4.69",
        status=status,
        draft_generator_mode=normalize_text(config.get("draft_generator_mode")),
        queue_item_count=len(config.get("research_queue_items", [])) if isinstance(config.get("research_queue_items"), list) else 0,
        draft_pack_count=len(draft_packs),
        ready_draft_count=next_step_counts["collect_public_evidence"],
        needs_more_public_data_count=next_step_counts["verify_public_identifiers_manually"] + next_step_counts["fix_queue_or_classification_inputs"],
        manual_source_review_count=next_step_counts["refresh_public_cache_before_pack"] + next_step_counts["no_action_until_manual_review"],
        blocked_safe_count=next_step_counts["hold_until_safe"],
        skipped_item_count=len(skipped_items),
        blocked_item_count=len(blocked_items),
        duplicate_draft_pack_id_count=duplicate_count,
        draft_packs=draft_packs,
        skipped_items=skipped_items,
        blocked_items=tuple(blocked_items),
        warnings=(),
        blockers=blockers,
        next_safe_action=normalize_text(config.get("next_manual_action")),
    )


def _output_root_blockers(path: str | Path) -> tuple[str, ...]:
    text = normalize_text(path)
    if not text:
        return ("evidence pack draft output root is required.",)
    normalized = text.replace("\\", "/").rstrip("/")
    blocked_roots = {"docs", "templates", "jarvis/data", "."}
    if normalized in blocked_roots or normalized.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("evidence pack draft output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def _path_blockers(path: str | Path, root: str | Path) -> tuple[str, ...]:
    candidate = Path(path).resolve()
    root_path = Path(root).resolve()
    try:
        candidate.relative_to(root_path)
    except ValueError:
        return ("path must stay under the configured evidence pack draft output root.",)
    return ()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def execute_authorized_evidence_pack_draft_cache_write(
    config: dict[str, Any],
    draft_packs: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None:
        blockers.extend(_path_blockers(output_root, ALLOWED_OUTPUT_ROOT))
    for draft in draft_packs:
        blockers.extend(f"{draft.get('asset_id', 'unknown')}: {reason}" for reason in validate_evidence_pack_draft(draft))
    if blockers:
        return {"status": "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    draft_created_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = {"draft_created_at": draft_created_at, "draft_pack_data_unverified": True, "draft_packs": list(draft_packs)}
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digest = _sha256_bytes(raw_bytes)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "public_asset_universe.evidence_pack_drafts.json"
    metadata_path = output_root / "public_asset_universe.evidence_pack_drafts.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "draft_created_at": draft_created_at,
        "draft_pack_count": len(draft_packs),
        "content_sha256": digest,
        "draft_pack_data_unverified": True,
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
        "status": "PUBLIC_EVIDENCE_PACK_DRAFT_GENERATOR_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_public_evidence_pack_draft_generator_summary(result: PublicEvidencePackDraftGeneratorResult) -> str:
    return (
        f"status={result.status}; queue_items={result.queue_item_count}; draft_packs={result.draft_pack_count}; "
        f"ready={result.ready_draft_count}; needs_more={result.needs_more_public_data_count}; "
        f"manual_source_review={result.manual_source_review_count}; blocked_safe={result.blocked_safe_count}; "
        f"blocked_items={result.blocked_item_count}"
    )


def load_public_evidence_pack_draft_generator_result(path: str | Path) -> PublicEvidencePackDraftGeneratorResult:
    return evaluate_public_evidence_pack_draft_generator(load_json(path))
