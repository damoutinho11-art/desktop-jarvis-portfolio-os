# J.A.R.V.I.S. v4.58 Public Data Freshness Monitor

v4.58 monitors local public-data cache freshness only. It reads source metadata and cache index metadata, then reports which sources are fresh, stale, missing, failed, or governed by manual refresh policy.

It performs no network calls, no fetching, no downloads, no parsing as evidence, no evidence extraction, no evidence verification, no approval, no trust, no investability, no registry mutation, no allocation advice, no buy/sell request, no trade, and no executor work.

## Freshness Rules

- Daily sources should usually be refreshed every day. A daily source is fresh within 1 calendar day of `current_date`.
- Weekly sources should usually be refreshed within 7 calendar days.
- Manual sources require human policy/review and are not stale automatically.
- Failed cache entries need a v4.57 explicit local-cache fetch if the source is still needed.
- Missing cache entries only mean “consider running v4.57 explicit public fetch local-cache-only.”

Stale or missing data is not approval, not evidence verification, not a buy/sell signal, and not a trade instruction.

Raw cached data remains unverified until a separate manual evidence review pipeline. A future manual source review/fact-entry bridge from cached public data may be added only if separately requested, and it still must not automatically verify evidence.

## Commands

```powershell
python -m jarvis.jarvis_public_data_freshness_monitor_report
python -m jarvis.jarvis_public_data_freshness_monitor_report --input jarvis\data\jarvis_public_data_freshness_monitor.synthetic_complete.example.json
```

## Tests

```powershell
python -m unittest jarvis.tests.test_jarvis_public_data_freshness_monitor jarvis.tests.test_jarvis_public_data_freshness_monitor_report -v
```

## Route

v4.56 manual candidate data entry workspace -> v4.57 public data fetcher local cache control plane -> v4.58 public data freshness monitor -> future manual source review/fact entry only if separately requested -> v4.27-v4.47 evidence/manual review pipeline.
