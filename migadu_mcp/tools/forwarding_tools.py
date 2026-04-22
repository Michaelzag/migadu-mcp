"""MCP tools for forwarding operations."""

from typing import Any

from fastmcp import Context, FastMCP

from migadu_mcp.services.service_factory import get_service_factory
from migadu_mcp.utils.decorators import migadu_bulk_tool, migadu_tool, resolve_domain
from migadu_mcp.utils.schemas import (
    ForwardingCreateRequest,
    ForwardingDeleteRequest,
    ForwardingUpdateRequest,
)


def register_forwarding_tools(mcp: FastMCP) -> None:
    @migadu_tool(mcp, read_only=True, summarize_response=True)
    async def list_forwardings(
        mailbox: str, ctx: Context, domain: str | None = None
    ) -> dict[str, Any]:
        """List external forwardings configured on a mailbox."""
        resolved = resolve_domain(domain)
        await ctx.info(f"📋 Listing forwardings for {mailbox}@{resolved}")
        return (
            await get_service_factory()
            .forwarding_service()
            .list_forwardings(resolved, mailbox)
        )

    @migadu_tool(mcp, read_only=True)
    async def get_forwarding(
        mailbox: str, address: str, ctx: Context, domain: str | None = None
    ) -> dict[str, Any]:
        """Get details for a specific forwarding (confirmation status, expiry, active state)."""
        resolved = resolve_domain(domain)
        await ctx.info(f"📋 Getting forwarding {address} on {mailbox}@{resolved}")
        return (
            await get_service_factory()
            .forwarding_service()
            .get_forwarding(resolved, mailbox, address)
        )

    @migadu_bulk_tool(
        mcp, ForwardingCreateRequest, entity="forwarding", idempotent=False
    )
    async def create_forwarding(
        item: ForwardingCreateRequest, ctx: Context
    ) -> dict[str, Any]:
        """Create forwarding(s). Forwardings require external-user confirmation. List of dicts with: mailbox, address, domain (optional), expires_on (optional, YYYY-MM-DD), remove_upon_expiry (optional)."""
        domain = item.domain or resolve_domain(None)
        await ctx.info(
            f"📋 Creating forwarding {item.address} on {item.mailbox}@{domain}"
        )
        result = (
            await get_service_factory()
            .forwarding_service()
            .create_forwarding(
                domain=domain,
                mailbox=item.mailbox,
                address=str(item.address),
                expires_on=item.expires_on.isoformat() if item.expires_on else None,
                remove_upon_expiry=item.remove_upon_expiry,
            )
        )
        return {"forwarding": result, "success": True}

    @migadu_bulk_tool(mcp, ForwardingUpdateRequest, entity="forwarding")
    async def update_forwarding(
        item: ForwardingUpdateRequest, ctx: Context
    ) -> dict[str, Any]:
        """Update forwarding(s). List of dicts with: mailbox, address (required), and any of: is_active, expires_on, remove_upon_expiry, domain."""
        domain = item.domain or resolve_domain(None)
        await ctx.info(
            f"📋 Updating forwarding {item.address} on {item.mailbox}@{domain}"
        )
        result = (
            await get_service_factory()
            .forwarding_service()
            .update_forwarding(
                domain=domain,
                mailbox=item.mailbox,
                address=str(item.address),
                is_active=item.is_active,
                expires_on=item.expires_on.isoformat() if item.expires_on else None,
                remove_upon_expiry=item.remove_upon_expiry,
            )
        )
        return {"forwarding": result, "success": True}

    @migadu_bulk_tool(
        mcp, ForwardingDeleteRequest, entity="forwarding", destructive=True
    )
    async def delete_forwarding(
        item: ForwardingDeleteRequest, ctx: Context
    ) -> dict[str, Any]:
        """Delete forwarding(s). DESTRUCTIVE. List of dicts with: mailbox, address, domain (optional)."""
        domain = item.domain or resolve_domain(None)
        await ctx.warning(f"🗑️ Deleting forwarding {item.address} on {item.mailbox}")
        await (
            get_service_factory()
            .forwarding_service()
            .delete_forwarding(domain, item.mailbox, str(item.address))
        )
        return {"deleted": str(item.address), "success": True}

    _ = (
        list_forwardings,
        get_forwarding,
        create_forwarding,
        update_forwarding,
        delete_forwarding,
    )
