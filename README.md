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

## 📬 How to Change Email Recipients

To update who receives the final email summaries:

1. Open the `.env` file in the project root.
2. Locate the line:
   ```env
   EMAIL_RECIPIENTS=jamie@perigonpartners.co.uk
   ```
3. To add another recipient:
   - Add a comma after the existing email:
     ```env
     EMAIL_RECIPIENTS=jamie@perigonpartners.co.uk,
     ```
   - Then add the full new email address (no quotes):
     ```env
     EMAIL_RECIPIENTS=jamie@perigonpartners.co.uk,new.person@example.com
     ```

✅ Use commas to separate multiple email addresses.  
🚫 Do **not** use quotation marks around the emails.

---

## 🚀 Running This Project Locally

### ✅ Step-by-Step for New Users

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YOUR_ORG/perigon-email-summariser.git
   cd perigon-email-summariser
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   - Create a `.env` file in the root folder:
     ```env
     OPENAI_API_KEY=sk-...
     TENANT_ID=your-tenant-id
     CLIENT_ID=your-client-id
     TEAMS_WEBHOOK_URL=https://...
     EMAIL_RECIPIENTS=your@email.com
     ```

4. **Authenticate with Microsoft:**
   ```bash
   python auth.py
   ```

5. **Run the full script manually:**
   ```bash
   python main.py
   ```

---

## ⏰ Automation on Railway

This project runs automatically:

- **Every Monday at 09:05 AM**
- **Every Thursday at 09:05 AM**

### 🛠️ Railway Setup

- Railway's cron-like scheduler triggers:
  ```bash
  python main.py
  ```

- Deploy to Railway via:
  ```bash
  railway up
  ```

### 📚 Resources to Learn

If you're new to these tools, search for:
- `Railway Python deploy`
- `Railway scheduling cron job`
- `crontab.guru` (for cron syntax help)

---

## 📌 Editing Email Archiving Rules

To change how emails are treated after processing:

1. Open `outlook_reader.py`.
2. Scroll to the bottom.
3. Locate the sender lists:
   ```python
   ARCHIVE_SENDERS = [
       "Bloomberg Green", 
       "David Carlin", 
       ...
   ]

   DELETE_SENDERS = [
       "FT Climate Capital", 
       "Edie.net", 
       ...
   ]
   ```

✏️ Simply add or remove names to these lists.  
📌 Keep the formatting exactly the same.

---

## 📞 Help & Contact

If anything breaks, seems confusing, or you're new to Python and want to learn:

**Contact: Jamie Thomson**  
📧 Jamie.wlt@outlook.com  
📱 07708012486
