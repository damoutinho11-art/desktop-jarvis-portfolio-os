"""J.A.R.V.I.S. v163.0 premium portfolio orbit view."""

from __future__ import annotations

import argparse
import html
import json
from dataclasses import asdict, dataclass
from typing import Any, Mapping

from jarvis.runtime.finance_intelligence_core import build_finance_intelligence_core_result
from jarvis.runtime.portfolio_health_report_card import build_portfolio_health_report_card_result
from jarvis.runtime.premium_orbital_design_system import render_shell, render_status_badge
from jarvis.runtime.product_api import build_product_api_result

STATUS_READY = "JARVIS_V163_0_PORTFOLIO_ORBIT_VIEW_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V163_0_PORTFOLIO_ORBIT_VIEW_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_PREMIUM_PORTFOLIO_ORBIT_VIEW"

LANE_STYLE = {
    "emergency": {"ring": 0, "color": "var(--jarvis-green)", "label": "Emergency"},
    "etf_fund": {"ring": 1, "color": "var(--jarvis-cyan)", "label": "ETF/Fund Core"},
    "crypto": {"ring": 2, "color": "var(--jarvis-amber)", "label": "Crypto"},
    "individual_stock": {"ring": 3, "color": "var(--jarvis-magenta)", "label": "Stock Review"},
}

PLANET_POSITIONS = [
    (51, 8),
    (77, 24),
    (88, 52),
    (70, 78),
    (38, 87),
    (14, 61),
    (19, 28),
    (44, 18),
]


@dataclass(frozen=True)
class OrbitAsset:
    symbol: str
    name: str
    sleeve: str
    amount_eur: float
    freshness: str
    movement: str
    risk_note: str
    manual_review_note: str
    ring: int
    size: int
    color: str
    x: int
    y: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PortfolioOrbitViewResult:
    status: str
    final_verdict: str
    orbit_view_ready: bool
    portfolio_core_status: str
    assets: list[dict[str, Any]]
    manual_only: bool
    execution_forbidden: bool
    blockers: list[str]
    warnings: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _plain(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return dict(getattr(value, "__dict__", {}))


def _money(value: Any) -> float:
    try:
        return round(float(value or 0.0), 2)
    except Exception:
        return 0.0


def _safe_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True).replace("</", "<\\/")


