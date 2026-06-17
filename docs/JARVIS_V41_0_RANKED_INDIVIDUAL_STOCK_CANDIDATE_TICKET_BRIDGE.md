# J.A.R.V.I.S. v41.0 Ranked Individual Stock Candidate Ticket Bridge

## Purpose

v41 bridges the top ranked individual-stock candidate into the manual approval-ticket flow as review-only.

It does not approve the stock and it does not assign a buy amount.

## Command

Run full public stock bootstrap/ranking and bridge the top ranked candidate into the manual ticket:

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --bootstrap-stock-universe --write-stock-signals --write-ranked-stocks --write-stock-ticket
```

## Ticket field

v41 writes:

```text
selected_individual_stock_candidate
individual_stock_source_metadata
```

The candidate decision status is:

```text
RANKED_INDIVIDUAL_STOCK_CANDIDATE_BRIDGED_FOR_REVIEW_NOT_APPROVED
```

## Safety

v41 does not:

- approve a stock
- assign amount_eur
- mutate allocation
- mutate portfolio state
- create a buy request
- connect to brokers
- request credentials
- ingest private account data
- create orders
- execute trades

The final real-world buy remains manual outside J.A.R.V.I.S.
## Warning classification

If a fresh top-ranked stock candidate is available and the review-only stock ticket bridge writes successfully, non-top upstream stock-universe fetch warnings do not block the bridge.

Blocked upstream stages still block v41.