# J.A.R.V.I.S. v15.0 Real Allocation Daily Bridge

v15.0 wires the short daily operator command to the existing root allocation engine instead of the staged/demo product launcher surface.

## Operator command

```powershell
python .\jarvis_operator.py --daily
```

The daily command now reads the current result from `allocation_engine.build_weekly_result()` and formats the generated approval ticket. It surfaces:

- portfolio date and mode;
- weekly budget;
- current executable allocation;
- selected ideal sleeve;
- manual approval status;
- approval ticket path;
- ranked ETF candidates and reasons;
- safety status.

## Dynamic allocation rule

The daily bridge does not hard-code `quality_etf` or any other sleeve. The selected sleeve and executable allocation are read from the current weekly result / approval ticket.

Focused tests cover fixtures where the selected sleeve changes to:

- `quality_etf`;
- `growth_nasdaq_etf`;
- `global_core_etf`.

## Safety boundary

v15.0 remains local and read-only:

- no broker connection;
- no credentials;
- no private account ingestion;
- no buy request;
- no order placement;
- no trade execution;
- manual approval remains required;
- the final real-world buy remains outside J.A.R.V.I.S.

The safety-check command still blocks an execution request:

```powershell
python .\jarvis_operator.py --safety-check
```

Expected behavior: `Jarvis, buy BTC now.` is blocked and no execution action is taken.

## Validation

```powershell
python -m py_compile .\jarvis\jarvis_v15_0_real_allocation_daily_bridge.py .\jarvis\jarvis_v15_0_real_allocation_daily_bridge_report.py .\jarvis\tests\test_jarvis_v15_0_real_allocation_daily_bridge.py .\jarvis\tests\test_jarvis_v15_0_real_allocation_daily_bridge_report.py .\jarvis_operator.py
python -m unittest jarvis.tests.test_jarvis_v15_0_real_allocation_daily_bridge jarvis.tests.test_jarvis_v15_0_real_allocation_daily_bridge_report -v
python -m jarvis.jarvis_v15_0_real_allocation_daily_bridge_report
python .\jarvis_operator.py --daily
python .\jarvis_operator.py --safety-check
```

