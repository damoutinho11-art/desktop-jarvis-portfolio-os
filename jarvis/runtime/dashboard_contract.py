from __future__ import annotations

import argparse
import html
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.full_system_audit import build_full_system_audit_result
from jarvis.runtime.finance_intelligence_core import build_finance_intelligence_core_result
from jarvis.runtime.manual_holdings_update import DEFAULT_MANUAL_HOLDINGS_PATH
from jarvis.runtime.live_news_fetcher import DEFAULT_LIVE_NEWS_CACHE_PATH
from jarvis.runtime.product_api import _preserve_tracked_approval_ticket, build_product_api_result
from jarvis.runtime.jarvis_session_memory import (
    DEFAULT_SESSION_MEMORY_PATH,
    build_safe_session_snapshot,
    load_session_memory,
    summarize_session_memory,
)
from jarvis.runtime.what_changed_since_last_time import build_what_changed_since_last_time_result

STATUS_READY = "JARVIS_V140_0_DASHBOARD_DAILY_UI_CLEANUP_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V99_0_DASHBOARD_CONTRACT_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/dashboard_contract_latest.json"
DEFAULT_DASHBOARD_PATH = "outputs/dashboard_latest.html"


@dataclass(frozen=True)
class DashboardContractResult:
    status: str
    current_date: str
    dashboard_contract_ready: bool
    dashboard_html_written: bool
    dashboard_path: str
    backend_ready: bool
    product_api_ready: bool
    full_audit_ready: bool
    product_recommendations_allowed: bool
    manual_only: bool
    sections: dict[str, Any]
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return dict(getattr(value, "__dict__", {}))


def _money(value: Any) -> str:
    try:
        return f"EUR {float(value or 0.0):.2f}"
    except Exception:
        return "EUR 0.00"


def _dedupe(items: list[str]) -> list[str]:
    return list(dict.fromkeys(item for item in items if item))


def _html_list(items: list[Any]) -> str:
    if not items:
        return "<li>none</li>"
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _build_sections(
    product_api: dict[str, Any],
    audit: dict[str, Any],
    finance: dict[str, Any],
    *,
    current_date: str = "2026-06-20",
) -> dict[str, Any]:
    week = product_api.get("week_plan", {}) or {}
    data = product_api.get("data_readiness", {}) or {}
    news = product_api.get("news_coverage", {}) or {}
    safety = product_api.get("safety_status", {}) or {}
    holdings = product_api.get("manual_holdings", {}) or {}
    live_news = product_api.get("live_news_context", {}) or {}
    memory_snapshot = load_session_memory()
    current_snapshot = build_safe_session_snapshot(current_date=current_date, product_api_result=product_api)
    changed = build_what_changed_since_last_time_result(
        current_date=current_date,
        current_snapshot=current_snapshot,
    )

    return {
        "status": {
            "title": "System Status",
            "dashboard_ready": product_api.get("dashboard_ready"),
            "chat_ready": product_api.get("chat_ready"),
            "voice_ready": product_api.get("voice_ready"),
            "audit_verdict": audit.get("audit_verdict"),
            "blockers": list(audit.get("blockers", []) or []),
        },
        "week_plan": {
            "title": "Weekly Manual Plan",
            "monthly_contribution_eur": week.get("monthly_contribution_eur"),
            "emergency_top_up_eur": week.get("emergency_top_up_eur"),
            "crypto_eur": week.get("crypto_eur"),
            "etf_fund_eur": week.get("etf_fund_eur"),
            "individual_stock_eur": week.get("individual_stock_eur"),
            "selected_instruments": list(week.get("selected_instruments", []) or []),
        },
        "data": {
            "title": "Data Readiness",
            "data_readiness_ready": data.get("data_readiness_ready"),
            "missing_data": list(data.get("missing_data", []) or []),
            "missing_universe": list(data.get("missing_universe", []) or []),
            "crypto_candidates": data.get("crypto_candidate_count"),
            "etf_candidates": data.get("etf_candidate_count"),
            "stock_candidates": data.get("stock_candidate_count"),
        },
        "news": {
            "title": "News Coverage",
            "news_coverage_ready": news.get("news_coverage_ready"),
            "live_news_fetch_enabled": news.get("live_news_fetch_enabled"),
            "manual_review_required": news.get("manual_review_required"),
            "covered_categories": list(news.get("covered_categories", []) or []),
            "live_news_status": live_news.get("status"),
            "cache_loaded": live_news.get("cache_loaded"),
            "headline_count": live_news.get("usable_count"),
            "source_failures": list(live_news.get("source_failures", []) or []),
            "top_headlines": list(live_news.get("top_headlines", []) or []),
            "warnings": list(live_news.get("warnings", []) or []),
        },
        "finance_intelligence": {
            "title": "Finance Intelligence",
            "data_trust_summary": dict(finance.get("data_trust_summary", {}) or {}),
            "selected_instrument_coverage": list(finance.get("selected_instrument_coverage", []) or []),
            "market_movement_summary": finance.get("market_movement_summary"),
            "etf_gap_summary": finance.get("etf_gap_summary"),
            "fx_summary": dict(finance.get("fx_summary", {}) or {}),
            "news_summary": dict(finance.get("news_summary", {}) or {}),
            "manual_qa_checklist": list(finance.get("manual_qa_checklist", []) or []),
        },
        "manual_holdings": {
            "title": "Manual Holdings",
            "status": holdings.get("status"),
            "holdings_ready": holdings.get("holdings_ready"),
            "file_exists": holdings.get("file_exists"),
            "positions_count": holdings.get("positions_count"),
            "confirmed_positions_count": holdings.get("confirmed_positions_count"),
            "total_cost_basis_eur": holdings.get("total_cost_basis_eur"),
            "total_market_value_eur": holdings.get("total_market_value_eur"),
            "total_market_value_available": holdings.get("total_market_value_available"),
            "positions": list(holdings.get("positions", []) or []),
            "warnings": list(holdings.get("warnings", []) or []),
        },
        "safety": {
            "title": "Safety",
            "safety_check_blocked_execution": safety.get("safety_check_blocked_execution"),
            "manual_approval_required": safety.get("manual_approval_required"),
            "execution_forbidden": safety.get("execution_forbidden"),
            "broker_connection": safety.get("broker_connection"),
            "credentials_used": safety.get("credentials_used"),
            "order_created": safety.get("order_created"),
            "trade_executed": safety.get("trade_executed"),
        },
        "audit": {
            "title": "Full Audit",
            "formula_invariants_ready": audit.get("formula_invariants_ready"),
            "data_readiness_ready": audit.get("data_readiness_ready"),
            "news_coverage_ready": audit.get("news_coverage_ready"),
            "safety_ready": audit.get("safety_ready"),
            "speed_ready": audit.get("speed_ready"),
            "warnings": list(audit.get("warnings", []) or []),
        },
        "session_memory": {
            "title": "Last Session",
            "first_run": memory_snapshot is None,
            "memory_exists": bool(memory_snapshot),
            "memory_path": DEFAULT_SESSION_MEMORY_PATH,
            "summary_text": summarize_session_memory(memory_snapshot),
            "safe_derived_summary_only": True,
        },
        "what_changed": {
            "title": "What Changed Since Last Time",
            "first_run": changed.first_run,
            "comparison_available": changed.comparison_available,
            "summary_text": changed.summary_text,
            "changes": list(changed.changes or []),
            "manual_only": changed.manual_only,
            "blockers": list(changed.blockers or []),
            "warnings": list(changed.warnings or []),
        },
    }


