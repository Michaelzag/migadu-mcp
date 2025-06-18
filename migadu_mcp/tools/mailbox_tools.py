#!/usr/bin/env python3
"""
MCP tools for mailbox operations using List[Dict] + iterator pattern
"""

from typing import Dict, Any, List
from fastmcp import FastMCP, Context
from migadu_mcp.services.service_factory import get_service_factory
from migadu_mcp.utils.tool_helpers import (
    with_context_protection,
    log_operation_start,
    log_operation_success,
    log_operation_error,
)
from migadu_mcp.utils.bulk_processing import (
    bulk_processor_with_schema,
    ensure_iterable,
    log_bulk_operation_start,
    log_bulk_operation_result,
)
from migadu_mcp.utils.schemas import (
    MailboxCreateRequest,
    MailboxUpdateRequest,
    MailboxDeleteRequest,
    MailboxPasswordResetRequest,
    AutoresponderRequest,
)
from migadu_mcp.utils.email_parsing import parse_email_target, format_email_address


def register_mailbox_tools(mcp: FastMCP):
    """Register mailbox tools using List[Dict] + iterator pattern"""

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    @with_context_protection(max_tokens=2000)
    async def list_mailboxes(ctx: Context, domain: str | None = None) -> Dict[str, Any]:
        """List email mailboxes for domain. Returns summary with statistics and samples.

        Args:
            domain: Domain name. Uses MIGADU_DOMAIN if not provided.

        Returns:
            JSON object with mailbox summary and statistics
        """
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        await log_operation_start(ctx, "Listing mailboxes", domain)
        try:
            service = get_service_factory().mailbox_service()
            result = await service.list_mailboxes(domain)
            count = len(result.get("mailboxes", []))
            await log_operation_success(ctx, "Listed mailboxes", domain, count)
            return result
        except Exception as e:
            await log_operation_error(ctx, "List mailboxes", domain, str(e))
            raise

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_mailbox(target: str, ctx: Context) -> Dict[str, Any]:
        """Get detailed mailbox information with smart domain resolution.

        Args:
            target: Email address or local part if MIGADU_DOMAIN set

        Returns:
            JSON object with complete mailbox configuration
        """
        try:
            parsed = parse_email_target(target)
            domain, local_part = parsed[0]
            email_address = format_email_address(domain, local_part)

            await log_operation_start(ctx, "Retrieving mailbox details", email_address)
            service = get_service_factory().mailbox_service()
            result = await service.get_mailbox(domain, local_part)
            await log_operation_success(ctx, "Retrieved mailbox details", email_address)
            return result
        except Exception as e:
            await log_operation_error(ctx, "Get mailbox", str(target), str(e))
            raise

    @bulk_processor_with_schema(MailboxCreateRequest)
    async def process_create_mailbox(
        validated_item: MailboxCreateRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single mailbox creation with Pydantic validation"""
        # Use validated Pydantic model directly - all validation already done
        target = validated_item.target
        name = validated_item.name
        password = validated_item.password
        password_recovery_email = validated_item.password_recovery_email
        is_internal = validated_item.is_internal
        forwarding_to = validated_item.forwarding_to

        # Parse target
        parsed = parse_email_target(target)
        domain, local_part = parsed[0]
        email_address = format_email_address(domain, local_part)

        await log_operation_start(ctx, "Creating mailbox", f"{email_address} ({name})")

        service = get_service_factory().mailbox_service()
        result = await service.create_mailbox(
            domain,
            local_part,
            name,
            password,
            password_recovery_email,
            is_internal,
            forwarding_to,
        )

        await log_operation_success(ctx, "Created mailbox", email_address)
        if forwarding_to:
            await ctx.info(f"🔄 Configured forwarding to: {forwarding_to}")
        if is_internal:
            await ctx.info("🔒 Configured as internal-only mailbox")

        return {"mailbox": result, "email_address": email_address, "success": True}

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def create_mailbox(
        mailboxes: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Create email mailboxes. List of dicts with: target (email/local), name (display), password (optional), recovery_email (optional), is_internal (optional), forwarding_to (optional)."""
        count = len(list(ensure_iterable(mailboxes)))
        await log_bulk_operation_start(ctx, "Creating", count, "mailbox")

        result = await process_create_mailbox(mailboxes, ctx)
        await log_bulk_operation_result(ctx, "Mailbox creation", result, "mailbox")
        return result

    @bulk_processor_with_schema(MailboxUpdateRequest)
    async def process_update_mailbox(
        validated_item: MailboxUpdateRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single mailbox update with Pydantic validation"""
        # Use validated Pydantic model directly - all validation already done
        target = validated_item.target
        name = validated_item.name
        may_send = validated_item.may_send
        may_receive = validated_item.may_receive
        may_access_imap = validated_item.may_access_imap
        may_access_pop3 = validated_item.may_access_pop3
        spam_action = validated_item.spam_action
        spam_aggressiveness = validated_item.spam_aggressiveness

        # Parse target
        parsed = parse_email_target(target)
        domain, local_part = parsed[0]
        email_address = format_email_address(domain, local_part)

        await log_operation_start(ctx, "Updating mailbox", email_address)

        service = get_service_factory().mailbox_service()
        result = await service.update_mailbox(
            domain,
            local_part,
            name,
            may_send,
            may_receive,
            may_access_imap,
            may_access_pop3,
            spam_action,
            spam_aggressiveness,
        )

        await log_operation_success(ctx, "Updated mailbox", email_address)
        return {"mailbox": result, "email_address": email_address, "success": True}

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def update_mailbox(
        updates: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Update mailbox settings. List of dicts with: target (required), name (optional), may_send (optional), may_receive (optional), may_access_imap (optional), may_access_pop3 (optional), spam_action (optional), spam_aggressiveness (optional)."""
        count = len(list(ensure_iterable(updates)))
        await log_bulk_operation_start(ctx, "Updating", count, "mailbox")

        result = await process_update_mailbox(updates, ctx)
        await log_bulk_operation_result(ctx, "Mailbox update", result, "mailbox")
        return result

    @bulk_processor_with_schema(MailboxDeleteRequest)
    async def process_delete_mailbox(
        validated_item: MailboxDeleteRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single mailbox deletion with Pydantic validation"""
        # Use validated Pydantic model directly - all validation already done
        target = validated_item.target

        # Parse target
        parsed = parse_email_target(target)
        domain, local_part = parsed[0]
        email_address = format_email_address(domain, local_part)

        await ctx.warning(f"🗑️ DESTRUCTIVE: Deleting mailbox {email_address}")

        service = get_service_factory().mailbox_service()
        await service.delete_mailbox(domain, local_part)

        await log_operation_success(ctx, "Deleted mailbox", email_address)
        return {"deleted": email_address, "success": True}

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def delete_mailbox(
        targets: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Delete mailboxes. DESTRUCTIVE: Cannot be undone. List of dicts with: target (email/local)."""
        count = len(list(ensure_iterable(targets)))
        await log_bulk_operation_start(ctx, "Deleting", count, "mailbox")
        await ctx.warning("🗑️ DESTRUCTIVE: This operation cannot be undone!")

        result = await process_delete_mailbox(targets, ctx)
        await log_bulk_operation_result(ctx, "Mailbox deletion", result, "mailbox")
        return result

    @bulk_processor_with_schema(MailboxPasswordResetRequest)
    async def process_reset_password(
        validated_item: MailboxPasswordResetRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single password reset with Pydantic validation"""
        # Use validated Pydantic model directly - all validation already done
        target = validated_item.target
        new_password = validated_item.new_password

        # Parse target
        parsed = parse_email_target(target)
        domain, local_part = parsed[0]
        email_address = format_email_address(domain, local_part)

        await log_operation_start(ctx, "Resetting password", email_address)

        service = get_service_factory().mailbox_service()
        await service.reset_mailbox_password(domain, local_part, new_password)

        await log_operation_success(ctx, "Reset password", email_address)
        return {"reset": email_address, "success": True}

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def reset_mailbox_password(
        resets: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Reset mailbox passwords. List of dicts with: target (email/local), new_password (required)."""
        count = len(list(ensure_iterable(resets)))
        await log_bulk_operation_start(ctx, "Resetting passwords for", count, "mailbox")

        result = await process_reset_password(resets, ctx)
        await log_bulk_operation_result(ctx, "Password reset", result, "mailbox")
        return result

    @bulk_processor_with_schema(AutoresponderRequest)
    async def process_set_autoresponder(
        validated_item: AutoresponderRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single autoresponder configuration with Pydantic validation"""
        # Use validated Pydantic model directly - all validation already done
        target = validated_item.target
        active = validated_item.active
        subject = validated_item.subject
        body = validated_item.body
        expires_on = (
            validated_item.expires_on.isoformat() if validated_item.expires_on else None
        )

        # Parse target
        parsed = parse_email_target(target)
        domain, local_part = parsed[0]
        email_address = format_email_address(domain, local_part)

        status = "Enabling" if active else "Disabling"
        await log_operation_start(ctx, f"{status} autoresponder", email_address)

        service = get_service_factory().mailbox_service()
        result = await service.set_autoresponder(
            domain, local_part, active, subject, body, expires_on
        )

        await log_operation_success(
            ctx, f"{status.lower()} autoresponder", email_address
        )
        return {
            "autoresponder": result,
            "email_address": email_address,
            "success": True,
        }

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def set_autoresponder(
        autoresponders: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Configure mailbox autoresponders. List of dicts with: target (email/local), active (required), subject (optional), body (optional), expires_on (optional)."""
        count = len(list(ensure_iterable(autoresponders)))
        await log_bulk_operation_start(
            ctx, "Configuring autoresponders for", count, "mailbox"
        )

        result = await process_set_autoresponder(autoresponders, ctx)
        await log_bulk_operation_result(
            ctx, "Autoresponder configuration", result, "mailbox"
        )
        return result
