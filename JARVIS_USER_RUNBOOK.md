# J.A.R.V.I.S. User Runbook

This is the daily manual-use guide for Diogo.

J.A.R.V.I.S. is a local research and dashboard system. It helps decide what to review, but Diogo makes every real buy manually outside J.A.R.V.I.S.

## How Diogo Uses J.A.R.V.I.S. Daily

1. Start the app.
2. Read `READY FOR MANUAL USE`, Daily Notes, Today's Manual Plan, Market Headlines, Market Movement, Risk & Safety, System Checks, and Useful Actions.
3. Review quote freshness, optional headlines, and safety notes.
4. Make any real-world purchase manually outside J.A.R.V.I.S.
5. Record completed external purchases later in the local manual holdings file.

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

Optional chat is off by default. To open it with the launcher:

```cmd
set JARVIS_OPEN_CHAT=1
Start Jarvis.bat
```

PowerShell:

```powershell
$env:JARVIS_OPEN_CHAT = "1"
.\Start-Jarvis.ps1
```

This starts the local browser chat at:

```text
http://127.0.0.1:8765/chat
```

No installer, admin permission, account login, broker login, or credential setup is required.

## Helper Commands

Open or refresh the dashboard:

```powershell
python .\jarvis_operator.py --dashboard-contract --current-date 2026-06-20 --write-dashboard
```

Open local chat manually:

```powershell
python .\jarvis_operator.py --local-server --current-date 2026-06-20 --host 127.0.0.1 --port 8765
```

Read the daily briefing text:

```powershell
python .\jarvis_operator.py --voice-briefing-text --current-date 2026-06-20
```

Check what changed since the previous safe memory snapshot:

```powershell
python .\jarvis_operator.py --what-changed --current-date 2026-06-20
```

## Read The Dashboard

Use the dashboard as a review screen:

- Today's Manual Plan shows the current manual plan.
- Market Headlines shows optional public headline context. Missing news does not block the manual plan.
- Weekly Manual Plan shows the manual contribution split and selected instruments.
- Manual Holdings shows what Diogo has entered after real buys.
- Market Movement, Risk & Safety, and System Checks show trust and review state.
- Safety must show Manual-only, No broker, No credentials, No orders, No trades, and No auto-approval.

If Manual Holdings says `holdings not entered yet`, that is a review note. It does not block the daily manual workflow.

If Market Headlines says news is unavailable, that is a review note. It does not block the daily manual workflow.

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

## Manual Buy Workflow

J.A.R.V.I.S. can prepare a manual plan, evidence, market movement, headline context, and safety notes.

Diogo decides outside the app. Any real purchase happens manually in the external platform. Afterward, Diogo may update `jarvis/local/manual_holdings.local.json` by hand.

## Safety Rules

J.A.R.V.I.S. may research, summarize, score, route, and display review information.

Diogo manually decides and buys outside J.A.R.V.I.S.

J.A.R.V.I.S. must never connect to a broker, request credentials, create buy or sell requests, create orders, execute trades, mutate allocation, mutate approval tickets, or auto-approve anything.

## What J.A.R.V.I.S. Cannot Do

- No broker login.
- No credentials.
- No private account ingestion.
- No buy or sell request creation.
- No orders.
- No trades.
- No auto-approval.
- No allocation mutation from dashboard, chat, or voice.
- No approval-ticket mutation from dashboard, chat, or voice.

## What Not To Do

Do not put passwords, API keys, broker tokens, account numbers, IBANs, card numbers, or credentials into local JSON files.

Do not commit files from `outputs/` or `jarvis/local/`.

Do not ask J.A.R.V.I.S. to buy, sell, place an order, or approve a real-world transaction.
