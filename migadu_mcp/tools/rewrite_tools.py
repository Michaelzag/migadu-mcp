"""MCP tools for rewrite operations."""

from typing import Any

from fastmcp import Context, FastMCP

from migadu_mcp.services.service_factory import get_service_factory
from migadu_mcp.utils.decorators import migadu_bulk_tool, migadu_tool, resolve_domain
from migadu_mcp.utils.schemas import (
    RewriteCreateRequest,
    RewriteDeleteRequest,
    RewriteUpdateRequest,
)


def register_rewrite_tools(mcp: FastMCP) -> None:
    @migadu_tool(mcp, read_only=True, summarize_response=True)
    async def list_rewrites(ctx: Context, domain: str | None = None) -> dict[str, Any]:
        """List rewrite rules for a domain."""
        resolved = resolve_domain(domain)
        await ctx.info(f"📋 Listing rewrites for {resolved}")
        return await get_service_factory().rewrite_service().list_rewrites(resolved)

    @migadu_tool(mcp, read_only=True)
    async def get_rewrite(
        name: str, ctx: Context, domain: str | None = None
    ) -> dict[str, Any]:
        """Get rewrite rule details by slug/name."""
        resolved = resolve_domain(domain)
        await ctx.info(f"📋 Getting rewrite {name} for {resolved}")
        return await get_service_factory().rewrite_service().get_rewrite(resolved, name)

    @migadu_bulk_tool(mcp, RewriteCreateRequest, entity="rewrite", idempotent=False)
    async def create_rewrite(
        item: RewriteCreateRequest, ctx: Context
    ) -> dict[str, Any]:
        """Create rewrite rule(s). List of dicts with: name, local_part_rule (pattern), destinations, domain (optional), order_num (optional)."""
        domain = item.domain or resolve_domain(None)
        destinations = [str(d) for d in item.destinations]
        await ctx.info(f"📋 Creating rewrite {item.name} on {domain}")
        result = (
            await get_service_factory()
            .rewrite_service()
            .create_rewrite(
                domain, item.name, item.local_part_rule, destinations, item.order_num
            )
        )
        return {"rewrite": result, "success": True}

    @migadu_bulk_tool(mcp, RewriteUpdateRequest, entity="rewrite")
    async def update_rewrite(
        item: RewriteUpdateRequest, ctx: Context
    ) -> dict[str, Any]:
        """Update rewrite rule(s). List of dicts with: name (required), and any of: new_name, local_part_rule, destinations, order_num, domain."""
        domain = item.domain or resolve_domain(None)
        destinations = (
            [str(d) for d in item.destinations] if item.destinations else None
        )
        await ctx.info(f"📋 Updating rewrite {item.name} on {domain}")
        result = (
            await get_service_factory()
            .rewrite_service()
            .update_rewrite(
                domain,
                item.name,
                item.new_name,
                item.local_part_rule,
                destinations,
                item.order_num,
            )
        )
        return {"rewrite": result, "success": True}

    @migadu_bulk_tool(mcp, RewriteDeleteRequest, entity="rewrite", destructive=True)
    async def delete_rewrite(
        item: RewriteDeleteRequest, ctx: Context
    ) -> dict[str, Any]:
        """Delete rewrite rule(s). DESTRUCTIVE. List of dicts with: name, domain (optional)."""
        domain = item.domain or resolve_domain(None)
        await ctx.warning(f"🗑️ Deleting rewrite {item.name}")
        await get_service_factory().rewrite_service().delete_rewrite(domain, item.name)
        return {"deleted": item.name, "success": True}

    _ = (list_rewrites, get_rewrite, create_rewrite, update_rewrite, delete_rewrite)
