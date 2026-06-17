from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from jarvis.runtime import operator as runtime_operator
from jarvis.runtime.monthly_expenses_intake import (
    INTAKE_BLOCKED,
    INTAKE_READY,
    STATUS_BLOCKED,
    STATUS_READY,
    build_monthly_expenses_intake_result,
    build_monthly_expenses_template,
    format_monthly_expenses_intake,
)


def _confirmed_payload() -> dict:
    payload = build_monthly_expenses_template(current_date="2026-06-17")
    payload["is_template"] = False
    payload["expenses_confirmed"] = True
    payload["minimum_emergency_months"] = 3
    payload["ideal_emergency_months"] = 6
    payload["planned_monthly_contribution_eur"] = 400

    for item in payload["expense_categories"]:
        if item["category_id"] == "rent":
            item["monthly_eur"] = 500
        elif item["category_id"] == "utilities":
            item["monthly_eur"] = 120
        elif item["category_id"] == "food_basic":
            item["monthly_eur"] = 280
        elif item["category_id"] == "transport":
            item["monthly_eur"] = 50
        elif item["category_id"] == "phone_internet":
            item["monthly_eur"] = 35
        elif item["category_id"] == "insurance_health":
            item["monthly_eur"] = 40
        elif item["category_id"] == "subscriptions":
            item["monthly_eur"] = 25
        elif item["category_id"] == "restaurants_coffee":
            item["monthly_eur"] = 120
        elif item["category_id"] == "annual_irregular":
            item["monthly_eur"] = 80

    return payload


