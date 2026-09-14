# Mortgage Doc Intake AI

**An AI agent that automates mortgage document stacking** — checks a borrower's submitted documents against the required checklist for their loan type and employment status, drafts an automated request for anything missing, and flags anything with a real problem (illegible, stale, or a name mismatch) for a human to review.

Sixth project in a series applying the same deterministic-rules-plus-human-in-the-loop architecture to different back-office workflows. See also [LoadAudit AI](https://github.com/nextgenaiautomations16-alt/loadaudit-ai), [Carrier Vet AI](https://github.com/nextgenaiautomations16-alt/carrier-vet-ai), [Claims Intake AI](https://github.com/nextgenaiautomations16-alt/claims-intake-ai), [Support Triage AI](https://github.com/nextgenaiautomations16-alt/support-triage-ai), and [Lead Response AI](https://github.com/nextgenaiautomations16-alt/lead-response-ai).

## The problem

Before a loan file can move to underwriting, someone has to confirm every required document is present, current, legible, and actually belongs to the borrower. Which documents are required varies by loan type (conventional vs. FHA) and employment type (W-2 vs. self-employed), which makes the checklist itself easy to get wrong manually — and a missing or stale document discovered late in the process causes real delays.

## What this does

1. **Build the checklist** — determines exactly which documents a file needs based on loan type and employment type
2. **Verify, deterministically** — any required document missing entirely → incomplete; all present but one is illegible, stale (bank statements older than 60 days), or has a borrower-name mismatch → needs review; everything checks out → ready for underwriting
3. **Handle each outcome differently, on purpose** — incomplete files get an automatically drafted document request with zero human involvement (a missing file is a mechanical gap); needs-review files page a human in Slack with the specific reason, since illegibility and mismatches genuinely need a person to look at the actual document
4. **Evaluate honestly** — a labeled synthetic dataset and eval harness score outcome accuracy

## Quickstart

```bash
git clone <your-repo-url>
cd mortgage-doc-intake-ai
pip install -r requirements.txt

# 1. generate the synthetic dataset (26 applications across all outcomes)
python data/generate_synthetic_applications.py

# 2. run the evaluation harness
python -m eval.run_eval

# 3. run the API and try it yourself
uvicorn src.api:app --reload
# then POST to http://127.0.0.1:8000/applications/verify
```

Set `SLACK_WEBHOOK_URL` to actually post review-flagged applications to a channel; without it, alerts print to the console.

## Evaluation results (on the included synthetic dataset)

```
Total applications evaluated: 26
Outcome accuracy: 100.0%  (26/26)
```

## Architecture

See [docs/architecture.md](docs/architecture.md) for the full pipeline and why incomplete and needs-review files are handled completely differently.

## Demo

See [docs/demo_script.md](docs/demo_script.md) for a 3-4 minute walkthrough script.

## Tech stack

Python, FastAPI, flat-file/JSON data store.

## Roadmap

- Add OCR/document-vision to derive legibility from a real scanned file instead of taking it as a given input
- Hand off "ready" files to a real underwriting queue/LOS system
- Integrate with an actual borrower portal instead of a structured API call
- Make the freshness-window rule configurable per investor guideline rather than a single hardcoded 60-day rule
