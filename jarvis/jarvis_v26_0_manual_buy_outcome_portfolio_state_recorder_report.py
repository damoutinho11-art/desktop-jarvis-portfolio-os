"""Report CLI for J.A.R.V.I.S. v26.0 manual buy outcome portfolio-state recorder."""

from __future__ import annotations

import argparse
import json

from jarvis.jarvis_v26_0_manual_buy_outcome_portfolio_state_recorder import (
    CONFIRMATION_PHRASE,
    DEFAULT_APPROVAL_TICKET_PATH,
    DEFAULT_CONFIRMATION_LOG_PATH,
    DEFAULT_PORTFOLIO_STATE_PATH,
    build_manual_buy_outcome_portfolio_state_recorder_result,
    format_manual_buy_outcome_portfolio_state_recorder,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Report manual-buy portfolio-state recorder status.")
    parser.add_argument("--asset", default="btc")
    parser.add_argument("--lane", default="crypto", choices=["crypto", "stock_fund_etf"])
    parser.add_argument("--amount-eur", type=float, default=41.54)
    parser.add_argument("--execution-date", default=None)
    parser.add_argument("--confirmation-phrase", default=CONFIRMATION_PHRASE)
    parser.add_argument("--approval-ticket-path", default=DEFAULT_APPROVAL_TICKET_PATH)
    parser.add_argument("--portfolio-state-path", default=DEFAULT_PORTFOLIO_STATE_PATH)
    parser.add_argument("--confirmation-log-path", default=DEFAULT_CONFIRMATION_LOG_PATH)
    parser.add_argument("--write-state", action="store_true")
    args = parser.parse_args(argv)

    result = build_manual_buy_outcome_portfolio_state_recorder_result(
        asset=args.asset,
        lane=args.lane,
        amount_eur=args.amount_eur,
        execution_date=args.execution_date,
        confirmation_phrase=args.confirmation_phrase,
        approval_ticket_path=args.approval_ticket_path,
        portfolio_state_path=args.portfolio_state_path,
        confirmation_log_path=args.confirmation_log_path,
        write_state=args.write_state,
    )

    print("# J.A.R.V.I.S. v26.0 Manual Buy Outcome Portfolio-State Recorder")
    print()
    print(f"status: {result.status}")
    print(f"recorder status: {result.recorder_status}")
    print(f"asset: {result.asset}")
    print(f"lane: {result.lane}")
    print(f"amount eur: {result.amount_eur:,.2f}")
    print(f"execution date: {result.execution_date}")
    print(f"approval ticket loaded: {result.approval_ticket_loaded}")
    print(f"portfolio state loaded: {result.portfolio_state_loaded}")
    print(f"confirmation phrase valid: {result.confirmation_phrase_valid}")
    print(f"ticket match: {result.ticket_match}")
    print(f"portfolio state written: {result.portfolio_state_written}")
    print(f"confirmation logged: {result.confirmation_logged}")
    print(f"portfolio state mutation: {result.portfolio_state_mutation}")
    print(f"approval ticket mutation: {result.approval_ticket_mutation}")
    print(f"buy request created: {result.buy_request_created}")
    print(f"broker connection forbidden: {result.broker_connection_forbidden}")
    print(f"credentials forbidden: {result.credentials_forbidden}")
    print(f"private account data ingestion forbidden: {result.private_account_data_ingestion_forbidden}")
    print(f"order creation forbidden: {result.order_creation_forbidden}")
    print(f"no trades executed: {result.no_trades_executed}")
    print(f"blockers: {', '.join(result.blockers) if result.blockers else 'none'}")
    print(f"warnings: {', '.join(result.warnings) if result.warnings else 'none'}")
    print()
    print("## Console Output")
    print()
    print("```text")
    print(format_manual_buy_outcome_portfolio_state_recorder(result))
    print("```")
    print()
    print("## Result JSON")
    print()
    print("```json")
    print(json.dumps(result.to_dict(), indent=2, sort_keys=True))
    print("```")

    return 0 if not result.status.endswith("_BLOCKED_SAFE") else 1


if __name__ == "__main__":
    raise SystemExit(main())