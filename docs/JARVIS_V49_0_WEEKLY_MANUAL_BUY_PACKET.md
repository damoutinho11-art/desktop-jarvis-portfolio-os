# J.A.R.V.I.S. v49.0 Weekly Manual Buy Packet Generator

## Purpose

v49 is the first user-facing weekly product output built on the stable runtime facade.

Weekly buy-prep mode now renders:

```text
J.A.R.V.I.S. WEEKLY MANUAL BUY PACKET
```

instead of only showing the internal evidence bridge.

## Command

```powershell
python .\jarvis_operator.py --weekly-buy-prep --current-date 2026-06-17 --refresh-free-research-cache --write-evidence-pack
```

Optional weekly budget display:

```powershell
python .\jarvis_operator.py --weekly-buy-prep --current-date 2026-06-17 --weekly-budget-eur 100
```

v49 only displays the budget. It does not allocate capital automatically.

## Packet sections

The packet includes:

- crypto manual action
- ETF/fund manual action
- individual-stock review
- evidence summary
- source confidence
- risk notes
- safety state

## Safety

v49 does not:

- approve purchases
- assign capital automatically
- mutate allocation
- create buy requests
- connect to brokers
- request credentials
- ingest private account data
- create orders
- execute trades

Final real-world buy remains manual outside J.A.R.V.I.S.

## Next stage

The recommended next stage is:

```text
manual_weekly_amount_router
```

That should turn one weekly amount input into a safe manual packet allocation proposal, still without execution.
## Stock review evidence precision

The individual-stock review section must not reuse unrelated crypto or FX evidence. If no stock-specific evidence is available, it should say so explicitly. Stock-specific evidence comes from lanes such as `stocks_etfs_fundamentals` or `us_stock_validation`.