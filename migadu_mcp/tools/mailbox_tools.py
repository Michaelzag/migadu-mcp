"""MCP tools for mailbox operations."""

from typing import Any

from fastmcp import Context, FastMCP

from migadu_mcp.services.service_factory import get_service_factory
from migadu_mcp.utils.decorators import migadu_bulk_tool, migadu_tool, resolve_domain
from migadu_mcp.utils.email_parsing import format_email_address, parse_email_target
from migadu_mcp.utils.schemas import (
    AutoresponderRequest,
    MailboxCreateRequest,
    MailboxDeleteRequest,
    MailboxPasswordResetRequest,
    MailboxUpdateRequest,
)


def register_mailbox_tools(mcp: FastMCP) -> None:
    @migadu_tool(mcp, read_only=True, summarize_response=True)
    async def list_mailboxes(ctx: Context, domain: str | None = None) -> dict[str, Any]:
        """List email mailboxes for a domain."""
        resolved = resolve_domain(domain)
        await ctx.info(f"📋 Listing mailboxes for {resolved}")
        return await get_service_factory().mailbox_service().list_mailboxes(resolved)

    @migadu_tool(mcp, read_only=True)
    async def get_mailbox(target: str, ctx: Context) -> dict[str, Any]:
        """Get full mailbox details by email or local part."""
        domain, local_part = parse_email_target(target)[0]
        await ctx.info(f"📋 Getting mailbox {format_email_address(domain, local_part)}")
        return (
            await get_service_factory()
            .mailbox_service()
            .get_mailbox(domain, local_part)
        )

    @migadu_bulk_tool(mcp, MailboxCreateRequest, entity="mailbox", idempotent=False)
    async def create_mailbox(
        item: MailboxCreateRequest, ctx: Context
    ) -> dict[str, Any]:
        """Create mailbox(es). List of dicts with: target, name, password or password_recovery_email, is_internal (optional), forwarding_to (optional)."""
        domain, local_part = parse_email_target(item.target)[0]
        email = format_email_address(domain, local_part)
        await ctx.info(f"📋 Creating mailbox {email}")
        result = (
            await get_service_factory()
            .mailbox_service()
            .create_mailbox(
                domain=domain,
                local_part=local_part,
                name=item.name,
                password=item.password,
                password_recovery_email=item.password_recovery_email,
                is_internal=item.is_internal,
                forwarding_to=item.forwarding_to,
            )
        )
        return {"mailbox": result, "email_address": email, "success": True}

    @migadu_bulk_tool(mcp, MailboxUpdateRequest, entity="mailbox")
    async def update_mailbox(
        item: MailboxUpdateRequest, ctx: Context
    ) -> dict[str, Any]:
        """Update mailbox settings. List of dicts with: target (required) and any of: name, may_send, may_receive, may_access_imap, may_access_pop3, may_access_managesieve, spam_action, spam_aggressiveness, sender_denylist, sender_allowlist, recipient_denylist."""
        domain, local_part = parse_email_target(item.target)[0]
        email = format_email_address(domain, local_part)
        await ctx.info(f"📋 Updating mailbox {email}")
        result = (
            await get_service_factory()
            .mailbox_service()
            .update_mailbox(
                domain=domain,
                local_part=local_part,
                name=item.name,
                may_send=item.may_send,
                may_receive=item.may_receive,
                may_access_imap=item.may_access_imap,
                may_access_pop3=item.may_access_pop3,
                may_access_managesieve=item.may_access_managesieve,
                spam_action=item.spam_action,
                spam_aggressiveness=item.spam_aggressiveness,
                sender_denylist=item.sender_denylist,
                sender_allowlist=item.sender_allowlist,
                recipient_denylist=item.recipient_denylist,
            )
        )
        return {"mailbox": result, "email_address": email, "success": True}

    @migadu_bulk_tool(mcp, MailboxDeleteRequest, entity="mailbox", destructive=True)
    async def delete_mailbox(
        item: MailboxDeleteRequest, ctx: Context
    ) -> dict[str, Any]:
        """Delete mailbox(es). DESTRUCTIVE. List of dicts with: target."""
        domain, local_part = parse_email_target(item.target)[0]
        email = format_email_address(domain, local_part)
        await ctx.warning(f"🗑️ Deleting mailbox {email}")
        await get_service_factory().mailbox_service().delete_mailbox(domain, local_part)
        return {"deleted": email, "success": True}

    @migadu_bulk_tool(mcp, MailboxPasswordResetRequest, entity="password reset")
    async def reset_mailbox_password(
        item: MailboxPasswordResetRequest, ctx: Context
    ) -> dict[str, Any]:
        """Reset mailbox password(s). List of dicts with: target, new_password."""
        domain, local_part = parse_email_target(item.target)[0]
        email = format_email_address(domain, local_part)
        await ctx.info(f"📋 Resetting password for {email}")
        await (
            get_service_factory()
            .mailbox_service()
            .reset_mailbox_password(domain, local_part, item.new_password)
        )
        return {"reset": email, "success": True}

    @migadu_bulk_tool(mcp, AutoresponderRequest, entity="autoresponder")
    async def set_autoresponder(
        item: AutoresponderRequest, ctx: Context
    ) -> dict[str, Any]:
        """Configure autoresponder(s). List of dicts with: target, active, subject (optional), body (optional), expires_on (optional, YYYY-MM-DD)."""
        domain, local_part = parse_email_target(item.target)[0]
        email = format_email_address(domain, local_part)
        state = "enabling" if item.active else "disabling"
        await ctx.info(f"📋 {state.title()} autoresponder for {email}")
        result = (
            await get_service_factory()
            .mailbox_service()
            .set_autoresponder(
                domain=domain,
                local_part=local_part,
                active=item.active,
                subject=item.subject,
                body=item.body,
                expires_on=item.expires_on.isoformat() if item.expires_on else None,
            )
        )
        return {"autoresponder": result, "email_address": email, "success": True}

    # Silence unused-variable warnings — decorators register with mcp on evaluation.
    _ = (
        list_mailboxes,
        get_mailbox,
        create_mailbox,
        update_mailbox,
        delete_mailbox,
        reset_mailbox_password,
        set_autoresponder,
    )
