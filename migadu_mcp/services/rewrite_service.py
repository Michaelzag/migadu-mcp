#!/usr/bin/env python3
"""
Rewrite service for Migadu API operations
"""

from typing import Dict, Any, List, Optional
from migadu_mcp.client.migadu_client import MigaduClient


class RewriteService:
    """Service for rewrite operations"""

    def __init__(self, client: MigaduClient):
        self.client = client

    async def list_rewrites(self, domain: str) -> Dict[str, Any]:
        """List all rewrites for a domain"""
        return await self.client.request("GET", f"/domains/{domain}/rewrites")

    async def create_rewrite(
        self, domain: str, name: str, local_part_rule: str, destinations: List[str]
    ) -> Dict[str, Any]:
        """Create a new rewrite rule"""
        data = {
            "name": name,
            "local_part_rule": local_part_rule,
            "destinations": ",".join(destinations),
        }
        return await self.client.request(
            "POST", f"/domains/{domain}/rewrites", json=data
        )

    async def get_rewrite(self, domain: str, name: str) -> Dict[str, Any]:
        """Get details of a specific rewrite"""
        return await self.client.request("GET", f"/domains/{domain}/rewrites/{name}")

    async def update_rewrite(
        self,
        domain: str,
        name: str,
        new_name: Optional[str] = None,
        local_part_rule: Optional[str] = None,
        destinations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Update rewrite settings"""
        data: Dict[str, Any] = {}
        if new_name is not None:
            data["name"] = new_name
        if local_part_rule is not None:
            data["local_part_rule"] = local_part_rule
        if destinations is not None:
            data["destinations"] = ",".join(destinations)

        return await self.client.request(
            "PUT", f"/domains/{domain}/rewrites/{name}", json=data
        )

    async def delete_rewrite(self, domain: str, name: str) -> Dict[str, Any]:
        """Delete a rewrite rule"""
        return await self.client.request("DELETE", f"/domains/{domain}/rewrites/{name}")
