"""J.A.R.V.I.S. v161.0 premium orbital design system."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from typing import Any

STATUS_READY = "JARVIS_V161_0_PREMIUM_ORBITAL_DESIGN_SYSTEM_READY_SAFE"
FINAL_VERDICT_READY = "READY_FOR_PREMIUM_ORBITAL_UI_FOUNDATION"

NAV_ITEMS: tuple[tuple[str, str, str], ...] = (
    ("Dashboard", "/dashboard", "dashboard"),
    ("Chat", "/chat", "chat"),
    ("Orbit", "/orbit", "orbit"),
    ("Universe", "/universe", "universe"),
    ("Instruments", "/instruments", "instruments"),
    ("Portfolio Health", "/portfolio-health", "portfolio-health"),
    ("Memory", "/memory", "memory"),
    ("Safety", "/safety", "safety"),
    ("Settings", "/settings", "settings"),
    ("Briefing", "/briefing", "briefing"),
)

DESIGN_TOKENS: dict[str, Any] = {
    "colors": {
        "bg_deep": "#030711",
        "bg_orbit": "#07111f",
        "panel": "rgba(9, 20, 36, 0.72)",
        "panel_strong": "rgba(12, 27, 49, 0.88)",
        "line": "rgba(125, 218, 255, 0.18)",
        "line_hot": "rgba(92, 226, 255, 0.42)",
        "text": "#eef8ff",
        "muted": "#91a9c3",
        "cyan": "#55dfff",
        "blue": "#2d7dff",
        "teal": "#30e7bd",
        "green": "#78f2a8",
        "amber": "#ffbf5c",
        "red": "#ff5e6c",
        "magenta": "#ca6bff",
    },
    "spacing": {"xs": "6px", "sm": "10px", "md": "16px", "lg": "24px", "xl": "36px", "xxl": "56px"},
    "radius": {"sm": "8px", "md": "12px", "lg": "18px", "pill": "999px"},
    "motion": {
        "fast": "160ms",
        "normal": "260ms",
        "slow": "720ms",
        "ambient": "8s",
        "ease": "cubic-bezier(.22,.9,.24,1)",
        "soft": "cubic-bezier(.16,1,.3,1)",
    },
    "typography": {
        "body": "Inter, Segoe UI, system-ui, -apple-system, sans-serif",
        "mono": "Cascadia Mono, Consolas, ui-monospace, monospace",
        "hero": "clamp(34px, 6vw, 76px)",
        "section": "clamp(18px, 2.2vw, 28px)",
        "panel": "16px",
    },
}

COMPONENT_CLASSES = [
    "jarvis-shell",
    "jarvis-nav",
    "hud-hero",
    "glass-panel",
    "glass-card",
    "status-badge",
    "metric-tile",
    "orbital-core",
    "orbit-ring",
    "orbit-planet",
    "ticker-rail",
    "data-table",
    "detail-drawer",
    "motion-hover-lift",
    "motion-panel-enter",
    "state-ready",
    "state-review",
    "state-blocked",
    "state-speaking",
    "state-thinking",
]


def _css_var(name: str, value: str) -> str:
    return f"  --{name}: {value};"


def build_design_tokens_css() -> str:
    colors = DESIGN_TOKENS["colors"]
    spacing = DESIGN_TOKENS["spacing"]
    radius = DESIGN_TOKENS["radius"]
    motion = DESIGN_TOKENS["motion"]
    typography = DESIGN_TOKENS["typography"]
    variables = [":root {", "  color-scheme: dark;"]
    variables.extend(_css_var(f"jarvis-{key.replace('_', '-')}", value) for key, value in colors.items())
    variables.extend(_css_var(f"space-{key}", value) for key, value in spacing.items())
    variables.extend(_css_var(f"radius-{key}", value) for key, value in radius.items())
    variables.extend(_css_var(f"motion-{key}", value) for key, value in motion.items())
    variables.extend(_css_var(f"font-{key}", value) for key, value in typography.items())
    variables.append("}")
    return "\n".join(variables)


def build_premium_orbital_css() -> str:
    return build_design_tokens_css() + """
