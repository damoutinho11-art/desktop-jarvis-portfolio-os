"""Review and record manual decisions for saved J.A.R.V.I.S. approval tickets."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_TICKET_PATH = Path("outputs/approval_ticket_latest.json")
DEFAULT_REVIEWED_PATH = Path("outputs/approval_ticket_reviewed_latest.json")
DEFAULT_DECISIONS_PATH = Path("outputs/approval_decisions.jsonl")
DEFAULT_TEST_DECISIONS_PATH = Path("outputs/approval_decisions_test.jsonl")
SAFETY_LINE = "Manual approval required. No trades executed."


def load_ticket(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2, sort_keys=True)
        file.write("\n")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        json.dump(payload, file, sort_keys=True)
        file.write("\n")


def reviewed_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def format_amount(amount: int | float) -> str:
    return f"EUR {float(amount):,.2f}"


def print_action_section(title: str, actions: list[dict[str, Any]]) -> None:
    print(f"{title}:")
    if not actions:
        print("- None.")
        return
    for action in actions:
        print(f"- {action['asset']}: {format_amount(action['amount'])}; {action['reason']}")


def print_summary(ticket: dict[str, Any]) -> None:
    print("J.A.R.V.I.S. Approval Ticket Review")
    print("=" * 37)
    print(f"ticket_id: {ticket.get('ticket_id')}")
    print(f"as_of: {ticket.get('as_of')}")
    print(f"portfolio_mode: {ticket.get('portfolio_mode')}")
    print("executable_allocation:")
    for asset, amount in ticket.get("executable_allocation", {}).items():
        print(f"- {asset}: {format_amount(amount)}")
    print_action_section("blocked_actions", ticket.get("blocked_actions", []))
    print_action_section("fallback_actions", ticket.get("fallback_actions", []))
    print_action_section("reserve_actions", ticket.get("reserve_actions", []))
    print("warnings:")
    for warning in ticket.get("warnings", []):
        print(f"- {warning}")
    print(SAFETY_LINE)


def decision_record(
    ticket: dict[str, Any], decision: str, note: str, timestamp: str
) -> dict[str, Any]:
    return {
        "ticket_id": ticket["ticket_id"],
        "as_of": ticket["as_of"],
        "decision": decision,
        "note": note,
        "trades_executed": False,
        "timestamp": timestamp,
        "executable_allocation": ticket.get("executable_allocation", {}),
    }


def record_decision(
    ticket: dict[str, Any],
    decision: str,
    note: str,
    test_decision: bool = False,
    reviewed_path: Path = DEFAULT_REVIEWED_PATH,
    decisions_path: Path = DEFAULT_DECISIONS_PATH,
    test_decisions_path: Path = DEFAULT_TEST_DECISIONS_PATH,
) -> dict[str, Any]:
    timestamp = reviewed_timestamp()
    if test_decision:
        decisions_path = test_decisions_path

    record = decision_record(ticket, decision, note, timestamp)
    record["test_decision"] = test_decision

    reviewed_ticket = dict(ticket)
    reviewed_ticket["manual_decision"] = {
        "decision": decision,
        "note": note,
        "timestamp": timestamp,
        "trades_executed": False,
        "safety_line": SAFETY_LINE,
    }
    if test_decision:
        reviewed_ticket["test_decision"] = True
    reviewed_ticket["approval_status"] = f"manual_{decision}"
    reviewed_ticket["trades_executed"] = False

    save_json(reviewed_path, reviewed_ticket)
    append_jsonl(decisions_path, record)
    return record


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Review a J.A.R.V.I.S. manual approval ticket."
    )
    parser.add_argument(
        "--ticket",
        default=str(DEFAULT_TICKET_PATH),
        help="Path to approval ticket JSON. Defaults to outputs/approval_ticket_latest.json.",
    )
    parser.add_argument(
        "--decision",
        choices=["approved", "rejected", "skipped"],
        help="Record a manual decision for the ticket.",
    )
    parser.add_argument(
        "--note",
        default="",
        help='Optional review note, for example --note "Looks correct."',
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Write the decision to outputs/approval_decisions_test.jsonl.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ticket = load_ticket(Path(args.ticket))
    print_summary(ticket)

    if args.decision:
        record_decision(ticket, args.decision, args.note, test_decision=args.test)
        if args.test:
            print("Test decision recorded. No trades executed.")
        else:
            print("Decision recorded. No trades executed.")


if __name__ == "__main__":
    main()
