# Build record

October 14, 2026 — New project started during the Week 2 entry window.

- Read the DEV reminder in Mir's connected email and the current challenge page, template and official rules.
- Selected Side Hustle use case: scope creep for freelance developers. No previous Mir project source was reused.
- Built an original static interface, zero-dependency Python API, local SQLite persistence, schema/source validation, owner review and decimal-safe pricing.
- Implemented separate hand-authored sample mode; no sample is claimed as live inference.
- Added domain/HTTP tests, DOM workflow checks and eight real-model evaluation cases.
- Downloaded the Ollama runtime and Gemma 3 1B model for actual local inference. Model artifacts are excluded from the deliverable.
- Initial Gemma 3 1B evaluation passed only 1/8 development cases. Retained the results and escalated to testing a larger model.
- Gemma 3 4B with the initial prompt passed 4/8 cases. Added explicit precedence rules for contradictions, mixed requests, vague quality language and revision allowances; reran the same development set and retained both runs.
- DevRelay official installer returned HTTP 403 in this environment. No DevRelay installation, login, sticker or shared session is claimed. This file is a build summary, not a DevRelay transcript.

- Revised Gemma 3 4B prompt passed 6/8 development cases; included revision and mixed work remained failures. Selected 4B as the default and documented those limits.
- Real local-model API → database → owner review → $500 sample draft → deletion passed.
- 23 application/HTTP tests, JavaScript syntax and DOM workflow checks passed.

See VALIDATION.md for final measured results. Entries after the deadline must be identified in README.md.

October 14, 2026 — Created public repository `mir-quadri/scopeledger` and transferred the application, documentation, evaluations and CI configuration. Deployment identity, credentials, runtime databases and model weights are excluded. DEV submission remains unpublished.
