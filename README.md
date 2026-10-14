# ScopeLedger
### Keep good work profitable.

Public repository: https://github.com/mir-quadri/scopeledger

Owner-private guided preview: https://scopeledger.mirquadri.chatgpt.site (not yet a judge-accessible demo).

A local-first scope review and change-order workspace for freelance developers and small agencies. Built from scratch by Mir Quadri, with AI coding assistance, starting October 14, 2026 for Hacktoberfest Week 2: Side Hustle. This is a new project, not a continuation of an existing app.

## Run the real app

1. Install [Python 3.10+](https://www.python.org/downloads/) and [Ollama](https://ollama.com/download).
2. Start Ollama. In a terminal, run `ollama pull gemma3:4b`.
3. Unzip or clone this project, open its folder, and run `python3 server.py` (Windows: `py server.py`).
4. Open **http://127.0.0.1:8765**. Paste agreed scope and client requests, one item per line.
5. Choose **Review with local Gemma**. Inspect every suggestion and source citation. Set your hourly rate, estimate hours, and select changes to include. Export the draft and discuss it with your client.

No Python packages, API key or paid service required. The app is single-user and binds only to loopback. Live analysis sends documents only to the fixed local Ollama endpoint. Initial software/model downloads require internet; normal analysis does not require cloud AI. Local operating costs and hardware requirements still apply.

### Models

Default: `gemma3:4b` (about 3.4 GB model download). Allow several GB of working memory beyond the download and expect CPU inference to take time. The smaller 1B baseline performed poorly in our development cases and is not the recommended model. The 4B model still makes mistakes; inspect `docs/VALIDATION.md`.

Select any separately downloaded model with `SCOPELEDGER_MODEL`. For example, after `ollama pull gemma3:12b`, start with `SCOPELEDGER_MODEL=gemma3:12b python3 server.py`. That larger model has not been evaluated here and needs substantially more memory. In PowerShell, use `$env:SCOPELEDGER_MODEL="gemma3:12b"` and then `py server.py`.

Gemma is **open-weight**, subject to Google's Gemma terms; it is not distributed under this project's MIT license. No model weights are bundled. See the model card and terms before your own deployment.

## What works

- Local Gemma comparison with structured JSON output.
- Included / potential change / clarification classification, one result per request.
- Exact request and agreed-scope lines reconstructed by code, never copied from generated quotations.
- Validation rejects unknown IDs, missing requests, duplicated citations, malformed JSON and invented schema fields.
- Owner overrides, quarter-hour estimates and decimal-safe USD pricing.
- Backend approval gate: only owner-selected changes with positive effort can enter an export.
- Markdown change-order draft, marked as pending client acceptance. No email, invoice, payment or work authorization is sent.
- Local SQLite review history, automatic latest-review restoration, source fingerprints and audit events. Delete a review from the workspace to remove its rows and audit events.
- Responsive static guided demo. Its hand-authored sample is prominently labeled and never presented as AI inference.

**Storage:** analyses, source lines and owner decisions are stored unencrypted on your computer in `~/.scopeledger/ledger.sqlite3`. Override with `SCOPELEDGER_DB`. OS file permissions are restricted where supported. This is a local prototype, not a hosted multi-user service. Back up or delete the database as you would other client work. Delete is logical deletion; SQLite pages/backups may retain bytes.

## Verification

```sh
python3 -m unittest discover -s tests -v
node --check dist/app.js
```

Optional DOM workflow checks, requiring Node 20+:

```sh
npm ci
npm test
```

Real-model semantic evaluation (Ollama must be running):

```sh
python3 evals/run.py --model gemma3:4b --output evals/my-results.json
```

Unit/HTTP tests use a fake model transport and prove application behavior, not model quality. `evals/results-gemma3-1b.json`, when present, contains actual local-model outputs; it is distinct from the hand-authored demo. Read `docs/VALIDATION.md` for measured results and limits. Cases are small development fixtures, not an independent benchmark.

## Project map

- `core.py`: prompt, schema, source checks, owner review and pricing.
- `server.py`: loopback API, local SQLite history, same-origin controls.
- `dist/`: dependency-free interface and guided demo.
- `tests/`: domain, HTTP and DOM checks.
- `evals/`: eight labeled semantic cases and real-inference runner.
- `docs/PRODUCT_AND_ARCHITECTURE.md`: product scope, design, architecture and next milestones.
- `docs/SUBMISSION.md`: DEV submission draft; resolve explicit remaining items before publication.
- `docs/DEMO_SCRIPT.md`: concise demonstration recording guide.

## Limits and next steps

This prototype compares supplied text, not legal enforceability. It does not parse PDFs, monitor inboxes, count historical revision rounds, infer whether an agreement was signed, split mixed requests reliably, or independently establish client intent. IDs prove which source lines exist; they do not prove the model understood them. Model mistakes and prompt injection remain possible. Owners must verify suggestions. Large documents are bounded to 12,000 characters and 30 non-empty lines per source; use short atomic lines.

Commercial hypothesis: a $19 one-time local tool or a $49 assisted setup. No paid users, interviews, revenue or time savings have been validated. Future work should follow interviews and real usage, not add sponsor integrations for their own sake.

## Attribution and license

Original application code and design: Mir Quadri / Orchestrate AI, with OpenAI coding assistance. MIT license for this repository. Python standard library supplies the server and database API. Ollama is the separately installed inference runtime; Google Gemma supplies the separately downloaded model. jsdom is an optional development dependency. No copied product code, client documents or proprietary employer material is included. Sample businesses and requests are fictional.

References:
- [Challenge and current categories](https://dev.to/challenges/hacktoberfest-week2-2026-10-12)
- [Week 2 official rules](https://dev.to/page/hacktoberfest-week2-2026-10-12-contest-rules)
- [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs)
- [Gemma 3 on Ollama](https://ollama.com/library/gemma3)
- [Google Gemma terms](https://ai.google.dev/gemma/terms)
- [DevRelay](https://devrelay.com/): optional session/submission helper; not required by the app and not installed in the build environment because its installer returned HTTP 403.

Any updates after October 18, 2026, 11:59 p.m. PDT must be dated and identified here for challenge transparency.
