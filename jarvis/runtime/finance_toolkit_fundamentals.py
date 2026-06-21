"""J.A.R.V.I.S. v158.0 FinanceToolkit read-only fundamentals adapter."""

from __future__ import annotations

import argparse
import importlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

STATUS_READY = "JARVIS_V158_0_FINANCETOOLKIT_FUNDAMENTAL_ANALYSIS_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/finance_toolkit_fundamentals_latest.json"
SOURCE_NAME = "FinanceToolkit"

SECTION_KEYS = (
    "profitability",
    "solvency",
    "valuation",
    "growth",
    "cash_flow_quality",
    "income_statement_summary",
    "balance_sheet_summary",
    "ratio_summary",
)


@dataclass(frozen=True)
class FinanceToolkitFundamentalsResult:
    status: str
    dependency_available: bool
    fundamentals_ready: bool
    selected_symbols: list[str]
    context_label: str
    fundamental_context: dict[str, dict[str, Any]]
    fundamental_notes: list[str]
    risk_notes: list[str]
    blockers: list[str]
    warnings: list[str]
    report_written: bool
    report_path: str
    manual_review_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_financetoolkit_module() -> Any | None:
    for module_name in ("financetoolkit", "FinanceToolkit"):
        try:
            return importlib.import_module(module_name)
        except ImportError:
            continue
    return None


def _as_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, Mapping):
        return dict(value)
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        try:
            data = to_dict()
            return dict(data) if isinstance(data, Mapping) else {}
        except Exception:
            return {}
    return {}


def _clean_symbol(value: Any) -> str | None:
    if value in (None, "", [], {}):
        return None
    text = str(value).strip().upper()
    return text or None


def _to_number(value: Any) -> float | int | str | None:
    if value in (None, "", [], {}):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    if number.is_integer():
        return int(number)
    return round(number, 4)


def _normalize_section(value: Any) -> dict[str, Any]:
    data = _as_mapping(value)
    normalized: dict[str, Any] = {}
    for key, item in data.items():
        if isinstance(item, Mapping):
            nested = {str(nested_key): _to_number(nested_value) for nested_key, nested_value in item.items()}
            normalized[str(key)] = {k: v for k, v in nested.items() if v is not None}
        else:
            clean = _to_number(item)
            if clean is not None:
                normalized[str(key)] = clean
    return normalized


def normalize_fundamental_record(symbol: str, record: Mapping[str, Any], *, source: str = SOURCE_NAME) -> dict[str, Any]:
    normalized: dict[str, Any] = {"symbol": symbol.upper(), "source": source}
    for section in SECTION_KEYS:
        normalized[section] = _normalize_section(record.get(section, {}))
    return normalized


