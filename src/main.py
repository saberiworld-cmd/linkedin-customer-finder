import json
import os
from datetime import datetime, timezone
from pathlib import Path

from .dedupe import unique_leads
from .lead_schema import Lead

DAILY_MAX = int(os.getenv("DAILY_MAX_RECORDS", "5"))
OUTPUT = Path(os.getenv("OUTPUT_FILE", "data/leads.json"))
CONFIG = Path(os.getenv("TARGET_CONFIG", "config/target_profile.json"))


def load_existing() -> list[Lead]:
    if not OUTPUT.exists():
        return []
    raw = json.loads(OUTPUT.read_text(encoding="utf-8"))
    return [Lead.model_validate(item) for item in raw]


def load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def today_new_count(existing: list[Lead]) -> int:
    today = datetime.now(timezone.utc).date()
    return sum(1 for lead in existing if lead.collected_at.date() == today)


def run() -> None:
    config = load_config()
    existing = load_existing()
    remaining = max(0, min(DAILY_MAX, config.get("daily_new_records_max", DAILY_MAX)) - today_new_count(existing))

    # Provider-specific collection is injected through verified integrations.
    # Search must use the configured target profile and all enabled sources.
    # Never fabricate records and never bypass provider access controls.
    new_candidates: list[Lead] = []

    if remaining > 0:
        # TODO: invoke the verified Composio LinkedIn/Facebook actions and an
        # approved AI search/ranking provider. The AI should generate varied
        # search queries each run, score relevance, and return only new leads.
        pass

    combined = unique_leads(existing + new_candidates[:remaining])
    save(combined)
    print(
        f"Existing: {len(existing)} | Added today: {len(combined) - len(existing)} "
        f"| Total: {len(combined)} | Remaining daily capacity: "
        f"{max(0, DAILY_MAX - today_new_count(combined))}"
    )


def save(leads: list[Lead]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps([lead.model_dump(mode="json") for lead in leads], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    run()
