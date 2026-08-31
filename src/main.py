import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .ai_query_engine import generate_queries
from .unique_leads import unique_leads if False else None
from .lead_schema import Lead
from .web_discovery import discover_all

LINKEDIN_TARGET = int(os.getenv("LINKEDIN_TARGET", "5"))
FACEBOOK_TARGET = int(os.getenv("FACEBOOK_TARGET", "5"))
OUTPUT = Path(os.getenv("OUTPUT_FILE", "data/leads.json"))
CONFIG = Path(os.getenv("TARGET_CONFIG", "config/target_profile.json"))

# Keep compatibility with the repository's existing dedupe implementation.
from .dedupe import unique_leads


def load_existing() -> list[Lead]:
    if not OUTPUT.exists():
        return []
    raw = json.loads(OUTPUT.read_text(encoding="utf-8"))
    return [Lead.model_validate(item) for item in raw]


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def run() -> None:
    config = load_config()
    existing = load_existing()
    previous = [x.get("other_channels", "") for x in json.loads(OUTPUT.read_text(encoding="utf-8"))] if OUTPUT.exists() else []

    # One AI planning call followed by one combined Google Search interaction.
    # This avoids making two separate discovery API calls for the same run.
    queries = generate_queries(config, previous_queries=previous)
    candidates = discover_all(
        queries,
        linkedin_limit=LINKEDIN_TARGET,
        facebook_limit=FACEBOOK_TARGET,
    )

    now = datetime.now(timezone.utc)
    new_leads = []
    for item in candidates:
        try:
            new_leads.append(Lead(
                company=item.get("company") or item.get("name") or "Unknown",
                website=None,
                address=None,
                phone=None,
                whatsapp=None,
                email=None,
                other_channels=item.get("url"),
                person_name=item.get("name"),
                job_title=item.get("title"),
                source=item.get("source"),
                collected_at=now,
                confidence="Medium" if item.get("url") else "Low",
            ))
        except Exception as exc:
            print(f"Skipping invalid candidate: {exc}")

    combined = unique_leads(existing + new_leads)
    added = len(combined) - len(existing)
    save(combined)
    linkedin_added = sum(1 for item in new_leads if item.source == "linkedin")
    facebook_added = sum(1 for item in new_leads if item.source == "facebook")
    print(f"Target: {LINKEDIN_TARGET} LinkedIn + {FACEBOOK_TARGET} Facebook = {LINKEDIN_TARGET + FACEBOOK_TARGET}")
    print(f"Candidates: {len(candidates)} | Added after dedupe: {added} | LinkedIn: {linkedin_added} | Facebook: {facebook_added} | Total: {len(combined)}")


def save(leads: list[Lead]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps([lead.model_dump(mode="json") for lead in leads], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    run()
