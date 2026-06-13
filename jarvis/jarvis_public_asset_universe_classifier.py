"""Public asset universe classifier.

v4.67 classifies normalized public asset records structurally. It is not
screening, research scoring, evidence extraction, evidence verification,
recommendation, approval, allocation, trading, registry mutation, or execution.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_AUTHORIZATION_PHRASE = "AUTHORIZE_PUBLIC_ASSET_UNIVERSE_CLASSIFY_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE"
ALLOWED_OUTPUT_ROOT = Path("jarvis/local/public_asset_universe/classified")
ALLOWED_ASSET_CLASSES = {"ETF", "EQUITY", "FUND_OR_ETP", "CRYPTO_ASSET", "MARKET_REFERENCE", "UNKNOWN_PUBLIC_ASSET"}
ALLOWED_INSTRUMENT_TYPES = {"ETF", "COMMON_STOCK", "FUND", "ETP", "CRYPTO_ASSET", "MARKET_REFERENCE", "UNKNOWN_INSTRUMENT"}
ALLOWED_COMPLETENESS = {"COMPLETE_CORE_FIELDS", "PARTIAL_CORE_FIELDS", "MISSING_CORE_FIELDS"}
ALLOWED_FRESHNESS = {"FRESH_PUBLIC_DATA", "MANUAL_REVIEW_PUBLIC_DATA", "STALE_PUBLIC_DATA", "UNKNOWN_FRESHNESS"}
ALLOWED_READINESS = {
    "READY_FOR_RESEARCH_QUEUE",
    "NEEDS_MORE_PUBLIC_DATA",
    "NEEDS_MANUAL_SOURCE_REVIEW",
    "BLOCKED_BY_MISSING_FIELDS",
}
ALLOWED_CONFIDENCE = {
    "HIGH_STRUCTURAL_CONFIDENCE",
    "MEDIUM_STRUCTURAL_CONFIDENCE",
    "LOW_STRUCTURAL_CONFIDENCE",
    "BLOCKED_STRUCTURAL_CONFIDENCE",
}
VALID_NEXT_MANUAL_ACTIONS = {
    "review_classified_public_asset_universe",
    "proceed_to_research_priority_queue",
    "fix_normalized_records",
    "rerun_normalizer",
    "no_manual_asset_entry_required",
}
BLOCKED_NEXT_MANUAL_ACTIONS = {
    "screen_now",
    "score_now",
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
    "screening",
    "research_scoring",
    "ranking",
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
    "classified_data_unverified",
    "classification_only",
)
CORE_FIELDS = (
    "asset_id",
    "display_name",
    "asset_type",
    "symbol_or_identifier",
    "issuer_or_provider",
    "market_or_region",
    "currency",
    "source_id",
    "last_refreshed_at",
)
NORMALIZED_REQUIRED_FIELDS = (
    "asset_id",
    "display_name",
    "asset_type",
    "symbol_or_identifier",
    "issuer_or_provider",
    "exchange_or_venue",
    "market_or_region",
    "currency",
    "isin_or_figi_or_other_public_identifier",
    "source_id",
    "source_category_id",
    "source_reference_ids",
    "discovery_source",
    "discovered_at",
    "last_refreshed_at",
    "normalized_at",
    "data_freshness_status",
    "safety_notes",
)


@dataclass(frozen=True)
class PublicAssetUniverseClassifierResult:
    title: str
    version: str
    status: str
    classifier_mode: str
    normalized_record_count: int
    classified_record_count: int
    skipped_record_count: int
    blocked_record_count: int
    invalid_record_count: int
    duplicate_asset_id_count: int
    ready_for_research_queue_count: int
    needs_more_public_data_count: int
    needs_manual_source_review_count: int
    blocked_by_missing_fields_count: int
    classified_records: tuple[dict[str, Any], ...]
    skipped_records: tuple[str, ...]
    blocked_records: tuple[str, ...]
    warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    next_safe_action: str
    no_network_called: bool = True
    no_fetch_executed: bool = True
    no_cache_mutated: bool = True
    no_evidence_verification: bool = True
    no_screening: bool = True
    no_research_scoring: bool = True
    no_recommendation: bool = True
    no_approval: bool = True
    no_allocation: bool = True
    no_trade: bool = True
    no_executor: bool = True
    local_cache_only: bool = True
    classified_data_unverified: bool = True


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value).strip()) if value is not None else ""


def _upper(value: Any) -> str:
    return normalize_text(value).upper().replace("-", "_").replace(" ", "_")


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


def classify_asset_class(record: dict[str, Any]) -> str:
    text = _upper(record.get("asset_type"))
    aliases = {
        "ETF": "ETF",
        "EQUITY": "EQUITY",
        "STOCK": "EQUITY",
        "COMMON_STOCK": "EQUITY",
        "FUND": "FUND_OR_ETP",
        "ETP": "FUND_OR_ETP",
        "FUND_OR_ETP": "FUND_OR_ETP",
        "CRYPTO": "CRYPTO_ASSET",
        "CRYPTO_ASSET": "CRYPTO_ASSET",
        "MARKET": "MARKET_REFERENCE",
        "MARKET_REFERENCE": "MARKET_REFERENCE",
    }
    return aliases.get(text, "UNKNOWN_PUBLIC_ASSET")


def classify_instrument_type(record: dict[str, Any]) -> str:
    asset_class = classify_asset_class(record)
    text = _upper(" ".join(normalize_text(record.get(field)) for field in ("asset_type", "display_name", "source_category_id")))
    if asset_class == "ETF":
        return "ETF"
    if asset_class == "EQUITY":
        return "COMMON_STOCK"
    if asset_class == "CRYPTO_ASSET":
        return "CRYPTO_ASSET"
    if asset_class == "MARKET_REFERENCE":
        return "MARKET_REFERENCE"
    if asset_class == "FUND_OR_ETP":
        if "ETP" in text:
            return "ETP"
        if "FUND" in text:
            return "FUND"
    return "UNKNOWN_INSTRUMENT"


def classify_region_bucket(record: dict[str, Any]) -> str:
    text = _upper(record.get("market_or_region"))
    if not text or text == "UNKNOWN":
        return "REGION_UNKNOWN"
    if text in {"GLOBAL", "WORLD", "DEVELOPED_MARKETS", "EMERGING_MARKETS"}:
        return f"REGION_{text}"
    if text in {"UNITED_STATES", "US", "USA", "NORTH_AMERICA"}:
        return "REGION_NORTH_AMERICA"
    if text in {"EUROPE", "EU", "EUROZONE"}:
        return "REGION_EUROPE"
    return f"REGION_OTHER_{re.sub(r'[^A-Z0-9_]+', '_', text).strip('_')}"


def classify_currency_bucket(record: dict[str, Any]) -> str:
    text = _upper(record.get("currency"))
    if text in {"EUR", "USD", "GBP", "CHF"}:
        return f"CURRENCY_{text}"
    if len(text) == 3 and text.isalpha():
        return "CURRENCY_OTHER_PUBLIC"
    return "CURRENCY_UNKNOWN"


def classify_venue_bucket(record: dict[str, Any]) -> str:
    text = _upper(record.get("exchange_or_venue"))
    if not text:
        return "VENUE_UNKNOWN"
    if text in {"XETRA", "NASDAQ", "NYSE", "LSE", "PUBLIC"}:
        return f"VENUE_{text}"
    return "VENUE_OTHER_PUBLIC"


def classify_issuer_or_provider_bucket(record: dict[str, Any]) -> str:
    text = normalize_text(record.get("issuer_or_provider"))
    if not text:
        return "ISSUER_PROVIDER_MISSING"
    if len(text) < 3:
        return "ISSUER_PROVIDER_WEAK"
    return "ISSUER_PROVIDER_PRESENT"


def classify_identifier_quality(record: dict[str, Any]) -> str:
    text = normalize_text(record.get("isin_or_figi_or_other_public_identifier"))
    if not text:
        return "IDENTIFIER_MISSING"
    if re.fullmatch(r"[A-Z]{2}[A-Z0-9]{10}", text.upper()):
        return "IDENTIFIER_ISIN_SHAPED"
    if text.upper().startswith("BBG") and len(text) >= 10:
        return "IDENTIFIER_FIGI_SHAPED"
    if len(text) >= 3:
        return "IDENTIFIER_PUBLIC_OTHER"
    return "IDENTIFIER_WEAK"


def _missing_core_fields(record: dict[str, Any]) -> tuple[str, ...]:
    return tuple(field for field in CORE_FIELDS if not normalize_text(record.get(field)) or normalize_text(record.get(field)).upper() == "UNKNOWN")


def classify_data_completeness(record: dict[str, Any]) -> str:
    missing = _missing_core_fields(record)
    if not missing:
        return "COMPLETE_CORE_FIELDS"
    if len(missing) <= 3:
        return "PARTIAL_CORE_FIELDS"
    return "MISSING_CORE_FIELDS"


def classify_freshness(record: dict[str, Any]) -> str:
    text = _upper(record.get("data_freshness_status"))
    if text in {"CACHE_FRESH_SAFE", "FRESH"}:
        return "FRESH_PUBLIC_DATA"
    if text in {"CACHE_MANUAL_REVIEW_REQUIRED_SAFE", "MANUAL"}:
        return "MANUAL_REVIEW_PUBLIC_DATA"
    if text in {"CACHE_STALE_SAFE", "STALE", "CACHE_STALE_BLOCKED"}:
        return "STALE_PUBLIC_DATA"
    return "UNKNOWN_FRESHNESS"


def _safe_normalized_statuses(record: dict[str, Any]) -> bool:
    return (
        record.get("evidence_status") == "UNVERIFIED_PUBLIC_DATA"
        and record.get("approval_status") == "NOT_APPROVED"
        and record.get("investability_status") == "NOT_INVESTABLE"
        and record.get("execution_status") == "NO_EXECUTION"
        and record.get("classification_status") in {"NOT_CLASSIFIED", "CLASSIFICATION_PENDING"}
        and record.get("screening_status") == "NOT_SCREENED"
        and record.get("evidence_pack_status") == "NOT_GENERATED"
        and record.get("raw_unverified") is True
        and record.get("normalized_public_data_only") is True
        and record.get("manual_review_required") is True
        and record.get("manual_approval_required") is True
    )


def classify_evidence_readiness(record: dict[str, Any]) -> str:
    completeness = classify_data_completeness(record)
    freshness = classify_freshness(record)
    if completeness == "MISSING_CORE_FIELDS":
        return "BLOCKED_BY_MISSING_FIELDS"
    if completeness == "PARTIAL_CORE_FIELDS":
        return "NEEDS_MORE_PUBLIC_DATA"
    if freshness in {"STALE_PUBLIC_DATA", "UNKNOWN_FRESHNESS"}:
        return "NEEDS_MANUAL_SOURCE_REVIEW"
    if _safe_normalized_statuses(record):
        return "READY_FOR_RESEARCH_QUEUE"
    return "NEEDS_MANUAL_SOURCE_REVIEW"


def classify_confidence(record: dict[str, Any]) -> str:
    readiness = classify_evidence_readiness(record)
    completeness = classify_data_completeness(record)
    identifier = classify_identifier_quality(record)
    if readiness == "BLOCKED_BY_MISSING_FIELDS":
        return "BLOCKED_STRUCTURAL_CONFIDENCE"
    if completeness == "COMPLETE_CORE_FIELDS" and identifier in {"IDENTIFIER_ISIN_SHAPED", "IDENTIFIER_FIGI_SHAPED", "IDENTIFIER_PUBLIC_OTHER"}:
        return "HIGH_STRUCTURAL_CONFIDENCE"
    if completeness in {"COMPLETE_CORE_FIELDS", "PARTIAL_CORE_FIELDS"}:
        return "MEDIUM_STRUCTURAL_CONFIDENCE"
    return "LOW_STRUCTURAL_CONFIDENCE"


def validate_classifier_config(config: dict[str, Any]) -> tuple[str, ...]:
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
    for field in ("normalized_input_policy", "classified_output_policy", "authorization_policy", "classification_schema", "classification_rules", "quality_policy"):
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
            "classified_data_unverified": True,
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
    if not isinstance(config.get("normalized_records", []), list):
        blocked.append("normalized_records must be a list.")
    return tuple(dict.fromkeys(blocked))


def validate_normalized_record_for_classification(record: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    for field in NORMALIZED_REQUIRED_FIELDS:
        if field not in record:
            blocked.append(f"{field} is required.")
    expected = {
        "evidence_status": "UNVERIFIED_PUBLIC_DATA",
        "approval_status": "NOT_APPROVED",
        "investability_status": "NOT_INVESTABLE",
        "execution_status": "NO_EXECUTION",
        "screening_status": "NOT_SCREENED",
        "evidence_pack_status": "NOT_GENERATED",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            blocked.append(f"{field} must be {value}.")
    if record.get("classification_status") not in {"NOT_CLASSIFIED", "CLASSIFICATION_PENDING"}:
        blocked.append("classification_status must be NOT_CLASSIFIED or CLASSIFICATION_PENDING.")
    for field in ("raw_unverified", "normalized_public_data_only", "manual_review_required", "manual_approval_required"):
        if record.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in ("approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "candidate_registry_write", "executor_created"):
        if record.get(field) is True:
            blocked.append(f"{field} must not be true.")
    if record.get("portfolio_weight") not in {None, False, 0, 0.0}:
        blocked.append("portfolio_weight must not be nonzero.")
    return tuple(blocked)


def classify_normalized_record(record: dict[str, Any], current_date: Any) -> dict[str, Any]:
    missing = _missing_core_fields(record)
    classified = dict(record)
    classified.update(
        {
            "classified_at": normalize_text(current_date),
            "classification_status": "CLASSIFIED_PUBLIC_DATA_ONLY",
            "classification_method": "DETERMINISTIC_RULE_BASED_STRUCTURAL_ONLY",
            "asset_class": classify_asset_class(record),
            "instrument_type": classify_instrument_type(record),
            "region_bucket": classify_region_bucket(record),
            "currency_bucket": classify_currency_bucket(record),
            "venue_bucket": classify_venue_bucket(record),
            "issuer_or_provider_bucket": classify_issuer_or_provider_bucket(record),
            "identifier_quality": classify_identifier_quality(record),
            "data_completeness_bucket": classify_data_completeness(record),
            "freshness_bucket": classify_freshness(record),
            "evidence_readiness_bucket": classify_evidence_readiness(record),
            "missing_classification_fields": missing,
            "classification_confidence_label": classify_confidence(record),
            "classification_notes": (
                "Deterministic structural classification only.",
                "Not screening, scoring, recommendation, approval, allocation, trading, or execution.",
            ),
            "screening_status": "NOT_SCREENED",
            "research_score_status": "NOT_SCORED",
            "recommendation_status": "NO_RECOMMENDATION",
            "evidence_status": "UNVERIFIED_PUBLIC_DATA",
            "approval_status": "NOT_APPROVED",
            "investability_status": "NOT_INVESTABLE",
            "execution_status": "NO_EXECUTION",
            "manual_review_required": True,
            "manual_approval_required": True,
        }
    )
    return classified


def validate_classified_record(record: dict[str, Any]) -> tuple[str, ...]:
    blocked: list[str] = []
    required = (
        "asset_id",
        "classified_at",
        "classification_status",
        "classification_method",
        "asset_class",
        "instrument_type",
        "region_bucket",
        "currency_bucket",
        "venue_bucket",
        "issuer_or_provider_bucket",
        "identifier_quality",
        "data_completeness_bucket",
        "freshness_bucket",
        "evidence_readiness_bucket",
        "missing_classification_fields",
        "classification_confidence_label",
        "screening_status",
        "research_score_status",
        "recommendation_status",
    )
    for field in required:
        if field not in record or record.get(field) in {None, ""}:
            blocked.append(f"{field} is required.")
    allowed_checks = (
        ("asset_class", ALLOWED_ASSET_CLASSES),
        ("instrument_type", ALLOWED_INSTRUMENT_TYPES),
        ("data_completeness_bucket", ALLOWED_COMPLETENESS),
        ("freshness_bucket", ALLOWED_FRESHNESS),
        ("evidence_readiness_bucket", ALLOWED_READINESS),
        ("classification_confidence_label", ALLOWED_CONFIDENCE),
    )
    for field, allowed in allowed_checks:
        if record.get(field) not in allowed:
            blocked.append(f"{field} is not allowed.")
    expected = {
        "classification_status": "CLASSIFIED_PUBLIC_DATA_ONLY",
        "classification_method": "DETERMINISTIC_RULE_BASED_STRUCTURAL_ONLY",
        "screening_status": "NOT_SCREENED",
        "research_score_status": "NOT_SCORED",
        "recommendation_status": "NO_RECOMMENDATION",
        "evidence_status": "UNVERIFIED_PUBLIC_DATA",
        "approval_status": "NOT_APPROVED",
        "investability_status": "NOT_INVESTABLE",
        "execution_status": "NO_EXECUTION",
    }
    for field, value in expected.items():
        if record.get(field) != value:
            blocked.append(f"{field} must be {value}.")
    if record.get("recommendation_status") in {"BUY", "SELL", "HOLD"}:
        blocked.append("recommendation_status must not be BUY/SELL/HOLD.")
    for field in ("manual_review_required", "manual_approval_required"):
        if record.get(field) is not True:
            blocked.append(f"{field} must be true.")
    for field in ("approved_asset", "trusted_asset", "investable", "allocation_recommendation", "buy_signal", "sell_signal", "trade_executed", "registry_mutation", "candidate_registry_write", "executor_created"):
        if record.get(field) is True:
            blocked.append(f"{field} must not be true.")
    if record.get("portfolio_weight") not in {None, False, 0, 0.0}:
        blocked.append("portfolio_weight must not be nonzero.")
    return tuple(blocked)


def classify_normalized_records(config: dict[str, Any]) -> tuple[tuple[dict[str, Any], ...], tuple[str, ...], tuple[str, ...]]:
    classified: list[dict[str, Any]] = []
    skipped: list[str] = []
    blocked: list[str] = []
    for record in config.get("normalized_records", []):
        if not isinstance(record, dict):
            blocked.append("normalized record must be an object")
            continue
        asset_id = normalize_text(record.get("asset_id")) or "unknown"
        reasons = validate_normalized_record_for_classification(record)
        if reasons:
            if any(reason.startswith("classification_status") for reason in reasons):
                skipped.append(asset_id)
            else:
                blocked.append(f"{asset_id}: {'; '.join(reasons)}")
            continue
        classified_record = classify_normalized_record(record, config.get("current_date"))
        classified_reasons = validate_classified_record(classified_record)
        if classified_reasons:
            blocked.append(f"{asset_id}: {'; '.join(classified_reasons)}")
            continue
        classified.append(classified_record)
    return tuple(sorted(classified, key=lambda item: item["asset_id"])), tuple(skipped), tuple(blocked)


def evaluate_public_asset_universe_classifier(config: dict[str, Any]) -> PublicAssetUniverseClassifierResult:
    config_blockers = list(validate_classifier_config(config))
    if isinstance(config.get("normalized_records"), list) and not config.get("normalized_records"):
        config_blockers.append("normalized_records must contain at least one record.")
    classified_records, skipped_records, blocked_records = classify_normalized_records(config)
    ids = [record["asset_id"] for record in classified_records]
    duplicate_count = len(ids) - len(set(ids))
    record_blockers = ["duplicate asset_id detected."] if duplicate_count else []
    invalid_count = len(record_blockers)
    blockers = tuple(dict.fromkeys(config_blockers + list(blocked_records) + record_blockers))
    authorized = _authorization_valid(config)
    if config_blockers or (blockers and not classified_records):
        status = "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_BLOCKED_SAFE"
    elif blockers or skipped_records:
        status = "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_PARTIAL_SAFE"
    elif authorized:
        status = "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_READY_TO_WRITE_SAFE"
    else:
        status = "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_READY_SAFE"
    readiness_counts = {
        "READY_FOR_RESEARCH_QUEUE": 0,
        "NEEDS_MORE_PUBLIC_DATA": 0,
        "NEEDS_MANUAL_SOURCE_REVIEW": 0,
        "BLOCKED_BY_MISSING_FIELDS": 0,
    }
    for record in classified_records:
        readiness_counts[record["evidence_readiness_bucket"]] += 1
    return PublicAssetUniverseClassifierResult(
        title=normalize_text(config.get("title")) or "J.A.R.V.I.S. Public Asset Universe Classifier",
        version=normalize_text(config.get("version")) or "v4.67",
        status=status,
        classifier_mode=normalize_text(config.get("classifier_mode")),
        normalized_record_count=len(config.get("normalized_records", [])) if isinstance(config.get("normalized_records"), list) else 0,
        classified_record_count=len(classified_records),
        skipped_record_count=len(skipped_records),
        blocked_record_count=len(blocked_records),
        invalid_record_count=invalid_count,
        duplicate_asset_id_count=duplicate_count,
        ready_for_research_queue_count=readiness_counts["READY_FOR_RESEARCH_QUEUE"],
        needs_more_public_data_count=readiness_counts["NEEDS_MORE_PUBLIC_DATA"],
        needs_manual_source_review_count=readiness_counts["NEEDS_MANUAL_SOURCE_REVIEW"],
        blocked_by_missing_fields_count=readiness_counts["BLOCKED_BY_MISSING_FIELDS"],
        classified_records=classified_records,
        skipped_records=skipped_records,
        blocked_records=tuple(blocked_records),
        warnings=(),
        blockers=blockers,
        next_safe_action=normalize_text(config.get("next_manual_action")),
    )


def _output_root_blockers(path: str | Path) -> tuple[str, ...]:
    text = normalize_text(path)
    if not text:
        return ("classified output root is required.",)
    normalized = text.replace("\\", "/").rstrip("/")
    blocked_roots = {"docs", "templates", "jarvis/data", "."}
    if normalized in blocked_roots or normalized.startswith(("docs/", "templates/", "jarvis/data/")):
        return ("classified output root must not target docs, templates, repo root, or jarvis/data.",)
    return ()


def _path_blockers(path: str | Path, root: str | Path) -> tuple[str, ...]:
    candidate = Path(path).resolve()
    root_path = Path(root).resolve()
    try:
        candidate.relative_to(root_path)
    except ValueError:
        return ("path must stay under the configured classified output root.",)
    return ()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def execute_authorized_classified_cache_write(
    config: dict[str, Any],
    classified_records: tuple[dict[str, Any], ...] | list[dict[str, Any]],
    now: datetime | None = None,
    output_root_override: str | Path | None = None,
) -> dict[str, Any]:
    if not _authorization_valid(config):
        return {"status": "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_BLOCKED_SAFE", "written": False, "blockers": ("authorization phrase invalid.",)}
    output_root = Path(output_root_override) if output_root_override is not None else ALLOWED_OUTPUT_ROOT
    blockers = list(_output_root_blockers(output_root))
    if output_root_override is None:
        blockers.extend(_path_blockers(output_root, ALLOWED_OUTPUT_ROOT))
    for record in classified_records:
        blockers.extend(f"{record.get('asset_id', 'unknown')}: {reason}" for reason in validate_classified_record(record))
    if blockers:
        return {"status": "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_BLOCKED_SAFE", "written": False, "blockers": tuple(dict.fromkeys(blockers))}
    classified_at = (now or datetime.now(timezone.utc)).replace(microsecond=0).isoformat()
    payload = {"classified_at": classified_at, "classified_data_unverified": True, "records": list(classified_records)}
    raw_bytes = (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digest = _sha256_bytes(raw_bytes)
    output_root.mkdir(parents=True, exist_ok=True)
    output_path = output_root / "public_asset_universe.classified.json"
    metadata_path = output_root / "public_asset_universe.classified.metadata.json"
    output_path.write_bytes(raw_bytes)
    metadata = {
        "classified_at": classified_at,
        "record_count": len(classified_records),
        "content_sha256": digest,
        "classified_data_unverified": True,
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
        "status": "PUBLIC_ASSET_UNIVERSE_CLASSIFIER_WRITTEN_LOCAL_CACHE_SAFE",
        "written": True,
        "output_path": str(output_path),
        "metadata_path": str(metadata_path),
        "metadata": metadata,
        "blockers": (),
    }


def render_public_asset_universe_classifier_summary(result: PublicAssetUniverseClassifierResult) -> str:
    return (
        f"status={result.status}; normalized={result.normalized_record_count}; "
        f"classified={result.classified_record_count}; skipped={result.skipped_record_count}; "
        f"blocked={result.blocked_record_count}; ready={result.ready_for_research_queue_count}; "
        f"needs_more={result.needs_more_public_data_count}; manual_review={result.needs_manual_source_review_count}; "
        f"missing_fields={result.blocked_by_missing_fields_count}"
    )


def load_public_asset_universe_classifier_result(path: str | Path) -> PublicAssetUniverseClassifierResult:
    return evaluate_public_asset_universe_classifier(load_json(path))
