# J.A.R.V.I.S. Manual Candidate Watchlist Entry

v4.50 adds a manual candidate watchlist entry layer. It prepares user-entered watchlist records for v4.49 candidate intake and then the existing v4.27-v4.47 real-evidence pipeline.

Manual watchlist entry is not approval. It is not trust or investability. It is not evidence verification. It is not registry mutation. It does not fetch or download sources. It does not ingest private files automatically. It does not create allocation advice, portfolio weights, buy/sell requests, trades, or an executor.

## Purpose

The layer validates watchlist records, blocks unsafe claims, and creates preview-only v4.49 candidate intake records for safe entries. A preview is not written anywhere and does not call v4.49 automatically.

VWCE and FTAW were pilot anchors only. Future candidates must pass the same v4.49 candidate intake plus v4.27-v4.47 evidence and manual review chain. No candidate becomes trusted, approved, or investable automatically.

## Running Reports And Tests

```powershell
python -m py_compile jarvis\jarvis_manual_candidate_watchlist_entry.py jarvis\jarvis_manual_candidate_watchlist_entry_report.py jarvis\tests\test_jarvis_manual_candidate_watchlist_entry.py jarvis\tests\test_jarvis_manual_candidate_watchlist_entry_report.py
python -m unittest jarvis.tests.test_jarvis_manual_candidate_watchlist_entry jarvis.tests.test_jarvis_manual_candidate_watchlist_entry_report -v
python -m jarvis.jarvis_manual_candidate_watchlist_entry_report
python -m jarvis.jarvis_manual_candidate_watchlist_entry_report --input jarvis\data\jarvis_manual_candidate_watchlist_entry.synthetic_multi.example.json
python -m jarvis.jarvis_candidate_intake_report
python -m jarvis.jarvis_candidate_intake_report --input jarvis\data\jarvis_candidate_intake.synthetic_multi.example.json
python -m jarvis.jarvis_phase1_command_index_report
python -m unittest discover jarvis/tests
```

## Future Real Evidence Entry

Future real evidence entry should remain manual: user-entered public references, manually reviewed facts, identity checks, manual verification decisions, manual approval review, dry-run planning, and final audit. The system must not fetch sources, download files, extract facts, ingest private files, approve assets, mutate registries, or execute trades automatically.
