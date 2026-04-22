"""Mailbox service for the Migadu API."""

from __future__ import annotations

from typing import Any

from migadu_mcp.client.migadu_client import MigaduClient


class MailboxService:
    """CRUD for full email accounts with storage and IMAP/POP3/SMTP access."""

    def __init__(self, client: MigaduClient) -> None:
        self.client = client

    async def list_mailboxes(self, domain: str) -> dict[str, Any]:
        return await self.client.get(f"/domains/{domain}/mailboxes")

    async def get_mailbox(self, domain: str, local_part: str) -> dict[str, Any]:
        return await self.client.get(f"/domains/{domain}/mailboxes/{local_part}")

    async def create_mailbox(
        self,
        domain: str,
        local_part: str,
        name: str,
        password: str | None = None,
        password_recovery_email: str | None = None,
        is_internal: bool = False,
        forwarding_to: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "local_part": local_part,
            "name": name,
            "is_internal": is_internal,
        }
        if password:
            data["password"] = password
        elif password_recovery_email:
            data["password_method"] = "invitation"  # nosec B105 — API value, not a password
            data["password_recovery_email"] = password_recovery_email
        if forwarding_to:
            data["forwarding_to"] = forwarding_to
        return await self.client.post(f"/domains/{domain}/mailboxes", json=data)

    async def update_mailbox(
        self,
        domain: str,
        local_part: str,
        name: str | None = None,
        may_send: bool | None = None,
        may_receive: bool | None = None,
        may_access_imap: bool | None = None,
        may_access_pop3: bool | None = None,
        may_access_managesieve: bool | None = None,
        spam_action: str | None = None,
        spam_aggressiveness: str | None = None,
        sender_denylist: str | None = None,
        sender_allowlist: str | None = None,
        recipient_denylist: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        for key, value in [
            ("name", name),
            ("may_send", may_send),
            ("may_receive", may_receive),
            ("may_access_imap", may_access_imap),
            ("may_access_pop3", may_access_pop3),
            ("may_access_managesieve", may_access_managesieve),
            ("spam_action", spam_action),
            ("spam_aggressiveness", spam_aggressiveness),
            ("sender_denylist", sender_denylist),
            ("sender_allowlist", sender_allowlist),
            ("recipient_denylist", recipient_denylist),
        ]:
            if value is not None:
                data[key] = value
        return await self.client.put(
            f"/domains/{domain}/mailboxes/{local_part}", json=data
        )

    async def delete_mailbox(self, domain: str, local_part: str) -> None:
        await self.client.delete(f"/domains/{domain}/mailboxes/{local_part}")

    async def reset_mailbox_password(
        self, domain: str, local_part: str, new_password: str
    ) -> dict[str, Any]:
        return await self.client.put(
            f"/domains/{domain}/mailboxes/{local_part}",
            json={"password": new_password},
        )

    async def set_autoresponder(
        self,
        domain: str,
        local_part: str,
        active: bool,
        subject: str | None = None,
        body: str | None = None,
        expires_on: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {"autorespond_active": active}
        if subject is not None:
            data["autorespond_subject"] = subject
        if body is not None:
            data["autorespond_body"] = body
        if expires_on is not None:
            data["autorespond_expires_on"] = expires_on
        return await self.client.put(
            f"/domains/{domain}/mailboxes/{local_part}", json=data
        )
