"""J.A.R.V.I.S. v157.0 FinanceDatabase read-only universe adapter."""

from __future__ import annotations

import argparse
import importlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

STATUS_READY = "JARVIS_V157_0_FINANCEDATABASE_UNIVERSE_ADAPTER_READY_SAFE"
DEFAULT_OUTPUT_PATH = "outputs/finance_database_universe_latest.json"
SOURCE_NAME = "FinanceDatabase"

ASSET_CLASS_FACTORIES: tuple[tuple[str, tuple[str, ...], str], ...] = (
    ("equities", ("Equities",), "equity"),
    ("etfs_funds", ("ETFs", "Funds"), "fund"),
    ("indices", ("Indices",), "index"),
    ("currencies", ("Currencies",), "currency"),
    ("crypto", ("Cryptos", "Cryptocurrencies"), "crypto"),
    ("money_markets", ("Moneymarkets", "MoneyMarkets", "MoneyMarket"), "money_market"),
)

SYMBOL_KEYS = ("symbol", "ticker", "code", "id", "isin")
NAME_KEYS = ("name", "short_name", "long_name", "description", "title")
EXCHANGE_KEYS = ("exchange", "exchange_code", "mic", "market")
COUNTRY_KEYS = ("country", "country_name", "domicile")
CURRENCY_KEYS = ("currency", "currency_code", "quote_currency")
SECTOR_KEYS = ("sector", "category", "industry", "asset_class", "family")


@dataclass(frozen=True)
class FinanceDatabaseInstrument:
    symbol: str
    name: str | None
    asset_type: str
    exchange: str | None
    country: str | None
    currency: str | None
    sector_category: str | None
    source: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class FinanceDatabaseUniverseResult:
    status: str
    dependency_available: bool
    universe_ready: bool
    price_truth: bool
    metadata_counts: dict[str, int]
    sample_instruments: list[dict[str, Any]]
    blockers: list[str]
    warnings: list[str]
    report_written: bool
    report_path: str
    manual_review_required: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _first_value(record: Mapping[str, Any], keys: Iterable[str]) -> Any:
    lowered = {str(key).lower(): value for key, value in record.items()}
    for key in keys:
        if key in record and record[key] not in (None, "", [], {}):
            return record[key]
        value = lowered.get(key.lower())
        if value not in (None, "", [], {}):
            return value
    return None


def _clean_text(value: Any) -> str | None:
    if value in (None, "", [], {}):
        return None
    text = str(value).strip()
    return text or None


