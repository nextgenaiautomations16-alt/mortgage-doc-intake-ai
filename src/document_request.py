"""
Drafts a request-for-documents message for incomplete files. Template-based
by default; a real deployment might swap in an LLM call for friendlier
phrasing the way LoadAudit AI's dispute_drafting.py could, but a fixed
template is arguably preferable here -- borrowers respond better to a
clear, consistent checklist than to varied AI-generated phrasing.
"""

TEMPLATE = """Subject: A few more documents needed for your loan application

Hi {borrower_name},

Thanks for your application! Before we can move your file to underwriting,
we still need the following:

{missing_list}

You can upload these directly through your borrower portal, or reply to
this email with them attached. Let us know if you have any questions.

Thanks,
Loan Processing Team
"""


def draft_document_request(app: dict, result) -> str:
    missing_list = "\n".join(f"  - {doc.replace('_', ' ').title()}" for doc in result.missing_documents)
    return TEMPLATE.format(borrower_name=app["borrower_name"], missing_list=missing_list)
