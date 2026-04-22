"""MCP tools for domain operations."""

from typing import Any

from fastmcp import Context, FastMCP

from migadu_mcp.services.service_factory import get_service_factory
from migadu_mcp.utils.decorators import migadu_bulk_tool, migadu_tool
from migadu_mcp.utils.schemas import (
    DomainActivateRequest,
    DomainCreateRequest,
    DomainUpdateRequest,
)


def register_domain_tools(mcp: FastMCP) -> None:
    @migadu_tool(mcp, read_only=True, summarize_response=True)
    async def list_domains(ctx: Context) -> dict[str, Any]:
        """List all domains for the authenticated account."""
        await ctx.info("📋 Listing domains")
        return await get_service_factory().domain_service().list_domains()

    @migadu_tool(mcp, read_only=True)
    async def get_domain(name: str, ctx: Context) -> dict[str, Any]:
        """Get full details for a specific domain."""
        await ctx.info(f"📋 Getting domain {name}")
        return await get_service_factory().domain_service().get_domain(name)

    @migadu_tool(mcp, read_only=True)
    async def get_domain_records(name: str, ctx: Context) -> dict[str, Any]:
        """Get the DNS records (MX, SPF, DKIM, DMARC, verification) required for domain setup."""
        await ctx.info(f"📋 Fetching DNS records for {name}")
        return await get_service_factory().domain_service().get_domain_records(name)

    @migadu_tool(mcp, read_only=True)
    async def get_domain_diagnostics(name: str, ctx: Context) -> dict[str, Any]:
        """Run DNS validation diagnostics on a domain. Use after configuring records externally."""
        await ctx.info(f"📋 Running diagnostics for {name}")
        return await get_service_factory().domain_service().get_domain_diagnostics(name)

    @migadu_tool(mcp, read_only=True)
    async def get_domain_usage(name: str, ctx: Context) -> dict[str, Any]:
        """Get message and storage usage metrics for a domain."""
        await ctx.info(f"📋 Getting usage for {name}")
        return await get_service_factory().domain_service().get_domain_usage(name)

    @migadu_bulk_tool(mcp, DomainCreateRequest, entity="domain", idempotent=False)
    async def create_domain(item: DomainCreateRequest, ctx: Context) -> dict[str, Any]:
        """Create domain(s). Migadu recommends hosted_dns=False (use external DNS). List of dicts with: name, hosted_dns (optional, default false), create_default_addresses (optional, default true)."""
        await ctx.info(f"📋 Creating domain {item.name}")
        result = (
            await get_service_factory()
            .domain_service()
            .create_domain(item.name, item.hosted_dns, item.create_default_addresses)
        )
        return {"domain": result, "name": item.name, "success": True}

    @migadu_bulk_tool(mcp, DomainUpdateRequest, entity="domain")
    async def update_domain(item: DomainUpdateRequest, ctx: Context) -> dict[str, Any]:
        """Update domain field(s). List of dicts with: name (required), description (optional), tags (optional)."""
        await ctx.info(f"📋 Updating domain {item.name}")
        result = (
            await get_service_factory()
            .domain_service()
            .update_domain(item.name, item.description, item.tags)
        )
        return {"domain": result, "name": item.name, "success": True}

    @migadu_bulk_tool(mcp, DomainActivateRequest, entity="domain activation")
    async def activate_domain(
        item: DomainActivateRequest, ctx: Context
    ) -> dict[str, Any]:
        """Activate domain(s) once DNS records are configured. Fails with 422 if DNS validation fails. List of dicts with: name."""
        await ctx.info(f"📋 Activating domain {item.name}")
        result = await get_service_factory().domain_service().activate_domain(item.name)
        return {"domain": result, "name": item.name, "success": True}

    _ = (
        list_domains,
        get_domain,
        get_domain_records,
        get_domain_diagnostics,
        get_domain_usage,
        create_domain,
        update_domain,
        activate_domain,
    )
