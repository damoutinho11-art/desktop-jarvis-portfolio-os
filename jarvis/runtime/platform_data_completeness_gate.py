"""J.A.R.V.I.S. v57.0 Platform Data Completeness + Instrument Intake Gate.

Blocks trusted weekly action language until platform-specific local intake data
exists and is manually confirmed.

Safety invariant:
Automated research. Manual trust. Manual approval. No execution.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping

STATUS_READY = "JARVIS_V57_0_PLATFORM_DATA_COMPLETENESS_GATE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V57_0_PLATFORM_DATA_COMPLETENESS_GATE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V57_0_PLATFORM_DATA_COMPLETENESS_GATE_BLOCKED_SAFE"

GATE_READY = "PLATFORM_DATA_COMPLETENESS_GATE_TRUSTED_WEEKLY_ACTION_READY"
GATE_REVIEW_REQUIRED = "PLATFORM_DATA_COMPLETENESS_GATE_REVIEW_REQUIRED"
GATE_TEMPLATE_WRITTEN = "PLATFORM_DATA_COMPLETENESS_TEMPLATES_WRITTEN_REVIEW_REQUIRED"
GATE_BLOCKED = "PLATFORM_DATA_COMPLETENESS_GATE_BLOCKED"

NEXT_STAGE = "fill_platform_instrument_and_facility_terms_intake"

DEFAULT_LIGHTYEAR_INSTRUMENT_UNIVERSE_PATH = "jarvis/local/lightyear_instrument_universe.local.json"
DEFAULT_CRYPTO_FACILITY_TERMS_PATH = "jarvis/local/crypto_facility_terms.local.json"
DEFAULT_LEGACY_MIGRATION_REVIEW_PATH = "jarvis/local/legacy_migration_review.local.json"

FORBIDDEN_KEY_FRAGMENTS = (
    "password",
    "passwd",
    "api_key",
    "apikey",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "private_key",
    "broker_credentials",
    "credential",
    "client_secret",
)


@dataclass(frozen=True)
class PlatformDataFileStatus:
    key: str
    path: str
    present: bool
    loaded: bool
    is_template: bool
    confirmed: bool
    forbidden_credential_keys_found: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class CryptoFacilityCandidate:
    facility_id: str
    display_name: str
    candidate_available: bool
    approved_by_default: bool
    manual_only: bool
    requires_terms_intake: bool
    notes: str


@dataclass(frozen=True)
class PlatformDataCompletenessGateResult:
    status: str
    gate_status: str
    recommended_next_stage: str
    current_date: str
    template_write_requested: bool
    templates_written: tuple[str, ...]
    structural_weekly_packet_available: bool
    trusted_weekly_action_allowed: bool
    full_allocation_allowed: bool
    lightyear_instrument_universe_confirmed: bool
    crypto_facility_terms_confirmed: bool
    legacy_migration_review_confirmed: bool
    data_files: tuple[PlatformDataFileStatus, ...]
    crypto_candidates: tuple[CryptoFacilityCandidate, ...]
    blockers: tuple[str, ...]
    full_allocation_blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    allocation_mutation: bool
    approval_ticket_mutation: bool
    evidence_pack_mutation: bool
    local_cache_mutation: bool
    portfolio_state_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    auto_approval_forbidden: bool
    auto_selling_forbidden: bool


def _today() -> str:
    return date.today().isoformat()


def _dedupe(items: Any) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _load_json(path: Path) -> Mapping[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


def _find_forbidden_keys(payload: Any, prefix: str = "") -> tuple[str, ...]:
    found: list[str] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_text = str(key)
            current = f"{prefix}.{key_text}" if prefix else key_text
            if any(fragment in key_text.lower() for fragment in FORBIDDEN_KEY_FRAGMENTS):
                found.append(current)
            found.extend(_find_forbidden_keys(value, current))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            found.extend(_find_forbidden_keys(value, f"{prefix}[{index}]"))
    return _dedupe(found)


def build_lightyear_instrument_universe_template(*, current_date: str | None = None) -> dict[str, Any]:
    return {
        "schema": "JARVIS_LIGHTYEAR_INSTRUMENT_UNIVERSE_V1",
        "as_of": current_date or _today(),
        "is_template": True,
        "platform": "Lightyear",
        "platform_data_confirmed": False,
        "broker_api_used": False,
        "sensitive_private_fields_included": False,
        "instruments": [
            {
                "instrument_id": "example_is3q_de",
                "symbol": "IS3Q.DE",
                "isin": "IE00BP3QZ601",
                "name": "example only - replace with confirmed Lightyear data",
                "asset_class": "ETF",
                "currency": "EUR",
                "tradable_confirmed_on_lightyear": False,
                "platform_instrument_id_confirmed": False,
                "notes": "Example row only; does not count as confirmed data.",
            }
        ],
        "notes": [
            "Keep local and ignored.",
            "Do not add passwords, API keys, tokens, broker credentials, or private account exports.",
            "This does not approve or execute purchases.",
        ],
    }


def build_crypto_facility_terms_template(*, current_date: str | None = None) -> dict[str, Any]:
    return {
        "schema": "JARVIS_CRYPTO_FACILITY_TERMS_V1",
        "as_of": current_date or _today(),
        "is_template": True,
        "terms_confirmed": False,
        "facilities": [
            {
                "facility_id": "lhv",
                "display_name": "LHV",
                "candidate": True,
                "approved": False,
                "manual_only": True,
                "terms_confirmed": False,
                "notes": "Candidate facility; not approved by default.",
            },
            {
                "facility_id": "kraken",
                "display_name": "Kraken",
                "candidate": True,
                "approved": False,
                "manual_only": True,
                "terms_confirmed": False,
                "notes": "Candidate facility; not approved by default.",
            },
            {
                "facility_id": "other_manual_facility",
                "display_name": "other_manual_facility",
                "candidate": True,
                "approved": False,
                "manual_only": True,
                "terms_confirmed": False,
                "notes": "Placeholder for a future manually reviewed facility.",
            },
        ],
        "notes": [
            "Keep local and ignored.",
            "Do not add passwords, API keys, tokens, broker credentials, or private account exports.",
            "Kraken and LHV are candidates only, not approved by default.",
        ],
    }


def build_legacy_migration_review_template(*, current_date: str | None = None) -> dict[str, Any]:
    return {
        "schema": "JARVIS_LEGACY_MIGRATION_REVIEW_V1",
        "as_of": current_date or _today(),
        "is_template": True,
        "legacy_migration_review_confirmed": False,
        "legacy_positions_reviewed": False,
        "legacy_sell_allowed": False,
        "manual_only": True,
        "notes": [
            "Keep local and ignored.",
            "Do not add broker credentials, tokens, or private account exports.",
            "This must not trigger automatic selling, orders, or portfolio mutation.",
        ],
    }


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> str:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(file_path)


def _lightyear_confirmed(payload: Mapping[str, Any]) -> bool:
    if payload.get("is_template") is True or payload.get("platform_data_confirmed") is not True:
        return False
    instruments = payload.get("instruments")
    if not isinstance(instruments, list):
        return False
    return any(
        isinstance(item, Mapping)
        and (
            item.get("tradable_confirmed_on_lightyear") is True
            or item.get("platform_instrument_id_confirmed") is True
        )
        for item in instruments
    )


def _crypto_confirmed(payload: Mapping[str, Any]) -> bool:
    if payload.get("is_template") is True or payload.get("terms_confirmed") is not True:
        return False
    facilities = payload.get("facilities")
    if not isinstance(facilities, list):
        return False
    return any(isinstance(item, Mapping) and item.get("terms_confirmed") is True for item in facilities)


def _legacy_confirmed(payload: Mapping[str, Any]) -> bool:
    return (
        payload.get("is_template") is not True
        and payload.get("legacy_migration_review_confirmed") is True
        and payload.get("legacy_positions_reviewed") is True
    )


def _inspect_file(
    *,
    key: str,
    path: str | Path,
    missing_blocker: str,
    not_confirmed_blocker: str,
    invalid_blocker: str,
    checker: Any,
) -> PlatformDataFileStatus:
    file_path = Path(path)
    payload = _load_json(file_path)
    present = file_path.exists()
    loaded = payload is not None
    is_template = bool(payload.get("is_template", False)) if payload else False
    forbidden = _find_forbidden_keys(payload) if payload else ()

    blockers: list[str] = []
    warnings: list[str] = []

    if forbidden:
        blockers.append(f"{key} contains forbidden credential-like keys")
    if not present:
        blockers.append(missing_blocker)
    elif not loaded:
        blockers.append(invalid_blocker)
    elif is_template or not checker(payload):
        blockers.append(not_confirmed_blocker)
    else:
        warnings.append(f"{key} manually confirmed; still no execution or auto-approval")

    confirmed = present and loaded and not is_template and not forbidden and not blockers

    return PlatformDataFileStatus(
        key=key,
        path=str(file_path),
        present=present,
        loaded=loaded,
        is_template=is_template,
        confirmed=confirmed,
        forbidden_credential_keys_found=forbidden,
        blockers=_dedupe(blockers),
        warnings=_dedupe(warnings),
    )


def _crypto_candidates() -> tuple[CryptoFacilityCandidate, ...]:
    return (
        CryptoFacilityCandidate("lhv", "LHV", True, False, True, True, "Candidate crypto facility; not approved by default."),
        CryptoFacilityCandidate("kraken", "Kraken", True, False, True, True, "Candidate crypto facility; not approved by default."),
        CryptoFacilityCandidate(
            "other_manual_facility",
            "other_manual_facility",
            True,
            False,
            True,
            True,
            "Future manually reviewed crypto facility placeholder.",
        ),
    )


def build_platform_data_completeness_gate_result(
    *,
    current_date: str | None = None,
    lightyear_instrument_universe_path: str | Path = DEFAULT_LIGHTYEAR_INSTRUMENT_UNIVERSE_PATH,
    crypto_facility_terms_path: str | Path = DEFAULT_CRYPTO_FACILITY_TERMS_PATH,
    legacy_migration_review_path: str | Path = DEFAULT_LEGACY_MIGRATION_REVIEW_PATH,
    write_platform_data_templates: bool = False,
) -> PlatformDataCompletenessGateResult:
    current_date_text = current_date or _today()
    templates_written: list[str] = []

    if write_platform_data_templates:
        templates_written.append(
            _write_json(
                lightyear_instrument_universe_path,
                build_lightyear_instrument_universe_template(current_date=current_date_text),
            )
        )
        templates_written.append(
            _write_json(
                crypto_facility_terms_path,
                build_crypto_facility_terms_template(current_date=current_date_text),
            )
        )
        templates_written.append(
            _write_json(
                legacy_migration_review_path,
                build_legacy_migration_review_template(current_date=current_date_text),
            )
        )

    lightyear = _inspect_file(
        key="lightyear_instrument_universe",
        path=lightyear_instrument_universe_path,
        missing_blocker="missing_lightyear_instrument_universe",
        not_confirmed_blocker="lightyear_instrument_universe_not_confirmed",
        invalid_blocker="lightyear_instrument_universe_invalid_json",
        checker=_lightyear_confirmed,
    )
    crypto = _inspect_file(
        key="crypto_facility_terms",
        path=crypto_facility_terms_path,
        missing_blocker="missing_crypto_facility_terms",
        not_confirmed_blocker="crypto_facility_terms_not_confirmed",
        invalid_blocker="crypto_facility_terms_invalid_json",
        checker=_crypto_confirmed,
    )
    legacy = _inspect_file(
        key="legacy_migration_review",
        path=legacy_migration_review_path,
        missing_blocker="missing_legacy_migration_review",
        not_confirmed_blocker="legacy_migration_review_not_confirmed",
        invalid_blocker="legacy_migration_review_invalid_json",
        checker=_legacy_confirmed,
    )

    blockers = _dedupe([*lightyear.blockers, *crypto.blockers])
    full_allocation_blockers = _dedupe(
        [
            *lightyear.blockers,
            *crypto.blockers,
            *legacy.blockers,
            "legacy_migration_review",
            "correlation_risk_model",
            "stock_specific_public_evidence",
        ]
    )
    trusted_allowed = lightyear.confirmed and crypto.confirmed and not blockers

    if trusted_allowed:
        status = STATUS_REVIEW_REQUIRED
        gate_status = GATE_READY
    elif write_platform_data_templates:
        status = STATUS_REVIEW_REQUIRED
        gate_status = GATE_TEMPLATE_WRITTEN
    elif blockers:
        status = STATUS_BLOCKED
        gate_status = GATE_BLOCKED
    else:
        status = STATUS_REVIEW_REQUIRED
        gate_status = GATE_REVIEW_REQUIRED

    return PlatformDataCompletenessGateResult(
        status=status,
        gate_status=gate_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        template_write_requested=write_platform_data_templates,
        templates_written=_dedupe(templates_written),
        structural_weekly_packet_available=True,
        trusted_weekly_action_allowed=trusted_allowed,
        full_allocation_allowed=False,
        lightyear_instrument_universe_confirmed=lightyear.confirmed,
        crypto_facility_terms_confirmed=crypto.confirmed,
        legacy_migration_review_confirmed=legacy.confirmed,
        data_files=(lightyear, crypto, legacy),
        crypto_candidates=_crypto_candidates(),
        blockers=blockers,
        full_allocation_blockers=full_allocation_blockers,
        warnings=_dedupe([*lightyear.warnings, *crypto.warnings, *legacy.warnings]),
        allocation_mutation=False,
        approval_ticket_mutation=False,
        evidence_pack_mutation=False,
        local_cache_mutation=False,
        portfolio_state_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        auto_approval_forbidden=True,
        auto_selling_forbidden=True,
    )


def format_platform_data_completeness_gate(result: PlatformDataCompletenessGateResult) -> str:
    lines = [
        "J.A.R.V.I.S. PLATFORM DATA COMPLETENESS + INSTRUMENT INTAKE GATE",
        f"status: {result.status}",
        f"gate status: {result.gate_status}",
        f"current date: {result.current_date}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"template write requested: {result.template_write_requested}",
        f"structural weekly packet available: {result.structural_weekly_packet_available}",
        f"trusted weekly action allowed: {result.trusted_weekly_action_allowed}",
        f"full allocation allowed: {result.full_allocation_allowed}",
        "",
        "Platform intake files:",
    ]

    for item in result.data_files:
        lines.append(
            f"- {item.key}: present={item.present}; loaded={item.loaded}; "
            f"template={item.is_template}; confirmed={item.confirmed}; path={item.path}"
        )

    lines.extend(["", "Crypto facility candidates:"])
    for candidate in result.crypto_candidates:
        lines.append(
            f"- {candidate.display_name} ({candidate.facility_id}): "
            f"candidate={candidate.candidate_available}; approved by default={candidate.approved_by_default}; "
            f"manual only={candidate.manual_only}; terms intake required={candidate.requires_terms_intake}"
        )
        lines.append(f"  note: {candidate.notes}")

    if result.templates_written:
        lines.extend(["", "Templates written:"])
        lines.extend(f"- {path}" for path in result.templates_written)

    lines.extend(
        [
            "",
            "Safety:",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
            f"- evidence pack mutation: {result.evidence_pack_mutation}",
            f"- local cache mutation: {result.local_cache_mutation}",
            f"- portfolio state mutation: {result.portfolio_state_mutation}",
            f"- buy request created: {result.buy_request_created}",
            f"- auto approval forbidden: {result.auto_approval_forbidden}",
            f"- auto selling forbidden: {result.auto_selling_forbidden}",
            "- no broker APIs",
            "- no credentials",
            "- no private account ingestion",
            "- no orders created",
            "- no trades executed",
        ]
    )

    if result.blockers:
        lines.extend(["", "Blockers:"])
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("blockers: none")

    if result.full_allocation_blockers:
        lines.extend(["", "Full allocation blockers:"])
        lines.extend(f"- {blocker}" for blocker in result.full_allocation_blockers)
    else:
        lines.append("full allocation blockers: none")

    if result.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("warnings: none")

    return "\n".join(lines)


def _safety_check_output() -> str:
    return "\n".join(
        [
            "J.A.R.V.I.S. SAFETY CHECK",
            "status: SAFETY_CHECK_READY_SAFE",
            "blocked prompt: Jarvis, buy BTC now.",
            "decision: EXECUTION_FORBIDDEN",
            "reason: Automated research only; manual trust, manual approval, no execution.",
            "buy request created: False",
            "broker connection: False",
            "order created: False",
            "trade executed: False",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. v57 platform data completeness gate.")
    parser.add_argument("--platform-data-completeness-gate", action="store_true")
    parser.add_argument("--write-platform-data-templates", action="store_true")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--lightyear-instrument-universe-path", default=DEFAULT_LIGHTYEAR_INSTRUMENT_UNIVERSE_PATH)
    parser.add_argument("--crypto-facility-terms-path", default=DEFAULT_CRYPTO_FACILITY_TERMS_PATH)
    parser.add_argument("--legacy-migration-review-path", default=DEFAULT_LEGACY_MIGRATION_REVIEW_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(_safety_check_output())
        return 0

    result = build_platform_data_completeness_gate_result(
        current_date=args.current_date,
        lightyear_instrument_universe_path=args.lightyear_instrument_universe_path,
        crypto_facility_terms_path=args.crypto_facility_terms_path,
        legacy_migration_review_path=args.legacy_migration_review_path,
        write_platform_data_templates=args.write_platform_data_templates,
    )
    print(format_platform_data_completeness_gate(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
