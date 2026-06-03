# J.A.R.V.I.S. Portfolio OS v0

A safe, local, manual-approval portfolio allocation engine.

This project recommends weekly investment allocations against a fixed portfolio target. It does not connect to brokers, does not execute trades, does not use API keys, and does not make network calls.

## Safety Constitution

J.A.R.V.I.S. Portfolio OS v0 follows these rules:

- Manual approval required.
- No auto-trading.
- No leverage.
- No options.
- No futures.
- No staking yet.
- No use of emergency fund.
- No automatic selling.
- No random new assets.
- Emergency fund is tracked but excluded from allocation calculations.

Every report includes:

> Manual approval required. No trades executed.

## Files

- `jarvis_constitution.json` - fixed rules, target weights, and minimum efficient buy sizes.
- `portfolio_state.json` - current local portfolio state and weekly budget.
- `allocation_engine.py` - deterministic allocation logic.
- `etf_universe.json` - offline manual ETF scoring inputs.
- `etf_scoring.py` - ETF sleeve scoring formula.
- `voice_adapter.py` - optional local voice output via `pyttsx3`, with print fallback.
- `run_weekly_allocation.py` - command-line runner.
- `review_ticket.py` - manual approval ticket review and decision logger.
- `update_state.py` - safe portfolio state updater with backup creation.
- `status.py` - read-only portfolio status command.

## Readiness Gates

The engine reports two allocation views:

- Ideal allocation: target-weight recommendation before platform readiness gates.
- Executable allocation: current-week recommendation after platform readiness and minimum efficient buy checks.

If a route is not ready, or a suggested buy is below its minimum efficient buy size, the amount enters an executable fallback pool. The pool is reallocated to ready, underweight sleeves where minimum buy sizes and risk limits allow it. If no valid executable sleeve is available, the remainder goes to `tactical_reserve`.

Crypto fallback follows hard caps:

- BTC target: 10%
- BTC max: 15%
- Total crypto hard max: 22.5%
- HYPE + TAO combined max: 7.5%
- BTC fallback max: 40% of the weekly budget
- Total crypto-like buys max: 50% of the weekly budget
- No automatic selling

## Portfolio Modes

Each weekly report includes a portfolio mode:

- `construction_mode` for small or mostly empty portfolios.
- `transition_mode` while platform routes, legacy holdings, or legacy cash cleanup are incomplete.
- `normal_weekly_mode` when platforms are ready, cleanup is complete, and sleeves are within bands.
- `rebalance_watch_mode` when risk bands are breached, while still blocking automatic sells.

## Legacy Holdings

Old LHV Growth Account positions are tracked separately under `legacy_holdings`.
Known numeric values are included in investable value by mapping them into the closest current sleeve. Unknown or pending values should stay `null`; they are shown as `unknown/pending` and excluded from calculations.

J.A.R.V.I.S. does not recommend new buys into legacy instruments and does not recommend selling them without explicit user approval.

## Run

```bash
python run_weekly_allocation.py
```

On Windows, depending on your Python launcher:

```bash
py run_weekly_allocation.py
```

Running the weekly allocation creates a manual approval ticket in `outputs/approval_ticket_latest.json` and a dated copy such as `outputs/approval_ticket_2026-06-04.json`.
It also appends a compact audit record to `outputs/decision_log.jsonl` without overwriting prior entries.

Review the latest approval ticket:

```bash
python review_ticket.py
```

Record a manual decision without executing trades:

```bash
python review_ticket.py --decision approved --note "Manual review complete."
```

Decisions are saved to `outputs/approval_ticket_reviewed_latest.json` and appended to `outputs/approval_decisions.jsonl`.
Use `--test` for dry-run review checks; test decisions append to `outputs/approval_decisions_test.jsonl` and mark the reviewed copy with `test_decision: true`.

Approval tickets split decision context into:

- `blocked_actions` for recommendations blocked by platform, routing, minimum, or risk rules.
- `fallback_actions` for substitute recommendations such as BTC fallback.
- `reserve_actions` for money intentionally held in `tactical_reserve`.

Update local portfolio state with an automatic backup:

```bash
python update_state.py --set-platform lightyear_ready=true
python update_state.py --set-holding btc=61.54
python update_state.py --set-legacy lhv_growth_cash_pending_settlement=1271.57
```

Print read-only portfolio status:

```bash
python status.py
```

## Tests

Run the v0.1 stability checkpoint:

```bash
python test_jarvis_v01.py
```

Run the v0.2 ETF scoring checkpoint:

```bash
python test_jarvis_v02.py
```

Run the state updater tests:

```bash
python test_update_state.py
```

Run the status command tests:

```bash
python test_status.py
```

## ETF Scoring

J.A.R.V.I.S. v0.2 scores ETF sleeves from manual inputs only. It makes no network calls and uses no live market data.

ETF score = 45% allocation gap + 25% momentum + 15% valuation risk + 10% inverse concentration penalty + 5% fee/liquidity.

ETF scoring only affects ideal ETF sleeve priority. Platform readiness, manual approval, crypto throttles, approval tickets, and no-trade safety rules still apply.

## Current Target Portfolio

| Sleeve | Target |
| --- | ---: |
| global_core_etf | 55% |
| growth_nasdaq_etf | 15% |
| quality_etf | 10% |
| btc | 10% |
| hype | 2.5% |
| tao | 2.5% |
| discovery | 2.5% |
| tactical_reserve | 2.5% |

## Notes

- Values are stored in EUR.
- The emergency fund is visible in state but excluded from investable portfolio value and allocation calculations.
- Legacy LHV growth holdings are present as nullable fields for future migration or manual reconciliation.
- The allocation engine is intentionally simple, deterministic, and readable.
