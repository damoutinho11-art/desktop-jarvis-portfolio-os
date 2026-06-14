# J.A.R.V.I.S. v5.4 Research Draft Source Router Runbook

v5.4 routes v5.3 operator fixture review metadata into unverified research-draft
source references only.

v5.0 remains sealed. v5.1 wired public fixture preparation. v5.2 dry-ran local
public fixture import. v5.3 created the operator fixture review queue. v5.4
connects reviewed fixture metadata to future research packet draft preparation
without fetching, verifying, approving, recommending, allocating, or trading.

## Why v5.4 Is Not Redundant

- v5.1 answers what fixtures should exist and where.
- v5.2 answers whether local fixture metadata can be import-previewed safely.
- v5.3 answers what the operator reviewed, accepted, deferred, or rejected.
- v5.4 answers which reviewed metadata can become unverified research-draft
  source references and which must remain blocked or deferred.

v5.4 does not repeat fixture wiring, file inspection, or review-queue decisions.

## Boundary

J.A.R.V.I.S. does not fetch, download, scrape, call APIs, run browser automation,
or read external fixture files in v5.4. It consumes review-row metadata only.

Source routing is not evidence verification. It is not source truth verification.
It is not approval, trust, investability, recommendation, allocation, a buy/sell
signal, or trade execution.

## Router Outputs

Allowed outputs are:

- `research_draft_source_reference`
- `deferred_source_reference`
- `blocked_source_reference`
- `manual_fix_required_reference`
- `manual_refresh_required_reference`

`research_draft_source_reference` means only that metadata may be referenced in
future research draft packet preparation.

## Optional Write Contract

Default evaluation and reports write nothing.

The optional snapshot writer requires the exact authorization phrase:

`AUTHORIZE_V5_4_RESEARCH_DRAFT_SOURCE_ROUTER_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE`

Even with the phrase, the writer may only write a source-router snapshot and
metadata under:

`jarvis/local/public_source_fixtures/v5_4_research_draft_source_router/`

Tests use temporary directories for write-path coverage. No committed local,
private, cache, verified, approved, or runtime output is produced by v5.4.

## Run Commands

```powershell
python.exe -m jarvis.jarvis_v5_4_research_draft_source_router_report
python.exe -m jarvis.jarvis_v5_4_research_draft_source_router_report --input jarvis\data\jarvis_v5_4_research_draft_source_router.synthetic_complete.json
python.exe -m jarvis.jarvis_v5_4_research_draft_source_router_report --input jarvis\data\jarvis_v5_4_research_draft_source_router.synthetic_problematic.json
python.exe -m jarvis.jarvis_v5_4_research_draft_source_router_report --input jarvis\data\jarvis_v5_4_research_draft_source_router.synthetic_authorized_write.json
python.exe -m unittest jarvis.tests.test_jarvis_v5_4_research_draft_source_router jarvis.tests.test_jarvis_v5_4_research_draft_source_router_report
```

## What Not To Build Next

- no live fetch adapter inside v5.4
- no scraping
- no OCR
- no evidence verification
- no source truth verification
- no approval, trust, or investability
- no broker integration
- no executor

The suggested next phase is v5.5 Public Research Packet Draft Assembler, still
with no evidence verification and no fetch. Only after that should an explicit
authorized public fetch stub be considered.
