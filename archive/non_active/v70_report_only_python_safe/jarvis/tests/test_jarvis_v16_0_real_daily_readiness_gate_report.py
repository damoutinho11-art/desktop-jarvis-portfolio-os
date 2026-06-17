import tempfile
import unittest
from datetime import date
from pathlib import Path

from jarvis.jarvis_v16_0_real_daily_readiness_gate import build_real_daily_readiness_gate
from jarvis.jarvis_v16_0_real_daily_readiness_gate_report import (
    build_v16_0_real_daily_readiness_gate_report,
)
from jarvis.tests.test_jarvis_v16_0_real_daily_readiness_gate import _etf_universe, _state, _write_json
from jarvis.tests.test_jarvis_v15_0_real_allocation_daily_bridge import _ticket


class JarvisV160RealDailyReadinessGateReportTests(unittest.TestCase):
    def test_report_contains_readiness_freshness_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = _write_json(root / "portfolio_state.json", _state("2026-06-04"))
            ticket = _ticket("quality_etf")
            ticket_path = _write_json(root / "outputs" / "approval_ticket_latest.json", ticket)
            etf_path = _write_json(root / "etf_universe.json", _etf_universe())

            result = build_real_daily_readiness_gate(
                weekly_result={"approval_ticket": ticket},
                current_date=date(2026, 6, 17),
                portfolio_state_path=state_path,
                approval_ticket_path=ticket_path,
                etf_universe_path=etf_path,
            )
            report = build_v16_0_real_daily_readiness_gate_report(result)

        self.assertIn("J.A.R.V.I.S. v16.0 Real Daily Readiness Gate", report)
        self.assertIn("status: JARVIS_V16_0_REAL_DAILY_READINESS_GATE_REVIEW_REQUIRED_SAFE", report)
        self.assertIn("readiness status: STALE_REVIEW_REQUIRED", report)
        self.assertIn("recommendation trust: refresh_required_before_manual_action", report)
        self.assertIn("portfolio_state: STALE", report)
        self.assertIn("approval_ticket_latest: STALE", report)
        self.assertIn("manual approval required: True", report)
        self.assertIn("broker connection forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()