def _display_ready_label(result: DashboardContractResult) -> str:
    return "READY FOR MANUAL USE" if result.dashboard_contract_ready and not result.blockers else "REVIEW REQUIRED"


def _yes_no(value: Any) -> str:
    return "Yes" if bool(value) else "No"


def _friendly_lane(value: Any) -> str:
    mapping = {
        "crypto": "Crypto",
        "etf_fund": "ETF/Fund",
        "individual_stock": "Stock",
        "emergency": "Emergency",
    }
    return mapping.get(str(value), str(value or ""))


def _friendly_market_status(item: Mapping[str, Any]) -> tuple[str, str]:
    classification = str(item.get("classification") or "").strip().lower()
    freshness = str(item.get("freshness") or "").strip().lower()
    next_action = str(item.get("next_action") or "").strip().lower()
    trusted = bool(item.get("trusted_quote"))

    if "placeholder" in classification:
        return "Setup note", "Sleeve placeholder only; not a tradable instrument."
    if "missing" in classification or "missing" in next_action:
        return "Needs quote source", "Quote source is not connected yet."
    if "partial" in classification or "partial" in freshness or "unavailable" in freshness:
        return "Needs review", "Movement data is partial or unavailable."
    if trusted and any(token in freshness for token in ("ready", "fresh", "current")):
        return "Ready", "Fresh trusted public quote available."
    if trusted:
        return "Usable", "Trusted quote is available; check source freshness before acting."
    return "Needs review", "Check source freshness before any manual action."



