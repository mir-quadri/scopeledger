# ScopeLedger — Verification record

Measured October 14, 2026. The project is a prototype with owner-reviewed decisions. It is not validated for automatic client billing or unattended classification.

## Application verification

- 23 Python domain/HTTP tests passed: source identity and coverage, schema errors, decimal money, invalid rate/effort values, approval/export gates, local persistence, deletion, JSON handling, origin checks and Host checks.
- DOM workflow checks passed with jsdom: sample load, effort and selection, $500 illustrative export, classification overrides, decimal rates, invalid-rate export blocking, source-change invalidation, local-only inference guidance and literal rendering of markup-like source text.
- JavaScript syntax check passed.
- Unit/HTTP tests use a fake model transport. They verify application behavior, not the model's understanding.
- GitHub Actions workflow is provided but has not been run on GitHub; no Copilot category is claimed.
- Full visual browser QA was unavailable under the supported preview tooling. DOM checks do not establish visual quality or replace a real-device review.

## Real Gemma evaluation

Runtime: Ollama 0.40.4, local Linux CPU. No cloud inference. Eight short, synthetic development cases were authored before the first run. The same cases were reused while refining the prompt, so the final result is **not a held-out accuracy benchmark**.

| Model / prompt | Cases matched | Shape/source failures | Result file |
|---|---:|---:|---|
| Gemma 3 1B / initial | 1 of 8 | 3 | `evals/results-gemma3-1b.json` |
| Gemma 3 4B / initial | 4 of 8 | 0 | `evals/results-gemma3-4b.json` |
| Gemma 3 4B / revised v2 | 6 of 8 | 0 | `evals/results-gemma3-4b-v2.json` |

The 1B baseline marked some explicit exclusions as included. Its other failures included nonexistent citations and missing results, which the validator rejected. Moving to 4B helped, but prompt revision was also needed: conflicting clauses, mixed work and vague quality language need distinct instructions. The revised prompt adds decision precedence and independent examples.

### Final v2 case results

| Case | Expected | Actual | Outcome |
|---|---|---|---|
| Explicit exclusion | change | change | Matched |
| Included revision | included | change | Failed |
| Vague quality request | clarify | clarify | Matched |
| Additional language | change | change | Matched |
| Embedded instruction + excluded booking | clarify, change | clarify, change | Matched |
| Mixed included and excluded work | clarify | change | Failed |
| Conflicting scope clauses | clarify | clarify | Matched |
| Clear included deliverable | included | included | Matched |

The two failures could lead an owner to quote for included work or fail to split a mixed request. The app exposes the source and allows owner overrides; it cannot infer correctness from source IDs. Do not automate client communication from these results.

Observed latency for v2 was 7.13–12.11 seconds per short case on this environment. This is a small run, includes the first model request, and is not a performance promise. Longer text or different hardware can be much slower.

Model tag identities observed during the runs:

- `gemma3:1b`: Q4_K_M, model tag digest `421cd334a96a4b602b9730eb38b86a9e29db9acb65a970571e636dac0ed0bd70`.
- `gemma3:4b`: Q4_K_M, model tag digest `4ee9b21b692acb7b93d3d40cd669393da815fa727b38e10e8ef784a47df78273`.

Tags and runtimes can change. Keep outputs and record your own model version when reproducing.

## End-to-end result

See `evals/e2e-result.json` for the real local-model API run, owner overrides and exported draft. The owner decisions in that test are explicitly supplied by the test, not attributed to the model. The test uses an ephemeral SQLite database and deletes the stored review after export.

## Before real use

Run on the target laptop, inspect a real browser at desktop and mobile widths, test longer and adversarial cases, and collect feedback from freelance developers using sanitized documents. No first-user, payment, revenue or quantified time-saving claim has been validated.
