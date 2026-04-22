"""MCP tools for alias operations."""

from typing import Any

from fastmcp import Context, FastMCP

from migadu_mcp.services.service_factory import get_service_factory
from migadu_mcp.utils.decorators import migadu_bulk_tool, migadu_tool, resolve_domain
from migadu_mcp.utils.email_parsing import format_email_address
from migadu_mcp.utils.schemas import (
    AliasCreateRequest,
    AliasDeleteRequest,
    AliasUpdateRequest,
)


def register_alias_tools(mcp: FastMCP) -> None:
    @migadu_tool(mcp, read_only=True, summarize_response=True)
    async def list_aliases(ctx: Context, domain: str | None = None) -> dict[str, Any]:
        """List aliases for a domain."""
        resolved = resolve_domain(domain)
        await ctx.info(f"📋 Listing aliases for {resolved}")
        return await get_service_factory().alias_service().list_aliases(resolved)

    @migadu_tool(mcp, read_only=True)
    async def get_alias(
        target: str, ctx: Context, domain: str | None = None
    ) -> dict[str, Any]:
        """Get alias details by local part."""
        resolved = resolve_domain(domain)
        await ctx.info(f"📋 Getting alias {target}@{resolved}")
        return await get_service_factory().alias_service().get_alias(resolved, target)

    @migadu_bulk_tool(mcp, AliasCreateRequest, entity="alias", idempotent=False)
    async def create_alias(item: AliasCreateRequest, ctx: Context) -> dict[str, Any]:
        """Create alias(es). List of dicts with: target, destinations (list or CSV), domain (optional), is_internal (optional)."""
        domain = item.domain or resolve_domain(None)
        email = format_email_address(domain, item.target)
        destinations = [str(d) for d in item.destinations]
        await ctx.info(f"📋 Creating alias {email} -> {', '.join(destinations)}")
        result = (
            await get_service_factory()
            .alias_service()
            .create_alias(domain, item.target, destinations, item.is_internal)
        )
        return {"alias": result, "email_address": email, "success": True}

    @migadu_bulk_tool(mcp, AliasUpdateRequest, entity="alias")
    async def update_alias(item: AliasUpdateRequest, ctx: Context) -> dict[str, Any]:
        """Update alias destinations. List of dicts with: target, destinations (list or CSV), domain (optional)."""
        domain = item.domain or resolve_domain(None)
        email = format_email_address(domain, item.target)
        destinations = [str(d) for d in item.destinations]
        await ctx.info(f"📋 Updating alias {email} -> {', '.join(destinations)}")
        result = (
            await get_service_factory()
            .alias_service()
            .update_alias(domain, item.target, destinations)
        )
        return {"alias": result, "email_address": email, "success": True}

    @migadu_bulk_tool(mcp, AliasDeleteRequest, entity="alias", destructive=True)
    async def delete_alias(item: AliasDeleteRequest, ctx: Context) -> dict[str, Any]:
        """Delete alias(es). DESTRUCTIVE. List of dicts with: target, domain (optional)."""
        domain = item.domain or resolve_domain(None)
        email = format_email_address(domain, item.target)
        await ctx.warning(f"🗑️ Deleting alias {email}")
        await get_service_factory().alias_service().delete_alias(domain, item.target)
        return {"deleted": email, "success": True}

    _ = (list_aliases, get_alias, create_alias, update_alias, delete_alias)
