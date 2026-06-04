import json
import tempfile
import unittest
from pathlib import Path

from jarvis.contribution_approval_bridge import (
    bridge_contribution_plan,
    build_approval_request_from_plan_line,
    write_approval_requests,
)
from jarvis.contribution_planner import ContributionPlanResult, PlanLine
from jarvis.manual_approval_workflow import validate_approval_request


def _write_registry(asset_type="ETF") -> Path:
    asset = {
        "asset_id": "global_core_etf",
        "name": "Global Core",
        "asset_type": asset_type,
        "sleeve": "global_core",
        "ticker": "global_core_etf",
        "isin_or_symbol": "global_core_etf",
        "platforms": ["Lightyear"],
        "currency": "EUR",
        "domicile": "Ireland",
        "distribution_policy": "accumulating",
        "ter_or_fee": 0.2,
        "data_source": "manual_test",
        "approval_status": "approved_investable",
        "risk_level": "medium",
    }
    if asset_type == "ETF":
        asset.update({"provider": "Provider", "index_tracked": "Index", "replication_method": "physical"})
    if asset_type == "crypto":
        asset.update(
            {
                "network_or_protocol": "Bitcoin",
                "custody_platforms": ["LHV Crypto Investments"],
                "transferable": False,
                "mica_route_possible": True,
            }
        )
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".json", delete=False) as file:
        json.dump({"assets": [asset]}, file)
        return Path(file.name)


def _draft_plan(line: PlanLine | None = None) -> ContributionPlanResult:
    return ContributionPlanResult(
        status="DRAFT_PLAN",
        contribution_amount_eur=100.0,
        plan_lines=(line or PlanLine("global_core", "global_core_etf", "Lightyear", 100.0, "Underweight sleeve."),),
        blockers=(),
        warnings=(),
        manual_approval_required=True,
        creates_buy_request=False,
    )


class ContributionApprovalBridgeTests(unittest.TestCase):
    def test_blocked_contribution_plan_creates_zero_approval_requests(self) -> None:
        blocked = ContributionPlanResult(
            status="BLOCKED",
            contribution_amount_eur=100.0,
            plan_lines=(),
            blockers=("approved universe is empty.",),
            warnings=(),
            manual_approval_required=True,
            creates_buy_request=False,
        )

        result = bridge_contribution_plan(blocked, _write_registry())

        self.assertEqual(result.status, "BLOCKED")
        self.assertEqual(result.approval_requests, ())

    def test_draft_plan_creates_pending_manual_approval_buy_requests(self) -> None:
        result = bridge_contribution_plan(_draft_plan(), _write_registry())

        self.assertEqual(result.status, "PENDING_MANUAL_APPROVAL")
        self.assertEqual(result.approval_requests[0].action_type, "buy")
        self.assertEqual(result.approval_requests[0].status, "pending_manual_approval")

    def test_auto_execute_is_always_false(self) -> None:
        request = bridge_contribution_plan(_draft_plan(), _write_registry()).approval_requests[0]

        self.assertFalse(request.auto_execute)

    def test_manual_approval_required_is_always_true(self) -> None:
        request = bridge_contribution_plan(_draft_plan(), _write_registry()).approval_requests[0]

        self.assertTrue(request.manual_approval_required)

    def test_generated_requests_validate_through_manual_approval_workflow(self) -> None:
        request = bridge_contribution_plan(_draft_plan(), _write_registry()).approval_requests[0]

        self.assertTrue(validate_approval_request(request).valid)

    def test_crypto_plan_line_includes_crypto_confirmations(self) -> None:
        result = bridge_contribution_plan(_draft_plan(), _write_registry("crypto"))
        confirmations = result.approval_requests[0].required_confirmations

        self.assertIn("crypto_tax_risk_acknowledged", confirmations)
        self.assertIn("crypto_volatility_acknowledged", confirmations)

    def test_investment_account_line_includes_tax_confirmation(self) -> None:
        result = bridge_contribution_plan(_draft_plan(), _write_registry(), source_account_id="lightyear")

        self.assertIn("investment_account_tax_rules_acknowledged", result.approval_requests[0].required_confirmations)

    def test_invalid_generated_request_is_blocked(self) -> None:
        invalid_line = PlanLine("global_core", "global_core_etf", "", 100.0, "Missing platform.")

        result = bridge_contribution_plan(_draft_plan(invalid_line), _write_registry())

        self.assertEqual(result.status, "BLOCKED")
        self.assertEqual(result.approval_requests, ())
        self.assertTrue(result.blocked_lines)

    def test_bridge_writes_nothing_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            expected = Path(temp_dir) / "requests.json"
            bridge_contribution_plan(_draft_plan(), _write_registry())

            self.assertFalse(expected.exists())

    def test_optional_writer_writes_when_explicitly_called(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "requests.json"
            result = bridge_contribution_plan(_draft_plan(), _write_registry())

            write_approval_requests(result, target)

            self.assertTrue(target.exists())


if __name__ == "__main__":
    unittest.main()
