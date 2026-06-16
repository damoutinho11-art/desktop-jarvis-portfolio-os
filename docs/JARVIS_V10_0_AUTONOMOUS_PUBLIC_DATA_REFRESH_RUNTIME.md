# J.A.R.V.I.S. v10.0 Autonomous Public Data Refresh Runtime

## Verdict

v10.0 starts product mode.

It does not add another public-data planner. It orchestrates the existing public-data fetcher boundary behind a single autonomous refresh runtime.

## What v10.0 Uses

- v9.1 capability map and roadmap lock
- existing `jarvis_public_data_fetcher.py`
- existing local-cache-only public fetch boundary
- existing source validation rules
- existing no-broker/no-credentials/no-execution controls

## What v10.0 Adds

v10.0 adds one runtime layer that can:

- load a public data source manifest;
- validate public sources;
- build an update plan;
- optionally execute an explicitly authorized local-cache-only public fetch;
- write raw public data only under `jarvis/local`;
- report whether downstream normalization and source-quality gates can run.

## Default Mode

Default mode is safe dry-run contract mode.

If `jarvis/local/public_data_sources.local.json` does not exist, the report uses a demo manifest only to prove the runtime contract.

The demo manifest does not make a network call.

## Operational Mode

Operational mode should use:

`jarvis/local/public_data_sources.local.json`

That file is ignored by git and should contain real public source URLs.

## Real Fetch Boundary

Real public fetching requires the existing exact authorization phrase:

`AUTHORIZE_PUBLIC_DATA_FETCH_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE`

Even then, v10.0 only writes raw unverified public data into local cache.

## What v10.0 Does Not Do

v10.0 does not:

- create another source-selection layer;
- create another dry-run planner;
- create another provider registry;
- connect to brokers;
- use credentials;
- ingest private account data;
- treat raw data as verified evidence;
- create buy requests;
- place orders;
- execute trades.

## Manual Boundary

The only manual final action remains Diogo's real-world buy.

J.A.R.V.I.S. may autonomously gather data, validate sources, prepare evidence, generate recommendations, produce dashboards, and prepare voice summaries.

J.A.R.V.I.S. must not execute the buy.

## Next Stage

v10_1_unified_operator_runtime

Reason:

After v10.0, public data refresh has a single runtime entrypoint. The next product step is to unify refresh, quality, evidence, recommendation, dashboard, and voice-ready summary into one operator runtime.
