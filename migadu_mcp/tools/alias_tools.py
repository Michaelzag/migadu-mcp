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
    bulk_processor,
    ensure_iterable,
    log_bulk_operation_start,
    log_bulk_operation_result,
    validate_required_fields,
    get_field_with_default,
)
from migadu_mcp.utils.email_parsing import format_email_address


def register_alias_tools(mcp: FastMCP):
    """Register alias tools using List[Dict] + iterator pattern"""

    @mcp.tool(
        tags={"alias", "read", "list"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    @with_context_protection(max_tokens=2000)
    async def list_aliases(ctx: Context, domain: str | None = None) -> Dict[str, Any]:
        """List all email aliases for a domain. Returns summary with statistics and samples.

        Args:
            domain: Domain name (e.g., 'mydomain.org'). If not provided, uses MIGADU_DOMAIN.

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
        tags={"alias", "read", "details"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_alias(
        target: str, ctx: Context, domain: str | None = None
    ) -> Dict[str, Any]:
        """Get detailed information about a specific alias.

        Args:
            target: Local part of alias (e.g., 'sales' for sales@domain.com)
            domain: Domain name. If not provided, uses MIGADU_DOMAIN.

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

    @bulk_processor
    async def process_create_alias(
        item: Dict[str, Any], ctx: Context
    ) -> Dict[str, Any]:
        """Process a single alias creation"""
        # Validate required fields
        validate_required_fields(item, ["target", "destinations"], "create_alias")

        # Extract fields with defaults
        target = item["target"]
        destinations = item["destinations"]
        domain = get_field_with_default(item, "domain")
        is_internal = get_field_with_default(item, "is_internal", False)

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
        result = await service.create_alias(domain, target, destinations, is_internal)

        await log_operation_success(ctx, "Created alias", email_address)
        if is_internal:
            await ctx.info("🔒 Configured as internal-only alias")

        return {"alias": result, "email_address": email_address, "success": True}

    @mcp.tool(
        tags={"alias", "create", "forwarding"},
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
        """Create one or more email aliases with forwarding.

        Args:
            aliases: List of alias specifications. Each dict should contain:
                - target: Local part of alias (required)
                - destinations: List of email addresses to forward to (required)
                - domain: Domain name (optional, uses MIGADU_DOMAIN if not provided)
                - is_internal: Internal-only flag (optional, default: false)

        Returns:
            JSON object with created alias(es) information

        Examples:
            Single: [{"target": "sales", "destinations": ["bob@company.com", "alice@company.com"]}]
            Bulk: [
                {"target": "sales", "destinations": ["bob@company.com"]},
                {"target": "support", "destinations": ["help@company.com"], "domain": "other.com"}
            ]
        """
        count = len(list(ensure_iterable(aliases)))
        await log_bulk_operation_start(ctx, "Creating", count, "alias")

        result = await process_create_alias(aliases, ctx)
        await log_bulk_operation_result(ctx, "Alias creation", result, "alias")
        return result

    @bulk_processor
    async def process_update_alias(
        item: Dict[str, Any], ctx: Context
    ) -> Dict[str, Any]:
        """Process a single alias update"""
        # Validate required fields
        validate_required_fields(item, ["target", "destinations"], "update_alias")

        # Extract fields with defaults
        target = item["target"]
        destinations = item["destinations"]
        domain = get_field_with_default(item, "domain")

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
        result = await service.update_alias(domain, target, destinations)

        await log_operation_success(ctx, "Updated alias", email_address)
        return {"alias": result, "email_address": email_address, "success": True}

    @mcp.tool(
        tags={"alias", "update", "forwarding"},
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
        """Update destination addresses for one or more aliases.

        Args:
            updates: List of alias update specifications. Each dict should contain:
                - target: Local part of alias (required)
                - destinations: New list of email addresses to forward to (required)
                - domain: Domain name (optional, uses MIGADU_DOMAIN if not provided)

        Returns:
            JSON object with updated alias configuration(s)

        Examples:
            Single: [{"target": "sales", "destinations": ["newteam@company.com"]}]
            Bulk: [
                {"target": "sales", "destinations": ["bob@company.com", "carol@company.com"]},
                {"target": "support", "destinations": ["help@company.com"]}
            ]
        """
        count = len(list(ensure_iterable(updates)))
        await log_bulk_operation_start(ctx, "Updating", count, "alias")

        result = await process_update_alias(updates, ctx)
        await log_bulk_operation_result(ctx, "Alias update", result, "alias")
        return result

    @bulk_processor
    async def process_delete_alias(
        item: Dict[str, Any], ctx: Context
    ) -> Dict[str, Any]:
        """Process a single alias deletion"""
        # Validate required fields
        validate_required_fields(item, ["target"], "delete_alias")

        # Extract fields with defaults
        target = item["target"]
        domain = get_field_with_default(item, "domain")

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
        tags={"alias", "delete", "destructive"},
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
        """Delete one or more aliases.

        Args:
            targets: List of deletion specifications. Each dict should contain:
                - target: Local part of alias (required)
                - domain: Domain name (optional, uses MIGADU_DOMAIN if not provided)

        Returns:
            JSON object with deletion results

        Examples:
            Single: [{"target": "sales"}]
            Bulk: [{"target": "sales"}, {"target": "support", "domain": "other.com"}]
        """
        count = len(list(ensure_iterable(targets)))
        await log_bulk_operation_start(ctx, "Deleting", count, "alias")
        await ctx.warning("🗑️ DESTRUCTIVE: This operation cannot be undone!")

        result = await process_delete_alias(targets, ctx)
        await log_bulk_operation_result(ctx, "Alias deletion", result, "alias")
        return result
