import json
import os
import requests

MODEL = os.getenv("GROQ_MODEL", "groq/compound-mini")
API_KEY = os.getenv("GROQ_API_KEY")


def _call_groq(prompt: str) -> str:
    if not API_KEY:
        raise RuntimeError("GROQ_API_KEY is required")
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def generate_queries(profile: dict, previous_queries: list[str] | None = None) -> dict[str, list[str]]:
    previous_queries = previous_queries or []
    prompt = f"""You are a B2B lead discovery planner. Generate exactly 5 fresh search queries for LinkedIn and 5 for Facebook.
Target: companies and decision-makers that consume, produce, trade, import, export, distribute, or procure petroleum derivatives,
refined petroleum products, petrochemicals, industrial chemicals, oilfield products, and related materials.
Use varied countries, product terms, business roles, and procurement language. Avoid duplicates from previous queries.
Return JSON only with keys linkedin and facebook; each value must be an array of exactly 5 strings.
Previous queries: {json.dumps(previous_queries, ensure_ascii=False)}
Target profile: {json.dumps(profile, ensure_ascii=False)}"""
    text = _call_groq(prompt)
    text = text.replace("```json", "").replace("```", "").strip()
    data = json.loads(text)
    return {
        "linkedin": [str(q) for q in data.get("linkedin", [])[:5]],
        "facebook": [str(q) for q in data.get("facebook", [])[:5]],
    }
