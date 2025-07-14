import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def summarise_emails(email_bodies: list[str]) -> str:
    prompt = f"""
You are a news summariser for an ESG consultancy. 
You will receive a list of email text contents. 
Each contains a news item, client insight, or industry update.

Your job is to:
1. Extract the most relevant headlines
2. Remove duplicates or near-duplicates
3. Categorise them under:
   - Regulation & Policy
   - ESG Research & Stats
   - AI & Tech
   - Climate & Natural Resources
   - Other
4. Format the result in markdown, e.g.:

**Regulation & Policy**
- FCA launches ESG stress tests for banks  
- New UK rules mandate carbon reporting for mid-sized firms  

**AI & Tech**
- OpenAI releases GPT-5 roadmap

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
