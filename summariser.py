import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarise_emails(email_bodies: list[str]) -> str:
    prompt = f"""
You are an expert summariser working for an ESG consultancy.

You will receive a list of recent email contents. Each email contains a potential news item, industry development, or client insight.

Your job is to:
1. Identify and extract only the most relevant headlines — those that may directly affect our business, clients, or how ESG is reported or regulated.
2. Filter out anything generic or low-impact — such as internal regulatory process changes, minor corporate updates, or global news not affecting UK policy or financial institutions.
3. Categorise the final headlines under these strict groups:
   - REGULATION & POLICY
   - ESG RESEARCH & STATS
   - AI & TECH
   - CLIMATE & NATURAL RESOURCES
   - OTHER

Our business is primarily interested in:
- Regulatory, policy or legislative environmental updates affecting UK businesses — especially retail banks, EV charging infrastructure, PE GPs, and mid-sized UK companies (~100–1,000 employees).
- The four long-term forces shaping ESG: AI/tech disruption, climate change, natural resource risks, and financial regulation.
- UK financial sector shifts: M&A, strategy changes, fines, or propositions in banking or private equity.

Please apply *contextual judgement*. For example:
- "FCA introduces faster enforcement investigations" → NOT relevant
- "UK mandates carbon disclosure for private equity portfolio firms" → RELEVANT

Your output should be concise and email-ready using plain formatting.
Use **capitalised section headings**, and a clean dash `-` or asterisk `*` for each bullet:

Example:
REGULATION & POLICY  
- UK launches ESG audit standards for mid-sized firms  
- FCA requires Scope 3 disclosures in banking stress tests  

CLIMATE & NATURAL RESOURCES  
- UK insurers report £2.3B climate-related losses in 2024  

Here are the emails:  
{email_bodies}
"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an ESG news briefing summariser."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=1000,
    )

    return response.choices[0].message.content
