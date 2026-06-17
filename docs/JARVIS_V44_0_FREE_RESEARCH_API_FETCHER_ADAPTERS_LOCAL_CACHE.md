# J.A.R.V.I.S. v44.0 Free Research API Fetcher Adapters + Local Cache

## Purpose

v44 starts the real free-data adapter layer behind the v43 router.

It adds infrastructure for:

- CoinGecko free/demo crypto fetch
- ECB official FX reference fetch
- optional FMP fetch when `JARVIS_FMP_API_KEY` exists
- optional SEC EDGAR validation fetch
- local cache writes under `jarvis/local`

## Default daily mode

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17
```

Daily mode remains approval-ticket read-only and does not refresh the cache unless explicitly requested.

## Explicit cache refresh

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --refresh-free-research-cache
```

This writes:

```text
jarvis/local/free_research_api_cache.local.json
```

Do not commit this local cache file.

## Optional providers

FMP is used only when explicitly requested and when a local key exists:

```powershell
$env:JARVIS_FMP_API_KEY="..."
python .\jarvis_operator.py --weekly-buy-prep --current-date 2026-06-17 --refresh-free-research-cache --include-fmp
```

SEC EDGAR validation is explicit:

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --refresh-free-research-cache --include-sec
```

## Safety

v44 does not:

- connect to a broker
- use a broker API
- request credentials
- ingest private account data
- create buy requests
- create orders
- execute trades

Final real-world buy remains manual outside J.A.R.V.I.S.