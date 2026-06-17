# J.A.R.V.I.S. v55.0 Platform Lane Policy Engine

## Verdict

v55.0 adds the platform lane policy layer.

This codifies Diogo's platform decision:

- LHV: cash, emergency fund, and crypto.
- Lightyear: ETF, stock, and fund investing.
- Legacy positions: observed only until a separate migration review exists.

## Current contribution map

Monthly contribution plan:

- 75 EUR emergency top-up at LHV.
- 170 EUR crypto on LHV.
- 255 EUR ETF/fund/core investing on Lightyear.
- 0 EUR individual stock review-only on Lightyear.

## Legacy policy

Existing ETF/fund positions are not automatically sold.

They are tracked as legacy observed positions for net worth and risk. Selling,
migrating, or replacing them requires a separate explicit migration-review stage.

## Safety

- No allocation mutation.
- No approval-ticket mutation.
- No portfolio-state mutation.
- No buy request.
- No broker API.
- No credentials.
- No private account ingestion.
- No orders.
- No trades.