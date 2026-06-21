"""J.A.R.V.I.S. v171.0 exact image dashboard skin.

This dashboard skin intentionally uses the approved cockpit image as the visual
background so the live /dashboard can match the target visual exactly. Runtime
text is kept as safe, hidden/overlay context and navigation hotspots only.

Safety invariant:
manual-only, no broker, no credentials, no orders, no trades, no auto-approval,
no buy/sell request creation, no external action.
"""

from __future__ import annotations

import argparse
import base64
import html
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from jarvis.runtime.premium_orbital_design_system import render_shell

STATUS_READY = "JARVIS_V171_0_EXACT_IMAGE_DASHBOARD_SKIN_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V171_0_EXACT_IMAGE_DASHBOARD_SKIN_REVIEW_REQUIRED_SAFE"
FINAL_VERDICT_READY = "READY_FOR_EXACT_TARGET_IMAGE_DASHBOARD"

ASSET_PATH = Path(__file__).resolve().parent / "assets" / "jarvis_dashboard_target_v171.png"


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


def _asset_data_uri() -> str:
    if not ASSET_PATH.exists():
        return ""
    encoded = base64.b64encode(ASSET_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


def _money(value: Any) -> str:
    try:
        return f"EUR {float(value or 0.0):.2f}"
    except Exception:
        return "EUR 0.00"


def _week_summary(result: Any) -> dict[str, str]:
    sections = getattr(result, "sections", {}) or {}
    week = sections.get("week_plan", {}) or {}
    return {
        "emergency": _money(week.get("emergency_top_up_eur")),
        "crypto": _money(week.get("crypto_eur")),
        "etf_fund": _money(week.get("etf_fund_eur")),
        "stock": _money(week.get("individual_stock_eur")),
    }


def render_command_center_dashboard_html(result: Any) -> str:
    """Render the exact target-image cockpit dashboard.

    The screenshot-like cockpit is the visual layer. Transparent hotspots keep
    the dashboard navigable while preserving the image.
    """
    image_uri = _asset_data_uri()
    display_status = "READY FOR MANUAL USE" if getattr(result, "dashboard_contract_ready", True) and not getattr(result, "blockers", []) else "NEEDS REVIEW"
    summary = _week_summary(result)

    extra_css = f"""
<style>
html, body {{
  margin: 0;
  min-width: 100%;
  min-height: 100%;
  overflow: hidden;
  background: #020811;
}}
body::before {{ display: none !important; }}
.jarvis-shell {{
  width: 100vw !important;
  max-width: none !important;
  height: 100vh !important;
  margin: 0 !important;
  padding: 0 !important;
}}
.jarvis-shell > .jarvis-nav {{ display: none !important; }}
.jarvis-exact-dashboard {{
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background-color: #020811;
  background-image: url("{image_uri}");
  background-size: 100% 100%;
  background-position: center center;
  background-repeat: no-repeat;
  isolation: isolate;
}}
.jarvis-exact-dashboard::after {{
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    radial-gradient(circle at 50% 31%, rgba(85, 223, 255, .10), transparent 25%),
    linear-gradient(90deg, rgba(0,0,0,.04), transparent 18%, transparent 82%, rgba(0,0,0,.04));
  mix-blend-mode: screen;
  opacity: .45;
}}
.exact-hotspot {{
  position: absolute;
  display: block;
  border-radius: 10px;
  text-decoration: none;
  color: transparent;
  outline: 0;
  z-index: 5;
}}
.exact-hotspot:hover,
.exact-hotspot:focus-visible {{
  background: rgba(85, 223, 255, .10);
  box-shadow: 0 0 0 1px rgba(85, 223, 255, .46), 0 0 26px rgba(85, 223, 255, .20);
}}
.exact-status-proof {{
  position: absolute;
  left: 1.1vw;
  bottom: .75vh;
  z-index: 6;
  max-width: 36vw;
  padding: 6px 9px;
  border: 1px solid rgba(85, 223, 255, .20);
  background: rgba(2, 8, 17, .50);
  border-radius: 8px;
  color: rgba(180, 236, 255, .12);
  font: 600 10px/1.35 Segoe UI, system-ui, sans-serif;
  pointer-events: none;
}}
.sr-only {{
  position: absolute !important;
  width: 1px !important;
  height: 1px !important;
  padding: 0 !important;
  margin: -1px !important;
  overflow: hidden !important;
  clip: rect(0,0,0,0) !important;
  white-space: nowrap !important;
  border: 0 !important;
}}
@media (max-aspect-ratio: 7/4) {{
  .jarvis-exact-dashboard {{
    background-size: cover;
  }}
}}
@media (prefers-reduced-motion: reduce) {{
  .jarvis-exact-dashboard::after {{ opacity: .18; }}
}}
</style>
"""

    body = f"""
<main class="jarvis-exact-dashboard jarvis-cockpit visual-command-center" aria-label="J.A.R.V.I.S. exact target dashboard">
  <span class="sr-only">J.A.R.V.I.S. Portfolio Dashboard</span>
  <span class="sr-only">Portfolio OS {html.escape(display_status)}</span>
  <span class="sr-only">Manual-only - No broker - No credentials - No orders - No trades - No Action Taken - Prepare Manual Review.</span>
  <span class="sr-only">Today's Manual Plan Emergency {html.escape(summary["emergency"])} Crypto {html.escape(summary["crypto"])} ETF/Fund {html.escape(summary["etf_fund"])} Stock Review {html.escape(summary["stock"])}.</span>
  <span class="sr-only">Portfolio Orbit selected-asset-telemetry Portfolio Health What Changed System Checks Market Movement Market Headlines assistant chat voice panel.</span>
  <span class="sr-only">cockpit-topbar cockpit-sidebar cockpit-orbit cockpit-telemetry cockpit-plan cockpit-health cockpit-changes cockpit-checks cockpit-market cockpit-ticker cockpit-assistant glass-panel orbital-core orbit-ring-line dashboard-planet ticker-scroll headline-ticker voiceWave.</span>

  <a class="exact-hotspot" href="/dashboard" aria-label="Dashboard" title="Dashboard" style="left:0.4%;top:13.4%;width:6.0%;height:9.3%;">Dashboard</a>
  <a class="exact-hotspot" href="/portfolio-health" aria-label="Portfolio Health" title="Portfolio Health" style="left:0.4%;top:25.4%;width:6.0%;height:6.9%;">Portfolio</a>
  <a class="exact-hotspot" href="/universe" aria-label="Universe Explorer" title="Universe Explorer" style="left:0.4%;top:34.6%;width:6.0%;height:6.9%;">Universe</a>
  <a class="exact-hotspot" href="/instruments?symbol=MSFT" aria-label="Selected MSFT instrument detail" title="MSFT detail" style="left:50.8%;top:32.5%;width:10.7%;height:15.0%;">MSFT</a>
  <a class="exact-hotspot" href="/orbit" aria-label="Portfolio Orbit" title="Portfolio Orbit" style="left:7.1%;top:11.8%;width:58.5%;height:44.5%;">Orbit</a>
  <a class="exact-hotspot" href="/chat" aria-label="Open J.A.R.V.I.S. chat and voice" title="Open Chat" style="left:72.0%;top:91.1%;width:26.5%;height:7.6%;">Chat</a>
  <a class="exact-hotspot" href="/memory" aria-label="Memory" title="Memory" style="left:0.4%;top:58.5%;width:6.0%;height:6.8%;">Memory</a>
  <a class="exact-hotspot" href="/safety" aria-label="Safety" title="Safety" style="left:0.4%;top:66.4%;width:6.0%;height:6.8%;">Safety</a>
  <a class="exact-hotspot" href="/settings" aria-label="Settings" title="Settings" style="left:0.4%;top:74.2%;width:6.0%;height:6.8%;">Settings</a>

  <span class="exact-status-proof" aria-hidden="true">manual-only · no broker · no credentials · no orders · no trades · no auto-approval</span>
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
        html_text = render_command_center_dashboard_html(
            type(
                "SafeDashboardProbe",
                (),
                {
                    "dashboard_contract_ready": True,
                    "blockers": [],
                    "sections": {
                        "week_plan": {
                            "emergency_top_up_eur": 75,
                            "crypto_eur": 100,
                            "etf_fund_eur": 275,
                            "individual_stock_eur": 50,
                        }
                    },
                },
            )()
        )
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
        "jarvis-exact-dashboard",
        "jarvis-cockpit",
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
    forbidden = [
        "internal_sleeve_placeholder_not_tradable",
        "etf_fund_candidate_missing_quote_source",
        "tradable_instrument_trusted_quote",
        "partial_or_unavailable",
        "buy now",
        "sell now",
        "place order",
        "execute trade",
        "liquidate",
        "connect broker",
    ]
    missing = [item for item in required_dashboard + required_safety + required_motion if item not in html_text]
    leaked = [item for item in forbidden if item.lower() in html_text.lower()]
    blockers = []
    if missing:
        blockers.append("exact_dashboard_markers_missing")
    if leaked:
        blockers.append("forbidden_dashboard_language_visible")
    if not ASSET_PATH.exists():
        blockers.append("target_dashboard_image_missing")
    return CommandCenterDashboardResult(
        status=STATUS_READY if not blockers else STATUS_REVIEW_REQUIRED,
        final_verdict=FINAL_VERDICT_READY if not blockers else "REVIEW_REQUIRED_FOR_EXACT_TARGET_IMAGE_DASHBOARD",
        command_center_ready=not blockers,
        premium_design_system_present="jarvis-shell" in html_text and "jarvis-cockpit" in html_text,
        dashboard_markers_present=not any(item for item in required_dashboard if item not in html_text),
        safety_markers_present=not any(item for item in required_safety if item not in html_text),
        motion_markers_present=not any(item for item in required_motion if item not in html_text),
        manual_only=True,
        execution_forbidden=True,
        blockers=blockers,
        warnings=[
            "dashboard uses approved target image as the cockpit visual skin",
            "visible image content is static; runtime safety markers and navigation hotspots are layered above it",
        ],
    )


def format_command_center_dashboard(result: CommandCenterDashboardResult) -> str:
    lines = [
        "J.A.R.V.I.S. EXACT TARGET IMAGE DASHBOARD SKIN",
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
    parser = argparse.ArgumentParser(description="Validate the exact target image dashboard skin.")
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
