from datetime import datetime
import os
import requests
from dotenv import load_dotenv
from auth import get_graph_token
from bs4 import BeautifulSoup
from urllib.parse import quote

load_dotenv()

SHARED_MAILBOX = os.getenv("SHARED_MAILBOX")
GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"

# 🔁 Use actual email addresses, not display names
ARCHIVE_SENDERS = {
    "noreply@news.bloomberg.com",
    "davidcarlin@substack.com",
    "info@eciu.net",
    # "alerts@altinvestor.com",
    "news@e.privateequityinternational.com",
    "FT@newsletters.ft.com"
}

DELETE_SENDERS = {
    "news@edie.net",
    "firstft@ft.com",
    "instant@ft.com",
    "newsletter@sifted.eu",
    "climatecapital@ft.com",
    "insights@mckinsey.com",
    "stats@worldpopulationreview.com",
    "notifications@gov.uk",
    "updates@fca.org.uk"
}

def fetch_emails(since_time: datetime):
    token = get_graph_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    filter_datetime = since_time.isoformat()
    filter_clause = quote(f"receivedDateTime gt {filter_datetime}")
    url = (
        f"{GRAPH_API_BASE}/users/{SHARED_MAILBOX}/mailFolders/inbox/messages"
        f"?$filter={filter_clause}"
        f"&$orderby=receivedDateTime desc"
        f"&$top=100"
    )

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch emails: {response.status_code} - {response.text}")

    data = response.json()
    messages = data.get("value", [])

    email_data = []

    for msg in messages:
        subject = msg.get("subject", "[No Subject]")
        body_preview = msg.get("body", {}).get("content", "")
        sender_email = msg.get("sender", {}).get("emailAddress", {}).get("address", "").lower()
        message_id = msg.get("id")

        print(f"📥 Loaded email: {subject} from {sender_email}")

        email_data.append({
            "id": message_id,
            "subject": subject,
            "sender": sender_email,
            "content": f"{subject}\n{strip_html(body_preview)}"
        })

    return email_data

def get_folder_id(token, mailbox, folder_display_name):
    url = f"{GRAPH_API_BASE}/users/{mailbox}/mailFolders"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"❌ Failed to fetch folders: {response.status_code} - {response.text}")

    folders = response.json().get("value", [])
    for folder in folders:
        if folder["displayName"] == folder_display_name:
            return folder["id"]

    raise Exception(f"❌ Folder '{folder_display_name}' not found in mailbox.")

def move_email(token, message_id, mailbox, destination_folder_id):
    move_url = f"{GRAPH_API_BASE}/users/{mailbox}/messages/{message_id}/move"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "destinationId": destination_folder_id
    }

    res = requests.post(move_url, headers=headers, json=body)
    if res.status_code == 201:
        print(f"✅ Email moved successfully: {message_id}")
    else:
        print(f"❌ Move failed for {message_id}")
        print(f"🔢 Status Code: {res.status_code}")
        print(f"📨 Response: {res.text}")

def strip_html(html_content):
    return BeautifulSoup(html_content, "html.parser").get_text().strip()
