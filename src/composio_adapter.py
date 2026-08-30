"""Thin boundary for the connected Composio account.

The exact LinkedIn tool/action name is intentionally not hard-coded until it is
verified from the connected Composio toolkit. This prevents silently calling
the wrong action or relying on undocumented endpoints.
"""

from typing import Any


class ComposioLinkedInAdapter:
    def __init__(self, client: Any):
        self.client = client

    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        """Execute the verified LinkedIn search action through Composio.

        Wire this method to the exact connected Composio action in the next
        implementation step. Keep all provider-specific logic inside this
        adapter so the rest of the engine remains provider-agnostic.
        """
        raise NotImplementedError("Connect the verified Composio LinkedIn action")
