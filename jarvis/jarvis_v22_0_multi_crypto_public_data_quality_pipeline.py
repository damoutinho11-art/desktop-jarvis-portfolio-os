"""J.A.R.V.I.S. v22.0 multi-crypto public data quality pipeline.

This module generalizes the BTC-only v19/v20 public-data path to the crypto-lane
candidate set. It reads raw, unverified CoinGecko JSON fetched through the v10
public-data boundary, normalizes each configured crypto candidate, and applies a
source-quality gate.

It does not update allocation scores, does not regenerate approval tickets, does
not create buy requests, does not connect to brokers, and does not execute trades.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

STATUS_READY = "JARVIS_V22_0_MULTI_CRYPTO_PUBLIC_DATA_QUALITY_PIPELINE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V22_0_MULTI_CRYPTO_PUBLIC_DATA_QUALITY_PIPELINE_REVIEW_REQUIRED_SAFE"
PIPELINE_READY = "MULTI_CRYPTO_PUBLIC_DATA_QUALITY_PIPELINE_READY"
PIPELINE_REVIEW_REQUIRED = "MULTI_CRYPTO_PUBLIC_DATA_QUALITY_PIPELINE_REVIEW_REQUIRED"

CANDIDATE_QUALITY_READY = "CRYPTO_PUBLIC_SIGNAL_SOURCE_QUALITY_READY"
CANDIDATE_QUALITY_BLOCKED = "CRYPTO_PUBLIC_SIGNAL_SOURCE_QUALITY_BLOCKED"

DEFAULT_RAW_DIRECTORY = "jarvis/local/public_data/v10_raw"
DEFAULT_NORMALIZED_DIRECTORY = "jarvis/local/public_data/v22_multi_crypto_normalized"
DEFAULT_MAX_SIGNAL_AGE_DAYS = 1


@dataclass(frozen=True)
class CryptoCandidateConfig:
    candidate_id: str
    source_id: str
    coingecko_key: str
    min_price_eur: float
    max_price_eur: float
    max_abs_change_24h_pct: float


DEFAULT_CANDIDATES: tuple[CryptoCandidateConfig, ...] = (
    CryptoCandidateConfig(
        candidate_id="btc",
        source_id="coingecko_btc_simple_price_eur",
        coingecko_key="bitcoin",
        min_price_eur=1000.0,
        max_price_eur=1000000.0,
        max_abs_change_24h_pct=50.0,
    ),
    CryptoCandidateConfig(
        candidate_id="hype",
        source_id="coingecko_hype_simple_price_eur",
        coingecko_key="hyperliquid",
        min_price_eur=0.01,
        max_price_eur=10000.0,
        max_abs_change_24h_pct=75.0,
    ),
    CryptoCandidateConfig(
        candidate_id="tao",
        source_id="coingecko_tao_simple_price_eur",
        coingecko_key="bittensor",
        min_price_eur=0.01,
        max_price_eur=100000.0,
        max_abs_change_24h_pct=75.0,
    ),
)


@dataclass(frozen=True)
class CryptoPublicSignal:
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
    source_quality_ready: bool
    signal_age_days: int

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
            "source_quality_ready": self.source_quality_ready,
            "signal_age_days": self.signal_age_days,
        }


@dataclass(frozen=True)
class CryptoCandidateQualityResult:
    candidate_id: str
    source_id: str
    coingecko_key: str
    quality_status: str
    source_quality_ready: bool
    raw_file_found: bool
    selected_raw_file: str
    signal_written: bool
    normalized_signal_file: str
    signal_age_days: int | None
    signal: CryptoPublicSignal | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "source_id": self.source_id,
            "coingecko_key": self.coingecko_key,
            "quality_status": self.quality_status,
            "source_quality_ready": self.source_quality_ready,
            "raw_file_found": self.raw_file_found,
            "selected_raw_file": self.selected_raw_file,
            "signal_written": self.signal_written,
            "normalized_signal_file": self.normalized_signal_file,
            "signal_age_days": self.signal_age_days,
            "signal": self.signal.to_dict() if self.signal else None,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class MultiCryptoPublicDataQualityPipelineResult:
    status: str
    pipeline_status: str
    raw_directory: str
    normalized_directory: str
    current_date: str
    max_signal_age_days: int
    candidate_count: int
    source_quality_ready_count: int
    blocked_candidate_count: int
    all_crypto_public_signals_ready: bool
    candidate_results: tuple[CryptoCandidateQualityResult, ...]
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
            "pipeline_status": self.pipeline_status,
            "raw_directory": self.raw_directory,
            "normalized_directory": self.normalized_directory,
            "current_date": self.current_date,
            "max_signal_age_days": self.max_signal_age_days,
            "candidate_count": self.candidate_count,
            "source_quality_ready_count": self.source_quality_ready_count,
            "blocked_candidate_count": self.blocked_candidate_count,
            "all_crypto_public_signals_ready": self.all_crypto_public_signals_ready,
            "candidate_results": [item.to_dict() for item in self.candidate_results],
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


def _int(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_source_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return safe or "unknown_source"


def _is_under_jarvis_local(path: Path, root: Path) -> bool:
    resolved = path.resolve()
    local_root = (root / "jarvis" / "local").resolve()
    try:
        resolved.relative_to(local_root)
        return True
    except ValueError:
        return False


def _dedupe(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(items))


def _parse_date(value: str) -> date | None:
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _today_iso() -> str:
    return date.today().isoformat()


def _as_utc_timestamp(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).replace(microsecond=0).isoformat()


def _extract_as_of_from_filename(path: Path) -> str:
    match = re.match(r"^(\d{4}-\d{2}-\d{2})_", path.name)
    return match.group(1) if match else "unknown"


def find_latest_raw_crypto_file(
    raw_directory: str | Path,
    *,
    source_id: str,
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


def _blocked_candidate_result(
    config: CryptoCandidateConfig,
    *,
    raw_file_found: bool,
    selected_raw_file: str,
    blockers: list[str],
    warnings: list[str] | None = None,
) -> CryptoCandidateQualityResult:
    return CryptoCandidateQualityResult(
        candidate_id=config.candidate_id,
        source_id=config.source_id,
        coingecko_key=config.coingecko_key,
        quality_status=CANDIDATE_QUALITY_BLOCKED,
        source_quality_ready=False,
        raw_file_found=raw_file_found,
        selected_raw_file=selected_raw_file,
        signal_written=False,
        normalized_signal_file="",
        signal_age_days=None,
        signal=None,
        blockers=_dedupe(blockers),
        warnings=_dedupe(warnings or []),
    )


def normalize_and_quality_gate_crypto_raw(
    raw_file: str | Path,
    config: CryptoCandidateConfig,
    *,
    current_date: str,
    max_signal_age_days: int = DEFAULT_MAX_SIGNAL_AGE_DAYS,
) -> CryptoCandidateQualityResult:
    path = Path(raw_file)
    blockers: list[str] = []
    warnings: list[str] = []

    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001 - local public cache must fail closed.
        return _blocked_candidate_result(
            config,
            raw_file_found=True,
            selected_raw_file=str(path),
            blockers=[f"{config.candidate_id} raw public data is not valid JSON: {exc.__class__.__name__}: {_text(exc)}"],
            warnings=warnings,
        )

    if not isinstance(payload, dict):
        return _blocked_candidate_result(
            config,
            raw_file_found=True,
            selected_raw_file=str(path),
            blockers=[f"{config.candidate_id} raw public data must be a JSON object."],
            warnings=warnings,
        )

    coin = payload.get(config.coingecko_key)
    if not isinstance(coin, dict):
        return _blocked_candidate_result(
            config,
            raw_file_found=True,
            selected_raw_file=str(path),
            blockers=[f"{config.candidate_id} raw public data must contain a {config.coingecko_key} object."],
            warnings=warnings,
        )

    price_eur = _float(coin.get("eur"))
    market_cap_eur = _float(coin.get("eur_market_cap"))
    volume_24h_eur = _float(coin.get("eur_24h_vol"))
    change_24h_pct = _float(coin.get("eur_24h_change"))
    provider_last_updated_at = _int(coin.get("last_updated_at"))

    if price_eur is None or price_eur <= 0:
        blockers.append(f"{config.candidate_id} EUR price must be a positive number.")
    elif price_eur < config.min_price_eur or price_eur > config.max_price_eur:
        blockers.append(
            f"{config.candidate_id} EUR price {price_eur} is outside sanity range "
            f"{config.min_price_eur}..{config.max_price_eur}."
        )

    if market_cap_eur is None or market_cap_eur < 0:
        blockers.append(f"{config.candidate_id} EUR market cap must be a non-negative number.")
    if volume_24h_eur is None or volume_24h_eur < 0:
        blockers.append(f"{config.candidate_id} 24h EUR volume must be a non-negative number.")
    if change_24h_pct is None:
        blockers.append(f"{config.candidate_id} 24h EUR change percentage must be numeric.")
    elif abs(change_24h_pct) > config.max_abs_change_24h_pct:
        blockers.append(
            f"{config.candidate_id} 24h EUR change {change_24h_pct:.4f}% exceeds "
            f"sanity limit {config.max_abs_change_24h_pct:.4f}%."
        )
    if provider_last_updated_at is None or provider_last_updated_at <= 0:
        blockers.append(f"{config.candidate_id} provider last_updated_at must be a positive Unix timestamp.")

    as_of = _extract_as_of_from_filename(path)
    current = _parse_date(current_date)
    signal_date = _parse_date(as_of)
    signal_age_days: int | None = None
    if current is None:
        blockers.append("current_date must be YYYY-MM-DD.")
    if signal_date is None:
        blockers.append(f"{config.candidate_id} raw filename must include a YYYY-MM-DD as_of prefix.")
    if current is not None and signal_date is not None:
        signal_age_days = (current - signal_date).days
        if signal_age_days < 0:
            blockers.append(f"{config.candidate_id} signal as_of date is in the future.")
        elif signal_age_days > max_signal_age_days:
            blockers.append(
                f"{config.candidate_id} signal is stale: age {signal_age_days} days exceeds "
                f"max {max_signal_age_days} days."
            )

    if blockers:
        return _blocked_candidate_result(
            config,
            raw_file_found=True,
            selected_raw_file=str(path),
            blockers=blockers,
            warnings=warnings,
        )

    assert price_eur is not None
    assert market_cap_eur is not None
    assert volume_24h_eur is not None
    assert change_24h_pct is not None
    assert provider_last_updated_at is not None
    assert signal_age_days is not None

    signal = CryptoPublicSignal(
        candidate_id=config.candidate_id,
        source_id=config.source_id,
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
        source_quality_ready=True,
        signal_age_days=signal_age_days,
    )

    return CryptoCandidateQualityResult(
        candidate_id=config.candidate_id,
        source_id=config.source_id,
        coingecko_key=config.coingecko_key,
        quality_status=CANDIDATE_QUALITY_READY,
        source_quality_ready=True,
        raw_file_found=True,
        selected_raw_file=str(path),
        signal_written=False,
        normalized_signal_file="",
        signal_age_days=signal_age_days,
        signal=signal,
        blockers=tuple(),
        warnings=tuple(warnings),
    )


def build_multi_crypto_public_data_quality_pipeline_result(
    *,
    raw_directory: str | Path = DEFAULT_RAW_DIRECTORY,
    normalized_directory: str | Path = DEFAULT_NORMALIZED_DIRECTORY,
    root: str | Path = ".",
    current_date: str | None = None,
    max_signal_age_days: int = DEFAULT_MAX_SIGNAL_AGE_DAYS,
    write_local_signals: bool = False,
    candidates: tuple[CryptoCandidateConfig, ...] = DEFAULT_CANDIDATES,
) -> MultiCryptoPublicDataQualityPipelineResult:
    root_path = Path(root)
    raw_path = root_path / raw_directory
    normalized_path = root_path / normalized_directory
    current_date_text = current_date or _today_iso()

    blockers: list[str] = []
    warnings: list[str] = []

    if max_signal_age_days < 0:
        blockers.append("max_signal_age_days must be non-negative.")
    if not _is_under_jarvis_local(raw_path, root_path):
        blockers.append("raw_directory must be under ignored jarvis/local.")
    if not _is_under_jarvis_local(normalized_path, root_path):
        blockers.append("normalized_directory must be under ignored jarvis/local.")
    if _parse_date(current_date_text) is None:
        blockers.append("current_date must be YYYY-MM-DD.")

    candidate_results: list[CryptoCandidateQualityResult] = []
    if blockers:
        for config in candidates:
            candidate_results.append(
                _blocked_candidate_result(
                    config,
                    raw_file_found=False,
                    selected_raw_file="",
                    blockers=["pipeline configuration blocked before candidate evaluation."],
                    warnings=[],
                )
            )
    else:
        for config in candidates:
            selected = find_latest_raw_crypto_file(raw_directory, source_id=config.source_id, root=root_path)
            if selected is None:
                candidate_results.append(
                    _blocked_candidate_result(
                        config,
                        raw_file_found=False,
                        selected_raw_file="",
                        blockers=[f"No raw public data file found in {raw_path} for source {config.source_id}."],
                        warnings=[],
                    )
                )
                continue
            candidate_result = normalize_and_quality_gate_crypto_raw(
                selected,
                config,
                current_date=current_date_text,
                max_signal_age_days=max_signal_age_days,
            )
            candidate_results.append(candidate_result)

    if write_local_signals and not blockers:
        normalized_path.mkdir(parents=True, exist_ok=True)
        rewritten_results: list[CryptoCandidateQualityResult] = []
        for candidate_result in candidate_results:
            signal = candidate_result.signal
            if not candidate_result.source_quality_ready or signal is None:
                rewritten_results.append(candidate_result)
                continue
            output_file = normalized_path / f"{signal.as_of}_{_safe_source_id(signal.source_id)}.normalized.json"
            output_file.write_text(json.dumps(signal.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
            rewritten_results.append(
                CryptoCandidateQualityResult(
                    candidate_id=candidate_result.candidate_id,
                    source_id=candidate_result.source_id,
                    coingecko_key=candidate_result.coingecko_key,
                    quality_status=candidate_result.quality_status,
                    source_quality_ready=candidate_result.source_quality_ready,
                    raw_file_found=candidate_result.raw_file_found,
                    selected_raw_file=candidate_result.selected_raw_file,
                    signal_written=True,
                    normalized_signal_file=str(output_file),
                    signal_age_days=candidate_result.signal_age_days,
                    signal=candidate_result.signal,
                    blockers=candidate_result.blockers,
                    warnings=candidate_result.warnings,
                )
            )
        candidate_results = rewritten_results

    for candidate_result in candidate_results:
        for blocker in candidate_result.blockers:
            blockers.append(f"{candidate_result.candidate_id}: {blocker}")
        for warning in candidate_result.warnings:
            warnings.append(f"{candidate_result.candidate_id}: {warning}")

    ready_count = sum(1 for item in candidate_results if item.source_quality_ready)
    blocked_count = len(candidate_results) - ready_count
    all_ready = bool(candidate_results) and blocked_count == 0 and not blockers

    return MultiCryptoPublicDataQualityPipelineResult(
        status=STATUS_READY if all_ready else STATUS_REVIEW_REQUIRED,
        pipeline_status=PIPELINE_READY if all_ready else PIPELINE_REVIEW_REQUIRED,
        raw_directory=str(raw_path),
        normalized_directory=str(normalized_path),
        current_date=current_date_text,
        max_signal_age_days=max_signal_age_days,
        candidate_count=len(candidate_results),
        source_quality_ready_count=ready_count,
        blocked_candidate_count=blocked_count,
        all_crypto_public_signals_ready=all_ready,
        candidate_results=tuple(candidate_results),
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


def format_multi_crypto_public_data_quality_pipeline(
    result: MultiCryptoPublicDataQualityPipelineResult,
) -> str:
    lines = [
        "J.A.R.V.I.S. Multi-Crypto Public Data Quality Pipeline",
        f"status: {result.status}",
        f"pipeline status: {result.pipeline_status}",
        f"current date: {result.current_date}",
        f"candidate count: {result.candidate_count}",
        f"source quality ready count: {result.source_quality_ready_count}",
        f"blocked candidate count: {result.blocked_candidate_count}",
        f"all crypto public signals ready: {result.all_crypto_public_signals_ready}",
        f"recommendation quality current data: {result.recommendation_quality_current_data}",
        f"allocation mutation: {result.allocation_mutation}",
        f"approval ticket mutation: {result.approval_ticket_mutation}",
        f"buy request created: {result.buy_request_created}",
        "no broker connection",
        "no credentials",
        "no private account data ingestion",
        "no orders created",
        "no trades executed",
        "",
        "Crypto public signals:",
    ]

    for item in result.candidate_results:
        if item.signal:
            signal = item.signal
            lines.extend(
                [
                    f"- {signal.candidate_id}: {item.quality_status}; ready {item.source_quality_ready}; age {signal.signal_age_days} days",
                    f"  price: EUR {signal.price_eur:,.2f}; 24h change: {signal.change_24h_pct:.4f}%",
                    f"  source: {signal.source_id}; as_of: {signal.as_of}; provider updated: {signal.provider_last_updated_utc}",
                    f"  normalized written: {item.signal_written}; file: {item.normalized_signal_file or 'none'}",
                ]
            )
        else:
            lines.extend(
                [
                    f"- {item.candidate_id}: {item.quality_status}; ready {item.source_quality_ready}",
                    f"  source: {item.source_id}; raw file: {item.selected_raw_file or 'none'}",
                ]
            )
            for blocker in item.blockers:
                lines.append(f"  blocker: {blocker}")

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
    parser = argparse.ArgumentParser(description="Normalize and quality-gate multi-crypto public data.")
    parser.add_argument("--raw-directory", default=DEFAULT_RAW_DIRECTORY)
    parser.add_argument("--normalized-directory", default=DEFAULT_NORMALIZED_DIRECTORY)
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--max-signal-age-days", type=int, default=DEFAULT_MAX_SIGNAL_AGE_DAYS)
    parser.add_argument("--write-local-signals", action="store_true")
    args = parser.parse_args(argv)

    result = build_multi_crypto_public_data_quality_pipeline_result(
        raw_directory=args.raw_directory,
        normalized_directory=args.normalized_directory,
        current_date=args.current_date,
        max_signal_age_days=args.max_signal_age_days,
        write_local_signals=args.write_local_signals,
    )
    print(format_multi_crypto_public_data_quality_pipeline(result))
    return 0 if result.status == STATUS_READY else 1


if __name__ == "__main__":
    raise SystemExit(main())