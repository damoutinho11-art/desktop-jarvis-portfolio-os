# J.A.R.V.I.S. v5.1 Public Source Fixture Wiring Runbook

v5.0 is sealed. v5.1 is a post-MVP operational layer for preparing local public-source fixture metadata.

v5.1 helps the operator answer:

- which public-source fixture files are needed
- where to place them locally
- which formats are accepted
- which source category each fixture belongs to
- how each fixture maps into the v4.61-v4.71 public research pipeline
- what must be validated before fixture import dry-runs
- what remains manual and forbidden

This is not live fetching, scraping, API integration, evidence extraction, evidence verification, recommendation, approval, allocation, trading, registry mutation, or execution.

## Local Template

Copy:

`templates/jarvis_public_source_fixtures.local.template.json`

to:

`jarvis/local/public_source_fixtures/public_source_fixtures.local.json`

The local file is for operator-managed public-source fixture metadata. Do not include credentials, private account data, broker screenshots, wallet information, private files, or downloaded private data.

## Accepted Formats

- `csv`
- `json`
- `txt`
- `md`
- `html_saved_public_page`
- `pdf_public_document_reference_only`
- `unknown`

For HTML and PDF references, v5.1 validates only metadata and path safety. It does not OCR, parse, scrape, extract evidence, or verify content.

## Run

```powershell
python -m jarvis.jarvis_v5_1_public_source_fixture_wiring_report
python -m jarvis.jarvis_v5_1_public_source_fixture_wiring_report --input jarvis\data\jarvis_v5_1_public_source_fixture_wiring.synthetic_complete.json
python -m unittest jarvis.tests.test_jarvis_v5_1_public_source_fixture_wiring jarvis.tests.test_jarvis_v5_1_public_source_fixture_wiring_report -v
```

## Optional Snapshot Write

The default report writes nothing. A local validation snapshot requires this exact phrase:

`AUTHORIZE_V5_1_PUBLIC_SOURCE_FIXTURE_WIRING_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE`

Even with authorization, the snapshot remains local, unverified, unapproved, and non-executable.

## What Not To Build Next

- no live fetch adapter inside v5.1
- no scraping
- no evidence verification
- no broker integration
- no executor
- no recommendation or allocation engine
- no registry mutation

## Suggested Next Phase

v5.2 should be either Explicit-Authorization Public Fetch Adapter Stub or Real Fixture Import Dry-Run, depending on operator decision. The no-execution invariant remains.
