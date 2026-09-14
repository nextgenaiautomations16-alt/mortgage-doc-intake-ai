"""
Generates synthetic mortgage loan applications, each with a document
checklist and a set of submitted documents, plus a labeled ground truth
of how the file should be triaged.

Run: python generate_synthetic_applications.py
Outputs: applications.json, ground_truth.csv
"""
import json
import random
import csv
from pathlib import Path
from datetime import date, timedelta

random.seed(23)

BORROWER_NAMES = [
    "J. Alvarez", "M. Chen", "R. Patel", "K. Novak", "T. Osei",
    "S. Kowalski", "L. Rossi", "D. Nakamura", "A. Fischer", "P. Delgado",
]
LOAN_TYPES = ["conventional", "FHA"]
EMPLOYMENT_TYPES = ["W2", "self_employed"]

TODAY = date(2026, 9, 14)

# Base documents required for every application
BASE_REQUIRED = ["photo_id", "bank_statement", "credit_authorization"]
W2_REQUIRED = ["pay_stub", "w2_form"]
SELF_EMPLOYED_REQUIRED = ["tax_return_1", "tax_return_2", "profit_loss_statement"]
FHA_EXTRA_REQUIRED = ["fha_case_number_form"]

# Outcome categories:
#   ready       -> every required doc present, fresh, legible, name matches
#   incomplete  -> at least one required document type is missing entirely
#   needs_review -> all docs present but one has a real problem (stale,
#                   illegible, or borrower name mismatch)

N_APPLICATIONS = 26


def required_documents(loan_type: str, employment_type: str) -> list:
    docs = list(BASE_REQUIRED)
    docs += W2_REQUIRED if employment_type == "W2" else SELF_EMPLOYED_REQUIRED
    if loan_type == "FHA":
        docs += FHA_EXTRA_REQUIRED
    return docs


def make_application(app_id, outcome):
    borrower = random.choice(BORROWER_NAMES)
    loan_type = random.choice(LOAN_TYPES)
    employment_type = random.choice(EMPLOYMENT_TYPES)
    required = required_documents(loan_type, employment_type)

    submitted = []
    for doc_type in required:
        submitted.append({
            "doc_type": doc_type,
            "date_received": str(TODAY - timedelta(days=random.randint(1, 20))),
            "is_legible": True,
            "borrower_name_on_doc": borrower,
        })

    if outcome == "incomplete":
        # drop one required document entirely
        drop_idx = random.randrange(len(submitted))
        submitted.pop(drop_idx)
    elif outcome == "needs_review_stale":
        # bank statements older than 60 days are considered stale
        idx = next(i for i, d in enumerate(submitted) if d["doc_type"] == "bank_statement")
        submitted[idx]["date_received"] = str(TODAY - timedelta(days=random.randint(75, 120)))
    elif outcome == "needs_review_illegible":
        idx = random.randrange(len(submitted))
        submitted[idx]["is_legible"] = False
    elif outcome == "needs_review_name_mismatch":
        idx = random.randrange(len(submitted))
        submitted[idx]["borrower_name_on_doc"] = random.choice(
            [n for n in BORROWER_NAMES if n != borrower]
        )

    return {
        "application_id": f"APP{6000 + app_id}",
        "borrower_name": borrower,
        "loan_type": loan_type,
        "employment_type": employment_type,
        "submitted_documents": submitted,
    }


def expected_bucket(outcome_detail: str) -> str:
    if outcome_detail == "incomplete":
        return "incomplete"
    if outcome_detail.startswith("needs_review"):
        return "needs_review"
    return "ready"


def main():
    plan = (
        ["incomplete"] * 6
        + ["needs_review_stale"] * 4
        + ["needs_review_illegible"] * 3
        + ["needs_review_name_mismatch"] * 3
        + ["ready"] * (N_APPLICATIONS - 16)
    )
    random.shuffle(plan)

    applications = []
    ground_truth_rows = []

    for i, outcome_detail in enumerate(plan):
        app = make_application(i, outcome_detail)
        applications.append(app)
        ground_truth_rows.append({
            "application_id": app["application_id"],
            "expected_outcome": expected_bucket(outcome_detail),
            "detail": outcome_detail,
        })

    out_dir = Path(__file__).parent
    with open(out_dir / "applications.json", "w") as f:
        json.dump(applications, f, indent=2)
    with open(out_dir / "ground_truth.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["application_id", "expected_outcome", "detail"])
        writer.writeheader()
        writer.writerows(ground_truth_rows)

    print(f"Generated {N_APPLICATIONS} applications.")


if __name__ == "__main__":
    main()
