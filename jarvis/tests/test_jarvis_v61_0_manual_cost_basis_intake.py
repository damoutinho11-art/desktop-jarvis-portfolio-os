from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from jarvis.runtime.manual_cost_basis_intake import (
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_manual_cost_basis_intake_result,
    format_manual_cost_basis_intake,
    main as cost_basis_main,
    write_manual_cost_basis_template,
)


def _write(path: Path, payload: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _confirmed_cost_basis(path: Path) -> Path:
    return _write(
        path,
        {
            "schema": "JARVIS_MANUAL_COST_BASIS_V1",
            "as_of": "2026-06-17",
            "is_template": False,
            "cost_basis_confirmed": True,
            "currency": "EUR",
            "manual_only": True,
            "broker_api_used": False,
            "credentials_used": False,
            "private_account_ingestion_used": False,
            "positions": [
                {
                    "position_id": "btc_lhv_crypto",
                    "asset_name": "Bitcoin",
                    "symbol": "BTC",
                    "platform": "LHV",
                    "lane": "crypto",
                    "current_market_value_eur": 20.12,
                    "total_cost_basis_eur": 18.00,
                    "unrealized_gain_loss_eur": 2.12,
                    "cost_basis_source": "manual_user_entry",
                    "confirmed": True,
                },
                {
                    "position_id": "legacy_lhv_growth_account_combined",
                    "asset_name": "Legacy LHV Growth Account positions",
                    "symbol": "LEGACY_LHV_GROWTH",
                    "platform": "LHV",
                    "lane": "stock_fund_etf",
                    "current_market_value_eur": 1136.18,
                    "total_cost_basis_eur": 1000.00,
                    "unrealized_gain_loss_eur": 136.18,
                    "cost_basis_source": "manual_user_entry",
                    "confirmed": True,
                },
            ],
        },
    )


class JarvisV610ManualCostBasisIntakeTests(unittest.TestCase):
    def test_missing_file_blocks_without_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jarvis" / "local" / "manual_cost_basis.local.json"

            result = build_manual_cost_basis_intake_result(
                current_date="2026-06-17",
                manual_cost_basis_path=path,
            )

            self.assertEqual(result["status"], "JARVIS_V61_0_MANUAL_COST_BASIS_INTAKE_BLOCKED_SAFE")
            self.assertFalse(result["present"])
            self.assertFalse(result["cost_basis_ready_for_full_allocation_data_gate"])
            self.assertIn("manual_cost_basis_file_missing", result["blockers"])
            self.assertFalse(result["allocation_mutation"])
            self.assertFalse(result["approval_ticket_mutation"])
            self.assertFalse(result["portfolio_state_mutation"])
            self.assertFalse(result["buy_request_created"])
            self.assertFalse(result["auto_sell_allowed"])
            self.assertFalse(result["auto_migration_allowed"])
            self.assertTrue(result["broker_connection_forbidden"])
            self.assertTrue(result["credentials_forbidden"])
            self.assertTrue(result["order_creation_forbidden"])
            self.assertTrue(result["no_trades_executed"])

    def test_template_file_is_review_required_not_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jarvis" / "local" / "manual_cost_basis.local.json"
            write_manual_cost_basis_template(path, current_date="2026-06-17")

            result = build_manual_cost_basis_intake_result(
                current_date="2026-06-17",
                manual_cost_basis_path=path,
            )

            self.assertEqual(result["status"], STATUS_REVIEW_REQUIRED)
            self.assertTrue(result["present"])
            self.assertTrue(result["loaded"])
            self.assertTrue(result["template"])
            self.assertFalse(result["confirmed"])
            self.assertFalse(result["cost_basis_ready_for_full_allocation_data_gate"])
            self.assertIn("manual_cost_basis_file_is_template", result["blockers"])

    def test_confirmed_complete_cost_basis_is_ready_and_summarized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _confirmed_cost_basis(Path(tmp) / "jarvis" / "local" / "manual_cost_basis.local.json")

            result = build_manual_cost_basis_intake_result(
                current_date="2026-06-17",
                manual_cost_basis_path=path,
            )

            self.assertEqual(result["status"], STATUS_READY)
            self.assertTrue(result["confirmed"])
            self.assertTrue(result["cost_basis_ready_for_full_allocation_data_gate"])
            self.assertEqual(result["positions_count"], 2)
            self.assertEqual(result["confirmed_positions_count"], 2)
            self.assertEqual(result["missing_or_incomplete_positions"], [])
            self.assertEqual(result["total_market_value_eur"], 1156.30)
            self.assertEqual(result["total_cost_basis_eur"], 1018.00)
            self.assertEqual(result["total_unrealized_gain_loss_eur"], 138.30)
            self.assertEqual(result["blockers"], [])
            self.assertIn("manual cost basis manually confirmed", " ".join(result["warnings"]))

    def test_incomplete_confirmed_position_blocks_ready_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "jarvis" / "local" / "manual_cost_basis.local.json"
            _write(
                path,
                {
                    "schema": "JARVIS_MANUAL_COST_BASIS_V1",
                    "is_template": False,
                    "cost_basis_confirmed": True,
                    "positions": [
                        {
                            "position_id": "missing_cost_basis",
                            "asset_name": "Incomplete position",
                            "symbol": "BAD",
                            "current_market_value_eur": 100.0,
                            "total_cost_basis_eur": None,
                            "confirmed": True,
                        }
                    ],
                },
            )

            result = build_manual_cost_basis_intake_result(
                current_date="2026-06-17",
                manual_cost_basis_path=path,
            )

            self.assertFalse(result["cost_basis_ready_for_full_allocation_data_gate"])
            self.assertIn("manual_cost_basis_positions_incomplete", result["blockers"])
            self.assertIn("missing_cost_basis", result["missing_or_incomplete_positions"])

    def test_format_and_cli_include_safety_language(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = _confirmed_cost_basis(Path(tmp) / "jarvis" / "local" / "manual_cost_basis.local.json")
            result = build_manual_cost_basis_intake_result(
                current_date="2026-06-17",
                manual_cost_basis_path=path,
            )

            text = format_manual_cost_basis_intake(result)

            self.assertIn("J.A.R.V.I.S. MANUAL COST BASIS INTAKE", text)
            self.assertIn("ready for full allocation data gate: True", text)
            self.assertIn("total cost basis EUR: 1018.0", text)
            self.assertIn("- no broker connection", text)
            self.assertIn("- no trades executed", text)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = cost_basis_main(
                    [
                        "--manual-cost-basis-intake",
                        "--current-date",
                        "2026-06-17",
                        "--manual-cost-basis-path",
                        str(path),
                    ]
                )

            self.assertEqual(code, 0)
            self.assertIn("ready for full allocation data gate: True", output.getvalue())


if __name__ == "__main__":
    unittest.main()
