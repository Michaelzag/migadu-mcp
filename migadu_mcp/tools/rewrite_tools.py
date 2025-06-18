#!/usr/bin/env python3
"""
MCP tools for rewrite operations using List[Dict] + iterator pattern
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
    RewriteCreateRequest,
    RewriteUpdateRequest,
    RewriteDeleteRequest,
)


def register_rewrite_tools(mcp: FastMCP):
    """Register rewrite tools using List[Dict] + iterator pattern"""

    @mcp.tool(
        tags={"rewrite", "read", "list"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    @with_context_protection(max_tokens=2000)
    async def list_rewrites(ctx: Context, domain: str | None = None) -> Dict[str, Any]:
        """List all pattern-based rewrite rules for a domain. Returns summary with statistics and samples.

        Args:
            domain: Domain name (e.g., 'mydomain.org'). If not provided, uses MIGADU_DOMAIN.

        Returns:
            JSON object with rewrite rules summary and statistics
        """
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        await log_operation_start(ctx, "Listing rewrite rules", domain)
        try:
            service = get_service_factory().rewrite_service()
            result = await service.list_rewrites(domain)
            count = len(result.get("rewrites", []))
            await log_operation_success(ctx, "Listed rewrite rules", domain, count)
            return result
        except Exception as e:
            await log_operation_error(ctx, "List rewrites", domain, str(e))
            raise

    @mcp.tool(
        tags={"rewrite", "read", "details"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_rewrite(
        name: str, ctx: Context, domain: str | None = None
    ) -> Dict[str, Any]:
        """Get detailed information about a specific rewrite rule.

        Args:
            name: Unique identifier/slug of the rewrite rule
            domain: Domain name. If not provided, uses MIGADU_DOMAIN.

        Returns:
            JSON object with complete rewrite rule configuration
        """
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        try:
            await log_operation_start(
                ctx, "Retrieving rewrite rule details", f"{name}@{domain}"
            )

            service = get_service_factory().rewrite_service()
            result = await service.get_rewrite(domain, name)
            await log_operation_success(
                ctx, "Retrieved rewrite rule details", f"{name}@{domain}"
            )
            return result
        except Exception as e:
            await log_operation_error(ctx, "Get rewrite", f"{name}@{domain}", str(e))
            raise

    @bulk_processor_with_schema(RewriteCreateRequest)
    async def process_create_rewrite(
        validated_item: RewriteCreateRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single rewrite rule creation with Pydantic validation"""
        # Use validated Pydantic model directly - all validation already done
        name = validated_item.name
        local_part_rule = validated_item.local_part_rule
        destinations = validated_item.destinations
        domain = validated_item.domain

        # Get domain if not provided
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        await log_operation_start(
            ctx,
            "Creating rewrite rule",
            f"{name}: {local_part_rule} -> {', '.join(destinations)}",
        )

        service = get_service_factory().rewrite_service()
        # Convert List[EmailStr] to List[str] for service layer
        destinations_str = [str(dest) for dest in destinations]
        result = await service.create_rewrite(
            domain, name, local_part_rule, destinations_str
        )

        await log_operation_success(ctx, "Created rewrite rule", f"{name}@{domain}")
        return {"rewrite": result, "name": name, "domain": domain, "success": True}

    @mcp.tool(
        tags={"rewrite", "create", "pattern"},
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def create_rewrite(
        rewrites: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Create one or more pattern-based rewrite rules for dynamic email forwarding.

        Args:
            rewrites: List of rewrite specifications. Each dict should contain:
                - name: Unique identifier/slug for the rule (required)
                - local_part_rule: Pattern to match (e.g., 'demo-*', 'support-*') (required)
                - destinations: List of email addresses to forward to (required)
                - domain: Domain name (optional, uses MIGADU_DOMAIN if not provided)

        Returns:
            JSON object with created rewrite rule(s) information

        Examples:
            Single: [{"name": "demo-catchall", "local_part_rule": "demo-*", "destinations": ["admin@company.com"]}]
            Bulk: [
                {"name": "demo-catchall", "local_part_rule": "demo-*", "destinations": ["admin@company.com"]},
                {"name": "support-routing", "local_part_rule": "support-*", "destinations": ["help@company.com"]}
            ]
        """
        count = len(list(ensure_iterable(rewrites)))
        await log_bulk_operation_start(ctx, "Creating", count, "rewrite rule")

        result = await process_create_rewrite(rewrites, ctx)
        await log_bulk_operation_result(
            ctx, "Rewrite rule creation", result, "rewrite rule"
        )
        return result

    @bulk_processor_with_schema(RewriteUpdateRequest)
    async def process_update_rewrite(
        validated_item: RewriteUpdateRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single rewrite rule update with Pydantic validation"""
        # Use validated Pydantic model directly - all validation already done
        name = validated_item.name
        domain = validated_item.domain
        new_name = validated_item.new_name
        local_part_rule = validated_item.local_part_rule
        destinations = validated_item.destinations

        # Get domain if not provided
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        await log_operation_start(ctx, "Updating rewrite rule", f"{name}@{domain}")

        service = get_service_factory().rewrite_service()
        # Convert Optional[List[EmailStr]] to Optional[List[str]] for service layer
        destinations_str = None
        if destinations is not None:
            destinations_str = [str(dest) for dest in destinations]
        
        result = await service.update_rewrite(
            domain, name, new_name, local_part_rule, destinations_str
        )

        await log_operation_success(ctx, "Updated rewrite rule", f"{name}@{domain}")
        return {"rewrite": result, "name": name, "domain": domain, "success": True}

    @mcp.tool(
        tags={"rewrite", "update", "pattern"},
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def update_rewrite(
        updates: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Update configuration for one or more rewrite rules.

        Args:
            updates: List of rewrite update specifications. Each dict should contain:
                - name: Current identifier/slug of the rule (required)
                - domain: Domain name (optional, uses MIGADU_DOMAIN if not provided)
                - new_name: New identifier/slug (optional)
                - local_part_rule: New pattern to match (optional)
                - destinations: New list of destinations (optional)

        Returns:
            JSON object with updated rewrite rule configuration(s)

        Examples:
            Single: [{"name": "demo-catchall", "destinations": ["newadmin@company.com"]}]
            Bulk: [
                {"name": "demo-catchall", "local_part_rule": "test-*"},
                {"name": "support-routing", "new_name": "help-routing"}
            ]
        """
        count = len(list(ensure_iterable(updates)))
        await log_bulk_operation_start(ctx, "Updating", count, "rewrite rule")

        result = await process_update_rewrite(updates, ctx)
        await log_bulk_operation_result(
            ctx, "Rewrite rule update", result, "rewrite rule"
        )
        return result

    @bulk_processor_with_schema(RewriteDeleteRequest)
    async def process_delete_rewrite(
        validated_item: RewriteDeleteRequest, ctx: Context
    ) -> Dict[str, Any]:
        """Process a single rewrite rule deletion with Pydantic validation"""
        # Use validated Pydantic model directly - all validation already done
        name = validated_item.name
        domain = validated_item.domain

        # Get domain if not provided
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        await ctx.warning(f"🗑️ DESTRUCTIVE: Deleting rewrite rule {name}@{domain}")

        service = get_service_factory().rewrite_service()
        await service.delete_rewrite(domain, name)

        await log_operation_success(ctx, "Deleted rewrite rule", f"{name}@{domain}")
        return {"deleted": f"{name}@{domain}", "success": True}

    @mcp.tool(
        tags={"rewrite", "delete", "destructive"},
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def delete_rewrite(
        targets: List[Dict[str, Any]], ctx: Context
    ) -> Dict[str, Any]:
        """Delete one or more rewrite rules.

        Args:
            targets: List of deletion specifications. Each dict should contain:
                - name: Identifier/slug of the rule to delete (required)
                - domain: Domain name (optional, uses MIGADU_DOMAIN if not provided)

        Returns:
            JSON object with deletion results

        Examples:
            Single: [{"name": "demo-catchall"}]
            Bulk: [{"name": "demo-catchall"}, {"name": "support-routing", "domain": "other.com"}]
        """
        count = len(list(ensure_iterable(targets)))
        await log_bulk_operation_start(ctx, "Deleting", count, "rewrite rule")
        await ctx.warning("🗑️ DESTRUCTIVE: This operation cannot be undone!")

        result = await process_delete_rewrite(targets, ctx)
        await log_bulk_operation_result(
            ctx, "Rewrite rule deletion", result, "rewrite rule"
        )
        return result
