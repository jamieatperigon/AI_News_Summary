from outlook_reader import fetch_emails, move_email, get_folder_id, SHARED_MAILBOX
from summariser import summarise_emails
from email_sender import send_summary_email
from auth import get_graph_token
import os
from datetime import datetime, timezone, timedelta

# --- Sender rules ---
ARCHIVE_SENDERS = {
    "noreply@news.bloomberg.com",
    "davidcarlin@substack.com",
    "info@eciu.net",
    "news@e.privateequityinternational.com",
    "ft@newsletters.ft.com"
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

# --- Load last run time ---
last_run_file = "last_run.txt"
try:
    with open(last_run_file, "r") as f:
        last_run_str = f.read().strip()
        last_run_time = datetime.fromisoformat(last_run_str)
except (FileNotFoundError, ValueError):
    print("⚠️ last_run.txt missing or invalid, defaulting to 3 days ago.")
    last_run_time = datetime.now(timezone.utc) - timedelta(days=3)

# --- Create subject title based on last_run.txt ---
weekday_name = last_run_time.strftime("%A")
date_str = last_run_time.strftime("%-d/%-m")
email_subject = f"🗞️ {weekday_name} News Update: {date_str}"

if __name__ == "__main__":
    try:
        # --- Fetch emails ---
        try:
            emails = fetch_emails(last_run_time)
            print(f"\nFetched {len(emails)} emails from shared inbox.\n")
        except Exception as e:
            print(f"❌ Failed to fetch emails: {e}")
            emails = []

        # --- Summarise emails ---
        summary, usage_summary, used_bodies = ("[No summary generated]", "[No usage data]", [])
        if emails:
            email_bodies = [e.get("body", "") for e in emails if e.get("body")]
            if email_bodies:
                try:
                    summary, usage_summary, used_bodies = summarise_emails(email_bodies)
                    print("\n--- Summary ---\n")
                    print(summary)
                except Exception as e:
                    print(f"❌ Summarisation failed: {e}")
            else:
                print("⚠️ No valid email bodies to summarise.")
        else:
            print("⚠️ No emails fetched, skipping summarisation.")

        # --- Get folder IDs safely ---
        token = None
        try:
            token = get_graph_token()
            SumArchive_folder_id = get_folder_id(token, SHARED_MAILBOX, "SummarisedArchive")
            Delete_folder_id = get_folder_id(token, SHARED_MAILBOX, "TestDelete")  # Temporary delete folder
            Unsorted_folder_id = get_folder_id(token, SHARED_MAILBOX, "Unsorted")  # For unknown senders
        except Exception as e:
            print(f"⚠️ Could not fetch folder IDs: {e}")
            SumArchive_folder_id = Delete_folder_id = Unsorted_folder_id = None

        # --- Send summary email ---
        if summary and summary != "[No summary generated]":
            try:
                send_summary_email(
                    subject=email_subject,
                    body_text=summary,
                    recipients=os.getenv("EMAIL_RECIPIENTS")
                )
                print("✅ Summary email sent successfully.")
            except Exception as e:
                print(f"❌ Failed to send summary email: {e}")
        else:
            print("⚠️ No summary email sent (no summary available).")

        # --- Move emails ---
        if token and all([SumArchive_folder_id, Delete_folder_id, Unsorted_folder_id]):
            unknown_senders = set()
            for email in emails:
                try:
                    sender = email.get("sender", "[Unknown Sender]")
                    message_id = email.get("id")
                    subject = email.get("subject", "[No Subject]")
                    is_used = email.get("body") in used_bodies

                    if not message_id:
                        print(f"⚠️ Skipping email with missing ID: {subject}")
                        continue

                    if is_used or sender in ARCHIVE_SENDERS:
                        print(f"📥 Archiving: {subject} [{sender}]")
                        move_email(token, message_id, SHARED_MAILBOX, SumArchive_folder_id)
                    elif sender in DELETE_SENDERS:
                        print(f"🗑 Deleting: {subject} [{sender}]")
                        move_email(token, message_id, SHARED_MAILBOX, Delete_folder_id)
                    else:
                        print(f"📥 Moving to Unsorted: {subject} [{sender}]")
                        move_email(token, message_id, SHARED_MAILBOX, Unsorted_folder_id)
                        unknown_senders.add(sender)
                except Exception as e:
                    print(f"⚠️ Failed to move email: {e}")

            # Log unknown senders for review
            if unknown_senders:
                with open("unknown_senders_log.txt", "w") as log_file:
                    log_file.write("\n".join(sorted(unknown_senders)))
                print(f"📄 Logged {len(unknown_senders)} unknown senders to unknown_senders_log.txt.")
        else:
            print("⚠️ Skipping email move (missing folder IDs).")

        # --- Record run time ---
        try:
            with open(last_run_file, "w") as f:
                now_utc = datetime.now(timezone.utc).isoformat()
                f.write(now_utc)
            print("✅ Run time recorded.")
        except Exception as e:
            print(f"⚠️ Failed to record run time: {e}")

        # --- Print usage summary ---
        print(usage_summary)

    except Exception as e:
        print(f"❌ Unhandled error in main: {e}")
