# J.A.R.V.I.S. v5.2 Real Fixture Import Dry-Run Runbook

v5.2 inspects operator-managed local public fixture files before any downstream
fixture use. It is a deterministic dry-run layer only.

It does not fetch, download, scrape, call APIs, use a browser, schedule tasks, use
broker integrations, ingest private files, parse private account data, verify
evidence, approve assets, mutate registries, create allocation recommendations,
create buy/sell requests, trade, or create an executor.

## What v5.2 Does

- Accepts explicit JSON configuration for local public fixture records.
- Requires fixture paths to stay under `jarvis/local/public_source_fixtures`.
- Validates path, source category, fixture type, format, and safety controls.
- Checks file existence and whether the path is a file.
- Computes deterministic size, modification timestamp, and SHA-256 fingerprints.
- Reads only shallow metadata:
  - CSV: row count and header columns.
  - JSON: top-level type, top-level keys, and item count.
  - TXT/MD: line count.
  - HTML/PDF: presence, size, timestamp, and hash only.
- Produces import-preview and downstream pipeline-mapping summaries in memory.

## What v5.2 Does Not Do

- No live fetch adapter inside v5.2.
- No scraping.
- No OCR.
- No PDF parsing.
- No HTML scraping.
- No evidence extraction.
- No evidence verification.
- No screening.
- No research scoring.
- No recommendation.
- No approval, trust, or investability decision.
- No registry mutation or candidate write.
- No allocation, portfolio weight, buy/sell signal, or trade.
- No broker, Lightyear, LHV, crypto exchange, wallet, or executor integration.

## Optional Write Contract

The default path writes nothing. Reports write nothing.

The optional snapshot writer requires the exact authorization phrase:

`AUTHORIZE_V5_2_REAL_FIXTURE_IMPORT_DRY_RUN_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE`

Even with the phrase, the writer may only write a dry-run snapshot and metadata
under:

`jarvis/local/public_source_fixtures/v5_2_import_dry_run/`

Tests use temporary directories for write-path coverage. No committed classified,
imported, verified, approved, or private output is produced by v5.2.

## Run Commands

```powershell
python.exe -m jarvis.jarvis_v5_2_real_fixture_import_dry_run_report
python.exe -m jarvis.jarvis_v5_2_real_fixture_import_dry_run_report --input jarvis\data\jarvis_v5_2_real_fixture_import_dry_run.synthetic_complete.json
python.exe -m jarvis.jarvis_v5_2_real_fixture_import_dry_run_report --input jarvis\data\jarvis_v5_2_real_fixture_import_dry_run.synthetic_problematic.json
python.exe -m jarvis.jarvis_v5_2_real_fixture_import_dry_run_report --input jarvis\data\jarvis_v5_2_real_fixture_import_dry_run.synthetic_authorized_write.json
python.exe -m unittest jarvis.tests.test_jarvis_v5_2_real_fixture_import_dry_run jarvis.tests.test_jarvis_v5_2_real_fixture_import_dry_run_report
```

## Next Efficient Stage

The next efficient stage is v5.3 operator fixture review queue or an explicit
authorized public fetch stub. Do not build screening, evidence verification,
approval, broker integration, registry mutation, or an executor inside v5.2.
