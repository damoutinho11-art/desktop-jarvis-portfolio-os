# J.A.R.V.I.S. Manual Candidate Intake Bridge

v4.51 bridges v4.50 manual watchlist entries to v4.49 candidate intake by building a dry-run candidate intake packet preview.

The bridge is dry-run and report-only. It previews candidate intake packets; it does not write them. It does not collect evidence, verify evidence, mutate any registry or candidate registry, approve assets, trust assets, make assets investable, fetch or download sources, ingest private files, recommend allocations, create buy/sell requests, trade, or create an executor.

## Purpose

Manual watchlist entries can be reviewed as a batch before a future explicit manual candidate-intake acceptance step. v4.51 only shows which v4.50 entries are ready for human review as v4.49-compatible candidate intake previews.

VWCE and FTAW were pilot anchors only. Any future candidate must pass the same v4.27-v4.47 evidence and manual review chain. No candidate becomes trusted, approved, or investable automatically.

## Running Reports And Tests

```powershell
python -m py_compile jarvis\jarvis_manual_candidate_intake_bridge.py jarvis\jarvis_manual_candidate_intake_bridge_report.py jarvis\tests\test_jarvis_manual_candidate_intake_bridge.py jarvis\tests\test_jarvis_manual_candidate_intake_bridge_report.py
python -m unittest jarvis.tests.test_jarvis_manual_candidate_intake_bridge jarvis.tests.test_jarvis_manual_candidate_intake_bridge_report -v
python -m jarvis.jarvis_manual_candidate_intake_bridge_report
python -m jarvis.jarvis_manual_candidate_intake_bridge_report --input jarvis\data\jarvis_manual_candidate_intake_bridge.synthetic_multi.example.json
python -m jarvis.jarvis_manual_candidate_watchlist_entry_report
python -m jarvis.jarvis_candidate_intake_report
python -m jarvis.jarvis_phase1_command_index_report
python -m unittest discover jarvis/tests
```

## Future Stage Placeholder

A future layer may add an explicit manual candidate intake acceptance recorder or write-command contract, but only if separately requested. Such a future layer must still avoid registry mutation unless an explicit, separately validated write command exists.
