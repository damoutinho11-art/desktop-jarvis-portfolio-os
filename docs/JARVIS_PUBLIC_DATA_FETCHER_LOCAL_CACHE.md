# J.A.R.V.I.S. v4.57 Public Data Fetcher Local Cache

v4.57 is the first public data fetching boundary. It can validate public source manifests, preview daily/weekly/manual update plans, and, only with explicit authorization, fetch unauthenticated public data into ignored local cache.

Default mode is dry-run/no-network/no-write.

The required exact phrase for real fetch is:

```text
AUTHORIZE_PUBLIC_DATA_FETCH_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE
```

Fetched data is raw and unverified. Fetching is not evidence verification, not asset approval, not trust, not investability, not allocation advice, not a buy/sell request, and not trade execution.

## Frequencies

Daily updates are preferred for market/reference freshness. Weekly updates are acceptable for slower metadata. Manual sources can be reviewed on demand.

No scheduler is installed automatically.

## Local Manifest

Copy the committed template into an ignored local path before adding real public source URLs:

```powershell
New-Item -ItemType Directory -Force -Path jarvis\local
Copy-Item templates\jarvis_public_data_sources.local.template.json jarvis\local\public_data_sources.local.json
git status --short
```

Do not include private/account data, broker credentials, authenticated endpoints, tokens, screenshots, PDFs, or personal files. Public official references may be listed as URLs, but downloaded/private files must not be committed.

## Dry-Run Report

```powershell
python -m jarvis.jarvis_public_data_fetcher_report
python -m jarvis.jarvis_public_data_fetcher_report --input jarvis\data\jarvis_public_data_fetcher.synthetic_plan.example.json
python -m jarvis.jarvis_public_data_fetcher_report --input jarvis\data\jarvis_public_data_fetcher.example.json --manifest templates\jarvis_public_data_sources.local.template.json
```

## Explicit Local Fetch

Use only ignored local config and manifest files:

```powershell
python -m jarvis.jarvis_public_data_fetcher_report --input jarvis\local\public_data_fetcher.local.json --manifest jarvis\local\public_data_sources.local.json --execute-fetch --authorization-phrase AUTHORIZE_PUBLIC_DATA_FETCH_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE
```

The output directory must remain under `jarvis\local\`, such as `jarvis\local\public_data_snapshots`.

## Optional Manual Windows Task Scheduler Command

This command is documentation only. The code does not create scheduled tasks.

```powershell
schtasks /Create /TN "JARVIS Public Data Fetch Daily" /SC DAILY /ST 07:00 /TR "powershell -NoProfile -ExecutionPolicy Bypass -Command \"cd C:\Users\User\Documents\Codex\2026-06-04\desktop-jarvis-portfolio-os; python -m jarvis.jarvis_public_data_fetcher_report --input jarvis\local\public_data_fetcher.local.json --manifest jarvis\local\public_data_sources.local.json --execute-fetch --authorization-phrase AUTHORIZE_PUBLIC_DATA_FETCH_LOCAL_CACHE_ONLY_NO_VERIFY_NO_TRADE\"" /F
```

Scheduler creation is manual and optional. It should only use ignored local config and manifest paths.

## Safety

v4.57 does not mutate registries, write candidate registry files, write candidate intake files, persist candidate packets, approve assets, trust assets, mark assets investable, verify evidence, promote verified evidence, recommend allocations, construct portfolios, set portfolio weights, create buy/sell requests, trade, use broker/authenticated APIs, use credentials, ingest private files, ingest private/account data, or extract evidence facts automatically.
