"""J.A.R.V.I.S. v164.0 orbital instrument detail panel."""

from __future__ import annotations

import argparse
import html
from dataclasses import asdict, dataclass
from typing import Any, Mapping

from jarvis.runtime.finance_database_universe import build_finance_database_universe_result
from jarvis.runtime.finance_intelligence_core import build_finance_intelligence_core_result
from jarvis.runtime.finance_toolkit_fundamentals import build_finance_toolkit_fundamentals_result
from jarvis.runtime.premium_orbital_design_system import render_shell, render_status_badge
from jarvis.runtime.product_api import build_product_api_result
from jarvis.runtime.universe_explorer import DEFAULT_FIXTURE_UNIVERSE

STATUS_READY = "JARVIS_V164_0_ORBITAL_INSTRUMENT_DETAIL_PANEL_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V164_0_ORBITAL_INSTRUMENT_DETAIL_PANEL_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_ORBITAL_INSTRUMENT_DETAIL_PANEL"


@dataclass(frozen=True)
class OrbitalInstrumentDetailResult:
    status: str
    final_verdict: str
    detail_panel_ready: bool
    selected_symbol: str
    identity_metadata: dict[str, Any]
    price_movement_freshness: dict[str, Any]
    fundamental_context: dict[str, Any]
    portfolio_role: dict[str, Any]
    news_context: list[dict[str, Any]]
    risk_notes: list[str]
    why_visible: list[str]
    manual_checklist: list[str]
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


def _symbol(value: Any) -> str:
    text = str(value or "MSFT").strip().upper()
    return text or "MSFT"