* { box-sizing: border-box; }
html { min-height: 100%; background: var(--jarvis-bg-deep); }
body {
  margin: 0;
  min-height: 100vh;
  font-family: var(--font-body);
  color: var(--jarvis-text);
  background:
    radial-gradient(circle at 50% -12%, rgba(85, 223, 255, .24), transparent 34%),
    radial-gradient(circle at 88% 8%, rgba(202, 107, 255, .13), transparent 28%),
    linear-gradient(135deg, #030711 0%, #061021 42%, #02050d 100%);
}
body::before {
  content: "";
  position: fixed;
  inset: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(85, 223, 255, .045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(85, 223, 255, .045) 1px, transparent 1px);
  background-size: 54px 54px;
  mask-image: radial-gradient(circle at 50% 18%, black, transparent 76%);
  animation: jarvisGridDrift 18s linear infinite;
}
.jarvis-shell { width: min(1400px, calc(100% - 32px)); margin: 0 auto; padding: 22px 0 54px; position: relative; }
.jarvis-nav { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; margin: 0 0 20px; }
.jarvis-nav a {
  color: var(--jarvis-muted);
  text-decoration: none;
  border: 1px solid rgba(125, 218, 255, .16);
  border-radius: var(--radius-pill);
  padding: 9px 12px;
  background: rgba(8, 18, 34, .58);
  font-weight: 800;
  font-size: 13px;
  transition: transform var(--motion-fast) var(--motion-ease), border-color var(--motion-fast), color var(--motion-fast), background var(--motion-fast);
}
.jarvis-nav a.active, .jarvis-nav a:hover, .jarvis-nav a:focus { color: var(--jarvis-text); border-color: rgba(85, 223, 255, .62); background: rgba(85, 223, 255, .12); outline: none; transform: translateY(-1px); }
.hud-hero, .glass-panel, .glass-card, .detail-drawer {
  position: relative;
  border: 1px solid var(--jarvis-line);
  background: linear-gradient(145deg, rgba(10, 25, 46, .82), rgba(4, 10, 20, .66));
  box-shadow: 0 22px 80px rgba(0, 0, 0, .36), inset 0 1px 0 rgba(255,255,255,.08);
  backdrop-filter: blur(18px);
  overflow: hidden;
}
.hud-hero::after, .glass-panel::after, .glass-card::after, .detail-drawer::after {
  content: "";
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: linear-gradient(110deg, transparent 0 35%, rgba(125, 218, 255, .09) 48%, transparent 62% 100%);
  transform: translateX(-110%);
  animation: jarvisLightSweep 9s var(--motion-soft) infinite;
}
.hud-hero { border-radius: var(--radius-lg); padding: clamp(22px, 4vw, 42px); display: grid; gap: 18px; }
.glass-panel { border-radius: var(--radius-lg); padding: 22px; }
.glass-card { border-radius: var(--radius-md); padding: 18px; transition: transform var(--motion-normal) var(--motion-ease), border-color var(--motion-normal), box-shadow var(--motion-normal); }
.motion-hover-lift:hover, .glass-card:hover { transform: translateY(-3px); border-color: var(--jarvis-line-hot); box-shadow: 0 26px 90px rgba(5, 18, 34, .48), 0 0 28px rgba(85, 223, 255, .08); }
.status-badge { display: inline-flex; width: max-content; align-items: center; gap: 8px; border-radius: var(--radius-pill); padding: 8px 11px; font-size: 12px; font-weight: 900; letter-spacing: .04em; text-transform: uppercase; border: 1px solid rgba(125,218,255,.24); color: var(--jarvis-text); background: rgba(85, 223, 255, .08); }
.status-badge::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; box-shadow: 0 0 12px currentColor; }
.state-ready { color: var(--jarvis-green); border-color: rgba(120, 242, 168, .38); background: rgba(40, 210, 142, .10); animation: jarvisReadyGlow 4.8s ease-in-out infinite; }
.state-review { color: var(--jarvis-amber); border-color: rgba(255, 191, 92, .42); background: rgba(255, 191, 92, .11); animation: jarvisReviewPulse 2.8s ease-in-out infinite; }
.state-blocked { color: var(--jarvis-red); border-color: rgba(255, 94, 108, .48); background: rgba(255, 94, 108, .10); animation: jarvisContainmentPulse 1.4s ease-out 1; }
.metric-tile { min-height: 96px; display: grid; gap: 7px; padding: 15px; border-radius: var(--radius-md); border: 1px solid rgba(125,218,255,.14); background: rgba(5, 13, 25, .56); }
.metric-label { color: var(--jarvis-muted); font-size: 11px; font-weight: 850; letter-spacing: .08em; text-transform: uppercase; }
.metric-value { color: var(--jarvis-text); font-size: clamp(20px, 2.6vw, 32px); font-weight: 900; letter-spacing: 0; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { text-align: left; padding: 12px 10px; border-bottom: 1px solid rgba(125,218,255,.13); vertical-align: top; }
.data-table th { color: var(--jarvis-muted); font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }
.data-table tr { transition: background var(--motion-fast) var(--motion-ease); }
.data-table tbody tr:hover { background: rgba(85, 223, 255, .07); }
.orbital-core { border-radius: 50%; background: radial-gradient(circle at 35% 28%, #ffffff 0 7%, var(--jarvis-cyan) 12% 32%, var(--jarvis-blue) 52%, rgba(10, 20, 38, .9) 76%); box-shadow: 0 0 42px rgba(85, 223, 255, .42), inset 0 0 28px rgba(255,255,255,.18); animation: jarvisCoreBreath 4.2s ease-in-out infinite; }
.orbit-ring { border: 1px solid rgba(85, 223, 255, .18); border-radius: 50%; box-shadow: inset 0 0 28px rgba(85, 223, 255, .04); animation: jarvisOrbitalDrift 18s linear infinite; }
.orbit-planet { border-radius: 50%; background: var(--jarvis-cyan); box-shadow: 0 0 18px currentColor; transition: transform var(--motion-normal) var(--motion-ease), filter var(--motion-normal); }
.orbit-planet:hover, .orbit-planet:focus { transform: scale(1.12); filter: brightness(1.18); outline: none; }
.ticker-rail { overflow: hidden; border-radius: var(--radius-md); border: 1px solid rgba(125,218,255,.14); background: rgba(4, 12, 24, .62); }
.ticker-track { display: flex; width: max-content; gap: 12px; animation: jarvisTicker 30s linear infinite; }
.motion-panel-enter { animation: jarvisPanelEnter var(--motion-slow) var(--motion-soft) both; }
.state-thinking { animation: jarvisOrbSweep 1.3s linear infinite; }
.state-speaking { animation: jarvisSpeakingPulse .8s ease-in-out infinite; }
@keyframes jarvisGridDrift { from { background-position: 0 0, 0 0; } to { background-position: 54px 54px, 54px 54px; } }
@keyframes jarvisLightSweep { 0%, 58% { transform: translateX(-120%); } 72% { transform: translateX(120%); } 100% { transform: translateX(120%); } }
@keyframes jarvisReadyGlow { 0%, 100% { box-shadow: 0 0 0 rgba(120,242,168,0); } 50% { box-shadow: 0 0 20px rgba(120,242,168,.18); } }
@keyframes jarvisReviewPulse { 0%, 100% { box-shadow: 0 0 0 rgba(255,191,92,0); } 50% { box-shadow: 0 0 24px rgba(255,191,92,.24); } }
@keyframes jarvisContainmentPulse { 0% { box-shadow: 0 0 0 rgba(255,94,108,0); } 42% { box-shadow: 0 0 34px rgba(255,94,108,.36); } 100% { box-shadow: 0 0 0 rgba(255,94,108,0); } }
@keyframes jarvisCoreBreath { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.035); } }
@keyframes jarvisOrbitalDrift { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes jarvisTicker { from { transform: translateX(0); } to { transform: translateX(-50%); } }
@keyframes jarvisPanelEnter { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
@keyframes jarvisOrbSweep { from { filter: hue-rotate(0deg); } to { filter: hue-rotate(360deg); } }
@keyframes jarvisSpeakingPulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.055); } }
@media (max-width: 760px) { .jarvis-shell { width: min(100% - 24px, 1400px); padding-top: 14px; } .glass-panel, .glass-card { padding: 16px; } }
@media (prefers-reduced-motion: reduce) { *, *::before, *::after { animation-duration: 1ms !important; animation-iteration-count: 1 !important; scroll-behavior: auto !important; transition-duration: 1ms !important; } }
"""


def render_nav(active: str) -> str:
    links = []
    for label, href, key in NAV_ITEMS:
        class_name = "active" if key == active else ""
        links.append(f'<a class="{class_name}" href="{href}">{label}</a>')
    return '<nav class="jarvis-nav app-nav" aria-label="J.A.R.V.I.S. orbital navigation">' + "".join(links) + "</nav>"


def render_status_badge(label: str, state: str = "ready") -> str:
    safe_state = state if state in {"ready", "review", "blocked"} else "ready"
    return f'<span class="status-badge state-{safe_state}">{label}</span>'


def render_shell(*, title: str, active: str, body: str, extra_head: str = "") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{build_premium_orbital_css()}</style>
{extra_head}
</head>
<body>
<div class="jarvis-shell motion-panel-enter">
{render_nav(active)}
{body}
</div>
</body>
</html>"""


