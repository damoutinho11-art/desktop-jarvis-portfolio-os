"""J.A.R.V.I.S. v79.0 product mode operator.

This is the first user-facing product layer after the cleanup/archive work.

It does not create orders, connect brokers, mutate allocation, approve buys,
or execute trades. It gathers existing active-runtime results into one readable
operator view: today, week, or status.
"""

from __future__ import annotations

import argparse
import importlib
import inspect
import json
from dataclasses import asdict, dataclass, is_dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V79_0_PRODUCT_MODE_OPERATOR_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V79_0_PRODUCT_MODE_OPERATOR_REVIEW_REQUIRED_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/product_mode_operator_latest.json"


@dataclass(frozen=True)
class ProductModeComponent:
    name: str
    module_name: str
    available: bool
    status: str | None
    blockers: list[str]
    warnings: list[str]
    selected_fields: dict[str, Any]


@dataclass(frozen=True)
class ProductModeResult:
    status: str
    mode: str
    current_date: str
    product_verdict: str
    product_ready_for_manual_use: bool
    manual_approval_required: bool
    execution_forbidden: bool
    safety_check_blocked_execution: bool
    unresolved_local_import_count: int | None
    legacy_module_archive_candidate_count: int | None
    monthly_contribution_eur: float | None
    emergency_fund_eur: float | None
    emergency_months_covered: float | None
    minimum_emergency_fund_eur: float | None
    ideal_emergency_fund_eur: float | None
    recommended_emergency_top_up_eur: float | None
    recommended_crypto_eur: float | None
    recommended_etf_fund_eur: float | None
    recommended_individual_stock_eur: float | None
    full_allocation_blockers: list[str]
    today_lines: list[str]
    week_lines: list[str]
    status_lines: list[str]
    components: list[dict[str, Any]]
    deletion_performed: bool
    archive_performed: bool
    file_move_performed: bool
    runtime_behavior_mutation: bool
    allocation_mutation: bool
    approval_ticket_mutation: bool
    buy_request_created: bool
    broker_connection: bool
    credentials_used: bool
    private_account_data_ingestion: bool
    order_created: bool
    trade_executed: bool
    warnings: list[str]
    blockers: list[str]
    report_written: bool
    report_path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _to_plain(value: Any) -> Any:
    if is_dataclass(value):
        return _to_plain(asdict(value))
    if isinstance(value, Mapping):
        return {str(k): _to_plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_to_plain(v) for v in value]
    return value


def _norm(key: str) -> str:
    return key.lower().replace("-", "_").replace(" ", "_")


def _find_first(data: Any, keys: Sequence[str]) -> Any:
    wanted = {_norm(key) for key in keys}

    if isinstance(data, Mapping):
        normal_map = {_norm(str(k)): k for k in data.keys()}
        for key in wanted:
            if key in normal_map:
                value = data[normal_map[key]]
                if value is not None:
                    return value
        for value in data.values():
            found = _find_first(value, keys)
            if found is not None:
                return found

    if isinstance(data, list):
        for item in data:
            found = _find_first(item, keys)
            if found is not None:
                return found

    return None


def _find_all_strings(data: Any, keys: Sequence[str]) -> list[str]:
    found: list[str] = []
    wanted = {_norm(key) for key in keys}

    def walk(value: Any) -> None:
        if isinstance(value, Mapping):
            for raw_key, raw_value in value.items():
                if _norm(str(raw_key)) in wanted:
                    if isinstance(raw_value, str):
                        found.append(raw_value)
                    elif isinstance(raw_value, Sequence) and not isinstance(raw_value, (str, bytes)):
                        found.extend(str(item) for item in raw_value if str(item))
                walk(raw_value)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(data)
    return list(dict.fromkeys(found))


