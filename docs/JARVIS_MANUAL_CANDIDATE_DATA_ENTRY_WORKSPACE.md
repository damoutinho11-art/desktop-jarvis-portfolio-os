# J.A.R.V.I.S. v4.56 Manual Candidate Data Entry Workspace

v4.56 is a local-first workspace template and private-data guardrail layer for manual candidate watchlist entry.

v4.55 concluded that the v4.49-v4.54 candidate-intake dry-run chain is complete. v4.56 is not another gate. It adds safe templates, documentation, and a read-only workspace report so real candidate watchlist data can be entered locally without being committed.

## What This Does

- Provides a blank local template for manual candidate watchlist entry.
- Documents where real/private candidate data should live.
- Validates that committed examples and templates remain synthetic or blank.
- Confirms the next action is manual candidate watchlist data entry only.
- Confirms the route: v4.56 workspace -> v4.50 manual watchlist entry -> v4.49 candidate intake -> v4.27-v4.47 evidence and manual review pipeline.

## What This Does Not Do

v4.56 does not approve assets, trust candidates, mark assets investable, collect evidence, verify evidence, promote verified evidence, mutate registries, write candidate registry files, persist candidate intake packets, recommend allocations, set portfolio weights, create buy/sell requests, trade, call broker or authenticated APIs, use credentials, ingest private files, fetch sources, download files, extract facts, or create an executor.

VWCE and FTAW are pilot anchors only. Any candidate must still pass the v4.27-v4.47 evidence and manual review chain before later manual review stages can even be considered.

## Local Copy Workflow

Use PowerShell to copy the committed blank template into an ignored local path:

```powershell
New-Item -ItemType Directory -Force -Path jarvis\local
Copy-Item templates\jarvis_manual_candidate_watchlist_entry.local.template.json jarvis\local\manual_candidate_watchlist_entries.local.json
git status --short
```

The copied local file must remain ignored and uncommitted. Do not commit local candidate watchlists, account data, broker data, credentials, screenshots, PDFs, downloaded files, private files, or outputs.

## Report

```powershell
python -m jarvis.jarvis_manual_candidate_data_entry_workspace_report
python -m jarvis.jarvis_manual_candidate_data_entry_workspace_report --input jarvis\data\jarvis_manual_candidate_data_entry_workspace.example.json
```

## Tests

```powershell
python -m unittest jarvis.tests.test_jarvis_manual_candidate_data_entry_workspace jarvis.tests.test_jarvis_manual_candidate_data_entry_workspace_report -v
python -m unittest discover jarvis/tests
```
