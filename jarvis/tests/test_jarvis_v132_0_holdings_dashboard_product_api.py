from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from jarvis.runtime.daily_operator import build_daily_operator_result, format_daily_operator
from jarvis.runtime.dashboard_contract import build_dashboard_contract_result, render_dashboard_html
from jarvis.runtime.manual_holdings_update import MANUAL_SOURCE
from jarvis.runtime.product_api import build_product_api_result, format_product_api


def _write(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _valid_holdings_payload() -> dict:
    return {
        "schema": "JARVIS_MANUAL_HOLDINGS_V1",
        "as_of": "2026-06-20",
        "is_template": False,
        "manual_only": True,
        "source": MANUAL_SOURCE,
        "holdings_confirmed": True,
        "currency": "EUR",
        "positions": [
            {
                "symbol": "BTC",
                "name": "Bitcoin",
                "lane": "crypto",
                "quantity": 0.01,
                "average_price_eur": 60000.0,
                "cost_basis_eur": 600.0,
                "market_value_eur": 650.0,
                "platform": "Kraken",
                "purchase_date": "2026-06-20",
                "notes": "manual buy outside Jarvis",
            },
            {
                "symbol": "MSFT",
                "name": "Microsoft",
                "lane": "individual_stock",
                "quantity": 1.0,
                "average_price_eur": 420.0,
                "cost_basis_eur": 420.0,
                "market_value_eur": 430.0,
                "platform": "Lightyear",
                "purchase_date": "2026-06-20",
                "notes": "",
            },
        ],
    }


class JarvisV132HoldingsDashboardProductApiTests(unittest.TestCase):
    def test_product_api_exposes_missing_holdings_as_warning_not_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_holdings.local.json"

            result = build_product_api_result(
                current_date="2026-06-20",
                manual_holdings_path=path,
            )
            data = result.to_dict()

            self.assertTrue(result.api_ready)
            self.assertEqual(data["manual_holdings"]["status"], "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_REVIEW_REQUIRED_SAFE")
            self.assertFalse(data["manual_holdings"]["holdings_ready"])
            self.assertFalse(data["manual_holdings"]["file_exists"])
            self.assertEqual(data["manual_holdings"]["positions_count"], 0)
            self.assertFalse(any("manual_holdings" in blocker for blocker in result.blockers))
            self.assertIn("manual holdings not ready", " ".join(result.warnings))

            text = format_product_api(result)
            self.assertIn("MANUAL HOLDINGS:", text)
            self.assertIn("holdings not entered yet", text)

    def test_product_api_exposes_confirmed_holdings_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp) / "manual_holdings.local.json", _valid_holdings_payload())

            result = build_product_api_result(
                current_date="2026-06-20",
                manual_holdings_path=path,
            )
            holdings = result.manual_holdings

            self.assertTrue(result.api_ready)
            self.assertTrue(holdings["holdings_ready"])
            self.assertEqual(holdings["positions_count"], 2)
            self.assertEqual(holdings["confirmed_positions_count"], 2)
            self.assertEqual(holdings["total_cost_basis_eur"], 1020.0)
            self.assertEqual(holdings["total_market_value_eur"], 1080.0)
            self.assertFalse(holdings["safety_flags"]["order_created"])
            self.assertFalse(holdings["safety_flags"]["trade_executed"])

    def test_dashboard_shows_missing_holdings_without_failing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_holdings.local.json"

            result = build_dashboard_contract_result(
                current_date="2026-06-20",
                manual_holdings_path=path,
            )
            holdings = result.sections["manual_holdings"]
            html = render_dashboard_html(result)

            self.assertTrue(result.dashboard_contract_ready)
            self.assertFalse(holdings["file_exists"])
            self.assertFalse(holdings["holdings_ready"])
            self.assertIn("Manual Holdings", html)
            self.assertIn("holdings not entered yet", html)
            self.assertNotIn("dashboard_backend_not_ready", result.blockers)

    def test_dashboard_shows_confirmed_holdings_rows_and_totals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _write(Path(tmp) / "manual_holdings.local.json", _valid_holdings_payload())

            result = build_dashboard_contract_result(
                current_date="2026-06-20",
                manual_holdings_path=path,
            )
            holdings = result.sections["manual_holdings"]
            html = render_dashboard_html(result)

            self.assertTrue(result.dashboard_contract_ready)
            self.assertTrue(holdings["holdings_ready"])
            self.assertEqual(holdings["confirmed_positions_count"], 2)
            self.assertIn("Manual Holdings", html)
            self.assertIn("BTC", html)
            self.assertIn("MSFT", html)
            self.assertIn("EUR 1020.00", html)
            self.assertIn("EUR 1080.00", html)

    def test_daily_operator_includes_holdings_status_as_review_note(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_holdings.local.json"
            holdings_section = {
                "status": "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_REVIEW_REQUIRED_SAFE",
                "holdings_ready": False,
                "file_exists": False,
            }
            dashboard_payload = {
                "status": "JARVIS_V127_0_DASHBOARD_UX_FINAL_POLISH_READY_SAFE",
                "sections": {"manual_holdings": holdings_section},
            }
            final_gate = SimpleNamespace(
                final_acceptance_ready=True,
                status="JARVIS_V128_0_FINAL_PRODUCT_ACCEPTANCE_GATE_READY_SAFE",
                blockers=[],
                warnings=[],
            )
            product = SimpleNamespace(
                status="JARVIS_PRODUCT_MODE_READY_SAFE",
                blockers=[],
                warnings=[],
            )

            with (
                patch("jarvis.runtime.daily_operator._build_dashboard", return_value=(False, "outputs/dashboard_latest.html", dashboard_payload)),
                patch("jarvis.runtime.daily_operator.build_final_product_acceptance_gate_result", return_value=final_gate),
                patch("jarvis.runtime.daily_operator.build_product_mode_result", return_value=product),
                patch(
                    "jarvis.runtime.daily_operator.build_safety_check_console_output",
                    return_value="BLOCKED: dry run. No execution action was taken.",
                ),
            ):
                result = build_daily_operator_result(
                    current_date="2026-06-20",
                    refresh_quotes=False,
                    write_dashboard=False,
                    manual_holdings_path=path,
                )
            text = format_daily_operator(result)

            self.assertTrue(result.daily_operator_ready)
            self.assertEqual(result.blockers, [])
            self.assertEqual(
                result.proof["holdings_status"],
                "JARVIS_V131_0_MANUAL_HOLDINGS_UPDATE_REVIEW_REQUIRED_SAFE",
            )
            self.assertFalse(result.proof["holdings_ready"])
            self.assertFalse(result.proof["holdings_file_exists"])
            self.assertIn("holdings ready: False", text)
            self.assertIn("manual holdings file missing", " ".join(result.warnings))

    def test_blocked_holdings_file_blocks_product_api_for_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = _valid_holdings_payload()
            payload["manual_only"] = False
            payload["source"] = "broker_import"
            path = _write(Path(tmp) / "manual_holdings.local.json", payload)

            result = build_product_api_result(
                current_date="2026-06-20",
                manual_holdings_path=path,
            )

            self.assertFalse(result.api_ready)
            self.assertIn("manual_holdings_status_blocked", result.blockers)
            self.assertFalse(result.manual_holdings["safety_flags"]["trade_executed"])


if __name__ == "__main__":
    unittest.main()
