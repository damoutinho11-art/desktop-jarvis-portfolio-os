import unittest

import jarvis.runtime.chat_interface_contract as chat
from jarvis.runtime.finance_intelligence_core import answer_finance_intelligence_question


class TestJarvisV121QuoteCacheIntegrationAssistantBrainRouting(unittest.TestCase):
    def test_chat_answers_trust_and_today_questions_from_finance_intelligence(self):
        today = chat.build_chat_interface_contract_result(
            query="What happened today?",
            current_date="2026-06-20",
        ).response
        self.assertIn("Today's locally cached market movement", today)
        self.assertIn("GLOBAL_CORE_ETF", today)
        self.assertIn("VWCE", today)
        self.assertNotIn("I can answer: what is today", today)

        trust = chat.build_chat_interface_contract_result(
            query="Can I trust my ETF data?",
            current_date="2026-06-20",
        ).response
        self.assertIn("ETF/fund data trust", trust)
        self.assertIn("GLOBAL_CORE_ETF", trust)
        self.assertIn("VWCE", trust)
        self.assertNotIn("I can answer: what is today", trust)

    def test_vwce_answer_uses_normalized_finance_cache_not_stale_resolver_text(self):
        answer = answer_finance_intelligence_question("Tell me about VWCE", current_date="2026-06-20")
        self.assertIn("VWCE", answer)
        self.assertIn("Data / Source / Freshness", answer)
        self.assertIn("final real-world buy manually", answer)
        self.assertNotIn("no local quote/source/freshness record exists", answer)
        self.assertNotIn("Add VWCE to the ETF public source manifest", answer)

    def test_etf_trust_answer_exposes_autonomous_verification_language(self):
        answer = answer_finance_intelligence_question("Can I trust my ETF data?", current_date="2026-06-20")
        self.assertIn("ETF/fund data trust", answer)
        self.assertIn("GLOBAL_CORE_ETF", answer)
        self.assertIn("VWCE", answer)
        self.assertIn("final real-world buy remains manual", answer)


if __name__ == "__main__":
    unittest.main()
