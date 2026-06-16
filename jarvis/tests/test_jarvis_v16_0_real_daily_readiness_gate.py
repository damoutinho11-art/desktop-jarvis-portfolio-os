import json
import tempfile
import unittest
from datetime import date
from pathlib import Path

from jarvis.jarvis_v16_0_real_daily_readiness_gate import (
    READINESS_BLOCKED,
    READINESS_READY,
    READINESS_REVIEW_REQUIRED,
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_real_daily_readiness_console_output,
    build_real_daily_readiness_gate,
)
from jarvis.tests.test_jarvis_v15_0_real_allocation_daily_bridge import _ticket


def _write_json(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _state(as_of: str = "2026-06-04") -> dict:
    return {"as_of": as_of, "holdings": {}, "platform_status": {}}


def _etf_universe() -> dict:
    return {"quality_etf": {"enabled": True}}


class JarvisV160RealDailyReadinessGateTests(unittest.TestCase):
    def test_stale_portfolio_and_ticket_require_review_before_manual_action(self) -> None:
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
            output = build_real_daily_readiness_console_output(result)

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertEqual(result.readiness_status, READINESS_REVIEW_REQUIRED)
        self.assertFalse(result.data_ready_for_manual_review)
        self.assertTrue(result.stale_data_review_required)
        self.assertIn("recommendation trust: refresh_required_before_manual_action", output)
        self.assertIn("portfolio_state: STALE; as_of 2026-06-04; age 13 days", output)
        self.assertIn("approval_ticket_latest: STALE; as_of 2026-06-04; age 13 days", output)
        self.assertIn("best current executable allocation: quality_etf EUR 103.85", output)

    def test_fresh_data_is_ready_for_manual_review_but_still_manual_only(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = _write_json(root / "portfolio_state.json", _state("2026-06-17"))
            ticket = _ticket("growth_nasdaq_etf")
            ticket["as_of"] = "2026-06-17"
            ticket["timestamp"] = "2026-06-17"
            ticket_path = _write_json(root / "outputs" / "approval_ticket_latest.json", ticket)
            etf_path = _write_json(root / "etf_universe.json", {"as_of": "2026-06-17", "quality_etf": {"enabled": True}})

            result = build_real_daily_readiness_gate(
                weekly_result={"approval_ticket": ticket},
                current_date=date(2026, 6, 17),
                portfolio_state_path=state_path,
                approval_ticket_path=ticket_path,
                etf_universe_path=etf_path,
            )
            output = build_real_daily_readiness_console_output(result)

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.readiness_status, READINESS_READY)
        self.assertTrue(result.data_ready_for_manual_review)
        self.assertFalse(result.stale_data_review_required)
        self.assertEqual(result.allocation_result.selected_ideal_sleeve, "growth_nasdaq_etf")
        self.assertIn("selected ideal sleeve: growth_nasdaq_etf", output)
        self.assertIn("no broker connection", output)
        self.assertIn("no orders created", output)
        self.assertIn("no trades executed", output)

    def test_mismatched_saved_ticket_blocks_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = _write_json(root / "portfolio_state.json", _state("2026-06-17"))
            engine_ticket = _ticket("quality_etf")
            engine_ticket["as_of"] = "2026-06-17"
            saved_ticket = dict(engine_ticket)
            saved_ticket["as_of"] = "2026-06-04"
            ticket_path = _write_json(root / "outputs" / "approval_ticket_latest.json", saved_ticket)
            etf_path = _write_json(root / "etf_universe.json", {"as_of": "2026-06-17"})

            result = build_real_daily_readiness_gate(
                weekly_result={"approval_ticket": engine_ticket},
                current_date=date(2026, 6, 17),
                portfolio_state_path=state_path,
                approval_ticket_path=ticket_path,
                etf_universe_path=etf_path,
            )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.readiness_status, READINESS_BLOCKED)
        self.assertTrue(any("does not match" in blocker for blocker in result.blockers))

    def test_invalid_portfolio_date_blocks_readiness(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = _write_json(root / "portfolio_state.json", _state("not-a-date"))
            ticket = _ticket("quality_etf")
            ticket["as_of"] = "2026-06-17"
            ticket_path = _write_json(root / "outputs" / "approval_ticket_latest.json", ticket)
            etf_path = _write_json(root / "etf_universe.json", {"as_of": "2026-06-17"})

            result = build_real_daily_readiness_gate(
                weekly_result={"approval_ticket": ticket},
                current_date=date(2026, 6, 17),
                portfolio_state_path=state_path,
                approval_ticket_path=ticket_path,
                etf_universe_path=etf_path,
            )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("invalid or missing as_of" in blocker for blocker in result.blockers))

    def test_allocation_safety_blockers_flow_through_readiness_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_path = _write_json(root / "portfolio_state.json", _state("2026-06-17"))
            ticket = _ticket("quality_etf", safety_checks=["Manual approval required. No trades executed."])
            ticket["as_of"] = "2026-06-17"
            ticket_path = _write_json(root / "outputs" / "approval_ticket_latest.json", ticket)
            etf_path = _write_json(root / "etf_universe.json", {"as_of": "2026-06-17"})

            result = build_real_daily_readiness_gate(
                weekly_result={"approval_ticket": ticket},
                current_date=date(2026, 6, 17),
                portfolio_state_path=state_path,
                approval_ticket_path=ticket_path,
                etf_universe_path=etf_path,
            )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertTrue(any("broker" in blocker.lower() for blocker in result.blockers))
        self.assertTrue(any("order" in blocker.lower() for blocker in result.blockers))

    def test_current_real_daily_output_flags_stale_data_without_old_demo_candidate(self) -> None:
        result = build_real_daily_readiness_gate(current_date=date(2026, 6, 17))
        output = build_real_daily_readiness_console_output(result)

        self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
        self.assertIn("data readiness: STALE_REVIEW_REQUIRED", output)
        self.assertNotIn("btc_candidate", output)
        self.assertNotIn("crypto_core_btc", output)


if __name__ == "__main__":
    unittest.main()