@dataclass(frozen=True)
class PremiumOrbitalDesignSystemResult:
    status: str
    final_verdict: str
    design_system_ready: bool
    token_groups: list[str]
    reusable_components: list[str]
    motion_primitives: list[str]
    responsive_ready: bool
    manual_only: bool
    execution_forbidden: bool
    broker_connection_enabled: bool
    credentials_required: bool
    request_creation_enabled: bool
    external_instruction_created: bool
    external_completion_recorded: bool
    auto_approval_enabled: bool
    approval_mutation: bool
    allocation_mutation: bool
    warnings: list[str]
    blockers: list[str]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_premium_orbital_design_system_result() -> PremiumOrbitalDesignSystemResult:
    css = build_premium_orbital_css()
    required_markers = [
        "--jarvis-bg-deep",
        "--jarvis-cyan",
        "glass-panel",
        "status-badge",
        "orbital-core",
        "orbit-ring",
        "ticker-rail",
        "motion-panel-enter",
        "prefers-reduced-motion",
    ]
    missing = [marker for marker in required_markers if marker not in css]
    blockers = [] if not missing else ["design_system_markers_missing"]
    return PremiumOrbitalDesignSystemResult(
        status=STATUS_READY,
        final_verdict=FINAL_VERDICT_READY,
        design_system_ready=not blockers,
        token_groups=sorted(DESIGN_TOKENS),
        reusable_components=list(COMPONENT_CLASSES),
        motion_primitives=["ambient_grid", "glass_light_sweep", "hover_lift", "panel_enter", "orbital_drift", "status_pulse"],
        responsive_ready="@media (max-width: 760px)" in css and "prefers-reduced-motion" in css,
        manual_only=True,
        execution_forbidden=True,
        broker_connection_enabled=False,
        credentials_required=False,
        request_creation_enabled=False,
        external_instruction_created=False,
        external_completion_recorded=False,
        auto_approval_enabled=False,
        approval_mutation=False,
        allocation_mutation=False,
        warnings=["design system is visual only and does not mutate portfolio, approval, or local account state"],
        blockers=blockers,
    )


