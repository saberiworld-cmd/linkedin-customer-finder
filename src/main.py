import json
import os
from pathlib import Path

from .dedupe import unique_leads
from .lead_schema import Lead

DAILY_MAX = int(os.getenv("DAILY_MAX_RECORDS", "5"))
OUTPUT = Path(os.getenv("OUTPUT_FILE", "data/leads.json"))


def load_existing() -> list[Lead]:
    if not OUTPUT.exists():
        return []
    raw = json.loads(OUTPUT.read_text(encoding="utf-8"))
    return [Lead.model_validate(item) for item in raw]


def save(leads: list[Lead]) -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps([lead.model_dump(mode="json") for lead in leads], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def run() -> None:
    # Provider-specific collection is intentionally injected through the
    # Composio adapter. Do not place credentials or browser sessions here.
    existing = load_existing()
    new_candidates: list[Lead] = []

    # TODO: call the verified Composio LinkedIn action and map results to Lead.
    # The engine must stop at DAILY_MAX and may legitimately produce fewer
    # than DAILY_MAX records when no suitable new leads are found.

    combined = unique_leads(existing + new_candidates)
    save(combined)
    print(f"Existing: {len(existing)} | New: {len(combined) - len(existing)} | Total: {len(combined)}")


if __name__ == "__main__":
    run()
