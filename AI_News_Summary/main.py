from outlook_reader import fetch_emails
from summariser import summarise_emails
from email_sender import send_summary_email
import os
from datetime import datetime, timezone, timedelta
from auth import get_graph_token
from outlook_reader import move_email, ARCHIVE_SENDERS, DELETE_SENDERS, SHARED_MAILBOX
from outlook_reader import get_folder_id


# Create subject title
today = datetime.now()
weekday_name = today.strftime("%A")
date_str = today.strftime("%-d/%-m")
email_subject = f"🗞️ {weekday_name} News Update: {date_str}"

if __name__ == "__main__":

    # --- Load last run time ---
    last_run_file = "last_run.txt"
    try:
        with open(last_run_file, "r") as f:
            last_run_str = "2025-07-14T09:00:00+00:00"
            last_run_time = datetime.fromisoformat(last_run_str)
    except FileNotFoundError:
        print("⚠️ last_run.txt not found, defaulting to 3 days ago.")
        last_run_time = datetime.now() - timedelta(days=3)

    # --- Fetch emails ---
    emails = fetch_emails(last_run_time)
    print(f"\nFetched {len(emails)} emails from shared inbox.\n")

    # --- Summarise emails ---
    summary, usage_summary, used_bodies = summarise_emails([e["body"] for e in emails])
    print("\n--- Summary ---\n")
    print(summary)

    # --- Get folder IDs for archiving/deleting ---
    token = get_graph_token()
    SumArchive_folder_id = get_folder_id(token, SHARED_MAILBOX, "SummarisedArchive")
    TestDelete_folder_id = get_folder_id(token, SHARED_MAILBOX, "TestDelete")

    # --- Send summary email ---
    send_summary_email(
        subject=email_subject,
        body_text=summary,
        recipients=os.getenv("EMAIL_RECIPIENTS")
    )

    # --- Move only used emails ---
    used_ids = []
    for email in emails:
        if email["body"] in used_bodies:
            sender = email["sender"]
            message_id = email["id"]
            subject = email["subject"]
            used_ids.append(message_id)

            if sender in ARCHIVE_SENDERS:
                print(f"📥 Archiving: {subject} [{sender}]")
                move_email(token, message_id, SHARED_MAILBOX, SumArchive_folder_id)
            else:
                print(f"📥 Would be deleted (Testing): {subject} [{sender}]")
                move_email(token, message_id, SHARED_MAILBOX, TestDelete_folder_id)

    # --- Record run time ---
    with open(last_run_file, "w") as f:
        now_utc = datetime.now(timezone.utc).isoformat()
        f.write(now_utc)

    print(usage_summary)
