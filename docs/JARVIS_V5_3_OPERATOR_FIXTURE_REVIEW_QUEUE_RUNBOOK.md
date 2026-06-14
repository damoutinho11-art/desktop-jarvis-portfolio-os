# J.A.R.V.I.S. v5.3 Operator Fixture Review Queue Runbook

v5.3 creates a deterministic manual operator fixture review queue from v5.2
import-preview metadata.

v5.0 remains sealed. v5.1 wired public fixture preparation. v5.2 dry-ran local
public fixture import. v5.3 adds the human-control layer between import-preview
metadata and any later research draft source routing.

## Why v5.3 Is Not Redundant

- v5.1 answers what fixtures should exist and where.
- v5.2 answers whether local fixture metadata can be inspected/import-previewed
  safely.
- v5.3 answers what an operator must manually review, accept, defer, or reject
  before downstream research routing.

v5.3 does not inspect real fixture files again. It consumes import-preview
metadata only.

## Decision Semantics

Allowed queue decisions include:

- `needs_operator_review`
- `accepted_for_research_draft_only`
- `deferred_missing_file`
- `deferred_stale_fixture`
- `deferred_manual_refresh_required`
- `rejected_unsafe_path`
- `rejected_unsupported_format`
- `rejected_unsupported_category`
- `rejected_forbidden_flags`
- `rejected_duplicate_fixture_id`
- `rejected_private_or_credential_risk`
- `rejected_not_public_only`

`accepted_for_research_draft_only` means the fixture metadata may later be used
as an unverified source reference in research draft preparation. It is not
evidence verification. It is not approval, trust, investability, recommendation,
allocation, a buy/sell signal, or a trade.

## Safety Boundary

v5.3 does not fetch, download, scrape, call APIs, use browser automation, create
schedulers, use broker integrations, ingest private files, run OCR, parse PDFs,
scrape HTML, extract evidence, verify evidence, approve assets, mutate registry
files, recommend investments, allocate, trade, or create an executor.

## Optional Write Contract

Default evaluation and reports write nothing.

The optional queue snapshot writer requires the exact authorization phrase:

`AUTHORIZE_V5_3_OPERATOR_FIXTURE_REVIEW_QUEUE_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE`

Even with the phrase, the writer may only write a queue snapshot and metadata
under:

`jarvis/local/public_source_fixtures/v5_3_operator_review_queue/`

Tests use temporary directories for write-path coverage. No committed local,
private, cache, verified, approved, or runtime output is produced by v5.3.

## Run Commands

```powershell
python.exe -m jarvis.jarvis_v5_3_operator_fixture_review_queue_report
python.exe -m jarvis.jarvis_v5_3_operator_fixture_review_queue_report --input jarvis\data\jarvis_v5_3_operator_fixture_review_queue.synthetic_complete.json
python.exe -m jarvis.jarvis_v5_3_operator_fixture_review_queue_report --input jarvis\data\jarvis_v5_3_operator_fixture_review_queue.synthetic_problematic.json
python.exe -m jarvis.jarvis_v5_3_operator_fixture_review_queue_report --input jarvis\data\jarvis_v5_3_operator_fixture_review_queue.synthetic_authorized_write.json
python.exe -m unittest jarvis.tests.test_jarvis_v5_3_operator_fixture_review_queue jarvis.tests.test_jarvis_v5_3_operator_fixture_review_queue_report
```

## What Not To Build Next

- no live fetch adapter inside v5.3
- no scraping
- no OCR
- no evidence verification
- no approval, trust, or investability
- no broker integration
- no executor

The suggested next phase is v5.4 Research Draft Source Router, still with no
evidence verification and no fetch. Only after that should an explicit authorized
public fetch stub be considered.
