"""J.A.R.V.I.S. v81.0 correlation risk model.

Heuristic, brokerless, manual-only correlation/risk coverage for current holdings.
No broker connection, credentials, orders, trades, allocation mutation, or approval.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

from jarvis.runtime.safety import build_safety_check_console_output

STATUS_READY = "JARVIS_V81_0_CORRELATION_RISK_MODEL_READY_SAFE"
STATUS_REVIEW_REQUIRED = "JARVIS_V81_0_CORRELATION_RISK_MODEL_REVIEW_REQUIRED_SAFE"
MODEL_READY = "CORRELATION_RISK_MODEL_READY"
MODEL_REVIEW_REQUIRED = "CORRELATION_RISK_MODEL_REVIEW_REQUIRED"

DEFAULT_COST_BASIS_PATH = "jarvis/local/manual_cost_basis.local.json"
DEFAULT_PORTFOLIO_SNAPSHOT_PATH = "jarvis/local/manual_portfolio_snapshot.local.json"
DEFAULT_OUTPUT_PATH = "outputs/correlation_risk_model_latest.json"


@dataclass(frozen=True)
class CorrelationRiskModelResult:
    status: str
    model_status: str
    current_date: str
    correlation_model_ready: bool
    source_paths_checked: list[str]
    position_count: int
    classified_position_count: int
    total_market_value_eur: float
    exposure_weights: dict[str, float]
    concentration_notes: list[str]
    overlap_notes: list[str]
    missing_coverage: list[str]
    remaining_full_allocation_blockers: list[str]
    safety_check_blocked_execution: bool
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


def _norm(value: Any) -> str:
    return str(value or "").lower().replace("-", "_").replace(" ", "_")


def _as_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _walk_dicts(value: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if isinstance(value, Mapping):
        rows.append(dict(value))
        for child in value.values():
            rows.extend(_walk_dicts(child))
    elif isinstance(value, list):
        for child in value:
            rows.extend(_walk_dicts(child))
    return rows


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _position_identity(row: Mapping[str, Any]) -> str:
    keys = (
        "symbol", "ticker", "asset_symbol", "instrument_symbol",
        "id", "asset_id", "instrument_id", "name", "asset_name",
        "isin",
    )
    parts = [str(row.get(key, "")) for key in keys if row.get(key)]
    return " ".join(parts)


def _position_value(row: Mapping[str, Any]) -> float | None:
    value_keys = (
        "market_value_eur", "current_value_eur", "value_eur",
        "market_value", "current_value", "amount_eur",
    )
    for key in value_keys:
        value = _as_float(row.get(key))
        if value is not None and value > 0:
            return value
    return None


def _classify(identity: str) -> list[str]:
    text = _norm(identity)
    exposures: list[str] = []

    crypto_terms = ["btc", "bitcoin", "eth", "ethereum", "sol", "hype", "link", "avax", "near", "inj", "render", "tao"]
    if any(term in text for term in crypto_terms):
        exposures.append("crypto")

    if any(term in text for term in ["sxr8", "s&p", "sp500", "s&p500", "cspx", "vusa"]):
        exposures.extend(["equity", "us_large_cap"])

    if any(term in text for term in ["iemm", "emerging", "emim", "eimi"]):
        exposures.extend(["equity", "emerging_markets"])

    if any(term in text for term in ["xcha", "msci_world", "world", "lhvworld", "iwda", "swda"]):
        exposures.extend(["equity", "global_developed"])

    if any(term in text for term in ["is3q", "quality", "factor"]):
        exposures.extend(["equity", "quality_factor"])

    if any(term in text for term in ["msft", "microsoft", "aapl", "apple", "nvda", "nvidia", "googl", "alphabet", "amzn", "amazon"]):
        exposures.extend(["equity", "individual_stock", "us_large_cap"])

    if any(term in text for term in ["cash", "emergency", "savings"]):
        exposures.append("cash")

    return list(dict.fromkeys(exposures))


def _extract_positions(payloads: list[Any]) -> list[dict[str, Any]]:
    positions: list[dict[str, Any]] = []

    for payload in payloads:
        if payload is None:
            continue

        for row in _walk_dicts(payload):
            identity = _position_identity(row)
            value = _position_value(row)
            if identity and value is not None:
                exposures = _classify(identity)
                if exposures:
                    positions.append(
                        {
                            "identity": identity,
                            "market_value_eur": round(value, 2),
                            "exposures": exposures,
                        }
                    )

    deduped: dict[str, dict[str, Any]] = {}
    for pos in positions:
        key = _norm(pos["identity"])
        deduped[key] = pos

    return list(deduped.values())


def build_correlation_risk_model_result(
    *,
    current_date: str = "2026-06-17",
    cost_basis_path: str | Path = DEFAULT_COST_BASIS_PATH,
    portfolio_snapshot_path: str | Path = DEFAULT_PORTFOLIO_SNAPSHOT_PATH,
    write_report: bool = False,
    output_path: str | Path = DEFAULT_OUTPUT_PATH,
) -> CorrelationRiskModelResult:
    source_paths = [str(cost_basis_path), str(portfolio_snapshot_path)]
    payloads = [_load_json(Path(cost_basis_path)), _load_json(Path(portfolio_snapshot_path))]
    positions = _extract_positions(payloads)

    total = round(sum(float(pos["market_value_eur"]) for pos in positions), 2)
    exposure_values: dict[str, float] = {}

    for pos in positions:
        exposures = pos["exposures"]
        value = float(pos["market_value_eur"])
        for exposure in exposures:
            exposure_values[exposure] = exposure_values.get(exposure, 0.0) + value

    exposure_weights = {
        exposure: round(value / total, 4)
        for exposure, value in sorted(exposure_values.items())
        if total > 0
    }

    missing: list[str] = []
    if not positions:
        missing.append("classified_current_holdings")

    if "equity" not in exposure_weights:
        missing.append("equity_exposure_classification")

    if "crypto" not in exposure_weights:
        missing.append("crypto_exposure_classification")

    overlap_notes: list[str] = []
    if "global_developed" in exposure_weights and "us_large_cap" in exposure_weights:
        overlap_notes.append("global developed equity and US large-cap exposure overlap")
    if "quality_factor" in exposure_weights and "global_developed" in exposure_weights:
        overlap_notes.append("quality factor ETF likely overlaps with global developed equity")
    if "individual_stock" in exposure_weights and "us_large_cap" in exposure_weights:
        overlap_notes.append("individual US stocks overlap with US large-cap equity exposure")

    concentration_notes: list[str] = []
    for exposure, weight in exposure_weights.items():
        if weight >= 0.60:
            concentration_notes.append(f"{exposure} exposure is high at {weight:.0%}")
    if exposure_weights.get("crypto", 0.0) >= 0.20:
        concentration_notes.append(f"crypto exposure is high at {exposure_weights['crypto']:.0%}")

    safety_output = build_safety_check_console_output()
    safety_blocked = "BLOCKED:" in safety_output and "No execution action was taken" in safety_output

    blockers: list[str] = []
    if missing:
        blockers.append("missing coverage: " + ", ".join(missing))
    if not safety_blocked:
        blockers.append("safety-check did not block execution")

    ready = not blockers

    warnings = [
        "heuristic exposure model; not a broker feed and not a trading engine",
        "correlation model is sufficient for manual allocation gating, not precise portfolio optimization",
    ]

    result = CorrelationRiskModelResult(
        status=STATUS_READY if ready else STATUS_REVIEW_REQUIRED,
        model_status=MODEL_READY if ready else MODEL_REVIEW_REQUIRED,
        current_date=current_date,
        correlation_model_ready=ready,
        source_paths_checked=source_paths,
        position_count=len(positions),
        classified_position_count=len(positions),
        total_market_value_eur=total,
        exposure_weights=exposure_weights,
        concentration_notes=concentration_notes,
        overlap_notes=overlap_notes,
        missing_coverage=missing,
        remaining_full_allocation_blockers=[] if ready else ["correlation_risk_model"],
        safety_check_blocked_execution=safety_blocked,
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
        warnings=warnings,
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
        result = CorrelationRiskModelResult(**payload)

    return result


def format_correlation_risk_model(result: CorrelationRiskModelResult) -> str:
    lines = [
        "J.A.R.V.I.S. CORRELATION RISK MODEL",
        f"status: {result.status}",
        f"model status: {result.model_status}",
        f"current date: {result.current_date}",
        f"correlation model ready: {result.correlation_model_ready}",
        f"positions classified: {result.classified_position_count}",
        f"total market value EUR: {result.total_market_value_eur:.2f}",
        "exposure weights:",
    ]

    for exposure, weight in result.exposure_weights.items():
        lines.append(f"- {exposure}: {weight:.1%}")

    lines.append("overlap notes:")
    lines.extend(f"- {note}" for note in result.overlap_notes or ["none"])
    lines.append("concentration notes:")
    lines.extend(f"- {note}" for note in result.concentration_notes or ["none"])
    lines.append("missing coverage:")
    lines.extend(f"- {item}" for item in result.missing_coverage or ["none"])
    lines.append("remaining full-allocation blockers:")
    lines.extend(f"- {item}" for item in result.remaining_full_allocation_blockers or ["none"])

    lines.extend(
        [
            "Safety:",
            f"- manual approval required: True",
            f"- execution forbidden: True",
            f"- safety-check blocked execution: {result.safety_check_blocked_execution}",
            f"- buy request created: {result.buy_request_created}",
            f"- broker connection: {result.broker_connection}",
            f"- credentials used: {result.credentials_used}",
            f"- order created: {result.order_created}",
            f"- trade executed: {result.trade_executed}",
            "blockers:",
        ]
    )
    lines.extend(f"- {blocker}" for blocker in result.blockers or ["none"])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run J.A.R.V.I.S. correlation risk model.")
    parser.add_argument("--correlation-risk-model", action="store_true")
    parser.add_argument("--current-date", default="2026-06-17")
    parser.add_argument("--cost-basis-path", default=DEFAULT_COST_BASIS_PATH)
    parser.add_argument("--portfolio-snapshot-path", default=DEFAULT_PORTFOLIO_SNAPSHOT_PATH)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--output-path", default=DEFAULT_OUTPUT_PATH)
    parser.add_argument("--safety-check", action="store_true")
    args = parser.parse_args(argv)

    if args.safety_check:
        print(build_safety_check_console_output())
        return 0

    result = build_correlation_risk_model_result(
        current_date=args.current_date,
        cost_basis_path=args.cost_basis_path,
        portfolio_snapshot_path=args.portfolio_snapshot_path,
        write_report=args.write_report,
        output_path=args.output_path,
    )
    print(format_correlation_risk_model(result))
    return 0 if not result.blockers else 1


if __name__ == "__main__":
    raise SystemExit(main())
