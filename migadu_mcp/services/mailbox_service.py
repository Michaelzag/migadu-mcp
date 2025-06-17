#!/usr/bin/env python3
"""
Mailbox service for Migadu API operations
"""

from typing import Dict, Any, Optional, List
from migadu_mcp.client.migadu_client import MigaduClient, MigaduAPIError


class MailboxService:
    """Service for email mailbox operations providing CRUD functionality for full email accounts.

    Mailboxes are complete email accounts with storage, authentication, and protocol access (IMAP/POP3/SMTP).
    Unlike aliases which only forward messages, mailboxes store emails and allow user authentication.
    This service handles all mailbox lifecycle operations including creation, configuration, and deletion.
    """

    def __init__(self, client: MigaduClient):
        self.client = client

    async def list_mailboxes(self, domain: str) -> Dict[str, Any]:
        """Retrieve all email mailboxes configured for a domain with complete configuration details.

        Returns comprehensive information for each mailbox including permissions, spam settings,
        autoresponder configuration, and security options for domain-wide auditing and management.
        """
        return await self.client.request("GET", f"/domains/{domain}/mailboxes")

    async def get_mailbox(self, domain: str, local_part: str) -> Dict[str, Any]:
        """Retrieve detailed configuration for a specific mailbox including all settings and permissions.

        Shows complete mailbox state including authentication, protocol access, spam filtering,
        autoresponder status, and security policies for inspection and troubleshooting.
        """
        return await self.client.request(
            "GET", f"/domains/{domain}/mailboxes/{local_part}"
        )

    async def create_mailbox(
        self,
        domain: str,
        local_part: str,
        name: str,
        password: Optional[str] = None,
        password_recovery_email: Optional[str] = None,
        is_internal: bool = False,
        forwarding_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new email mailbox with full storage and authentication capabilities.

        Supports immediate password setup or invitation-based setup where the user sets their own password.
        Can create internal-only mailboxes (restricted to Migadu servers) and configure automatic
        forwarding during creation. Returns complete mailbox configuration upon successful creation.
        """
        data = {"local_part": local_part, "name": name, "is_internal": is_internal}

        if password:
            data["password"] = password
        elif password_recovery_email:
            data["password_method"] = "invitation"
            data["password_recovery_email"] = password_recovery_email

        if forwarding_to:
            data["forwarding_to"] = forwarding_to

        return await self.client.request(
            "POST", f"/domains/{domain}/mailboxes", json=data
        )

    async def update_mailbox(
        self,
        domain: str,
        local_part: str,
        name: Optional[str] = None,
        may_send: Optional[bool] = None,
        may_receive: Optional[bool] = None,
        may_access_imap: Optional[bool] = None,
        may_access_pop3: Optional[bool] = None,
        spam_action: Optional[str] = None,
        spam_aggressiveness: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Modify configuration settings for an existing mailbox including permissions and spam filtering.

        Allows selective updates to display name, send/receive permissions, protocol access controls,
        and spam filtering behavior without affecting other mailbox settings.
        """
        data: Dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if may_send is not None:
            data["may_send"] = may_send
        if may_receive is not None:
            data["may_receive"] = may_receive
        if may_access_imap is not None:
            data["may_access_imap"] = may_access_imap
        if may_access_pop3 is not None:
            data["may_access_pop3"] = may_access_pop3
        if spam_action is not None:
            data["spam_action"] = spam_action
        if spam_aggressiveness is not None:
            data["spam_aggressiveness"] = spam_aggressiveness

        return await self.client.request(
            "PUT", f"/domains/{domain}/mailboxes/{local_part}", json=data
        )

    async def delete_mailbox(self, domain: str, local_part: str) -> Dict[str, Any]:
        """Permanently delete a mailbox and all stored messages with API bug handling.

        Note: Due to Migadu API bug, successful deletions may return HTTP 500 errors.
        The operation actually succeeds despite the error response.
        """
        return await self.client.request(
            "DELETE", f"/domains/{domain}/mailboxes/{local_part}"
        )

    async def bulk_delete_mailboxes(
        self, domain: str, local_parts: List[str]
    ) -> Dict[str, Any]:
        """Delete multiple mailboxes efficiently with intelligent error handling for the Migadu API bug.

        Automatically categorizes results as deleted, already gone, or failed, handling the API's
        incorrect 500 error responses for successful deletions.
        """
        results: Dict[str, Any] = {
            "deleted": [],
            "already_gone": [],
            "failed": [],
            "total_requested": len(local_parts),
        }

        for local_part in local_parts:
            try:
                await self.client.request(
                    "DELETE", f"/domains/{domain}/mailboxes/{local_part}"
                )
                # If we get here without exception, it actually succeeded
                results["deleted"].append(local_part)
            except MigaduAPIError as e:
                if e.is_success:
                    # 500 error = successful deletion due to API bug
                    results["deleted"].append(local_part)
                elif e.status_code == 404 or "no such mailbox" in str(e).lower():
                    # Already deleted
                    results["already_gone"].append(local_part)
                else:
                    # Actual failure
                    results["failed"].append(
                        {"local_part": local_part, "error": str(e)}
                    )
            except Exception as e:
                # Other exceptions
                results["failed"].append({"local_part": local_part, "error": str(e)})

        return results

    async def reset_mailbox_password(
        self, domain: str, local_part: str, new_password: str
    ) -> Dict[str, Any]:
        """Reset mailbox password"""
        data = {"password": new_password}
        return await self.client.request(
            "PUT", f"/domains/{domain}/mailboxes/{local_part}", json=data
        )

    async def set_autoresponder(
        self,
        domain: str,
        local_part: str,
        active: bool,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        expires_on: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Configure mailbox autoresponder"""
        data: Dict[str, Any] = {"autorespond_active": active}
        if subject:
            data["autorespond_subject"] = subject
        if body:
            data["autorespond_body"] = body
        if expires_on:
            data["autorespond_expires_on"] = expires_on

        return await self.client.request(
            "PUT", f"/domains/{domain}/mailboxes/{local_part}", json=data
        )

    async def list_forwardings(self, domain: str, mailbox: str) -> Dict[str, Any]:
        """List all forwardings for a mailbox"""
        return await self.client.request(
            "GET", f"/domains/{domain}/mailboxes/{mailbox}/forwardings"
        )

    async def create_forwarding(
        self, domain: str, mailbox: str, address: str
    ) -> Dict[str, Any]:
        """Create a new forwarding for a mailbox"""
        data = {"address": address}
        return await self.client.request(
            "POST", f"/domains/{domain}/mailboxes/{mailbox}/forwardings", json=data
        )

    async def get_forwarding(
        self, domain: str, mailbox: str, address: str
    ) -> Dict[str, Any]:
        """Get details of a specific forwarding"""
        # URL encode the email address
        encoded_address = address.replace("@", "%40")
        return await self.client.request(
            "GET",
            f"/domains/{domain}/mailboxes/{mailbox}/forwardings/{encoded_address}",
        )

    async def update_forwarding(
        self,
        domain: str,
        mailbox: str,
        address: str,
        is_active: Optional[bool] = None,
        expires_on: Optional[str] = None,
        remove_upon_expiry: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Update forwarding settings"""
        data: Dict[str, Any] = {}
        if is_active is not None:
            data["is_active"] = is_active
        if expires_on is not None:
            data["expires_on"] = expires_on
        if remove_upon_expiry is not None:
            data["remove_upon_expiry"] = remove_upon_expiry

        encoded_address = address.replace("@", "%40")
        return await self.client.request(
            "PUT",
            f"/domains/{domain}/mailboxes/{mailbox}/forwardings/{encoded_address}",
            json=data,
        )

    async def delete_forwarding(
        self, domain: str, mailbox: str, address: str
    ) -> Dict[str, Any]:
        """Delete a forwarding"""
        encoded_address = address.replace("@", "%40")
        return await self.client.request(
            "DELETE",
            f"/domains/{domain}/mailboxes/{mailbox}/forwardings/{encoded_address}",
        )
