import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

def send_to_teams(text):
    if not WEBHOOK_URL:
        raise ValueError("No TEAMS_WEBHOOK_URL found in .env")
    headers = {"Content-Type": "application/json"}
    payload = {"text": text}
    response = requests.post(WEBHOOK_URL, headers=headers, data=json.dumps(payload))
    if response.status_code != 200:
        raise Exception(f"Failed to send to Teams: {response.status_code}, {response.text}")
    print("✅ Message sent to Teams.")

send_to_teams("### ✅ Test Message\nThis is a plain test.")