def _friendly_freshness(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return "check source"
    if "partial" in text or "unavailable" in text:
        return "needs review"
    if "ready" in text or "fresh" in text or "current" in text:
        return "fresh"
    return str(value)


def _headline_tag(item: Mapping[str, Any]) -> str:
    entities = [str(value) for value in (item.get("entity_tags") or []) if value]
    lanes = [str(value) for value in (item.get("lane_tags") or []) if value]
    joined = " ".join(entities + lanes).lower()
    if "btc" in joined or "bitcoin" in joined:
        return "BTC"
    if "eth" in joined or "ethereum" in joined:
        return "ETH"
    if "msft" in joined or "microsoft" in joined:
        return "MSFT"
    if "etf" in joined or "fund" in joined:
        return "ETF"
    if "macro" in joined or "rates" in joined or "central bank" in joined:
        return "Macro"
    if "market" in joined:
        return "Market"
    return "Market"


def _calm_dashboard_notes(result: DashboardContractResult, holdings: Mapping[str, Any], news: Mapping[str, Any]) -> list[str]:
    notes: list[str] = []
    if result.blockers:
        notes.append("Review required. Resolve blockers before using the manual plan.")
    else:
        notes.append("Ready for manual use. No blockers found.")

    if not news.get("cache_loaded"):
        notes.append("Live news is optional context. Missing headlines do not block today's plan.")
    if not holdings.get("file_exists"):
        notes.append("Holdings can be added manually after external buys; missing holdings do not block daily use.")

    notes.append("Manual-only safety is active: no broker, credentials, orders, trades, buy/sell requests, or auto-approval.")
    return _dedupe(notes)[:4]


def _render_legacy_dashboard_html(result: DashboardContractResult) -> str:
    sections = result.sections
    status = sections["status"]
    week = sections["week_plan"]
    data = sections["data"]
    news = sections["news"]
    finance = sections["finance_intelligence"]
    holdings = sections["manual_holdings"]
    safety = sections["safety"]
    audit = sections["audit"]
    memory = sections.get("session_memory", {})
    changed = sections.get("what_changed", {})

    rows = []
    for item in week.get("selected_instruments", []) or []:
        rows.append(
            "<tr>"
            f"<td>{html.escape(_friendly_lane(item.get('lane', '')))}</td>"
            f"<td>{html.escape(str(item.get('symbol', '')))}</td>"
            f"<td>{html.escape(_money(item.get('amount_eur')))}</td>"
            "</tr>"
        )
    selected_rows = "".join(rows) if rows else "<tr><td colspan='3'>none</td></tr>"
    selected_items = week.get("selected_instruments", []) or []

    def lane_summary(lane: str) -> str:
        labels = []
        for item in selected_items:
            if str(item.get("lane", "")) == lane:
                labels.append(f"{item.get('symbol', '')} {_money(item.get('amount_eur'))}")
        return ", ".join(labels) if labels else "none"

    crypto_summary = lane_summary("crypto")
    etf_summary = lane_summary("etf_fund")
    stock_summary = lane_summary("individual_stock")
    trust = finance.get("data_trust_summary", {}) or {}

    coverage_rows = []
    for item in finance.get("selected_instrument_coverage", []) or []:
        status_label, note = _friendly_market_status(item)
        coverage_rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('symbol', '')))}</td>"
            f"<td>{html.escape(status_label)}</td>"
            f"<td>{html.escape(_friendly_freshness(item.get('freshness')))}</td>"
            f"<td>{html.escape(note)}</td>"
            "</tr>"
        )
    coverage_table = "".join(coverage_rows) if coverage_rows else "<tr><td colspan='4'>none</td></tr>"

    holdings_rows = []
    for item in holdings.get("positions", []) or []:
        holdings_rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('symbol', '')))}</td>"
            f"<td>{html.escape(str(item.get('name', '')))}</td>"
            f"<td>{html.escape(_friendly_lane(item.get('lane', '')))}</td>"
            f"<td>{html.escape(str(item.get('quantity', '')))}</td>"
            f"<td>{html.escape(_money(item.get('cost_basis_eur')))}</td>"
            f"<td>{html.escape(_money(item.get('market_value_eur')) if item.get('market_value_eur') is not None else 'not available')}</td>"
            f"<td>{html.escape(str(item.get('platform', '')))}</td>"
            "</tr>"
        )
    if holdings_rows:
        holdings_table = "".join(holdings_rows)
    else:
        holdings_table = "<tr><td colspan='7'>holdings not entered yet</td></tr>"
    holdings_market_value = (
        _money(holdings.get("total_market_value_eur"))
        if holdings.get("total_market_value_available")
        else "not available"
    )
    headline_chips = []
    for item in (news.get("top_headlines", []) or [])[:8]:
        tag = _headline_tag(item)
        headline_chips.append(
            "<article class=\"headline-chip\">"
            f"<span class=\"headline-tag\">{html.escape(tag)}</span>"
            f"<strong>{html.escape(str(item.get('title', '')))}</strong>"
            f"<span>{html.escape(str(item.get('source') or 'public source'))} | "
            f"{html.escape(str(item.get('freshness_status') or 'freshness unknown'))}</span>"
            f"<a href=\"{html.escape(str(item.get('url') or '#'))}\">source</a>"
            "</article>"
        )
    headline_items = "".join(headline_chips)
    headline_ticker = (
        "<div class=\"headline-ticker\" aria-label=\"Market headlines ticker\">"
        f"<div class=\"headline-track\">{headline_items}{headline_items}</div>"
        "</div>"
        if headline_chips
        else (
            "<div class=\"headline-ticker headline-ticker-empty\">"
            "<strong>Headlines are quiet - not blocking today's manual plan.</strong>"
            "<span>Public headlines are optional context and never an action signal.</span>"
            "</div>"
        )
    )
    source_failures = len(news.get("source_failures") or [])
    setup_note = (
        "Holdings file detected. Review positions before any manual external action."
        if holdings.get("file_exists")
        else "Holdings not entered yet. Use the template command after Diogo buys manually outside J.A.R.V.I.S."
    )
    display_status = _display_ready_label(result)
    display_status_class = "ok" if display_status == "READY FOR MANUAL USE" else "warn"
    blockers_label = "None — ready for manual use" if not result.blockers else "; ".join(result.blockers)
    daily_notes = "".join(f"<li>{html.escape(item)}</li>" for item in _calm_dashboard_notes(result, holdings, news))
    memory_label = "First run" if memory.get("first_run", True) else "Memory found"
    memory_summary = str(
        memory.get("summary_text")
        or "First run: no previous J.A.R.V.I.S. session memory exists yet. This is safe and not a blocker."
    )
    changed_label = "First run" if changed.get("first_run", True) else "Comparison ready"
    changed_summary = str(
        changed.get("summary_text")
        or "Since last time: first run. No previous safe snapshot exists yet, so no comparison is available."
    )
    changed_rows = _html_list(list(changed.get("changes") or ["No previous safe snapshot exists yet."]))

    css = """
    :root { color-scheme: light; --bg:#f6f7f4; --panel:#ffffff; --ink:#17202a; --muted:#687386; --line:#dfe4dc; --ok:#0f7a45; --warn:#9a6500; --risk:#b42318; --accent:#2f6f63; --soft:#eef6f2; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Segoe UI, Arial, sans-serif; background:var(--bg); color:var(--ink); }
    header, main { max-width:1180px; margin:0 auto; padding:20px; }
    .app-nav { display:flex; flex-wrap:wrap; gap:8px; margin-bottom:18px; }
    .app-nav a { color:#253244; text-decoration:none; border:1px solid var(--line); border-radius:8px; padding:10px 12px; font-weight:800; background:#fff; }
    .app-nav a.active, .app-nav a:hover, .app-nav a:focus { background:#17202a; color:#fff; border-color:#17202a; outline:none; }
    h1 { margin:0 0 6px; font-size:clamp(28px,4vw,42px); letter-spacing:-.02em; }
    h2 { margin:0 0 14px; font-size:20px; letter-spacing:-.01em; }
    p { color:#39475a; line-height:1.5; }
    .subtitle { color:var(--muted); }
    .safety-banner { margin-top:18px; border:1px solid #9bd8b8; background:#eaf8f1; color:#10492e; border-radius:14px; padding:14px 16px; font-weight:700; }
    .status-hero { margin-top:18px; background:var(--soft); border:1px solid #bddccc; border-radius:18px; padding:18px; display:grid; gap:6px; }
    .status-hero strong { font-size:clamp(28px,4vw,44px); letter-spacing:-.03em; }
    main { display:grid; grid-template-columns:repeat(12,1fr); gap:16px; padding-top:0; }
    .card { grid-column:span 6; background:var(--panel); border:1px solid var(--line); border-radius:16px; padding:18px; box-shadow:0 1px 2px rgba(20,32,50,.05); }
    .wide { grid-column:span 12; }
    .grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }
    .metric { min-height:74px; border-left:4px solid var(--accent); padding:9px 11px; background:#fafbf8; border-radius:10px; }
    .label { color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.06em; }
    .value { font-size:21px; font-weight:750; margin-top:5px; overflow-wrap:anywhere; }
    .ok { color:var(--ok); }
    .warn { color:var(--warn); }
    .risk { color:var(--risk); }
    .badge { display:inline-block; padding:4px 8px; border-radius:999px; background:#edf7fa; color:#0b5e72; border:1px solid #b8dfe8; font-size:12px; font-weight:700; }
    .headline-ticker { width:100%; overflow:hidden; border:1px solid var(--line); background:#fbfcf9; border-radius:12px; padding:10px; }
    .headline-track { display:flex; width:max-content; gap:10px; animation:ticker-scroll 44s linear infinite; }
    .headline-ticker:hover .headline-track { animation-play-state:paused; }
    .headline-chip { min-width:280px; max-width:380px; border:1px solid var(--line); background:#fff; border-radius:10px; padding:11px; display:grid; gap:5px; }
    .headline-chip span, .action-card span, .headline-ticker-empty span { color:var(--muted); font-size:13px; }
    .headline-tag { width:max-content; color:#174f43 !important; background:#e6f4ee; border:1px solid #bee1d1; border-radius:999px; padding:3px 7px; font-size:11px !important; font-weight:800; }
    .headline-ticker-empty { display:grid; gap:5px; }
    @keyframes ticker-scroll { from { transform:translateX(0); } to { transform:translateX(-50%); } }
    .action-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:10px; }
    .action-card { padding:13px; background:#fafbf8; border:1px solid var(--line); border-radius:12px; display:grid; gap:6px; }
    .action-card strong { font-size:15px; }
    code { font-family:Cascadia Mono, Consolas, monospace; background:#eef2f7; border:1px solid #d7deea; border-radius:6px; padding:3px 6px; font-size:12px; }
    table { width:100%; border-collapse:collapse; margin-top:14px; }
    th, td { text-align:left; padding:10px 8px; border-bottom:1px solid var(--line); vertical-align:top; }
    th { color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.06em; }
    ul { margin:0; padding-left:20px; color:#39475a; }
    @media (max-width:820px) { header, main { padding:14px; } .card { grid-column:span 12; } .grid, .action-grid { grid-template-columns:1fr; } .value { font-size:19px; } }
    """

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>J.A.R.V.I.S. Portfolio Dashboard</title>
<style>{css}</style>
</head>
<body>
<header>
<nav class="app-nav" aria-label="J.A.R.V.I.S. app navigation">
<a class="active" href="/dashboard">Dashboard</a>
<a href="/chat">Chat</a>
<a href="/briefing">Briefing</a>
<a href="/memory">Memory</a>
<a href="/safety">Safety</a>
</nav>
<h1>J.A.R.V.I.S. Portfolio Dashboard</h1>
<div class="subtitle">Generated locally from the read-only product API. Current date: {html.escape(result.current_date)}</div>
<div class="safety-banner">Manual-only safety: Diogo buys outside J.A.R.V.I.S. No broker. No credentials. No orders. No trades. No buy/sell requests. No auto-approval.</div>
<div class="status-hero"><span>App Status</span><strong class="{display_status_class}">{display_status}</strong><span>{html.escape(blockers_label)}</span></div>
</header>
<main>
<section class="card wide">
<h2>Today's Manual Plan</h2>
<div class="grid">
<div class="metric"><div class="label">Emergency Top-up</div><div class="value">{_money(week.get("emergency_top_up_eur"))}</div></div>
<div class="metric"><div class="label">Crypto</div><div class="value">{_money(week.get("crypto_eur"))}</div></div>
<div class="metric"><div class="label">ETF/Fund</div><div class="value">{_money(week.get("etf_fund_eur"))}</div></div>
<div class="metric"><div class="label">Stock</div><div class="value">{_money(week.get("individual_stock_eur"))}</div></div>
<div class="metric"><div class="label">Safety Block</div><div class="value ok">{_yes_no(safety.get("safety_check_blocked_execution"))}</div></div>
<div class="metric"><div class="label">Blockers</div><div class="value ok">{len(result.blockers)}</div></div>
</div>
<ul>
<li>Crypto checklist: {html.escape(crypto_summary)}</li>
<li>ETF/fund checklist: {html.escape(etf_summary)}</li>
<li>Stock checklist: {html.escape(stock_summary)}</li>
<li>Execution remains outside J.A.R.V.I.S.; this dashboard is read-only.</li>
</ul>
</section>

