# J.A.R.V.I.S. v43.0 Free Research API Router + Weekly Policy

## Purpose

v43 codifies the operating model:

- daily check-ins and finance analysis
- weekly manual buy preparation
- free-first research data router
- optional API keys only from local environment
- no broker API
- no order API
- no execution

## Daily mode

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17
```

Daily mode is check-in only and should remain read-only. It can refresh/read the three-lane action brief, source confidence, risk/warning state, and provider readiness.

It does not mean daily buying.

## Weekly buy preparation mode

```powershell
python .\jarvis_operator.py --weekly-buy-prep --current-date 2026-06-17
```

Weekly mode allows manual buy preparation only if:

- the three-lane action brief is READY
- source confidence passes
- no blockers exist
- no safety boundary is violated

It still does not create a buy request, order, or trade.

## Free-first provider router

v43 defines the provider plan:

- `fmp_free_optional` for stocks, ETFs, fundamentals, ETF metadata, ETF holdings when a local key exists
- `coingecko_free_or_demo` for crypto
- `sec_edgar_official` for official US stock validation
- `ecb_fx_official` for EUR FX reference
- `yahoo_chart_public_fallback` for public price fallback
- `local_cache_audit_trail` for cache, rate-limit protection, and audit history

## Local API keys

Do not commit API keys.

Optional local environment variables:

```powershell
$env:JARVIS_FMP_API_KEY="..."
$env:JARVIS_COINGECKO_API_KEY="..."
```

Missing optional keys do not block the system while no-key official/public fallbacks remain available.

## Safety

v43 does not:

- connect to a broker
- use a broker API
- request credentials
- ingest private account data
- create buy requests
- create orders
- execute trades

Final real-world buy remains manual outside J.A.R.V.I.S.
## Daily read-only rule

Daily mode must not mutate the approval ticket. Weekly buy-prep mode may refresh/write the manual review ticket.
## Honest confidence scoring

Missing optional keys should reduce confidence honestly. The free/no-key stack can still be sufficient for weekly investing, but it should not report maximum confidence until richer optional research sources are present or validated.