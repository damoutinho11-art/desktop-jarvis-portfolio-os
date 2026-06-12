# Manual Candidate Workspace Templates

These templates are safe to commit because they contain no real candidate, account, broker, credential, screenshot, PDF, or private portfolio data.

Copy templates into an ignored local/private path before entering real watchlist data:

```powershell
New-Item -ItemType Directory -Force -Path jarvis\local
Copy-Item templates\jarvis_manual_candidate_watchlist_entry.local.template.json jarvis\local\manual_candidate_watchlist_entries.local.json
git status --short
```

The copied local file must remain ignored and uncommitted. v4.56 does not approve assets, trust candidates, write registries, collect evidence, verify evidence, recommend allocations, create buy/sell requests, trade, or create an executor.
