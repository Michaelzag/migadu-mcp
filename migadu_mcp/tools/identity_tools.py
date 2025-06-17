#!/usr/bin/env python3
"""
MCP tools for identity operations
"""

from typing import Dict, Any, Optional
from fastmcp import FastMCP
from migadu_mcp.services.service_factory import get_service_factory


def register_identity_tools(mcp: FastMCP):
    """Register identity tools with FastMCP instance"""

    @mcp.tool
    async def list_identities(domain: str, mailbox: str) -> Dict[str, Any]:
        """Retrieve all email identities configured for a mailbox. Identities are additional 'send-as'
        email addresses that a mailbox user can use when composing messages, beyond their primary email
        address. Each identity has its own permissions, display name, and access controls. Use this to
        audit which additional email addresses a user can send from and manage identity-based permissions.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            mailbox: Username part of the mailbox (e.g., 'demo' for demo@mydomain.org)

        Returns:
            JSON object containing array of all identities with permissions and configuration
        """
        factory = get_service_factory()
        service = factory.identity_service()
        return await service.list_identities(domain, mailbox)

    @mcp.tool
    async def create_identity(
        domain: str, mailbox: str, local_part: str, name: str, password: str
    ) -> Dict[str, Any]:
        """Create a new email identity for a mailbox user. Identities allow users to send emails from
        additional addresses within the same domain while using their existing mailbox for storage and
        authentication. This is useful for role-based email addresses (support@, sales@) or departmental
        addresses that should be managed by specific users. The identity requires its own password for
        SMTP authentication when sending.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            mailbox: Username of the mailbox that will own this identity (e.g., 'demo')
            local_part: Username part of the new identity address (e.g., 'support' for support@mydomain.org)
            name: Display name for this identity (e.g., 'Support Team')
            password: Password for SMTP authentication when sending from this identity

        Returns:
            JSON object with newly created identity configuration and permissions
        """
        factory = get_service_factory()
        service = factory.identity_service()
        return await service.create_identity(
            domain, mailbox, local_part, name, password
        )

    @mcp.tool
    async def get_identity(domain: str, mailbox: str, identity: str) -> Dict[str, Any]:
        """Retrieve detailed information about a specific email identity. Shows the identity's
        configuration including display name, permissions (send/receive/IMAP/POP3 access), and footer
        settings. Use this to inspect identity settings before making changes or troubleshooting
        send-as issues.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            mailbox: Username of the mailbox that owns this identity (e.g., 'demo')
            identity: Local part of the identity address (e.g., 'support' for support@mydomain.org)

        Returns:
            JSON object with complete identity configuration and permissions
        """
        factory = get_service_factory()
        service = factory.identity_service()
        return await service.get_identity(domain, mailbox, identity)

    @mcp.tool
    async def update_identity(
        domain: str,
        mailbox: str,
        identity: str,
        name: Optional[str] = None,
        may_send: Optional[bool] = None,
        may_receive: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Modify configuration settings for an existing email identity. Update the display name or
        adjust permissions for sending and receiving emails. Common use cases include changing role
        titles, restricting send-only identities, or disabling identities temporarily without deletion.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            mailbox: Username of the mailbox that owns this identity (e.g., 'demo')
            identity: Local part of the identity address (e.g., 'support' for support@mydomain.org)
            name: Update display name for this identity
            may_send: Allow/deny sending emails from this identity
            may_receive: Allow/deny receiving emails to this identity address

        Returns:
            JSON object with updated identity configuration
        """
        factory = get_service_factory()
        service = factory.identity_service()
        return await service.update_identity(
            domain, mailbox, identity, name, may_send, may_receive
        )

    @mcp.tool
    async def delete_identity(
        domain: str, mailbox: str, identity: str
    ) -> Dict[str, Any]:
        """Permanently remove an email identity from a mailbox. The identity address will no longer
        be available for sending or receiving emails, and cannot be used for SMTP authentication.
        This action is irreversible - the identity address becomes available for reuse after deletion.
        Use this to clean up old role-based addresses or when reassigning identities to different mailboxes.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            mailbox: Username of the mailbox that owns this identity (e.g., 'demo')
            identity: Local part of the identity address to delete (e.g., 'support')

        Returns:
            JSON object confirming identity deletion
        """
        factory = get_service_factory()
        service = factory.identity_service()
        return await service.delete_identity(domain, mailbox, identity)