def _coverage_by_symbol(finance: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    rows = finance.get("selected_instrument_coverage") or []
    if not isinstance(rows, list):
        return {}
    return {str(item.get("symbol") or "").upper(): dict(item) for item in rows if isinstance(item, Mapping)}


def _asset_name(symbol: str, item: Mapping[str, Any], coverage: Mapping[str, Any]) -> str:
    for key in ("name", "instrument_name", "display_name", "resolved_name"):
        if item.get(key):
            return str(item[key])
        if coverage.get(key):
            return str(coverage[key])
    return symbol


def build_orbit_assets(
    *,
    product_api_result: Mapping[str, Any] | Any | None = None,
    finance_result: Mapping[str, Any] | Any | None = None,
    current_date: str = "2026-06-21",
) -> list[OrbitAsset]:
    product = _plain(product_api_result) if product_api_result is not None else _plain(build_product_api_result(current_date=current_date))
    finance = _plain(finance_result) if finance_result is not None else _plain(build_finance_intelligence_core_result(current_date=current_date))
    week = product.get("week_plan") or {}
    selected = list(week.get("selected_instruments") or [])
    coverage = _coverage_by_symbol(finance)
    if not selected:
        selected = [
            {"lane": "emergency", "symbol": "Emergency", "amount_eur": week.get("emergency_top_up_eur")},
            {"lane": "etf_fund", "symbol": "VWCE", "amount_eur": week.get("etf_fund_eur")},
            {"lane": "crypto", "symbol": "BTC", "amount_eur": week.get("crypto_eur")},
            {"lane": "individual_stock", "symbol": "MSFT", "amount_eur": week.get("individual_stock_eur")},
        ]
    assets: list[OrbitAsset] = []
    max_amount = max([_money(item.get("amount_eur")) for item in selected] + [1.0])
    for index, item in enumerate(selected[:8]):
        symbol = str(item.get("symbol") or item.get("lane") or "Review").upper()
        lane = str(item.get("lane") or "etf_fund")
        style = LANE_STYLE.get(lane, LANE_STYLE["etf_fund"])
        amount = _money(item.get("amount_eur"))
        cov = coverage.get(symbol, {})
        freshness = str(cov.get("freshness") or cov.get("freshness_status") or "review")
        movement = str(cov.get("movement_summary") or cov.get("classification") or "Movement context for manual review")
        risk_note = (
            "Review concentration and freshness before relying on this context."
            if freshness.lower() not in {"ready", "fresh", "current"}
            else "Freshness context is calm; continue manual review."
        )
        position = PLANET_POSITIONS[index % len(PLANET_POSITIONS)]
        size = int(18 + min(24, (amount / max_amount) * 24))
        assets.append(
            OrbitAsset(
                symbol=symbol,
                name=_asset_name(symbol, item, cov),
                sleeve=str(style["label"]),
                amount_eur=amount,
                freshness=freshness,
                movement=movement,
                risk_note=risk_note,
                manual_review_note="Prepare Manual Review; J.A.R.V.I.S. does not create external instructions.",
                ring=int(style["ring"]),
                size=size,
                color=str(style["color"]),
                x=position[0],
                y=position[1],
            )
        )
    return assets


def build_portfolio_orbit_view_result(
    *,
    current_date: str = "2026-06-21",
    product_api_result: Mapping[str, Any] | Any | None = None,
    finance_result: Mapping[str, Any] | Any | None = None,
) -> PortfolioOrbitViewResult:
    assets = build_orbit_assets(
        current_date=current_date,
        product_api_result=product_api_result,
        finance_result=finance_result,
    )
    health = build_portfolio_health_report_card_result(current_date=current_date, product_api_result=product_api_result)
    blockers = []
    if not assets:
        blockers.append("orbit_assets_missing")
    if not health.report_card_ready:
        blockers.append("portfolio_health_not_ready")
    return PortfolioOrbitViewResult(
        status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
        final_verdict=FINAL_VERDICT_READY if not blockers else "REVIEW_REQUIRED_FOR_PREMIUM_PORTFOLIO_ORBIT_VIEW",
        orbit_view_ready=not blockers,
        portfolio_core_status=str(health.overall_status),
        assets=[asset.to_dict() for asset in assets],
        manual_only=True,
        execution_forbidden=True,
        blockers=blockers,
        warnings=["portfolio orbit is a visualization for manual review and does not mutate portfolio state"],
    )


def render_portfolio_orbit_view(result: PortfolioOrbitViewResult) -> str:
    first = result.assets[0] if result.assets else {}
    planets = []
    for asset in result.assets:
        review_class = " needs-review" if "ready" not in str(asset.get("freshness", "")).lower() else ""
        planets.append(
            '<button class="orbit-planet planet-focus'
            f'{review_class}" type="button" data-symbol="{html.escape(str(asset.get("symbol")))}" '
            f'style="left:{asset.get("x")}%; top:{asset.get("y")}%; width:{asset.get("size")}px; height:{asset.get("size")}px; color:{asset.get("color")}; background:{asset.get("color")};" '
            f'aria-label="Focus {html.escape(str(asset.get("symbol")))}">'
            f'<span>{html.escape(str(asset.get("symbol")))}</span>'
            "</button>"
        )
    legend_items = "".join(
        f'<li><span style="background:{style["color"]}"></span>{html.escape(str(style["label"]))}</li>'
        for style in LANE_STYLE.values()
    )
    extra_css = """
<style>
.orbit-layout { display:grid; grid-template-columns:minmax(0,1.35fr) 390px; gap:18px; align-items:stretch; }
.orbit-stage { min-height:690px; position:relative; display:grid; place-items:center; }
.orbit-map { width:min(680px, 88vw); aspect-ratio:1; position:relative; }
.orbit-map .orbital-core { position:absolute; width:132px; height:132px; left:50%; top:50%; transform:translate(-50%,-50%); display:grid; place-items:center; text-align:center; color:#02111c; font-weight:950; }
.orbit-map .ring { position:absolute; border-radius:50%; border:1px solid rgba(85,223,255,.2); box-shadow:inset 0 0 34px rgba(85,223,255,.05); animation:jarvisOrbitalDrift 26s linear infinite; }
.orbit-map .ring.r1 { inset:34%; }
.orbit-map .ring.r2 { inset:24%; animation-duration:34s; }
.orbit-map .ring.r3 { inset:14%; animation-duration:42s; }
.orbit-map .ring.r4 { inset:4%; animation-duration:52s; }
.planet-focus { position:absolute; border:0; cursor:pointer; display:grid; place-items:center; transform:translate(-50%,-50%); }
.planet-focus span { position:absolute; top:calc(100% + 7px); left:50%; transform:translateX(-50%); color:var(--jarvis-text); font-size:11px; font-weight:900; text-shadow:0 0 10px #000; white-space:nowrap; }
.planet-focus.needs-review { outline:2px solid rgba(255,191,92,.72); animation:jarvisReviewPulse 3.2s ease-in-out infinite; }
.orbit-side { display:grid; gap:14px; align-content:start; }
.detail-drawer { border-radius:var(--radius-lg); padding:22px; min-height:330px; }
.detail-title { margin:0; font-size:clamp(28px,4vw,44px); }
.telemetry-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:10px; margin-top:16px; }
.legend { display:grid; gap:9px; margin:0; padding:0; list-style:none; color:var(--jarvis-muted); }
.legend li { display:flex; align-items:center; gap:9px; }
.legend span { width:11px; height:11px; border-radius:50%; box-shadow:0 0 14px currentColor; }
.manual-note { color:var(--jarvis-green); }
@media (max-width:1040px) { .orbit-layout { grid-template-columns:1fr; } .orbit-stage { min-height:560px; } }
@media (max-width:640px) { .orbit-stage { min-height:410px; } .orbit-map .orbital-core { width:96px; height:96px; } .telemetry-grid { grid-template-columns:1fr; } }
</style>
"""
    assets_json = _safe_json(result.assets)
    initial = _safe_json(first)
    body = f"""
<main class="orbit-layout">
  <section class="glass-panel orbit-stage">
    <div class="section-head">
      <div>
        {render_status_badge("Portfolio Orbit", "ready" if result.orbit_view_ready else "review")}
        <h1 class="detail-title">Portfolio Orbit</h1>
        <p class="muted">The portfolio is a solar system: sleeves are orbits, instruments are planets, glow reflects freshness, and amber outlines mark review context.</p>
      </div>
    </div>
    <div class="orbit-map" aria-label="Portfolio orbital visualization">
      <div class="ring r1 orbit-ring"></div><div class="ring r2 orbit-ring"></div><div class="ring r3 orbit-ring"></div><div class="ring r4 orbit-ring"></div>
      <div class="orbital-core"><span>J.A.R.V.I.S.<br>{html.escape(result.portfolio_core_status.upper())}</span></div>
      {''.join(planets)}
    </div>
  </section>
  <aside class="orbit-side">
    <section class="detail-drawer" id="orbitDetail">
      <span class="status-badge state-ready">Selected Instrument</span>
      <h2 class="detail-title" id="detailSymbol">{html.escape(str(first.get("symbol", "n/a")))}</h2>
      <p class="muted" id="detailName">{html.escape(str(first.get("name", "No instrument selected")))}</p>
      <div class="telemetry-grid">
        <div class="metric-tile"><span class="metric-label">Sleeve</span><strong class="metric-value" id="detailSleeve">{html.escape(str(first.get("sleeve", "n/a")))}</strong></div>
        <div class="metric-tile"><span class="metric-label">Plan Amount</span><strong class="metric-value" id="detailAmount">EUR {float(first.get("amount_eur") or 0):.2f}</strong></div>
        <div class="metric-tile"><span class="metric-label">Freshness</span><strong class="metric-value" id="detailFreshness">{html.escape(str(first.get("freshness", "review")))}</strong></div>
        <div class="metric-tile"><span class="metric-label">Core Status</span><strong class="metric-value">{html.escape(result.portfolio_core_status)}</strong></div>
      </div>
      <h3>Movement</h3><p class="muted" id="detailMovement">{html.escape(str(first.get("movement", "Movement context for manual review")))}</p>
      <h3>Risk Notes</h3><p class="muted" id="detailRisk">{html.escape(str(first.get("risk_note", "Review freshness and concentration.")))}</p>
      <h3>Manual Review Note</h3><p class="manual-note" id="detailManual">{html.escape(str(first.get("manual_review_note", "Prepare Manual Review.")))}</p>
    </section>
    <section class="glass-card">
      <h2>Legend</h2>
      <ul class="legend">{legend_items}</ul>
      <p class="muted">Planet size reflects planned amount. Distance and amber outline are visual review cues, not instructions.</p>
    </section>
  </aside>
</main>
<script>
const orbitAssets = {assets_json};
const initialOrbitAsset = {initial};
function updateOrbitDetail(asset) {{
  if (!asset) return;
  document.getElementById("detailSymbol").textContent = asset.symbol || "n/a";
  document.getElementById("detailName").textContent = asset.name || "";
  document.getElementById("detailSleeve").textContent = asset.sleeve || "n/a";
  document.getElementById("detailAmount").textContent = "EUR " + Number(asset.amount_eur || 0).toFixed(2);
  document.getElementById("detailFreshness").textContent = asset.freshness || "review";
  document.getElementById("detailMovement").textContent = asset.movement || "Movement context for manual review";
  document.getElementById("detailRisk").textContent = asset.risk_note || "Review freshness and concentration.";
  document.getElementById("detailManual").textContent = asset.manual_review_note || "Prepare Manual Review.";
}}
document.querySelectorAll(".planet-focus").forEach((planet) => {{
  planet.addEventListener("click", () => {{
    const asset = orbitAssets.find((item) => item.symbol === planet.dataset.symbol);
    updateOrbitDetail(asset);
  }});
}});
updateOrbitDetail(initialOrbitAsset);
</script>
"""
    return render_shell(title="J.A.R.V.I.S. Portfolio Orbit", active="orbit", body=body, extra_head=extra_css)


def format_portfolio_orbit_view(result: PortfolioOrbitViewResult) -> str:
    lines = [
        "J.A.R.V.I.S. PORTFOLIO ORBIT VIEW",
        f"status: {result.status}",
        f"final verdict: {result.final_verdict}",
        f"orbit view ready: {result.orbit_view_ready}",
        f"portfolio core status: {result.portfolio_core_status}",
        f"assets: {len(result.assets)}",
        f"manual_only: {result.manual_only}",
        f"execution_forbidden: {result.execution_forbidden}",
        "",
        "ASSETS:",
    ]
    lines.extend(f"- {item['symbol']}: {item['sleeve']}; freshness={item['freshness']}" for item in result.assets or [])
    lines.extend(["", "WARNINGS:", *[f"- {item}" for item in result.warnings or ["none"]], "", "BLOCKERS:"])
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render or validate the premium portfolio orbit view.")
    parser.add_argument("--portfolio-orbit-view", action="store_true")
    parser.add_argument("--current-date", default="2026-06-21")
    parser.add_argument("--html", action="store_true")
    args = parser.parse_args(argv)
    result = build_portfolio_orbit_view_result(current_date=args.current_date)
    if args.html:
        print(render_portfolio_orbit_view(result))
    else:
        print(format_portfolio_orbit_view(result))
    return 0 if result.orbit_view_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "FINAL_VERDICT_READY",
    "OrbitAsset",
    "PortfolioOrbitViewResult",
    "build_orbit_assets",
    "build_portfolio_orbit_view_result",
    "render_portfolio_orbit_view",
    "format_portfolio_orbit_view",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