<section class="card wide">
<h2>Daily Notes</h2>
<ul>{daily_notes}</ul>
</section>

<section class="card"><h2>Last Session</h2>
<p><span class="badge">{html.escape(memory_label)}</span></p>
<p>{html.escape(memory_summary)}</p>
<ul>
<li>Safe derived summaries only.</li>
<li>Memory path: <code>{html.escape(str(memory.get("memory_path") or DEFAULT_SESSION_MEMORY_PATH))}</code></li>
</ul>
</section>

<section class="card"><h2>What Changed Since Last Time</h2>
<p><span class="badge">{html.escape(changed_label)}</span></p>
<p>{html.escape(changed_summary)}</p>
<ul>{changed_rows}</ul>
</section>

<section class="card wide">
<h2>Weekly Manual Plan</h2>
<div class="grid">
<div class="metric"><div class="label">Monthly</div><div class="value">{_money(week.get("monthly_contribution_eur"))}</div></div>
<div class="metric"><div class="label">Emergency</div><div class="value">{_money(week.get("emergency_top_up_eur"))}</div></div>
<div class="metric"><div class="label">Crypto</div><div class="value">{_money(week.get("crypto_eur"))}</div></div>
<div class="metric"><div class="label">ETF/Fund</div><div class="value">{_money(week.get("etf_fund_eur"))}</div></div>
<div class="metric"><div class="label">Stock</div><div class="value">{_money(week.get("individual_stock_eur"))}</div></div>
</div>
<table><thead><tr><th>Lane</th><th>Instrument</th><th>Amount</th></tr></thead><tbody>{selected_rows}</tbody></table>
</section>

