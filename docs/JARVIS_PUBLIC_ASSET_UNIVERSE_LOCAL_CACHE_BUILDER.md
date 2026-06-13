# J.A.R.V.I.S. v4.64 Public Asset Universe Local Cache Builder

v4.64 is the first controlled local-cache builder for public asset universe sources.

The default mode does not fetch and does not write. The only path that may fetch and write is the explicit authorized helper path, guarded by the exact phrase:

`AUTHORIZE_PUBLIC_ASSET_UNIVERSE_FETCH_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE`

Authorized cache building is limited to public unauthenticated sources, local cache paths under `jarvis/local/public_asset_universe/`, and raw unverified data plus metadata sidecars. Tests use fake fetchers and temporary cache roots; no internet is required.

Raw cache is not evidence verification. Cache metadata is not approval. Universe data is not trust, investability, allocation advice, a buy/sell signal, trade authorization, or executor authorization.

## Safety Boundary

- Default report path performs no network calls, fetching, downloading, or writes.
- The import path is safe and does not instantiate a fetcher.
- Any real network path must be explicit, authorized, and local-cache-only.
- No broker, Lightyear, LHV, crypto exchange private API, wallet, credential, or account integration is allowed.
- No credentials or private/account data may be ingested.
- No source parsing as evidence, evidence extraction, evidence verification, or verified evidence promotion happens in v4.64.
- No registry mutation, candidate registry write, candidate intake write, allocation, portfolio weight, buy/sell signal, trade, or executor is created.

## Commands

Default blocked report:

```powershell
python -m jarvis.jarvis_public_asset_universe_local_cache_builder_report
```

Unauthorized fixture:

```powershell
python -m jarvis.jarvis_public_asset_universe_local_cache_builder_report --input jarvis\data\jarvis_public_asset_universe_local_cache_builder.synthetic_unauthorized.json
```

Authorized synthetic readiness report, still no execution:

```powershell
python -m jarvis.jarvis_public_asset_universe_local_cache_builder_report --input jarvis\data\jarvis_public_asset_universe_local_cache_builder.synthetic_authorized.json
```

Focused tests:

```powershell
python -m unittest jarvis.tests.test_jarvis_public_asset_universe_local_cache_builder jarvis.tests.test_jarvis_public_asset_universe_local_cache_builder_report -v
```

## What Not To Build Next

- no classifier inside v4.64
- no evidence extraction
- no scheduler
- no investment screening
- no broker integration
- no registry mutation
- no executor

## Next Efficient Stage

The next useful stage is either v4.65 Public Asset Universe Cache Freshness + Integrity Audit or v4.65 Public Asset Universe Normalizer, depending on whether the cache builder remains stable.
