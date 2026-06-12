import json
import tempfile
import unittest
from pathlib import Path

from jarvis.jarvis_manual_candidate_data_entry_workspace import (
    BLOCKED_STATUS,
    PARTIAL_STATUS,
    READY_STATUS,
    REQUIRED_TEMPLATE_FIELDS,
    UNSAFE_SAFETY_CONTROLS,
    UNSAFE_TEMPLATE_FLAGS,
    build_manual_candidate_data_entry_workspace_pack,
    load_manual_candidate_data_entry_workspace_pack,
    load_template,
)


DEFAULT_WORKSPACE = "jarvis/data/jarvis_manual_candidate_data_entry_workspace.example.json"
TEMPLATE = "templates/jarvis_manual_candidate_watchlist_entry.local.template.json"


def _default_data() -> dict:
    return json.loads(Path(DEFAULT_WORKSPACE).read_text(encoding="utf-8"))


class ManualCandidateDataEntryWorkspaceTests(unittest.TestCase):
    def test_default_workspace_example_is_safe(self) -> None:
        pack = load_manual_candidate_data_entry_workspace_pack(DEFAULT_WORKSPACE)

        self.assertIn(pack.overall_status, {READY_STATUS, PARTIAL_STATUS})
        self.assertFalse(pack.registry_mutation)
        self.assertFalse(pack.candidate_registry_write)
        self.assertFalse(pack.candidate_intake_file_written)
        self.assertEqual(pack.next_action, "manual_candidate_watchlist_data_entry_only")

    def test_template_contains_required_v450_fields_and_blank_placeholder(self) -> None:
        template = load_template(TEMPLATE)
        entry = template["entries"][0]

        for field in REQUIRED_TEMPLATE_FIELDS:
            self.assertIn(field, entry)
        for field in ("watchlist_entry_id", "candidate_id", "display_name", "symbol_or_identifier", "issuer_or_provider"):
            self.assertEqual(entry[field], "")
        populated_placeholder_values = " ".join(str(value).lower() for value in entry.values() if isinstance(value, str) and value)
        for forbidden_value in ("account number", "portfolio value", "credential", "broker login", "password"):
            self.assertNotIn(forbidden_value, populated_placeholder_values)

    def test_template_unsafe_flags_are_false(self) -> None:
        entry = load_template(TEMPLATE)["entries"][0]

        for field in UNSAFE_TEMPLATE_FLAGS:
            with self.subTest(field=field):
                self.assertIs(entry[field], False)

    def test_unsafe_safety_controls_block(self) -> None:
        for field in UNSAFE_SAFETY_CONTROLS:
            with self.subTest(field=field):
                data = _default_data()
                data["safety_controls"][field] = True
                pack = build_manual_candidate_data_entry_workspace_pack(data)
                self.assertEqual(pack.overall_status, BLOCKED_STATUS)
                self.assertIn(f"safety_controls.{field} must be false.", pack.blocked_reasons)

    def test_unsafe_next_actions_block(self) -> None:
        for next_action in ("another_review_gate", "evidence_collection", "registry_mutation", "trade_execution"):
            with self.subTest(next_action=next_action):
                data = _default_data()
                data["next_action"] = next_action
                pack = build_manual_candidate_data_entry_workspace_pack(data)
                self.assertEqual(pack.overall_status, BLOCKED_STATUS)

    def test_recommended_paths_must_be_local_or_private(self) -> None:
        data = _default_data()
        data["recommended_local_paths"] = ["jarvis/data/real_candidate_watchlist.json"]

        pack = build_manual_candidate_data_entry_workspace_pack(data)

        self.assertEqual(pack.overall_status, BLOCKED_STATUS)
        self.assertTrue(any("recommended local path must be private/local" in reason for reason in pack.blocked_reasons))

    def test_missing_gitignore_patterns_are_partial_not_mutation(self) -> None:
        data = _default_data()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            (root / "templates").mkdir()
            (root / TEMPLATE).write_text(Path(TEMPLATE).read_text(encoding="utf-8"), encoding="utf-8")
            (root / ".gitignore").write_text("*.pyc\n", encoding="utf-8")

            pack = build_manual_candidate_data_entry_workspace_pack(data, root=root)

        self.assertEqual(pack.overall_status, PARTIAL_STATUS)
        self.assertTrue(pack.missing_gitignore_patterns)
        self.assertFalse(pack.registry_mutation)

    def test_module_creates_no_directories_or_files(self) -> None:
        data = _default_data()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
            pack = build_manual_candidate_data_entry_workspace_pack(data, root=root)
            after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

        self.assertIn(pack.overall_status, {BLOCKED_STATUS, PARTIAL_STATUS})
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
