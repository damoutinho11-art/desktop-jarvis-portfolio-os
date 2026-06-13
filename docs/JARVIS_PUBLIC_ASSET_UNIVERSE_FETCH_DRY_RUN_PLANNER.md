# J.A.R.V.I.S. v4.63 Public Asset Universe Fetch Dry-Run Planner

v4.63 consumes a public asset universe source manifest and creates fetch dry-run
plans only. It comes after v4.61 public universe discovery planning and v4.62
public source manifest schema validation.

This is not an actual fetcher, cache builder, scheduler, classifier, evidence
extractor, investment screener, broker integration, or executor.

## Purpose

The dry-run planner describes:

- public sources that would be eligible for a future fetch
- public manual-reference sources that should not be automatically downloaded
- blocked sources and reasons
- required explicit authorization phrase
- planned raw cache, metadata, and fetch-plan paths
- freshness requirements
- deterministic future fetch order

## Authorization

Future fetch requires this exact phrase:

```text
AUTHORIZE_PUBLIC_ASSET_UNIVERSE_FETCH_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE
```

v4.63 still does not fetch even if a fixture contains an authorization phrase.
It is dry-run planning only.

## Safety Boundaries

v4.63 does not make network calls, fetch, download, scrape, call APIs, write cache
files, create local files, schedule tasks, run subprocesses, automate a browser,
use credentials, integrate with Lightyear/LHV/crypto exchanges, ingest private or
account data, extract evidence, verify evidence, promote evidence, approve
assets, mutate registries, recommend allocation, emit buy/sell signals, trade, or
create an executor.

Future fetched data remains raw and unverified. Source fetch planning is not
verification. Cache planning is not approval. Screening is not investment advice.

## Next Stage

The next efficient stage is v4.64 Public Asset Universe Local Cache Builder,
which may write ignored local cache only if separately implemented and explicitly
authorized. Do not build an actual fetcher in v4.63.

## Run

```powershell
python -m jarvis.jarvis_public_asset_universe_fetch_dry_run_planner_report
python -m jarvis.jarvis_public_asset_universe_fetch_dry_run_planner_report --input jarvis\data\jarvis_public_asset_universe_fetch_dry_run_planner.synthetic_complete.json
python -m unittest jarvis.tests.test_jarvis_public_asset_universe_fetch_dry_run_planner jarvis.tests.test_jarvis_public_asset_universe_fetch_dry_run_planner_report -v
```

The v5.0 target remains a local-first public research OS, not a trading bot.
