# J.A.R.V.I.S. v40.0 Individual Stock Public Universe Bootstrap

## Purpose

v40 gives the individual-stock lane a real public starter universe without committing local state.

It writes a local public Yahoo-chart stock universe under:

```text
jarvis/local/individual_stock_public_universe.local.json
```

Then it can run v39 to fetch public Yahoo chart quotes, write local stock signals, and write local ranked candidates.

## Important distinction

The bootstrap universe is not:

- a buy list
- a recommendation
- an approval
- an approval ticket
- an order plan

It is only a public data universe for quote fetching and review-only ranking.

## Command

Write starter public Yahoo-chart stock universe, stock signals, and ranked candidates:

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --bootstrap-stock-universe --write-stock-signals --write-ranked-stocks
```

## Local outputs

Do not commit these:

```text
jarvis/local/individual_stock_public_universe.local.json
jarvis/local/individual_stock_public_signals.local.json
jarvis/local/individual_stock_public_ranked_candidates.local.json
```

## Safety

v40 does not:

- mutate allocation
- write stock approval tickets
- create buy requests
- connect to brokers
- request credentials
- ingest private account data
- create orders
- execute trades

The final real-world buy remains manual outside J.A.R.V.I.S.