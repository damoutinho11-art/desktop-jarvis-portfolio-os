import unittest

from jarvis.portfolio_snapshot_engine import load_constitution


class ConstitutionTests(unittest.TestCase):
    def test_safety_rules_are_present(self) -> None:
        constitution = load_constitution()
        rules = constitution["safety_rules"]

        self.assertTrue(rules["manual_approval_required"])
        self.assertTrue(rules["no_live_trading"])
        self.assertTrue(rules["no_api_credentials"])
        self.assertTrue(rules["no_broker_execution"])
        self.assertTrue(rules["protect_emergency_fund"])
        self.assertTrue(rules["recommendations_require_valid_snapshot"])

    def test_unknown_assets_are_not_preapproved(self) -> None:
        constitution = load_constitution()
        self.assertNotIn("RANDOM_NEW_ASSET", constitution["approved_assets"])


if __name__ == "__main__":
    unittest.main()

