import os
from openai import OpenAI, error as openai_error
from dotenv import load_dotenv
import tiktoken

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _build_prompt(email_bodies: list[str]) -> str:
    return f"""
You are a news summariser for an ESG consultancy in the UK.

You will receive a list of raw email contents containing ESG-related news, research, regulatory updates, or industry developments.

Your job is to produce a visually engaging, concise summary xemail, broken into sections.

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

def _estimate_tokens(text: str, model: str = "gpt-4o") -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
        return len(enc.encode(text))
    except Exception:
        return len(text.split())  # fallback estimate

def _summarise_emails_inner(email_bodies: list[str]) -> tuple[str, str]:
    prompt = _build_prompt(email_bodies)

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

def summarise_emails(email_bodies: list[str]) -> tuple[str, str, list[str]]:
    trimmed = email_bodies[:]
    reduction_step = 1

    while trimmed:
        try:
            est_tokens = _estimate_tokens(_build_prompt(trimmed))
            if est_tokens > 7000:
                raise openai_error.InvalidRequestError("Token estimate too high", None)

            summary, usage = _summarise_emails_inner(trimmed)
            return summary, usage, trimmed  # return used emails

        except openai_error.InvalidRequestError as e:
            if "maximum context length" in str(e) or "token" in str(e).lower():
                if len(trimmed) > 50:
                    reduction_step = 5
                elif len(trimmed) > 20:
                    reduction_step = 3
                else:
                    reduction_step = 1
                trimmed = trimmed[:-reduction_step]
            else:
                raise

    raise RuntimeError("Could not summarise any emails within token limit.")
