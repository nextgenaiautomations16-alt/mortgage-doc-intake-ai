# Demo Script (3-4 minutes)

**0:00-0:30 — The problem**
"Before a loan file can go to underwriting, someone has to confirm every
required document is present, current, legible, and actually belongs to
the borrower. This 'document stacking' step is manual, and depends on
what the loan type and the borrower's employment type require. This is
Mortgage Doc Intake AI — it automates that check."

**0:30-1:15 — Show the eval**
Run `python -m eval.run_eval` live. Point out the three distinct
outcomes: ready, incomplete, needs_review.

**1:15-2:00 — Show an incomplete file**
Hit the API with a file missing a required W-2. Show it returns
`incomplete` with an automatically drafted request to the borrower — no
human involved, since a missing document is a mechanical gap, not a
judgment call.

**2:00-2:45 — Show a needs_review file**
Hit the API with a file that has a stale bank statement. Show it
escalates to Slack with the specific reason, and explain why staleness/
illegibility/name-mismatch cases are handled differently from missing
documents — these need an actual human look.

**2:45-3:30 — Close**
"Sixth project in the series — same rules-engine-plus-human-in-the-loop
architecture, applied to a document-heavy compliance workflow that's
close to real-estate lending, which pairs naturally with the lead-response
project earlier in the series."
