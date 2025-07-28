from outlook_reader import fetch_emails
from summariser import summarise_emails
from email_sender import send_summary_email
import os
from datetime import datetime, timezone, timedelta
from auth import get_graph_token
from outlook_reader import move_email, ARCHIVE_SENDERS, DELETE_SENDERS, SHARED_MAILBOX, get_folder_id

# --- Create subject title --- normal subject maker, change for retro running
# today = datetime.now()
# weekday_name = today.strftime("%A")
# date_str = today.strftime("%-d/%-m")
# email_subject = f"🗞️ {weekday_name} News Update: {date_str}"

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
        # --- Load last run time ---
        last_run_file = "last_run.txt"
        try:
            with open(last_run_file, "r") as f:
                last_run_str = f.read().strip() or "2025-07-14T09:00:00+00:00"
                last_run_time = datetime.fromisoformat(last_run_str)
        except (FileNotFoundError, ValueError):
            print("⚠️ last_run.txt missing or invalid, defaulting to 3 days ago.")
            last_run_time = datetime.now(timezone.utc) - timedelta(days=3)

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
            try:
                email_bodies = [e.get("body", "") for e in emails if e.get("body")]
                if email_bodies:
                    summary, usage_summary, used_bodies = summarise_emails(email_bodies)
                    print("\n--- Summary ---\n")
                    print(summary)
                else:
                    print("⚠️ No valid email bodies to summarise.")
            except Exception as e:
                print(f"❌ Summarisation failed: {e}")
        else:
            print("⚠️ No emails fetched, skipping summarisation.")

        # --- Get folder IDs safely ---
        token = None
        try:
            token = get_graph_token()
            SumArchive_folder_id = get_folder_id(token, SHARED_MAILBOX, "SummarisedArchive")
            TestDelete_folder_id = get_folder_id(token, SHARED_MAILBOX, "TestDelete")
        except Exception as e:
            print(f"⚠️ Could not fetch folder IDs: {e}")
            SumArchive_folder_id, TestDelete_folder_id = None, None

        # --- Send summary email (only if summary exists) ---
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

        # --- Move used emails safely ---
        if token and (SumArchive_folder_id or TestDelete_folder_id):
            for email in emails:
                try:
                    if email.get("body") in used_bodies:
                        sender = email.get("sender", "[Unknown Sender]")
                        message_id = email.get("id")
                        subject = email.get("subject", "[No Subject]")

                        if not message_id:
                            print(f"⚠️ Skipping email with missing ID: {subject}")
                            continue

                        if sender in ARCHIVE_SENDERS:
                            print(f"📥 Archiving: {subject} [{sender}]")
                            move_email(token, message_id, SHARED_MAILBOX, SumArchive_folder_id)
                        else:
                            print(f"📥 Moving to delete (Test): {subject} [{sender}]")
                            move_email(token, message_id, SHARED_MAILBOX, TestDelete_folder_id)
                except Exception as e:
                    print(f"⚠️ Failed to move email: {e}")
        else:
            print("⚠️ Skipping email move (token or folders unavailable).")

        # --- Record run time safely ---
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
