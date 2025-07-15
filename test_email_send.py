from datetime import datetime
from outlook_reader import fetch_emails

# Use a fixed test time — e.g. yesterday at 9am
test_time = datetime.fromisoformat("2025-07-14T09:00:00+00:00")

emails = fetch_emails(test_time)

print(f"\n📬 Retrieved {len(emails)} emails.")
print("Preview:")
for i, email in enumerate(emails[:2], start=1):
    print(f"\n--- Email {i} ---\n{email[:500]}")
