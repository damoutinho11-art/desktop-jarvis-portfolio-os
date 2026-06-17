# J.A.R.V.I.S. v42.0 Three-Lane Daily Action Brief

## Purpose

v42 makes the root daily operator produce one clean three-lane manual action brief:

- crypto lane
- stock/fund/ETF lane
- individual stock lane

The individual stock lane remains review-only. It has no amount assigned and no purchase approval.

## Default daily command

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17
```

The default daily command runs the stock bridge safely and writes:

- local public stock universe/signals/ranked files under `jarvis/local`
- review-only stock candidate fields in `outputs/approval_ticket_latest.json`

## Safety

v42 blocks unsafe states:

- individual stock `amount_eur` must remain null
- individual stock `approved_for_purchase` must remain false
- no buy request can be created
- no broker connection
- no credentials
- no private account ingestion
- no orders
- no trades

The final real-world buy remains manual outside J.A.R.V.I.S.