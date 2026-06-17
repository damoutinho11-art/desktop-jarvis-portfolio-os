"""J.A.R.V.I.S. v43.0 free research API router + weekly policy.

v43 codifies the operating model:

- day-by-day = check-ins and finance analysis
- week-by-week = manual buy preparation
- free-first research API/source router
- no broker API, no order API, no execution

This stage does not fetch new external API endpoints. It makes the provider/router
contract explicit, detects optional local API-key availability, and gates weekly
manual-buy preparation by data/source confidence and v42 three-lane readiness.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable, Mapping

from .jarvis_v12_1_local_voice_io_shell import DEFAULT_COMMAND_SAMPLES
from .jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from .jarvis_v38_0_individual_stock_public_universe_engine import (
    DEFAULT_STOCK_SIGNALS_PATH,
    DEFAULT_STOCK_UNIVERSE_PATH,
)
from .jarvis_v39_0_individual_stock_public_ranker import DEFAULT_RANKED_STOCKS_PATH
from .jarvis_v41_0_ranked_individual_stock_candidate_ticket_bridge import DEFAULT_APPROVAL_TICKET_PATH
from .jarvis_v42_0_three_lane_daily_action_brief import (
    ThreeLaneDailyActionBriefResult,
    build_three_lane_daily_action_brief_result,
)

STATUS_READY = "JARVIS_V43_0_FREE_RESEARCH_API_ROUTER_WEEKLY_POLICY_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V43_0_FREE_RESEARCH_API_ROUTER_WEEKLY_POLICY_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V43_0_FREE_RESEARCH_API_ROUTER_WEEKLY_POLICY_BLOCKED_SAFE"

ROUTER_READY = "FREE_RESEARCH_API_ROUTER_WEEKLY_POLICY_READY"
ROUTER_REVIEW_REQUIRED = "FREE_RESEARCH_API_ROUTER_WEEKLY_POLICY_REVIEW_REQUIRED"
ROUTER_BLOCKED = "FREE_RESEARCH_API_ROUTER_WEEKLY_POLICY_BLOCKED"

MODE_DAILY_CHECK_IN = "daily_check_in"
MODE_WEEKLY_BUY_PREP = "weekly_buy_prep"

NEXT_STAGE = "free_research_api_fetcher_adapters_and_local_cache"


@dataclass(frozen=True)
class ResearchProviderStatus:
    provider_id: str
    lane: str
    role: str
    cost_model: str
    requires_api_key: bool
    api_key_env_var: str | None
    api_key_present: bool
    no_key_fallback_available: bool
    status: str
    confidence_points: int
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "lane": self.lane,
            "role": self.role,
            "cost_model": self.cost_model,
            "requires_api_key": self.requires_api_key,
            "api_key_env_var": self.api_key_env_var,
            "api_key_present": self.api_key_present,
            "no_key_fallback_available": self.no_key_fallback_available,
            "status": self.status,
            "confidence_points": self.confidence_points,
            "notes": list(self.notes),
        }


@dataclass(frozen=True)
class FreeResearchApiRouterWeeklyPolicyResult:
    status: str
    router_status: str
    recommended_next_stage: str
    current_date: str
    operating_mode: str
    daily_check_in_only: bool
    weekly_buy_preparation_allowed: bool
    manual_buy_action_today: bool
    source_confidence_score: int
    source_confidence_grade: str
    free_stack_sufficient_for_weekly_investing: bool
    paid_api_required_now: bool
    broker_api_required_now: bool
    provider_statuses: tuple[ResearchProviderStatus, ...]
    approval_ticket_path: str
    stock_universe_path: str
    stock_signals_path: str
    ranked_stocks_path: str
    upstream_three_lane_result: Any
    crypto_candidate: str | None
    crypto_amount_eur: float | None
    etf_symbol: str | None
    etf_amount_eur: float | None
    stock_symbol: str | None
    stock_manual_amount_required: bool | None
    stock_approved_for_purchase: bool | None
    recommendation_quality_current_data: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    portfolio_state_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_data_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    final_user_buy_action_required: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "router_status": self.router_status,
            "recommended_next_stage": self.recommended_next_stage,
            "current_date": self.current_date,
            "operating_mode": self.operating_mode,
            "daily_check_in_only": self.daily_check_in_only,
            "weekly_buy_preparation_allowed": self.weekly_buy_preparation_allowed,
            "manual_buy_action_today": self.manual_buy_action_today,
            "source_confidence_score": self.source_confidence_score,
            "source_confidence_grade": self.source_confidence_grade,
            "free_stack_sufficient_for_weekly_investing": self.free_stack_sufficient_for_weekly_investing,
            "paid_api_required_now": self.paid_api_required_now,
            "broker_api_required_now": self.broker_api_required_now,
            "provider_statuses": [provider.to_dict() for provider in self.provider_statuses],
            "approval_ticket_path": self.approval_ticket_path,
            "stock_universe_path": self.stock_universe_path,
            "stock_signals_path": self.stock_signals_path,
            "ranked_stocks_path": self.ranked_stocks_path,
            "upstream_three_lane_result": self.upstream_three_lane_result.to_dict()
            if hasattr(self.upstream_three_lane_result, "to_dict")
            else dict(getattr(self.upstream_three_lane_result, "__dict__", {})),
            "crypto_candidate": self.crypto_candidate,
            "crypto_amount_eur": self.crypto_amount_eur,
            "etf_symbol": self.etf_symbol,
            "etf_amount_eur": self.etf_amount_eur,
            "stock_symbol": self.stock_symbol,
            "stock_manual_amount_required": self.stock_manual_amount_required,
            "stock_approved_for_purchase": self.stock_approved_for_purchase,
            "recommendation_quality_current_data": self.recommendation_quality_current_data,
            "allocation_mutation": self.allocation_mutation,
            "approval_ticket_mutation": self.approval_ticket_mutation,
            "portfolio_state_mutation": self.portfolio_state_mutation,
            "buy_request_created": self.buy_request_created,
            "broker_connection_forbidden": self.broker_connection_forbidden,
            "credentials_forbidden": self.credentials_forbidden,
            "private_account_data_ingestion_forbidden": self.private_account_data_ingestion_forbidden,
            "order_creation_forbidden": self.order_creation_forbidden,
            "no_trades_executed": self.no_trades_executed,
            "final_user_buy_action_required": self.final_user_buy_action_required,
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
        }


def _today_iso() -> str:
    return date.today().isoformat()


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    text = str(value).strip()
    if len(text) >= 10:
        text = text[:10]
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None


def _resolve_path(path: str | Path, root: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return Path(root) / candidate


def _is_under(path: Path, root: str | Path, child: str) -> bool:
    resolved = path.resolve()
    allowed_root = (Path(root) / child).resolve()
    try:
        resolved.relative_to(allowed_root)
        return True
    except ValueError:
        return False


def _dedupe(items: list[str] | tuple[str, ...]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _env_has_key(env: Mapping[str, str], key: str | None) -> bool:
    if not key:
        return False
    return bool(str(env.get(key, "")).strip())


def build_research_provider_statuses(env: Mapping[str, str] | None = None) -> tuple[ResearchProviderStatus, ...]:
    source_env: Mapping[str, str] = env if env is not None else os.environ

    fmp_key = _env_has_key(source_env, "JARVIS_FMP_API_KEY")
    coingecko_key = _env_has_key(source_env, "JARVIS_COINGECKO_API_KEY")

    return (
        ResearchProviderStatus(
            provider_id="fmp_free_optional",
            lane="stocks_etfs_fundamentals",
            role="primary_free_research_api_when_key_present",
            cost_model="free_optional_key",
            requires_api_key=True,
            api_key_env_var="JARVIS_FMP_API_KEY",
            api_key_present=fmp_key,
            no_key_fallback_available=True,
            status="OPTIONAL_KEY_PRESENT_READY" if fmp_key else "OPTIONAL_KEY_MISSING_FALLBACK_ACTIVE",
            confidence_points=24 if fmp_key else 8,
            notes=(
                "Use for stock fundamentals, ETF metadata, ETF holdings, and richer stock/ETF research when a local key exists.",
                "Missing key does not block weekly investing because SEC/ECB/Yahoo/local fallbacks remain available.",
            ),
        ),
        ResearchProviderStatus(
            provider_id="coingecko_free_or_demo",
            lane="crypto",
            role="primary_free_crypto_research_api",
            cost_model="free_public_or_demo_key",
            requires_api_key=False,
            api_key_env_var="JARVIS_COINGECKO_API_KEY",
            api_key_present=coingecko_key,
            no_key_fallback_available=True,
            status="PUBLIC_OR_KEYED_READY",
            confidence_points=22 if coingecko_key else 20,
            notes=(
                "Use for crypto price, market cap, volume, liquidity, and coin metadata.",
                "Cache aggressively because free/demo limits can vary.",
            ),
        ),
        ResearchProviderStatus(
            provider_id="sec_edgar_official",
            lane="us_stock_validation",
            role="official_fundamental_validation",
            cost_model="free_no_key_official",
            requires_api_key=False,
            api_key_env_var=None,
            api_key_present=False,
            no_key_fallback_available=True,
            status="NO_KEY_OFFICIAL_READY",
            confidence_points=18,
            notes=(
                "Use as official validation for US company facts and filings.",
            ),
        ),
        ResearchProviderStatus(
            provider_id="ecb_fx_official",
            lane="fx",
            role="official_eur_fx_reference",
            cost_model="free_no_key_official",
            requires_api_key=False,
            api_key_env_var=None,
            api_key_present=False,
            no_key_fallback_available=True,
            status="NO_KEY_OFFICIAL_READY",
            confidence_points=8,
            notes=(
                "Use for EUR/USD and EUR reference conversion checks.",
            ),
        ),
        ResearchProviderStatus(
            provider_id="yahoo_chart_public_fallback",
            lane="stocks_etfs_price",
            role="public_quote_fallback",
            cost_model="free_no_key_public",
            requires_api_key=False,
            api_key_env_var=None,
            api_key_present=False,
            no_key_fallback_available=True,
            status="NO_KEY_PUBLIC_FALLBACK_READY",
            confidence_points=8,
            notes=(
                "Use as resilient quote fallback, not as the whole research brain.",
            ),
        ),
        ResearchProviderStatus(
            provider_id="local_cache_audit_trail",
            lane="all",
            role="cache_and_audit_fallback",
            cost_model="local_no_key",
            requires_api_key=False,
            api_key_env_var=None,
            api_key_present=False,
            no_key_fallback_available=True,
            status="LOCAL_CACHE_READY",
            confidence_points=8,
            notes=(
                "Use for rate-limit protection, reproducibility, and audit history.",
            ),
        ),
    )


def _confidence_grade(score: int) -> str:
    if score >= 85:
        return "HIGH_FREE_STACK"
    if score >= 70:
        return "MEDIUM_HIGH_FREE_STACK"
    if score >= 55:
        return "MEDIUM_FREE_STACK"
    return "LOW_SOURCE_CONFIDENCE"


def build_free_research_api_router_weekly_policy_result(
    *,
    current_date: str | None = None,
    operating_mode: str = MODE_DAILY_CHECK_IN,
    approval_ticket_path: str | Path = DEFAULT_APPROVAL_TICKET_PATH,
    stock_universe_path: str | Path = DEFAULT_STOCK_UNIVERSE_PATH,
    stock_signals_path: str | Path = DEFAULT_STOCK_SIGNALS_PATH,
    ranked_stocks_path: str | Path = DEFAULT_RANKED_STOCKS_PATH,
    root: str | Path = ".",
    max_age_days: int = 7,
    env: Mapping[str, str] | None = None,
    action_brief_builder: Callable[..., ThreeLaneDailyActionBriefResult] = build_three_lane_daily_action_brief_result,
    upstream_three_lane_result: ThreeLaneDailyActionBriefResult | None = None,
) -> FreeResearchApiRouterWeeklyPolicyResult:
    current_date_text = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []

    if _parse_date(current_date_text) is None:
        blockers.append("current_date must use YYYY-MM-DD format.")

    if operating_mode not in {MODE_DAILY_CHECK_IN, MODE_WEEKLY_BUY_PREP}:
        blockers.append("operating_mode must be daily_check_in or weekly_buy_prep.")

    resolved_ticket = _resolve_path(approval_ticket_path, root)
    resolved_universe = _resolve_path(stock_universe_path, root)
    resolved_signals = _resolve_path(stock_signals_path, root)
    resolved_ranked = _resolve_path(ranked_stocks_path, root)

    if not _is_under(resolved_ticket, root, "outputs"):
        blockers.append("approval ticket path must remain under outputs/.")
    for label, path in (
        ("stock universe path", resolved_universe),
        ("stock signals path", resolved_signals),
        ("ranked stocks path", resolved_ranked),
    ):
        if not _is_under(path, root, "jarvis/local"):
            blockers.append(f"{label} must remain under jarvis/local/.")

    action_result = upstream_three_lane_result
    if action_result is None and not blockers:
        weekly_mode = operating_mode == MODE_WEEKLY_BUY_PREP
        action_result = action_brief_builder(
            current_date=current_date_text,
            approval_ticket_path=approval_ticket_path,
            stock_universe_path=stock_universe_path,
            stock_signals_path=stock_signals_path,
            ranked_stocks_path=ranked_stocks_path,
            root=root,
            max_age_days=max_age_days,
            run_stock_bridge=weekly_mode,
            write_stock_ticket=weekly_mode,
            bootstrap_stock_universe=weekly_mode,
            write_stock_signals=weekly_mode,
            write_ranked_stocks=weekly_mode,
        )

    if action_result is not None:
        action_blockers = tuple(getattr(action_result, "blockers", ()) or ())
        action_warnings = tuple(getattr(action_result, "warnings", ()) or ())
        if operating_mode == MODE_DAILY_CHECK_IN:
            action_warnings = tuple(
                warning for warning in action_warnings if warning != "stock bridge was not run."
            )
        blockers.extend(action_blockers)
        warnings.extend(action_warnings)
        action_status = str(getattr(action_result, "status", ""))
        if "BLOCKED" in action_status:
            blockers.append("three-lane daily action brief was blocked.")
        elif action_warnings and ("READY" not in action_status or "REVIEW_REQUIRED" in action_status):
            warnings.append("three-lane daily action brief requires review.")

    providers = build_research_provider_statuses(env)
    source_confidence_score = min(100, sum(provider.confidence_points for provider in providers))
    source_confidence_grade = _confidence_grade(source_confidence_score)
    free_stack_sufficient = source_confidence_score >= 70 and source_confidence_grade != "LOW_SOURCE_CONFIDENCE"

    if not free_stack_sufficient:
        warnings.append("free research source stack confidence is below weekly investing threshold.")

    unique_blockers = _dedupe(blockers)
    unique_warnings = _dedupe(warnings)

    daily_check_in_only = operating_mode == MODE_DAILY_CHECK_IN
    weekly_buy_preparation_allowed = (
        operating_mode == MODE_WEEKLY_BUY_PREP
        and not unique_blockers
        and not unique_warnings
        and free_stack_sufficient
    )
    manual_buy_action_today = weekly_buy_preparation_allowed

    if unique_blockers:
        status = STATUS_BLOCKED
        router_status = ROUTER_BLOCKED
    elif unique_warnings:
        status = STATUS_REVIEW_REQUIRED
        router_status = ROUTER_REVIEW_REQUIRED
    else:
        status = STATUS_READY
        router_status = ROUTER_READY

    return FreeResearchApiRouterWeeklyPolicyResult(
        status=status,
        router_status=router_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        operating_mode=operating_mode,
        daily_check_in_only=daily_check_in_only,
        weekly_buy_preparation_allowed=weekly_buy_preparation_allowed,
        manual_buy_action_today=manual_buy_action_today,
        source_confidence_score=source_confidence_score,
        source_confidence_grade=source_confidence_grade,
        free_stack_sufficient_for_weekly_investing=free_stack_sufficient,
        paid_api_required_now=False,
        broker_api_required_now=False,
        provider_statuses=providers,
        approval_ticket_path=str(resolved_ticket),
        stock_universe_path=str(resolved_universe),
        stock_signals_path=str(resolved_signals),
        ranked_stocks_path=str(resolved_ranked),
        upstream_three_lane_result=action_result,
        crypto_candidate=getattr(action_result, "crypto_candidate", None),
        crypto_amount_eur=getattr(action_result, "crypto_amount_eur", None),
        etf_symbol=getattr(action_result, "etf_symbol", None),
        etf_amount_eur=getattr(action_result, "etf_amount_eur", None),
        stock_symbol=getattr(action_result, "stock_symbol", None),
        stock_manual_amount_required=getattr(action_result, "stock_manual_amount_required", None),
        stock_approved_for_purchase=getattr(action_result, "stock_approved_for_purchase", None),
        recommendation_quality_current_data=not unique_blockers and not unique_warnings,
        allocation_mutation=False,
        approval_ticket_mutation=(
            operating_mode == MODE_WEEKLY_BUY_PREP
            and bool(getattr(action_result, "approval_ticket_mutation", False))
        ),
        portfolio_state_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_data_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        final_user_buy_action_required=True,
        blockers=unique_blockers,
        warnings=unique_warnings,
    )


def format_free_research_api_router_weekly_policy(result: FreeResearchApiRouterWeeklyPolicyResult) -> str:
    lines = [
        "J.A.R.V.I.S. Free Research API Router + Weekly Policy",
        f"status: {result.status}",
        f"router status: {result.router_status}",
        f"current date: {result.current_date}",
        f"operating mode: {result.operating_mode}",
        f"daily check-in only: {result.daily_check_in_only}",
        f"weekly buy preparation allowed: {result.weekly_buy_preparation_allowed}",
        f"manual buy action today: {result.manual_buy_action_today}",
        f"source confidence score: {result.source_confidence_score}",
        f"source confidence grade: {result.source_confidence_grade}",
        f"free stack sufficient for weekly investing: {result.free_stack_sufficient_for_weekly_investing}",
        f"paid API required now: {result.paid_api_required_now}",
        f"broker API required now: {result.broker_api_required_now}",
        "",
        "Operating policy:",
        "- daily mode is read-only check-ins, source quality, drift/risk review, and finance analysis",
        "- weekly mode is for manual buy preparation",
        "- free APIs/no-key official sources are used first, but missing optional research keys reduce confidence honestly",
        "- paid APIs are not required until the router proves a free-data gap",
        "- broker APIs are not required for research and remain outside execution",
        "",
        "Three-lane snapshot:",
        f"- Crypto: {result.crypto_candidate or 'none'} / EUR {result.crypto_amount_eur:,.2f}" if result.crypto_amount_eur is not None else f"- Crypto: {result.crypto_candidate or 'none'} / amount none",
        f"- ETF/fund: {result.etf_symbol or 'none'} / EUR {result.etf_amount_eur:,.2f}" if result.etf_amount_eur is not None else f"- ETF/fund: {result.etf_symbol or 'none'} / amount none",
        f"- Individual stock: {result.stock_symbol or 'none'} / manual amount required: {result.stock_manual_amount_required} / approved: {result.stock_approved_for_purchase}",
        "",
        "Free-first provider router:",
    ]

    for provider in result.provider_statuses:
        key_text = "n/a" if provider.api_key_env_var is None else f"{provider.api_key_env_var} present={provider.api_key_present}"
        lines.append(
            f"- {provider.provider_id}: {provider.status}; lane={provider.lane}; role={provider.role}; {key_text}"
        )

    lines.extend(
        [
            "",
            "Safety:",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
            f"- portfolio state mutation: {result.portfolio_state_mutation}",
            f"- buy request created: {result.buy_request_created}",
            "- no broker connection",
            "- no credentials",
            "- no private account data ingestion",
            "- no orders created",
            "- no trades executed",
            "- final real-world buy remains manual outside J.A.R.V.I.S.",
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
    parser = argparse.ArgumentParser(description="Run the safe free research API router and weekly policy.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--daily", action="store_true", help="Run daily check-in mode.")
    mode.add_argument("--weekly-buy-prep", action="store_true", help="Run weekly manual buy preparation mode.")
    mode.add_argument("--safety-check", action="store_true", help="Verify that a buy command is blocked.")
    mode.add_argument("--voice-command", help="Run one custom typed Jarvis command through the safe local voice handler.")
    mode.add_argument("--demo", action="store_true", help="Show demo typed Jarvis commands.")
    parser.add_argument("--current-date", default=None, help="Optional YYYY-MM-DD date for reproducible readiness checks.")
    parser.add_argument("--approval-ticket-path", default=DEFAULT_APPROVAL_TICKET_PATH)
    parser.add_argument("--stock-universe-path", default=DEFAULT_STOCK_UNIVERSE_PATH)
    parser.add_argument("--stock-signals-path", default=DEFAULT_STOCK_SIGNALS_PATH)
    parser.add_argument("--ranked-stocks-path", default=DEFAULT_RANKED_STOCKS_PATH)
    parser.add_argument("--max-age-days", type=int, default=7)
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    if args.voice_command:
        print(build_safety_check_console_output(args.voice_command))
        return 0

    if args.demo:
        print("Available typed Jarvis commands:")
        for command in DEFAULT_COMMAND_SAMPLES:
            print(f"- {command}")
        return 0

    operating_mode = MODE_WEEKLY_BUY_PREP if args.weekly_buy_prep else MODE_DAILY_CHECK_IN
    result = build_free_research_api_router_weekly_policy_result(
        current_date=args.current_date,
        operating_mode=operating_mode,
        approval_ticket_path=args.approval_ticket_path,
        stock_universe_path=args.stock_universe_path,
        stock_signals_path=args.stock_signals_path,
        ranked_stocks_path=args.ranked_stocks_path,
        max_age_days=args.max_age_days,
    )
    print(format_free_research_api_router_weekly_policy(result))
    return 0 if result.status != STATUS_BLOCKED else 1


if __name__ == "__main__":
    raise SystemExit(main())