"""Identity service for the Migadu API."""

from __future__ import annotations

from typing import Any

from migadu_mcp.client.migadu_client import MigaduClient


class IdentityService:
    """Send-as identities attached to a mailbox."""

    def __init__(self, client: MigaduClient) -> None:
        self.client = client

    async def list_identities(self, domain: str, mailbox: str) -> dict[str, Any]:
        return await self.client.get(
            f"/domains/{domain}/mailboxes/{mailbox}/identities"
        )

    async def get_identity(
        self, domain: str, mailbox: str, identity: str
    ) -> dict[str, Any]:
        return await self.client.get(
            f"/domains/{domain}/mailboxes/{mailbox}/identities/{identity}"
        )

    async def create_identity(
        self,
        domain: str,
        mailbox: str,
        local_part: str,
        name: str,
        password: str,
    ) -> dict[str, Any]:
        data = {"local_part": local_part, "name": name, "password": password}
        return await self.client.post(
            f"/domains/{domain}/mailboxes/{mailbox}/identities", json=data
        )

    async def update_identity(
        self,
        domain: str,
        mailbox: str,
        identity: str,
        name: str | None = None,
        may_send: bool | None = None,
        may_receive: bool | None = None,
        may_access_imap: bool | None = None,
        may_access_pop3: bool | None = None,
        may_access_managesieve: bool | None = None,
        footer_active: bool | None = None,
        footer_plain_body: str | None = None,
        footer_html_body: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for key, value in [
            ("name", name),
            ("may_send", may_send),
            ("may_receive", may_receive),
            ("may_access_imap", may_access_imap),
            ("may_access_pop3", may_access_pop3),
            ("may_access_managesieve", may_access_managesieve),
            ("footer_active", footer_active),
            ("footer_plain_body", footer_plain_body),
            ("footer_html_body", footer_html_body),
        ]:
            if value is not None:
                data[key] = value
        return await self.client.put(
            f"/domains/{domain}/mailboxes/{mailbox}/identities/{identity}", json=data
        )

    async def delete_identity(self, domain: str, mailbox: str, identity: str) -> None:
        await self.client.delete(
            f"/domains/{domain}/mailboxes/{mailbox}/identities/{identity}"
        )
