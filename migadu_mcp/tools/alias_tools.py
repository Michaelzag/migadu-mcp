#!/usr/bin/env python3
"""
MCP tools for alias operations
"""

from typing import Dict, Any, List
from fastmcp import FastMCP
from migadu_mcp.services.service_factory import get_service_factory


def register_alias_tools(mcp: FastMCP):
    """Register alias tools with FastMCP instance"""

    @mcp.tool
    async def list_aliases(domain: str) -> Dict[str, Any]:
        """Retrieve all email aliases configured for a domain. Aliases are email addresses that
        automatically forward incoming messages to one or more destination addresses without storing
        the messages themselves. Unlike mailboxes, aliases have no storage, authentication, or IMAP/POP3
        access - they only redirect messages. Each alias shows its destinations, internal-only status,
        and routing configuration. Use this to audit email forwarding rules and manage domain-wide
        email routing infrastructure.

        Args:
            domain: The domain name to list aliases for (e.g., 'mydomain.org')

        Returns:
            JSON object containing array of all aliases with their destinations and configuration
        """
        factory = get_service_factory()
        service = factory.alias_service()
        return await service.list_aliases(domain)

    @mcp.tool
    async def create_alias(
        domain: str, local_part: str, destinations: List[str], is_internal: bool = False
    ) -> Dict[str, Any]:
        """Create a new email alias that forwards messages to specified destination addresses. Aliases
        provide email forwarding without storage - incoming messages are immediately redirected to the
        destination addresses on the same domain. Use is_internal=True to restrict the alias to only
        accept messages from Migadu servers (useful for system notifications). Perfect for creating
        distribution lists, department addresses, or role-based email addresses.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            local_part: Username part of the alias address (e.g., 'sales' for sales@mydomain.org)
            destinations: List of email addresses to forward messages to (must be on same domain)
            is_internal: If True, only accepts messages from Migadu servers (no external email)

        Returns:
            JSON object with newly created alias configuration showing destinations
        """
        factory = get_service_factory()
        service = factory.alias_service()
        return await service.create_alias(domain, local_part, destinations, is_internal)

    @mcp.tool
    async def get_alias(domain: str, local_part: str) -> Dict[str, Any]:
        """Retrieve detailed information about a specific email alias. Shows the alias configuration
        including all destination addresses, internal-only status, and routing behavior. Use this to
        inspect alias settings before making changes or troubleshooting message delivery issues.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            local_part: Username part of the alias address (e.g., 'sales' for sales@mydomain.org)

        Returns:
            JSON object with complete alias configuration including destinations
        """
        factory = get_service_factory()
        service = factory.alias_service()
        return await service.get_alias(domain, local_part)

    @mcp.tool
    async def update_alias(
        domain: str, local_part: str, destinations: List[str]
    ) -> Dict[str, Any]:
        """Modify the destination addresses for an existing email alias. This changes where the alias
        forwards incoming messages without affecting the alias address itself. All destinations must
        be on the same domain as the alias. Use this to update distribution lists, change department
        routing, or modify forwarding rules for role-based addresses.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            local_part: Username part of the alias address (e.g., 'sales' for sales@mydomain.org)
            destinations: New list of email addresses to forward messages to (must be on same domain)

        Returns:
            JSON object with updated alias configuration showing new destinations
        """
        factory = get_service_factory()
        service = factory.alias_service()
        return await service.update_alias(domain, local_part, destinations)

    @mcp.tool
    async def delete_alias(domain: str, local_part: str) -> Dict[str, Any]:
        """Permanently remove an email alias from the domain. The alias address will no longer accept
        or forward messages, and becomes available for reuse. This action is immediate and irreversible.
        Use this to clean up old distribution lists, discontinued role addresses, or when reorganizing
        email routing infrastructure.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            local_part: Username part of the alias address to delete (e.g., 'sales')

        Returns:
            JSON object confirming alias deletion
        """
        factory = get_service_factory()
        service = factory.alias_service()
        return await service.delete_alias(domain, local_part)
