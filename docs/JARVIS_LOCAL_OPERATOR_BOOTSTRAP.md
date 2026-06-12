# J.A.R.V.I.S. v4.60 Local Operator Bootstrap

v4.60 is a bootstrap guide and smoke-test layer. It is not a gate.

It documents the manual local setup path and validates that the plan is safe. It does not create files or directories, run commands, fetch data, schedule tasks, scan local/private folders, ingest private files, verify evidence, approve candidates, trust candidates, mark candidates investable, recommend allocation, buy, sell, trade, or execute anything.

## Manual Bootstrap Commands

These commands are for the human operator to run manually:

```powershell
New-Item -ItemType Directory -Force -Path jarvis\local
Copy-Item templates\jarvis_manual_candidate_watchlist_entry.local.template.json jarvis\local\manual_candidate_watchlist_entries.local.json
Copy-Item templates\jarvis_public_data_sources.local.template.json jarvis\local\public_data_sources.local.json
git status --short
```

The copied files must remain ignored and uncommitted.

## Dry-Run Reports

```powershell
python -m jarvis.jarvis_manual_candidate_data_entry_workspace_report
python -m jarvis.jarvis_public_data_fetcher_report --input jarvis\data\jarvis_public_data_fetcher.example.json --manifest templates\jarvis_public_data_sources.local.template.json
python -m jarvis.jarvis_public_data_freshness_monitor_report --input jarvis\data\jarvis_public_data_freshness_monitor.synthetic_complete.example.json
python -m jarvis.jarvis_operator_status_dashboard_report --input jarvis\data\jarvis_operator_status_dashboard.synthetic_complete.example.json
```

## Next Efficient Action

1. Edit the local candidate watchlist.
2. Configure the local public source manifest.
3. Optionally run v4.57 explicit fetch manually, only with ignored local config and the exact authorization phrase.

## What Not To Build

- more gates
- scheduler/executor
- evidence extraction
- registry mutation
- allocation/buy/sell/trade logic

## v5.0 Direction

The v5.0 direction is a usable local-first research OS MVP: automated research structure, manual trust, manual approval, and no execution.
