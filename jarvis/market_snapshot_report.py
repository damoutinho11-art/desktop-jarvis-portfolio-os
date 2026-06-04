"""Readable local market snapshot report."""

from __future__ import annotations

from pathlib import Path

from .market_data_loader import load_market_data
from .risk_metrics import RiskMetricResult, compute_market_risk_metrics


def _format_percent(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.2f}%"


def build_market_snapshot_report(metrics: list[RiskMetricResult]) -> str:
    lines = [
        "J.A.R.V.I.S. Market Data Fixture Report",
        "Read-only local fixture. No recommendations generated.",
    ]
    for metric in metrics:
        lines.extend(
            [
                "",
                f"asset_id: {metric.asset_id}",
                f"currency: {metric.currency}",
                f"latest_price: {metric.latest_price:.4f}",
                f"return_1m: {_format_percent(metric.return_1m)}",
                f"return_3m: {_format_percent(metric.return_3m)}",
                f"return_6m: {_format_percent(metric.return_6m)}",
                f"return_12m: {_format_percent(metric.return_12m)}",
                f"annualized_volatility: {_format_percent(metric.annualized_volatility)}",
                f"max_drawdown: {_format_percent(metric.max_drawdown)}",
                f"distance_from_high: {_format_percent(metric.distance_from_high)}",
                f"data_points: {metric.data_points}",
                f"oldest_date: {metric.oldest_date}",
                f"latest_date: {metric.latest_date}",
                "warnings:",
            ]
        )
        if metric.warnings:
            lines.extend(f"- {warning}" for warning in metric.warnings)
        else:
            lines.append("- none")
    lines.append("")
    lines.append("No trades executed.")
    return "\n".join(lines)


def report_market_snapshot(path: str | Path) -> str:
    snapshot = load_market_data(path)
    return build_market_snapshot_report(compute_market_risk_metrics(snapshot))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Report deterministic metrics from local market data fixtures.")
    parser.add_argument("market_data_path", nargs="?", default="jarvis/data/market_data.example.json")
    args = parser.parse_args()
    print(report_market_snapshot(args.market_data_path))


if __name__ == "__main__":
    main()
