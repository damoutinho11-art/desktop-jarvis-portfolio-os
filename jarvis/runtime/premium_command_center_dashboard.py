"""J.A.R.V.I.S. v162.0 Iron Man command center dashboard renderer."""

from __future__ import annotations

import argparse
import html
from dataclasses import asdict, dataclass
from typing import Any, Mapping

from jarvis.runtime.premium_orbital_design_system import render_shell, render_status_badge
from jarvis.runtime.universe_explorer import build_universe_explorer_result

STATUS_READY = "JARVIS_V162_0_IRON_MAN_COMMAND_CENTER_DASHBOARD_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V162_0_IRON_MAN_COMMAND_CENTER_DASHBOARD_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_PREMIUM_COMMAND_CENTER_DASHBOARD"


@dataclass(frozen=True)
class CommandCenterDashboardResult:
    status: str
    final_verdict: str
    command_center_ready: bool
    premium_design_system_present: bool
    dashboard_markers_present: bool
    safety_markers_present: bool
    motion_markers_present: bool
    manual_only: bool
    execution_forbidden: bool
    blockers: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _money(value: Any) -> str:
    try:
        return f"EUR {float(value or 0.0):.2f}"
    except Exception:
        return "EUR 0.00"


def _yes_no(value: Any) -> str:
    return "Yes" if bool(value) else "No"


def _list(items: list[Any]) -> str:
    if not items:
        return "<li>none</li>"
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in items)


def _lane_label(value: Any) -> str:
    return {
        "crypto": "Crypto",
        "etf_fund": "ETF/Fund Core",
        "individual_stock": "Stock Review",
        "emergency": "Emergency",
    }.get(str(value or ""), str(value or "Unknown"))


def _friendly_freshness(value: Any) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return "check source"
    if "ready" in text or "fresh" in text or "current" in text:
        return "fresh"
    if "missing" in text or "partial" in text or "unavailable" in text:
        return "needs review"
    return text


def _ticker(news: Mapping[str, Any]) -> str:
    chips = []
    for item in (news.get("top_headlines") or [])[:8]:
        title = str(item.get("title") or "Market context unavailable")
        source = str(item.get("source") or "public source")
        freshness = str(item.get("freshness_status") or "freshness unknown")
        chips.append(
            '<article class="headline-chip glass-card">'
            f"<strong>{html.escape(title)}</strong>"
            f"<span>{html.escape(source)} | {html.escape(freshness)}</span>"
            "</article>"
        )
    if not chips:
        chips.append(
            '<article class="headline-chip glass-card">'
            "<strong>Headlines are quiet</strong>"
            "<span>Public headlines are optional context and never recommend action from headline alone.</span>"
            "</article>"
        )
    content = "".join(chips)
    return (
        '<section class="glass-panel command-section">'
        '<div class="section-head"><h2>Market Headlines</h2><span class="status-badge state-ready">Context Only</span></div>'
        '<p class="muted">Public headlines are optional context and never recommend action from headline alone.</p>'
        '<div class="headline-ticker ticker-rail" aria-label="Market headlines ticker">'
        f'<div class="ticker-track headline-track">{content}{content}</div>'
        "</div>"
        "</section>"
    )


def _selected_rows(items: list[Mapping[str, Any]]) -> str:
    rows = []
    for item in items:
        rows.append(
            "<tr>"
            f"<td>{html.escape(_lane_label(item.get('lane')))}</td>"
            f"<td>{html.escape(str(item.get('symbol') or 'Review'))}</td>"
            f"<td>{html.escape(_money(item.get('amount_eur')))}</td>"
            "</tr>"
        )
    return "".join(rows) if rows else "<tr><td colspan='3'>No selected instruments</td></tr>"


def _coverage_rows(items: list[Mapping[str, Any]]) -> str:
    rows = []
    for item in items[:8]:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('symbol') or 'n/a'))}</td>"
            f"<td>{html.escape(_friendly_freshness(item.get('freshness')))}</td>"
            f"<td>{html.escape(str(item.get('classification') or item.get('identity_confidence') or 'review context'))}</td>"
            "</tr>"
        )
    return "".join(rows) if rows else "<tr><td colspan='3'>No movement records</td></tr>"


