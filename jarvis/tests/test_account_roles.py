import unittest

from jarvis.portfolio_snapshot_engine import load_account_roles


class AccountRolesTests(unittest.TestCase):
    def test_required_account_roles(self) -> None:
        roles = load_account_roles()

        self.assertEqual(roles["lhv_crypto_investments"]["role"], "investment_account_crypto")
        self.assertTrue(roles["lhv_crypto_investments"]["further_buying_requires_recommendation_and_approval"])
        self.assertEqual(roles["lhv_growth"]["role"], "legacy_cleanup")
        self.assertEqual(roles["lightyear"]["role"], "ETF_engine")
        self.assertEqual(roles["trade_republic"]["role"], "spending_cash_rewards")
        self.assertEqual(roles["kraken"]["role"], "restricted_crypto_external")

    def test_daily_spending_and_emergency_are_not_investable_by_default(self) -> None:
        roles = load_account_roles()
        self.assertFalse(roles["daily_spending"]["include_in_investable_by_default"])
        self.assertFalse(roles["emergency_fund"]["include_in_investable_by_default"])
        self.assertTrue(roles["emergency_fund"]["protected"])


if __name__ == "__main__":
    unittest.main()