class JarvisV580MonthlyExpensesIntakeTests(unittest.TestCase):
    def test_missing_expenses_file_blocks_emergency_decision(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "monthly_expenses.local.json"
            result = build_monthly_expenses_intake_result(
                current_date="2026-06-17",
                monthly_expenses_path=path,
            )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertEqual(result.intake_status, INTAKE_BLOCKED)
        self.assertFalse(result.expenses_confirmed)
        self.assertFalse(result.emergency_fund_decision_allowed)
        self.assertFalse(result.monthly_contribution_decision_allowed)
        self.assertIn("missing_monthly_expenses", result.blockers)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.portfolio_state_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertTrue(result.no_trades_executed)

    def test_template_write_is_explicit_and_does_not_confirm_expenses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "monthly_expenses.local.json"
            result = build_monthly_expenses_intake_result(
                current_date="2026-06-17",
                monthly_expenses_path=path,
                write_monthly_expenses_template=True,
            )

            self.assertTrue(path.exists())
            payload = json.loads(path.read_text(encoding="utf-8"))

        self.assertTrue(result.template_written)
        self.assertTrue(result.is_template)
        self.assertTrue(payload["is_template"])
        self.assertFalse(payload["expenses_confirmed"])
        self.assertFalse(result.expenses_confirmed)
        self.assertFalse(result.emergency_fund_decision_allowed)
        self.assertIn("monthly_expenses_template_not_confirmed", result.blockers)

    def test_blank_template_still_blocks_after_written(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "monthly_expenses.local.json"
            path.write_text(json.dumps(build_monthly_expenses_template(current_date="2026-06-17")), encoding="utf-8")

            result = build_monthly_expenses_intake_result(
                current_date="2026-06-17",
                monthly_expenses_path=path,
            )

        self.assertEqual(result.status, STATUS_BLOCKED)
        self.assertFalse(result.expenses_confirmed)
        self.assertFalse(result.emergency_fund_decision_allowed)
        self.assertIn("monthly_expenses_template_not_confirmed", result.blockers)

    def test_confirmed_expenses_compute_survival_normal_flexible_and_emergency_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "monthly_expenses.local.json"
            path.write_text(json.dumps(_confirmed_payload()), encoding="utf-8")

            result = build_monthly_expenses_intake_result(
                current_date="2026-06-17",
                monthly_expenses_path=path,
            )

        self.assertEqual(result.status, STATUS_READY)
        self.assertEqual(result.intake_status, INTAKE_READY)
        self.assertTrue(result.expenses_confirmed)
        self.assertTrue(result.emergency_fund_decision_allowed)
        self.assertTrue(result.monthly_contribution_decision_allowed)
        self.assertEqual(result.survival_monthly_expenses_eur, 950.0)
        self.assertEqual(result.flexible_monthly_expenses_eur, 145.0)
        self.assertEqual(result.normal_monthly_expenses_eur, 1250.0)
        self.assertEqual(result.planned_monthly_contribution_eur, 400.0)
        self.assertEqual(result.minimum_emergency_fund_eur, 2850.0)
        self.assertEqual(result.ideal_emergency_fund_eur, 7500.0)
        self.assertEqual(result.blockers, ())

    def test_credential_like_keys_block_intake_even_if_values_look_confirmed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "monthly_expenses.local.json"
            payload = _confirmed_payload()
            payload["api_key"] = "do-not-store-this"
            path.write_text(json.dumps(payload), encoding="utf-8")

            result = build_monthly_expenses_intake_result(
                current_date="2026-06-17",
                monthly_expenses_path=path,
            )

        self.assertFalse(result.expenses_confirmed)
        self.assertFalse(result.emergency_fund_decision_allowed)
        self.assertIn("monthly_expenses_contains_forbidden_credential_like_keys", result.blockers)
        self.assertIn("api_key", result.forbidden_credential_keys_found)

    def test_format_contains_summary_targets_blockers_and_safety(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "monthly_expenses.local.json"
            path.write_text(json.dumps(_confirmed_payload()), encoding="utf-8")

            result = build_monthly_expenses_intake_result(
                current_date="2026-06-17",
                monthly_expenses_path=path,
            )

        output = format_monthly_expenses_intake(result)
        self.assertIn("J.A.R.V.I.S. MONTHLY EXPENSES INTAKE", output)
        self.assertIn("survival monthly expenses EUR: 950.00", output)
        self.assertIn("normal monthly expenses EUR: 1250.00", output)
        self.assertIn("minimum emergency fund EUR: 2850.0", output)
        self.assertIn("ideal emergency fund EUR: 7500.0", output)
        self.assertIn("emergency fund decision allowed: True", output)
        self.assertIn("no trades executed", output)

    def test_runtime_facade_routes_template_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "monthly_expenses.local.json"
            stdout = io.StringIO()

            with redirect_stdout(stdout):
                exit_code = runtime_operator.main(
                    [
                        "--write-monthly-expenses-template",
                        "--current-date",
                        "2026-06-17",
                        "--monthly-expenses-path",
                        str(path),
                    ]
                )

            self.assertEqual(exit_code, 0)
            self.assertTrue(path.exists())
            self.assertIn("MONTHLY_EXPENSES_TEMPLATE_WRITTEN", stdout.getvalue())
            self.assertIn("expenses confirmed: False", stdout.getvalue())

    def test_runtime_surface_reports_v58_and_monthly_expenses_module(self) -> None:
        surface = runtime_operator.get_active_runtime_surface()

        self.assertIn(surface["active_runtime_stage"], {"v58.0", "v59.0", "v60.0", "v61.0", "v62.0", "v63.0", "v64.0", "v65.0", "v66.0", "v67.0", "v68.0", "v69.0", "v70.0", "v71.0", "v72.0", "v73.0", "v74.0", "v75.0", "v76.0", "v77.0", "v78.0", "v79.0", "v80.0", "v81.0", "v82.0", "v83.0", "v84.0", "v85.0", "v86.0"})
        self.assertIn(surface["current_operator_surface"], {"monthly_expenses_intake", "personal_finance_contribution_bridge", "manual_cost_basis_intake", "manual_cost_basis_bridge", "active_runtime_surface_redundancy_audit", "import_closure_safe_archive_plan", "stable_runtime_safety_facade", "import_closure_precision_hotfix", "import_closure_relative_import_precision", "non_active_archive_candidate_report", "reversible_archive_staging_plan", "reversible_report_archive_execution", "remaining_python_archive_risk_audit", "next_safe_python_archive_execution_plan", "next_safe_python_archive_execution", "validation_blocked_legacy_candidate_decoupling_audit", "validation_blocked_v5_replacement_plan", "active_runtime_v5_replacement_coverage", "final_v5_archive_execution_plan", "final_v5_archive_execution", "product_mode_operator", "product_output_quality", "correlation_risk_model", "stock_specific_public_evidence", "data_freshness_acquisition_gate", "tradable_candidate_universe_gate", "stock_candidate_universe_expansion", "cross_lane_dynamic_allocation_preflight"})
        self.assertEqual(
            surface["active_monthly_expenses_intake_module"],
            "jarvis.runtime.monthly_expenses_intake",
        )
        self.assertTrue(surface["execution_forbidden"])
        self.assertTrue(surface["manual_approval_required"])


if __name__ == "__main__":
    unittest.main()
