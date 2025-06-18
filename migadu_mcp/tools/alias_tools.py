#!/usr/bin/env python3
"""
MCP tools for alias operations using List[Dict] + iterator pattern
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
    AliasCreateRequest,
    AliasUpdateRequest,
    AliasDeleteRequest,
)
from migadu_mcp.utils.email_parsing import format_email_address


def register_alias_tools(mcp: FastMCP):
    """Register alias tools using List[Dict] + iterator pattern"""

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    @with_context_protection(max_tokens=2000)
    async def list_aliases(ctx: Context, domain: str | None = None) -> Dict[str, Any]:
        """List email aliases for domain. Returns summary with statistics and samples.

        Args:
            domain: Domain name. Uses MIGADU_DOMAIN if not provided.

        Returns:
            JSON object with alias summary and statistics
        """
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        await log_operation_start(ctx, "Listing aliases", domain)
        try:
            service = get_service_factory().alias_service()
            result = await service.list_aliases(domain)
            count = len(result.get("aliases", []))
            await log_operation_success(ctx, "Listed aliases", domain, count)
            return result
        except Exception as e:
            await log_operation_error(ctx, "List aliases", domain, str(e))
            raise

    @mcp.tool(
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_alias(
        target: str, ctx: Context, domain: str | None = None
    ) -> Dict[str, Any]:
        """Get detailed alias information.

        Args:
            target: Local part of alias
            domain: Domain name. Uses MIGADU_DOMAIN if not provided.

        Returns:
            JSON object with complete alias configuration
        """
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        try:
            email_address = format_email_address(domain, target)
            await log_operation_start(ctx, "Retrieving alias details", email_address)

            service = get_service_factory().alias_service()
            result = await service.get_alias(domain, target)
            await log_operation_success(ctx, "Retrieved alias details", email_address)
            return result
        except Exception as e:
            await log_operation_error(ctx, "Get alias", f"{target}@{domain}", str(e))
            raise

    @bulk_processor_with_schema(AliasCreateRequest)
    async def process_create_alias(
        validated_item: AliasCreateRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single alias creation with Pydantic validation"""
        # Use validated Pydantic model directly - all validation already done
        target = validated_item.target
        destinations = validated_item.destinations
        domain = validated_item.domain
        is_internal = validated_item.is_internal

        # Get domain if not provided
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        email_address = format_email_address(domain, target)
        await log_operation_start(
            ctx, "Creating alias", f"{email_address} -> {', '.join(destinations)}"
        )

        service = get_service_factory().alias_service()
        # Convert List[EmailStr] to List[str] for service layer
        destinations_str = [str(dest) for dest in destinations]
        result = await service.create_alias(
            domain, target, destinations_str, is_internal
        )

        await log_operation_success(ctx, "Created alias", email_address)
        if is_internal:
            await ctx.info("🔒 Configured as internal-only alias")

        return {"alias": result, "email_address": email_address, "success": True}

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def create_alias(
        aliases: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Create email aliases with forwarding. List of dicts with: target (local part), destinations (email list), domain (optional), is_internal (optional)."""
        count = len(list(ensure_iterable(aliases)))
        await log_bulk_operation_start(ctx, "Creating", count, "alias")

        result = await process_create_alias(aliases, ctx)
        await log_bulk_operation_result(ctx, "Alias creation", result, "alias")
        return result

    @bulk_processor_with_schema(AliasUpdateRequest)
    async def process_update_alias(
        validated_item: AliasUpdateRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single alias update with Pydantic validation"""
        # Use validated Pydantic model directly - all validation already done
        target = validated_item.target
        destinations = validated_item.destinations
        domain = validated_item.domain

        # Get domain if not provided
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        email_address = format_email_address(domain, target)
        await log_operation_start(
            ctx, "Updating alias", f"{email_address} -> {', '.join(destinations)}"
        )

        service = get_service_factory().alias_service()
        # Convert List[EmailStr] to List[str] for service layer
        destinations_str = [str(dest) for dest in destinations]
        result = await service.update_alias(domain, target, destinations_str)

        await log_operation_success(ctx, "Updated alias", email_address)
        return {"alias": result, "email_address": email_address, "success": True}

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def update_alias(
        updates: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Update alias destinations. List of dicts with: target (local part), destinations (email list), domain (optional)."""
        count = len(list(ensure_iterable(updates)))
        await log_bulk_operation_start(ctx, "Updating", count, "alias")

        result = await process_update_alias(updates, ctx)
        await log_bulk_operation_result(ctx, "Alias update", result, "alias")
        return result

    @bulk_processor_with_schema(AliasDeleteRequest)
    async def process_delete_alias(
        validated_item: AliasDeleteRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single alias deletion with Pydantic validation"""
        # Use validated Pydantic model directly - all validation already done
        target = validated_item.target
        domain = validated_item.domain

        # Get domain if not provided
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        email_address = format_email_address(domain, target)
        await ctx.warning(f"🗑️ DESTRUCTIVE: Deleting alias {email_address}")

        service = get_service_factory().alias_service()
        await service.delete_alias(domain, target)

        await log_operation_success(ctx, "Deleted alias", email_address)
        return {"deleted": email_address, "success": True}

    @mcp.tool(
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def delete_alias(
        targets: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Delete aliases. DESTRUCTIVE: Cannot be undone. List of dicts with: target (local part), domain (optional)."""
        count = len(list(ensure_iterable(targets)))
        await log_bulk_operation_start(ctx, "Deleting", count, "alias")
        await ctx.warning("🗑️ DESTRUCTIVE: This operation cannot be undone!")

        result = await process_delete_alias(targets, ctx)
        await log_bulk_operation_result(ctx, "Alias deletion", result, "alias")
        return result
