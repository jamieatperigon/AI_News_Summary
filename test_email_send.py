import os
from email_sender import send_summary_email

send_summary_email(
    subject="✅ Test ESG Summary Email",
    body_text="This is a plain text test of the email summary system.",
    recipients=os.getenv("EMAIL_RECIPIENTS")
)