def format_premium_orbital_design_system(result: PremiumOrbitalDesignSystemResult) -> str:
    lines = [
        "J.A.R.V.I.S. PREMIUM ORBITAL DESIGN SYSTEM",
        f"status: {result.status}",
        f"final verdict: {result.final_verdict}",
        f"design system ready: {result.design_system_ready}",
        f"responsive ready: {result.responsive_ready}",
        "",
        "TOKEN GROUPS:",
        *[f"- {item}" for item in result.token_groups],
        "",
        "REUSABLE COMPONENTS:",
        *[f"- {item}" for item in result.reusable_components],
        "",
        "MOTION PRIMITIVES:",
        *[f"- {item}" for item in result.motion_primitives],
        "",
        "SAFETY:",
        f"- manual_only: {result.manual_only}",
        f"- execution_forbidden: {result.execution_forbidden}",
        f"- broker_connection_enabled: {result.broker_connection_enabled}",
        f"- credentials_required: {result.credentials_required}",
        f"- request_creation_enabled: {result.request_creation_enabled}",
        f"- external_instruction_created: {result.external_instruction_created}",
        f"- external_completion_recorded: {result.external_completion_recorded}",
        f"- auto_approval_enabled: {result.auto_approval_enabled}",
        f"- approval_mutation: {result.approval_mutation}",
        f"- allocation_mutation: {result.allocation_mutation}",
        "",
        "WARNINGS:",
        *[f"- {item}" for item in result.warnings or ["none"]],
        "",
        "BLOCKERS:",
        *[f"- {item}" for item in result.blockers or ["none"]],
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the J.A.R.V.I.S. premium orbital design system.")
    parser.add_argument("--premium-orbital-design-system", action="store_true")
    _args = parser.parse_args(argv)
    result = build_premium_orbital_design_system_result()
    print(format_premium_orbital_design_system(result))
    return 0 if result.design_system_ready else 1


__all__ = [
    "STATUS_READY",
    "FINAL_VERDICT_READY",
    "NAV_ITEMS",
    "DESIGN_TOKENS",
    "COMPONENT_CLASSES",
    "PremiumOrbitalDesignSystemResult",
    "build_design_tokens_css",
    "build_premium_orbital_css",
    "render_nav",
    "render_status_badge",
    "render_shell",
    "build_premium_orbital_design_system_result",
    "format_premium_orbital_design_system",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
