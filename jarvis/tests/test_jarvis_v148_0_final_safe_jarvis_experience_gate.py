from __future__ import annotations

import contextlib
import io
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.final_safe_jarvis_experience_gate import (
    FINAL_VERDICT_READY,
    STATUS_READY,
    build_final_safe_jarvis_experience_gate_result,
    format_final_safe_jarvis_experience_gate,
)


def _ns(**kwargs):
    return SimpleNamespace(**kwargs)


class JarvisV148FinalSafeExperienceGateTests(unittest.TestCase):
    def _patch_ready(self):
        return (
            patch(
                "jarvis.runtime.final_safe_jarvis_experience_gate.build_product_api_result",
                return_value=_ns(
                    status="JARVIS_V96_0_PRODUCT_API_LAYER_READY_SAFE",
                    api_ready=True,
                    warnings=[],
                    to_dict=lambda: {
                        "status": "JARVIS_V96_0_PRODUCT_API_LAYER_READY_SAFE",
                        "api_ready": True,
                        "warnings": [],
                    },
                ),
            ),
            patch(
                "jarvis.runtime.final_safe_jarvis_experience_gate.build_dashboard_noise_audit_result",
                return_value=_ns(status="JARVIS_V139_0_DASHBOARD_NOISE_AUDIT_READY_SAFE", dashboard_noise_audit_ready=True, warnings=[]),
            ),
            patch(
                "jarvis.runtime.final_safe_jarvis_experience_gate.build_dashboard_calm_ui_freeze_gate_result",
                return_value=_ns(status="JARVIS_V141_0_FINAL_CALM_UI_FREEZE_GATE_READY_SAFE", calm_ui_freeze_gate_ready=True, warnings=[]),
            ),
            patch(
                "jarvis.runtime.final_safe_jarvis_experience_gate.build_jarvis_session_memory_result",
                return_value=_ns(status="JARVIS_V142_0_JARVIS_SESSION_MEMORY_READY_SAFE", session_memory_ready=True, warnings=[]),
            ),
            patch(
                "jarvis.runtime.final_safe_jarvis_experience_gate.build_voice_briefing_result",
                return_value=_ns(status="JARVIS_V143_0_VOICE_DAILY_BRIEFING_SHELL_READY_SAFE", voice_briefing_ready=True, text="Good evening, Diogo.", warnings=[]),
            ),
            patch(
                "jarvis.runtime.final_safe_jarvis_experience_gate._news_ticker_ready_or_optional",
                return_value=(True, {"missing": [], "forbidden_found": []}),
            ),
            patch(
                "jarvis.runtime.final_safe_jarvis_experience_gate.build_assistant_router_result",
                side_effect=[
                    _ns(
                        status="JARVIS_V113_0_ASSISTANT_ROUTER_READY_SAFE",
                        intent="today_plan",
                        reply="Good evening, Diogo. Manual-only safety is active.",
                        execution_refused=False,
                        order_created=False,
                        trade_executed=False,
                    ),
                    _ns(
                        status="JARVIS_V113_0_ASSISTANT_ROUTER_REFUSED_SAFE",
                        intent="safety",
                        reply="Request refused safely.",
                        execution_refused=True,
                        order_created=False,
                        trade_executed=False,
                    ),
                ],
            ),
            patch(
                "jarvis.runtime.final_safe_jarvis_experience_gate.build_safe_session_snapshot",
                return_value={"dashboard_ready_label": "READY FOR MANUAL USE"},
            ),
            patch(
                "jarvis.runtime.final_safe_jarvis_experience_gate.build_what_changed_since_last_time_result",
                return_value=_ns(status="JARVIS_V146_0_WHAT_CHANGED_SINCE_LAST_TIME_READY_SAFE", what_changed_ready=True, warnings=[]),
            ),
            patch(
                "jarvis.runtime.final_safe_jarvis_experience_gate.build_local_app_packaging_polish_result",
                return_value=_ns(status="JARVIS_V147_0_LOCAL_APP_PACKAGING_POLISH_READY_SAFE", local_app_packaging_ready=True, warnings=[]),
            ),
            patch(
                "jarvis.runtime.final_safe_jarvis_experience_gate.build_safety_check_console_output",
                return_value="BLOCKED: dry run. No execution action was taken.",
            ),
        )

    def test_final_gate_ready_for_safe_daily_use(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            result = build_final_safe_jarvis_experience_gate_result(current_date="2026-06-20")

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.final_verdict, FINAL_VERDICT_READY)
        self.assertTrue(result.final_safe_jarvis_experience_ready)
        self.assertTrue(result.product_api_ready)
        self.assertTrue(result.chat_personality_ready)
        self.assertTrue(result.local_app_packaging_ready)
        self.assertEqual(result.blockers, [])

    def test_format_lists_final_verdict_and_safety_assertions(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            text = format_final_safe_jarvis_experience_gate(
                build_final_safe_jarvis_experience_gate_result(current_date="2026-06-20")
            )

        self.assertIn("J.A.R.V.I.S. FINAL SAFE JARVIS EXPERIENCE GATE", text)
        self.assertIn("final verdict: READY_FOR_SAFE_DAILY_USE", text)
        self.assertIn("manual_only: True", text)
        self.assertIn("broker_connection_enabled: False", text)
        self.assertIn("approval_mutation: False", text)

    def test_safety_failure_blocks_final_gate(self) -> None:
        patches = list(self._patch_ready())
        patches[-1] = patch(
            "jarvis.runtime.final_safe_jarvis_experience_gate.build_safety_check_console_output",
            return_value="NOT BLOCKED",
        )
        with contextlib.ExitStack() as stack:
            for item in patches:
                stack.enter_context(item)
            result = build_final_safe_jarvis_experience_gate_result(current_date="2026-06-20")

        self.assertFalse(result.final_safe_jarvis_experience_ready)
        self.assertIn("safety_check_did_not_block_execution", result.blockers)

    def test_operator_routes_final_gate(self) -> None:
        with contextlib.ExitStack() as stack:
            for item in self._patch_ready():
                stack.enter_context(item)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = runtime_operator.main(["--final-safe-jarvis-experience-gate", "--current-date", "2026-06-20"])

        self.assertEqual(code, 0)
        self.assertIn("JARVIS_V148_0_FINAL_SAFE_JARVIS_EXPERIENCE_GATE_READY_SAFE", output.getvalue())


if __name__ == "__main__":
    unittest.main()
