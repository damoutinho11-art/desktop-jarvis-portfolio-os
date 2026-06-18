from __future__ import annotations

import unittest

from jarvis.runtime.multi_candidate_instrument_selector import (
    STATUS_READY,
    _select_crypto,
    _select_etf_fund,
    _select_stock,
    build_multi_candidate_instrument_selector_result,
    format_multi_candidate_instrument_selector,
)


class JarvisV910MultiCandidateInstrumentSelectorTests(unittest.TestCase):
    def test_selector_is_ready_and_uses_v90_lane_amounts(self) -> None:
        result = build_multi_candidate_instrument_selector_result(current_date="2026-06-18")

        self.assertEqual(result.status, STATUS_READY)
        self.assertTrue(result.selector_ready)
        self.assertEqual(result.monthly_contribution_eur, 500.0)
        self.assertEqual(result.emergency_top_up_eur, 75.0)
        self.assertEqual(result.crypto_lane_eur, 100.0)
        self.assertEqual(result.etf_fund_lane_eur, 275.0)
        self.assertEqual(result.individual_stock_lane_eur, 50.0)
        self.assertEqual(result.blockers, [])

    def test_current_monthly_plan_is_practical_not_over_fragmented(self) -> None:
        result = build_multi_candidate_instrument_selector_result(current_date="2026-06-18")

        crypto = [item for item in result.selections if item.lane == "crypto"]
        etf_fund = [item for item in result.selections if item.lane == "etf_fund"]
        stocks = [item for item in result.selections if item.lane == "individual_stock"]

        self.assertEqual([item.symbol for item in crypto], ["BTC", "ETH"])
        self.assertEqual([item.amount_eur for item in crypto], [60.0, 40.0])

        self.assertEqual(len(etf_fund), 2)
        self.assertEqual(etf_fund[0].amount_eur, 220.0)
        self.assertEqual(etf_fund[1].amount_eur, 55.0)

        self.assertEqual(len(stocks), 1)
        self.assertEqual(stocks[0].symbol, "MSFT")
        self.assertEqual(stocks[0].amount_eur, 50.0)

    def test_lane_totals_match_allocator_amounts(self) -> None:
        result = build_multi_candidate_instrument_selector_result(current_date="2026-06-18")

        self.assertEqual(result.lane_totals["crypto"], result.crypto_lane_eur)
        self.assertEqual(result.lane_totals["etf_fund"], result.etf_fund_lane_eur)
        self.assertEqual(result.lane_totals["individual_stock"], result.individual_stock_lane_eur)
        self.assertEqual(
            round(
                result.emergency_top_up_eur
                + result.lane_totals["crypto"]
                + result.lane_totals["etf_fund"]
                + result.lane_totals["individual_stock"],
                2,
            ),
            result.monthly_contribution_eur,
        )

    def test_selector_can_choose_more_than_four_crypto_candidates_when_amount_supports_it(self) -> None:
        selections, blockers = _select_crypto(
            amount=1000.0,
            candidates=["BTC", "ETH", "SOL", "LINK", "HYPE", "AVAX", "NEAR", "INJ", "RENDER", "TAO"],
            current_date="2026-06-18",
        )

        self.assertEqual(blockers, [])
        self.assertGreater(len(selections), 4)
        self.assertEqual(round(sum(item.amount_eur for item in selections), 2), 1000.0)
        self.assertGreaterEqual(min(item.amount_eur for item in selections), 25.0)

    def test_selector_can_choose_more_than_four_etf_candidates_when_amount_supports_it(self) -> None:
        selections, blockers = _select_etf_fund(
            amount=2000.0,
            candidates=[
                "GLOBAL_CORE_ETF",
                "VWCE",
                "SXR8",
                "QUALITY_ETF",
                "IS3Q.DE",
                "QDVE",
                "GROWTH_NASDAQ_ETF",
                "TECHNOLOGY_TILT_ETF",
            ],
            current_date="2026-06-18",
        )

        self.assertEqual(blockers, [])
        self.assertGreater(len(selections), 4)
        self.assertEqual(round(sum(item.amount_eur for item in selections), 2), 2000.0)
        self.assertGreaterEqual(min(item.amount_eur for item in selections), 50.0)

    def test_stock_selector_splits_only_when_practical(self) -> None:
        small_selections, small_blockers = _select_stock(
            amount=50.0,
            candidates=["MSFT", "META", "AAPL"],
            stock_evidence={
                "top_stock_symbol": "MSFT",
                "top_stock_name": "Microsoft Corporation",
                "public_as_of": "2026-06-17",
            },
        )
        larger_selections, larger_blockers = _select_stock(
            amount=500.0,
            candidates=["MSFT", "META", "AAPL", "NVDA", "GOOGL", "AMZN"],
            stock_evidence={
                "top_stock_symbol": "MSFT",
                "top_stock_name": "Microsoft Corporation",
                "public_as_of": "2026-06-17",
            },
        )

        self.assertEqual(small_blockers, [])
        self.assertEqual(larger_blockers, [])
        self.assertEqual(len(small_selections), 1)
        self.assertGreater(len(larger_selections), 1)
        self.assertEqual(round(sum(item.amount_eur for item in larger_selections), 2), 500.0)
        self.assertGreaterEqual(min(item.amount_eur for item in larger_selections), 45.0)

    def test_safety_flags_remain_manual_only(self) -> None:
        result = build_multi_candidate_instrument_selector_result(current_date="2026-06-18")

        self.assertTrue(result.manual_approval_required)
        self.assertTrue(result.safety_check_blocked_execution)
        self.assertFalse(result.approved_for_purchase)
        self.assertFalse(result.allocation_mutation)
        self.assertFalse(result.approval_ticket_mutation)
        self.assertFalse(result.buy_request_created)
        self.assertFalse(result.broker_connection)
        self.assertFalse(result.credentials_used)
        self.assertFalse(result.order_created)
        self.assertFalse(result.trade_executed)

    def test_formatter_shows_clean_manual_recommendation(self) -> None:
        result = build_multi_candidate_instrument_selector_result(current_date="2026-06-18")
        text = format_multi_candidate_instrument_selector(result)

        self.assertIn("J.A.R.V.I.S. MULTI-CANDIDATE INSTRUMENT SELECTOR", text)
        self.assertIn("BTC / Bitcoin -> EUR 60.00", text)
        self.assertIn("ETH / Ethereum -> EUR 40.00", text)
        self.assertIn("MSFT / Microsoft Corporation -> EUR 50.00", text)
        self.assertIn("manual approval required: True", text)
        self.assertIn("trade executed: False", text)


if __name__ == "__main__":
    unittest.main()
