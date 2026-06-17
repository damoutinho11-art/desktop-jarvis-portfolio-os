"""J.A.R.V.I.S. v20.0 BTC public signal source-quality gate.

This module reads the normalized BTC public signal produced by v19 and decides
whether the signal is fresh and structurally safe enough for a later scoring
integration stage. It does not update allocation scores, does not regenerate
approval tickets, does not create buy requests, and does not execute trades.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

STATUS_READY = "JARVIS_V20_0_BTC_PUBLIC_SIGNAL_SOURCE_QUALITY_GATE_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V20_0_BTC_PUBLIC_SIGNAL_SOURCE_QUALITY_GATE_BLOCKED_SAFE"
QUALITY_READY = "BTC_PUBLIC_SIGNAL_SOURCE_QUALITY_READY"
QUALITY_BLOCKED = "BTC_PUBLIC_SIGNAL_SOURCE_QUALITY_BLOCKED"

DEFAULT_SIGNAL_DIRECTORY = "jarvis/local/public_data/v19_normalized"
DEFAULT_SOURCE_ID = "coingecko_btc_simple_price_eur"
DEFAULT_CANDIDATE_ID = "btc"
DEFAULT_MAX_SIGNAL_AGE_DAYS = 1
MIN_PRICE_EUR = 1000.0
MAX_PRICE_EUR = 1000000.0
MAX_ABS_CHANGE_24H_PCT = 50.0


@dataclass(frozen=True)
class BtcPublicSignalQualityResult:
    status: str
    quality_status: str
    signal_directory: str
    signal_file_found: bool
    selected_signal_file: str
    current_date: str
    max_signal_age_days: int
    signal_age_days: int | None
    source_quality_ready: bool
    candidate_id: str
    source_id: str
    as_of: str
    price_eur: float | None
    market_cap_eur: float | None
    volume_24h_eur: float | None
    change_24h_pct: float | None
    provider_last_updated_utc: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    recommendation_quality_current_data: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "quality_status": self.quality_status,
            "signal_directory": self.signal_directory,
            "signal_file_found": self.signal_file_found,
            "selected_signal_file": self.selected_signal_file,
            "current_date": self.current_date,
            "max_signal_age_days": self.max_signal_age_days,
            "signal_age_days": self.signal_age_days,
            "source_quality_ready": self.source_quality_ready,
            "candidate_id": self.candidate_id,
            "source_id": self.source_id,
            "as_of": self.as_of,
            "price_eur": self.price_eur,
            "market_cap_eur": self.market_cap_eur,
            "volume_24h_eur": self.volume_24h_eur,
            "change_24h_pct": self.change_24h_pct,
            "provider_last_updated_utc": self.provider_last_updated_utc,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
        }


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_source_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return safe or DEFAULT_SOURCE_ID


def _is_under_jarvis_local(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    local_root = (root / "jarvis" / "local").resolve()
    try:
        resolved.relative_to(local_root)
        return True
    except ValueError:
        return False


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _today_iso() -> str:
    return date.today().isoformat()


def _dedupe(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))


def find_latest_btc_normalized_signal_file(
    signal_directory: str | Path = DEFAULT_SIGNAL_DIRECTORY,
    *,
    source_id: str = DEFAULT_SOURCE_ID,
    root: str | Path = ".",
) -> Path | None:
    root_path = Path(root)
    signal_path = root_path / signal_directory
    if not signal_path.is_dir():
        return None
    safe_source_id = _safe_source_id(source_id)
    candidates = sorted(
        signal_path.glob(f"*_{safe_source_id}.normalized.json"),
        key=lambda item: (item.name, item.stat().st_mtime),
    )
    return candidates[-1] if candidates else None


def _blocked_result(
    *,
    signal_directory: str | Path,
    root: str | Path,
    current_date: str,
    max_signal_age_days: int,
    blockers: list[str],
    warnings: list[str] | None = None,
    selected_signal_file: str = "",
) -> BtcPublicSignalQualityResult:
    root_path = Path(root)
    return BtcPublicSignalQualityResult(
        status=STATUS_BLOCKED,
        quality_status=QUALITY_BLOCKED,
        signal_directory=str(root_path / signal_directory),
        signal_file_found=bool(selected_signal_file),
        selected_signal_file=selected_signal_file,
        current_date=current_date,
        max_signal_age_days=max_signal_age_days,
        signal_age_days=None,
        source_quality_ready=False,
        candidate_id=DEFAULT_CANDIDATE_ID,
        source_id=DEFAULT_SOURCE_ID,
        as_of="",
        price_eur=None,
        market_cap_eur=None,
        volume_24h_eur=None,
        change_24h_pct=None,
        provider_last_updated_utc="",
        blockers=_dedupe(blockers),
        warnings=_dedupe(warnings or []),
        recommendation_quality_current_data=False,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
    )


def build_btc_public_signal_source_quality_gate_result(
    *,
    signal_directory: str | Path = DEFAULT_SIGNAL_DIRECTORY,
    source_id: str = DEFAULT_SOURCE_ID,
    root: str | Path = ".",
    current_date: str | None = None,
    max_signal_age_days: int = DEFAULT_MAX_SIGNAL_AGE_DAYS,
) -> BtcPublicSignalQualityResult:
    root_path = Path(root)
    current_date_text = current_date or _today_iso()
    signal_path = root_path / signal_directory
    blockers: list[str] = []
    warnings: list[str] = []

    if max_signal_age_days < 0:
        blockers.append("max_signal_age_days must be non-negative.")

    if not _is_under_jarvis_local(signal_path, root_path):
        blockers.append("signal_directory must be under ignored jarvis/local.")
        return _blocked_result(
            signal_directory=signal_directory,
            root=root_path,
            current_date=current_date_text,
            max_signal_age_days=max_signal_age_days,
            blockers=blockers,
            warnings=warnings,
        )

    selected = find_latest_btc_normalized_signal_file(signal_directory, source_id=source_id, root=root_path)
    if selected is None:
        blockers.append(f"No normalized BTC public signal found in {signal_path} for source {source_id}.")
        return _blocked_result(
            signal_directory=signal_directory,
            root=root_path,
            current_date=current_date_text,
            max_signal_age_days=max_signal_age_days,
            blockers=blockers,
            warnings=warnings,
        )

    try:
        payload = json.loads(selected.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001 - public local cache must fail closed.
        blockers.append(f"normalized BTC public signal is not valid JSON: {exc.__class__.__name__}: {_text(exc)}")
        return _blocked_result(
            signal_directory=signal_directory,
            root=root_path,
            current_date=current_date_text,
            max_signal_age_days=max_signal_age_days,
            blockers=blockers,
            warnings=warnings,
            selected_signal_file=str(selected),
        )

    if not isinstance(payload, dict):
        blockers.append("normalized BTC public signal must be a JSON object.")
        return _blocked_result(
            signal_directory=signal_directory,
            root=root_path,
            current_date=current_date_text,
            max_signal_age_days=max_signal_age_days,
            blockers=blockers,
            warnings=warnings,
            selected_signal_file=str(selected),
        )

    candidate_id = _text(payload.get("candidate_id"))
    source_id_value = _text(payload.get("source_id"))
    as_of = _text(payload.get("as_of"))
    price_eur = _float(payload.get("price_eur"))
    market_cap_eur = _float(payload.get("market_cap_eur"))
    volume_24h_eur = _float(payload.get("volume_24h_eur"))
    change_24h_pct = _float(payload.get("change_24h_pct"))
    provider_last_updated_utc = _text(payload.get("provider_last_updated_utc"))

    if candidate_id != DEFAULT_CANDIDATE_ID:
        blockers.append("normalized signal candidate_id must be btc.")
    if source_id_value != source_id:
        blockers.append(f"normalized signal source_id must be {source_id}.")
    if payload.get("normalized_public_signal") is not True:
        blockers.append("normalized_public_signal must be true.")
    if payload.get("ready_for_source_quality_gate") is not True:
        blockers.append("ready_for_source_quality_gate must be true.")
    if payload.get("raw_data_unverified") is not True:
        warnings.append("raw_data_unverified should remain true before later trust/scoring integration.")

    current_day = _parse_date(current_date_text)
    as_of_day = _parse_date(as_of)
    signal_age_days: int | None = None
    if current_day is None:
        blockers.append("current_date must use YYYY-MM-DD format.")
    if as_of_day is None:
        blockers.append("normalized signal as_of must use YYYY-MM-DD format.")
    if current_day is not None and as_of_day is not None:
        signal_age_days = (current_day - as_of_day).days
        if signal_age_days < 0:
            blockers.append("normalized signal as_of cannot be in the future.")
        if signal_age_days > max_signal_age_days:
            blockers.append(
                f"normalized BTC public signal is stale: age {signal_age_days} days exceeds max {max_signal_age_days} days."
            )

    if price_eur is None or price_eur < MIN_PRICE_EUR or price_eur > MAX_PRICE_EUR:
        blockers.append(
            f"BTC price_eur must be between {MIN_PRICE_EUR:,.0f} and {MAX_PRICE_EUR:,.0f}."
        )
    if market_cap_eur is None or market_cap_eur <= 0:
        blockers.append("BTC market_cap_eur must be positive.")
    if volume_24h_eur is None or volume_24h_eur <= 0:
        blockers.append("BTC volume_24h_eur must be positive.")
    if change_24h_pct is None:
        blockers.append("BTC change_24h_pct must be numeric.")
    elif abs(change_24h_pct) > MAX_ABS_CHANGE_24H_PCT:
        blockers.append(
            f"BTC absolute 24h change exceeds sanity limit: {change_24h_pct:.4f}% vs {MAX_ABS_CHANGE_24H_PCT:.2f}%."
        )

    if provider_last_updated_utc:
        try:
            datetime.fromisoformat(provider_last_updated_utc.replace("Z", "+00:00"))
        except ValueError:
            blockers.append("provider_last_updated_utc must be ISO-8601 parseable.")
    else:
        blockers.append("provider_last_updated_utc is required.")

    source_quality_ready = not blockers
    return BtcPublicSignalQualityResult(
        status=STATUS_READY if source_quality_ready else STATUS_BLOCKED,
        quality_status=QUALITY_READY if source_quality_ready else QUALITY_BLOCKED,
        signal_directory=str(signal_path),
        signal_file_found=True,
        selected_signal_file=str(selected),
        current_date=current_date_text,
        max_signal_age_days=max_signal_age_days,
        signal_age_days=signal_age_days,
        source_quality_ready=source_quality_ready,
        candidate_id=candidate_id,
        source_id=source_id_value,
        as_of=as_of,
        price_eur=price_eur,
        market_cap_eur=market_cap_eur,
        volume_24h_eur=volume_24h_eur,
        change_24h_pct=change_24h_pct,
        provider_last_updated_utc=provider_last_updated_utc,
        blockers=_dedupe(blockers),
        warnings=_dedupe(warnings),
        recommendation_quality_current_data=False,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
    )


def format_btc_public_signal_source_quality_gate(result: BtcPublicSignalQualityResult) -> str:
    lines = [
        "J.A.R.V.I.S. BTC Public Signal Source-Quality Gate",
        f"status: {result.status}",
        f"quality status: {result.quality_status}",
        f"source quality ready: {result.source_quality_ready}",
        f"signal file found: {result.signal_file_found}",
        f"selected signal file: {result.selected_signal_file or 'none'}",
        f"current date: {result.current_date}",
        f"max signal age days: {result.max_signal_age_days}",
        f"signal age days: {result.signal_age_days if result.signal_age_days is not None else 'unknown'}",
        f"candidate: {result.candidate_id or 'none'}",
        f"source: {result.source_id or 'none'}",
        f"as_of: {result.as_of or 'none'}",
        f"price_eur: {result.price_eur:,.2f}" if result.price_eur is not None else "price_eur: none",
        f"market_cap_eur: {result.market_cap_eur:,.2f}" if result.market_cap_eur is not None else "market_cap_eur: none",
        f"volume_24h_eur: {result.volume_24h_eur:,.2f}" if result.volume_24h_eur is not None else "volume_24h_eur: none",
        f"change_24h_pct: {result.change_24h_pct:.4f}" if result.change_24h_pct is not None else "change_24h_pct: none",
        f"provider_last_updated_utc: {result.provider_last_updated_utc or 'none'}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
    ]
    if result.blockers:
        lines.extend(["", "Blockers:"])
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("blockers: none")
    if result.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("warnings: none")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Quality-gate normalized BTC public signal data.")
    parser.add_argument("--signal-directory", default=DEFAULT_SIGNAL_DIRECTORY)
    parser.add_argument("--source-id", default=DEFAULT_SOURCE_ID)
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--max-signal-age-days", type=int, default=DEFAULT_MAX_SIGNAL_AGE_DAYS)
    args = parser.parse_args(argv)
    result = build_btc_public_signal_source_quality_gate_result(
        signal_directory=args.signal_directory,
        source_id=args.source_id,
        current_date=args.current_date,
        max_signal_age_days=args.max_signal_age_days,
    )
    print(format_btc_public_signal_source_quality_gate(result))
    return 0 if result.status == STATUS_READY else 1


if __name__ == "__main__":
    raise SystemExit(main())