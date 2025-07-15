from outlook_reader import fetch_emails
from summariser import summarise_emails
from email_sender import send_summary_email
import os
from datetime import datetime, timezone
from auth import get_graph_token
from outlook_reader import move_email, ARCHIVE_SENDERS, DELETE_SENDERS, SHARED_MAILBOX
from outlook_reader import get_folder_id


# Create subject title
today = datetime.now()
weekday_name = today.strftime("%A")     # e.g. "Monday"
date_str = today.strftime("%-d/%-m")     # e.g. "15/7" (no leading zeroes)
email_subject = f"🗞️ {weekday_name} News Update: {date_str}"


if __name__ == "__main__":
    # ALL of your run logic goes here

    # FETCH EMAILS
    # --- Load last run time ---
    last_run_file = "last_run.txt"
    try:
        with open(last_run_file, "r") as f:
            # last_run_str = f.read().strip()
            last_run_str = "2025-07-14T09:00:00+00:00"
            last_run_time = datetime.fromisoformat(last_run_str)
    except FileNotFoundError:
        print("⚠️ last_run.txt not found, defaulting to 3 days ago.")
        last_run_time = datetime.now() - timedelta(days=3)
    emails = fetch_emails(last_run_time)  # Fetch recent emails
    print(f"\nFetched {len(emails)} emails from shared inbox.\n")

    # ADJUST IF TESTING 
    summary, usage_summary = summarise_emails(emails) #turn off to test without GPT, turn line below on
    # summary = "This is your summary, no openAI call" #turn on for testing, provided line above is turned off

    # GPT output
    print("\n--- Summary ---\n")
    print(summary)

    token = get_graph_token()
    # print("✅ Access token retrieved successfully!") can enable if you want, it works, i dont need to see it every time

    archive_folder_id = get_folder_id(token, SHARED_MAILBOX, "SummarisedArchive")

    # send email
    send_summary_email(
    subject=email_subject,
    body_text=summary,
    recipients=os.getenv("EMAIL_RECIPIENTS")
    )

    for email in emails:
        sender = email["sender"]
        message_id = email["id"]
        subject = email["subject"]

        if sender in ARCHIVE_SENDERS:
            print(f"📥 Archiving: {subject} [{sender}]")
            move_email(token, message_id, SHARED_MAILBOX, archive_folder_id)
        else:
            move_email(token, message_id, SHARED_MAILBOX, "deletedItems")
        # elif sender in DELETE_SENDERS:
        #     print(f"🗑️ Deleting: {subject} [{sender}]")
        #     move_email(token, message_id, SHARED_MAILBOX, "deletedItems")


    # Overwrite last sent email datetime
    with open(last_run_file, "w") as f:
        now_utc = datetime.now(timezone.utc).isoformat()
        f.write(now_utc)

    print(usage_summary)  # Only works if GPT is enabled


