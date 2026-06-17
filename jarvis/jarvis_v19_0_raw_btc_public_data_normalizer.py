"""J.A.R.V.I.S. v19.0 raw BTC public data normalizer.

This module parses raw, unverified public BTC market data fetched through the
v10 public-data boundary and turns it into a local normalized candidate signal.
It does not update allocation scores, does not create buy requests, and does
not execute trades.
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATUS_READY = "JARVIS_V19_0_RAW_BTC_PUBLIC_DATA_NORMALIZER_READY_SAFE"
STATUS_BLOCKED = "JARVIS_V19_0_RAW_BTC_PUBLIC_DATA_NORMALIZER_BLOCKED_SAFE"
NORMALIZER_READY = "RAW_BTC_PUBLIC_DATA_NORMALIZER_READY"
NORMALIZER_BLOCKED = "RAW_BTC_PUBLIC_DATA_NORMALIZER_BLOCKED"
DEFAULT_RAW_DIRECTORY = "jarvis/local/public_data/v10_raw"
DEFAULT_NORMALIZED_DIRECTORY = "jarvis/local/public_data/v19_normalized"
DEFAULT_SOURCE_ID = "coingecko_btc_simple_price_eur"


@dataclass(frozen=True)
class BtcMarketSignal:
    candidate_id: str
    source_id: str
    source_file: str
    as_of: str
    price_eur: float
    market_cap_eur: float
    volume_24h_eur: float
    change_24h_pct: float
    provider_last_updated_at: int
    provider_last_updated_utc: str
    raw_data_unverified: bool
    normalized_public_signal: bool
    ready_for_source_quality_gate: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "source_id": self.source_id,
            "source_file": self.source_file,
            "as_of": self.as_of,
            "price_eur": self.price_eur,
            "market_cap_eur": self.market_cap_eur,
            "volume_24h_eur": self.volume_24h_eur,
            "change_24h_pct": self.change_24h_pct,
            "provider_last_updated_at": self.provider_last_updated_at,
            "provider_last_updated_utc": self.provider_last_updated_utc,
            "raw_data_unverified": self.raw_data_unverified,
            "normalized_public_signal": self.normalized_public_signal,
            "ready_for_source_quality_gate": self.ready_for_source_quality_gate,
        }


@dataclass(frozen=True)
class RawBtcPublicDataNormalizerResult:
    status: str
    normalizer_status: str
    raw_directory: str
    normalized_directory: str
    raw_file_found: bool
    selected_raw_file: str
    source_id: str
    candidate_id: str
    signal_ready: bool
    signal_written: bool
    normalized_signal_file: str
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    btc_signal: BtcMarketSignal | None
    recommendation_quality_current_data: bool
    allocation_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    raw_data_unverified: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "normalizer_status": self.normalizer_status,
            "raw_directory": self.raw_directory,
            "normalized_directory": self.normalized_directory,
            "raw_file_found": self.raw_file_found,
            "selected_raw_file": self.selected_raw_file,
            "source_id": self.source_id,
            "candidate_id": self.candidate_id,
            "signal_ready": self.signal_ready,
            "signal_written": self.signal_written,
            "normalized_signal_file": self.normalized_signal_file,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "btc_signal": self.btc_signal.to_dict() if self.btc_signal else None,
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "allocation_mutation": self.allocation_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "raw_data_unverified": self.raw_data_unverified,
        }


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number


def _int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number


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


def _as_utc_timestamp(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(microsecond=0).isoformat()


def _extract_as_of_from_filename(path: Path) -> str:
    match = re.match(r"^(\d{4}-\d{2}-\d{2})_", path.name)
    return match.group(1) if match else "unknown"


def find_latest_raw_btc_file(
    raw_directory: str | Path = DEFAULT_RAW_DIRECTORY,
    *,
    source_id: str = DEFAULT_SOURCE_ID,
    root: str | Path = ".",
) -> Path | None:
    root_path = Path(root)
    raw_path = root_path / raw_directory
    if not raw_path.is_dir():
        return None
    safe_source_id = _safe_source_id(source_id)
    candidates = sorted(
        raw_path.glob(f"*_{safe_source_id}.json.raw"),
        key=lambda item: (item.name, item.stat().st_mtime),
    )
    return candidates[-1] if candidates else None


def normalize_coingecko_btc_raw(
    raw_file: str | Path,
    *,
    source_id: str = DEFAULT_SOURCE_ID,
) -> tuple[BtcMarketSignal | None, tuple[str, ...], tuple[str, ...]]:
    path = Path(raw_file)
    blockers: list[str] = []
    warnings: list[str] = []
    try:
        raw = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001 - raw public data must fail closed.
        return None, (f"raw BTC public data is not valid JSON: {exc.__class__.__name__}: {_text(exc)}",), tuple(warnings)

    if not isinstance(raw, dict):
        return None, ("raw BTC public data must be a JSON object.",), tuple(warnings)
    bitcoin = raw.get("bitcoin")
    if not isinstance(bitcoin, dict):
        return None, ("raw BTC public data must contain a bitcoin object.",), tuple(warnings)

    price_eur = _float(bitcoin.get("eur"))
    market_cap_eur = _float(bitcoin.get("eur_market_cap"))
    volume_24h_eur = _float(bitcoin.get("eur_24h_vol"))
    change_24h_pct = _float(bitcoin.get("eur_24h_change"))
    provider_last_updated_at = _int(bitcoin.get("last_updated_at"))

    if price_eur is None or price_eur <= 0:
        blockers.append("BTC EUR price must be a positive number.")
    if market_cap_eur is None or market_cap_eur < 0:
        blockers.append("BTC EUR market cap must be a non-negative number.")
    if volume_24h_eur is None or volume_24h_eur < 0:
        blockers.append("BTC 24h EUR volume must be a non-negative number.")
    if change_24h_pct is None:
        blockers.append("BTC 24h EUR change percentage must be numeric.")
    if provider_last_updated_at is None or provider_last_updated_at <= 0:
        blockers.append("BTC provider last_updated_at must be a positive Unix timestamp.")

    as_of = _extract_as_of_from_filename(path)
    if as_of == "unknown":
        warnings.append("raw BTC filename does not include an as_of date prefix.")

    if blockers:
        return None, tuple(blockers), tuple(warnings)

    assert price_eur is not None
    assert market_cap_eur is not None
    assert volume_24h_eur is not None
    assert change_24h_pct is not None
    assert provider_last_updated_at is not None
    return (
        BtcMarketSignal(
            candidate_id="btc",
            source_id=source_id,
            source_file=str(path),
            as_of=as_of,
            price_eur=round(price_eur, 8),
            market_cap_eur=round(market_cap_eur, 8),
            volume_24h_eur=round(volume_24h_eur, 8),
            change_24h_pct=round(change_24h_pct, 8),
            provider_last_updated_at=provider_last_updated_at,
            provider_last_updated_utc=_as_utc_timestamp(provider_last_updated_at),
            raw_data_unverified=True,
            normalized_public_signal=True,
            ready_for_source_quality_gate=True,
        ),
        tuple(blockers),
        tuple(warnings),
    )


def build_raw_btc_public_data_normalizer_result(
    *,
    raw_directory: str | Path = DEFAULT_RAW_DIRECTORY,
    normalized_directory: str | Path = DEFAULT_NORMALIZED_DIRECTORY,
    source_id: str = DEFAULT_SOURCE_ID,
    root: str | Path = ".",
    write_local_signal: bool = False,
) -> RawBtcPublicDataNormalizerResult:
    root_path = Path(root)
    raw_path = root_path / raw_directory
    normalized_path = root_path / normalized_directory
    blockers: list[str] = []
    warnings: list[str] = []

    selected = find_latest_raw_btc_file(raw_directory, source_id=source_id, root=root_path)
    if selected is None:
        blockers.append(f"No raw BTC public data file found in {raw_path} for source {source_id}.")
        return RawBtcPublicDataNormalizerResult(
            status=STATUS_BLOCKED,
            normalizer_status=NORMALIZER_BLOCKED,
            raw_directory=str(raw_path),
            normalized_directory=str(normalized_path),
            raw_file_found=False,
            selected_raw_file="",
            source_id=source_id,
            candidate_id="btc",
            signal_ready=False,
            signal_written=False,
            normalized_signal_file="",
            blockers=tuple(blockers),
            warnings=tuple(warnings),
            btc_signal=None,
            recommendation_quality_current_data=False,
            allocation_mutation=False,
            buy_request_created=False,
            broker_connection_forbidden=True,
            credentials_forbidden=True,
            private_account_data_ingestion_forbidden=True,
            order_creation_forbidden=True,
            no_trades_executed=True,
            raw_data_unverified=True,
        )

    signal, signal_blockers, signal_warnings = normalize_coingecko_btc_raw(selected, source_id=source_id)
    blockers.extend(signal_blockers)
    warnings.extend(signal_warnings)

    normalized_signal_file = ""
    signal_written = False
    if signal and write_local_signal:
        if not _is_under_jarvis_local(normalized_path, root_path):
            blockers.append("normalized_directory must be under ignored jarvis/local.")
        else:
            normalized_path.mkdir(parents=True, exist_ok=True)
            output_file = normalized_path / f"{signal.as_of}_{_safe_source_id(source_id)}.normalized.json"
            output_file.write_text(json.dumps(signal.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            normalized_signal_file = str(output_file)
            signal_written = True

    signal_ready = signal is not None and not blockers
    return RawBtcPublicDataNormalizerResult(
        status=STATUS_READY if signal_ready else STATUS_BLOCKED,
        normalizer_status=NORMALIZER_READY if signal_ready else NORMALIZER_BLOCKED,
        raw_directory=str(raw_path),
        normalized_directory=str(normalized_path),
        raw_file_found=True,
        selected_raw_file=str(selected),
        source_id=source_id,
        candidate_id="btc",
        signal_ready=signal_ready,
        signal_written=signal_written and signal_ready,
        normalized_signal_file=normalized_signal_file if signal_ready else "",
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
        btc_signal=signal if signal_ready else None,
        recommendation_quality_current_data=False,
        allocation_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        raw_data_unverified=True,
    )


def format_raw_btc_public_data_normalizer(result: RawBtcPublicDataNormalizerResult) -> str:
    lines = [
        "J.A.R.V.I.S. Raw BTC Public Data Normalizer",
        f"status: {result.status}",
        f"normalizer status: {result.normalizer_status}",
        f"raw file found: {result.raw_file_found}",
        f"selected raw file: {result.selected_raw_file or 'none'}",
        f"signal ready: {result.signal_ready}",
        f"signal written: {result.signal_written}",
        f"normalized signal file: {result.normalized_signal_file or 'none'}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no buy request",
        "no orders created",
        "no trades executed",
    ]
    if result.btc_signal:
        signal = result.btc_signal
        lines.extend(
            [
                "",
                "BTC normalized public signal:",
                f"- candidate: {signal.candidate_id}",
                f"- source: {signal.source_id}",
                f"- as_of: {signal.as_of}",
                f"- price_eur: {signal.price_eur:,.2f}",
                f"- market_cap_eur: {signal.market_cap_eur:,.2f}",
                f"- volume_24h_eur: {signal.volume_24h_eur:,.2f}",
                f"- change_24h_pct: {signal.change_24h_pct:.4f}",
                f"- provider_last_updated_utc: {signal.provider_last_updated_utc}",
                "- raw data remains unverified until source-quality gate passes",
            ]
        )
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
    parser = argparse.ArgumentParser(description="Normalize raw BTC public data fetched by J.A.R.V.I.S.")
    parser.add_argument("--raw-directory", default=DEFAULT_RAW_DIRECTORY)
    parser.add_argument("--normalized-directory", default=DEFAULT_NORMALIZED_DIRECTORY)
    parser.add_argument("--source-id", default=DEFAULT_SOURCE_ID)
    parser.add_argument("--write-local-signal", action="store_true")
    args = parser.parse_args(argv)
    result = build_raw_btc_public_data_normalizer_result(
        raw_directory=args.raw_directory,
        normalized_directory=args.normalized_directory,
        source_id=args.source_id,
        write_local_signal=args.write_local_signal,
    )
    print(format_raw_btc_public_data_normalizer(result))
    return 0 if result.status == STATUS_READY else 1


if __name__ == "__main__":
    raise SystemExit(main())
