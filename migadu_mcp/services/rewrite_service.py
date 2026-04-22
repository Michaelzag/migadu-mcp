"""Rewrite service for the Migadu API."""

from __future__ import annotations

from typing import Any

from migadu_mcp.client.migadu_client import MigaduClient


class RewriteService:
    """CRUD for pattern-based routing rules."""

    def __init__(self, client: MigaduClient) -> None:
        self.client = client

    async def list_rewrites(self, domain: str) -> dict[str, Any]:
        return await self.client.get(f"/domains/{domain}/rewrites")

    async def get_rewrite(self, domain: str, name: str) -> dict[str, Any]:
        return await self.client.get(f"/domains/{domain}/rewrites/{name}")

    async def create_rewrite(
        self,
        domain: str,
        name: str,
        local_part_rule: str,
        destinations: list[str],
        order_num: int | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "name": name,
            "local_part_rule": local_part_rule,
            "destinations": ",".join(destinations),
        }
        if order_num is not None:
            data["order_num"] = order_num
        return await self.client.post(f"/domains/{domain}/rewrites", json=data)

    async def update_rewrite(
        self,
        domain: str,
        name: str,
        new_name: str | None = None,
        local_part_rule: str | None = None,
        destinations: list[str] | None = None,
        order_num: int | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if new_name is not None:
            data["name"] = new_name
        if local_part_rule is not None:
            data["local_part_rule"] = local_part_rule
        if destinations is not None:
            data["destinations"] = ",".join(destinations)
        if order_num is not None:
            data["order_num"] = order_num
        return await self.client.put(f"/domains/{domain}/rewrites/{name}", json=data)

    async def delete_rewrite(self, domain: str, name: str) -> None:
        await self.client.delete(f"/domains/{domain}/rewrites/{name}")