def _records_from_table(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if isinstance(value, list):
        return [dict(item) for item in value if isinstance(item, Mapping)]
    if isinstance(value, Mapping):
        if all(isinstance(item, Mapping) for item in value.values()):
            rows = []
            for key, item in value.items():
                row = dict(item)
                row.setdefault("symbol", key)
                rows.append(row)
            return rows
        return [dict(value)]
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        try:
            records = to_dict(orient="records")
            if isinstance(records, list):
                return [dict(item) for item in records if isinstance(item, Mapping)]
        except TypeError:
            pass
        try:
            data = to_dict()
            return _records_from_table(data)
        except Exception:
            return []
    return []


def normalize_universe_record(record: Mapping[str, Any], *, asset_type: str, source: str = SOURCE_NAME) -> dict[str, Any] | None:
    symbol = _clean_text(_first_value(record, SYMBOL_KEYS))
    if not symbol:
        return None
    instrument = FinanceDatabaseInstrument(
        symbol=symbol.upper(),
        name=_clean_text(_first_value(record, NAME_KEYS)),
        asset_type=asset_type,
        exchange=_clean_text(_first_value(record, EXCHANGE_KEYS)),
        country=_clean_text(_first_value(record, COUNTRY_KEYS)),
        currency=_clean_text(_first_value(record, CURRENCY_KEYS)),
        sector_category=_clean_text(_first_value(record, SECTOR_KEYS)),
        source=source,
    )
    return instrument.to_dict()


def normalize_fixture_universe(fixture: Mapping[str, Any]) -> tuple[dict[str, int], list[dict[str, Any]]]:
    counts: dict[str, int] = {key: 0 for key, _, _ in ASSET_CLASS_FACTORIES}
    samples: list[dict[str, Any]] = []
    for class_key, _factories, default_type in ASSET_CLASS_FACTORIES:
        records = _records_from_table(fixture.get(class_key, []))
        counts[class_key] = len(records)
        for record in records:
            normalized = normalize_universe_record(
                record,
                asset_type=str(record.get("asset_type") or default_type),
                source=str(record.get("source") or SOURCE_NAME),
            )
            if normalized:
                samples.append(normalized)
    return counts, samples


def _load_financedatabase_module() -> Any | None:
    for module_name in ("financedatabase", "FinanceDatabase"):
        try:
            return importlib.import_module(module_name)
        except ImportError:
            continue
    return None


def _select_rows(factory: Any) -> list[dict[str, Any]]:
    try:
        instance = factory()
    except Exception:
        return []
    for method_name in ("select", "show_options", "to_pandas"):
        method = getattr(instance, method_name, None)
        if not callable(method):
            continue
        try:
            rows = _records_from_table(method())
        except Exception:
            rows = []
        if rows:
            return rows
    return _records_from_table(instance)


def _read_financedatabase_universe(module: Any) -> tuple[dict[str, int], list[dict[str, Any]], list[str]]:
    counts: dict[str, int] = {key: 0 for key, _, _ in ASSET_CLASS_FACTORIES}
    samples: list[dict[str, Any]] = []
    warnings: list[str] = []
    for class_key, factory_names, default_type in ASSET_CLASS_FACTORIES:
        class_rows: list[dict[str, Any]] = []
        for factory_name in factory_names:
            factory = getattr(module, factory_name, None)
            if factory is None:
                continue
            rows = _select_rows(factory)
            class_rows.extend(rows)
        counts[class_key] = len(class_rows)
        if not class_rows:
            warnings.append(f"{class_key} metadata not available from installed FinanceDatabase package")
        for record in class_rows[:10]:
            normalized = normalize_universe_record(record, asset_type=default_type)
            if normalized:
                samples.append(normalized)
    return counts, samples, warnings


def build_finance_database_universe_result(
    *,
    fixture_universe: Mapping[str, Any] | None = None,
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> FinanceDatabaseUniverseResult:
    warnings = [
        "FinanceDatabase is read-only metadata context, not price truth",
        "manual review remains required before using any candidate",
    ]
    dependency_available = False
    if fixture_universe is not None:
        counts, samples = normalize_fixture_universe(fixture_universe)
        dependency_available = True
        warnings.append("fixture universe supplied for deterministic normalization")
    else:
        module = _load_financedatabase_module()
        if module is None:
            counts = {key: 0 for key, _, _ in ASSET_CLASS_FACTORIES}
            samples = []
            warnings.append("optional dependency not installed")
        else:
            dependency_available = True
            counts, samples, package_warnings = _read_financedatabase_universe(module)
            warnings.extend(package_warnings)

    universe_ready = dependency_available and bool(samples)
    result = FinanceDatabaseUniverseResult(
        status=STATUS_READY,
        dependency_available=dependency_available,
        universe_ready=universe_ready,
        price_truth=False,
        metadata_counts=counts,
        sample_instruments=samples[:25],
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


def format_finance_database_universe(result: FinanceDatabaseUniverseResult) -> str:
    lines = [
        "J.A.R.V.I.S. FINANCEDATABASE UNIVERSE ADAPTER",
        f"status: {result.status}",
        f"dependency available: {result.dependency_available}",
        f"universe ready: {result.universe_ready}",
        f"FinanceDatabase price truth: {result.price_truth}",
        f"manual review required: {result.manual_review_required}",
        "",
        "METADATA COUNTS:",
    ]
    for key, count in result.metadata_counts.items():
        lines.append(f"- {key}: {count}")
    lines.extend(["", "SAMPLE INSTRUMENTS:"])
    for item in result.sample_instruments[:10]:
        lines.append(
            f"- {item.get('symbol')}: {item.get('name') or 'n/a'}; type={item.get('asset_type')}; "
            f"exchange={item.get('exchange') or 'n/a'}; country={item.get('country') or 'n/a'}; "
            f"currency={item.get('currency') or 'n/a'}; category={item.get('sector_category') or 'n/a'}; source={item.get('source')}"
        )
    if not result.sample_instruments:
        lines.append("- none")
    lines.extend(["", "WARNINGS:"])
    lines.extend(f"- {item}" for item in result.warnings or ["none"])
    lines.extend(["", "BLOCKERS:"])
    lines.extend(f"- {item}" for item in result.blockers or ["none"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect optional FinanceDatabase universe metadata.")
    parser.add_argument("--finance-database-universe", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    args = parser.parse_args(argv)
    result = build_finance_database_universe_result(write_report=args.write_report, output_path=args.output_path)
    print(format_finance_database_universe(result))
    return 0


__all__ = [
    "STATUS_READY",
    "FinanceDatabaseUniverseResult",
    "normalize_universe_record",
    "normalize_fixture_universe",
    "build_finance_database_universe_result",
    "format_finance_database_universe",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
