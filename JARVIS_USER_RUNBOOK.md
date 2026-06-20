# J.A.R.V.I.S. User Runbook

This is the daily manual-use guide for Diogo.

J.A.R.V.I.S. is a local research and dashboard system. It helps decide what to review, but Diogo makes every real buy manually outside J.A.R.V.I.S.

## Start The App

Double-click:

```text
Start Jarvis.bat
```

PowerShell alternative:

```powershell
.\Start-Jarvis.ps1
```

## What Start Jarvis.bat Does

It runs the daily operator for today's date:

```powershell
python .\jarvis_operator.py --daily-operator --current-date <today> --max-targets 10
```

If the daily operator is ready, it opens:

```text
outputs\dashboard_latest.html
```

If J.A.R.V.I.S. needs review, it does not open the dashboard automatically.

## Read The Dashboard

Use the dashboard as a review screen:

- Today's Manual Action Summary shows the current manual plan.
- Weekly Manual Plan shows the manual contribution split and selected instruments.
- Manual Holdings shows what Diogo has entered after real buys.
- Data, News, Finance Intelligence, and Audit show trust and review state.
- Safety must show no broker, no credentials, no orders, and no trades.
- Blockers should be none before acting manually.

If Manual Holdings says `holdings not entered yet`, that is a review note. It does not block the daily manual workflow.

## Update Holdings After A Manual Buy

After Diogo buys outside J.A.R.V.I.S., update the local holdings file:

```text
jarvis/local/manual_holdings.local.json
```

First create the blank template if it does not exist:

```powershell
python .\jarvis_operator.py --write-holdings-template --current-date 2026-06-20
```

Then edit the local JSON file by hand. Fill only real buys already completed outside J.A.R.V.I.S. Set:

```json
"is_template": false,
"manual_only": true,
"source": "diogo_manual_entry",
"holdings_confirmed": true
```

Check the holdings status:

```powershell
python .\jarvis_operator.py --holdings-status --current-date 2026-06-20
```

## Safety Rules

J.A.R.V.I.S. may research, summarize, score, route, and display review information.

Diogo manually decides and buys outside J.A.R.V.I.S.

J.A.R.V.I.S. must never connect to a broker, request credentials, create buy or sell requests, create orders, execute trades, mutate allocation, mutate approval tickets, or auto-approve anything.

## What Not To Do

Do not put passwords, API keys, broker tokens, account numbers, IBANs, card numbers, or credentials into local JSON files.

Do not commit files from `outputs/` or `jarvis/local/`.

Do not ask J.A.R.V.I.S. to buy, sell, place an order, or approve a real-world transaction.
