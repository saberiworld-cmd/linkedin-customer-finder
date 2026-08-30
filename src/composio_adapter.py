"""Optional enrichment boundary for authorized Composio connections.

Discovery is performed through Gemini grounded web search because the currently
connected LinkedIn toolkit does not expose general people/company search and
Facebook page search may be deprecated. Composio can enrich identifiers when a
compatible action is available; discovery never fabricates data.
"""

from typing import Any


class ComposioSocialAdapter:
    def __init__(self, client: Any | None = None):
        self.client = client

    def enrich_linkedin(self, person_id: str | None = None, organization_id: str | None = None) -> dict[str, Any]:
        return {"person_id": person_id, "organization_id": organization_id}

    def enrich_facebook_page(self, page_id: str | None = None) -> dict[str, Any]:
        return {"page_id": page_id}

    def send_email(self, recipient: str, subject: str, body: str) -> Any:
        raise NotImplementedError("Email sending remains disabled until explicitly enabled")
