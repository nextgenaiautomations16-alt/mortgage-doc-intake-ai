"""
Runs the synthetic applications through verification and sends real
Slack alerts for every application needing manual review (illegible docs,
stale statements, name mismatches). Incomplete and ready files never
page anyone.

Run from repo root: python -m scripts.send_demo_alerts
Requires SLACK_WEBHOOK_URL to be set (falls back to console logging if not).
"""
import json
from pathlib import Path

from src.verification import verify_application
from src.notifications import send_review_alert

DATA_DIR = Path(__file__).parent.parent / "data"


def main():
    with open(DATA_DIR / "applications.json") as f:
        applications = json.load(f)

    sent = 0
    for app in applications:
        result = verify_application(app)
        if result.outcome == "needs_review":
            ok = send_review_alert(app, result)
            print(f"{app['application_id']} ({app['borrower_name']}): alert {'sent' if ok else 'FAILED'}")
            sent += 1

    print(f"\nDone — {sent} application(s) flagged for review and alerted.")


if __name__ == "__main__":
    main()
