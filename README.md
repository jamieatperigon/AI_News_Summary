# 📨 ESG Outlook Inbox Summariser

This Python-based tool automates the process of reading a shared Outlook inbox, summarising emails relevant to ESG and regulatory developments, and posting the output via email. It is built to run automatically twice a week via cloud deployment.

> Created by Jamie Walker, Summer 2025 Intern  
> 📧 Jamie.wlt@outlook.com  
> 📱 07708012486

---

## 🌐 What This Project Does

- ✅ Connects to a **shared Microsoft Outlook inbox**.
- ✅ Checks for **new emails since the last run**.
- ✅ Uses **OpenAI GPT** to:
  - Detect which emails are relevant.
  - Extract headlines, sections (themes), and sources.
  - Group and deduplicate content into clear summaries.
- ✅ Sends output to various **Emails**.
- ✅ Archives or deletes emails based on rules.
- ✅ Runs automatically on **Railway** (cloud) **twice a week**.

---

## 🔧 Tech Stack / Tools Used

| Tool/Library         | Purpose                                                                 |
|----------------------|-------------------------------------------------------------------------|
| Python               | Programming language                                                    |
| Microsoft Graph API  | Accessing emails, archiving, moving them                            |
| OpenAI API           | Summarising and structuring content                                     |
| Railway              | Cloud platform for automated scheduled runs                             |
| dotenv (`.env`)      | Storing secrets (API keys, tokens)                                      |
| `requests`           | Sending API calls to Microsoft Graph                                    |
| `beautifulsoup4`     | (Unused now – originally for parsing email HTML, can be removed)        |

### 👉 What to Google if you're new

- "How Microsoft Graph API works"
- "Device code flow authentication Microsoft Graph"
- "What is OpenAI GPT and how to call it via Python"
- "Railway app Python deployment"
- "How to run a Python script on a schedule (cronjob)"

---

## 🗂 File-by-File Breakdown

### `main.py`
Entry point. Runs the entire flow:
- Authenticates with Microsoft
- Reads emails
- Summarises them using OpenAI
- Sends output to email
- Archives or deletes processed emails

> 📌 Only run this file manually if debugging. Usually triggered by Railway on schedule.

---

### `auth.py`
Handles Microsoft login using **device code flow** (user logs in via browser once).
- Uses `requests` to get an OAuth token.
- Stores the token in memory (for use in other functions).

🔍 Learn more: [Microsoft Graph Auth Docs](https://learn.microsoft.com/en-us/graph/auth-v2-user)

---

### `outlook_reader.py`
Handles:
- Reading from a **shared inbox** (`/users/{shared_account}/mailFolders/inbox/messages`)
- Filtering only **unread emails** since the last run
- Storing a timestamp in `last_run.txt`
- Moving emails to Archive or Deleted folders based on sender

🗂 Senders to **archive** or **delete** are hardcoded near the bottom.

---

### `summariser.py`
This is where OpenAI is used:
- **Step 1**: Classifies relevance of each email and extracts:
  - Headline
  - Section (e.g., “AI & Tech”, “Climate”)
  - Source
- **Step 2**: Groups & deduplicates entries, formats them into a markdown summary.

Prompt engineering is done carefully here to:
- Keep output **brief and punchy**
- Ensure **grouping by section** (Regulation, ESG Research, etc.)

✏️ You can tweak the prompt in `summariser.py` if the style needs adjusting.

---

How to change emails that recieve update:
- in the .env file
- under the EMAIL_RECIPIENTS=jamie@perigonpartners.co.uk
- add a comma to the previous email (EMAIL_RECIPIENTS=jamie@perigonpartners.co.uk,)
- type in the next email, the full address (do not put it in "")


**🚀 Running This Project Locally**

# ✅ Step-by-Step for New Users

    Clone the repo to your local machine:
        git clone https://github.com/YOUR_ORG/perigon-email-summariser.git
        cd perigon-email-summariser

Install dependencies:
    pip install -r requirements.txt

Set up .env file:
    Create a .env file in the project root with:
        OPENAI_API_KEY=sk-...
        TENANT_ID=...
        CLIENT_ID=...
        TEAMS_WEBHOOK_URL=https://...

Authenticate once:
    python auth.py

Run the full script:
    python main.py


**⏰ Automation on Railway**

This script is scheduled to run every:
Monday at 09:05 AM
Thursday at 09:05 AM

# 🛠️ Config:
    Railway’s cron-like scheduler triggers python main.py.
    Deploy via Railway using the web UI or railway up.

# 📚 Learn (Search in Google/ChatGPT):
    Railway Docs
    Cron syntax guide


**📌 Editing Email Rules**

If someone in the future wants to:
    Change which emails get archived or deleted...
        → Open outlook_reader.py, scroll to the end, and edit ARCHIVE_SENDERS and DELETE_SENDERS.
    Follow the sytax as it is previously...

**📞 Help & Contact**
If you have any issues, want help understanding the code, or need guidance on how any of the technologies work:

Contact Jamie Thomson
📧 Jamie.wlt@outlook.com
📱 07708012486
