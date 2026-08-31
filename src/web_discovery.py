import re
from urllib.parse import quote, unquote, urlparse

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/126 Safari/537.36"}


def _extract_result_links(html: str, site: str, limit: int) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    results = []
    seen = set()
    for a in soup.select("li.b_algo h2 a, h2 a"):
        href = a.get("href", "")
        title = a.get_text(" ", strip=True)
        if not href or not title:
            continue
        if href.startswith("/"):
            continue
        parsed = urlparse(href)
        if parsed.scheme not in ("http", "https"):
            continue
        host = parsed.netloc.lower().split(":")[0]
        if not (host == site or host.endswith("." + site)):
            continue
        canonical = href.split("?")[0].rstrip("/")
        if canonical in seen:
            continue
        seen.add(canonical)
        container = a.find_parent("li")
        snippet = ""
        if container:
            p = container.find("p")
            if p:
                snippet = p.get_text(" ", strip=True)
        results.append({"name": title, "title": None, "company": title, "url": canonical, "snippet": snippet})
        if len(results) >= limit:
            break
    return results


def _search_bing(query: str, site: str, limit: int = 5) -> list[dict]:
    scoped = f"site:{site} {query}"
    url = "https://www.bing.com/search?q=" + quote(scoped) + "&count=10"
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return _extract_result_links(r.text, site, limit)


def discover_all(queries: dict[str, list[str]], linkedin_limit: int = 5, facebook_limit: int = 5) -> list[dict]:
    results: list[dict] = []
    targets = (("linkedin", "linkedin.com", linkedin_limit), ("facebook", "facebook.com", facebook_limit))
    for source, site, target in targets:
        if target <= 0:
            continue
        seen = set()
        for query in queries.get(source, []):
            try:
                found = _search_bing(query, site, limit=target)
            except requests.RequestException as exc:
                print(f"{source} web search failed for query '{query}': {exc}")
                continue
            for item in found:
                if item["url"] in seen:
                    continue
                seen.add(item["url"])
                item["source"] = source
                results.append(item)
                if sum(1 for x in results if x["source"] == source) >= target:
                    break
            if sum(1 for x in results if x["source"] == source) >= target:
                break
    return results


def discover(source: str, queries: list[str], limit: int = 5) -> list[dict]:
    return discover_all(
        {"linkedin": queries if source == "linkedin" else [], "facebook": queries if source == "facebook" else []},
        linkedin_limit=limit if source == "linkedin" else 0,
        facebook_limit=limit if source == "facebook" else 0,
    )
