from __future__ import annotations

import unittest

from jarvis.runtime.local_server import render_chat_page


class JarvisV1520AnimatedJarvisOrbTests(unittest.TestCase):
    def test_chat_page_includes_animated_orb_states(self) -> None:
        html = render_chat_page()

        self.assertIn("id=\"jarvisOrb\"", html)
        self.assertIn("class=\"jarvis-orb state-idle\"", html)
        self.assertIn("state-listening", html)
        self.assertIn("state-thinking", html)
        self.assertIn("state-speaking", html)
        self.assertIn("@keyframes orbPulse", html)
        self.assertIn("@keyframes orbRing", html)
        self.assertIn("function setOrbState(state)", html)

    def test_orb_state_is_visual_only(self) -> None:
        html = render_chat_page()

        self.assertIn('const allowed = ["idle", "listening", "thinking", "speaking"]', html)
        self.assertIn('jarvisOrb.className = "jarvis-orb state-" + nextState', html)
        self.assertNotIn("createOrder", html)
        self.assertNotIn("executeTrade", html)
        self.assertNotIn("brokerLogin", html)
        self.assertNotIn("autoApproval", html)


if __name__ == "__main__":
    unittest.main()
