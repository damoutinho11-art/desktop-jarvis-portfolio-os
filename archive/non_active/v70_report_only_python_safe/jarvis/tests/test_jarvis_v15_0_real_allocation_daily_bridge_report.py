import unittest

from jarvis.jarvis_v15_0_real_allocation_daily_bridge import build_real_allocation_daily_bridge
from jarvis.jarvis_v15_0_real_allocation_daily_bridge_report import (
    build_v15_0_real_allocation_daily_bridge_report,
)
from jarvis.tests.test_jarvis_v15_0_real_allocation_daily_bridge import _ticket


class JarvisV150RealAllocationDailyBridgeReportTests(unittest.TestCase):
    def test_report_contains_real_allocation_and_safety(self) -> None:
        result = build_real_allocation_daily_bridge(
            weekly_result={"approval_ticket": _ticket("growth_nasdaq_etf")}
        )
        report = build_v15_0_real_allocation_daily_bridge_report(result)

        self.assertIn("J.A.R.V.I.S. v15.0 Real Allocation Daily Bridge", report)
        self.assertIn("status: JARVIS_V15_0_REAL_ALLOCATION_DAILY_BRIDGE_READY_SAFE", report)
        self.assertIn("real allocation engine used: False", report)
        self.assertIn("selected ideal sleeve: growth_nasdaq_etf", report)
        self.assertIn("broker connection forbidden: True", report)
        self.assertIn("no trades executed: True", report)


if __name__ == "__main__":
    unittest.main()