def _holdings_rows(items: list[Mapping[str, Any]]) -> str:
    rows = []
    for item in items[:6]:
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('symbol') or 'n/a'))}</td>"
            f"<td>{html.escape(_lane_label(item.get('lane')))}</td>"
            f"<td>{html.escape(str(item.get('quantity') or 'n/a'))}</td>"
            f"<td>{html.escape(_money(item.get('market_value_eur')) if item.get('market_value_eur') is not None else 'not available')}</td>"
            "</tr>"
        )
    return "".join(rows) if rows else "<tr><td colspan='4'>Holdings not entered yet</td></tr>"


def render_command_center_dashboard_html(result: Any) -> str:
    sections = result.sections
    week = sections["week_plan"]
    news = sections["news"]
    finance = sections["finance_intelligence"]
    holdings = sections["manual_holdings"]
    safety = sections["safety"]
    audit = sections["audit"]
    memory = sections.get("session_memory", {})
    changed = sections.get("what_changed", {})
    selected = list(week.get("selected_instruments") or [])
    coverage = list(finance.get("selected_instrument_coverage") or [])
    universe = build_universe_explorer_result(query="find European accumulating global ETFs")
    universe_symbols = ", ".join(item.get("symbol", "") for item in universe.top_candidates[:3]) or "none"
    display_status = "READY FOR MANUAL USE" if result.dashboard_contract_ready and not result.blockers else "NEEDS REVIEW"
    status_state = "ready" if display_status == "READY FOR MANUAL USE" else "review"
    health_label = "Ready" if result.dashboard_contract_ready and safety.get("safety_check_blocked_execution") else "Needs Review"
    changed_summary = str(
        changed.get("summary_text")
        or "Since last time: first run. No previous safe snapshot exists yet, so no comparison is available."
    )
    memory_summary = str(
        memory.get("summary_text")
        or "First run: no previous J.A.R.V.I.S. session memory exists yet. This is safe and not a blocker."
    )
    safety_line = (
        "Manual-only safety: Prepare Manual Review only. No broker. No credentials. "
        "No order tickets. No external instructions. No external completion records. No auto-approval."
    )
    extra_css = """
<style>
.command-grid { display:grid; grid-template-columns:repeat(12,minmax(0,1fr)); gap:16px; }
.command-hero { grid-column:span 12; min-height:310px; }
.hero-inner { display:grid; grid-template-columns:minmax(0,1.25fr) 310px; gap:24px; align-items:center; }
.hero-title { margin:0; font-size:var(--font-hero); letter-spacing:0; line-height:.92; }
.hero-subtitle, .muted { color:var(--jarvis-muted); line-height:1.55; }
.hero-core { width:min(270px,70vw); aspect-ratio:1; margin:auto; display:grid; place-items:center; position:relative; }
.hero-core .orbital-core { width:45%; aspect-ratio:1; display:grid; place-items:center; text-align:center; font-weight:900; color:#02111c; }
.hero-core .orbit-ring { position:absolute; inset:7%; }
.hero-core .orbit-ring:nth-child(2) { inset:21%; animation-duration:22s; }
.hero-core .orbit-ring:nth-child(3) { inset:34%; animation-duration:16s; }
.hero-core .planet { position:absolute; width:18px; height:18px; border-radius:50%; box-shadow:0 0 22px currentColor; }
.planet.emergency { color:var(--jarvis-green); background:var(--jarvis-green); left:13%; top:48%; }
.planet.etf { color:var(--jarvis-cyan); background:var(--jarvis-cyan); right:10%; top:35%; }
.planet.crypto { color:var(--jarvis-amber); background:var(--jarvis-amber); left:52%; bottom:9%; }
.planet.stock { color:var(--jarvis-magenta); background:var(--jarvis-magenta); right:28%; bottom:22%; }
.metric-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; }
.command-section { grid-column:span 6; }
.wide { grid-column:span 12; }
.section-head { display:flex; justify-content:space-between; gap:12px; align-items:start; margin-bottom:12px; }
.section-head h2, .glass-panel h2 { margin:0; font-size:var(--font-section); letter-spacing:0; }
.headline-chip { min-width:330px; display:grid; gap:6px; margin:10px 0; }
.headline-chip strong { color:var(--jarvis-text); }
.headline-chip span { color:var(--jarvis-muted); font-size:13px; }
.headline-track { animation-name:ticker-scroll; }
@keyframes ticker-scroll { from { transform:translateX(0); } to { transform:translateX(-50%); } }
.compact-list { margin:0; padding-left:18px; color:var(--jarvis-muted); }
.safe-note { color:var(--jarvis-green); border-color:rgba(120,242,168,.32); background:rgba(20,70,48,.24); }
@media (max-width:980px) { .hero-inner { grid-template-columns:1fr; } .command-section { grid-column:span 12; } .metric-grid { grid-template-columns:repeat(2,minmax(0,1fr)); } }
@media (max-width:640px) { .metric-grid { grid-template-columns:1fr; } .headline-chip { min-width:260px; } }
</style>
"""
    body = f"""
<main class="command-grid">
<section class="hud-hero command-hero">
  <div class="hero-inner">
    <div>
      {render_status_badge(display_status, status_state)}
      <h1 class="hero-title">J.A.R.V.I.S.</h1>
      <p class="hero-subtitle">Premium orbital portfolio command center. Current date: {html.escape(result.current_date)}</p>
      <div class="glass-card safe-note">{html.escape(safety_line)}</div>
    </div>
    <div class="hero-core" aria-label="Portfolio orbital core">
      <div class="orbit-ring"></div><div class="orbit-ring"></div><div class="orbit-ring"></div>
      <span class="planet emergency"></span><span class="planet etf"></span><span class="planet crypto"></span><span class="planet stock"></span>
      <div class="orbital-core">CORE</div>
    </div>
  </div>
</section>

<section class="glass-panel wide">
  <div class="section-head"><h2>Today's Manual Plan</h2>{render_status_badge("Prepare Manual Review", "ready")}</div>
  <div class="metric-grid">
    <div class="metric-tile"><span class="metric-label">Emergency</span><strong class="metric-value">{_money(week.get("emergency_top_up_eur"))}</strong></div>
    <div class="metric-tile"><span class="metric-label">ETF/Fund Core</span><strong class="metric-value">{_money(week.get("etf_fund_eur"))}</strong></div>
    <div class="metric-tile"><span class="metric-label">Crypto</span><strong class="metric-value">{_money(week.get("crypto_eur"))}</strong></div>
    <div class="metric-tile"><span class="metric-label">Stock Review</span><strong class="metric-value">{_money(week.get("individual_stock_eur"))}</strong></div>
  </div>
  <table class="data-table"><thead><tr><th>Sleeve</th><th>Instrument</th><th>Amount</th></tr></thead><tbody>{_selected_rows(selected)}</tbody></table>
</section>

{_ticker(news)}

<section class="glass-panel command-section">
  <div class="section-head"><h2>Portfolio Health</h2>{render_status_badge(health_label, "ready" if health_label == "Ready" else "review")}</div>
  <ul class="compact-list">
    <li>Dashboard contract ready: {_yes_no(result.dashboard_contract_ready)}</li>
    <li>Safety check blocked execution: {_yes_no(safety.get("safety_check_blocked_execution"))}</li>
    <li>Manual approval required: {_yes_no(safety.get("manual_approval_required"))}</li>
    <li>Blockers: {html.escape(", ".join(result.blockers) if result.blockers else "none")}</li>
  </ul>
</section>

<section class="glass-panel command-section">
  <div class="section-head"><h2>What Changed Since Last Time</h2>{render_status_badge("Review Note Ready", "ready")}</div>
  <p class="muted">{html.escape(changed_summary)}</p>
  <ul class="compact-list">{_list(list(changed.get("changes") or ["No previous safe snapshot exists yet."]))}</ul>
</section>

<section class="glass-panel command-section">
  <div class="section-head"><h2>Last Session</h2>{render_status_badge("Memory", "ready")}</div>
  <p class="muted">{html.escape(memory_summary)}</p>
  <ul class="compact-list"><li>Safe derived summaries only.</li><li>Memory remains local and read-only.</li></ul>
</section>

<section class="glass-panel command-section">
  <div class="section-head"><h2>Universe Explorer</h2>{render_status_badge("Evidence Summary", "ready")}</div>
  <div class="metric-tile"><span class="metric-label">Candidates</span><strong class="metric-value">{universe.candidate_count}</strong></div>
  <p class="muted">Sample candidates: {html.escape(universe_symbols)}. Manual review required.</p>
</section>

<section class="glass-panel wide">
  <div class="section-head"><h2>Market Movement</h2>{render_status_badge("Freshness Context", "review" if (finance.get("data_trust_summary") or {}).get("partial_records") else "ready")}</div>
  <p class="muted">{html.escape(str(finance.get("market_movement_summary") or "Movement context unavailable."))}</p>
  <table class="data-table"><thead><tr><th>Symbol</th><th>Freshness</th><th>Context</th></tr></thead><tbody>{_coverage_rows(coverage)}</tbody></table>
</section>

<section class="glass-panel command-section">
  <div class="section-head"><h2>Manual Holdings Summary</h2>{render_status_badge("Needs Review" if not holdings.get("holdings_ready") else "Ready", "review" if not holdings.get("holdings_ready") else "ready")}</div>
  <table class="data-table"><thead><tr><th>Symbol</th><th>Sleeve</th><th>Qty</th><th>Value</th></tr></thead><tbody>{_holdings_rows(list(holdings.get("positions") or []))}</tbody></table>
</section>

<section class="glass-panel command-section">
  <div class="section-head"><h2>System Checks / Safety</h2>{render_status_badge("Manual-Only", "ready")}</div>
  <ul class="compact-list">
    <li>Plan math ready: {_yes_no(audit.get("formula_invariants_ready"))}</li>
    <li>Data ready: {_yes_no(audit.get("data_readiness_ready"))}</li>
    <li>News context ready: {_yes_no(audit.get("news_coverage_ready"))}</li>
    <li>Safety ready: {_yes_no(audit.get("safety_ready"))}</li>
    <li>No broker, credentials, order tickets, external instructions, external completion records, or auto-approval.</li>
  </ul>
</section>
</main>
"""
    return render_shell(
        title="J.A.R.V.I.S. Portfolio Dashboard",
        active="dashboard",
        body=body,
        extra_head=extra_css,
    )