def _float_or_none(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _flatten_numeric_fields(data: Any, prefix: str = "") -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    if isinstance(data, Mapping):
        for key, value in data.items():
            key_path = f"{prefix}.{key}" if prefix else str(key)
            rows.extend(_flatten_numeric_fields(value, key_path))
    elif isinstance(data, list):
        for item in data:
            rows.extend(_flatten_numeric_fields(item, prefix))
    elif isinstance(data, (int, float)) and not isinstance(data, bool):
        rows.append({"key": prefix, "value": round(float(data), 2)})

    return rows


def _first_numeric_by_terms(
    components: Sequence[ProductModeComponent],
    include_terms: Sequence[str],
    exclude_terms: Sequence[str] = (),
) -> float | None:
    include = [_norm(term) for term in include_terms]
    exclude = [_norm(term) for term in exclude_terms]

    for component in components:
        rows = component.selected_fields.get("__flat_numeric_fields", [])
        if not isinstance(rows, list):
            continue

        for row in rows:
            key = _norm(str(row.get("key", "")))
            if all(term in key for term in include) and not any(term in key for term in exclude):
                return _float_or_none(row.get("value"))

    return None


def _call_builder(
    *,
    component_name: str,
    module_name: str,
    builder_names: Sequence[str],
    kwargs: dict[str, Any],
    selected_keys: Sequence[str],
) -> ProductModeComponent:
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - defensive product surface
        return ProductModeComponent(
            name=component_name,
            module_name=module_name,
            available=False,
            status=None,
            blockers=[f"import failed: {exc}"],
            warnings=[],
            selected_fields={},
        )

    builder = None
    for name in builder_names:
        candidate = getattr(module, name, None)
        if callable(candidate):
            builder = candidate
            break

    if builder is None:
        return ProductModeComponent(
            name=component_name,
            module_name=module_name,
            available=False,
            status=None,
            blockers=[f"no supported builder found: {', '.join(builder_names)}"],
            warnings=[],
            selected_fields={},
        )

    try:
        signature = inspect.signature(builder)
        if any(param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values()):
            supported_kwargs = kwargs
        else:
            supported_kwargs = {
                key: value for key, value in kwargs.items() if key in signature.parameters
            }
        result = builder(**supported_kwargs)
        data = _to_plain(result)
    except Exception as exc:  # pragma: no cover - defensive product surface
        return ProductModeComponent(
            name=component_name,
            module_name=module_name,
            available=False,
            status=None,
            blockers=[f"builder failed: {exc}"],
            warnings=[],
            selected_fields={},
        )

    selected: dict[str, Any] = {}
    for key in selected_keys:
        value = _find_first(data, [key])
        if value is not None:
            selected[key] = value

    status = _find_first(
        data,
        [
            "status",
            "audit_status",
            "policy_status",
            "decision_status",
            "packet_status",
            "execution_status",
            "coverage_status",
            "plan_status",
        ],
    )

    return ProductModeComponent(
        name=component_name,
        module_name=module_name,
        available=True,
        status=str(status) if status is not None else None,
        blockers=_find_all_strings(data, ["blockers", "full_allocation_blockers"]),
        warnings=_find_all_strings(data, ["warnings"]),
        selected_fields=selected,
    )


def _component_data(components: Sequence[ProductModeComponent]) -> list[dict[str, Any]]:
    return [asdict(component) for component in components]


def _first_amount(components: Sequence[ProductModeComponent], keys: Sequence[str]) -> float | None:
    for component in components:
        value = _find_first(component.selected_fields, keys)
        amount = _float_or_none(value)
        if amount is not None:
            return amount
    return None


def _first_value(components: Sequence[ProductModeComponent], keys: Sequence[str]) -> Any:
    for component in components:
        value = _find_first(component.selected_fields, keys)
        if value is not None:
            return value
    return None


def _money(value: float | None) -> str:
    return "unknown" if value is None else f"EUR {value:.2f}"


def _clean_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence):
        return list(dict.fromkeys(str(item) for item in value if str(item)))
    return [str(value)]


