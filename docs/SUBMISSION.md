---
title: "I built ScopeLedger to turn ‘one more thing’ into a clear scope conversation"
published: false
tags: devchallenge, hf26challenge, gemma, opensource
---

*This is a submission for the [Hacktoberfest Open-Source AI Challenge Week 2: Side Hustle](https://dev.to/challenges/hacktoberfest-week2-2026-10-12).*

> PUBLICATION CHECK: Add a judge-accessible demo or video URL below. The current hosted preview is private. Review the measured model results in VALIDATION.md and confirm a local demo before publishing. This draft has not been submitted to DEV.

## What I Built

“One more thing” sounds harmless. On a fixed-price project, five small requests can become a second project nobody agreed to pay for.

I built **ScopeLedger** for freelance developers and small agencies. Paste the agreed deliverables beside the client’s new requests. A local Gemma model proposes which asks are included, which may be additional work, and which need a conversation. Each suggestion comes with source lines you can check.

Then you decide. Override the classification, estimate the effort, set your rate and select the changes to quote. ScopeLedger exports a change-order draft. It does not send an invoice or assume the client has agreed.

My commercial hypothesis is a $19 one-time local tool, with an optional assisted setup. I have not validated that price or acquired a paying user. The next test is putting a real scope disagreement through it with freelance developers.

## Demo

**Add the public demo or video URL here before publication.**

The guided sample uses a five-page website, two revision rounds, excluded appointment booking and an English-only launch. Booking and Spanish support illustrate potential changes. A first color revision illustrates included work. “Make it more premium” illustrates a request that needs clarification.

Three hours for booking plus two for Spanish at an owner-entered $100/hour creates an illustrative $500 quote. That is arithmetic, not a claim of recovered revenue. The guided sample is hand-authored and labeled separately from live AI.

## Code

[ScopeLedger source code](https://github.com/mir-quadri/scopeledger)

The application is MIT-licensed. Gemma weights are downloaded separately under Google’s terms. The repository includes the local app, tests, evaluation fixtures and actual model-run results.

## How I Built It

I kept the stack small: Python’s standard library, SQLite, a dependency-free browser interface and Gemma through Ollama. The live model runs on the same machine as the app. No hosted AI API key is needed.

Gemma handles the part that simple matching cannot: deciding whether a new ask is actually covered by the agreed deliverables. Application code handles what should be deterministic: request IDs, source citations, complete coverage, owner approval and pricing.

I use structured JSON output. The validator rejects unknown source IDs, duplicate requests, missing requests and unexpected fields. Quotes are reconstructed from the source text rather than copied from model-generated quotations. Prices come only from the owner’s rate and quarter-hour estimates, calculated with decimal arithmetic.

There is an important boundary: a valid citation does not mean a correct interpretation. The owner can change every proposed classification, and the backend refuses to export an unreviewed change or a change without a positive estimate.

The first real model evaluation changed the design decision. Gemma 3 1B passed only 1 of my 8 development cases. It treated some explicitly excluded work as included. I retained those results and tested a larger model rather than presenting the sample walkthrough as proof that the AI worked. The revised 4B prompt matched 6 of the 8 development cases. It still mishandled an included revision and a request mixing included and excluded work. I retained both failures and made owner review central to the workflow. The 23 application/HTTP checks and the DOM workflow check passed separately. A real local-model API-to-export run also passed, using explicit owner decisions to produce a $500 sample draft.

The cases cover included work, exclusions, vague requests, a new language, mixed work, conflicting scope and an instruction embedded inside client text. This is a small development set, not evidence of production accuracy. The application and HTTP checks separately test pricing, persistence, export gates and input validation. A DOM workflow check covers the sample, overrides, export and source-change invalidation.

The prototype still has limits. It needs short, atomic text lines. It does not parse PDFs, track historical revision usage or establish legal obligations. Local SQLite data is not encrypted. Model judgment still needs a human review.

## Why Does Open Innovation Matter?

Client requests can contain pricing, delivery details and commercially sensitive information. Local open-weight inference lets the comparison run without sending those documents to a hosted AI provider.

It also lets me change the model without rewriting the review and pricing workflow. That mattered immediately: the smallest model was not reliable enough for the task. I could test a larger Gemma model against the same cases and inspect the difference.

This does not mean inference has no cost. A laptop still needs memory, processing time and power. The trade-off is control over where the work runs and which model performs it.

## My Agent Session

I used OpenAI coding assistance to design and implement this new project. `docs/BUILD_LOG.md` records the major decisions. DevRelay’s official installer returned HTTP 403 in this environment, so I have not claimed a DevRelay session or sticker. No private emails or client documents are included in the project.

## Prize Categories

**Best Use of Gemma** — Gemma performs the semantic scope comparison in the live local app. Real inference results are included in the evaluation report. I am not claiming categories for tools I did not use.

---

Built by Mir Quadri / Orchestrate AI. Started October 14, 2026. AI-assisted development and writing; reviewed by the author before publication.