<section class="card wide">
<h2>Holdings Status</h2>
<div class="grid">
<div class="metric"><div class="label">File Entered</div><div class="value warn">{_yes_no(holdings.get("file_exists"))}</div></div>
<div class="metric"><div class="label">Holdings Ready</div><div class="value warn">{_yes_no(holdings.get("holdings_ready"))}</div></div>
<div class="metric"><div class="label">Positions</div><div class="value">{html.escape(str(holdings.get("positions_count")))}</div></div>
<div class="metric"><div class="label">Confirmed</div><div class="value">{html.escape(str(holdings.get("confirmed_positions_count")))}</div></div>
<div class="metric"><div class="label">Cost Basis</div><div class="value">{_money(holdings.get("total_cost_basis_eur"))}</div></div>
<div class="metric"><div class="label">Market Value</div><div class="value">{html.escape(holdings_market_value)}</div></div>
</div>
<ul>
<li>{html.escape(setup_note)}</li>
<li>This section is read-only and records Diogo manual entries only.</li>
</ul>
<table><thead><tr><th>Symbol</th><th>Name</th><th>Lane</th><th>Quantity</th><th>Cost Basis</th><th>Market Value</th><th>Platform</th></tr></thead><tbody>{holdings_table}</tbody></table>
</section>

<section class="card"><h2>Market Data</h2><ul>
<li>Ready: {_yes_no(data.get("data_readiness_ready"))}</li>
<li>Crypto candidates: {data.get("crypto_candidates")}</li>
<li>ETF/fund candidates: {data.get("etf_candidates")}</li>
<li>Stock candidates: {data.get("stock_candidates")}</li>
<li>Missing data: {html.escape(", ".join(data.get("missing_data") or []) or "none")}</li>
<li>Missing universe: {html.escape(", ".join(data.get("missing_universe") or []) or "none")}</li>
</ul></section>

