import json
import os
import requests

MODEL = os.getenv("GROQ_MODEL", "groq/compound-mini")
API_KEY = os.getenv("GROQ_API_KEY")


def _search(prompt: str) -> str:
    if not API_KEY:
        raise RuntimeError("GROQ_API_KEY is required")
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
        },
        timeout=90,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def discover_all(queries: dict[str, list[str]], linkedin_limit: int = 5, facebook_limit: int = 5) -> list[dict]:
    results: list[dict] = []
    for source, limit in (("linkedin", linkedin_limit), ("facebook", facebook_limit)):
        site = "linkedin.com" if source == "linkedin" else "facebook.com"
        prompt = f"""Use your built-in real-time web search to find up to {limit} NEW B2B prospects for {source}.
Search the public web and prioritize canonical URLs on {site}. Target companies and clearly business-relevant decision-makers
that consume, produce, trade, import, export, distribute, or procure petroleum derivatives, refined petroleum products,
petrochemicals, industrial chemicals, oilfield products, or related materials.
Use these search themes and vary them: {json.dumps(queries.get(source, []), ensure_ascii=False)}.
Do not invent data. Return JSON only as an array of objects with name,title,company,url,snippet,source.
Only include results with a real public URL from {site}."""
        text = _search(prompt).replace("```json", "").replace("```", "").strip()
        data = json.loads(text)
        if isinstance(data, list):
            for item in data:
                if not isinstance(item, dict):
                    continue
                url = str(item.get("url", ""))
                if site not in url:
                    continue
                item["source"] = source
                results.append(item)
    return results


def discover(source: str, queries: list[str], limit: int = 5) -> list[dict]:
    return discover_all(
        {"linkedin": queries if source == "linkedin" else [], "facebook": queries if source == "facebook" else []},
        linkedin_limit=limit if source == "linkedin" else 0,
        facebook_limit=limit if source == "facebook" else 0,
    )
