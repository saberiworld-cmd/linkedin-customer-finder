"""Provider boundary for authorized Composio connections.

The exact LinkedIn/Facebook action names are intentionally not guessed. They
must be discovered from the user's connected Composio toolkits before wiring.
"""

from typing import Any


class ComposioSocialAdapter:
    def __init__(self, client: Any):
        self.client = client

    def search_linkedin(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Run the verified LinkedIn search action through Composio."""
        raise NotImplementedError("Discover and connect the verified Composio LinkedIn action")

    def search_facebook(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Run the verified Facebook search action through Composio."""
        raise NotImplementedError("Discover and connect the verified Composio Facebook action")

    def send_email(self, recipient: str, subject: str, body: str) -> Any:
        """Send outreach only through an explicitly authorized email integration."""
        raise NotImplementedError("Connect an authorized email provider before enabling outreach")
