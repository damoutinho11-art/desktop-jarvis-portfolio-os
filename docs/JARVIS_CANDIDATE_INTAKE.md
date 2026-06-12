# J.A.R.V.I.S. Candidate Intake

v4.49 adds a record-only candidate intake and watchlist expansion layer. It lets J.A.R.V.I.S. describe many possible candidate assets and route them toward the existing Phase 1 real-evidence pipeline.

Candidate intake is not approval. It is not trust. It is not investability. It is not evidence verification. It is not registry mutation. It is not allocation advice, a buy/sell request, or trade execution.

## Purpose

The intake layer captures manually entered candidate metadata, validates required fields, blocks unsafe claims, maps each asset type to conservative evidence expectations, and points valid candidates toward the existing v4.27-v4.47 pipeline.

VWCE and FTAW were pilot anchors only. They are not privileged hardcoded assumptions. Any future candidate must pass the same evidence, identity, manual verification, manual approval, dry-run, and final audit chain before becoming trusted. No asset becomes investable or trusted automatically.

## How It Connects To v4.48

v4.48 documents the completed Phase 1 backend gate chain and command index. v4.49 uses that completed chain as the destination route for candidate intake records. It does not add another approval gate and does not change existing v4.27-v4.48 behavior.

## Evidence Expectations

ETF and fund candidates require instrument identity, issuer/provider identity, domicile or listing, fee/cost reference, holdings or strategy reference, risk reference, and official product/page document references.

Stock candidates require instrument identity, issuer identity, listing exchange, financial reporting reference, risk reference, and official investor-relations or exchange references.

Bond, cash-equivalent, crypto, commodity, and other candidates use conservative placeholder mappings with manual review and official-source identity checks. Unknown or `other` asset types remain review-needed and do not become approved.

## Running Reports And Tests

```powershell
python -m py_compile jarvis\jarvis_candidate_intake.py jarvis\jarvis_candidate_intake_report.py jarvis\tests\test_jarvis_candidate_intake.py jarvis\tests\test_jarvis_candidate_intake_report.py
python -m unittest jarvis.tests.test_jarvis_candidate_intake jarvis.tests.test_jarvis_candidate_intake_report -v
python -m jarvis.jarvis_candidate_intake_report
python -m jarvis.jarvis_candidate_intake_report --input jarvis\data\jarvis_candidate_intake.synthetic_multi.example.json
python -m jarvis.jarvis_phase1_command_index_report
python -m unittest discover jarvis/tests
```

## Future Real Evidence Entry

Future real evidence entry should remain manual. Users should enter public references, manually confirm identity, manually record verification decisions, and then rely on the existing dry-run and audit reports. The system must not fetch sources, download documents, extract facts, ingest private files, approve assets, mutate registries, or execute trades automatically.
