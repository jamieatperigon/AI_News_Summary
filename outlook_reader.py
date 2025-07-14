import os
import requests
from dotenv import load_dotenv
from auth import get_graph_token

load_dotenv()

SHARED_MAILBOX = os.getenv("SHARED_MAILBOX")
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

def fetch_emails(limit=25):
    token = get_graph_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Build URL to fetch messages from the shared inbox
    url = f"{GRAPH_API_BASE}/users/{SHARED_MAILBOX}/mailFolders/Inbox/messages?$top={limit}&$orderby=receivedDateTime desc"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch emails: {response.status_code} - {response.text}")

    data = response.json()
    messages = data.get("value", [])

    email_texts = []
    for msg in messages:
        subject = msg.get("subject", "[No Subject]")
        body_preview = msg.get("body", {}).get("content", "")

        email_texts.append(f"{subject}\n{strip_html(body_preview)}")

    return email_texts

def strip_html(html_content):
    """Very simple HTML remover for email bodies"""
    from bs4 import BeautifulSoup
    return BeautifulSoup(html_content, "html.parser").get_text().strip()
