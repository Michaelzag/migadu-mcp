#!/usr/bin/env python3
"""
MCP tools for identity operations using List[Dict] + iterator pattern
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
    IdentityCreateRequest,
    IdentityUpdateRequest,
    IdentityDeleteRequest,
)
from migadu_mcp.utils.email_parsing import format_email_address


def register_identity_tools(mcp: FastMCP):
    """Register identity tools using List[Dict] + iterator pattern"""

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    @with_context_protection(max_tokens=2000)
    async def list_identities(
        mailbox: str, ctx: Context, domain: str | None = None
    ) -> Dict[str, Any]:
        """List email identities for mailbox. Returns summary with statistics and samples."""
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        await log_operation_start(ctx, "Listing identities", f"{mailbox}@{domain}")
        try:
            service = get_service_factory().identity_service()
            result = await service.list_identities(domain, mailbox)
            count = len(result.get("identities", []))
            await log_operation_success(
                ctx, "Listed identities", f"{mailbox}@{domain}", count
            )
            return result
        except Exception as e:
            await log_operation_error(
                ctx, "List identities", f"{mailbox}@{domain}", str(e)
            )
            raise

    @bulk_processor_with_schema(IdentityCreateRequest)
    async def process_create_identity(
        validated_item: IdentityCreateRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single identity creation"""
        # Get domain if not provided
        domain = validated_item.domain
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        email_address = format_email_address(domain, validated_item.target)
        await log_operation_start(
            ctx, "Creating identity", f"{email_address} for {validated_item.mailbox}"
        )

        service = get_service_factory().identity_service()
        result = await service.create_identity(
            domain,
            validated_item.mailbox,
            validated_item.target,
            validated_item.name,
            validated_item.password,
        )

        await log_operation_success(ctx, "Created identity", email_address)
        return {"identity": result, "email_address": email_address, "success": True}

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def create_identity(
        identities: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Create email identities. List of dicts with: target, mailbox, name, password (required), domain (optional)."""
        count = len(list(ensure_iterable(identities)))
        await log_bulk_operation_start(ctx, "Creating", count, "identity")

        result = await process_create_identity(identities, ctx)
        await log_bulk_operation_result(ctx, "Identity creation", result, "identity")
        return result

    @bulk_processor_with_schema(IdentityUpdateRequest)
    async def process_update_identity(
        validated_item: IdentityUpdateRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single identity update"""
        # Get domain if not provided
        domain = validated_item.domain
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        email_address = format_email_address(domain, validated_item.target)
        await log_operation_start(ctx, "Updating identity", email_address)

        service = get_service_factory().identity_service()
        result = await service.update_identity(
            domain,
            validated_item.mailbox,
            validated_item.target,
            validated_item.name,
            validated_item.may_send,
            validated_item.may_receive,
        )

        await log_operation_success(ctx, "Updated identity", email_address)
        return {"identity": result, "email_address": email_address, "success": True}

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def update_identity(
        updates: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Update identity settings. List of dicts with: target, mailbox (required), domain, name, may_send, may_receive (optional)."""
        count = len(list(ensure_iterable(updates)))
        await log_bulk_operation_start(ctx, "Updating", count, "identity")

        result = await process_update_identity(updates, ctx)
        await log_bulk_operation_result(ctx, "Identity update", result, "identity")
        return result

    @bulk_processor_with_schema(IdentityDeleteRequest)
    async def process_delete_identity(
        validated_item: IdentityDeleteRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single identity deletion"""
        # Get domain if not provided
        domain = validated_item.domain
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        email_address = format_email_address(domain, validated_item.target)
        await ctx.warning(f"🗑️ DESTRUCTIVE: Deleting identity {email_address}")

        service = get_service_factory().identity_service()
        await service.delete_identity(
            domain, validated_item.mailbox, validated_item.target
        )

        await log_operation_success(ctx, "Deleted identity", email_address)
        return {"deleted": email_address, "success": True}

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def delete_identity(
        targets: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Delete identities. DESTRUCTIVE: Cannot be undone. List of dicts with: target, mailbox (required), domain (optional)."""
        count = len(list(ensure_iterable(targets)))
        await log_bulk_operation_start(ctx, "Deleting", count, "identity")
        await ctx.warning("🗑️ DESTRUCTIVE: This operation cannot be undone!")

        result = await process_delete_identity(targets, ctx)
        await log_bulk_operation_result(ctx, "Identity deletion", result, "identity")
        return result
