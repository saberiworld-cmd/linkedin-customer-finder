import json
import os
import requests

MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
API_KEY = os.getenv("AI_API_KEY")


def generate_queries(profile: dict, previous_queries: list[str] | None = None) -> dict[str, list[str]]:
    if not API_KEY:
        raise RuntimeError("AI_API_KEY is required")

    previous_queries = previous_queries or []
    prompt = f"""You are a B2B lead-discovery query planner.
Create fresh, non-repetitive search queries for two sources: LinkedIn and Facebook.
Target: companies and relevant decision-makers that consume, produce, trade, import,
export, distribute, or procure petroleum derivatives, refined petroleum products,
and petrochemical/industrial chemical materials.
Return JSON only with keys linkedin and facebook. Each key must contain 5 concise
search queries. Avoid queries already used in this list: {json.dumps(previous_queries)}.
Target profile: {json.dumps(profile, ensure_ascii=False)}"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"
    response = requests.post(
        url,
        params={"key": API_KEY},
        json={"contents": [{"parts": [{"text": prompt}]}]},
        timeout=45,
    )
    response.raise_for_status()
    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    text = text.replace("```json", "").replace("```", "").strip()
    data = json.loads(text)
    return {
        "linkedin": [str(q) for q in data.get("linkedin", [])[:5]],
        "facebook": [str(q) for q in data.get("facebook", [])[:5]],
    }
