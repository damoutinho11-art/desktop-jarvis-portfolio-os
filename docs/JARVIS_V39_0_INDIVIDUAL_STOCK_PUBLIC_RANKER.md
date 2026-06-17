# J.A.R.V.I.S. v39.0 Individual Stock Public Ranker

## Purpose

v39 ranks individual stocks only after v38 has produced fresh public stock signals.

The ranker consumes public-source-ready stock signals and creates a review-only ranking. It does not approve, ticket, allocate, order, or trade.

## Inputs

```text
jarvis/local/individual_stock_public_universe.local.json
jarvis/local/individual_stock_public_signals.local.json
```

## Optional output

```text
jarvis/local/individual_stock_public_ranked_candidates.local.json
```

This output is local/operator-managed and should not be committed.

## Commands

Run daily ranking:

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17
```

Write local stock signals and ranked candidates:

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --write-stock-signals --write-ranked-stocks
```

## Ranked candidate safety status

Ranked candidates use:

```text
RANKED_STOCK_CANDIDATE_FOR_REVIEW_NOT_APPROVED
```

This means the candidate is not approved for purchase and is not written into the approval ticket.

## Safety

v39 does not:

- mutate allocation
- write stock approval tickets
- create buy requests
- connect to brokers
- request credentials
- ingest private account data
- create orders
- execute trades

The final real-world buy remains manual outside J.A.R.V.I.S.