def build_command_center_dashboard_result(html_text: str | None = None) -> CommandCenterDashboardResult:
    if html_text is None:
        from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html

        html_text = render_dashboard_html(build_dashboard_contract_result(current_date="2026-06-21"))
    required_dashboard = [
        "J.A.R.V.I.S. Portfolio Dashboard",
        "Today's Manual Plan",
        "Market Headlines",
        "Portfolio Health",
        "What Changed Since Last Time",
        "Market Movement",
        "Manual Holdings Summary",
        "System Checks / Safety",
    ]
    required_safety = [
        "Manual-only safety",
        "Prepare Manual Review",
        "No broker",
        "No credentials",
        "No order tickets",
        "No auto-approval",
    ]
    required_motion = ["orbital-core", "orbit-ring", "ticker-scroll", "headline-ticker", "motion-panel-enter"]
    missing = [item for item in required_dashboard + required_safety + required_motion if item not in html_text]
    blockers = [] if not missing else ["command_center_markers_missing"]
    return CommandCenterDashboardResult(
        status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
        final_verdict=FINAL_VERDICT_READY if not blockers else "REVIEW_REQUIRED_FOR_PREMIUM_COMMAND_CENTER_DASHBOARD",
        command_center_ready=not blockers,
        premium_design_system_present="jarvis-shell" in html_text and "glass-panel" in html_text,
        dashboard_markers_present=not any(item for item in required_dashboard if item not in html_text),
        safety_markers_present=not any(item for item in required_safety if item not in html_text),
        motion_markers_present=not any(item for item in required_motion if item not in html_text),
        manual_only=True,
        execution_forbidden=True,
        blockers=blockers,
        warnings=["command center dashboard is a read-only local UI surface"],
    )


def format_command_center_dashboard(result: CommandCenterDashboardResult) -> str:
    lines = [
        "J.A.R.V.I.S. IRON MAN COMMAND CENTER DASHBOARD",
        f"status: {result.status}",
        f"final verdict: {result.final_verdict}",
        f"command center ready: {result.command_center_ready}",
        f"premium design system present: {result.premium_design_system_present}",
        f"dashboard markers present: {result.dashboard_markers_present}",
        f"safety markers present: {result.safety_markers_present}",
        f"motion markers present: {result.motion_markers_present}",
        f"manual_only: {result.manual_only}",
        f"execution_forbidden: {result.execution_forbidden}",
        "",
        "WARNINGS:",
        *[f"- {item}" for item in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the premium command center dashboard.")
    parser.add_argument("--command-center-dashboard", action="store_true")
    _args = parser.parse_args(argv)
    result = build_command_center_dashboard_result()
    print(format_command_center_dashboard(result))
    return 0 if result.command_center_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "FINAL_VERDICT_READY",
    "CommandCenterDashboardResult",
    "render_command_center_dashboard_html",
    "build_command_center_dashboard_result",
    "format_command_center_dashboard",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
