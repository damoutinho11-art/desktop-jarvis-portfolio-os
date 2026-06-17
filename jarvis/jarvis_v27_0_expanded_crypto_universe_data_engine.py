"""J.A.R.V.I.S. v27.0 expanded crypto universe data engine.

v27 moves the crypto lane beyond the BTC/HYPE/TAO seed set by:
- defining an expanded public crypto universe;
- building a local public-data source manifest for CoinGecko simple-price endpoints;
- reusing the existing v10 local-cache fetch boundary and v22 normalizer/source-quality gate;
- scoring source-ready crypto candidates with public market-cap, volume, volatility, and platform-readiness inputs.

It does not create buy requests, connect to brokers, ingest private account data,
place orders, or execute trades.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .jarvis_v22_0_multi_crypto_public_data_quality_pipeline import (
    DEFAULT_MAX_SIGNAL_AGE_DAYS,
    DEFAULT_NORMALIZED_DIRECTORY,
    DEFAULT_RAW_DIRECTORY,
    CryptoCandidateConfig,
    CryptoCandidateQualityResult,
    build_multi_crypto_public_data_quality_pipeline_result,
)

STATUS_READY = "JARVIS_V27_0_EXPANDED_CRYPTO_UNIVERSE_DATA_ENGINE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V27_0_EXPANDED_CRYPTO_UNIVERSE_DATA_ENGINE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V27_0_EXPANDED_CRYPTO_UNIVERSE_DATA_ENGINE_BLOCKED_SAFE"

ENGINE_READY = "EXPANDED_CRYPTO_UNIVERSE_DATA_ENGINE_READY"
ENGINE_REVIEW_REQUIRED = "EXPANDED_CRYPTO_UNIVERSE_DATA_ENGINE_REVIEW_REQUIRED"
ENGINE_BLOCKED = "EXPANDED_CRYPTO_UNIVERSE_DATA_ENGINE_BLOCKED"

DEFAULT_MANIFEST_PATH = "jarvis/local/public_data_sources.local.json"
DEFAULT_MISSING_MANIFEST_PATH = "jarvis/local/public_data_sources.missing.local.json"
DEFAULT_PORTFOLIO_STATE_PATH = "portfolio_state.json"


@dataclass(frozen=True)
class ExpandedCryptoUniverseCandidate:
    candidate_id: str
    display_name: str
    coingecko_key: str
    source_id: str
    platform_route: str
    platform_status_key: str
    min_price_eur: float
    max_price_eur: float
    max_abs_change_24h_pct: float
    min_market_cap_eur: float
    min_volume_24h_eur: float

    def to_v22_config(self) -> CryptoCandidateConfig:
        return CryptoCandidateConfig(
            candidate_id=self.candidate_id,
            source_id=self.source_id,
            coingecko_key=self.coingecko_key,
            min_price_eur=self.min_price_eur,
            max_price_eur=self.max_price_eur,
            max_abs_change_24h_pct=self.max_abs_change_24h_pct,
        )

    def to_source_manifest_entry(self) -> dict[str, Any]:
        url = (
            "https://api.coingecko.com/api/v3/simple/price"
            f"?ids={self.coingecko_key}"
            "&vs_currencies=eur"
            "&include_market_cap=true"
            "&include_24hr_vol=true"
            "&include_24hr_change=true"
            "&include_last_updated_at=true"
        )
        return {
            "source_id": self.source_id,
            "candidate_id": self.candidate_id,
            "display_name": f"{self.display_name} EUR public market data",
            "source_type": "public_market_data_json",
            "source_url": url,
            "update_frequency": "daily",
            "public_source_only": True,
            "requires_authentication": False,
            "requires_credentials": False,
            "broker_or_trading_api": False,
            "contains_private_data": False,
            "expected_content_type": "application/json",
        }


DEFAULT_EXPANDED_CRYPTO_UNIVERSE: tuple[ExpandedCryptoUniverseCandidate, ...] = (
    ExpandedCryptoUniverseCandidate("btc", "Bitcoin", "bitcoin", "coingecko_btc_simple_price_eur", "lhv_crypto", "lhv_crypto_ready", 1000.0, 1000000.0, 50.0, 100_000_000_000.0, 1_000_000_000.0),
    ExpandedCryptoUniverseCandidate("eth", "Ethereum", "ethereum", "coingecko_eth_simple_price_eur", "lhv_crypto", "lhv_crypto_ready", 10.0, 100000.0, 60.0, 50_000_000_000.0, 500_000_000.0),
    ExpandedCryptoUniverseCandidate("sol", "Solana", "solana", "coingecko_sol_simple_price_eur", "lhv_crypto", "lhv_crypto_ready", 0.1, 10000.0, 70.0, 5_000_000_000.0, 100_000_000.0),
    ExpandedCryptoUniverseCandidate("link", "Chainlink", "chainlink", "coingecko_link_simple_price_eur", "lhv_crypto", "lhv_crypto_ready", 0.01, 10000.0, 75.0, 1_000_000_000.0, 50_000_000.0),
    ExpandedCryptoUniverseCandidate("avax", "Avalanche", "avalanche-2", "coingecko_avax_simple_price_eur", "lhv_crypto", "lhv_crypto_ready", 0.01, 10000.0, 75.0, 1_000_000_000.0, 50_000_000.0),
    ExpandedCryptoUniverseCandidate("near", "NEAR Protocol", "near", "coingecko_near_simple_price_eur", "lhv_crypto", "lhv_crypto_ready", 0.01, 10000.0, 80.0, 500_000_000.0, 25_000_000.0),
    ExpandedCryptoUniverseCandidate("inj", "Injective", "injective-protocol", "coingecko_inj_simple_price_eur", "lhv_crypto", "lhv_crypto_ready", 0.01, 10000.0, 85.0, 250_000_000.0, 10_000_000.0),
    ExpandedCryptoUniverseCandidate("render", "Render", "render-token", "coingecko_render_simple_price_eur", "lhv_crypto", "lhv_crypto_ready", 0.01, 10000.0, 85.0, 250_000_000.0, 10_000_000.0),
    ExpandedCryptoUniverseCandidate("hype", "Hyperliquid", "hyperliquid", "coingecko_hype_simple_price_eur", "lhv_crypto", "lhv_crypto_ready", 0.01, 10000.0, 85.0, 250_000_000.0, 10_000_000.0),
    ExpandedCryptoUniverseCandidate("tao", "Bittensor", "bittensor", "coingecko_tao_simple_price_eur", "kraken", "kraken_ready", 0.01, 100000.0, 85.0, 250_000_000.0, 10_000_000.0),
)


@dataclass(frozen=True)
class ExpandedCryptoCandidateScore:
    candidate_id: str
    display_name: str
    source_id: str
    coingecko_key: str
    platform_route: str
    platform_ready: bool
    source_quality_ready: bool
    decision_status: str
    total_score: float
    market_cap_score: float
    volume_score: float
    stability_score: float
    platform_score: float
    price_eur: float | None
    market_cap_eur: float | None
    volume_24h_eur: float | None
    change_24h_pct: float | None
    signal_age_days: int | None
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "display_name": self.display_name,
            "source_id": self.source_id,
            "coingecko_key": self.coingecko_key,
            "platform_route": self.platform_route,
            "platform_ready": self.platform_ready,
            "source_quality_ready": self.source_quality_ready,
            "decision_status": self.decision_status,
            "total_score": self.total_score,
            "market_cap_score": self.market_cap_score,
            "volume_score": self.volume_score,
            "stability_score": self.stability_score,
            "platform_score": self.platform_score,
            "price_eur": self.price_eur,
            "market_cap_eur": self.market_cap_eur,
            "volume_24h_eur": self.volume_24h_eur,
            "change_24h_pct": self.change_24h_pct,
            "signal_age_days": self.signal_age_days,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


@dataclass(frozen=True)
class ExpandedCryptoUniverseDataEngineResult:
    status: str
    engine_status: str
    current_date: str
    universe_candidate_count: int
    manifest_path: str
    manifest_written: bool
    source_manifest: dict[str, Any]
    public_data_pipeline_status: str
    source_quality_ready_count: int
    source_quality_blocked_count: int
    full_public_data_coverage: bool
    platform_ready_count: int
    ranked_candidate_count: int
    top_candidate_id: str | None
    top_candidate_score: float
    candidate_scores: tuple[ExpandedCryptoCandidateScore, ...]
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
    final_user_buy_action_required: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "engine_status": self.engine_status,
            "current_date": self.current_date,
            "universe_candidate_count": self.universe_candidate_count,
            "manifest_path": self.manifest_path,
            "manifest_written": self.manifest_written,
            "source_manifest": self.source_manifest,
            "public_data_pipeline_status": self.public_data_pipeline_status,
            "source_quality_ready_count": self.source_quality_ready_count,
            "source_quality_blocked_count": self.source_quality_blocked_count,
            "full_public_data_coverage": self.full_public_data_coverage,
            "platform_ready_count": self.platform_ready_count,
            "ranked_candidate_count": self.ranked_candidate_count,
            "top_candidate_id": self.top_candidate_id,
            "top_candidate_score": self.top_candidate_score,
            "candidate_scores": [item.to_dict() for item in self.candidate_scores],
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
            "final_user_buy_action_required": self.final_user_buy_action_required,
        }


def _dedupe(items: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _load_json_if_exists(path: str | Path) -> dict[str, Any]:
    candidate = Path(path)
    if not candidate.is_file():
        return {}
    try:
        payload = json.loads(candidate.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def _is_under_jarvis_local(path: str | Path, root: str | Path = ".") -> bool:
    candidate = Path(path)
    resolved = (Path(root) / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()

    # Normal production path: under this repo's ignored jarvis/local directory.
    local_root = (Path(root) / "jarvis" / "local").resolve()
    try:
        resolved.relative_to(local_root)
        return True
    except ValueError:
        pass

    # Test/local-cache path: allow absolute temp roots only when the destination
    # itself is inside a jarvis/local directory segment.
    parts = [part.lower() for part in resolved.parts]
    return any(
        parts[index] == "jarvis" and index + 1 < len(parts) and parts[index + 1] == "local"
        for index in range(len(parts) - 1)
    )


def build_expanded_crypto_public_data_source_manifest(
    candidates: tuple[ExpandedCryptoUniverseCandidate, ...] = DEFAULT_EXPANDED_CRYPTO_UNIVERSE,
) -> dict[str, Any]:
    return {
        "title": "JARVIS v27.0 Expanded Crypto Public Data Source Manifest",
        "version": "v27.0-expanded-crypto-universe",
        "update_frequency": "daily",
        "sources": [candidate.to_source_manifest_entry() for candidate in candidates],
    }


def _write_manifest(path: str | Path, manifest: dict[str, Any]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _platform_status(portfolio_state_path: str | Path) -> dict[str, bool]:
    state = _load_json_if_exists(portfolio_state_path)
    status = state.get("platform_status", {})
    if not isinstance(status, dict):
        status = {}
    return {str(key): value is True for key, value in status.items()}


def _score_ratio(value: float, minimum: float, maximum: float) -> float:
    if minimum <= 0 or value <= 0:
        return 0.0
    ratio = value / minimum
    if ratio <= 1:
        return round(maximum * 0.5, 2)
    return round(min(maximum, maximum * 0.5 + math.log10(ratio) * maximum * 0.2), 2)


def _score_candidate(
    config: ExpandedCryptoUniverseCandidate,
    quality: CryptoCandidateQualityResult,
    *,
    platform_ready: bool,
) -> ExpandedCryptoCandidateScore:
    blockers: list[str] = []
    warnings: list[str] = list(quality.warnings)
    signal = quality.signal

    if not quality.source_quality_ready or signal is None:
        blockers.extend(quality.blockers)
        decision = "BLOCKED_BY_PUBLIC_DATA_QUALITY"
        if not quality.raw_file_found:
            decision = "BLOCKED_MISSING_PUBLIC_DATA"
        return ExpandedCryptoCandidateScore(
            candidate_id=config.candidate_id,
            display_name=config.display_name,
            source_id=config.source_id,
            coingecko_key=config.coingecko_key,
            platform_route=config.platform_route,
            platform_ready=platform_ready,
            source_quality_ready=False,
            decision_status=decision,
            total_score=0.0,
            market_cap_score=0.0,
            volume_score=0.0,
            stability_score=0.0,
            platform_score=0.0,
            price_eur=None,
            market_cap_eur=None,
            volume_24h_eur=None,
            change_24h_pct=None,
            signal_age_days=quality.signal_age_days,
            blockers=_dedupe(blockers),
            warnings=_dedupe(warnings),
        )

    if not platform_ready:
        blockers.append(f"{config.candidate_id} platform route {config.platform_route} is not ready.")

    if signal.market_cap_eur < config.min_market_cap_eur:
        blockers.append(
            f"{config.candidate_id} market cap EUR {signal.market_cap_eur:,.2f} is below minimum EUR {config.min_market_cap_eur:,.2f}."
        )
    if signal.volume_24h_eur < config.min_volume_24h_eur:
        blockers.append(
            f"{config.candidate_id} 24h volume EUR {signal.volume_24h_eur:,.2f} is below minimum EUR {config.min_volume_24h_eur:,.2f}."
        )

    market_cap_score = _score_ratio(signal.market_cap_eur, config.min_market_cap_eur, 35.0)
    volume_score = _score_ratio(signal.volume_24h_eur, config.min_volume_24h_eur, 25.0)
    stability_score = round(max(0.0, 20.0 - min(20.0, abs(signal.change_24h_pct) * 0.75)), 2)
    platform_score = 20.0 if platform_ready else 0.0
    total_score = round(market_cap_score + volume_score + stability_score + platform_score, 2)

    if blockers:
        decision = "BLOCKED_BY_PLATFORM_OR_MARKET_QUALITY"
    else:
        decision = "RANKED_FOR_CRYPTO_LANE"

    return ExpandedCryptoCandidateScore(
        candidate_id=config.candidate_id,
        display_name=config.display_name,
        source_id=config.source_id,
        coingecko_key=config.coingecko_key,
        platform_route=config.platform_route,
        platform_ready=platform_ready,
        source_quality_ready=True,
        decision_status=decision,
        total_score=total_score if not blockers else 0.0,
        market_cap_score=market_cap_score,
        volume_score=volume_score,
        stability_score=stability_score,
        platform_score=platform_score,
        price_eur=signal.price_eur,
        market_cap_eur=signal.market_cap_eur,
        volume_24h_eur=signal.volume_24h_eur,
        change_24h_pct=signal.change_24h_pct,
        signal_age_days=signal.signal_age_days,
        blockers=_dedupe(blockers),
        warnings=_dedupe(warnings),
    )


def build_expanded_crypto_universe_data_engine_result(
    *,
    current_date: str | None = None,
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    missing_manifest_path: str | Path = DEFAULT_MISSING_MANIFEST_PATH,
    portfolio_state_path: str | Path = DEFAULT_PORTFOLIO_STATE_PATH,
    raw_directory: str | Path = DEFAULT_RAW_DIRECTORY,
    normalized_directory: str | Path = DEFAULT_NORMALIZED_DIRECTORY,
    max_signal_age_days: int = DEFAULT_MAX_SIGNAL_AGE_DAYS,
    write_local_manifest: bool = False,
    write_missing_manifest: bool = False,
    write_local_signals: bool = False,
    candidates: tuple[ExpandedCryptoUniverseCandidate, ...] = DEFAULT_EXPANDED_CRYPTO_UNIVERSE,
) -> ExpandedCryptoUniverseDataEngineResult:
    blockers: list[str] = []
    warnings: list[str] = []
    manifest = build_expanded_crypto_public_data_source_manifest(candidates)

    if write_local_manifest and not _is_under_jarvis_local(manifest_path):
        blockers.append("manifest_path must be under ignored jarvis/local.")
    if write_missing_manifest and not _is_under_jarvis_local(missing_manifest_path):
        blockers.append("missing_manifest_path must be under ignored jarvis/local.")

    manifest_written = False
    if write_local_manifest and not blockers:
        _write_manifest(manifest_path, manifest)
        manifest_written = True

    platform = _platform_status(portfolio_state_path)
    candidate_by_id = {candidate.candidate_id: candidate for candidate in candidates}
    v22_candidates = tuple(candidate.to_v22_config() for candidate in candidates)

    pipeline = build_multi_crypto_public_data_quality_pipeline_result(
        raw_directory=raw_directory,
        normalized_directory=normalized_directory,
        current_date=current_date,
        max_signal_age_days=max_signal_age_days,
        write_local_signals=write_local_signals,
        candidates=v22_candidates,
    )

    warnings.extend(pipeline.warnings)
    candidate_scores: list[ExpandedCryptoCandidateScore] = []
    for quality in pipeline.candidate_results:
        config = candidate_by_id[quality.candidate_id]
        route_ready = platform.get(config.platform_status_key, False)
        candidate_scores.append(_score_candidate(config, quality, platform_ready=route_ready))

    ranked = sorted(
        candidate_scores,
        key=lambda item: (item.decision_status == "RANKED_FOR_CRYPTO_LANE", item.total_score),
        reverse=True,
    )
    ready_scores = [item for item in ranked if item.decision_status == "RANKED_FOR_CRYPTO_LANE"]
    top = ready_scores[0] if ready_scores else None

    source_ready_count = sum(1 for item in candidate_scores if item.source_quality_ready)
    source_blocked_count = len(candidate_scores) - source_ready_count
    full_public_data_coverage = source_blocked_count == 0
    platform_ready_count = sum(1 for item in candidate_scores if item.platform_ready)
    ranked_count = len(ready_scores)

    if write_missing_manifest and not blockers:
        missing_source_candidates = tuple(
            candidate_by_id[item.candidate_id] for item in candidate_scores if not item.source_quality_ready
        )
        _write_manifest(missing_manifest_path, build_expanded_crypto_public_data_source_manifest(missing_source_candidates))
        warnings.append(f"missing-source retry manifest written: {missing_manifest_path}")

    for item in candidate_scores:
        for blocker in item.blockers:
            if item.decision_status in {"BLOCKED_MISSING_PUBLIC_DATA", "BLOCKED_BY_PUBLIC_DATA_QUALITY"}:
                warnings.append(f"{item.candidate_id}: {blocker}")

    if blockers:
        status = STATUS_BLOCKED
        engine_status = ENGINE_BLOCKED
    elif source_blocked_count > 0:
        status = STATUS_REVIEW_REQUIRED
        engine_status = ENGINE_REVIEW_REQUIRED
    elif ranked_count == 0:
        status = STATUS_REVIEW_REQUIRED
        engine_status = ENGINE_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        engine_status = ENGINE_READY

    return ExpandedCryptoUniverseDataEngineResult(
        status=status,
        engine_status=engine_status,
        current_date=pipeline.current_date,
        universe_candidate_count=len(candidates),
        manifest_path=str(manifest_path),
        manifest_written=manifest_written,
        source_manifest=manifest,
        public_data_pipeline_status=pipeline.status,
        source_quality_ready_count=source_ready_count,
        source_quality_blocked_count=source_blocked_count,
        full_public_data_coverage=full_public_data_coverage,
        platform_ready_count=platform_ready_count,
        ranked_candidate_count=ranked_count,
        top_candidate_id=top.candidate_id if top else None,
        top_candidate_score=top.total_score if top else 0.0,
        candidate_scores=tuple(ranked),
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
        final_user_buy_action_required=True,
    )


def format_expanded_crypto_universe_data_engine(result: ExpandedCryptoUniverseDataEngineResult) -> str:
    lines = [
        "J.A.R.V.I.S. Expanded Crypto Universe Data Engine",
        f"status: {result.status}",
        f"engine status: {result.engine_status}",
        f"current date: {result.current_date}",
        f"universe candidate count: {result.universe_candidate_count}",
        f"manifest path: {result.manifest_path}",
        f"manifest written: {result.manifest_written}",
        f"public data pipeline status: {result.public_data_pipeline_status}",
        f"source quality ready count: {result.source_quality_ready_count}",
        f"source quality blocked count: {result.source_quality_blocked_count}",
        f"full public data coverage: {result.full_public_data_coverage}",
        f"platform ready count: {result.platform_ready_count}",
        f"ranked candidate count: {result.ranked_candidate_count}",
        f"top candidate: {result.top_candidate_id or 'none'}",
        f"top candidate score: {result.top_candidate_score:,.2f}",
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
        "Ranked crypto universe:",
    ]

    for item in result.candidate_scores:
        lines.append(
            f"- {item.candidate_id}: {item.decision_status}; score {item.total_score:,.2f}; "
            f"source_ready {item.source_quality_ready}; platform_ready {item.platform_ready}; route {item.platform_route}"
        )
        if item.price_eur is not None:
            lines.append(
                f"  price EUR {item.price_eur:,.2f}; market cap EUR {item.market_cap_eur:,.2f}; "
                f"24h volume EUR {item.volume_24h_eur:,.2f}; 24h change {item.change_24h_pct:,.4f}%"
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
    parser = argparse.ArgumentParser(description="Build expanded crypto universe manifest and scoring.")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--manifest-path", default=DEFAULT_MANIFEST_PATH)
    parser.add_argument("--missing-manifest-path", default=DEFAULT_MISSING_MANIFEST_PATH)
    parser.add_argument("--portfolio-state-path", default=DEFAULT_PORTFOLIO_STATE_PATH)
    parser.add_argument("--raw-directory", default=DEFAULT_RAW_DIRECTORY)
    parser.add_argument("--normalized-directory", default=DEFAULT_NORMALIZED_DIRECTORY)
    parser.add_argument("--max-signal-age-days", type=int, default=DEFAULT_MAX_SIGNAL_AGE_DAYS)
    parser.add_argument("--write-local-manifest", action="store_true")
    parser.add_argument("--write-missing-manifest", action="store_true")
    parser.add_argument("--write-local-signals", action="store_true")
    args = parser.parse_args(argv)

    result = build_expanded_crypto_universe_data_engine_result(
        current_date=args.current_date,
        manifest_path=args.manifest_path,
        missing_manifest_path=args.missing_manifest_path,
        portfolio_state_path=args.portfolio_state_path,
        raw_directory=args.raw_directory,
        normalized_directory=args.normalized_directory,
        max_signal_age_days=args.max_signal_age_days,
        write_local_manifest=args.write_local_manifest,
        write_missing_manifest=args.write_missing_manifest,
        write_local_signals=args.write_local_signals,
    )
    print(format_expanded_crypto_universe_data_engine(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())