"""
Mock Email Sender Tool: Simulates sending emails without actual SMTP.

Used in Phase 1 for testing orchestration logic without external dependencies.
In Phase 7, swap this for RealEmailSenderTool (SMTP/API) — agents won't know the difference.
"""

from typing import Any, Dict
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class MockEmailSenderTool:
    """Mock email sender tool that logs instead of actually sending."""

    name = "email_sender"
    capability_tags = ["email_sending", "notification"]

    def __init__(self):
        """Initialize with sent emails log."""
        self.sent_emails = []

    async def call(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a mock email send operation.

        Args:
            input_data: {
                "to": str (recipient email),
                "subject": str,
                "body": str,
                "html": str (optional),
                "cc": list (optional),
                "bcc": list (optional)
            }

        Returns:
            Success response with mock email ID.
        """
        to = input_data.get("to")
        subject = input_data.get("subject", "")
        body = input_data.get("body", "")
        html = input_data.get("html")
        cc = input_data.get("cc", [])
        bcc = input_data.get("bcc", [])

        # Validate required fields
        if not to or not subject:
            return {
                "success": False,
                "error": "Missing required fields: 'to' and 'subject'",
            }

        # Mock email ID
        email_id = f"MOCK-EMAIL-{len(self.sent_emails) + 1:05d}"
        timestamp = datetime.now().isoformat()

        # Log the email
        email_record = {
            "id": email_id,
            "to": to,
            "cc": cc,
            "bcc": bcc,
            "subject": subject,
            "body": body,
            "html": html,
            "sent_at": timestamp,
            "status": "sent",
        }

        self.sent_emails.append(email_record)

        logger.info(f"MockEmailSenderTool: Email {email_id} sent to {to}")
        logger.debug(f"Email: {json.dumps(email_record, indent=2)}")

        return {
            "success": True,
            "message": f"Email sent successfully",
            "email_id": email_id,
            "sent_at": timestamp,
        }

    async def get_sent_emails(self) -> list:
        """
        Retrieve all sent emails (for testing/verification).

        Returns:
            List of all sent email records.
        """
        return self.sent_emails

    async def clear_sent_emails(self) -> None:
        """Clear all sent emails log (for testing)."""
        self.sent_emails.clear()
