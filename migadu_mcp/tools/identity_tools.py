"""MCP tools for identity operations."""

from typing import Any

from fastmcp import Context, FastMCP

from migadu_mcp.services.service_factory import get_service_factory
from migadu_mcp.utils.decorators import migadu_bulk_tool, migadu_tool, resolve_domain
from migadu_mcp.utils.email_parsing import format_email_address
from migadu_mcp.utils.schemas import (
    IdentityCreateRequest,
    IdentityDeleteRequest,
    IdentityUpdateRequest,
)


def register_identity_tools(mcp: FastMCP) -> None:
    @migadu_tool(mcp, read_only=True, summarize_response=True)
    async def list_identities(
        mailbox: str, ctx: Context, domain: str | None = None
    ) -> dict[str, Any]:
        """List identities (send-as addresses) for a mailbox."""
        resolved = resolve_domain(domain)
        await ctx.info(f"📋 Listing identities for {mailbox}@{resolved}")
        return (
            await get_service_factory()
            .identity_service()
            .list_identities(resolved, mailbox)
        )

    @migadu_tool(mcp, read_only=True)
    async def get_identity(
        mailbox: str, identity: str, ctx: Context, domain: str | None = None
    ) -> dict[str, Any]:
        """Get full details for a specific identity."""
        resolved = resolve_domain(domain)
        await ctx.info(f"📋 Getting identity {identity}@{resolved} for {mailbox}")
        return (
            await get_service_factory()
            .identity_service()
            .get_identity(resolved, mailbox, identity)
        )

    @migadu_bulk_tool(mcp, IdentityCreateRequest, entity="identity", idempotent=False)
    async def create_identity(
        item: IdentityCreateRequest, ctx: Context
    ) -> dict[str, Any]:
        """Create identit(ies). List of dicts with: target, mailbox, name, password, domain (optional)."""
        domain = item.domain or resolve_domain(None)
        email = format_email_address(domain, item.target)
        await ctx.info(f"📋 Creating identity {email} on {item.mailbox}")
        result = (
            await get_service_factory()
            .identity_service()
            .create_identity(
                domain, item.mailbox, item.target, item.name, item.password
            )
        )
        return {"identity": result, "email_address": email, "success": True}

    @migadu_bulk_tool(mcp, IdentityUpdateRequest, entity="identity")
    async def update_identity(
        item: IdentityUpdateRequest, ctx: Context
    ) -> dict[str, Any]:
        """Update identity settings. List of dicts with: target, mailbox (required) and any of: domain, name, may_send, may_receive, may_access_imap, may_access_pop3, may_access_managesieve, footer_active, footer_plain_body, footer_html_body."""
        domain = item.domain or resolve_domain(None)
        email = format_email_address(domain, item.target)
        await ctx.info(f"📋 Updating identity {email}")
        result = (
            await get_service_factory()
            .identity_service()
            .update_identity(
                domain=domain,
                mailbox=item.mailbox,
                identity=item.target,
                name=item.name,
                may_send=item.may_send,
                may_receive=item.may_receive,
                may_access_imap=item.may_access_imap,
                may_access_pop3=item.may_access_pop3,
                may_access_managesieve=item.may_access_managesieve,
                footer_active=item.footer_active,
                footer_plain_body=item.footer_plain_body,
                footer_html_body=item.footer_html_body,
            )
        )
        return {"identity": result, "email_address": email, "success": True}

    @migadu_bulk_tool(mcp, IdentityDeleteRequest, entity="identity", destructive=True)
    async def delete_identity(
        item: IdentityDeleteRequest, ctx: Context
    ) -> dict[str, Any]:
        """Delete identit(ies). DESTRUCTIVE. List of dicts with: target, mailbox, domain (optional)."""
        domain = item.domain or resolve_domain(None)
        email = format_email_address(domain, item.target)
        await ctx.warning(f"🗑️ Deleting identity {email}")
        await (
            get_service_factory()
            .identity_service()
            .delete_identity(domain, item.mailbox, item.target)
        )
        return {"deleted": email, "success": True}

    _ = (
        list_identities,
        get_identity,
        create_identity,
        update_identity,
        delete_identity,
    )
