from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.allocation_strategy_audit import build_allocation_strategy_data_coverage_audit_result
from jarvis.runtime.manual_portfolio_snapshot import (
    STATUS_BLOCKED,
    STATUS_READY,
    STATUS_REVIEW_REQUIRED,
    build_manual_portfolio_snapshot_intake_result,
    build_manual_portfolio_snapshot_template,
    format_manual_portfolio_snapshot_intake,
    _find_forbidden_keys,
)


class JarvisV520ManualPortfolioSnapshotIntakeTests(unittest.TestCase):
    def test_template_is_brokerless_and_contains_no_credentials(self) -> None:
        template = build_manual_portfolio_snapshot_template(current_date="2026-06-17")
        self.assertEqual(template["schema"], "JARVIS_MANUAL_PORTFOLIO_SNAPSHOT_V1")
        self.assertTrue(template["brokerless_manual_snapshot"])
        self.assertTrue(template["is_template"])
        self.assertEqual(_find_forbidden_keys(template), ())
        self.assertIn("holdings", template)
        self.assertIn("cash_eur", template)
        self.assertIn("cost_basis", template)

    def test_missing_snapshot_is_review_required_not_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            result = build_manual_portfolio_snapshot_intake_result(
                current_date="2026-06-17",
                snapshot_path=path,
                enforce_local_path=False,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertFalse(result.snapshot_present)
            self.assertFalse(result.valid_for_allocation_data_gate)
            self.assertFalse(result.buy_request_created)
            self.assertTrue(result.no_trades_executed)

    def test_write_template_creates_local_review_required_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            result = build_manual_portfolio_snapshot_intake_result(
                current_date="2026-06-17",
                snapshot_path=path,
                write_template=True,
                enforce_local_path=False,
            )

            self.assertEqual(result.status, STATUS_REVIEW_REQUIRED)
            self.assertTrue(result.template_written)
            self.assertTrue(path.exists())
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertTrue(payload["is_template"])
            self.assertTrue(payload["brokerless_manual_snapshot"])

    def test_valid_manual_snapshot_is_ready_for_data_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            path.write_text(
                json.dumps(
                    {
                        "schema": "JARVIS_MANUAL_PORTFOLIO_SNAPSHOT_V1",
                        "snapshot_date": "2026-06-17",
                        "is_template": False,
                        "brokerless_manual_snapshot": True,
                        "cash_eur": 250.0,
                        "holdings": [
                            {
                                "lane": "stock_fund_etf",
                                "symbol": "IS3Q.DE",
                                "quantity": 1.0,
                                "market_value_eur": 75.0,
                                "cost_basis_eur": 70.0,
                            }
                        ],
                        "cost_basis": {"IS3Q.DE": 70.0},
                    }
                ),
                encoding="utf-8",
            )

            result = build_manual_portfolio_snapshot_intake_result(
                current_date="2026-06-17",
                snapshot_path=path,
                enforce_local_path=False,
            )

            self.assertEqual(result.status, STATUS_READY)
            self.assertTrue(result.valid_for_allocation_data_gate)
            self.assertEqual(result.holdings_count, 1)
            self.assertEqual(result.cash_eur, 250.0)
            self.assertFalse(result.approval_ticket_mutation)

    def test_credential_like_keys_block_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            path.write_text(
                json.dumps(
                    {
                        "is_template": False,
                        "brokerless_manual_snapshot": True,
                        "cash_eur": 10.0,
                        "holdings": [{"symbol": "IS3Q.DE"}],
                        "cost_basis": {"IS3Q.DE": 1.0},
                        "api_key": "do-not-store-this",
                    }
                ),
                encoding="utf-8",
            )

            result = build_manual_portfolio_snapshot_intake_result(
                current_date="2026-06-17",
                snapshot_path=path,
                enforce_local_path=False,
            )

            self.assertEqual(result.status, STATUS_BLOCKED)
            self.assertIn("api_key", result.forbidden_credential_keys_found)

    def test_format_mentions_manual_local_policy_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing.json"
            result = build_manual_portfolio_snapshot_intake_result(
                current_date="2026-06-17",
                snapshot_path=path,
                enforce_local_path=False,
            )
            output = format_manual_portfolio_snapshot_intake(result)

            self.assertIn("J.A.R.V.I.S. MANUAL PORTFOLIO SNAPSHOT INTAKE", output)
            self.assertIn("local JSON file only", output)
            self.assertIn("no broker connection", output)
            self.assertIn("no trades executed", output)

    def test_runtime_facade_routes_template_command(self) -> None:
        path = Path("jarvis/local/manual_portfolio_snapshot_intake_test.local.json")
        try:
            if path.exists():
                path.unlink()
            buffer = io.StringIO()
            with redirect_stdout(buffer):
                code = runtime_operator.main(
                    [
                        "--write-manual-portfolio-snapshot-template",
                        "--manual-portfolio-snapshot-path",
                        str(path),
                        "--current-date",
                        "2026-06-17",
                    ]
                )

            output = buffer.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("MANUAL PORTFOLIO SNAPSHOT INTAKE", output)
            self.assertTrue(path.exists())
        finally:
            if path.exists():
                path.unlink()

    def test_runtime_surface_keeps_snapshot_module_after_later_stages(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        self.assertIn("active_runtime_stage", surface)
        self.assertEqual(
            surface["active_manual_portfolio_snapshot_module"],
            "jarvis.runtime.manual_portfolio_snapshot",
        )

    def test_template_snapshot_does_not_improve_allocation_audit_manual_data_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            path.write_text(
                json.dumps(build_manual_portfolio_snapshot_template(current_date="2026-06-17")),
                encoding="utf-8",
            )

            audit = build_allocation_strategy_data_coverage_audit_result(
                current_date="2026-06-17",
                manual_portfolio_snapshot_path=path,
                upstream_result=type(
                    "Upstream",
                    (),
                    {
                        "status": "JARVIS_V45_0_FREE_RESEARCH_CACHE_EVIDENCE_PACK_BRIDGE_READY_SAFE",
                        "source_confidence_score": 70,
                        "source_confidence_grade": "MEDIUM_HIGH_FREE_STACK",
                        "free_stack_sufficient_for_weekly_investing": True,
                        "paid_api_required_now": False,
                        "broker_api_required_now": False,
                        "evidence_items": (),
                        "approval_ticket_mutation": False,
                        "blockers": (),
                        "warnings": (),
                    },
                )(),
            
                manual_cost_basis_path=Path("jarvis/local/__test_missing_manual_cost_basis.local.json"),)

            covered = {item.key for item in audit.coverage_items if item.available}
            self.assertNotIn("manual_holdings_snapshot", covered)
            self.assertNotIn("manual_cash_snapshot", covered)
            self.assertNotIn("manual_cost_basis", covered)
            self.assertNotIn("brokerless_manual_snapshot_policy", covered)
            self.assertIn("manual_holdings_snapshot", audit.missing_full_allocation_required_keys)
    def test_snapshot_improves_allocation_audit_manual_data_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manual_portfolio_snapshot.local.json"
            path.write_text(
                json.dumps(
                    {
                        "schema": "JARVIS_MANUAL_PORTFOLIO_SNAPSHOT_V1",
                        "snapshot_date": "2026-06-17",
                        "is_template": False,
                        "brokerless_manual_snapshot": True,
                        "cash_eur": 250.0,
                        "holdings": [{"lane": "stock_fund_etf", "symbol": "IS3Q.DE", "market_value_eur": 75.0}],
                        "cost_basis": {"IS3Q.DE": 70.0},
                    }
                ),
                encoding="utf-8",
            )

            audit = build_allocation_strategy_data_coverage_audit_result(
                current_date="2026-06-17",
                manual_portfolio_snapshot_path=path,
                upstream_result=type(
                    "Upstream",
                    (),
                    {
                        "status": "JARVIS_V45_0_FREE_RESEARCH_CACHE_EVIDENCE_PACK_BRIDGE_READY_SAFE",
                        "source_confidence_score": 70,
                        "source_confidence_grade": "MEDIUM_HIGH_FREE_STACK",
                        "free_stack_sufficient_for_weekly_investing": True,
                        "paid_api_required_now": False,
                        "broker_api_required_now": False,
                        "evidence_items": (),
                        "approval_ticket_mutation": False,
                        "blockers": (),
                        "warnings": (),
                    },
                )(),
            
                manual_cost_basis_path=Path("jarvis/local/__test_missing_manual_cost_basis.local.json"),)

            covered = {item.key for item in audit.coverage_items if item.available}
            self.assertIn("manual_holdings_snapshot", covered)
            self.assertIn("manual_cash_snapshot", covered)
            self.assertIn("manual_cost_basis", covered)
            self.assertIn("brokerless_manual_snapshot_policy", covered)


if __name__ == "__main__":
    unittest.main()