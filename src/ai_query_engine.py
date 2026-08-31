import json
import os

from google import genai

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
API_KEY = os.getenv("AI_API_KEY")


def generate_queries(profile: dict, previous_queries: list[str] | None = None) -> dict[str, list[str]]:
    if not API_KEY:
        raise RuntimeError("AI_API_KEY is required")

    client = genai.Client(api_key=API_KEY)
    previous_queries = previous_queries or []
    prompt = f"""You are a B2B lead-discovery query planner.
Create fresh, non-repetitive search queries for two sources: LinkedIn and Facebook.
Target: companies and relevant decision-makers that consume, produce, trade, import,
export, distribute, or procure petroleum derivatives, refined petroleum products,
and petrochemical/industrial chemical materials.
Return JSON only with keys linkedin and facebook. Each key must contain exactly 5 concise
search queries. Avoid queries already used in this list: {json.dumps(previous_queries, ensure_ascii=False)}.
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
