from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


STATUS_READY = "JARVIS_V117_0_PUBLIC_DATA_PROVIDER_REGISTRY_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/public_data_provider_registry_latest.json"


@dataclass(frozen=True)
class PublicDataProvider:
    provider_id: str
    display_name: str
    provider_type: str
    priority: int
    purpose: list[str]
    assets_covered: list[str]
    enabled_now: bool
    live_fetch_supported: bool
    local_cache_supported: bool
    api_key_required: bool
    api_key_configured: bool
    current_local_paths: list[str]
    assistant_ready: bool
    freshness_policy: str
    known_strengths: list[str]
    known_gaps: list[str]
    safety_notes: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PublicDataProviderRegistryResult:
    status: str
    current_date: str
    providers: list[dict[str, Any]]
    provider_plan: list[dict[str, Any]]
    secret_policy: list[str]
    enabled_provider_count: int
    assistant_ready_provider_count: int
    major_gaps: list[str]
    recommended_next_stage: str
    execution_forbidden: bool
    broker_connection: bool
    credentials_used: bool
    order_created: bool
    trade_executed: bool
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _exists(path: str) -> bool:
    return Path(path).exists()


def build_public_data_provider_registry_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    write_report: bool = False,
) -> PublicDataProviderRegistryResult:
    providers = [
        PublicDataProvider(
            provider_id="coingecko",
            display_name="CoinGecko",
            provider_type="crypto_market_data",
            priority=1,
            purpose=["crypto_prices", "crypto_market_cap", "crypto_volume", "crypto_24h_change"],
            assets_covered=["BTC", "ETH", "SOL", "LINK", "AVAX", "HYPE", "NEAR", "RENDER", "INJ", "TAO"],
            enabled_now=True,
            live_fetch_supported=False,
            local_cache_supported=True,
            api_key_required=False,
            api_key_configured=False,
            current_local_paths=["jarvis/local/public_data/v22_multi_crypto_normalized"],
            assistant_ready=_exists("jarvis/local/public_data/v22_multi_crypto_normalized"),
            freshness_policy="local normalized cache; source/as_of and signal_age_days required",
            known_strengths=[
                "BTC and ETH prices are available from local normalized public cache",
                "24h percentage movement is available for crypto candidates",
                "no credentials required for current local cache usage",
            ],
            known_gaps=[
                "not refreshed live by assistant question path",
                "no 7d/30d history exposed to assistant yet",
                "no live news cause attached to price movement",
            ],
            safety_notes=["read-only public market data only", "no broker or execution capability"],
        ),
        PublicDataProvider(
            provider_id="yahoo_chart_local",
            display_name="Yahoo Chart Local Cache",
            provider_type="stock_etf_quote_data",
            priority=2,
            purpose=["stock_quotes", "etf_quotes", "selected_instrument_quote_checks"],
            assets_covered=["MSFT", "IS3Q.DE", "other ranked stock candidates"],
            enabled_now=True,
            live_fetch_supported=False,
            local_cache_supported=True,
            api_key_required=False,
            api_key_configured=False,
            current_local_paths=[
                "jarvis/local/individual_stock_public_ranked_candidates.local.json",
                "jarvis/local/stock_fund_etf_selected_instrument.local.json",
            ],
            assistant_ready=_exists("jarvis/local/individual_stock_public_ranked_candidates.local.json"),
            freshness_policy="local quote cache; source_as_of must not be in the future and source_status must be ready",
            known_strengths=[
                "MSFT quote is available and assistant-ready",
                "ranked stock candidates include source_as_of, provider, currency, and close_price",
            ],
            known_gaps=[
                "VWCE quote is missing from current assistant bridge",
                "GLOBAL_CORE_ETF is still an internal sleeve/placeholder without quote",
                "IS3Q.DE quote exists but has future-date/freshness warning",
            ],
            safety_notes=["read-only quote cache only", "no broker or execution capability"],
        ),
        PublicDataProvider(
            provider_id="ecb_fx",
            display_name="European Central Bank FX",
            provider_type="fx_reference_data",
            priority=3,
            purpose=["eur_fx_reference_rates", "usd_to_eur_context", "currency_conversion_context"],
            assets_covered=["EUR", "USD", "major FX pairs"],
            enabled_now=False,
            live_fetch_supported=False,
            local_cache_supported=True,
            api_key_required=False,
            api_key_configured=False,
            current_local_paths=[],
            assistant_ready=False,
            freshness_policy="official reference-rate cache required; as_of required",
            known_strengths=[
                "best fit for EUR-based portfolio FX reference rates",
                "no broker/execution dependency",
            ],
            known_gaps=[
                "not yet exposed as a first-class assistant market-data bridge record",
                "USD stock quote conversion to EUR is not yet assistant-facing",
            ],
            safety_notes=["reference data only", "no execution capability"],
        ),
        PublicDataProvider(
            provider_id="fmp_or_eodhd_future",
            display_name="FMP/EODHD Future Read-Only Provider",
            provider_type="future_market_data_provider",
            priority=4,
            purpose=["etf_quotes", "stock_quotes", "historical_prices", "fundamentals", "market_news"],
            assets_covered=["VWCE", "IS3Q.DE", "MSFT", "ETF/fund universe", "stock universe"],
            enabled_now=False,
            live_fetch_supported=False,
            local_cache_supported=False,
            api_key_required=True,
            api_key_configured=False,
            current_local_paths=[],
            assistant_ready=False,
            freshness_policy="future provider; must cache locally, normalize, and disclose source/as_of/freshness",
            known_strengths=[
                "likely best future upgrade for broad ETF/fund quote coverage",
                "can reduce dependence on ad-hoc Yahoo/Lightyear metadata",
            ],
            known_gaps=[
                "not implemented",
                "no API key/config contract",
                "no cache/normalizer/freshness gate",
            ],
            safety_notes=["must remain read-only", "must never connect to brokerage or trading endpoints"],
        ),
        PublicDataProvider(
            provider_id="news_future",
            display_name="Future Financial News Cache",
            provider_type="future_news_provider",
            priority=5,
            purpose=["macro_news", "crypto_news", "etf_news", "stock_news", "portfolio_relevance"],
            assets_covered=["portfolio watchlist", "crypto lane", "ETF/fund lane", "stock lane", "macro"],
            enabled_now=False,
            live_fetch_supported=False,
            local_cache_supported=False,
            api_key_required=True,
            api_key_configured=False,
            current_local_paths=[],
            assistant_ready=False,
            freshness_policy="future news cache; every headline must include source, timestamp, URL/id, and relevance reason",
            known_strengths=[
                "needed for real 'what happened today' assistant answers",
                "can power portfolio-relevant news summaries",
            ],
            known_gaps=[
                "live news fetch is disabled today",
                "current news layer is readiness/policy, not real headlines",
                "no relevance scorer yet",
            ],
            safety_notes=["no fake headlines", "no claimed market cause without sourced headline/data"],
        ),
    ]

    provider_dicts = [provider.to_dict() for provider in providers]
    provider_plan = [
        {
            "provider_id": "coingecko",
            "phase": "enabled_local_cache_now",
            "action": "Use existing normalized local crypto cache; do not live-fetch during assistant answers.",
            "default_enabled": True,
            "optional_env_key_only": False,
            "secrets_may_be_written": False,
        },
        {
            "provider_id": "yahoo_chart_local",
            "phase": "enabled_local_cache_now",
            "action": "Use existing local stock/ETF quote caches; quarantine future-dated or invalid ETF rows.",
            "default_enabled": True,
            "optional_env_key_only": False,
            "secrets_may_be_written": False,
        },
        {
            "provider_id": "ecb_fx",
            "phase": "planned_read_only_local_cache",
            "action": "Parse official ECB EUR/USD reference data into a local cache before assistant currency conversion.",
            "default_enabled": False,
            "optional_env_key_only": False,
            "secrets_may_be_written": False,
        },
        {
            "provider_id": "fmp_or_eodhd_future",
            "phase": "future_default_off",
            "action": "Add only as read-only optional-env-key providers; redact keys from URLs, caches, logs, reports, and outputs.",
            "default_enabled": False,
            "optional_env_key_only": True,
            "secrets_may_be_written": False,
        },
        {
            "provider_id": "news_future",
            "phase": "future_default_off",
            "action": "Add cached headline ingestion only when source, timestamp, URL/id, and relevance can be stored without fabricating news.",
            "default_enabled": False,
            "optional_env_key_only": True,
            "secrets_may_be_written": False,
        },
    ]
    secret_policy = [
        "broker/trading/execution APIs are forbidden",
        "external provider keys, if supported later, must be optional environment variables only",
        "provider keys must never be written to cache, logs, reports, request URLs, or outputs",
        "future paid/live providers must remain default-off until read-only cache and redaction tests exist",
    ]
    major_gaps = [
        "ETF quote coverage is incomplete: VWCE and GLOBAL_CORE_ETF have no trusted quote in the assistant bridge.",
        "IS3Q.DE quote exists but is not trusted because source_as_of/freshness is suspicious.",
        "FX is not yet a first-class assistant-facing provider.",
        "Live/cached financial news headlines are not implemented; current news layer is readiness only.",
        "No universal refresh/cache command exists for all public market data.",
        "No 7d/30d historical movement layer is exposed to assistant answers.",
    ]

    result = PublicDataProviderRegistryResult(
        status=STATUS_READY,
        current_date=current_date,
        providers=provider_dicts,
        provider_plan=provider_plan,
        secret_policy=secret_policy,
        enabled_provider_count=sum(1 for provider in providers if provider.enabled_now),
        assistant_ready_provider_count=sum(1 for provider in providers if provider.assistant_ready),
        major_gaps=major_gaps,
        recommended_next_stage="v118 Universal Market Data Refresh + ETF Quote Resolver",
        execution_forbidden=True,
        broker_connection=False,
        credentials_used=False,
        order_created=False,
        trade_executed=False,
        report_written=bool(write_report),
        report_path=str(output_path),
    )

    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(
            json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    return result


def format_public_data_provider_registry(result: PublicDataProviderRegistryResult) -> str:
    lines = [
        "J.A.R.V.I.S. PUBLIC DATA PROVIDER REGISTRY",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"enabled providers: {result.enabled_provider_count}",
        f"assistant-ready providers: {result.assistant_ready_provider_count}",
        "",
        "PROVIDERS:",
    ]
    for provider in result.providers:
        lines.append(
            f"- {provider['provider_id']}: enabled={provider['enabled_now']}; "
            f"assistant_ready={provider['assistant_ready']}; type={provider['provider_type']}; "
            f"purpose={', '.join(provider['purpose'])}"
        )
    lines.extend(
        [
            "",
            "PROVIDER PLAN:",
            *[
                f"- {plan['provider_id']}: phase={plan['phase']}; default_enabled={plan['default_enabled']}; "
                f"optional_env_key_only={plan['optional_env_key_only']}; secrets_may_be_written={plan['secrets_may_be_written']}; "
                f"action={plan['action']}"
                for plan in result.provider_plan
            ],
            "",
            "SECRET POLICY:",
            *[f"- {policy}" for policy in result.secret_policy],
        ]
    )
    lines.extend(
        [
            "",
            "MAJOR GAPS:",
            *[f"- {gap}" for gap in result.major_gaps],
            "",
            f"recommended next stage: {result.recommended_next_stage}",
            "",
            "SAFETY:",
            "- read-only public/provider registry only",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)

    result = build_public_data_provider_registry_result(
        current_date=args.current_date,
        output_path=args.output_path,
        write_report=args.write_report,
    )
    print(format_public_data_provider_registry(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