def normalize_fixture_fundamentals(fixture: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    raw_records = fixture.get("symbols", fixture)
    if not isinstance(raw_records, Mapping):
        return records
    for raw_symbol, raw_record in raw_records.items():
        symbol = _clean_symbol(raw_symbol)
        if not symbol or not isinstance(raw_record, Mapping):
            continue
        records[symbol] = normalize_fundamental_record(symbol, raw_record, source=str(raw_record.get("source") or SOURCE_NAME))
    return records


def _extract_from_toolkit_instance(instance: Any, symbols: list[str]) -> dict[str, dict[str, Any]]:
    method_map = {
        "profitability": ("ratios.collect_profitability_ratios", "get_profitability_ratios"),
        "solvency": ("ratios.collect_solvency_ratios", "get_solvency_ratios"),
        "valuation": ("ratios.collect_valuation_ratios", "get_valuation_ratios"),
        "growth": ("models.get_growth_rates", "get_growth_rates"),
        "cash_flow_quality": ("ratios.collect_cash_flow_ratios", "get_cash_flow_ratios"),
        "income_statement_summary": ("get_income_statement",),
        "balance_sheet_summary": ("get_balance_sheet_statement", "get_balance_sheet"),
        "ratio_summary": ("ratios.collect_all_ratios", "get_ratios"),
    }
    per_symbol = {symbol: {section: {} for section in SECTION_KEYS} for symbol in symbols}

    def resolve(path: str) -> Any:
        current = instance
        for part in path.split("."):
            current = getattr(current, part, None)
            if current is None:
                return None
        return current

    for section, candidates in method_map.items():
        table: Any = None
        for method_name in candidates:
            method = resolve(method_name)
            if not callable(method):
                continue
            try:
                table = method()
            except Exception:
                table = None
            if table is not None:
                break
        data = _as_mapping(table)
        if not data:
            continue
        for symbol in symbols:
            symbol_data = data.get(symbol) or data.get(symbol.upper()) or data.get(symbol.lower())
            if isinstance(symbol_data, Mapping):
                per_symbol[symbol][section] = _normalize_section(symbol_data)
    return {
        symbol: normalize_fundamental_record(symbol, record)
        for symbol, record in per_symbol.items()
        if any(record.get(section) for section in SECTION_KEYS)
    }


def _read_financetoolkit_fundamentals(module: Any, symbols: list[str]) -> tuple[dict[str, dict[str, Any]], list[str]]:
    warnings: list[str] = []
    toolkit_factory = getattr(module, "Toolkit", None)
    if toolkit_factory is None:
        return {}, ["FinanceToolkit Toolkit class not found"]
    if not symbols:
        return {}, ["no selected symbols supplied for FinanceToolkit fundamentals"]
    try:
        instance = toolkit_factory(tickers=symbols)
    except TypeError:
        try:
            instance = toolkit_factory(symbols)
        except Exception as exc:
            return {}, [f"FinanceToolkit initialization failed safely: {exc}"]
    except Exception as exc:
        return {}, [f"FinanceToolkit initialization failed safely: {exc}"]
    records = _extract_from_toolkit_instance(instance, symbols)
    if not records:
        warnings.append("FinanceToolkit returned no normalizable fundamentals")
    return records, warnings


def _notes(records: Mapping[str, Mapping[str, Any]]) -> tuple[list[str], list[str]]:
    fundamental_notes: list[str] = []
    risk_notes: list[str] = []
    for symbol, record in sorted(records.items()):
        populated = [section for section in SECTION_KEYS if record.get(section)]
        if populated:
            fundamental_notes.append(f"{symbol}: fundamental context available for {', '.join(populated)}")
        else:
            risk_notes.append(f"{symbol}: no normalized fundamental metrics available")
        if not record.get("cash_flow_quality"):
            risk_notes.append(f"{symbol}: cash flow quality context missing")
        if not record.get("solvency"):
            risk_notes.append(f"{symbol}: solvency context missing")
    return list(dict.fromkeys(fundamental_notes)), list(dict.fromkeys(risk_notes))


def build_finance_toolkit_fundamentals_result(
    *,
    symbols: list[str] | None = None,
    fixture_fundamentals: Mapping[str, Any] | None = None,
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> FinanceToolkitFundamentalsResult:
    selected = [symbol for symbol in (_clean_symbol(item) for item in (symbols or [])) if symbol]
    warnings = [
        "FinanceToolkit fundamentals are context for manual review",
        "no private access is read or required by this adapter",
    ]
    dependency_available = False
    if fixture_fundamentals is not None:
        dependency_available = True
        records = normalize_fixture_fundamentals(fixture_fundamentals)
        if not selected:
            selected = sorted(records)
        warnings.append("fixture fundamentals supplied for deterministic normalization")
    else:
        module = _load_financetoolkit_module()
        if module is None:
            records = {}
            warnings.append("optional dependency not installed")
        else:
            dependency_available = True
            records, package_warnings = _read_financetoolkit_fundamentals(module, selected)
            warnings.extend(package_warnings)

    if selected:
        records = {symbol: record for symbol, record in records.items() if symbol in selected}
    fundamental_notes, risk_notes = _notes(records)
    if not records and selected:
        risk_notes.append("selected symbols have no normalized fundamental context yet")

    result = FinanceToolkitFundamentalsResult(
        status=STATUS_READY,
        dependency_available=dependency_available,
        fundamentals_ready=bool(records),
        selected_symbols=selected,
        context_label="fundamental context for manual review",
        fundamental_context=dict(records),
        fundamental_notes=fundamental_notes,
        risk_notes=risk_notes,
        blockers=[],
        warnings=list(dict.fromkeys(warnings)),
        report_written=bool(write_report),
        report_path=str(output_path),
        manual_review_required=True,
    )
    if write_report:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        Path(output_path).write_text(json.dumps(result.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def format_finance_toolkit_fundamentals(result: FinanceToolkitFundamentalsResult) -> str:
    lines = [
        "J.A.R.V.I.S. FINANCETOOLKIT FUNDAMENTAL ANALYSIS",
        f"status: {result.status}",
        f"dependency available: {result.dependency_available}",
        f"fundamentals ready: {result.fundamentals_ready}",
        f"selected symbols: {', '.join(result.selected_symbols) if result.selected_symbols else 'none'}",
        f"context: {result.context_label}",
        f"manual review required: {result.manual_review_required}",
        "",
        "FUNDAMENTAL NOTES:",
    ]
    lines.extend(f"- {item}" for item in result.fundamental_notes or ["none"])
    lines.extend(["", "RISK NOTES:"])
    lines.extend(f"- {item}" for item in result.risk_notes or ["none"])
    lines.extend(["", "SYMBOL CONTEXT:"])
    if result.fundamental_context:
        for symbol, record in result.fundamental_context.items():
            populated = [section for section in SECTION_KEYS if record.get(section)]
            lines.append(f"- {symbol}: {', '.join(populated) if populated else 'no sections'}")
    else:
        lines.append("- none")
    lines.extend(["", "WARNINGS:"])
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.extend(["", "BLOCKERS:"])
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect optional FinanceToolkit fundamental context.")
    parser.add_argument("--finance-toolkit-fundamentals", action="store_true")
    parser.add_argument("--symbols", nargs="*", default=[])
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)
    result = build_finance_toolkit_fundamentals_result(
        symbols=args.symbols,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_finance_toolkit_fundamentals(result))
    return 0


__all__ = [
    "STATUS_READY",
    "SECTION_KEYS",
    "FinanceToolkitFundamentalsResult",
    "normalize_fundamental_record",
    "normalize_fixture_fundamentals",
    "build_finance_toolkit_fundamentals_result",
    "format_finance_toolkit_fundamentals",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())

