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

STATUS_READY = "JARVIS_V127_0_DASHBOARD_UX_FINAL_POLISH_READY_SAFE"
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


def _build_sections(product_api: dict[str, Any], audit: dict[str, Any], finance: dict[str, Any]) -> dict[str, Any]:
    week = product_api.get("week_plan", {}) or {}
    data = product_api.get("data_readiness", {}) or {}
    news = product_api.get("news_coverage", {}) or {}
    safety = product_api.get("safety_status", {}) or {}
    holdings = product_api.get("manual_holdings", {}) or {}
    live_news = product_api.get("live_news_context", {}) or {}

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
    }


def render_dashboard_html(result: DashboardContractResult) -> str:
    sections = result.sections
    status = sections["status"]
    week = sections["week_plan"]
    data = sections["data"]
    news = sections["news"]
    finance = sections["finance_intelligence"]
    holdings = sections["manual_holdings"]
    safety = sections["safety"]
    audit = sections["audit"]

    rows = []
    for item in week.get("selected_instruments", []) or []:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('lane', '')))}</td>"
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
        coverage_rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('symbol', '')))}</td>"
            f"<td>{html.escape(str(item.get('classification', '')))}</td>"
            f"<td>{html.escape(str(item.get('trusted_quote', '')))}</td>"
            f"<td>{html.escape(str(item.get('freshness', '')))}</td>"
            f"<td>{html.escape(str(item.get('next_action', '')))}</td>"
            "</tr>"
        )
    coverage_table = "".join(coverage_rows) if coverage_rows else "<tr><td colspan='5'>none</td></tr>"

    holdings_rows = []
    for item in holdings.get("positions", []) or []:
        holdings_rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('symbol', '')))}</td>"
            f"<td>{html.escape(str(item.get('name', '')))}</td>"
            f"<td>{html.escape(str(item.get('lane', '')))}</td>"
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
    headline_rows = []
    for item in news.get("top_headlines", []) or []:
        headline_rows.append(
            "<li>"
            f"<strong>{html.escape(str(item.get('title', '')))}</strong>"
            f"<span>source={html.escape(str(item.get('source') or 'n/a'))} · "
            f"freshness={html.escape(str(item.get('freshness_status') or 'n/a'))}</span>"
            f"<a href=\"{html.escape(str(item.get('url') or '#'))}\">source</a>"
            "</li>"
        )
    headline_list = "".join(headline_rows) if headline_rows else (
        "<li><strong>No local live news cache yet</strong>"
        "<span>Run live news fetch when you want public headline context; missing news is not a blocker.</span></li>"
    )
    source_failures = len(news.get("source_failures") or [])
    setup_note = (
        "Holdings file detected. Review positions before any manual external action."
        if holdings.get("file_exists")
        else "Holdings not entered yet. Use the template command after Diogo buys manually outside J.A.R.V.I.S."
    )

    css = """
    :root { color-scheme: light; --bg:#f5f7fa; --panel:#ffffff; --ink:#17202a; --muted:#627085; --line:#dbe1ea; --ok:#0f7a45; --warn:#9a6500; --risk:#b42318; --accent:#0b6f88; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:Segoe UI, Arial, sans-serif; background:var(--bg); color:var(--ink); }
    header, main { max-width:1220px; margin:0 auto; padding:20px; }
    h1 { margin:0 0 6px; font-size:clamp(28px,4vw,42px); letter-spacing:0; }
    h2 { margin:0 0 14px; font-size:20px; letter-spacing:0; }
    p { color:#39475a; line-height:1.5; }
    .subtitle { color:var(--muted); }
    .safety-banner { margin-top:18px; border:1px solid #86d4b1; background:#eaf8f1; color:#10492e; border-radius:8px; padding:14px 16px; font-weight:700; }
    main { display:grid; grid-template-columns:repeat(12,1fr); gap:16px; padding-top:0; }
    .card { grid-column:span 6; background:var(--panel); border:1px solid var(--line); border-radius:8px; padding:18px; box-shadow:0 1px 2px rgba(20,32,50,.06); }
    .wide { grid-column:span 12; }
    .grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:12px; }
    .metric { min-height:74px; border-left:4px solid var(--accent); padding:8px 10px; background:#f8fafc; }
    .label { color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.06em; }
    .value { font-size:21px; font-weight:750; margin-top:5px; overflow-wrap:anywhere; }
    .ok { color:var(--ok); }
    .warn { color:var(--warn); }
    .risk { color:var(--risk); }
    .badge { display:inline-block; padding:4px 8px; border-radius:999px; background:#edf7fa; color:#0b5e72; border:1px solid #b8dfe8; font-size:12px; font-weight:700; }
    .headline-list { list-style:none; padding:0; margin:0; display:grid; gap:10px; }
    .headline-list li { border-top:1px solid var(--line); padding-top:10px; display:grid; gap:3px; }
    .headline-list span, .command-list span { color:var(--muted); font-size:13px; }
    .command-list { list-style:none; margin:0; padding:0; display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; }
    .command-list li { padding:10px; background:#f8fafc; border:1px solid var(--line); border-radius:6px; }
    code { font-family:Cascadia Mono, Consolas, monospace; background:#eef2f7; border:1px solid #d7deea; border-radius:4px; padding:2px 5px; }
    table { width:100%; border-collapse:collapse; margin-top:14px; }
    th, td { text-align:left; padding:10px 8px; border-bottom:1px solid var(--line); vertical-align:top; }
    th { color:var(--muted); font-size:11px; text-transform:uppercase; letter-spacing:.06em; }
    ul { margin:0; padding-left:20px; color:#39475a; }
    @media (max-width:820px) { header, main { padding:14px; } .card { grid-column:span 12; } .grid, .command-list { grid-template-columns:1fr; } .value { font-size:19px; } }
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
<h1>J.A.R.V.I.S. Portfolio Dashboard</h1>
<div class="subtitle">Generated locally from the read-only product API. Current date: {html.escape(result.current_date)}</div>
<div class="safety-banner">Manual-only safety: Diogo buys outside J.A.R.V.I.S. No broker connection, credentials, orders, trades, buy/sell requests, or auto-approval.</div>
</header>
<main>
<section class="card wide">
<h2>Today's Manual Plan</h2>
<div class="grid">
<div class="metric"><div class="label">Emergency Top-up</div><div class="value">{_money(week.get("emergency_top_up_eur"))}</div></div>
<div class="metric"><div class="label">Crypto</div><div class="value">{_money(week.get("crypto_eur"))}</div></div>
<div class="metric"><div class="label">ETF/Fund</div><div class="value">{_money(week.get("etf_fund_eur"))}</div></div>
<div class="metric"><div class="label">Stock</div><div class="value">{_money(week.get("individual_stock_eur"))}</div></div>
<div class="metric"><div class="label">Safety</div><div class="value ok">{safety.get("safety_check_blocked_execution")}</div></div>
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
<h2>Top Status / Readiness</h2>
<div class="grid">
<div class="metric"><div class="label">Dashboard</div><div class="value ok">{status.get("dashboard_ready")}</div></div>
<div class="metric"><div class="label">Chat</div><div class="value ok">{status.get("chat_ready")}</div></div>
<div class="metric"><div class="label">Voice</div><div class="value ok">{status.get("voice_ready")}</div></div>
<div class="metric"><div class="label">Audit</div><div class="value warn">{html.escape(str(status.get("audit_verdict")))}</div></div>
<div class="metric"><div class="label">Contract</div><div class="value ok">{result.dashboard_contract_ready}</div></div>
<div class="metric"><div class="label">Manual Only</div><div class="value ok">{result.manual_only}</div></div>
</div>
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
<div class="metric"><div class="label">File Exists</div><div class="value warn">{holdings.get("file_exists")}</div></div>
<div class="metric"><div class="label">Holdings Ready</div><div class="value warn">{holdings.get("holdings_ready")}</div></div>
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
<li>Ready: {data.get("data_readiness_ready")}</li>
<li>Crypto candidates: {data.get("crypto_candidates")}</li>
<li>ETF/fund candidates: {data.get("etf_candidates")}</li>
<li>Stock candidates: {data.get("stock_candidates")}</li>
<li>Missing data: {html.escape(", ".join(data.get("missing_data") or []) or "none")}</li>
<li>Missing universe: {html.escape(", ".join(data.get("missing_universe") or []) or "none")}</li>
</ul></section>

<section class="card"><h2>Live News / Headline Context</h2>
<div class="grid">
<div class="metric"><div class="label">Headlines</div><div class="value">{html.escape(str(news.get("headline_count") or 0))}</div></div>
<div class="metric"><div class="label">Cache Loaded</div><div class="value">{news.get("cache_loaded")}</div></div>
<div class="metric"><div class="label">Source Failures</div><div class="value warn">{source_failures}</div></div>
</div>
<p><span class="badge">Possible context only</span> Headlines do not prove why prices moved. Check source time, URL, and relevance before any manual action.</p>
<ul class="headline-list">{headline_list}</ul>
</section>

<section class="card wide"><h2>Market Movement</h2>
<div class="grid">
<div class="metric"><div class="label">Trusted Records</div><div class="value">{html.escape(str(trust.get("trusted_records")))}</div></div>
<div class="metric"><div class="label">Partial Records</div><div class="value warn">{html.escape(str(trust.get("partial_records")))}</div></div>
<div class="metric"><div class="label">FX Conversion</div><div class="value warn">{html.escape(str((finance.get("fx_summary") or {}).get("conversion_available")))}</div></div>
</div>
<p>{html.escape(str(finance.get("market_movement_summary") or ""))}</p>
<table><thead><tr><th>Symbol</th><th>Classification</th><th>Trusted</th><th>Freshness</th><th>Next Action</th></tr></thead><tbody>{coverage_table}</tbody></table>
</section>

<section class="card"><h2>Risk & Safety</h2><ul>
<li>Safety-check blocked execution: {safety.get("safety_check_blocked_execution")}</li>
<li>Manual approval required: {safety.get("manual_approval_required")}</li>
<li>Execution forbidden: {safety.get("execution_forbidden")}</li>
<li>Broker connection: {safety.get("broker_connection")}</li>
<li>Credentials used: {safety.get("credentials_used")}</li>
<li>Order created: {safety.get("order_created")}</li>
<li>Trade executed: {safety.get("trade_executed")}</li>
</ul></section>

<section class="card"><h2>Audit</h2><ul>
<li>Formula invariants ready: {audit.get("formula_invariants_ready")}</li>
<li>Data readiness ready: {audit.get("data_readiness_ready")}</li>
<li>News coverage ready: {audit.get("news_coverage_ready")}</li>
<li>Safety ready: {audit.get("safety_ready")}</li>
<li>Speed ready: {audit.get("speed_ready")}</li>
</ul></section>

<section class="card wide"><h2>Blockers / Warnings</h2><details open><summary>Review dashboard warnings</summary><ul>{_html_list(result.warnings)}</ul></details></section>
<section class="card wide"><h2>Blockers</h2><ul>{_html_list(result.blockers)}</ul></section>
<section class="card wide"><h2>How to Use Today</h2><ul>
<li>Confirm the weekly manual plan total matches the contribution.</li>
<li>Confirm BTC, ETH, ETF/fund, and stock rows are visible.</li>
<li>Confirm Holdings Status is visible; if missing, it says holdings not entered yet.</li>
<li>Confirm Live News / Headline Context shows source and freshness labels when available.</li>
<li>Confirm Market Movement shows data trust honestly.</li>
<li>Confirm safety shows no broker, credentials, orders, or trades.</li>
</ul></section>
<section class="card wide"><h2>Useful Commands</h2>
<ul class="command-list">
<li><code>Start Jarvis.bat</code><span>Open the local app launcher.</span></li>
<li><code>python .\\jarvis_operator.py --daily-operator --current-date {html.escape(result.current_date)} --skip-refresh</code><span>Run the daily manual operator.</span></li>
<li><code>python .\\jarvis_operator.py --holdings-status --current-date {html.escape(result.current_date)}</code><span>Check manual holdings status.</span></li>
<li><code>python .\\jarvis_operator.py --write-holdings-template --current-date {html.escape(result.current_date)}</code><span>Create the blank holdings template.</span></li>
<li><code>python .\\jarvis_operator.py --post-app-acceptance-gate --current-date {html.escape(result.current_date)}</code><span>Verify the app is ready for manual use.</span></li>
</ul></section>
</main>
</body>
</html>
"""


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
    sections = _build_sections(product_api, audit, finance)
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
