#!/usr/bin/env python3
"""
Alias service for Migadu API operations
"""

from typing import Dict, Any, List
from migadu_mcp.client.migadu_client import MigaduClient


class AliasService:
    """Service for alias operations"""

    def __init__(self, client: MigaduClient):
        self.client = client

    async def list_aliases(self, domain: str) -> Dict[str, Any]:
        """List all aliases for a domain"""
        return await self.client.request("GET", f"/domains/{domain}/aliases")

    async def create_alias(
        self,
        domain: str,
        local_part: str,
        destinations: List[str],
        is_internal: bool = False,
    ) -> Dict[str, Any]:
        """Create a new alias"""
        data = {
            "local_part": local_part,
            "destinations": ",".join(destinations),
            "is_internal": is_internal,
        }
        return await self.client.request(
            "POST", f"/domains/{domain}/aliases", json=data
        )

    async def get_alias(self, domain: str, local_part: str) -> Dict[str, Any]:
        """Get details of a specific alias"""
        return await self.client.request(
            "GET", f"/domains/{domain}/aliases/{local_part}"
        )

    async def update_alias(
        self, domain: str, local_part: str, destinations: List[str]
    ) -> Dict[str, Any]:
        """Update alias destinations"""
        data = {"destinations": ",".join(destinations)}
        return await self.client.request(
            "PUT", f"/domains/{domain}/aliases/{local_part}", json=data
        )

    async def delete_alias(self, domain: str, local_part: str) -> Dict[str, Any]:
        """Delete an alias"""
        return await self.client.request(
            "DELETE", f"/domains/{domain}/aliases/{local_part}"
        )
