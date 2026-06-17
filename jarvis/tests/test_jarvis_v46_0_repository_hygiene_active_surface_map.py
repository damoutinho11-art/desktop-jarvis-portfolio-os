from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class JarvisV460RepositoryHygieneActiveSurfaceMapTests(unittest.TestCase):
    def test_readme_describes_current_v45_system_not_v0_only(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("Current operating model", readme)
        self.assertIn("v45 free-research cache evidence-pack bridge", readme)
        self.assertIn("Optional public research APIs", readme)
        self.assertNotIn("does not use API keys, and does not make network calls", readme)

    def test_generated_files_are_ignored(self) -> None:
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

        self.assertIn("apply_v*.ps1", gitignore)
        self.assertIn("outputs/free_research_evidence_pack_latest.json", gitignore)
        self.assertIn("jarvis/local/free_research_api_cache.local.json", gitignore)

    def test_active_system_map_exists(self) -> None:
        active_map = (ROOT / "docs" / "JARVIS_ACTIVE_SYSTEM_MAP.md").read_text(encoding="utf-8")

        self.assertIn("jarvis_operator.py", active_map)
        self.assertIn("jarvis_v45_0_free_research_cache_evidence_pack_bridge", active_map)
        self.assertIn("Do not change in hygiene stages", active_map)

    def test_hygiene_plan_exists(self) -> None:
        plan = (ROOT / "docs" / "JARVIS_REPOSITORY_HYGIENE_PLAN.md").read_text(encoding="utf-8")

        self.assertIn("Clean safely first. Collapse dependencies second. Delete legacy code last.", plan)
        self.assertIn("Runtime Dependency Slimline", plan)

    def test_stale_root_portfolio_backups_removed(self) -> None:
        backups = sorted(ROOT.glob("portfolio_state_backup_20260604_*.json"))

        self.assertEqual(backups, [])


if __name__ == "__main__":
    unittest.main()