import json
import os
import requests

API_KEY = os.getenv("AI_API_KEY")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def _available_models() -> list[dict]:
    response = requests.get(
        f"{BASE_URL}/models",
        params={"key": API_KEY, "pageSize": 100},
        timeout=30,
    )
    response.raise_for_status()
    return response.json().get("models", [])


def _select_model() -> str:
    requested = DEFAULT_MODEL.removeprefix("models/")
    models = _available_models()

    # Prefer the configured model when the API advertises generateContent.
    for model in models:
        name = model.get("name", "").removeprefix("models/")
        methods = model.get("supportedGenerationMethods", [])
        if name == requested and "generateContent" in methods:
            return name

    # Safe fallbacks for text generation if the configured model is unavailable.
    preferred = ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3.5-flash-lite"]
    for candidate in preferred:
        for model in models:
            name = model.get("name", "").removeprefix("models/")
            methods = model.get("supportedGenerationMethods", [])
            if name == candidate and "generateContent" in methods:
                return name

    raise RuntimeError("No Gemini model supporting generateContent is available for this API key")


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

    model = _select_model()
    url = f"{BASE_URL}/models/{model}:generateContent"
    response = requests.post(
        url,
        params={"key": API_KEY},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"},
        },
        timeout=45,
    )
    response.raise_for_status()
    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    data = json.loads(text)
    return {
        "linkedin": [str(q) for q in data.get("linkedin", [])[:5]],
        "facebook": [str(q) for q in data.get("facebook", [])[:5]],
    }
