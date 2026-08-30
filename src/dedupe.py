from .lead_schema import Lead


def key(lead: Lead) -> str:
    if lead.linkedin_url:
        return str(lead.linkedin_url).rstrip("/").lower()
    email = (lead.email or "").strip().lower()
    if email:
        return email
    return "|".join(
        [
            (lead.company or "").strip().lower(),
            (lead.person_name or "").strip().lower(),
            (lead.job_title or "").strip().lower(),
        ]
    )


def unique_leads(leads: list[Lead]) -> list[Lead]:
    seen: set[str] = set()
    output: list[Lead] = []
    for lead in leads:
        k = key(lead)
        if k and k not in seen:
            seen.add(k)
            output.append(lead)
    return output
