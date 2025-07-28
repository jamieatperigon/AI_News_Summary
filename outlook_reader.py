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


# --- Fetch emails from inbox since last_run.txt ---
def fetch_emails(since_time: datetime):
    token = get_graph_token()
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    filter_clause = quote(f"receivedDateTime gt {since_time.isoformat()}")
    url = (
        f"{GRAPH_API_BASE}/users/{SHARED_MAILBOX}/mailFolders/inbox/messages"
        f"?$filter={filter_clause}"
        f"&$orderby=receivedDateTime desc"
        f"&$top=30"
    )

    all_emails = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch emails: {response.status_code} - {response.text}")

        data = response.json()
        messages = data.get("value", [])
        for msg in messages:
            try:
                subject = msg.get("subject") or "[No Subject]"
                body_html = (msg.get("body") or {}).get("content", "") or ""
                sender_email = (msg.get("sender") or {}).get("emailAddress", {}).get("address", "[Unknown Sender]").lower()
                message_id = msg.get("id", "[Missing ID]")

                # Convert HTML safely to plain text
                clean_body = strip_html(body_html) if body_html else "[No Content]"

                all_emails.append({
                    "id": message_id,
                    "subject": subject,
                    "sender": sender_email,
                    "body": clean_body  # Standardized key used by summariser.py
                })
            except Exception as e:
                print(f"[WARN] Skipping malformed email entry: {e}")
                continue

        # Handle pagination if more results exist
        url = data.get("@odata.nextLink")

    # Log unique senders for review (to help maintain DELETE/ARCHIVE lists in main.py)
        # Log all unique senders cumulatively
    log_file = "unique_senders_log.txt"
    existing_senders = set()
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            existing_senders = {line.strip().lower() for line in f if line.strip()}

    current_senders = {email["sender"].lower() for email in all_emails}
    all_senders = sorted(existing_senders.union(current_senders))

    with open(log_file, "w") as f:
        f.write("\n".join(all_senders))

    print(f"📄 Updated {log_file} with {len(current_senders)} new senders (total: {len(all_senders)})")


    return all_emails


# --- Get folder ID from folder display name ---
def get_folder_id(token, mailbox, folder_display_name):
    url = f"{GRAPH_API_BASE}/users/{mailbox}/mailFolders?$top=50"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"❌ Failed to fetch folders: {response.status_code} - {response.text}")

    folders = response.json().get("value", [])
    for folder in folders:
        if folder["displayName"] == folder_display_name:
            return folder["id"]

    raise Exception(f"❌ Folder '{folder_display_name}' not found in mailbox.")


# --- Move email to another folder ---
def move_email(token, message_id, mailbox, destination_folder_id):
    move_url = f"{GRAPH_API_BASE}/users/{mailbox}/messages/{message_id}/move"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {"destinationId": destination_folder_id}

    res = requests.post(move_url, headers=headers, json=body)
    if res.status_code == 201:
        print(f"✅ Email moved successfully: {message_id}")
    else:
        print(f"❌ Move failed for {message_id}")
        print(f"🔢 Status Code: {res.status_code}")
        print(f"📨 Response: {res.text}")


# --- Strip HTML to plain text ---
def strip_html(html_content):
    return BeautifulSoup(html_content, "html.parser").get_text().strip()
