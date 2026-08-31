import json
import os

from google import genai

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
API_KEY = os.getenv("AI_API_KEY")


def generate_queries(profile: dict, previous_queries: list[str] | None = None) -> dict[str, list[str]]:
    if not API_KEY:
        raise RuntimeError("AI_API_KEY is required")

    client = genai.Client(api_key=API_KEY)
    previous_queries = previous_queries or []
    prompt = f"""You are a B2B lead discovery planner.
Generate exactly 5 fresh search queries for LinkedIn and exactly 5 for Facebook.
Target: companies and decision-makers that consume, produce, trade, import, export,
distribute, or procure petroleum derivatives, refined petroleum products, petrochemicals,
industrial chemicals, oilfield products, and related materials.
Vary product terms, regions, company types, and procurement/commercial roles.
Avoid previously used query strings.
Return JSON only with keys linkedin and facebook; each value is an array of exactly 5 strings.
Previous query strings: {json.dumps(previous_queries, ensure_ascii=False)}
Target profile: {json.dumps(profile, ensure_ascii=False)}"""

    interaction = client.interactions.create(
        model=MODEL,
        input=prompt,
        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": {
                "type": "object",
                "properties": {
                    "linkedin": {"type": "array", "items": {"type": "string"}},
                    "facebook": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["linkedin", "facebook"],
            },
        },
    )
    text = interaction.output_text
    if not text:
        raise RuntimeError("Gemini returned an empty response")
    data = json.loads(text)
    return {
        "linkedin": [str(q) for q in data.get("linkedin", [])[:5]],
        "facebook": [str(q) for q in data.get("facebook", [])[:5]],
    }
