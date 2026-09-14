# Architecture

```
Borrower submits documents (portal upload, email, fax)
      |
      v
Checklist generation (src/verification.py: required_documents())
  - base docs required for every loan
  - + W-2/pay stub OR tax returns/P&L, depending on employment type
  - + FHA-specific form, if loan type is FHA
      |
      v
Verification engine (src/verification.py: verify_application())
  - any required doc type missing entirely -> incomplete
  - all present, but one is illegible, stale (bank statement >60 days),
    or has a borrower-name mismatch -> needs_review
  - all present, fresh, legible, name matches -> ready
      |
      +--> incomplete   --> automated document request drafted
      |                     (src/document_request.py) -- no human paged,
      |                     this is a mechanical "you're missing X" case
      |
      +--> needs_review --> Slack alert with the specific reason
      |                     (src/notifications.py) -- illegibility, staleness,
      |                     and name mismatches all require a human to look
      |                     at the actual document, not just count files
      |
      +--> ready        --> moves to underwriting queue (not yet built,
      |                     see roadmap)
      |
      v
Evaluation (eval/run_eval.py)
  - outcome accuracy against a labeled synthetic test set
```

## Why the required-document checklist isn't user-configurable in this MVP

Which documents a loan file needs is largely dictated by investor and
agency guidelines (Fannie Mae, FHA), not by a lender's own preference.
Hardcoding the checklist logic here reflects that it's a compliance
requirement to get right, not a style choice -- a production version
would still want this centralized and versioned carefully, not exposed
as a freeform config a non-specialist could edit casually.

## Why "incomplete" and "needs_review" are handled completely differently

A missing document is a simple, mechanical gap -- the system can draft
the exact request and send it without human involvement. An illegible
scan, a stale bank statement, or a name mismatch all require someone to
actually look at the document and use judgment (is this legible enough
after all? is the mismatch a maiden-name issue or a real problem?) --
that's the line this project draws between automation and human review.

## What's stubbed vs. real

- Real: the checklist engine, the verification rules, an evaluation
  harness with real accuracy numbers on synthetic data, a working FastAPI
  endpoint, Slack alerting for review cases, and automated document-request
  drafting for incomplete files.
- Stubbed/roadmap: OCR/document-vision to actually assess legibility from
  a real scanned file (this MVP takes `is_legible` as a given input field
  rather than deriving it from an image), a real underwriting-queue
  hand-off, borrower-portal integration to receive documents automatically
  rather than via a structured API call, and freshness-window
  configuration per investor guideline rather than a single hardcoded
  60-day rule.
