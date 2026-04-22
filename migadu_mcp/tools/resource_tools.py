"""MCP resources for Migadu — read-only views mapped to URI templates."""

from typing import Any

from fastmcp import Context, FastMCP

from migadu_mcp.services.service_factory import get_service_factory


def register_resources(mcp: FastMCP) -> None:
    # --- Domain-level ---

    @mcp.resource(
        "domains://",
        name="All Domains",
        description="All domains for the authenticated account",
        mime_type="application/json",
        tags={"domain", "account", "inventory"},
    )
    async def all_domains(ctx: Context) -> dict[str, Any]:
        await ctx.info("📋 Loading all domains")
        return await get_service_factory().domain_service().list_domains()

    @mcp.resource(
        "domain://{name}",
        name="Domain Details",
        description="Full configuration details for a specific domain",
        mime_type="application/json",
        tags={"domain", "configuration"},
    )
    async def domain_details(name: str, ctx: Context) -> dict[str, Any]:
        await ctx.info(f"📋 Loading domain {name}")
        return await get_service_factory().domain_service().get_domain(name)

    @mcp.resource(
        "domain-records://{name}",
        name="Domain DNS Records",
        description="DNS records required to set up a domain (MX, SPF, DKIM, DMARC, verification)",
        mime_type="application/json",
        tags={"domain", "dns", "setup"},
    )
    async def domain_records(name: str, ctx: Context) -> dict[str, Any]:
        await ctx.info(f"📋 Loading DNS records for {name}")
        return await get_service_factory().domain_service().get_domain_records(name)

    @mcp.resource(
        "domain-usage://{name}",
        name="Domain Usage",
        description="Message and storage usage metrics for a domain",
        mime_type="application/json",
        tags={"domain", "metrics", "usage"},
    )
    async def domain_usage(name: str, ctx: Context) -> dict[str, Any]:
        await ctx.info(f"📋 Loading usage for {name}")
        return await get_service_factory().domain_service().get_domain_usage(name)

    # --- Mailbox-level ---

    @mcp.resource(
        "mailboxes://{domain}",
        name="Domain Mailboxes",
        description="All email mailboxes for a domain",
        mime_type="application/json",
        tags={"mailbox", "domain", "inventory"},
    )
    async def domain_mailboxes(domain: str, ctx: Context) -> dict[str, Any]:
        await ctx.info(f"📋 Loading mailboxes for {domain}")
        return await get_service_factory().mailbox_service().list_mailboxes(domain)

    @mcp.resource(
        "mailbox://{domain}/{local_part}",
        name="Mailbox Details",
        description="Full configuration for a specific mailbox",
        mime_type="application/json",
        tags={"mailbox", "configuration"},
    )
    async def mailbox_details(
        domain: str, local_part: str, ctx: Context
    ) -> dict[str, Any]:
        await ctx.info(f"📋 Loading mailbox {local_part}@{domain}")
        return (
            await get_service_factory()
            .mailbox_service()
            .get_mailbox(domain, local_part)
        )

    @mcp.resource(
        "identities://{domain}/{mailbox}",
        name="Mailbox Identities",
        description="Send-as identities configured for a mailbox",
        mime_type="application/json",
        tags={"identity", "mailbox"},
    )
    async def mailbox_identities(
        domain: str, mailbox: str, ctx: Context
    ) -> dict[str, Any]:
        await ctx.info(f"📋 Loading identities for {mailbox}@{domain}")
        return (
            await get_service_factory()
            .identity_service()
            .list_identities(domain, mailbox)
        )

    @mcp.resource(
        "forwardings://{domain}/{mailbox}",
        name="Mailbox Forwardings",
        description="External forwardings configured for a mailbox",
        mime_type="application/json",
        tags={"forwarding", "mailbox"},
    )
    async def mailbox_forwardings(
        domain: str, mailbox: str, ctx: Context
    ) -> dict[str, Any]:
        await ctx.info(f"📋 Loading forwardings for {mailbox}@{domain}")
        return (
            await get_service_factory()
            .forwarding_service()
            .list_forwardings(domain, mailbox)
        )

    @mcp.resource(
        "aliases://{domain}",
        name="Domain Aliases",
        description="All aliases for a domain",
        mime_type="application/json",
        tags={"alias", "domain"},
    )
    async def domain_aliases(domain: str, ctx: Context) -> dict[str, Any]:
        await ctx.info(f"📋 Loading aliases for {domain}")
        return await get_service_factory().alias_service().list_aliases(domain)

    @mcp.resource(
        "rewrites://{domain}",
        name="Domain Rewrites",
        description="All pattern-based rewrite rules for a domain",
        mime_type="application/json",
        tags={"rewrite", "domain"},
    )
    async def domain_rewrites(domain: str, ctx: Context) -> dict[str, Any]:
        await ctx.info(f"📋 Loading rewrites for {domain}")
        return await get_service_factory().rewrite_service().list_rewrites(domain)

    _ = (
        all_domains,
        domain_details,
        domain_records,
        domain_usage,
        domain_mailboxes,
        mailbox_details,
        mailbox_identities,
        mailbox_forwardings,
        domain_aliases,
        domain_rewrites,
    )
