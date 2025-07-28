import os
from openai import OpenAI
import openai
from dotenv import load_dotenv
import tiktoken

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _build_prompt(email_bodies: list[str]) -> str:
    return f"""
You are a news summariser for an ESG consultancy in the UK.

You will receive a list of raw email contents containing ESG-related news, research, regulatory updates, or industry developments.

Your goal is to create an **extremely concise, must-read daily email**.  
If there is **no genuinely relevant news**, return exactly:  
"Nothing very important today."

---

🧠 Selection Rules:
- **Include only items that ESG professionals would find actionable or strategically important:**
  - UK/EU regulation or policy updates (enacted, draft, or consultations).
  - Major banking, EV infrastructure, or private equity developments tied to ESG.
  - Authoritative ESG reporting/disclosure guidance or standards (ISSB, CSRD, FCA, etc.).
  - Significant climate-related events with measurable financial or operational impact.
- **Include borderline items ONLY IF they have direct ESG implications** (e.g., large corporate ESG strategy shifts, major fines).
- **Exclude**: Opinion pieces, PR fluff, generic thought leadership, awards, speculative forecasts.

---

🎯 Output Rules:
1. If at least 1–2 strong items exist, output them cleanly by section.
2. If only 1 moderately relevant item exists, output it alone (don’t pad sections).
3. If none meet the bar, return only:
   "Nothing very important today."

---

📬 Format:
- Use only sections that have content:
  - 📜 REGULATION & POLICY  
  - 📊 ESG RESEARCH & STATS  
  - 🤖 AI & TECH  
  - 🌍 CLIMATE & NATURAL RESOURCES  
  - 📌 OTHER (for clearly ESG-relevant outliers)
- Bullets: `-` prefix, ultra-concise (max 12 words).
- No filler text, no intro sentences.

---

Examples:

**If important:**
📜 REGULATION & POLICY  
- FCA launches consultation on Scope 3 reporting  

🌍 CLIMATE & NATURAL RESOURCES  
- Heatwave causes £300M insured crop losses in Europe  

**If weak/no relevant items:**
Nothing very important today.

---

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
                raise openai.OpenAIError("Token estimate too high")

            summary, usage = _summarise_emails_inner(trimmed)
            return summary, usage, trimmed  # return used emails

        except openai.OpenAIError as e:
            if "maximum context length" in str(e).lower() or "token" in str(e).lower():
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