<section class="card"><h2>Market Headlines</h2>
<div class="grid">
<div class="metric"><div class="label">Headlines</div><div class="value">{html.escape(str(news.get("headline_count") or 0))}</div></div>
<div class="metric"><div class="label">Cache Loaded</div><div class="value">{_yes_no(news.get("cache_loaded"))}</div></div>
<div class="metric"><div class="label">Source Failures</div><div class="value warn">{source_failures}</div></div>
</div>
<p><span class="badge">Possible context only</span> Public headlines are optional and never recommend action from headline alone.</p>
{headline_ticker}
</section>

<section class="card wide"><h2>Market Movement</h2>
<div class="grid">
<div class="metric"><div class="label">Trusted Records</div><div class="value">{html.escape(str(trust.get("trusted_records")))}</div></div>
<div class="metric"><div class="label">Review Records</div><div class="value warn">{html.escape(str(trust.get("partial_records")))}</div></div>
<div class="metric"><div class="label">FX Conversion</div><div class="value warn">{_yes_no((finance.get("fx_summary") or {}).get("conversion_available"))}</div></div>
</div>
<p>{html.escape(str(finance.get("market_movement_summary") or ""))}</p>
<table><thead><tr><th>Symbol</th><th>Status</th><th>Freshness</th><th>Note</th></tr></thead><tbody>{coverage_table}</tbody></table>
</section>

<section class="card"><h2>Risk & Safety</h2><ul>
<li>Safety-check blocked execution: {_yes_no(safety.get("safety_check_blocked_execution"))}</li>
<li>Manual approval required: {_yes_no(safety.get("manual_approval_required"))}</li>
<li>Execution forbidden: {_yes_no(safety.get("execution_forbidden"))}</li>
<li>Broker connection: {_yes_no(safety.get("broker_connection"))}</li>
<li>Credentials used: {_yes_no(safety.get("credentials_used"))}</li>
<li>Order created: {_yes_no(safety.get("order_created"))}</li>
<li>Trade executed: {_yes_no(safety.get("trade_executed"))}</li>
</ul></section>

<section class="card"><h2>System Checks</h2><ul>
<li>Plan math ready: {_yes_no(audit.get("formula_invariants_ready"))}</li>
<li>Data ready: {_yes_no(audit.get("data_readiness_ready"))}</li>
<li>News context ready: {_yes_no(audit.get("news_coverage_ready"))}</li>
<li>Safety ready: {_yes_no(audit.get("safety_ready"))}</li>
<li>Speed ready: {_yes_no(audit.get("speed_ready"))}</li>
</ul></section>

