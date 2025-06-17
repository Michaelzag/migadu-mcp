#!/usr/bin/env python3
"""
Identity service for Migadu API operations
"""

from typing import Dict, Any, Optional
from migadu_mcp.client.migadu_client import MigaduClient


class IdentityService:
    """Service for identity operations"""

    def __init__(self, client: MigaduClient):
        self.client = client

    async def list_identities(self, domain: str, mailbox: str) -> Dict[str, Any]:
        """List all identities for a mailbox"""
        return await self.client.request(
            "GET", f"/domains/{domain}/mailboxes/{mailbox}/identities"
        )

    async def create_identity(
        self, domain: str, mailbox: str, local_part: str, name: str, password: str
    ) -> Dict[str, Any]:
        """Create a new identity for a mailbox"""
        data = {"local_part": local_part, "name": name, "password": password}
        return await self.client.request(
            "POST", f"/domains/{domain}/mailboxes/{mailbox}/identities", json=data
        )

    async def get_identity(
        self, domain: str, mailbox: str, identity: str
    ) -> Dict[str, Any]:
        """Get details of a specific identity"""
        return await self.client.request(
            "GET", f"/domains/{domain}/mailboxes/{mailbox}/identities/{identity}"
        )

    async def update_identity(
        self,
        domain: str,
        mailbox: str,
        identity: str,
        name: Optional[str] = None,
        may_send: Optional[bool] = None,
        may_receive: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update identity settings"""
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if may_send is not None:
            data["may_send"] = may_send
        if may_receive is not None:
            data["may_receive"] = may_receive

        return await self.client.request(
            "PUT",
            f"/domains/{domain}/mailboxes/{mailbox}/identities/{identity}",
            json=data,
        )

    async def delete_identity(
        self, domain: str, mailbox: str, identity: str
    ) -> Dict[str, Any]:
        """Delete an identity"""
        return await self.client.request(
            "DELETE", f"/domains/{domain}/mailboxes/{mailbox}/identities/{identity}"
        )
