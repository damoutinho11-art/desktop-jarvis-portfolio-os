"""J.A.R.V.I.S. v59.0 personal finance contribution decision bridge.

Combines confirmed monthly expenses, manual portfolio snapshot, platform intake,
public evidence coverage, and dynamic target policy into one manual-only monthly
contribution decision.

Safety invariant: Automated research. Manual trust. Manual approval. No execution.
"""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any, Mapping, Sequence

from jarvis.jarvis_v16_0_real_daily_readiness_gate import build_safety_check_console_output
from jarvis.jarvis_v45_0_free_research_cache_evidence_pack_bridge import DEFAULT_EVIDENCE_PACK_PATH
from jarvis.runtime.dynamic_target_policy import DEFAULT_AGE_YEARS, build_dynamic_target_policy_result
from jarvis.runtime.manual_portfolio_snapshot import DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH
from jarvis.runtime.manual_cost_basis_intake import DEFAULT_MANUAL_COST_BASIS_PATH, build_manual_cost_basis_intake_result
from jarvis.runtime.portfolio_exposure_audit import DEFAULT_IDEAL_EMERGENCY_MONTHS, DEFAULT_MIN_EMERGENCY_MONTHS

STATUS_READY = "JARVIS_V62_0_MANUAL_COST_BASIS_BRIDGE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V62_0_MANUAL_COST_BASIS_BRIDGE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V62_0_MANUAL_COST_BASIS_BRIDGE_BLOCKED_SAFE"
BRIDGE_READY = "PERSONAL_FINANCE_CONTRIBUTION_BRIDGE_READY"
BRIDGE_REVIEW_REQUIRED = "PERSONAL_FINANCE_CONTRIBUTION_BRIDGE_REVIEW_REQUIRED"
BRIDGE_BLOCKED = "PERSONAL_FINANCE_CONTRIBUTION_BRIDGE_BLOCKED"

DEFAULT_MONTHLY_EXPENSES_PATH = "jarvis/local/monthly_expenses.local.json"
DEFAULT_LIGHTYEAR_INSTRUMENT_UNIVERSE_PATH = "jarvis/local/lightyear_instrument_universe.local.json"
DEFAULT_CRYPTO_FACILITY_TERMS_PATH = "jarvis/local/crypto_facility_terms.local.json"
DEFAULT_LEGACY_MIGRATION_REVIEW_PATH = "jarvis/local/legacy_migration_review.local.json"


def _today_iso() -> str:
    return date.today().isoformat()


def _round2(value: Any) -> float:
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return 0.0


def _dedupe(items: Sequence[str]) -> list[str]:
    return list(dict.fromkeys(str(item) for item in items if str(item)))


