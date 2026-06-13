# J.A.R.V.I.S. v4.62 Public Asset Universe Source Manifest

v4.62 defines the source manifest schema after the v4.61 public asset universe
discovery plan.

The manifest describes allowed public source metadata before any fetching. It is
the primary path toward broad automated public research, replacing manual
one-by-one asset entry as the main workflow. Manual watchlists remain optional
and secondary for forced or user-specific research ideas.

## What This Stage Does

- Defines allowed public source categories.
- Defines source entry metadata for future universe discovery.
- Validates URL, credential, broker, account, and private endpoint boundaries.
- Defines future fetch policy, local cache policy, and identifier policy.
- Documents the future explicit authorization phrase:

```text
AUTHORIZE_PUBLIC_ASSET_UNIVERSE_FETCH_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE
```

## What This Stage Does Not Do

v4.62 does not fetch, download, scrape, call APIs, or write cache files. It does
not integrate with Lightyear, LHV, crypto exchanges, wallets, brokers, or
authenticated services. It does not use credentials and does not ingest private
or account data.

Source discovery is not verification. Future fetched data remains raw and
unverified. Classification is not approval. Screening is not investment advice.
No source manifest status means approval, trust, investability, allocation,
buy/sell signal, trade execution, registry mutation, or executor authorization.

## Future Path

The next efficient stage is v4.63 Public Asset Universe Fetch Dry-Run Planner.
Do not build a universe fetcher yet in v4.62. Do not build a scheduler,
classifier, evidence extractor, broker integration, trading flow, or executor.

## Run

```powershell
python -m jarvis.jarvis_public_asset_universe_source_manifest_report
python -m jarvis.jarvis_public_asset_universe_source_manifest_report --input jarvis\data\jarvis_public_asset_universe_source_manifest.synthetic_complete.example.json
python -m unittest jarvis.tests.test_jarvis_public_asset_universe_source_manifest jarvis.tests.test_jarvis_public_asset_universe_source_manifest_report -v
```

The v5.0 target remains a local-first public research OS, not a trading bot.