def _coverage_by_symbol(finance: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    rows = finance.get("selected_instrument_coverage") or []
    if not isinstance(rows, list):
        return {}
    return {str(item.get("symbol") or "").upper(): dict(item) for item in rows if isinstance(item, Mapping)}


def _find_metadata(symbol: str, universe_fixture: Mapping[str, Any] | None = None) -> tuple[dict[str, Any], list[str]]:
    result = build_finance_database_universe_result(fixture_universe=universe_fixture)
    if not result.sample_instruments:
        result = build_finance_database_universe_result(fixture_universe=DEFAULT_FIXTURE_UNIVERSE)
    warnings = list(result.warnings or [])
    for item in result.sample_instruments:
        if str(item.get("symbol") or "").upper() == symbol:
            return dict(item), warnings
    return {
        "symbol": symbol,
        "name": symbol,
        "asset_type": "unknown",
        "exchange": None,
        "country": None,
        "currency": None,
        "sector_category": None,
        "source": "symbol fallback",
    }, warnings + [f"{symbol} metadata not found in current universe context"]


def _portfolio_role(symbol: str, product: Mapping[str, Any]) -> dict[str, Any]:
    week = product.get("week_plan") or {}
    selected = list(week.get("selected_instruments") or [])
    for item in selected:
        if str(item.get("symbol") or "").upper() == symbol:
            return {
                "appears_in_plan": True,
                "sleeve": item.get("lane"),
                "amount_eur": item.get("amount_eur"),
                "reason": "selected instrument appears in the current manual plan context",
            }
    return {
        "appears_in_plan": False,
        "sleeve": None,
        "amount_eur": None,
        "reason": "instrument appears through universe or detail lookup context",
    }


def _news_context(symbol: str, product: Mapping[str, Any]) -> list[dict[str, Any]]:
    live = product.get("live_news_context") or {}
    rows = []
    for item in live.get("top_headlines") or []:
        text = f"{item.get('title', '')} {' '.join(item.get('entity_tags') or [])}".upper()
        if symbol in text:
            rows.append(
                {
                    "title": item.get("title"),
                    "source": item.get("source"),
                    "freshness_status": item.get("freshness_status"),
                    "url": item.get("url"),
                }
            )
    return rows[:5]


def _risk_notes(symbol: str, metadata: Mapping[str, Any], coverage: Mapping[str, Any], fundamentals_ready: bool) -> list[str]:
    notes = []
    freshness = str(coverage.get("freshness") or coverage.get("freshness_status") or "").lower()
    if not freshness or any(token in freshness for token in ("partial", "missing", "unavailable", "review")):
        notes.append("freshness or movement context needs review")
    if metadata.get("asset_type") in {"crypto"}:
        notes.append("crypto sleeve is higher volatility context")
    if metadata.get("asset_type") in {"fund"} and not metadata.get("currency"):
        notes.append("fund currency metadata is missing")
    if not fundamentals_ready:
        notes.append("fundamental context is optional or unavailable for this symbol")
    return list(dict.fromkeys(notes)) or ["no elevated detail-panel risk note detected"]


def build_orbital_instrument_detail_result(
    *,
    symbol: str = "MSFT",
    current_date: str = "2026-06-21",
    product_api_result: Mapping[str, Any] | Any | None = None,
    finance_result: Mapping[str, Any] | Any | None = None,
    universe_fixture: Mapping[str, Any] | None = None,
    fundamentals_fixture: Mapping[str, Any] | None = None,
) -> OrbitalInstrumentDetailResult:
    selected_symbol = _symbol(symbol)
    product = _plain(product_api_result) if product_api_result is not None else _plain(build_product_api_result(current_date=current_date))
    finance = _plain(finance_result) if finance_result is not None else _plain(build_finance_intelligence_core_result(current_date=current_date))
    metadata, metadata_warnings = _find_metadata(selected_symbol, universe_fixture)
    coverage = _coverage_by_symbol(finance).get(selected_symbol, {})
    fundamentals = build_finance_toolkit_fundamentals_result(
        symbols=[selected_symbol],
        fixture_fundamentals=fundamentals_fixture,
    )
    fundamental_context = fundamentals.fundamental_context.get(selected_symbol, {})
    role = _portfolio_role(selected_symbol, product)
    news = _news_context(selected_symbol, product)
    freshness = {
        "symbol": selected_symbol,
        "freshness": coverage.get("freshness") or coverage.get("freshness_status") or "review",
        "movement": coverage.get("movement_summary") or coverage.get("classification") or "movement context for manual review",
        "source": coverage.get("source") or coverage.get("provider") or "J.A.R.V.I.S. finance intelligence",
        "as_of": coverage.get("source_as_of") or coverage.get("as_of") or current_date,
    }
    why_visible = [role["reason"]]
    if metadata.get("source"):
        why_visible.append(f"metadata source: {metadata.get('source')}")
    if coverage:
        why_visible.append("freshness or movement context is available")
    manual_checklist = [
        "Confirm identity metadata and symbol before relying on the context.",
        "Review freshness and movement notes.",
        "Read risk notes and any available news context.",
        "Use this as an Evidence Summary for manual review only.",
    ]
    blockers: list[str] = []
    if not selected_symbol:
        blockers.append("selected_symbol_missing")
    return OrbitalInstrumentDetailResult(
        status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
        final_verdict=FINAL_VERDICT_READY if not blockers else "REVIEW_REQUIRED_FOR_ORBITAL_INSTRUMENT_DETAIL_PANEL",
        detail_panel_ready=not blockers,
        selected_symbol=selected_symbol,
        identity_metadata=metadata,
        price_movement_freshness=freshness,
        fundamental_context=fundamental_context,
        portfolio_role=role,
        news_context=news,
        risk_notes=_risk_notes(selected_symbol, metadata, coverage, fundamentals.fundamentals_ready),
        why_visible=why_visible,
        manual_checklist=manual_checklist,
        manual_only=True,
        execution_forbidden=True,
        blockers=blockers,
        warnings=list(dict.fromkeys(metadata_warnings + list(fundamentals.warnings or []))),
    )


def _dict_list(items: Mapping[str, Any]) -> str:
    if not items:
        return "<li>none</li>"
    return "".join(f"<li><strong>{html.escape(str(key))}:</strong> {html.escape(str(value))}</li>" for key, value in items.items())


def _list(items: list[Any]) -> str:
    return "".join(f"<li>{html.escape(str(item))}</li>" for item in (items or ["none"]))


def render_orbital_instrument_detail_panel(result: OrbitalInstrumentDetailResult) -> str:
    state = "ready" if result.detail_panel_ready else "review"
    fundamentals = result.fundamental_context
    populated_sections = [key for key, value in fundamentals.items() if value and key not in {"symbol", "source"}]
    news_items = "".join(
        "<article class=\"glass-card\">"
        f"<strong>{html.escape(str(item.get('title') or 'News context'))}</strong>"
        f"<p class=\"muted\">{html.escape(str(item.get('source') or 'public source'))} | {html.escape(str(item.get('freshness_status') or 'freshness unknown'))}</p>"
        "</article>"
        for item in result.news_context
    ) or '<article class="glass-card"><strong>No symbol-specific headline loaded</strong><p class="muted">News context is optional and not a blocker.</p></article>'
    extra_css = """
<style>
.detail-grid { display:grid; grid-template-columns:minmax(0,1.1fr) minmax(320px,.9fr); gap:16px; }
.detail-hero { display:grid; gap:14px; }
.symbol-title { margin:0; font-size:clamp(42px,7vw,92px); line-height:.9; }
.muted { color:var(--jarvis-muted); line-height:1.55; }
.detail-section { display:grid; gap:12px; }
.detail-stack { display:grid; gap:14px; }
.metric-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
.panel-list { margin:0; padding-left:18px; color:var(--jarvis-muted); line-height:1.55; }
.manual-checklist li { margin-bottom:8px; }
@media (max-width:960px) { .detail-grid { grid-template-columns:1fr; } }
@media (max-width:640px) { .metric-grid { grid-template-columns:1fr; } }
</style>
"""
    body = f"""
<main class="detail-grid">
  <section class="hud-hero detail-hero">
    {render_status_badge("Instrument Detail", state)}
    <h1 class="symbol-title">{html.escape(result.selected_symbol)}</h1>
    <p class="muted">{html.escape(str(result.identity_metadata.get("name") or result.selected_symbol))}</p>
    <div class="metric-grid">
      <div class="metric-tile"><span class="metric-label">Asset Type</span><strong class="metric-value">{html.escape(str(result.identity_metadata.get("asset_type") or "unknown"))}</strong></div>
      <div class="metric-tile"><span class="metric-label">Sleeve</span><strong class="metric-value">{html.escape(str(result.portfolio_role.get("sleeve") or "lookup"))}</strong></div>
      <div class="metric-tile"><span class="metric-label">Freshness</span><strong class="metric-value">{html.escape(str(result.price_movement_freshness.get("freshness")))}</strong></div>
      <div class="metric-tile"><span class="metric-label">Plan Amount</span><strong class="metric-value">EUR {float(result.portfolio_role.get("amount_eur") or 0):.2f}</strong></div>
    </div>
    <p class="muted">Manual-only detail panel. No external instruction, order ticket, account login, private sync, or auto-approval path is present.</p>
  </section>
  <aside class="detail-stack">
    <section class="glass-panel detail-section"><h2>Identity and Metadata</h2><ul class="panel-list">{_dict_list(result.identity_metadata)}</ul></section>
    <section class="glass-panel detail-section"><h2>Why It Appears</h2><ul class="panel-list">{_list(result.why_visible)}</ul></section>
  </aside>
  <section class="glass-panel detail-section">
    <h2>Price / Movement / Freshness</h2>
    <ul class="panel-list">{_dict_list(result.price_movement_freshness)}</ul>
  </section>
  <section class="glass-panel detail-section">
    <h2>Fundamental Context</h2>
    <p class="muted">Available sections: {html.escape(", ".join(populated_sections) if populated_sections else "optional context unavailable")}</p>
    <ul class="panel-list">{_dict_list({key: value for key, value in fundamentals.items() if key in populated_sections[:4]})}</ul>
  </section>
  <section class="glass-panel detail-section">
    <h2>Risk Notes</h2>
    <ul class="panel-list">{_list(result.risk_notes)}</ul>
  </section>
  <section class="glass-panel detail-section">
    <h2>News Context</h2>
    <div class="detail-stack">{news_items}</div>
  </section>
  <section class="glass-panel detail-section">
    <h2>Manual Checklist</h2>
    <ul class="panel-list manual-checklist">{_list(result.manual_checklist)}</ul>
  </section>
</main>
"""
    return render_shell(
        title=f"J.A.R.V.I.S. Instrument Detail - {result.selected_symbol}",
        active="instruments",
        body=body,
        extra_head=extra_css,
    )


def format_orbital_instrument_detail_panel(result: OrbitalInstrumentDetailResult) -> str:
    lines = [
        "J.A.R.V.I.S. ORBITAL INSTRUMENT DETAIL PANEL",
        f"status: {result.status}",
        f"final verdict: {result.final_verdict}",
        f"detail panel ready: {result.detail_panel_ready}",
        f"selected symbol: {result.selected_symbol}",
        f"manual_only: {result.manual_only}",
        f"execution_forbidden: {result.execution_forbidden}",
        "",
        "IDENTITY:",
        *[f"- {key}: {value}" for key, value in result.identity_metadata.items()],
        "",
        "FRESHNESS:",
        *[f"- {key}: {value}" for key, value in result.price_movement_freshness.items()],
        "",
        "MANUAL CHECKLIST:",
        *[f"- {item}" for item in result.manual_checklist],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render or validate an orbital instrument detail panel.")
    parser.add_argument("--orbital-instrument-detail", action="store_true")
    parser.add_argument("--symbol", default="MSFT")
    parser.add_argument("--current-date", default="2026-06-21")
    parser.add_argument("--html", action="store_true")
    args = parser.parse_args(argv)
    result = build_orbital_instrument_detail_result(symbol=args.symbol, current_date=args.current_date)
    if args.html:
        print(render_orbital_instrument_detail_panel(result))
    else:
        print(format_orbital_instrument_detail_panel(result))
    return 0 if result.detail_panel_ready else 1


__all__ = [
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "FINAL_VERDICT_READY",
    "OrbitalInstrumentDetailResult",
    "build_orbital_instrument_detail_result",
    "render_orbital_instrument_detail_panel",
    "format_orbital_instrument_detail_panel",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
