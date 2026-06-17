# J.A.R.V.I.S. v50.0 Manual Weekly Amount Router

## Purpose

v50 turns a weekly budget into a manual review amount proposal inside the weekly buy packet.

Example:

```powershell
python .\jarvis_operator.py --weekly-buy-prep --current-date 2026-06-17 --weekly-budget-eur 100 --refresh-free-research-cache --write-evidence-pack
```

The packet now includes:

```text
Manual amount router
```

## Routing policy

v50 does not use a fixed long-term allocation.

It routes only when:

- Diogo provides a positive weekly budget
- refreshed usable evidence exists for the lane

The default v50 policy is:

- crypto can receive a proposed amount only when crypto evidence is usable
- crypto is capped at 40 percent of the weekly budget because of volatility
- ETF/fund receives the evidence-weighted remainder when ETF/fund or FX evidence is usable
- individual stock remains review-only at 0 EUR in v50
- no route mutates portfolio allocation

## Safety

v50 does not:

- approve purchases
- mutate allocation
- create buy requests
- connect to brokers
- request credentials
- ingest private account data
- create orders
- execute trades

Final real-world buy remains manual outside J.A.R.V.I.S.

## Expected output for EUR 100 with refreshed evidence

```text
crypto: 40.0 EUR
ETF/fund: 60.0 EUR
individual stock review: 0.0 EUR
buy request created: False
no broker connection
no trades executed
```