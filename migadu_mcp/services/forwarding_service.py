"""Forwarding service for the Migadu API.

Forwardings are external email addresses a mailbox delivers a copy of its messages to,
gated by a confirmation flow. Extracted from mailbox_service.py for consistency with
other per-resource services.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import quote

from migadu_mcp.client.migadu_client import MigaduClient


def _encode_address(address: str) -> str:
    return quote(address, safe="")


class ForwardingService:
    def __init__(self, client: MigaduClient) -> None:
        self.client = client

    async def list_forwardings(self, domain: str, mailbox: str) -> dict[str, Any]:
        return await self.client.get(
            f"/domains/{domain}/mailboxes/{mailbox}/forwardings"
        )

    async def get_forwarding(
        self, domain: str, mailbox: str, address: str
    ) -> dict[str, Any]:
        return await self.client.get(
            f"/domains/{domain}/mailboxes/{mailbox}/forwardings/{_encode_address(address)}"
        )

    async def create_forwarding(
        self,
        domain: str,
        mailbox: str,
        address: str,
        expires_on: str | None = None,
        remove_upon_expiry: bool | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {"address": address}
        if expires_on is not None:
            data["expires_on"] = expires_on
        if remove_upon_expiry is not None:
            data["remove_upon_expiry"] = remove_upon_expiry
        return await self.client.post(
            f"/domains/{domain}/mailboxes/{mailbox}/forwardings", json=data
        )

    async def update_forwarding(
        self,
        domain: str,
        mailbox: str,
        address: str,
        is_active: bool | None = None,
        expires_on: str | None = None,
        remove_upon_expiry: bool | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if is_active is not None:
            data["is_active"] = is_active
        if expires_on is not None:
            data["expires_on"] = expires_on
        if remove_upon_expiry is not None:
            data["remove_upon_expiry"] = remove_upon_expiry
        return await self.client.put(
            f"/domains/{domain}/mailboxes/{mailbox}/forwardings/{_encode_address(address)}",
            json=data,
        )

    async def delete_forwarding(self, domain: str, mailbox: str, address: str) -> None:
        await self.client.delete(
            f"/domains/{domain}/mailboxes/{mailbox}/forwardings/{_encode_address(address)}"
        )
