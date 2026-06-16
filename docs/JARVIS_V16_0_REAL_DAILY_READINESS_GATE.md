# J.A.R.V.I.S. v16.0 Real Daily Readiness Gate

## Purpose

v16.0 adds the missing daily product gate after v15.0 wired the daily operator to the real root allocation engine.

The daily command now answers two separate questions:

1. What is the current real allocation recommendation from the local engine?
2. Is the local data behind that recommendation fresh enough to trust before Diogo performs any manual real-world buy outside J.A.R.V.I.S.?

## Active command

```powershell
python .\jarvis_operator.py --daily
```

## What v16 checks

- `portfolio_state.json` `as_of` date.
- `outputs/approval_ticket_latest.json` `as_of` date.
- Whether the saved approval ticket date matches the current allocation engine ticket date.
- Optional `etf_universe.json` `as_of` / `updated_at` metadata when present.
- Existing v15 safety boundary: manual approval required, no broker connection, no orders created, and no trades executed.

## Expected current behavior

With the current local data snapshot dated `2026-06-04`, the daily operator should show a stale-data review requirement when run later than the configured freshness window:

```text
J.A.R.V.I.S. Real Allocation Daily Operator
operator date: <today>
data readiness: STALE_REVIEW_REQUIRED
recommendation trust: refresh_required_before_manual_action
manual action guidance: Refresh local portfolio data and approval ticket before any manual buy.
```

The recommendation can still be displayed for review, but J.A.R.V.I.S. should not present stale data as ready for a manual action.

## Safety boundary

v16.0 does not add broker access, credentials, private brokerage/account ingestion, buy requests, orders, or trade execution. The final real-world buy remains Diogo's manual action outside J.A.R.V.I.S.
