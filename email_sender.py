import requests
import os
from dotenv import load_dotenv
from auth import get_graph_token as get_access_token

load_dotenv()

# takes inputs from varies files, put them together to form the actual email, then sends it
def send_summary_email(subject, body_text, recipients):
    token = get_access_token()
    user_email = os.getenv("SENDER_EMAIL")  # Add to .env
    url = f"https://graph.microsoft.com/v1.0/users/{user_email}/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    email_msg = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",  # Change to "HTML" if using HTML
                "content": body_text
            },
            "toRecipients": [
                {"emailAddress": {"address": r.strip()}} for r in recipients.split(",")
            ]
        }
    }

    response = requests.post(url, headers=headers, json=email_msg)
    if response.status_code != 202:
        raise Exception(f"❌ Email failed: {response.status_code}, {response.text}")
    print("✅ Email sent successfully.")
