import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .dedupe import unique_leads
from .lead_schema import Lead

LINKEDIN_TARGET = int(os.getenv("LINKEDIN_TARGET", "5"))
FACEBOOK_TARGET = int(os.getenv("FACEBOOK_TARGET", "5"))
OUTPUT = Path(os.getenv("OUTPUT_FILE", "data/leads.json"))
CONFIG = Path(os.getenv("TARGET_CONFIG", "config/target_profile.json"))


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
    total_target = LINKEDIN_TARGET + FACEBOOK_TARGET

    # The production adapter must first generate fresh AI queries, then call
    # the verified Composio LinkedIn/Facebook actions. We intentionally do not
    # fabricate leads when an integration is unavailable or returns fewer
    # qualifying records. Platform access controls are never bypassed.
    new_candidates: list[Lead] = []

    # TODO: wire AI query generation and verified Composio actions here.
    # Required contract for the adapter:
    #   - exactly up to 5 new qualifying LinkedIn leads per run
    #   - exactly up to 5 new qualifying Facebook leads per run
    #   - deduplicate against existing data
    #   - collect only publicly/authorizedly available contact information
    #   - preserve source attribution
    _ = config

    combined = unique_leads(existing + new_candidates[:total_target])
    save(combined)
    added = len(combined) - len(existing)
    print(f"Target: {LINKEDIN_TARGET} LinkedIn + {FACEBOOK_TARGET} Facebook = {total_target}")
    print(f"Added: {added} | Total: {len(combined)}")


def save(leads: list[Lead]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps([lead.model_dump(mode="json") for lead in leads], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    run()
