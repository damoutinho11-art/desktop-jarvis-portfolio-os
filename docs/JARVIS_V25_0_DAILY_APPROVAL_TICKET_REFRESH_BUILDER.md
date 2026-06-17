# J.A.R.V.I.S. v25.0 Daily Approval Ticket Refresh Builder

## Purpose

v25 refreshes the local manual approval ticket from the active v24 daily operator.

It writes a current `outputs/approval_ticket_latest.json` only when explicitly requested with `--write-ticket`.

## Scope

Included:

- selected crypto candidate from the v23/v24 crypto-lane selection gate
- selected stock/fund/ETF lane from the current allocation engine
- manual approval status
- current as_of/timestamp
- stale portfolio warnings
- safety checks

Excluded:

- buy request creation
- broker connection
- credentials
- private account ingestion
- order placement
- trade execution
- automatic selling

## Safety note

This stage intentionally mutates the local approval ticket when `--write-ticket` is used. That is not a broker action and not a buy request. It is only a local manual-review artifact.

## v25.1 as-of basis hotfix

The approval ticket must not claim a fresher `as_of` date than the allocation engine basis. If the allocation result is still based on an older portfolio state, the ticket uses that allocation `as_of` and stores the actual build date separately as `generated_at` / `ticket_generated_at`.

This prevents the daily readiness gate from blocking on an approval-ticket/allocation as-of mismatch while still keeping stale portfolio review warnings visible.

## v25.2 approval-ticket replacement deadlock hotfix

v25.1 correctly changed the new ticket basis, but the existing stale local ticket could still block the builder before the corrected replacement was written. v25.2 allows the builder to replace exactly that existing approval-ticket/allocation as-of mismatch when the new ticket uses the allocation basis as `as_of` and stores the build date separately as `generated_at`.

This exception is narrow: it only clears the existing-ticket mismatch blocker. It does not clear portfolio stale warnings, does not create a buy request, and does not permit broker/order/trade actions.

