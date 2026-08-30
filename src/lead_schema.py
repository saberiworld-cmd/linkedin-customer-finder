from datetime import datetime, timezone
from pydantic import BaseModel, Field, HttpUrl


class Lead(BaseModel):
    company: str
    person_name: str | None = None
    job_title: str | None = None
    linkedin_url: HttpUrl | None = None
    company_linkedin_url: HttpUrl | None = None
    website: HttpUrl | None = None
    country: str | None = None
    industry: str | None = None
    email: str | None = None
    phone: str | None = None
    source: str = "linkedin"
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: str = "medium"
