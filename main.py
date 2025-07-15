from outlook_reader import fetch_emails
from summariser import summarise_emails
from email_sender import send_summary_email
import os
from datetime import datetime, timezone
from auth import get_graph_token


# Create subject title
today = datetime.now()
weekday_name = today.strftime("%A")     # e.g. "Monday"
date_str = today.strftime("%-d/%-m")     # e.g. "15/7" (no leading zeroes)
email_subject = f"🗞️ {weekday_name} News Update: {date_str}"

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

summary, usage_summary = summarise_emails(emails)
# summary = "This is your summary, no openAI call"
print("\n--- Summary ---\n")
print(summary)

# check tokens ?/
token = get_graph_token()
print("✅ Access token retrieved successfully!")
# print(token[:100] + "...")  # Print only first 100 chars

# send email
send_summary_email(
subject=email_subject,
body_text=summary,
recipients=os.getenv("EMAIL_RECIPIENTS")
)

# Overwrite last sent email
with open(last_run_file, "w") as f:
    now_utc = datetime.now(timezone.utc).isoformat()
    f.write(now_utc)

print(usage_summary)

