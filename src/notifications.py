"""
Posts applications needing manual review to Slack. "Incomplete" files
don't page a human -- they get an automated document request instead
(src/document_request.py). "Ready" files don't page anyone either; they
move straight to the underwriting queue. Only genuine judgment calls
(illegible docs, stale statements, name mismatches) interrupt a person.
"""
import os
import requests

SLACK_WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL")


def send_review_alert(app: dict, result) -> bool:
    reasons_text = "\n".join(f"• {r}" for r in result.reasons)

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"📋 File needs review — {app.get('borrower_name')} ({app.get('application_id')})"}
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Loan type:*\n{app.get('loan_type', 'N/A')}"},
                {"type": "mrkdwn", "text": f"*Employment:*\n{app.get('employment_type', 'N/A')}"},
            ]
        },
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Why it needs a look:*\n{reasons_text}"}
        },
    ]

    payload = {"text": f"Application {app.get('application_id')} needs review", "blocks": blocks}

    if not SLACK_WEBHOOK_URL:
        print("[notifications] SLACK_WEBHOOK_URL not set — logging alert instead of sending:")
        print(reasons_text)
        return True

    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"[notifications] Failed to send Slack alert: {e}")
        return False
