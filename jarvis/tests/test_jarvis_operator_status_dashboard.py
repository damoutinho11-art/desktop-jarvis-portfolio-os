import copy
import unittest

from jarvis.jarvis_operator_status_dashboard import (
    BLOCKED_NEXT_MANUAL_ACTIONS,
    FALSE_REQUIRED_SAFETY_FIELDS,
    REQUIRED_COMPONENT_IDS,
    TRUE_REQUIRED_SAFETY_FIELDS,
    VALID_NEXT_MANUAL_ACTIONS,
    evaluate_operator_dashboard,
    load_json,
    validate_dashboard_config,
)


DEFAULT_CONFIG = "jarvis/data/jarvis_operator_status_dashboard.example.json"
SYNTHETIC_COMPLETE = "jarvis/data/jarvis_operator_status_dashboard.synthetic_complete.example.json"


def _complete_data():
    return load_json(SYNTHETIC_COMPLETE)


class OperatorStatusDashboardTests(unittest.TestCase):
    def test_default_example_blocks_or_partials_safely(self) -> None:
        result = evaluate_operator_dashboard(load_json(DEFAULT_CONFIG))

        self.assertIn(result.overall_status, {"OPERATOR_STATUS_DASHBOARD_BLOCKED_SAFE", "OPERATOR_STATUS_DASHBOARD_PARTIAL_SAFE"})
        self.assertFalse(result.network_calls)
        self.assertFalse(result.writes)

    def test_synthetic_complete_ready(self) -> None:
        result = evaluate_operator_dashboard(_complete_data())

        self.assertEqual(result.overall_status, "OPERATOR_STATUS_DASHBOARD_READY_SAFE")
        self.assertEqual({component.component_id for component in result.components}, set(REQUIRED_COMPONENT_IDS))

    def test_required_components_are_enforced(self) -> None:
        for component_id in ("phase1_real_pipeline", "phase2_candidate_intake_chain", "public_data_freshness_monitor"):
            with self.subTest(component_id=component_id):
                data = _complete_data()
                data["component_statuses"] = [
                    component for component in data["component_statuses"] if component["component_id"] != component_id
                ]
                result = evaluate_operator_dashboard(data)
                self.assertEqual(result.overall_status, "OPERATOR_STATUS_DASHBOARD_BLOCKED_SAFE")
                self.assertTrue(any(component_id in reason for reason in result.blocked_reasons))

    def test_unsafe_safety_controls_are_blocked(self) -> None:
        for field in FALSE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data["safety_controls"][field] = True
                self.assertTrue(validate_dashboard_config(data))

    def test_required_true_controls_are_enforced(self) -> None:
        for field in TRUE_REQUIRED_SAFETY_FIELDS:
            with self.subTest(field=field):
                data = _complete_data()
                data["safety_controls"][field] = False
                self.assertTrue(validate_dashboard_config(data))

    def test_next_manual_action_valid_values_accepted(self) -> None:
        for action in VALID_NEXT_MANUAL_ACTIONS:
            with self.subTest(action=action):
                data = _complete_data()
                data["next_manual_action"] = action
                result = evaluate_operator_dashboard(data)
                self.assertNotEqual(result.overall_status, "OPERATOR_STATUS_DASHBOARD_BLOCKED_SAFE")

    def test_blocked_next_manual_actions(self) -> None:
        for action in ("another_gate", "evidence_verification", "approval", "allocation_recommendation", "trade_execution"):
            with self.subTest(action=action):
                data = _complete_data()
                data["next_manual_action"] = action
                result = evaluate_operator_dashboard(data)
                self.assertEqual(result.overall_status, "OPERATOR_STATUS_DASHBOARD_BLOCKED_SAFE")

    def test_component_status_must_be_safe(self) -> None:
        data = _complete_data()
        data["component_statuses"][0]["latest_known_status"] = "APPROVED"

        result = evaluate_operator_dashboard(data)

        self.assertEqual(result.overall_status, "OPERATOR_STATUS_DASHBOARD_BLOCKED_SAFE")

    def test_component_redundancy_note_required(self) -> None:
        data = _complete_data()
        data["component_statuses"][0]["redundant_next_steps_to_avoid"] = []

        result = evaluate_operator_dashboard(data)

        self.assertEqual(result.overall_status, "OPERATOR_STATUS_DASHBOARD_BLOCKED_SAFE")


if __name__ == "__main__":
    unittest.main()
