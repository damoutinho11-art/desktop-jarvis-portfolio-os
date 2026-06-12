import copy
import unittest

from jarvis.jarvis_local_operator_bootstrap import (
    FALSE_REQUIRED_SAFETY_FIELDS,
    TRUE_REQUIRED_SAFETY_FIELDS,
    VALID_NEXT_MANUAL_ACTIONS,
    evaluate_local_operator_bootstrap,
    load_json,
    validate_bootstrap_config,
    validate_gitignore_expectations,
    validate_local_path,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_local_operator_bootstrap.example.json"
SYNTHETIC_READY = "jarvis/data/jarvis_local_operator_bootstrap.synthetic_ready.example.json"


def _ready_data():
    return load_json(SYNTHETIC_READY)


class LocalOperatorBootstrapTests(unittest.TestCase):
    def test_default_example_blocks_or_partials_safely(self) -> None:
        result = evaluate_local_operator_bootstrap(load_json(DEFAULT_CONFIG))

        self.assertIn(result.overall_status, {"LOCAL_OPERATOR_BOOTSTRAP_BLOCKED_SAFE", "LOCAL_OPERATOR_BOOTSTRAP_PARTIAL_SAFE"})
        self.assertFalse(result.writes)
        self.assertFalse(result.subprocess_execution)

    def test_synthetic_ready_returns_ready(self) -> None:
        result = evaluate_local_operator_bootstrap(_ready_data())

        self.assertEqual(result.overall_status, "LOCAL_OPERATOR_BOOTSTRAP_READY_SAFE")
        self.assertEqual(len(result.templates), 2)

    def test_required_templates_are_enforced(self) -> None:
        data = _ready_data()
        data["templates"] = data["templates"][:1]

        result = evaluate_local_operator_bootstrap(data)

        self.assertEqual(result.overall_status, "LOCAL_OPERATOR_BOOTSTRAP_BLOCKED_SAFE")

    def test_recommended_local_paths_are_enforced(self) -> None:
        data = _ready_data()
        data["recommended_local_paths"] = []

        result = evaluate_local_operator_bootstrap(data)

        self.assertEqual(result.overall_status, "LOCAL_OPERATOR_BOOTSTRAP_BLOCKED_SAFE")

    def test_unsafe_local_path_blocks(self) -> None:
        self.assertTrue(validate_local_path("jarvis/data/manual_candidate_watchlist.json"))

    def test_template_flags_block(self) -> None:
        for field, value in (("contains_private_data", True), ("should_commit_local_copy", True)):
            with self.subTest(field=field):
                data = _ready_data()
                data["templates"][0][field] = value
                result = evaluate_local_operator_bootstrap(data)
                self.assertEqual(result.overall_status, "LOCAL_OPERATOR_BOOTSTRAP_BLOCKED_SAFE")

    def test_missing_gitignore_patterns_partial_not_mutation(self) -> None:
        data = _ready_data()
        result = evaluate_local_operator_bootstrap(data, gitignore_text="*.pyc\n")

        self.assertEqual(result.overall_status, "LOCAL_OPERATOR_BOOTSTRAP_PARTIAL_SAFE")
        self.assertTrue(result.missing_gitignore_patterns)
        self.assertFalse(result.registry_mutation)

    def test_unsafe_safety_controls_are_blocked(self) -> None:
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _ready_data()
                data["safety_controls"][field] = True
                self.assertTrue(validate_bootstrap_config(data))

    def test_required_true_assertions_are_enforced(self) -> None:
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _ready_data()
                data["safety_controls"][field] = False
                self.assertTrue(validate_bootstrap_config(data))

    def test_next_manual_action_valid_values_accepted(self) -> None:
        for action in VALID_NEXT_MANUAL_ACTIONS:
            with self.subTest(action=action):
                data = _ready_data()
                data["next_manual_action"] = action
                result = evaluate_local_operator_bootstrap(data)
                self.assertNotEqual(result.overall_status, "LOCAL_OPERATOR_BOOTSTRAP_BLOCKED_SAFE")

    def test_blocked_next_manual_actions(self) -> None:
        for action in ("another_gate", "scheduler_creation", "evidence_verification", "approval", "allocation_recommendation", "trade_execution"):
            with self.subTest(action=action):
                data = _ready_data()
                data["next_manual_action"] = action
                result = evaluate_local_operator_bootstrap(data)
                self.assertEqual(result.overall_status, "LOCAL_OPERATOR_BOOTSTRAP_BLOCKED_SAFE")


if __name__ == "__main__":
    unittest.main()
