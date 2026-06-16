# J.A.R.V.I.S. v14.0 Daily Operator Entrypoint

## Verdict

v14.0 adds a daily-use root entrypoint for the released product-mode local operator stack.

It is convenience polish only.

It does not add strategy, recommendation, evidence, data refresh, UI, voice, broker, credential, order, or trading logic.

## Daily Command

From the repository root:

    python .\jarvis_operator.py --daily

This runs the v13.0 launcher, generates the local command-center HTML, and asks:

    Jarvis, summarize operator status.

## Safety Check Command

    python .\jarvis_operator.py --safety-check

This verifies that the execution wall still blocks:

    Jarvis, buy BTC now.

Expected result:

    BLOCKED
    No execution action was taken.

## Custom Typed Jarvis Command

    python .\jarvis_operator.py --voice-command "Jarvis, explain missing data."

## Demo

    python .\jarvis_operator.py --demo

## Safety Boundary

J.A.R.V.I.S. prepares information.

Diogo performs the final real-world buy outside J.A.R.V.I.S.

v14.0 confirms:

- no broker connection;
- no credentials;
- no private account ingestion;
- no buy request;
- no order placement;
- no trade execution;
- no microphone;
- no speech-to-text;
- no text-to-speech;
- no web server;
- no network listener.

## Next Stage

v14_1_operator_readme_and_shortcuts_polish

Reason:

After the root entrypoint exists, the next useful step is README/runbook polish only.
