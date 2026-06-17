# J.A.R.V.I.S. v35.0 Selected Stock/Fund/ETF Instrument Ticket Bridge

## Purpose

v35 bridges the selected real ETF/fund instrument from the local v34 resolution into the manual approval ticket.

This fixes the output gap where the ETF lane had already resolved `quality_etf` into a real instrument, but older ticket output still displayed only the abstract sleeve.

## Inputs

- Approval ticket:
  - `outputs/approval_ticket_latest.json`
- Local selected real instrument resolution:
  - `jarvis/local/stock_fund_etf_selected_instrument.local.json`

## Write behavior

The approval ticket is updated only with:

```powershell
python .\jarvis_operator.py --daily --current-date 2026-06-17 --write-ticket
```

Without `--write-ticket`, v35 reviews and reports the bridge status but does not mutate the ticket.

## Ticket fields added

v35 preserves the sleeve:

```json
"selected_stock_fund_etf_candidate": "quality_etf"
```

and adds real-instrument fields:

```json
"selected_stock_fund_etf_sleeve": "quality_etf",
"selected_stock_fund_etf_real_instrument": { ... },
"selected_stock_fund_etf_real_instrument_symbol": "IS3Q.DE",
"stock_fund_etf_lane_mode": "sleeve_resolved_to_real_instrument",
"stock_fund_etf_source_metadata": {
  "metadata_status": "ETF_SOURCE_METADATA_READY"
}
```

## Safety

v35 does not:

- choose a new allocation
- choose a new sleeve
- create a buy request
- connect to a broker
- request credentials
- ingest private account data
- place orders
- execute trades

The final real-world buy remains manual outside J.A.R.V.I.S.