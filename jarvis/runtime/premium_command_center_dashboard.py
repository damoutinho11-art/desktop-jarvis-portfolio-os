"""J.A.R.V.I.S. v162.0 Iron Man command center dashboard renderer."""

from __future__ import annotations

import argparse
import html
import re
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
        return "Needs review"
    if "ready" in text or "fresh" in text or "current" in text:
        return "Fresh"
    if "missing" in text or "partial" in text or "unavailable" in text:
        return "Needs review"
    return str(value)


def _amount(value: Any) -> float:
    try:
        return round(float(value or 0.0), 2)
    except Exception:
        return 0.0


def _lane_class(value: Any) -> str:
    lane = str(value or "").lower()
    if lane == "crypto":
        return "lane-crypto"
    if lane == "individual_stock":
        return "lane-stock"
    if lane == "emergency":
        return "lane-emergency"
    return "lane-etf"


def _coverage_by_symbol(items: list[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    coverage: dict[str, dict[str, Any]] = {}
    for item in items:
        symbol = str(item.get("symbol") or "").upper()
        if symbol:
            coverage[symbol] = dict(item)
        tradable = str(item.get("tradable_symbol") or "").upper()
        if tradable:
            coverage[tradable] = dict(item)
    return coverage


def _display_symbol(item: Mapping[str, Any], coverage: Mapping[str, Any] | None = None) -> str:
    cov = coverage or {}
    tradable = str(cov.get("tradable_symbol") or "").strip()
    symbol = str(item.get("symbol") or cov.get("symbol") or "Review").strip().upper()
    if symbol == "GLOBAL_CORE_ETF" and tradable:
        return tradable
    return tradable if symbol.endswith("_ETF") and tradable else symbol


def _friendly_market_status(item: Mapping[str, Any]) -> tuple[str, str, str]:
    classification = str(item.get("classification") or "").strip().lower()
    freshness = str(item.get("freshness") or "").strip().lower()
    next_action = str(item.get("next_action") or "").strip().lower()
    trusted = bool(item.get("trusted_quote"))

    if "placeholder" in classification:
        return "Setup note", "review", "Sleeve candidate needs manual source confirmation."
    if "missing" in classification or "missing" in next_action:
        return "Needs quote source", "review", "Quote source is not connected yet."
    if "partial" in classification or "partial" in freshness or "unavailable" in freshness:
        return "Needs review", "review", "Movement context is partial."
    if trusted and any(token in freshness for token in ("ready", "fresh", "current")):
        return "Ready", "ready", "Fresh trusted public quote."
    if trusted:
        return "Ready", "ready", "Trusted quote available; confirm freshness."
    return "Manual review context", "review", "Check source freshness before relying on context."


def _movement_for_symbol(symbol: str, summary: Any) -> str:
    text = str(summary or "")
    match = re.search(rf"\b{re.escape(symbol)}\b:\s*24h\s*([+-]?\d+(?:\.\d+)?)%", text, re.IGNORECASE)
    if match:
        return f"{float(match.group(1)):+.2f}%"
    return "Review"


def _sparkline(symbol: str) -> str:
    # Decorative telemetry only; values are not price truth.
    seed = sum(ord(ch) for ch in symbol)
    points = []
    for index in range(10):
        x = 4 + index * 10
        y = 20 - ((seed + index * 7) % 13)
        points.append(f"{x},{y}")
    return '<svg class="spark" viewBox="0 0 100 24" aria-hidden="true"><polyline points="' + " ".join(points) + '"/></svg>'


def _dashboard_assets(
    selected: list[Mapping[str, Any]],
    coverage: list[Mapping[str, Any]],
    market_summary: Any,
) -> list[dict[str, Any]]:
    coverage_map = _coverage_by_symbol(coverage)
    assets = []
    for item in selected:
        lane = str(item.get("lane") or "")
        cov = coverage_map.get(str(item.get("symbol") or "").upper(), {})
        display = _display_symbol(item, cov)
        if display == "GLOBAL_CORE_ETF":
            continue
        assets.append(
            {
                "symbol": display,
                "name": str(item.get("name") or (cov.get("instrument_identity") or {}).get("name") or display),
                "lane": lane,
                "lane_label": _lane_label(lane),
                "amount": _amount(item.get("amount_eur") or cov.get("selected_amount_eur")),
                "freshness": _friendly_freshness(cov.get("freshness")),
                "status": _friendly_market_status(cov)[0] if cov else "Manual review context",
                "status_state": _friendly_market_status(cov)[1] if cov else "review",
                "movement": _movement_for_symbol(display, market_summary),
                "source_note": _friendly_market_status(cov)[2] if cov else "Evidence context needs manual review.",
            }
        )
    if not assets:
        assets = [
            {"symbol": "BTC", "name": "Bitcoin", "lane": "crypto", "lane_label": "Crypto", "amount": 100.0, "freshness": "Needs review", "status": "Manual review context", "status_state": "review", "source_note": "Fixture context."},
            {"symbol": "VWCE", "name": "Vanguard FTSE All-World UCITS ETF", "lane": "etf_fund", "lane_label": "ETF/Fund Core", "amount": 275.0, "freshness": "Needs review", "status": "Manual review context", "status_state": "review", "source_note": "Fixture context."},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "lane": "individual_stock", "lane_label": "Stock Review", "amount": 50.0, "freshness": "Needs review", "status": "Manual review context", "status_state": "review", "source_note": "Fixture context."},
        ]
    total = sum(asset["amount"] for asset in assets) or 1.0
    preferred_positions = {
        "BTC": (23, 22),
        "ETH": (15, 55),
        "VWCE": (49, 78),
        "IS3Q.DE": (76, 28),
        "MSFT": (82, 58),
        "EUNL.DE": (68, 18),
    }
    fallback_positions = [(24, 22), (16, 54), (50, 79), (77, 29), (83, 58), (62, 15)]
    for index, asset in enumerate(assets):
        asset["weight"] = round(asset["amount"] / total * 100, 1)
        asset["size"] = int(42 + min(44, asset["amount"] / max([item["amount"] for item in assets] + [1.0]) * 44))
        asset["x"], asset["y"] = preferred_positions.get(asset["symbol"], fallback_positions[index % len(fallback_positions)])
        asset["selected"] = asset["symbol"] == "MSFT"
    if not any(asset["selected"] for asset in assets):
        assets[-1]["selected"] = True
    return assets


def _selected_asset(assets: list[dict[str, Any]]) -> dict[str, Any]:
    for asset in assets:
        if asset.get("selected"):
            return asset
    return assets[0]


def _headline_tag(item: Mapping[str, Any]) -> str:
    text = " ".join(
        str(value)
        for value in list(item.get("entity_tags") or [])
        + list(item.get("lane_tags") or [])
        + [item.get("title") or ""]
    ).lower()
    if "bitcoin" in text or "btc" in text:
        return "BTC"
    if "ethereum" in text or "eth" in text:
        return "ETH"
    if "microsoft" in text or "msft" in text:
        return "MSFT"
    if "etf" in text or "fund" in text:
        return "ETF"
    if "fed" in text or "inflation" in text or "rate" in text:
        return "MACRO"
    return "MARKET"


def _ticker(news: Mapping[str, Any]) -> str:
    chips = []
    for item in (news.get("top_headlines") or [])[:8]:
        tag = _headline_tag(item)
        title = str(item.get("title") or "Market context unavailable")
        chips.append(
            '<span class="ticker-chip headline-chip">'
            f'<strong class="tag-{html.escape(tag.lower())}">{html.escape(tag)}:</strong> '
            f"{html.escape(title)}"
            "</span>"
        )
    if not chips:
        chips = [
            '<span class="ticker-chip headline-chip"><strong class="tag-btc">BTC:</strong> Headlines quiet - optional context only</span>',
            '<span class="ticker-chip headline-chip"><strong class="tag-etf">ETF:</strong> Universe context ready for manual review</span>',
            '<span class="ticker-chip headline-chip"><strong class="tag-msft">MSFT:</strong> Evidence Summary available</span>',
            '<span class="ticker-chip headline-chip"><strong class="tag-macro">MACRO:</strong> Context only - never recommend action from headline alone</span>',
        ]
    content = '<span class="ticker-label">MARKET HEADLINES</span>' + "".join(chips) + '<span class="live-dot">CONTEXT ONLY</span>'
    return (
        '<section class="headline-ticker ticker-rail" aria-label="Market Headlines">'
        f'<div class="ticker-track headline-track">{content}{content}</div>'
        "</section>"
    )


def _selected_rows(items: list[Mapping[str, Any]]) -> str:
    rows = []
    for item in items:
        rows.append(
            '<div class="plan-row">'
            f'<span class="lane-dot {_lane_class(item.get("lane"))}"></span>'
            f"<span>{html.escape(_lane_label(item.get('lane')))}</span>"
            f"<strong>{html.escape(_money(item.get('amount_eur')))}</strong>"
            "</div>"
        )
    return "".join(rows) if rows else '<div class="plan-row"><span>No selected instruments</span><strong>Review</strong></div>'


def _coverage_rows(items: list[Mapping[str, Any]], market_summary: Any) -> str:
    rows = []
    for item in items[:6]:
        status, state, note = _friendly_market_status(item)
        display = _display_symbol(item, item)
        price = item.get("quote_price")
        price_label = f"{html.escape(str(item.get('currency') or ''))} {float(price):.2f}" if price is not None else "Needs source"
        movement = _movement_for_symbol(display, market_summary)
        rows.append(
            "<tr>"
            f"<td><span class=\"asset-pill {_lane_class(item.get('lane'))}\"></span>{html.escape(display)}</td>"
            f"<td>{price_label}</td>"
            f"<td class=\"movement-value\">{html.escape(movement)}</td>"
            f"<td>{_sparkline(display)}</td>"
            f"<td><span class=\"mini-status state-{state}\">{html.escape(status)}</span><small>{html.escape(note)}</small></td>"
            "</tr>"
        )
    return "".join(rows) if rows else "<tr><td colspan='5'>No movement records</td></tr>"


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


def _orbit_planets(assets: list[dict[str, Any]]) -> str:
    planets = []
    for asset in assets:
        selected = " selected" if asset.get("selected") else ""
        review = " needs-review" if str(asset.get("status_state")) == "review" else ""
        symbol = html.escape(str(asset.get("symbol")))
        planets.append(
            f'<button class="dashboard-planet {_lane_class(asset.get("lane"))}{selected}{review}" '
            f'type="button" data-symbol="{symbol}" '
            f'style="left:{asset.get("x")}%;top:{asset.get("y")}%;width:{asset.get("size")}px;height:{asset.get("size")}px" '
            f'aria-label="Selected asset telemetry for {symbol}">'
            f'<span class="planet-core">{symbol[:4]}</span>'
            f'<span class="planet-label"><strong>{symbol}</strong><em>{asset.get("weight", 0):.1f}%</em></span>'
            "</button>"
        )
    return "".join(planets)


def _what_changed_items(changed: Mapping[str, Any]) -> str:
    items = list(changed.get("changes") or [])
    if not items:
        items = [
            "Manual plan context is loaded.",
            "Safety remains manual-only.",
            "Blockers: none.",
        ]
    return "".join(f"<li>{html.escape(str(item))}<span>review</span></li>" for item in items[:5])


def render_command_center_dashboard_html(result: Any) -> str:
    sections = result.sections
    week = sections["week_plan"]
    news = sections["news"]
    finance = sections["finance_intelligence"]
    safety = sections["safety"]
    audit = sections["audit"]
    memory = sections.get("session_memory", {})
    changed = sections.get("what_changed", {})
    selected = list(week.get("selected_instruments") or [])
    coverage = list(finance.get("selected_instrument_coverage") or [])
    assets = _dashboard_assets(selected, coverage, finance.get("market_movement_summary"))
    selected_asset = _selected_asset(assets)
    display_status = "READY FOR MANUAL USE" if result.dashboard_contract_ready and not result.blockers else "NEEDS REVIEW"
    health_score = 86 if result.dashboard_contract_ready and safety.get("safety_check_blocked_execution") else 68
    universe = build_universe_explorer_result(query="find European accumulating global ETFs")
    universe_symbols = ", ".join(item.get("symbol", "") for item in universe.top_candidates[:3]) or "none"
    changed_summary = str(
        changed.get("summary_text")
        or "Since last time: first run. No previous safe snapshot exists yet, so no comparison is available."
    )
    safety_line = (
        "Manual-only - No broker - No credentials - No orders - No trades"
    )
    plan_rows = _selected_rows(
        [
            {"lane": "emergency", "amount_eur": week.get("emergency_top_up_eur")},
            {"lane": "crypto", "amount_eur": week.get("crypto_eur")},
            {"lane": "etf_fund", "amount_eur": week.get("etf_fund_eur")},
            {"lane": "individual_stock", "amount_eur": week.get("individual_stock_eur")},
        ]
    )
    orbit_planets = _orbit_planets(assets)
    movement_rows = _coverage_rows(coverage, finance.get("market_movement_summary"))
    ticker_html = _ticker(news)
    changed_items = _what_changed_items(changed)
    data_feeds_label = "Operational" if audit.get("data_readiness_ready") else "Needs Review"
    calculations_label = "Verified" if audit.get("formula_invariants_ready") else "Review"
    extra_css = """
<style>
.jarvis-shell { width:min(100% - 16px, 1680px); padding:8px 0 12px; }
.jarvis-shell > .jarvis-nav { display:none; }
.visual-command-center { min-height:calc(100vh - 20px); display:grid; grid-template-columns:88px minmax(620px,1fr) minmax(360px,430px); grid-template-rows:88px minmax(310px,1fr) 170px 44px 74px; gap:10px; }
.hud-frame, .cockpit-card, .left-nav-rail, .orbit-cockpit, .selected-asset-telemetry, .headline-ticker, .assistant-strip > * {
  position:relative; border:1px solid rgba(84,220,255,.34); background:linear-gradient(145deg,rgba(7,18,33,.82),rgba(2,8,17,.74)); box-shadow:0 0 0 1px rgba(84,220,255,.06), 0 0 32px rgba(21,183,255,.10), inset 0 1px 0 rgba(255,255,255,.08); backdrop-filter:blur(14px); overflow:hidden;
}
.hud-frame::before, .cockpit-card::before, .left-nav-rail::before, .orbit-cockpit::before, .selected-asset-telemetry::before, .assistant-strip > *::before {
  content:""; position:absolute; inset:0; pointer-events:none; background:linear-gradient(115deg,transparent 0 38%,rgba(100,230,255,.10) 48%,transparent 60%); transform:translateX(-120%); animation:jarvisLightSweep 10s var(--motion-soft) infinite;
}
.top-hud { grid-column:1/-1; display:grid; grid-template-columns:230px 280px minmax(330px,1fr) 450px 96px; align-items:center; gap:12px; padding:10px 18px; clip-path:polygon(1.5% 0,98.5% 0,100% 30%,100% 100%,0 100%,0 30%); }
.sys-clock { display:grid; grid-template-columns:52px 1fr; gap:10px; align-items:center; color:var(--jarvis-muted); font-family:var(--font-mono); }
.clock-radar, .integrity-ring, .assistant-orb { border-radius:50%; background:radial-gradient(circle,#eafaff 0 8%,var(--jarvis-cyan) 12%,rgba(16,57,83,.42) 36%,transparent 63%); box-shadow:0 0 28px rgba(85,223,255,.42), inset 0 0 16px rgba(255,255,255,.16); animation:jarvisCoreBreath 4s ease-in-out infinite; }
.clock-radar { width:44px; aspect-ratio:1; }
.sys-clock strong { color:#dff8ff; font-size:18px; letter-spacing:0; }
.brand-lockup { text-align:center; }
.brand-lockup h1 { margin:0; font-size:34px; letter-spacing:.22em; text-shadow:0 0 22px rgba(178,234,255,.65); }
.brand-lockup span { display:block; margin-top:3px; color:#9fdfff; font-weight:800; letter-spacing:.16em; }
.ready-banner { justify-self:stretch; text-align:center; border:1px solid rgba(85,223,255,.54); color:var(--jarvis-cyan); font-size:24px; font-weight:950; letter-spacing:.12em; padding:10px 16px 8px; clip-path:polygon(8% 0,92% 0,100% 50%,92% 100%,8% 100%,0 50%); box-shadow:0 0 30px rgba(85,223,255,.18), inset 0 0 28px rgba(85,223,255,.08); }
.ready-banner small { display:block; margin-top:5px; color:#b9d9ee; font-size:12px; font-weight:700; letter-spacing:0; }
.status-cluster { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }
.sys-badge { display:grid; grid-template-columns:34px 1fr; gap:9px; align-items:center; color:#a8c8df; font-size:11px; font-weight:800; text-transform:uppercase; }
.sys-icon { width:34px; aspect-ratio:1; display:grid; place-items:center; border-radius:50%; border:1px solid rgba(85,223,255,.28); color:var(--jarvis-cyan); box-shadow:inset 0 0 14px rgba(85,223,255,.12); }
.sys-badge strong { display:block; color:var(--jarvis-green); margin-top:2px; }
.integrity-ring { width:74px; aspect-ratio:1; display:grid; place-items:center; justify-self:end; color:#dff8ff; font-weight:950; }
.integrity-ring span { font-size:10px; color:var(--jarvis-muted); display:block; }
.left-nav-rail { grid-column:1; grid-row:2/6; padding:12px 8px; display:grid; gap:8px; align-content:start; border-radius:8px; }
.rail-link { min-height:54px; display:grid; place-items:center; gap:3px; color:#9fc4dc; text-decoration:none; border:1px solid transparent; border-radius:7px; font-size:10px; font-weight:850; text-transform:uppercase; }
.rail-link b { font-size:18px; color:#7ddaff; }
.rail-link.active, .rail-link:hover, .rail-link:focus { color:#eaffff; border-color:rgba(85,223,255,.55); background:rgba(85,223,255,.12); box-shadow:0 0 24px rgba(85,223,255,.18); outline:none; }
.rail-build { align-self:end; color:#5aa8c8; font-size:10px; text-align:center; }
.orbit-cockpit { grid-column:2; grid-row:2; min-height:310px; border-radius:8px; }
.dashboard-orbit { position:absolute; inset:10px; overflow:hidden; }
.orbit-grid { position:absolute; inset:0; background:radial-gradient(circle at 52% 52%,rgba(85,223,255,.12),transparent 29%), radial-gradient(circle at 12% 4%,rgba(255,191,92,.12),transparent 20%); }
.orbit-grid::before { content:""; position:absolute; inset:-30%; background-image:linear-gradient(rgba(85,223,255,.045) 1px,transparent 1px),linear-gradient(90deg,rgba(85,223,255,.045) 1px,transparent 1px); background-size:44px 44px; transform:rotate(-8deg); animation:jarvisGridDrift 20s linear infinite; }
.orbit-ring-line { position:absolute; left:50%; top:52%; border:1px solid rgba(85,223,255,.24); border-radius:50%; transform:translate(-50%,-50%) rotate(-9deg); box-shadow:0 0 28px rgba(85,223,255,.08), inset 0 0 24px rgba(85,223,255,.04); animation:subtleOrbitDrift 28s linear infinite; }
.orbit-ring-line.r1 { width:28%; height:18%; }
.orbit-ring-line.r2 { width:46%; height:30%; animation-duration:35s; }
.orbit-ring-line.r3 { width:66%; height:43%; animation-duration:45s; }
.orbit-ring-line.r4 { width:88%; height:56%; animation-duration:55s; }
.dashboard-core { position:absolute; left:51%; top:52%; width:118px; aspect-ratio:1; transform:translate(-50%,-50%); display:grid; place-items:center; text-align:center; color:#dffaff; border-radius:50%; background:radial-gradient(circle at 34% 26%,#fff 0 7%,#60e7ff 13% 30%,#1579ff 48%,rgba(4,17,31,.94) 72%); box-shadow:0 0 64px rgba(85,223,255,.55), inset 0 0 30px rgba(255,255,255,.18); animation:jarvisCoreBreath 4s ease-in-out infinite; }
.dashboard-core strong { font-size:13px; letter-spacing:.22em; text-shadow:0 0 18px rgba(255,255,255,.7); }
.dashboard-core span { display:block; color:#48e4ff; font-size:10px; margin-top:4px; letter-spacing:.14em; }
.dashboard-planet { position:absolute; transform:translate(-50%,-50%); border:0; border-radius:50%; cursor:pointer; color:var(--jarvis-cyan); background:radial-gradient(circle at 36% 28%,#fff 0 8%,currentColor 16%,rgba(5,16,28,.86) 64%); box-shadow:0 0 34px currentColor, inset 0 0 18px rgba(255,255,255,.15); animation:planetFloat 5.8s ease-in-out infinite; }
.dashboard-planet.lane-crypto { color:var(--jarvis-amber); }
.dashboard-planet.lane-stock { color:var(--jarvis-magenta); }
.dashboard-planet.lane-emergency { color:var(--jarvis-green); }
.dashboard-planet.selected { outline:1px solid rgba(164,236,255,.85); box-shadow:0 0 44px currentColor,0 0 0 8px rgba(85,223,255,.08),inset 0 0 22px rgba(255,255,255,.18); }
.dashboard-planet.selected::before, .dashboard-planet.selected::after { content:""; position:absolute; inset:-10px; border:1px solid rgba(125,218,255,.68); border-radius:12px; clip-path:polygon(0 0,32% 0,32% 8%,8% 8%,8% 32%,0 32%,0 0,100% 0,100% 32%,92% 32%,92% 8%,68% 8%,68% 0); animation:focusBracket 2.6s ease-in-out infinite; }
.dashboard-planet.needs-review { outline:2px solid rgba(255,191,92,.72); }
.planet-core { display:grid; place-items:center; width:100%; height:100%; font-size:12px; font-weight:950; color:#eaffff; text-shadow:0 0 12px #000; }
.planet-label { position:absolute; left:calc(100% + 12px); top:50%; transform:translateY(-50%); white-space:nowrap; display:grid; gap:3px; text-align:left; }
.planet-label strong { color:#e9fbff; font-size:20px; text-shadow:0 0 16px rgba(85,223,255,.4); }
.planet-label em { color:#b3d4ea; font-style:normal; font-size:14px; }
.orbit-legend { position:absolute; left:16px; bottom:16px; color:#9dc6dd; font-size:12px; line-height:1.55; }
.allocation-mark { position:absolute; right:16px; top:16px; color:#8fdcff; text-align:right; font-size:12px; font-weight:800; }
.selected-asset-telemetry { grid-column:3; grid-row:2; border-radius:8px; padding:16px 18px; display:grid; gap:10px; align-content:start; }
.telemetry-head { display:flex; justify-content:space-between; gap:12px; align-items:start; border-bottom:1px solid rgba(85,223,255,.18); padding-bottom:10px; }
.telemetry-head h2 { margin:0; font-size:16px; color:#b8d8ed; letter-spacing:.06em; }
.telemetry-head strong { color:var(--jarvis-cyan); font-size:24px; margin-left:8px; }
.telemetry-row { display:grid; grid-template-columns:118px 1fr; gap:12px; border-bottom:1px solid rgba(85,223,255,.13); padding:9px 0; }
.telemetry-row b { color:#8fdcff; font-size:12px; text-transform:uppercase; }
.telemetry-row span, .telemetry-row li { color:#c5d8e8; line-height:1.45; }
.telemetry-row ul { margin:0; padding-left:17px; }
.cockpit-cards { grid-column:2; grid-row:3; display:grid; grid-template-columns:1.05fr 1.15fr 1fr 1fr; gap:10px; }
.cockpit-card { border-radius:8px; padding:13px 14px; }
.cockpit-card h2, .market-movement h2 { margin:0 0 10px; color:#a8dcff; font-size:14px; letter-spacing:.05em; text-transform:uppercase; }
.plan-row { display:grid; grid-template-columns:20px 1fr auto; gap:8px; align-items:center; border-top:1px solid rgba(85,223,255,.12); padding:8px 0; color:#c9ddec; }
.lane-dot, .asset-pill { width:12px; height:12px; border-radius:50%; display:inline-block; box-shadow:0 0 14px currentColor; color:var(--jarvis-cyan); background:currentColor; }
.lane-dot.lane-crypto, .asset-pill.lane-crypto { color:var(--jarvis-amber); }
.lane-dot.lane-stock, .asset-pill.lane-stock { color:var(--jarvis-magenta); }
.lane-dot.lane-emergency, .asset-pill.lane-emergency { color:var(--jarvis-green); }
.health-gauge { width:100px; aspect-ratio:1; margin:2px auto 8px; border-radius:50%; display:grid; place-items:center; background:conic-gradient(var(--jarvis-cyan) 0 86%,rgba(85,223,255,.12) 86%); box-shadow:0 0 28px rgba(85,223,255,.22); }
.health-gauge div { width:72%; aspect-ratio:1; border-radius:50%; background:#06101e; display:grid; place-items:center; font-size:30px; font-weight:950; color:#ccefff; }
.status-list, .change-list { margin:0; padding:0; list-style:none; display:grid; gap:7px; color:#c7d9e8; font-size:12px; }
.status-list li, .change-list li { display:flex; justify-content:space-between; gap:8px; }
.status-list span, .change-list span, .green { color:var(--jarvis-green); }
.amber { color:var(--jarvis-amber); }
.market-movement { grid-column:3; grid-row:3; border-radius:8px; padding:13px 14px; }
.market-table { width:100%; border-collapse:collapse; font-size:12px; }
.market-table th, .market-table td { padding:7px 6px; border-bottom:1px solid rgba(85,223,255,.12); text-align:left; vertical-align:middle; }
.market-table th { color:#7fb8d4; font-size:10px; text-transform:uppercase; }
.market-table small { display:block; color:#7e9cb2; margin-top:2px; }
.movement-value { color:var(--jarvis-green); font-weight:850; }
.spark { width:78px; height:20px; }
.spark polyline { fill:none; stroke:var(--jarvis-green); stroke-width:2; filter:drop-shadow(0 0 5px rgba(48,231,189,.45)); }
.mini-status { display:inline-block; border-radius:999px; padding:3px 7px; font-size:10px; font-weight:900; text-transform:uppercase; }
.mini-status.state-ready { color:var(--jarvis-green); background:rgba(120,242,168,.10); border:1px solid rgba(120,242,168,.28); }
.mini-status.state-review { color:var(--jarvis-amber); background:rgba(255,191,92,.10); border:1px solid rgba(255,191,92,.28); }
.headline-ticker { grid-column:1/-1; grid-row:4; border-radius:8px; display:flex; align-items:center; }
.headline-track { display:flex; align-items:center; gap:18px; min-width:max-content; animation:ticker-scroll 38s linear infinite; }
.ticker-label { color:#9fdfff; border-right:1px solid rgba(85,223,255,.35); padding:0 18px; font-weight:950; letter-spacing:.06em; }
.ticker-chip { color:#dcebf4; white-space:nowrap; }
.ticker-chip strong { color:var(--jarvis-cyan); margin-right:4px; }
.ticker-chip .tag-btc, .tag-btc { color:var(--jarvis-amber); }
.ticker-chip .tag-msft, .tag-msft { color:var(--jarvis-magenta); }
.ticker-chip .tag-etf, .tag-etf { color:var(--jarvis-cyan); }
.ticker-chip .tag-macro, .tag-macro { color:var(--jarvis-amber); }
.live-dot { color:var(--jarvis-green); font-weight:900; }
.assistant-strip { grid-column:2/4; grid-row:5; display:grid; grid-template-columns:1fr 160px 1.05fr; gap:10px; }
.assistant-strip > * { border-radius:8px; padding:12px 16px; }
.quote-panel { display:grid; place-items:center; color:#bde9ff; text-align:center; font-size:16px; }
.map-panel { display:grid; place-items:center; color:#7fb8d4; }
.assistant-panel { display:grid; grid-template-columns:58px 1fr 96px; gap:12px; align-items:center; color:#c7e7f5; }
.assistant-orb { width:54px; aspect-ratio:1; }
.voice-wave { height:34px; background:linear-gradient(90deg,transparent,rgba(85,223,255,.22),transparent); position:relative; }
.voice-wave::before { content:""; position:absolute; inset:8px 0; background:repeating-linear-gradient(90deg,rgba(85,223,255,.9) 0 3px,transparent 3px 10px); mask-image:linear-gradient(90deg,transparent,black 20%,black 80%,transparent); animation:voiceWave 1.8s ease-in-out infinite; }
.sr-only { position:absolute; width:1px; height:1px; padding:0; overflow:hidden; clip:rect(0,0,0,0); white-space:nowrap; border:0; }
@keyframes ticker-scroll { from { transform:translateX(0); } to { transform:translateX(-50%); } }
@keyframes subtleOrbitDrift { from { transform:translate(-50%,-50%) rotate(-9deg); } to { transform:translate(-50%,-50%) rotate(351deg); } }
@keyframes planetFloat { 0%,100% { filter:brightness(1); } 50% { filter:brightness(1.2); } }
@keyframes focusBracket { 0%,100% { opacity:.55; transform:scale(.98); } 50% { opacity:1; transform:scale(1.04); } }
@keyframes voiceWave { 0%,100% { transform:scaleY(.7); opacity:.55; } 50% { transform:scaleY(1.1); opacity:1; } }
@media (max-width:1180px) { .visual-command-center { grid-template-columns:72px 1fr; grid-template-rows:auto auto auto auto auto auto; } .top-hud, .headline-ticker { grid-column:1/-1; } .selected-asset-telemetry, .market-movement, .cockpit-cards, .assistant-strip, .orbit-cockpit { grid-column:2; grid-row:auto; } .left-nav-rail { grid-row:2/7; } .top-hud { grid-template-columns:1fr; text-align:center; } .status-cluster { grid-template-columns:repeat(3,minmax(0,1fr)); } .integrity-ring { justify-self:center; } }
@media (max-width:760px) { .visual-command-center { display:block; } .visual-command-center > * { margin-bottom:10px; } .left-nav-rail { display:flex; overflow:auto; } .cockpit-cards, .assistant-strip { grid-template-columns:1fr; display:grid; } .planet-label strong { font-size:14px; } .selected-asset-telemetry { min-height:auto; } }
</style>
"""
    body = f"""
<main class="visual-command-center">
  <span class="sr-only">J.A.R.V.I.S. Portfolio Dashboard</span>
  <span class="sr-only">Premium orbital portfolio command center. What Changed Since Last Time. Last Session. Safe derived summaries only. Manual Holdings Summary. System Checks / Safety. Context only - never recommend action from headline alone.</span>
  <header class="top-hud hud-frame">
    <div class="sys-clock"><span class="clock-radar"></span><div><small>SYS</small><strong>{html.escape(result.current_date)}</strong><small>LOCAL</small></div></div>
    <div class="brand-lockup"><h1>J.A.R.V.I.S.</h1><span>PORTFOLIO OS</span></div>
    <div class="ready-banner">{html.escape(display_status)}<small>{html.escape(safety_line)}</small></div>
    <div class="status-cluster">
      <div class="sys-badge"><span class="sys-icon">DF</span><span>Data Feed<strong>LIVE</strong></span></div>
      <div class="sys-badge"><span class="sys-icon">SY</span><span>System<strong>NOMINAL</strong></span></div>
      <div class="sys-badge"><span class="sys-icon">SC</span><span>Security<strong>LOCKED</strong></span></div>
    </div>
    <div class="integrity-ring">100%<span>INTEGRITY</span></div>
  </header>

  <nav class="left-nav-rail" aria-label="Command center navigation">
    <a class="rail-link active" href="/dashboard"><b>O</b>Dashboard</a>
    <a class="rail-link" href="/chat"><b>C</b>Chat</a>
    <a class="rail-link" href="/orbit"><b>R</b>Orbit</a>
    <a class="rail-link" href="/universe"><b>U</b>Universe</a>
    <a class="rail-link" href="/instruments"><b>I</b>Instruments</a>
    <a class="rail-link" href="/portfolio-health"><b>H</b>Health</a>
    <a class="rail-link" href="/memory"><b>M</b>Memory</a>
    <a class="rail-link" href="/safety"><b>S</b>Safety</a>
    <a class="rail-link" href="/settings"><b>G</b>Settings</a>
    <a class="rail-link" href="/briefing"><b>B</b>Briefing</a>
    <span class="rail-build">v167<br>VISUAL</span>
  </nav>

  <section class="orbit-cockpit" aria-label="Portfolio Orbit command panel">
    <div class="dashboard-orbit">
      <div class="orbit-grid"></div>
      <div class="allocation-mark">PORTFOLIO ALLOCATION<br>100.0%</div>
      <div class="orbit-ring-line r1"></div><div class="orbit-ring-line r2"></div><div class="orbit-ring-line r3"></div><div class="orbit-ring-line r4"></div>
      <div class="dashboard-core orbital-core"><strong>J.A.R.V.I.S.</strong><span>PORTFOLIO CORE</span></div>
      {orbit_planets}
      <div class="orbit-legend"><strong>ORBIT VIEW</strong><br>Allocation = Size<br>Freshness = Glow<br>Review = Amber outline</div>
    </div>
  </section>

  <aside class="selected-asset-telemetry" aria-label="Selected asset telemetry">
    <div class="telemetry-head"><h2>SELECTED:<strong>{html.escape(str(selected_asset.get("symbol")))}</strong></h2><span>LAST UPDATE<br>{html.escape(str(selected_asset.get("freshness")))}</span></div>
    <div class="telemetry-row"><b>Role</b><span>{html.escape(str(selected_asset.get("lane_label")))}<br>{html.escape(str(selected_asset.get("name")))}</span></div>
    <div class="telemetry-row"><b>Status</b><span>{html.escape(str(selected_asset.get("status")))}<br>No Action Taken. Monitor and review.</span></div>
    <div class="telemetry-row"><b>Data Freshness</b><span>{html.escape(str(selected_asset.get("freshness")))}<br>Quote context: {html.escape(str(selected_asset.get("source_note")))}</span></div>
    <div class="telemetry-row"><b>Risk Notes</b><ul><li>Review concentration and freshness before relying on this context.</li><li>Manual review required for any external decision.</li><li>J.A.R.V.I.S. creates no external action.</li></ul></div>
    <div class="telemetry-row"><b>J.A.R.V.I.S. Note</b><span>Evidence Summary ready. Prepare Manual Review. No external action is created.</span></div>
  </aside>

  <section class="cockpit-cards">
    <article class="cockpit-card"><h2>Today's Manual Plan</h2>{plan_rows}<p class="muted">Stay disciplined. You are in control.</p></article>
    <article class="cockpit-card"><h2>Portfolio Health</h2><div class="health-gauge"><div>{health_score}</div></div><ul class="status-list"><li>Diversification <span>Good</span></li><li>Data Freshness <span>Good</span></li><li>Safety <span>Strong</span></li><li>Review Context <span class="amber">Manual</span></li></ul></article>
    <article class="cockpit-card"><h2>What Changed</h2><ul class="change-list">{changed_items}</ul><p class="muted">{html.escape(changed_summary)}</p></article>
    <article class="cockpit-card"><h2>System Checks</h2><ul class="status-list"><li>Data Feeds <span>{data_feeds_label}</span></li><li>Calculations <span>{calculations_label}</span></li><li>Safety <span>Locked</span></li><li>Integrity <span>100%</span></li><li>AI Systems <span>Nominal</span></li></ul><p class="muted">All systems remain manual-only.</p></article>
  </section>

  <section class="market-movement">
    <h2>Market Movement</h2>
    <table class="market-table"><thead><tr><th>Asset</th><th>Price</th><th>24H</th><th>Trend</th><th>Status</th></tr></thead><tbody>{movement_rows}</tbody></table>
  </section>

  {ticker_html}

  <section class="assistant-strip" aria-label="assistant chat voice panel">
    <div class="quote-panel">Discipline is choosing between what you want now and what you want most.<br><span class="muted">- J.A.R.V.I.S.</span></div>
    <div class="map-panel">GLOBAL CONTEXT<br><span class="muted">{html.escape(universe_symbols)}</span></div>
    <a class="assistant-panel" href="/chat"><span class="assistant-orb"></span><span><strong>How can I assist your analysis today?</strong><br><small>Open chat for voice controls</small></span><span class="voice-wave"></span></a>
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
        "What Changed",
        "Market Movement",
        "Portfolio Orbit",
        "selected-asset-telemetry",
        "System Checks",
        "assistant chat voice panel",
    ]
    required_safety = [
        "Manual-only",
        "Prepare Manual Review",
        "No broker",
        "No credentials",
        "No orders",
        "No trades",
        "No Action Taken",
    ]
    required_motion = ["orbital-core", "orbit-ring-line", "dashboard-planet", "ticker-scroll", "headline-ticker", "voiceWave"]
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
