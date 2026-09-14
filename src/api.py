"""
Minimal FastAPI service exposing the document-stacking pipeline.

Run: uvicorn src.api:app --reload
Then: POST an application to /applications/verify
"""
from fastapi import FastAPI
from pydantic import BaseModel

from .verification import verify_application
from .notifications import send_review_alert
from .document_request import draft_document_request

app = FastAPI(title="Mortgage Doc Intake AI")


class SubmittedDocument(BaseModel):
    doc_type: str
    date_received: str
    is_legible: bool = True
    borrower_name_on_doc: str


class Application(BaseModel):
    application_id: str
    borrower_name: str
    loan_type: str
    employment_type: str
    submitted_documents: list[SubmittedDocument]


@app.post("/applications/verify")
def verify(application: Application):
    app_dict = application.model_dump()
    result = verify_application(app_dict)

    response = {
        "application_id": result.application_id,
        "outcome": result.outcome,
        "reasons": result.reasons,
    }

    if result.outcome == "needs_review":
        response["slack_alert_sent"] = send_review_alert(app_dict, result)
    elif result.outcome == "incomplete":
        response["document_request_draft"] = draft_document_request(app_dict, result)

    return response


@app.get("/health")
def health():
    return {"status": "ok"}