<section class="card wide"><h2>How to Use Today</h2><ul>
<li>Open J.A.R.V.I.S. and read the manual plan.</li>
<li>Check quote freshness and headline context if you want extra confidence.</li>
<li>Make any buy manually outside J.A.R.V.I.S. only after your own review.</li>
<li>Update holdings manually after an external buy.</li>
</ul></section>
<section class="card wide"><h2>Useful Actions</h2>
<div class="action-grid">
<div class="action-card"><strong>Open J.A.R.V.I.S.</strong><code>Start Jarvis.bat</code><span>Launch dashboard and chat.</span></div>
<div class="action-card"><strong>Update holdings</strong><code>--holdings-template</code><span>Create the manual holdings template.</span></div>
<div class="action-card"><strong>Safety check</strong><code>--safety-check</code><span>Confirm execution stays blocked.</span></div>
</div></section>
</main>
</body>
</html>
"""


def render_dashboard_html(result: DashboardContractResult) -> str:
    from jarvis.runtime.premium_command_center_dashboard import render_command_center_dashboard_html

    return render_command_center_dashboard_html(result)


def build_dashboard_contract_result(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    dashboard_path: str | Path = DEFAULT_DASHBOARD_PATH,
    write_report: bool = False,
    write_dashboard: bool = False,
    manual_holdings_path: str | Path = DEFAULT_MANUAL_HOLDINGS_PATH,
    live_news_cache_path: str | Path = DEFAULT_LIVE_NEWS_CACHE_PATH,
) -> DashboardContractResult:
    with _preserve_tracked_approval_ticket():
        return _build_dashboard_contract_result_unprotected(
            current_date=current_date,
            output_path=output_path,
            dashboard_path=dashboard_path,
            write_report=write_report,
            write_dashboard=write_dashboard,
            manual_holdings_path=manual_holdings_path,
            live_news_cache_path=live_news_cache_path,
        )


def _build_dashboard_contract_result_unprotected(
    *,
    current_date: str = "2026-06-18",
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
    dashboard_path: str | Path = DEFAULT_DASHBOARD_PATH,
    write_report: bool = False,
    write_dashboard: bool = False,
    manual_holdings_path: str | Path = DEFAULT_MANUAL_HOLDINGS_PATH,
    live_news_cache_path: str | Path = DEFAULT_LIVE_NEWS_CACHE_PATH,
) -> DashboardContractResult:
    started = time.perf_counter()
    product_api_result = build_product_api_result(
        current_date=current_date,
        manual_holdings_path=manual_holdings_path,
        live_news_cache_path=live_news_cache_path,
    )
    product_api_elapsed_seconds = round(time.perf_counter() - started, 3)
    product_api = _plain(product_api_result)
    audit = _plain(
        build_full_system_audit_result(
            current_date=current_date,
            product_api_result=product_api_result,
            product_api_elapsed_seconds=product_api_elapsed_seconds,
        )
    )
    finance_result = build_finance_intelligence_core_result(current_date=current_date)
    finance = _plain(finance_result)
    sections = _build_sections(product_api, audit, finance, current_date=current_date)
    safety = sections["safety"]

    manual_only = bool(
        safety.get("manual_approval_required")
        and safety.get("execution_forbidden")
        and safety.get("safety_check_blocked_execution")
        and not safety.get("broker_connection")
        and not safety.get("credentials_used")
        and not safety.get("order_created")
        and not safety.get("trade_executed")
    )
    backend_ready = bool(
        product_api.get("dashboard_ready")
        and product_api.get("chat_ready")
        and product_api.get("voice_ready")
        and audit.get("dashboard_chat_voice_backend_ready")
    )

    blockers = []
    blockers.extend(str(item) for item in (product_api.get("blockers") or []))
    blockers.extend(str(item) for item in (audit.get("blockers") or []))
    if not backend_ready:
        blockers.append("dashboard_backend_not_ready")
    if not manual_only:
        blockers.append("manual_only_safety_not_ready")
    blockers = _dedupe(blockers)

    warnings = _dedupe(
        [
            "dashboard contract is local/static and does not start a web server",
            "dashboard HTML is generated only when write_dashboard=True or when the local /dashboard route explicitly serves the generated artifact",
        ]
        + [str(item) for item in (product_api.get("warnings") or [])]
        + [str(item) for item in (audit.get("warnings") or [])]
        + [str(item) for item in (finance.get("warnings") or [])]
    )

    ready = not blockers
    result = DashboardContractResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        current_date=current_date,
        dashboard_contract_ready=ready,
        dashboard_html_written=bool(write_dashboard),
        dashboard_path=str(dashboard_path),
        backend_ready=backend_ready,
        product_api_ready=bool(product_api.get("api_ready")),
        full_audit_ready=not bool(audit.get("blockers")),
        product_recommendations_allowed=bool(product_api.get("product_recommendations_allowed")),
        manual_only=manual_only,
        sections=sections,
        warnings=warnings,
        blockers=blockers,
        report_written=bool(write_report),
        report_path=str(output_path),
    )

    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if write_dashboard:
        Path(dashboard_path).parent.mkdir(parents=True, exist_ok=True)
        Path(dashboard_path).write_text(render_dashboard_html(result), encoding="utf-8")

    return result



def _v127_clean_dashboard_warnings(warnings: list[str]) -> list[str]:
    """Keep the dashboard contract user-facing while preserving safety honesty."""
    if not warnings:
        return ["none"]

    drop_contains = (
        "dashboard HTML is generated only when",
        "data readiness status aggregates existing",
        "this command does not fetch data",
        "fast product summary uses dynamic candidate scoring",
        "full system audit is read-only",
        "finance intelligence core is read-only",
        "news is a contract/readiness layer",
        "product-mode audit warning:",
        "ignored non-data preflight blocker",
    )

    cleaned: list[str] = []
    for warning in warnings:
        text = str(warning).strip()
        if not text:
            continue
        if any(fragment in text for fragment in drop_contains):
            continue
        if text not in cleaned:
            cleaned.append(text)

    priority = [
        "dashboard contract is local/static and does not start a web server",
        "product API is read-only and exposes dashboard/chat/voice payloads only",
        "manual approval remains required; no execution path is created",
        "product mode is manual-only; Diogo performs any buy outside J.A.R.V.I.S.",
        "no broker, credentials, order, trade, or auto-approval path is enabled",
        "live news fetching is not enabled in v98; this is a policy/readiness coverage contract",
        "manual review remains required before acting on any headline or recommendation",
        "local cache data can be stale; source/as_of/freshness must be shown in answers",
    ]

    ordered = [item for item in priority if item in cleaned]
    ordered.extend(item for item in cleaned if item not in ordered)

    return ordered[:8] or ["none"]



def format_dashboard_contract(result: DashboardContractResult) -> str:
    dashboard_open_path = result.dashboard_path.replace("/", "\\")
    lines = [
        "J.A.R.V.I.S. DASHBOARD CONTRACT",
        f"status: {result.status}",
        f"current date: {result.current_date}",
        f"dashboard contract ready: {result.dashboard_contract_ready}",
        f"backend ready: {result.backend_ready}",
        f"product API ready: {result.product_api_ready}",
        f"full audit ready: {result.full_audit_ready}",
        f"product recommendations allowed: {result.product_recommendations_allowed}",
        f"manual-only safety: {result.manual_only}",
        f"dashboard html written: {result.dashboard_html_written}",
        f"dashboard path: {result.dashboard_path}",
        "",
        "OPEN DASHBOARD:",
        f"- start .\\{dashboard_open_path}",
        "",
        "QA CHECKLIST:",
        "- verify Weekly Manual Plan is visible",
        "- verify BTC, ETH, ETF/fund, and MSFT rows are visible",
        "- verify Manual Holdings is visible and missing holdings are a review note",
        "- verify News and Safety sections are visible",
        "- verify Blockers is none before manual action",
        "",
        "SECTIONS:",
    ]
    lines.extend(f"- {key}: {value.get('title')}" for key, value in result.sections.items())
    lines.append("")
    lines.append("WARNINGS:")
    lines.extend(f"- {item}" for item in _v127_clean_dashboard_warnings(list(result.warnings or [])))
    lines.append("")
    lines.append("BLOCKERS:")
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    lines.append("")
    lines.append(f"report written: {result.report_written}")
    lines.append(f"report path: {result.report_path}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build J.A.R.V.I.S. dashboard contract.")
    parser.add_argument("--dashboard-contract", action="store_true")
    parser.add_argument("--current-date", default="2026-06-18")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--write-dashboard", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--dashboard-path", default=DEFAULT_DASHBOARD_PATH)
    parser.add_argument("--holdings-path", default=DEFAULT_MANUAL_HOLDINGS_PATH)
    parser.add_argument("--news-cache-path", default=DEFAULT_LIVE_NEWS_CACHE_PATH)
    args = parser.parse_args(argv)

    result = build_dashboard_contract_result(
        current_date=args.current_date,
        output_path=args.output_path,
        dashboard_path=args.dashboard_path,
        write_report=args.write_report,
        write_dashboard=args.write_dashboard,
        manual_holdings_path=args.holdings_path,
        live_news_cache_path=args.news_cache_path,
    )
    print(format_dashboard_contract(result))
    return 0 if not result.blockers else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "DashboardContractResult",
    "build_dashboard_contract_result",
    "render_dashboard_html",
    "format_dashboard_contract",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