def build_product_mode_result(
    *,
    mode: str = "today",
    current_date: str = "2026-06-17",
    monthly_contribution_eur: float | None = None,
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> ProductModeResult:
    mode = mode.lower().strip()
    if mode not in {"today", "week", "status"}:
        mode = "today"

    common_kwargs = {
        "current_date": current_date,
        "monthly_contribution_eur": monthly_contribution_eur,
    }

    components = [
        _call_builder(
            component_name="personal_finance_contribution_bridge",
            module_name="jarvis.runtime.personal_finance_contribution_bridge",
            builder_names=["build_personal_finance_contribution_bridge_result"],
            kwargs=common_kwargs,
            selected_keys=[
                "monthly_contribution_eur",
                "planned_monthly_contribution_eur",
                "normal_monthly_expenses_eur",
                "survival_monthly_expenses_eur",
                "emergency_fund_eur",
                "emergency_months_covered",
                "minimum_emergency_fund_eur",
                "ideal_emergency_fund_eur",
                "recommended_emergency_top_up_eur",
                "emergency_top_up_eur",
                "recommended_crypto_eur",
                "crypto_eur",
                "recommended_crypto_contribution_eur",
                "recommended_etf_fund_eur",
                "recommended_equity_eur",
                "etf_fund_eur",
                "recommended_individual_stock_eur",
                "individual_stock_eur",
                "full_allocation_blockers",
                "remaining_full_allocation_blockers",
            ],
        ),
        _call_builder(
            component_name="allocation_strategy_audit",
            module_name="jarvis.runtime.allocation_strategy_audit",
            builder_names=["build_allocation_strategy_data_coverage_audit_result"],
            kwargs=common_kwargs,
            selected_keys=[
                "full_allocation_blockers",
                "remaining_full_allocation_blockers",
                "weekly_router_blockers",
                "coverage_items",
            ],
        ),
        _call_builder(
            component_name="platform_weekly_action_packet",
            module_name="jarvis.runtime.platform_weekly_action_packet",
            builder_names=["build_platform_aware_weekly_action_packet_result"],
            kwargs=common_kwargs,
            selected_keys=[
                "monthly_contribution_eur",
                "emergency_top_up_eur",
                "crypto_eur",
                "etf_fund_eur",
                "individual_stock_eur",
                "weekly_actions",
                "actions",
            ],
        ),
        _call_builder(
            component_name="weekly_manual_buy_packet",
            module_name="jarvis.runtime.weekly_packet",
            builder_names=["build_weekly_manual_buy_packet_result"],
            kwargs={**common_kwargs, "weekly_budget_eur": None},
            selected_keys=[
                "weekly_budget_eur",
                "manual_actions",
                "actions",
                "crypto_amount_eur",
                "equity_amount_eur",
                "stock_amount_eur",
            ],
        ),
        _call_builder(
            component_name="platform_data_completeness_gate",
            module_name="jarvis.runtime.platform_data_completeness_gate",
            builder_names=["build_platform_data_completeness_gate_result"],
            kwargs=common_kwargs,
            selected_keys=[
                "lightyear_instrument_universe_ready",
                "crypto_facility_terms_ready",
                "legacy_migration_review_ready",
                "platform_data_ready",
            ],
        ),
        _call_builder(
            component_name="import_closure_safe_archive_plan",
            module_name="jarvis.runtime.import_closure_safe_archive_plan",
            builder_names=["build_import_closure_safe_archive_plan_result"],
            kwargs=common_kwargs,
            selected_keys=[
                "unresolved_local_import_count",
                "legacy_module_archive_candidate_count",
                "active_import_closure_count",
                "active_runtime_module_count",
                "active_versioned_module_count",
            ],
        ),
    ]

    safety_output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output

    unresolved_imports = _float_or_none(
        _first_value(components, ["unresolved_local_import_count"])
    )
    unresolved_import_count = int(unresolved_imports) if unresolved_imports is not None else None

    legacy_candidates = _float_or_none(
        _first_value(components, ["legacy_module_archive_candidate_count"])
    )
    legacy_module_archive_candidate_count = int(legacy_candidates) if legacy_candidates is not None else None

    monthly_contribution = _first_amount(
        components,
        ["monthly_contribution_eur", "planned_monthly_contribution_eur"],
    ) or _first_numeric_by_terms(
        components,
        ["contribution", "eur"],
        ["recommended", "crypto", "stock", "etf", "fund"],
    )

    emergency_fund = _first_amount(components, ["emergency_fund_eur"]) or _first_numeric_by_terms(
        components,
        ["emergency", "fund", "eur"],
        ["minimum", "ideal", "target", "top", "up", "months"],
    )

    emergency_months = _first_amount(components, ["emergency_months_covered"]) or _first_numeric_by_terms(
        components,
        ["emergency", "months"],
        [],
    )

    min_emergency = _first_amount(components, ["minimum_emergency_fund_eur"]) or _first_numeric_by_terms(
        components,
        ["minimum", "emergency"],
        ["months"],
    )

    ideal_emergency = _first_amount(components, ["ideal_emergency_fund_eur"]) or _first_numeric_by_terms(
        components,
        ["ideal", "emergency"],
        ["months"],
    )

    emergency_top_up = _first_amount(
        components,
        ["recommended_emergency_top_up_eur", "emergency_top_up_eur"],
    ) or _first_numeric_by_terms(
        components,
        ["emergency", "top"],
        ["months"],
    )

    crypto = _first_amount(
        components,
        [
            "recommended_crypto_eur",
            "recommended_crypto_contribution_eur",
            "crypto_eur",
            "crypto_amount_eur",
        ],
    ) or _first_numeric_by_terms(
        components,
        ["crypto"],
        ["market", "cost", "price", "facility", "ready"],
    )

    etf = _first_amount(
        components,
        [
            "recommended_etf_fund_eur",
            "recommended_equity_eur",
            "etf_fund_eur",
            "equity_amount_eur",
        ],
    ) or _first_numeric_by_terms(
        components,
        ["etf"],
        ["market", "cost", "price", "ready"],
    ) or _first_numeric_by_terms(
        components,
        ["fund"],
        ["emergency", "market", "cost", "price", "ready"],
    )

    stock = _first_amount(
        components,
        [
            "recommended_individual_stock_eur",
            "individual_stock_eur",
            "stock_amount_eur",
        ],
    ) or _first_numeric_by_terms(
        components,
        ["stock"],
        ["market", "cost", "price", "ready"],
    )

    full_allocation_blockers: list[str] = []
    for component in components:
        full_allocation_blockers.extend(
            _clean_list(
                _find_first(
                    component.selected_fields,
                    ["full_allocation_blockers", "remaining_full_allocation_blockers"],
                )
            )
        )
    for component in components:
        for blocker in component.blockers:
            key = _norm(blocker)
            if (
                "correlation" in key
                or "stock_specific" in key
                or "stock_specific_public_evidence" in key
            ):
                full_allocation_blockers.append(blocker)

    full_allocation_blockers = list(dict.fromkeys(full_allocation_blockers))

    component_blockers = [
        f"{component.name}: {blocker}"
        for component in components
        for blocker in component.blockers
        if blocker
    ]

    warnings = [
        "product mode is manual-only; Diogo performs any buy outside J.A.R.V.I.S.",
        "no broker, credentials, order, trade, or auto-approval path is enabled",
    ]
    warnings.extend(
        f"{component.name}: unavailable" for component in components if not component.available
    )

    blockers: list[str] = []
    if not safety_blocked:
        blockers.append("safety-check did not block execution")
    if unresolved_import_count not in (0, None):
        blockers.append(f"unresolved local imports: {unresolved_import_count}")

    product_ready = not blockers
    product_verdict = (
        "READY_FOR_MANUAL_USE"
        if product_ready
        else "REVIEW_REQUIRED_BEFORE_MANUAL_USE"
    )

    today_lines = [
        f"Product verdict: {product_verdict}",
        f"Safety: {'execution blocked' if safety_blocked else 'REVIEW REQUIRED'}",
        f"Emergency fund: {_money(emergency_fund)}"
        + (f" ({emergency_months:.2f} months)" if emergency_months is not None else ""),
        f"Minimum emergency target: {_money(min_emergency)}",
        f"Ideal emergency target: {_money(ideal_emergency)}",
        f"Monthly contribution detected: {_money(monthly_contribution)}",
        "Manual action today: review the week packet; do not execute inside J.A.R.V.I.S.",
    ]

    week_lines = [
        f"Monthly contribution: {_money(monthly_contribution)}",
        f"Emergency top-up: {_money(emergency_top_up)}",
        f"Crypto lane: {_money(crypto)}",
        f"ETF/fund lane: {_money(etf)}",
        f"Individual stock lane: {_money(stock)}",
        "Execution: manual-only outside J.A.R.V.I.S.",
    ]

    if full_allocation_blockers:
        week_lines.append("Full allocation still blocked by: " + ", ".join(full_allocation_blockers))
    else:
        week_lines.append("Full allocation blockers: none reported by active components")

    status_lines = [
        f"Active product mode: {mode}",
        f"Safety-check blocked execution: {safety_blocked}",
        f"Unresolved local imports: {unresolved_import_count}",
        f"Legacy module archive candidates: {legacy_module_archive_candidate_count}",
        f"Components available: {sum(1 for component in components if component.available)} / {len(components)}",
        f"Full allocation blockers: {', '.join(full_allocation_blockers) if full_allocation_blockers else 'none reported'}",
        f"Component blockers: {', '.join(component_blockers) if component_blockers else 'none'}",
    ]

    result = ProductModeResult(
        status=STATUS_READY if product_ready else STATUS_REVIEW_REQUIRED,
        mode=mode,
        current_date=current_date,
        product_verdict=product_verdict,
        product_ready_for_manual_use=product_ready,
        manual_approval_required=True,
        execution_forbidden=True,
        safety_check_blocked_execution=safety_blocked,
        unresolved_local_import_count=unresolved_import_count,
        legacy_module_archive_candidate_count=legacy_module_archive_candidate_count,
        monthly_contribution_eur=monthly_contribution,
        emergency_fund_eur=emergency_fund,
        emergency_months_covered=emergency_months,
        minimum_emergency_fund_eur=min_emergency,
        ideal_emergency_fund_eur=ideal_emergency,
        recommended_emergency_top_up_eur=emergency_top_up,
        recommended_crypto_eur=crypto,
        recommended_etf_fund_eur=etf,
        recommended_individual_stock_eur=stock,
        full_allocation_blockers=full_allocation_blockers,
        today_lines=today_lines,
        week_lines=week_lines,
        status_lines=status_lines,
        components=_component_data(components),
        deletion_performed=False,
        archive_performed=False,
        file_move_performed=False,
        runtime_behavior_mutation=False,
        allocation_mutation=False,
        approval_ticket_mutation=False,
        buy_request_created=False,
        broker_connection=False,
        credentials_used=False,
        private_account_data_ingestion=False,
        order_created=False,
        trade_executed=False,
        warnings=list(dict.fromkeys(warnings)),
        blockers=blockers,
        report_written=False,
        report_path=str(output_path),
    )

    if write_report:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        payload["report_written"] = True
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = ProductModeResult(**payload)

    return result


def format_product_mode(result: ProductModeResult) -> str:
    title = {
        "today": "J.A.R.V.I.S. TODAY",
        "week": "J.A.R.V.I.S. WEEK",
        "status": "J.A.R.V.I.S. STATUS",
    }[result.mode]

    if result.mode == "today":
        active_lines = result.today_lines
    elif result.mode == "week":
        active_lines = result.week_lines
    else:
        active_lines = result.status_lines

    lines = [
        title,
        f"status: {result.status}",
        f"verdict: {result.product_verdict}",
        f"current date: {result.current_date}",
        "",
        "SUMMARY:",
    ]
    lines.extend(f"- {line}" for line in active_lines)

    lines.extend(
        [
            "",
            "SAFETY:",
            f"- manual approval required: {result.manual_approval_required}",
            f"- execution forbidden: {result.execution_forbidden}",
            f"- safety-check blocked execution: {result.safety_check_blocked_execution}",
            f"- deletion performed: {result.deletion_performed}",
            f"- archive performed: {result.archive_performed}",
            f"- file move performed: {result.file_move_performed}",
            f"- runtime behavior mutation: {result.runtime_behavior_mutation}",
            f"- allocation mutation: {result.allocation_mutation}",
            f"- approval ticket mutation: {result.approval_ticket_mutation}",
            f"- buy request created: {result.buy_request_created}",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- private account data ingestion: {result.private_account_data_ingestion}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            "",
            "WARNINGS:",
        ]
    )
    lines.extend(f"- {warning}" for warning in result.warnings)
    lines.extend(["", "BLOCKERS:"])
    lines.extend(f"- {blocker}" for blocker in result.blockers or ["none"])
    lines.extend(["", f"report written: {result.report_written}", f"report path: {result.report_path}"])

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. product mode.")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--today", action="store_true")
    mode_group.add_argument("--week", action="store_true")
    mode_group.add_argument("--status", action="store_true")
    parser.add_argument("--product-mode", choices=["today", "week", "status"], default=None)
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--monthly-contribution-eur", type=float, default=None)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")

    args, _unknown = parser.parse_known_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    mode = args.product_mode or "today"
    if args.week:
        mode = "week"
    elif args.status:
        mode = "status"
    elif args.today:
        mode = "today"

    result = build_product_mode_result(
        mode=mode,
        current_date=args.current_date,
        monthly_contribution_eur=args.monthly_contribution_eur,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_product_mode(result))
    return 0 if not result.blockers else 1


__all__ = [
    "DEFAULT_OUTPUT_PATH",
    "STATUS_READY",
    "STATUS_REVIEW_REQUIRED",
    "ProductModeComponent",
    "ProductModeResult",
    "build_product_mode_result",
    "format_product_mode",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
