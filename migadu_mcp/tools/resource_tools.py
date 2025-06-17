#!/usr/bin/env python3
"""
MCP resources for Migadu API
"""

from typing import Dict, Any
from fastmcp import FastMCP, Context
from migadu_mcp.services.service_factory import get_service_factory


def register_resources(mcp: FastMCP):
    """Register resources with FastMCP instance"""

    @mcp.resource(
        "mailboxes://{domain}",
        name="Domain Mailboxes",
        description="Comprehensive overview of all email mailboxes configured for a domain",
        mime_type="application/json",
        tags={"mailbox", "domain", "inventory", "audit"},
    )
    async def domain_mailboxes(domain: str, ctx: Context) -> Dict[str, Any]:
        """Resource providing comprehensive overview of all email mailboxes configured for a domain.
        Returns detailed information for each mailbox including storage status, permissions, spam settings,
        autoresponder configuration, and account security options. Use this resource for domain-wide
        mailbox auditing, capacity planning, and organizational email infrastructure analysis.

        URI Format: mailboxes://example.org
        """
        await ctx.info(f"📋 Loading mailbox inventory for domain: {domain}")

        try:
            factory = get_service_factory()
            service = factory.mailbox_service()
            result = await service.list_mailboxes(domain)
            count = len(result.get("mailboxes", []))
            await ctx.info(f"✅ Loaded {count} mailboxes for {domain}")
            return result
        except Exception as e:
            await ctx.error(f"❌ Failed to load mailboxes for {domain}: {str(e)}")
            raise

    @mcp.resource(
        "mailbox://{domain}/{local_part}",
        name="Mailbox Details",
        description="Complete configuration and status details for a specific email mailbox",
        mime_type="application/json",
        tags={"mailbox", "details", "configuration", "troubleshooting"},
    )
    async def mailbox_details(
        domain: str, local_part: str, ctx: Context
    ) -> Dict[str, Any]:
        """Resource providing complete configuration details for a specific email mailbox. Includes
        authentication settings, protocol permissions (IMAP/POP3/ManageSieve), spam filtering configuration,
        autoresponder status, footer settings, allowlists/denylists, and security policies. Use this
        resource for detailed mailbox inspection, troubleshooting, and configuration verification.

        URI Format: mailbox://example.org/username
        """
        email_address = f"{local_part}@{domain}"
        await ctx.info(f"📋 Loading detailed configuration for: {email_address}")

        try:
            factory = get_service_factory()
            service = factory.mailbox_service()
            result = await service.get_mailbox(domain, local_part)
            await ctx.info(f"✅ Loaded configuration for {email_address}")
            return result
        except Exception as e:
            await ctx.error(
                f"❌ Failed to load mailbox details for {email_address}: {str(e)}"
            )
            raise

    @mcp.resource(
        "identities://{domain}/{mailbox}",
        name="Mailbox Identities",
        description="Send-as email addresses and permissions for a mailbox",
        mime_type="application/json",
        tags={"identity", "mailbox", "permissions", "send-as"},
    )
    async def mailbox_identities(
        domain: str, mailbox: str, ctx: Context
    ) -> Dict[str, Any]:
        """Resource providing all email identities (send-as addresses) configured for a specific mailbox.
        Shows additional email addresses the mailbox user can send from, each with their own permissions,
        display names, and access controls. Use this resource to audit send-as capabilities and manage
        role-based email address permissions within an organization.

        URI Format: identities://example.org/username
        """
        await ctx.info(f"📋 Loading identities for mailbox: {mailbox}@{domain}")

        try:
            factory = get_service_factory()
            service = factory.identity_service()
            result = await service.list_identities(domain, mailbox)
            count = len(result.get("identities", []))
            await ctx.info(f"✅ Loaded {count} identities for {mailbox}@{domain}")
            return result
        except Exception as e:
            await ctx.error(
                f"❌ Failed to load identities for {mailbox}@{domain}: {str(e)}"
            )
            raise

    @mcp.resource(
        "forwardings://{domain}/{mailbox}",
        name="Mailbox Forwardings",
        description="External forwarding rules and confirmation status for a mailbox",
        mime_type="application/json",
        tags={"forwarding", "mailbox", "external", "routing"},
    )
    async def mailbox_forwardings(
        domain: str, mailbox: str, ctx: Context
    ) -> Dict[str, Any]:
        """Resource providing all external forwarding rules configured for a specific mailbox. Shows
        destination addresses, confirmation status, expiration settings, and active state for each
        forwarding rule. Use this resource to audit external message routing, verify forwarding
        confirmations, and manage temporary or scheduled forwarding arrangements.

        URI Format: forwardings://example.org/username
        """
        await ctx.info(f"📋 Loading forwarding rules for mailbox: {mailbox}@{domain}")

        try:
            factory = get_service_factory()
            service = factory.mailbox_service()
            result = await service.list_forwardings(domain, mailbox)
            count = len(result.get("forwardings", []))
            await ctx.info(f"✅ Loaded {count} forwarding rules for {mailbox}@{domain}")
            return result
        except Exception as e:
            await ctx.error(
                f"❌ Failed to load forwardings for {mailbox}@{domain}: {str(e)}"
            )
            raise

    @mcp.resource(
        "aliases://{domain}",
        name="Domain Aliases",
        description="Overview of all email aliases and forwarding rules for a domain",
        mime_type="application/json",
        tags={"alias", "domain", "forwarding", "routing"},
    )
    async def domain_aliases(domain: str, ctx: Context) -> Dict[str, Any]:
        """Resource providing comprehensive overview of all email aliases configured for a domain.
        Shows forwarding addresses that redirect messages without storage, including destination
        addresses, internal-only status, and routing configuration. Use this resource for domain-wide
        forwarding audits, distribution list management, and email routing infrastructure analysis.

        URI Format: aliases://example.org
        """
        await ctx.info(f"📋 Loading alias inventory for domain: {domain}")

        try:
            factory = get_service_factory()
            service = factory.alias_service()
            result = await service.list_aliases(domain)
            count = len(result.get("aliases", []))
            await ctx.info(f"✅ Loaded {count} aliases for {domain}")
            return result
        except Exception as e:
            await ctx.error(f"❌ Failed to load aliases for {domain}: {str(e)}")
            raise

    @mcp.resource("rewrites://{domain}")
    async def domain_rewrites(domain: str) -> Dict[str, Any]:
        """Resource providing all pattern-based rewrite rules configured for a domain. Shows wildcard
        patterns, destination addresses, processing order, and rule configuration for dynamic email
        routing. Use this resource to audit pattern-based forwarding systems, verify rule precedence,
        and manage complex email routing scenarios that require wildcard matching.

        URI Format: rewrites://example.org
        """
        factory = get_service_factory()
        service = factory.rewrite_service()
        return await service.list_rewrites(domain)
