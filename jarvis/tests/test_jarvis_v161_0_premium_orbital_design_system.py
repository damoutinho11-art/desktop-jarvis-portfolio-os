from __future__ import annotations

import contextlib
import io
import unittest

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.premium_orbital_design_system import (
    STATUS_READY,
    build_premium_orbital_css,
    build_premium_orbital_design_system_result,
    render_nav,
    render_shell,
    render_status_badge,
)


class JarvisV161PremiumOrbitalDesignSystemTests(unittest.TestCase):
    def test_design_system_result_ready_safe(self) -> None:
        result = build_premium_orbital_design_system_result()

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.design_system_ready)
        self.assertTrue(result.responsive_ready)
        self.assertEqual(result.blockers, [])
        self.assertTrue(result.manual_only)
        self.assertTrue(result.execution_forbidden)
        self.assertFalse(result.broker_connection_enabled)
        self.assertFalse(result.credentials_required)
        self.assertFalse(result.request_creation_enabled)
        self.assertFalse(result.external_instruction_created)
        self.assertFalse(result.external_completion_recorded)
        self.assertFalse(result.auto_approval_enabled)
        self.assertFalse(result.approval_mutation)
        self.assertFalse(result.allocation_mutation)

    def test_css_contains_tokens_components_and_motion(self) -> None:
        css = build_premium_orbital_css()

        for marker in (
            "--jarvis-bg-deep",
            "--jarvis-cyan",
            "--jarvis-amber",
            "--jarvis-magenta",
            ".glass-panel",
            ".status-badge",
            ".orbital-core",
            ".orbit-ring",
            ".orbit-planet",
            ".ticker-rail",
            ".data-table",
            ".motion-panel-enter",
            "@keyframes jarvisGridDrift",
            "@keyframes jarvisLightSweep",
            "@media (prefers-reduced-motion: reduce)",
        ):
            self.assertIn(marker, css)

    def test_nav_and_shell_render_target_structure(self) -> None:
        nav = render_nav("orbit")
        shell = render_shell(title="J.A.R.V.I.S. Test", active="orbit", body="<main>body</main>")

        self.assertIn('href="/dashboard"', nav)
        self.assertIn('href="/orbit"', nav)
        self.assertIn('href="/universe"', nav)
        self.assertIn('href="/portfolio-health"', nav)
        self.assertIn('class="active" href="/orbit"', nav)
        self.assertIn("jarvis-shell", shell)
        self.assertIn("motion-panel-enter", shell)
        self.assertIn("J.A.R.V.I.S. Test", shell)

    def test_status_badge_normalizes_unknown_state_to_ready(self) -> None:
        self.assertIn("state-ready", render_status_badge("Ready for Manual Use", "nonsense"))
        self.assertIn("state-review", render_status_badge("Needs Review", "review"))
        self.assertIn("state-blocked", render_status_badge("Blocked", "blocked"))

    def test_operator_route_works(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = runtime_operator.main(["--premium-orbital-design-system"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V161_0_PREMIUM_ORBITAL_DESIGN_SYSTEM_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
