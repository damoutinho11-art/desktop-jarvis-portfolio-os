# J.A.R.V.I.S. v4.52 Manual Candidate Intake Review Decision

v4.52 records a human review decision about a v4.51 manual candidate intake bridge preview packet. It is a report-only decision recorder.

The allowed decisions are:

- `DEFER`
- `REJECT`
- `ACCEPT_FOR_CANDIDATE_INTAKE_DRY_RUN`

`ACCEPT_FOR_CANDIDATE_INTAKE_DRY_RUN` means only that a human accepted the v4.51 preview for a future explicit dry-run candidate intake packet stage. It is not asset approval, trust, investability, evidence collection, evidence verification, allocation advice, a buy/sell request, a trade, registry mutation, or execution authorization.

## Safety Boundary

The recorder does not write candidate intake files. It does not mutate the registry or candidate registry. It does not collect evidence. It does not verify evidence. It does not promote verified evidence. It does not approve, trust, or invest candidates. It does not fetch or download sources. It does not ingest private files.

VWCE and FTAW remain pilot anchors only. Any future candidate must pass the same v4.27-v4.47 evidence and manual review chain.

## Commands

Default blocked example:

```powershell
python -m jarvis.jarvis_manual_candidate_intake_review_decision_report
```

Synthetic defer example:

```powershell
python -m jarvis.jarvis_manual_candidate_intake_review_decision_report --input jarvis\data\jarvis_manual_candidate_intake_review_decision.synthetic_defer.example.json
```

Synthetic accept-for-dry-run example:

```powershell
python -m jarvis.jarvis_manual_candidate_intake_review_decision_report --input jarvis\data\jarvis_manual_candidate_intake_review_decision.synthetic_accept.example.json
```

Focused tests:

```powershell
python -m unittest jarvis.tests.test_jarvis_manual_candidate_intake_review_decision jarvis.tests.test_jarvis_manual_candidate_intake_review_decision_report -v
```

## Future Stage

A future stage may build an explicit dry-run candidate intake packet or command contract, but only if separately requested. That future stage must still preserve the no-registry-mutation, no-approval, no-execution boundary unless a later manual contract explicitly changes scope.
