from outlook_reader import fetch_emails
from summariser import summarise_emails
from email_sender import send_to_teams

emails = fetch_emails(limit=20)  # Fetch 20 recent emails
print(f"\nFetched {len(emails)} emails from shared inbox.\n")

summary = summarise_emails(emails)
print("\n--- Summary ---\n")
print(summary)

# Optional: send to Teams
# send_to_teams(summary)


summary = summarise_emails(emails)
print("\n--- Summary ---\n")
print(summary)

send_to_teams(summary)


from auth import get_graph_token

token = get_graph_token()
print("✅ Access token retrieved successfully!")
print(token[:100] + "...")  # Print only first 100 chars
