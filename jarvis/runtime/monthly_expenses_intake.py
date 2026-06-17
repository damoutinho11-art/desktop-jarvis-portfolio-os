"""J.A.R.V.I.S. v58.0 Monthly Expenses Intake.

Creates and validates a local-only monthly expenses intake file.

Purpose:
- stop using made-up emergency fund numbers
- calculate emergency fund targets from confirmed expenses
- classify survival, normal, and flexible monthly expenses
- keep all data brokerless, credential-free, and manual-only

Safety invariant:
Automated research. Manual trust. Manual approval. No execution.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Mapping

STATUS_READY = "JARVIS_V58_0_MONTHLY_EXPENSES_INTAKE_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V58_0_MONTHLY_EXPENSES_INTAKE_REVIEW_REQUIRED_SAFE"
STATUS_BLOCKED = "JARVIS_V58_0_MONTHLY_EXPENSES_INTAKE_BLOCKED_SAFE"

INTAKE_READY = "MONTHLY_EXPENSES_READY_FOR_EMERGENCY_FUND_DECISION"
INTAKE_TEMPLATE_WRITTEN = "MONTHLY_EXPENSES_TEMPLATE_WRITTEN_REVIEW_REQUIRED"
INTAKE_BLOCKED = "MONTHLY_EXPENSES_INTAKE_BLOCKED"

NEXT_STAGE = "personal_finance_data_readiness_gate"

DEFAULT_MONTHLY_EXPENSES_PATH = "jarvis/local/monthly_expenses.local.json"

FORBIDDEN_KEY_FRAGMENTS = (
    "password",
    "passwd",
    "api_key",
    "apikey",
    "secret",
    "token",
    "access_token",
    "refresh_token",
    "private_key",
    "broker_credentials",
    "credential",
    "client_secret",
    "bank_login",
    "card_number",
)


@dataclass(frozen=True)
class ExpenseCategory:
    category_id: str
    label: str
    monthly_eur: float
    expense_type: str
    required: bool
    notes: str


@dataclass(frozen=True)
class MonthlyExpensesIntakeResult:
    status: str
    intake_status: str
    recommended_next_stage: str
    current_date: str
    path: str
    present: bool
    loaded: bool
    is_template: bool
    expenses_confirmed: bool
    emergency_fund_decision_allowed: bool
    monthly_contribution_decision_allowed: bool
    template_write_requested: bool
    template_written: bool
    survival_monthly_expenses_eur: float
    normal_monthly_expenses_eur: float
    flexible_monthly_expenses_eur: float
    planned_monthly_contribution_eur: float | None
    minimum_emergency_months: float
    ideal_emergency_months: float
    minimum_emergency_fund_eur: float | None
    ideal_emergency_fund_eur: float | None
    expense_categories: tuple[ExpenseCategory, ...]
    forbidden_credential_keys_found: tuple[str, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    allocation_mutation: bool
    approval_ticket_mutation: bool
    evidence_pack_mutation: bool
    local_cache_mutation: bool
    portfolio_state_mutation: bool
    buy_request_created: bool
    broker_connection_forbidden: bool
    credentials_forbidden: bool
    private_account_ingestion_forbidden: bool
    order_creation_forbidden: bool
    no_trades_executed: bool
    auto_approval_forbidden: bool
    auto_selling_forbidden: bool


def _today() -> str:
    return date.today().isoformat()


def _dedupe(items: Any) -> tuple[str, ...]:
    return tuple(dict.fromkeys(str(item) for item in items if str(item)))


def _to_float(value: Any, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.replace(",", ".").strip())
        except ValueError:
            return default
    return default


def _money(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 2)


def _load_json(path: Path) -> Mapping[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, Mapping) else None


def _find_forbidden_keys(payload: Any, prefix: str = "") -> tuple[str, ...]:
    found: list[str] = []
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            key_text = str(key)
            current = f"{prefix}.{key_text}" if prefix else key_text
            if any(fragment in key_text.lower() for fragment in FORBIDDEN_KEY_FRAGMENTS):
                found.append(current)
            found.extend(_find_forbidden_keys(value, current))
    elif isinstance(payload, list):
        for index, value in enumerate(payload):
            found.extend(_find_forbidden_keys(value, f"{prefix}[{index}]"))
    return _dedupe(found)


def build_monthly_expenses_template(*, current_date: str | None = None) -> dict[str, Any]:
    current_date_text = current_date or _today()
    return {
        "schema": "JARVIS_MONTHLY_EXPENSES_V1",
        "as_of": current_date_text,
        "is_template": True,
        "expenses_confirmed": False,
        "currency": "EUR",
        "minimum_emergency_months": 3,
        "ideal_emergency_months": 6,
        "planned_monthly_contribution_eur": 400,
        "expense_categories": [
            {
                "category_id": "rent",
                "label": "Rent / housing",
                "monthly_eur": 0,
                "expense_type": "survival",
                "required": True,
                "notes": "Manual estimate only.",
            },
            {
                "category_id": "utilities",
                "label": "Utilities",
                "monthly_eur": 0,
                "expense_type": "survival",
                "required": True,
                "notes": "Electricity, heating, water, building fees.",
            },
            {
                "category_id": "food_basic",
                "label": "Food - basic",
                "monthly_eur": 0,
                "expense_type": "survival",
                "required": True,
                "notes": "Minimum realistic groceries.",
            },
            {
                "category_id": "transport",
                "label": "Transport",
                "monthly_eur": 0,
                "expense_type": "survival",
                "required": True,
                "notes": "Public transport, fuel, taxis if unavoidable.",
            },
            {
                "category_id": "phone_internet",
                "label": "Phone / internet",
                "monthly_eur": 0,
                "expense_type": "normal",
                "required": True,
                "notes": "Communication bills.",
            },
            {
                "category_id": "insurance_health",
                "label": "Insurance / health",
                "monthly_eur": 0,
                "expense_type": "normal",
                "required": False,
                "notes": "Insurance, medicine, appointments averaged monthly.",
            },
            {
                "category_id": "subscriptions",
                "label": "Subscriptions",
                "monthly_eur": 0,
                "expense_type": "flexible",
                "required": False,
                "notes": "Streaming, apps, memberships.",
            },
            {
                "category_id": "restaurants_coffee",
                "label": "Restaurants / coffee",
                "monthly_eur": 0,
                "expense_type": "flexible",
                "required": False,
                "notes": "Flexible lifestyle spending.",
            },
            {
                "category_id": "clothes_personal",
                "label": "Clothes / personal",
                "monthly_eur": 0,
                "expense_type": "flexible",
                "required": False,
                "notes": "Average monthly estimate.",
            },
            {
                "category_id": "annual_irregular",
                "label": "Annual / irregular costs averaged monthly",
                "monthly_eur": 0,
                "expense_type": "normal",
                "required": False,
                "notes": "Flights, gifts, repairs, taxes, renewals divided by 12.",
            },
            {
                "category_id": "other_required",
                "label": "Other required expenses",
                "monthly_eur": 0,
                "expense_type": "normal",
                "required": False,
                "notes": "Anything necessary not listed above.",
            },
        ],
        "notes": [
            "Keep this file local and ignored.",
            "Do not add bank logins, card numbers, passwords, API keys, tokens, or credentials.",
            "Set is_template to false and expenses_confirmed to true only after manually filling real estimates.",
            "This intake does not mutate portfolio state and does not approve any buy.",
        ],
    }


def _write_template(path: str | Path, payload: Mapping[str, Any]) -> str:
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(file_path)


def _parse_categories(payload: Mapping[str, Any]) -> tuple[ExpenseCategory, ...]:
    raw_categories = payload.get("expense_categories")
    if not isinstance(raw_categories, list):
        return ()

    categories: list[ExpenseCategory] = []
    for raw in raw_categories:
        if not isinstance(raw, Mapping):
            continue
        expense_type = str(raw.get("expense_type", "normal")).strip().lower()
        if expense_type not in {"survival", "normal", "flexible"}:
            expense_type = "normal"
        categories.append(
            ExpenseCategory(
                category_id=str(raw.get("category_id", "")).strip(),
                label=str(raw.get("label", "")).strip(),
                monthly_eur=_to_float(raw.get("monthly_eur"), 0.0),
                expense_type=expense_type,
                required=bool(raw.get("required", False)),
                notes=str(raw.get("notes", "")).strip(),
            )
        )
    return tuple(categories)


def _sum_by_type(categories: tuple[ExpenseCategory, ...], expense_type: str) -> float:
    return round(sum(item.monthly_eur for item in categories if item.expense_type == expense_type), 2)


def build_monthly_expenses_intake_result(
    *,
    current_date: str | None = None,
    monthly_expenses_path: str | Path = DEFAULT_MONTHLY_EXPENSES_PATH,
    write_monthly_expenses_template: bool = False,
) -> MonthlyExpensesIntakeResult:
    current_date_text = current_date or _today()
    path = Path(monthly_expenses_path)
    template_written = False

    if write_monthly_expenses_template:
        _write_template(path, build_monthly_expenses_template(current_date=current_date_text))
        template_written = True

    payload = _load_json(path)
    present = path.exists()
    loaded = payload is not None
    is_template = bool(payload.get("is_template", False)) if payload else False
    forbidden_keys = _find_forbidden_keys(payload) if payload else ()
    categories = _parse_categories(payload) if payload else ()

    blockers: list[str] = []
    warnings: list[str] = []

    if not present:
        blockers.append("missing_monthly_expenses")
    elif not loaded:
        blockers.append("monthly_expenses_invalid_json")
    elif forbidden_keys:
        blockers.append("monthly_expenses_contains_forbidden_credential_like_keys")
    elif is_template:
        blockers.append("monthly_expenses_template_not_confirmed")
    elif payload.get("expenses_confirmed") is not True:
        blockers.append("monthly_expenses_not_confirmed")
    elif not categories:
        blockers.append("monthly_expense_categories_missing")
    elif all(item.monthly_eur <= 0 for item in categories):
        blockers.append("monthly_expense_values_missing")
    elif _sum_by_type(categories, "survival") <= 0:
        blockers.append("survival_expenses_missing")

    survival = _sum_by_type(categories, "survival")
    normal_base = _sum_by_type(categories, "normal")
    flexible = _sum_by_type(categories, "flexible")
    normal_total = round(survival + normal_base + flexible, 2)

    min_months = _to_float(payload.get("minimum_emergency_months"), 3.0) if payload else 3.0
    ideal_months = _to_float(payload.get("ideal_emergency_months"), 6.0) if payload else 6.0
    if min_months <= 0:
        min_months = 3.0
        warnings.append("minimum_emergency_months_invalid_defaulted_to_3")
    if ideal_months < min_months:
        ideal_months = min_months
        warnings.append("ideal_emergency_months_below_minimum_defaulted_to_minimum")

    planned_contribution_raw = payload.get("planned_monthly_contribution_eur") if payload else None
    planned_contribution = _to_float(planned_contribution_raw, -1.0)
    planned_contribution_value: float | None = planned_contribution if planned_contribution >= 0 else None

    confirmed = not blockers and bool(payload and payload.get("expenses_confirmed") is True)
    emergency_decision_allowed = confirmed
    contribution_decision_allowed = confirmed and planned_contribution_value is not None

    min_emergency = _money(survival * min_months) if confirmed else None
    ideal_emergency = _money(normal_total * ideal_months) if confirmed else None

    if confirmed:
        warnings.append("monthly expenses are manually confirmed; still no execution or auto-approval")

    if confirmed:
        status = STATUS_READY
        intake_status = INTAKE_READY
    elif write_monthly_expenses_template:
        status = STATUS_REVIEW_REQUIRED
        intake_status = INTAKE_TEMPLATE_WRITTEN
    else:
        status = STATUS_BLOCKED
        intake_status = INTAKE_BLOCKED

    return MonthlyExpensesIntakeResult(
        status=status,
        intake_status=intake_status,
        recommended_next_stage=NEXT_STAGE,
        current_date=current_date_text,
        path=str(path),
        present=present,
        loaded=loaded,
        is_template=is_template,
        expenses_confirmed=confirmed,
        emergency_fund_decision_allowed=emergency_decision_allowed,
        monthly_contribution_decision_allowed=contribution_decision_allowed,
        template_write_requested=write_monthly_expenses_template,
        template_written=template_written,
        survival_monthly_expenses_eur=_money(survival) or 0.0,
        normal_monthly_expenses_eur=_money(normal_total) or 0.0,
        flexible_monthly_expenses_eur=_money(flexible) or 0.0,
        planned_monthly_contribution_eur=_money(planned_contribution_value),
        minimum_emergency_months=min_months,
        ideal_emergency_months=ideal_months,
        minimum_emergency_fund_eur=min_emergency,
        ideal_emergency_fund_eur=ideal_emergency,
        expense_categories=categories,
        forbidden_credential_keys_found=forbidden_keys,
        blockers=_dedupe(blockers),
        warnings=_dedupe(warnings),
        allocation_mutation=False,
        approval_ticket_mutation=False,
        evidence_pack_mutation=False,
        local_cache_mutation=False,
        portfolio_state_mutation=False,
        buy_request_created=False,
        broker_connection_forbidden=True,
        credentials_forbidden=True,
        private_account_ingestion_forbidden=True,
        order_creation_forbidden=True,
        no_trades_executed=True,
        auto_approval_forbidden=True,
        auto_selling_forbidden=True,
    )


def format_monthly_expenses_intake(result: MonthlyExpensesIntakeResult) -> str:
    lines = [
        "J.A.R.V.I.S. MONTHLY EXPENSES INTAKE",
        f"status: {result.status}",
        f"intake status: {result.intake_status}",
        f"current date: {result.current_date}",
        f"recommended next stage: {result.recommended_next_stage}",
        f"path: {result.path}",
        f"present: {result.present}",
        f"loaded: {result.loaded}",
        f"template: {result.is_template}",
        f"expenses confirmed: {result.expenses_confirmed}",
        f"template write requested: {result.template_write_requested}",
        f"template written: {result.template_written}",
        "",
        "Expense summary:",
        f"- survival monthly expenses EUR: {result.survival_monthly_expenses_eur:.2f}",
        f"- normal monthly expenses EUR: {result.normal_monthly_expenses_eur:.2f}",
        f"- flexible monthly expenses EUR: {result.flexible_monthly_expenses_eur:.2f}",
        f"- planned monthly contribution EUR: {result.planned_monthly_contribution_eur}",
        "",
        "Emergency fund targets:",
        f"- minimum emergency months: {result.minimum_emergency_months:g}",
        f"- ideal emergency months: {result.ideal_emergency_months:g}",
        f"- minimum emergency fund EUR: {result.minimum_emergency_fund_eur}",
        f"- ideal emergency fund EUR: {result.ideal_emergency_fund_eur}",
        f"- emergency fund decision allowed: {result.emergency_fund_decision_allowed}",
        f"- monthly contribution decision allowed: {result.monthly_contribution_decision_allowed}",
        "",
        "Categories:",
    ]

    if result.expense_categories:
        for item in result.expense_categories:
            lines.append(
                f"- {item.category_id}: {item.label}; type={item.expense_type}; "
                f"required={item.required}; monthly EUR={item.monthly_eur:.2f}"
            )
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "Safety:",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
            f"- evidence pack mutation: {result.evidence_pack_mutation}",
            f"- local cache mutation: {result.local_cache_mutation}",
            f"- portfolio state mutation: {result.portfolio_state_mutation}",
            f"- buy request created: {result.buy_request_created}",
            f"- auto approval forbidden: {result.auto_approval_forbidden}",
            f"- auto selling forbidden: {result.auto_selling_forbidden}",
            "- no broker APIs",
            "- no credentials",
            "- no private account ingestion",
            "- no orders created",
            "- no trades executed",
        ]
    )

    if result.forbidden_credential_keys_found:
        lines.extend(["", "Forbidden credential-like keys found:"])
        lines.extend(f"- {key}" for key in result.forbidden_credential_keys_found)

    if result.blockers:
        lines.extend(["", "Blockers:"])
        lines.extend(f"- {blocker}" for blocker in result.blockers)
    else:
        lines.append("blockers: none")

    if result.warnings:
        lines.extend(["", "Warnings:"])
        lines.extend(f"- {warning}" for warning in result.warnings)
    else:
        lines.append("warnings: none")

    return "\n".join(lines)


def _safety_check_output() -> str:
    return "\n".join(
        [
            "J.A.R.V.I.S. SAFETY CHECK",
            "status: SAFETY_CHECK_READY_SAFE",
            "blocked prompt: Jarvis, buy BTC now.",
            "decision: EXECUTION_FORBIDDEN",
            "reason: Automated research only; manual trust, manual approval, no execution.",
            "buy request created: False",
            "broker connection: False",
            "order created: False",
            "trade executed: False",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="J.A.R.V.I.S. v58 monthly expenses intake.")
    parser.add_argument("--monthly-expenses-intake", action="store_true")
    parser.add_argument("--write-monthly-expenses-template", action="store_true")
    parser.add_argument("--current-date", default=None)
    parser.add_argument("--monthly-expenses-path", default=DEFAULT_MONTHLY_EXPENSES_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(_safety_check_output())
        return 0

    result = build_monthly_expenses_intake_result(
        current_date=args.current_date,
        monthly_expenses_path=args.monthly_expenses_path,
        write_monthly_expenses_template=args.write_monthly_expenses_template,
    )
    print(format_monthly_expenses_intake(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
