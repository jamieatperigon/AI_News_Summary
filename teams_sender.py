import requests
import os
from dotenv import load_dotenv

load_dotenv()

def send_to_teams(summary_text: str):
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    if not webhook_url:
        raise ValueError("TEAMS_WEBHOOK_URL not set in .env file")

    payload = {
        "text": summary_text
    }

    response = requests.post(webhook_url, json=payload)
    if response.status_code != 200:
        raise Exception(f"Failed to send to Teams: {response.status_code}, {response.text}")
