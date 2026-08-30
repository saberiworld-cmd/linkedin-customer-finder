import json
import os
import re
import requests

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_KEY = os.getenv("AI_API_KEY")


def discover(source: str, queries: list[str], limit: int = 5) -> list[dict]:
    if not API_KEY:
        raise RuntimeError("AI_API_KEY is required")
    site = "linkedin.com" if source == "linkedin" else "facebook.com"
    prompt = f'''Find up to {limit} NEW B2B prospects from public web results for {source}.
Only return business/company pages or clearly business-relevant professional profiles.
Target companies/persons involved in consuming, producing, trading, importing, exporting,
distributing, or procuring petroleum derivatives, refined products, petrochemicals,
industrial chemicals, oilfield products or related materials.
Use these search themes: {json.dumps(queries, ensure_ascii=False)}
Prioritize results whose public URL is on {site}. Do not invent URLs, names, emails or phones.
Return JSON only: [{{"name":"", "title":"", "company":"", "url":"", "snippet":"", "source":"{source}"}}]'''
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "tools": [{"google_search": {}}],
    }
    r = requests.post(url, params={"key": API_KEY}, json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    text = data["candidates"][0]["content"]["parts"][0]["text"]
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    items = json.loads(text)
    return [x for x in items if isinstance(x, dict)][:limit]
