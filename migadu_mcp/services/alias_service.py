"""Alias service for the Migadu API."""

from __future__ import annotations

from typing import Any

from migadu_mcp.client.migadu_client import MigaduClient


class AliasService:
    """CRUD for forwarding aliases (no storage, just destination rules)."""

    def __init__(self, client: MigaduClient) -> None:
        self.client = client

    async def list_aliases(self, domain: str) -> dict[str, Any]:
        return await self.client.get(f"/domains/{domain}/aliases")

    async def get_alias(self, domain: str, local_part: str) -> dict[str, Any]:
        return await self.client.get(f"/domains/{domain}/aliases/{local_part}")

    async def create_alias(
        self,
        domain: str,
        local_part: str,
        destinations: list[str],
        is_internal: bool = False,
    ) -> dict[str, Any]:
        data = {
            "local_part": local_part,
            "destinations": ",".join(destinations),
            "is_internal": is_internal,
        }
        return await self.client.post(f"/domains/{domain}/aliases", json=data)

    async def update_alias(
        self, domain: str, local_part: str, destinations: list[str]
    ) -> dict[str, Any]:
        return await self.client.put(
            f"/domains/{domain}/aliases/{local_part}",
            json={"destinations": ",".join(destinations)},
        )

    async def delete_alias(self, domain: str, local_part: str) -> None:
        await self.client.delete(f"/domains/{domain}/aliases/{local_part}")