def _read_json(path: str | Path) -> tuple[bool, bool, dict[str, Any], str | None]:
    resolved = Path(path)
    if not resolved.exists():
        return False, False, {}, None
    try:
        payload = json.loads(resolved.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        return True, False, {}, str(exc)
    if not isinstance(payload, dict):
        return True, False, {}, "JSON root is not an object"
    return True, True, payload, None


def _num(payload: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        value = payload.get(key)
        if value in (None, ""):
            continue
        try:
            return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _expense_summary(payload: Mapping[str, Any]) -> dict[str, Any]:
    contribution = _num(payload, "planned_monthly_contribution_eur", "monthly_contribution_eur", "target_monthly_contribution_eur")
    survival = _num(payload, "survival_monthly_expenses_eur", "survival_expenses_eur")
    normal = _num(payload, "normal_monthly_expenses_eur", "monthly_expenses_eur")
    flexible = _num(payload, "flexible_monthly_expenses_eur", "flexible_expenses_eur")

    categories = payload.get("categories")
    if categories is None:
        categories = payload.get("expense_categories")
    if categories is None:
        categories = payload.get("monthly_expense_categories")
    if normal is None and isinstance(categories, (dict, list)):
        items = categories.values() if isinstance(categories, dict) else categories
        survival_sum = normal_extra_sum = flexible_sum = 0.0
        for item in items:
            if not isinstance(item, Mapping):
                continue
            amount = _round2(_num(item, "monthly_eur", "monthly_amount_eur", "amount_eur", "monthly_cost_eur", "eur_per_month"))
            typ = str(item.get("type", item.get("expense_type", item.get("category_type", "normal")))).lower()
            if typ == "survival":
                survival_sum += amount
            elif typ == "flexible":
                flexible_sum += amount
            else:
                normal_extra_sum += amount
        survival = _round2(survival if survival is not None else survival_sum)
        flexible = _round2(flexible if flexible is not None else flexible_sum)
        normal = _round2(survival + normal_extra_sum + flexible)

    return {
        "confirmed": bool(payload.get("expenses_confirmed")) and not bool(payload.get("is_template")),
        "monthly_contribution_eur": _round2(contribution) if contribution is not None else None,
        "normal_monthly_expenses_eur": _round2(normal) if normal is not None else None,
        "survival_monthly_expenses_eur": _round2(survival) if survival is not None else None,
        "flexible_monthly_expenses_eur": _round2(flexible) if flexible is not None else None,
        "minimum_emergency_months": float(_num(payload, "minimum_emergency_months", "min_emergency_months") or DEFAULT_MIN_EMERGENCY_MONTHS),
        "ideal_emergency_months": float(_num(payload, "ideal_emergency_months") or DEFAULT_IDEAL_EMERGENCY_MONTHS),
    }


def _confirmed_file(key: str, path: str | Path, confirm_keys: Sequence[str], note: str) -> tuple[dict[str, Any], dict[str, Any], str | None]:
    present, loaded, payload, error = _read_json(path)
    template = bool(payload.get("is_template")) if loaded else False
    confirmed = loaded and not template and any(bool(payload.get(item)) for item in confirm_keys)
    return {
        "key": key,
        "path": str(path),
        "present": present,
        "loaded": loaded,
        "template": template,
        "confirmed": confirmed,
        "note": note,
    }, payload, error


def _evidence_coverage(path: str | Path) -> tuple[bool, bool, bool, bool, str | None]:
    present, loaded, payload, error = _read_json(path)
    if not loaded:
        return present, loaded, False, False, error
    items: list[Mapping[str, Any]] = []
    for key in ("evidence_items", "items", "evidence"):
        value = payload.get(key)
        if isinstance(value, list):
            items.extend(item for item in value if isinstance(item, Mapping))
    crypto = etf_fx = False
    for item in items:
        if item.get("usable_for_research", True) is False:
            continue
        text = " ".join(str(item.get(k, "")) for k in ("provider_id", "lane", "data_kind", "status", "source_quality")).lower()
        crypto = crypto or "coingecko" in text or "crypto" in text
        etf_fx = etf_fx or "ecb" in text or "fx" in text or "etf" in text or "official_free_source_ready" in text
    if not items:
        text = json.dumps(payload, sort_keys=True).lower()
        crypto = "coingecko" in text or "public_crypto_source_ready" in text
        etf_fx = "ecb" in text or "official_free_source_ready" in text or "fx" in text
    return present, loaded, crypto, etf_fx, None


def _target_amount(dynamic: Any, lane: str) -> float:
    for item in getattr(dynamic, "proposed_contribution_targets", ()):
        if getattr(item, "lane", None) == lane:
            return _round2(getattr(item, "amount_eur", 0.0))
    return 0.0


def _crypto_ceiling(dynamic: Any) -> float | None:
    for band in getattr(dynamic, "target_bands", ()):
        if getattr(band, "lane", None) == "crypto":
            return getattr(band, "target_ceiling_pct", None)
    return None


def _manual_actions(*, allowed: bool, cash_platform: str, crypto_platform: str, investment_platform: str, emergency: float, crypto: float, etf: float, stock: float) -> list[dict[str, Any]]:
    return [
        {"step": 1, "platform": cash_platform, "lane": "cash_reserve", "amount_eur": emergency, "allowed_by_decision": allowed and emergency > 0, "review_only": False, "manual_only": True, "action": "Top up the protected emergency fund manually.", "note": "Emergency reserve is protected cash, not an investment sleeve."},
        {"step": 2, "platform": crypto_platform, "lane": "crypto", "amount_eur": crypto, "allowed_by_decision": allowed and crypto > 0, "review_only": False, "manual_only": True, "action": "Review refreshed crypto evidence, then buy manually only if satisfied.", "note": "Crypto remains a volatile satellite sleeve; no automatic purchase is allowed."},
        {"step": 3, "platform": investment_platform, "lane": "stock_fund_etf", "amount_eur": etf, "allowed_by_decision": allowed and etf > 0, "review_only": False, "manual_only": True, "action": "Review ETF/fund evidence, then buy manually only if satisfied.", "note": "Core ETF/fund investing is the main long-term compounding sleeve."},
        {"step": 4, "platform": investment_platform, "lane": "individual_stock", "amount_eur": stock, "allowed_by_decision": False, "review_only": True, "manual_only": True, "action": "Keep individual-stock contribution at 0 EUR.", "note": "Individual stocks stay review-only until stock-specific evidence is complete."},
        {"step": 5, "platform": "legacy_observed", "lane": "legacy_positions", "amount_eur": 0.0, "allowed_by_decision": False, "review_only": True, "manual_only": True, "action": "Observe legacy positions only; do not sell or migrate automatically.", "note": "Selling or migration requires a separate legacy migration review."},
    ]


def build_personal_finance_contribution_bridge_result(
    *,
    current_date: str | None = None,
    monthly_expenses_path: str | Path = DEFAULT_MONTHLY_EXPENSES_PATH,
    snapshot_path: str | Path = DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH,
    evidence_pack_path: str | Path = DEFAULT_EVIDENCE_PACK_PATH,
    lightyear_instrument_universe_path: str | Path = DEFAULT_LIGHTYEAR_INSTRUMENT_UNIVERSE_PATH,
    crypto_facility_terms_path: str | Path = DEFAULT_CRYPTO_FACILITY_TERMS_PATH,
    legacy_migration_review_path: str | Path = DEFAULT_LEGACY_MIGRATION_REVIEW_PATH,
    manual_cost_basis_path: str | Path = DEFAULT_MANUAL_COST_BASIS_PATH,
    age_years: int | None = DEFAULT_AGE_YEARS,
    new_investing_platform: str = "Lightyear",
    crypto_platform: str = "LHV",
    cash_emergency_platform: str = "LHV",
) -> dict[str, Any]:
    effective_date = current_date or _today_iso()
    blockers: list[str] = []
    warnings: list[str] = []
    flags: list[str] = ["PERSONAL_FINANCE_CONTRIBUTION_BRIDGE_MANUAL_ONLY"]

    expenses_present, expenses_loaded, expenses_payload, expenses_error = _read_json(monthly_expenses_path)
    if expenses_error:
        blockers.append("monthly_expenses_file_unreadable")
    if not expenses_present:
        blockers.append("monthly_expenses_file_missing")
    elif not expenses_loaded:
        blockers.append("monthly_expenses_file_not_loaded")
    expenses = _expense_summary(expenses_payload)
    if not expenses["confirmed"]:
        blockers.append("monthly_expenses_not_confirmed")
    if expenses["monthly_contribution_eur"] is None:
        blockers.append("planned_monthly_contribution_missing")
    if expenses["normal_monthly_expenses_eur"] is None:
        blockers.append("normal_monthly_expenses_missing")

    lightyear, _, lightyear_error = _confirmed_file("lightyear_instrument_universe", lightyear_instrument_universe_path, ("platform_data_confirmed", "confirmed", "instruments_confirmed"), "required for trusted weekly manual ETF/fund action")
    crypto_terms, crypto_payload, crypto_error = _confirmed_file("crypto_facility_terms", crypto_facility_terms_path, ("terms_confirmed", "confirmed", "facility_terms_confirmed"), "required for trusted weekly manual crypto action")
    legacy, _, legacy_error = _confirmed_file("legacy_migration_review", legacy_migration_review_path, ("migration_review_confirmed", "confirmed", "review_confirmed"), "not required for new-money monthly contribution; required before selling or migration")
    if lightyear_error:
        blockers.append("lightyear_instrument_universe_unreadable")
    if crypto_error:
        blockers.append("crypto_facility_terms_unreadable")
    if legacy_error:
        warnings.append("legacy_migration_review_unreadable")
    if not lightyear["confirmed"]:
        blockers.append("lightyear_instrument_universe_not_confirmed")
    if not crypto_terms["confirmed"]:
        blockers.append("crypto_facility_terms_not_confirmed")
    if not legacy["confirmed"]:
        warnings.append("legacy_migration_review_not_confirmed")

    evidence_present, evidence_loaded, crypto_evidence, etf_fx_evidence, evidence_error = _evidence_coverage(evidence_pack_path)
    if evidence_error:
        blockers.append("evidence_pack_unreadable")
    if not evidence_present:
        blockers.append("evidence_pack_missing")
    elif not evidence_loaded:
        blockers.append("evidence_pack_not_loaded")
    if not crypto_evidence:
        blockers.append("crypto_public_evidence_missing")
    if not etf_fx_evidence:
        blockers.append("etf_fx_public_evidence_missing")

    dynamic = build_dynamic_target_policy_result(
        current_date=effective_date,
        snapshot_path=snapshot_path,
        monthly_contribution_eur=expenses["monthly_contribution_eur"],
        monthly_expenses_eur=expenses["normal_monthly_expenses_eur"],
        minimum_emergency_months=expenses["minimum_emergency_months"],
        ideal_emergency_months=expenses["ideal_emergency_months"],
        age_years=age_years,
    )
    blockers.extend(getattr(dynamic, "blockers", ()))
    warnings.extend(getattr(dynamic, "warnings", ()))
    flags.extend(getattr(dynamic, "policy_flags", ()))

    crypto_amount = _target_amount(dynamic, "crypto")
    etf_amount = _target_amount(dynamic, "stock_fund_etf")
    stock_amount = _target_amount(dynamic, "individual_stock")
    emergency_top_up = _round2(getattr(dynamic, "suggested_monthly_emergency_top_up_eur", 0.0))
    investable = _round2(getattr(dynamic, "suggested_monthly_investment_after_emergency_eur", 0.0))
    facility_crypto_cap = _num(crypto_payload, "max_crypto_allocation_percent", "crypto_cap_percent")
    dynamic_crypto_ceiling = _crypto_ceiling(dynamic)
    if facility_crypto_cap is not None and dynamic_crypto_ceiling is not None and facility_crypto_cap != dynamic_crypto_ceiling:
        warnings.append("crypto facility cap differs from dynamic target ceiling; using stricter v54 target policy until risk model reconciliation")

    manual_cost_basis = build_manual_cost_basis_intake_result(
        current_date=effective_date,
        manual_cost_basis_path=manual_cost_basis_path,
        write_template=False,
    )
    manual_cost_basis_ready = bool(manual_cost_basis.get("cost_basis_ready_for_full_allocation_data_gate"))
    if manual_cost_basis_ready:
        warnings.append("manual cost basis confirmed locally; still no selling, migration, orders, or trades")

    full_allocation_requirements = [
        "correlation_risk_model",
        "stock_specific_public_evidence",
    ]
    if not manual_cost_basis_ready:
        full_allocation_requirements.append("manual_cost_basis")
    if not legacy["confirmed"]:
        full_allocation_requirements.insert(0, "legacy_migration_review")

    unique_blockers = _dedupe(blockers)
    trusted_allowed = not unique_blockers
    status = STATUS_BLOCKED if unique_blockers else STATUS_REVIEW_REQUIRED if warnings or flags else STATUS_READY
    bridge_status = BRIDGE_BLOCKED if unique_blockers else BRIDGE_REVIEW_REQUIRED if warnings or flags else BRIDGE_READY

    return {
        "status": status,
        "bridge_status": bridge_status,
        "current_date": effective_date,
        "trusted_monthly_contribution_decision_allowed": trusted_allowed,
        "full_allocation_allowed": False,
        "monthly_expenses_path": str(monthly_expenses_path),
        "monthly_expenses_confirmed": expenses["confirmed"],
        "monthly_contribution_eur": expenses["monthly_contribution_eur"],
        "normal_monthly_expenses_eur": expenses["normal_monthly_expenses_eur"],
        "survival_monthly_expenses_eur": expenses["survival_monthly_expenses_eur"],
        "flexible_monthly_expenses_eur": expenses["flexible_monthly_expenses_eur"],
        "snapshot_path": str(snapshot_path),
        "snapshot_ready": bool(getattr(dynamic, "snapshot_ready", False)),
        "current_emergency_fund_eur": _round2(getattr(dynamic, "emergency_fund_current_eur", 0.0)),
        "emergency_months_covered": getattr(dynamic, "emergency_months_covered", None),
        "minimum_emergency_target_eur": getattr(dynamic, "minimum_emergency_target_eur", None),
        "ideal_emergency_target_eur": getattr(dynamic, "ideal_emergency_target_eur", None),
        "suggested_monthly_emergency_top_up_eur": emergency_top_up,
        "suggested_monthly_investment_after_emergency_eur": investable,
        "crypto_amount_eur": crypto_amount,
        "stock_fund_etf_amount_eur": etf_amount,
        "individual_stock_amount_eur": stock_amount,
        "crypto_facility_max_allocation_percent": facility_crypto_cap,
        "dynamic_crypto_target_ceiling_percent": dynamic_crypto_ceiling,
        "platform_files": [lightyear, crypto_terms, legacy],
        "evidence_pack_path": str(evidence_pack_path),
        "evidence_pack_present": evidence_present,
        "evidence_pack_loaded": evidence_loaded,
        "manual_cost_basis_path": str(manual_cost_basis_path),
        "manual_cost_basis_ready": manual_cost_basis_ready,
        "manual_cost_basis_confirmed_positions_count": manual_cost_basis.get("confirmed_positions_count"),
        "manual_cost_basis_total_market_value_eur": manual_cost_basis.get("total_market_value_eur"),
        "manual_cost_basis_total_cost_basis_eur": manual_cost_basis.get("total_cost_basis_eur"),
        "manual_cost_basis_total_unrealized_gain_loss_eur": manual_cost_basis.get("total_unrealized_gain_loss_eur"),
        "crypto_public_evidence_covered": crypto_evidence,
        "etf_fx_public_evidence_covered": etf_fx_evidence,
        "manual_actions": _manual_actions(allowed=trusted_allowed, cash_platform=cash_emergency_platform, crypto_platform=crypto_platform, investment_platform=new_investing_platform, emergency=emergency_top_up, crypto=crypto_amount, etf=etf_amount, stock=stock_amount),
        "policy_flags": _dedupe(flags),
        "full_allocation_still_requires": full_allocation_requirements,
        "blockers": unique_blockers,
        "warnings": _dedupe(warnings),
        "allocation_mutation": False,
        "approval_ticket_mutation": False,
        "evidence_pack_mutation": False,
        "local_cache_mutation": False,
        "portfolio_state_mutation": False,
        "buy_request_created": False,
        "broker_connection_forbidden": True,
        "credentials_forbidden": True,
        "private_account_data_ingestion_forbidden": True,
        "order_creation_forbidden": True,
        "no_trades_executed": True,
        "final_user_buy_action_required": True,
    }


def format_personal_finance_contribution_bridge(result: Mapping[str, Any]) -> str:
    lines = [
        "J.A.R.V.I.S. PERSONAL FINANCE CONTRIBUTION DECISION BRIDGE",
        f"status: {result['status']}",
        f"bridge status: {result['bridge_status']}",
        f"current date: {result['current_date']}",
        f"trusted monthly contribution decision allowed: {result['trusted_monthly_contribution_decision_allowed']}",
        f"full allocation allowed: {result['full_allocation_allowed']}",
        "",
        "Personal finance inputs:",
        f"- monthly expenses path: {result['monthly_expenses_path']}",
        f"- monthly expenses confirmed: {result['monthly_expenses_confirmed']}",
        f"- monthly contribution EUR: {result['monthly_contribution_eur']}",
        f"- normal monthly expenses EUR: {result['normal_monthly_expenses_eur']}",
        f"- survival monthly expenses EUR: {result['survival_monthly_expenses_eur']}",
        f"- flexible monthly expenses EUR: {result['flexible_monthly_expenses_eur']}",
        "",
        "Emergency and contribution decision:",
        f"- current emergency fund EUR: {result['current_emergency_fund_eur']}",
        f"- emergency months covered: {result['emergency_months_covered']}",
        f"- minimum emergency target EUR: {result['minimum_emergency_target_eur']}",
        f"- ideal emergency target EUR: {result['ideal_emergency_target_eur']}",
        f"- recommended emergency top-up EUR: {result['suggested_monthly_emergency_top_up_eur']}",
        f"- recommended investable amount EUR: {result['suggested_monthly_investment_after_emergency_eur']}",
        f"- recommended crypto amount EUR: {result['crypto_amount_eur']}",
        f"- recommended ETF/fund amount EUR: {result['stock_fund_etf_amount_eur']}",
        f"- recommended individual stock amount EUR: {result['individual_stock_amount_eur']}",
        "",
        "Crypto policy reconciliation:",
        f"- crypto facility max allocation percent: {result['crypto_facility_max_allocation_percent']}",
        f"- dynamic target crypto ceiling percent: {result['dynamic_crypto_target_ceiling_percent']}",
        "",
        "Platform readiness:",
    ]
    for item in result["platform_files"]:
        lines.append(f"- {item['key']}: present={item['present']}; loaded={item['loaded']}; template={item['template']}; confirmed={item['confirmed']}; path={item['path']}")
        lines.append(f"  note: {item['note']}")
    lines.extend([
        "",
        "Evidence readiness:",
        f"- evidence pack path: {result['evidence_pack_path']}",
        f"- evidence pack present: {result['evidence_pack_present']}",
        f"- evidence pack loaded: {result['evidence_pack_loaded']}",
        f"- crypto public evidence covered: {result['crypto_public_evidence_covered']}",
        f"- ETF/FX public evidence covered: {result['etf_fx_public_evidence_covered']}",
        "",
        "Manual cost basis readiness:",
        f"- manual cost basis path: {result['manual_cost_basis_path']}",
        f"- manual cost basis ready: {result['manual_cost_basis_ready']}",
        f"- confirmed positions count: {result['manual_cost_basis_confirmed_positions_count']}",
        f"- total market value EUR: {result['manual_cost_basis_total_market_value_eur']}",
        f"- total cost basis EUR: {result['manual_cost_basis_total_cost_basis_eur']}",
        f"- total unrealized gain/loss EUR: {result['manual_cost_basis_total_unrealized_gain_loss_eur']}",
        "",
        "Manual contribution actions:",
    ])
    for action in result["manual_actions"]:
        lines.append(f"{action['step']}. {action['platform']} / {action['lane']}: {action['amount_eur']} EUR; allowed by decision={action['allowed_by_decision']}; review only={action['review_only']}")
        lines.append(f"   action: {action['action']}")
        lines.append(f"   note: {action['note']}")
    lines.append("")
    lines.append("Full allocation still requires:")
    lines.extend(f"- {item}" for item in result["full_allocation_still_requires"])
    lines.extend([
        "",
        "Safety:",
        f"- allocation mutation: {result['allocation_mutation']}",
        f"- approval ticket mutation: {result['approval_ticket_mutation']}",
        f"- evidence pack mutation: {result['evidence_pack_mutation']}",
        f"- local cache mutation: {result['local_cache_mutation']}",
        f"- portfolio state mutation: {result['portfolio_state_mutation']}",
        f"- buy request created: {result['buy_request_created']}",
        "- no broker connection",
        "- no credentials",
        "- no private account data ingestion",
        "- no orders created",
        "- no trades executed",
        f"- final user buy action required: {result['final_user_buy_action_required']}",
        "",
        "Policy flags:",
    ])
    lines.extend(f"- {item}" for item in result["policy_flags"]) if result["policy_flags"] else lines.append("- none")
    if result["blockers"]:
        lines.extend(["", "Blockers:"] + [f"- {item}" for item in result["blockers"]])
    else:
        lines.append("blockers: none")
    if result["warnings"]:
        lines.extend(["", "Warnings:"] + [f"- {item}" for item in result["warnings"]])
    else:
        lines.append("warnings: none")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. v59 personal finance contribution bridge")
    parser.add_argument("--personal-finance-contribution-bridge", action="store_true")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--monthly-expenses-path", default=DEFAULT_MONTHLY_EXPENSES_PATH)
    parser.add_argument("--manual-portfolio-snapshot-path", default=DEFAULT_MANUAL_PORTFOLIO_SNAPSHOT_PATH)
    parser.add_argument("--evidence-pack-path", default=DEFAULT_EVIDENCE_PACK_PATH)
    parser.add_argument("--lightyear-instrument-universe-path", default=DEFAULT_LIGHTYEAR_INSTRUMENT_UNIVERSE_PATH)
    parser.add_argument("--crypto-facility-terms-path", default=DEFAULT_CRYPTO_FACILITY_TERMS_PATH)
    parser.add_argument("--legacy-migration-review-path", default=DEFAULT_LEGACY_MIGRATION_REVIEW_PATH)
    parser.add_argument("--manual-cost-basis-path", default=DEFAULT_MANUAL_COST_BASIS_PATH)
    parser.add_argument("--age-years", type=int, default=DEFAULT_AGE_YEARS)
    parser.add_argument("--new-investing-platform", default="Lightyear")
    parser.add_argument("--crypto-platform", default="LHV")
    parser.add_argument("--cash-emergency-platform", default="LHV")
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)
    if args.safety_check:
        print(build_safety_check_console_output())
        return 0
    result = build_personal_finance_contribution_bridge_result(
        current_date=args.current_date,
        monthly_expenses_path=args.monthly_expenses_path,
        snapshot_path=args.manual_portfolio_snapshot_path,
        evidence_pack_path=args.evidence_pack_path,
        lightyear_instrument_universe_path=args.lightyear_instrument_universe_path,
        crypto_facility_terms_path=args.crypto_facility_terms_path,
        legacy_migration_review_path=args.legacy_migration_review_path,
        manual_cost_basis_path=args.manual_cost_basis_path,
        age_years=args.age_years,
        new_investing_platform=args.new_investing_platform,
        crypto_platform=args.crypto_platform,
        cash_emergency_platform=args.cash_emergency_platform,
    )
    print(format_personal_finance_contribution_bridge(result))
    return 0


__all__ = [
    "BRIDGE_BLOCKED",
    "BRIDGE_READY",
    "BRIDGE_REVIEW_REQUIRED",
    "DEFAULT_MONTHLY_EXPENSES_PATH",
    "STATUS_BLOCKED",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "build_personal_finance_contribution_bridge_result",
    "format_personal_finance_contribution_bridge",
    "main",
]
