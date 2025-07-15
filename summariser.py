import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# connecting to the API
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarise_emails(email_bodies: list[str]) -> tuple[str, str]:
# GPT prompt
    prompt = f"""
You are a news summariser for an ESG consultancy in the UK.

You will receive a list of raw email contents containing ESG-related news, research, regulatory updates, or industry developments.

Your job is to produce a visually engaging, concise summary email, broken into sections.

---

🧠 Instructions:
1. Summarise only the most relevant items — those that directly impact ESG reporting or strategic decision-making, especially:
   - UK and European regulation or policy
   - Banking, EV infrastructure, private equity
   - ESG disclosure standards or implementation guidance
   - Tangible climate-related developments (e.g. losses, weather, tipping points)
2. Avoid quoting politicians or general opinion pieces. Ignore "Minister says X", "CEO calls for Y".
3. Choose only the best stories. Limit each section to:
   - REGULATION & POLICY: max 6
   - ESG RESEARCH & STATS: max 3
   - AI & TECH: max 2
   - CLIMATE & NATURAL RESOURCES: max 2
   - OTHER: max 4
4. After generating your list, double-check that no two headlines describe the same event. Deduplicate if needed.

---

📬 Formatting Rules (for Outlook):
- Use UPPERCASE section titles with emojis
- Use `-` for bullets (no markdown)
- Keep each bullet concise

---

🎯 Example Format:

📜 REGULATION & POLICY  
- UK launches mandatory ESG audits  
- FCA consults on Scope 3 reporting

📊 ESG RESEARCH & STATS  
- 85% of pensions miss net-zero targets

🤖 AI & TECH  
- EU finalises AI Act enforcement timeline

🌍 CLIMATE & NATURAL RESOURCES  
- July storms cause £1.4B in losses

📌 OTHER  
- PwC launches ESG due diligence unit

---

Only include items that meet the criteria above.  
Here are the emails:
{email_bodies}
"""
#  chatGPT settings, and setup
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an ESG news briefing summariser."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000,
    )

    summary = response.choices[0].message.content

    # --- Token + Cost logging ---
    prompt_tokens = response.usage.prompt_tokens
    completion_tokens = response.usage.completion_tokens
    total_tokens = response.usage.total_tokens

    prompt_cost = prompt_tokens * 0.01 / 1000
    completion_cost = completion_tokens * 0.03 / 1000
    total_cost = prompt_cost + completion_cost

    usage_summary = (
        "[OpenAI Usage]\n"
        f"- Prompt tokens:     {prompt_tokens}\n"
        f"- Completion tokens: {completion_tokens}\n"
        f"- Total tokens:      {total_tokens}\n"
        f"- Estimated cost:    ${total_cost:.4f} USD"
    )

    return summary, usage_summary
