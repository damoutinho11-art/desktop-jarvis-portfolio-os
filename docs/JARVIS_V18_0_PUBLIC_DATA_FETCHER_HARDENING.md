# J.A.R.V.I.S. v18.0 Public Data Fetcher Hardening

## Verdict

v18.0 hardens the already-existing public-data fetch boundary so the active product path can move from fetch skeletons toward real autonomous public data refresh without weakening the no-execution safety boundary.

## What changed

- UTF-8 BOM local manifests are accepted safely.
- A bad public source fetch no longer crashes the operator/report path.
- Fetch failures are returned as safe blocked source status instead of Python tracebacks.
- Successful raw public fetches still write only to ignored `jarvis/local` cache paths.
- Raw public data remains unverified and does not update allocation scoring yet.

## Product meaning

This stage does not normalize raw BTC/ETF data and does not alter allocation recommendations. It only makes the public fetch layer reliable enough for the next stage: raw public data normalization and source-quality gating.

## Safety boundary

- No broker connection.
- No credentials.
- No private account ingestion.
- No buy request.
- No orders.
- No trades.
- Final real-world buy remains manual outside J.A.R.V.I.S.
