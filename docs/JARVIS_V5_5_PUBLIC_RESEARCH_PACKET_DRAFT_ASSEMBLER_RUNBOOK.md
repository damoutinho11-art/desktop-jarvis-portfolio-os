# J.A.R.V.I.S. v5.5 Public Research Packet Draft Assembler Runbook

v5.5 consumes v5.4 research-draft source route-row metadata and assembles
unverified public research packet drafts for human review only.

v5.0 remains sealed. v5.1 wired public fixture preparation. v5.2 dry-ran local
public fixture import. v5.3 created the operator fixture review queue. v5.4
routed accepted review metadata into unverified research-draft source references.
v5.5 groups those references into public research packet drafts without reading
external fixture files, fetching, verifying, approving, recommending, allocating,
or trading.

## Why v5.5 Is Not Redundant

- v5.1 answers what fixtures should exist and where.
- v5.2 answers whether local fixture metadata can be import-previewed safely.
- v5.3 answers what the operator reviewed, accepted, deferred, or rejected.
- v5.4 answers which reviewed metadata can become unverified research-draft
  source references.
- v5.5 answers how those unverified source references can be grouped into
  unverified public research packet drafts for later human review.

v5.5 does not repeat source routing, fixture wiring, file inspection, or
operator queue decisions.

## Boundary

J.A.R.V.I.S. does not fetch, download, scrape, call APIs, run browser automation,
read external fixture files, OCR, parse PDFs, or parse HTML in v5.5. It consumes
route-row metadata only.

Packet draft assembly is not evidence extraction. It is not evidence
verification. It is not source truth verification. It is not approval, trust,
investability, recommendation, allocation, a buy/sell signal, or trade execution.

## Packet Draft Outputs

Allowed outputs are:

- `public_research_packet_draft`
- `deferred_public_research_packet_draft`
- `manual_fix_required_public_research_packet_draft`
- `blocked_public_research_packet_draft`

`public_research_packet_draft` means only that unverified source-route metadata
has been grouped into a draft packet for human review.

## Optional Write Contract

Default evaluation and reports write nothing.

The optional snapshot writer requires the exact authorization phrase:

`AUTHORIZE_V5_5_PUBLIC_RESEARCH_PACKET_DRAFT_ASSEMBLER_LOCAL_ONLY_NO_FETCH_NO_VERIFY_NO_TRADE`

Even with the phrase, the writer may only write a packet-draft snapshot and
metadata under:

`jarvis/local/public_source_fixtures/v5_5_public_research_packet_drafts/`

Tests use temporary directories for write-path coverage. No committed local,
private, cache, verified, approved, or runtime output is produced by v5.5.

## Run Commands

```powershell
python.exe -m jarvis.jarvis_v5_5_public_research_packet_draft_assembler_report
python.exe -m jarvis.jarvis_v5_5_public_research_packet_draft_assembler_report --input jarvis\data\jarvis_v5_5_public_research_packet_draft_assembler.synthetic_complete.json
python.exe -m jarvis.jarvis_v5_5_public_research_packet_draft_assembler_report --input jarvis\data\jarvis_v5_5_public_research_packet_draft_assembler.synthetic_problematic.json
python.exe -m jarvis.jarvis_v5_5_public_research_packet_draft_assembler_report --input jarvis\data\jarvis_v5_5_public_research_packet_draft_assembler.synthetic_authorized_write.json
python.exe -m unittest jarvis.tests.test_jarvis_v5_5_public_research_packet_draft_assembler jarvis.tests.test_jarvis_v5_5_public_research_packet_draft_assembler_report
```

## What Not To Build Next

- no live fetch adapter inside v5.5
- no scraping
- no OCR
- no PDF parsing
- no HTML parsing
- no evidence extraction
- no evidence verification
- no source truth verification
- no approval, trust, or investability
- no recommendation, allocation, or trading
- no broker integration
- no executor

The suggested next phase is v5.6 Public Research Packet Human Review Queue,
still with no evidence verification and no fetch.
