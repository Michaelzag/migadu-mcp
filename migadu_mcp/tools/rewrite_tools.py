#!/usr/bin/env python3
"""
MCP tools for rewrite operations
"""

from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from migadu_mcp.services.service_factory import get_service_factory


def register_rewrite_tools(mcp: FastMCP):
    """Register rewrite tools with FastMCP instance"""

    @mcp.tool
    async def list_rewrites(domain: str) -> Dict[str, Any]:
        """Retrieve all pattern-based rewrite rules configured for a domain. Rewrites are advanced
        aliases that use wildcard patterns to match multiple email addresses and forward them to
        specified destinations. Unlike regular aliases, rewrites can capture entire ranges of addresses
        using patterns like 'support-*' to match support-tickets, support-billing, etc. Each rewrite
        shows its pattern rule, destinations, and processing order. Use this to manage dynamic email
        routing and pattern-based forwarding systems.

        Args:
            domain: The domain name to list rewrite rules for (e.g., 'mydomain.org')

        Returns:
            JSON object containing array of all rewrite rules with patterns and destinations
        """
        factory = get_service_factory()
        service = factory.rewrite_service()
        return await service.list_rewrites(domain)

    @mcp.tool
    async def create_rewrite(
        domain: str, name: str, local_part_rule: str, destinations: List[str]
    ) -> Dict[str, Any]:
        """Create a new pattern-based rewrite rule for dynamic email forwarding. Rewrites use wildcard
        patterns to match multiple email addresses and forward them to specified destinations. For example,
        a pattern 'demo-*' will match demo-test, demo-staging, demo-production, etc. This enables dynamic
        email routing without creating individual aliases for each variation. Destinations must be on the
        same domain - external addresses will be rewritten to the domain.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            name: Unique identifier/slug for this rewrite rule (e.g., 'demo-catchall')
            local_part_rule: Pattern to match email addresses (e.g., 'demo-*' or 'support-*')
            destinations: List of email addresses to forward matched messages to (same domain only)

        Returns:
            JSON object with newly created rewrite rule configuration
        """
        factory = get_service_factory()
        service = factory.rewrite_service()
        return await service.create_rewrite(domain, name, local_part_rule, destinations)

    @mcp.tool
    async def get_rewrite(domain: str, name: str) -> Dict[str, Any]:
        """Retrieve detailed information about a specific pattern-based rewrite rule. Shows the wildcard
        pattern, destination addresses, processing order, and rule configuration. Use this to inspect
        rewrite settings before making changes or troubleshooting pattern-based email routing issues.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            name: Unique identifier/slug of the rewrite rule (e.g., 'demo-catchall')

        Returns:
            JSON object with complete rewrite rule configuration and pattern details
        """
        factory = get_service_factory()
        service = factory.rewrite_service()
        return await service.get_rewrite(domain, name)

    @mcp.tool
    async def update_rewrite(
        domain: str,
        name: str,
        new_name: Optional[str] = None,
        local_part_rule: Optional[str] = None,
        destinations: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Modify configuration for an existing pattern-based rewrite rule. Update the rule name,
        change the wildcard pattern, or modify destination addresses. Use this to adjust pattern
        matching behavior, update forwarding destinations, or rename rules for better organization.
        All destinations must remain on the same domain.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            name: Current unique identifier/slug of the rewrite rule
            new_name: New identifier/slug for the rule (optional)
            local_part_rule: New pattern to match email addresses (e.g., 'support-*')
            destinations: New list of email addresses to forward to (same domain only)

        Returns:
            JSON object with updated rewrite rule configuration
        """
        factory = get_service_factory()
        service = factory.rewrite_service()
        return await service.update_rewrite(
            domain, name, new_name, local_part_rule, destinations
        )

    @mcp.tool
    async def delete_rewrite(domain: str, name: str) -> Dict[str, Any]:
        """Permanently remove a pattern-based rewrite rule from the domain. The wildcard pattern will
        no longer match or forward messages, and all matching email addresses become unavailable. This
        action is immediate and irreversible. Use this to clean up old pattern rules or when restructuring
        dynamic email routing systems.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            name: Unique identifier/slug of the rewrite rule to delete

        Returns:
            JSON object confirming rewrite rule deletion
        """
        factory = get_service_factory()
        service = factory.rewrite_service()
        return await service.delete_rewrite(domain, name)
