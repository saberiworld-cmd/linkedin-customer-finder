import json
import os

from google import genai

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
API_KEY = os.getenv("AI_API_KEY")


def discover_all(queries: dict[str, list[str]], linkedin_limit: int = 5, facebook_limit: int = 5) -> list[dict]:
    if not API_KEY:
        raise RuntimeError("AI_API_KEY is required")

    client = genai.Client(api_key=API_KEY)
    prompt = f"""You are a B2B lead discovery researcher using Google Search.
Find NEW, publicly discoverable business prospects in exactly two source buckets.
Target: companies and relevant decision-makers that consume, produce, trade, import,
export, distribute, or procure petroleum derivatives, refined petroleum products,
petrochemicals, industrial chemicals, oilfield products or related materials.

For LinkedIn, return up to {linkedin_limit} results whose canonical public URL is on linkedin.com.
For Facebook, return up to {facebook_limit} results whose canonical public URL is on facebook.com.
Prefer company pages and clearly business-relevant professional profiles. Do not return personal
social profiles unless they are clearly business-relevant and publicly visible.
Use the supplied query themes as starting points, but vary the search as needed.
Do not invent names, companies, URLs, emails, phones, titles or snippets.
Return JSON only as an object with keys linkedin and facebook. Each is an array of objects with:
name, title, company, url, snippet, source.
Query themes: {json.dumps(queries, ensure_ascii=False)}"""

    interaction = client.interactions.create(
        model=MODEL,
        input=prompt,
        tools=[{"type": "google_search"}],
        generation_config={"max_output_tokens": 3000, "thinking_level": "low"},
    )
    text = interaction.output_text
    text = text.replace("```json", "").replace("```", "").strip()
    data = json.loads(text)

    results = []
    for source, limit in (("linkedin", linkedin_limit), ("facebook", facebook_limit)):
        for item in data.get(source, [])[:limit]:
            if isinstance(item, dict):
                url = str(item.get("url", ""))
                if source == "linkedin" and "linkedin.com" not in url:
                    continue
                if source == "facebook" and "facebook.com" not in url:
                    continue
                item["source"] = source
                results.append(item)
    return results


def discover(source: str, queries: list[str], limit: int = 5) -> list[dict]:
    """Backward-compatible single-source wrapper."""
    return discover_all({"linkedin": queries if source == "linkedin" else [], "facebook": queries if source == "facebook" else []},
                        linkedin_limit=limit if source == "linkedin" else 0,
                        facebook_limit=limit if source == "facebook" else 0)
