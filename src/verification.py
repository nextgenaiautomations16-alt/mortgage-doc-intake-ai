"""
Deterministic document-stacking verification engine.

Same principle as the rest of the series: the required-document checklist
and the completeness/freshness/legibility checks are explicit rules a loan
processor can point to -- not a model's subjective read of "does this
file look ready." That matters here because sending an incomplete file to
underwriting wastes real time on both sides, and the checklist itself is
often dictated by investor/agency guidelines (Fannie Mae, FHA) that are
not up for interpretation.
"""
from dataclasses import dataclass, field
from datetime import date

BANK_STATEMENT_FRESHNESS_DAYS = 60

BASE_REQUIRED = ["photo_id", "bank_statement", "credit_authorization"]
W2_REQUIRED = ["pay_stub", "w2_form"]
SELF_EMPLOYED_REQUIRED = ["tax_return_1", "tax_return_2", "profit_loss_statement"]
FHA_EXTRA_REQUIRED = ["fha_case_number_form"]


@dataclass
class StackingResult:
    application_id: str
    outcome: str  # "ready", "incomplete", or "needs_review"
    reasons: list = field(default_factory=list)
    missing_documents: list = field(default_factory=list)


def required_documents(loan_type: str, employment_type: str) -> list:
    docs = list(BASE_REQUIRED)
    docs += W2_REQUIRED if employment_type == "W2" else SELF_EMPLOYED_REQUIRED
    if loan_type == "FHA":
        docs += FHA_EXTRA_REQUIRED
    return docs


def verify_application(app: dict, today: date = None) -> StackingResult:
    today = today or date(2026, 9, 14)
    app_id = app["application_id"]
    borrower_name = app["borrower_name"]
    required = required_documents(app["loan_type"], app["employment_type"])
    submitted_by_type = {d["doc_type"]: d for d in app["submitted_documents"]}

    missing = [doc_type for doc_type in required if doc_type not in submitted_by_type]
    if missing:
        return StackingResult(
            app_id, "incomplete",
            [f"Missing required document(s): {', '.join(missing)}"],
            missing,
        )

    reasons = []

    for doc_type in required:
        doc = submitted_by_type[doc_type]

        if not doc.get("is_legible", True):
            reasons.append(f"{doc_type} was submitted but is not legible")

        if doc.get("borrower_name_on_doc") != borrower_name:
            reasons.append(
                f"{doc_type} shows borrower name '{doc.get('borrower_name_on_doc')}', "
                f"which does not match the application name '{borrower_name}'"
            )

        if doc_type == "bank_statement":
            received = date.fromisoformat(doc["date_received"])
            age_days = (today - received).days
            if age_days > BANK_STATEMENT_FRESHNESS_DAYS:
                reasons.append(f"Bank statement is {age_days} days old, exceeding the {BANK_STATEMENT_FRESHNESS_DAYS}-day freshness window")

    if reasons:
        return StackingResult(app_id, "needs_review", reasons, [])

    return StackingResult(app_id, "ready", [], [])


def run_batch(applications: list) -> list:
    return [verify_application(app) for app in applications]
