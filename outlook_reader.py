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

# Addresses of senders we want to archive, not delete
ARCHIVE_SENDERS = {
    "noreply@news.bloomberg.com",
    "davidcarlin@substack.com",
    "info@eciu.net",
    # "alerts@altinvestor.com",
    "news@e.privateequityinternational.com",
    "FT@newsletters.ft.com"
}

#  Addresses of senders we want to delete
# FIX THESE OT CORRECT EMAILS IF WANT TO IMPLEMENT THIS FEATURE, should for security
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

# get emails from inbox, depending on datetime in last_run.txt
def fetch_emails(since_time: datetime):
    token = get_graph_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
# only takes emails that have been sent since it was last run
    filter_datetime = since_time.isoformat()
    filter_clause = quote(f"receivedDateTime gt {filter_datetime}")

# comment out the URL below for testing, and uncomment the second URL, and vice versa
    url = (
        f"{GRAPH_API_BASE}/users/{SHARED_MAILBOX}/mailFolders/inbox/messages"
        f"?$filter={filter_clause}"
        f"&$orderby=receivedDateTime desc"
        f"&$top=100"
    )

# 🔵 Use this line for testing – fetch most recent 20 emails regardless of time
    # url = (
    #     f"{GRAPH_API_BASE}/users/{SHARED_MAILBOX}/mailFolders/inbox/messages"
    #     f"?$orderby=receivedDateTime desc"
    #     f"&$top=6"
    # )

    response = requests.get(url, headers=headers)

    # error catching
    if response.status_code != 200:
        raise Exception(f"Failed to fetch emails: {response.status_code} - {response.text}")

# puts data from emails into dictionary, to be used partly for GPT prompt and partly for accurate email filing
    data = response.json()
    messages = data.get("value", [])
    email_data = []
    for msg in messages:
        subject = msg.get("subject", "[No Subject]")
        body_preview = msg.get("body", {}).get("content", "")
        sender_email = msg.get("sender", {}).get("emailAddress", {}).get("address", "").lower()
        message_id = msg.get("id")

        email_data.append({
            "id": message_id,
            "subject": subject,
            "sender": sender_email,
            "content": f"{subject}\n{strip_html(body_preview)}"
        })
    return email_data

# getting folder ID from folder name so that emails can be sent to correct folder
def get_folder_id(token, mailbox, folder_display_name):
    url = f"{GRAPH_API_BASE}/users/{mailbox}/mailFolders"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    # error catching
    if response.status_code != 200:
        raise Exception(f"❌ Failed to fetch folders: {response.status_code} - {response.text}")
    # returnign the folder ID
    folders = response.json().get("value", [])
    for folder in folders:
        if folder["displayName"] == folder_display_name:
            return folder["id"]
    # error catching
    raise Exception(f"❌ Folder '{folder_display_name}' not found in mailbox.")

def move_email(token, message_id, mailbox, destination_folder_id):
    # logic to move email
    move_url = f"{GRAPH_API_BASE}/users/{mailbox}/messages/{message_id}/move"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "destinationId": destination_folder_id
    }

    res = requests.post(move_url, headers=headers, json=body)
    # Error catching, more info for debugging
    if res.status_code == 201:
        print(f"✅ Email moved successfully: {message_id}")
    else:
        print(f"❌ Move failed for {message_id}")
        print(f"🔢 Status Code: {res.status_code}")
        print(f"📨 Response: {res.text}")

# sends clean text to OpenAI so it doesnt get confused by links
def strip_html(html_content):
    return BeautifulSoup(html_content, "html.parser").get_text().strip()
