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
    bulk_processor,
    ensure_iterable,
    log_bulk_operation_start,
    log_bulk_operation_result,
    validate_required_fields,
    get_field_with_default,
)
from migadu_mcp.utils.email_parsing import format_email_address


def register_identity_tools(mcp: FastMCP):
    """Register identity tools using List[Dict] + iterator pattern"""

    @mcp.tool(
        tags={"identity", "read", "list"},
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
        """List all email identities for a mailbox. Returns summary with statistics and samples.

        Args:
            mailbox: Username of the mailbox that owns identities
            domain: Domain name. If not provided, uses MIGADU_DOMAIN.

        Returns:
            JSON object with identity summary and statistics
        """
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

    @bulk_processor
    async def process_create_identity(
        item: Dict[str, Any], ctx: Context
    ) -> Dict[str, Any]:
        """Process a single identity creation"""
        # Validate required fields
        validate_required_fields(
            item, ["target", "mailbox", "name", "password"], "create_identity"
        )

        # Extract fields with defaults
        target = item["target"]
        mailbox = item["mailbox"]
        name = item["name"]
        password = item["password"]
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
            ctx, "Creating identity", f"{email_address} for {mailbox}"
        )

        service = get_service_factory().identity_service()
        result = await service.create_identity(domain, mailbox, target, name, password)

        await log_operation_success(ctx, "Created identity", email_address)
        return {"identity": result, "email_address": email_address, "success": True}

    @mcp.tool(
        tags={"identity", "create", "send-as"},
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
        """Create one or more email identities for mailboxes.

        Args:
            identities: List of identity specifications. Each dict should contain:
                - target: Local part of identity address (required)
                - mailbox: Username of mailbox that owns this identity (required)
                - name: Display name for identity (required)
                - password: Password for SMTP authentication (required)
                - domain: Domain name (optional, uses MIGADU_DOMAIN if not provided)

        Returns:
            JSON object with created identity(ies) information

        Examples:
            Single: [{"target": "support", "mailbox": "john", "name": "Support Team", "password": "secret123"}]
            Bulk: [
                {"target": "support", "mailbox": "john", "name": "Support", "password": "secret123"},
                {"target": "sales", "mailbox": "jane", "name": "Sales Team", "password": "secret456"}
            ]
        """
        count = len(list(ensure_iterable(identities)))
        await log_bulk_operation_start(ctx, "Creating", count, "identity")

        result = await process_create_identity(identities, ctx)
        await log_bulk_operation_result(ctx, "Identity creation", result, "identity")
        return result

    @bulk_processor
    async def process_update_identity(
        item: Dict[str, Any], ctx: Context
    ) -> Dict[str, Any]:
        """Process a single identity update"""
        # Validate required fields
        validate_required_fields(item, ["target", "mailbox"], "update_identity")

        # Extract fields with defaults
        target = item["target"]
        mailbox = item["mailbox"]
        domain = get_field_with_default(item, "domain")
        name = get_field_with_default(item, "name")
        may_send = get_field_with_default(item, "may_send")
        may_receive = get_field_with_default(item, "may_receive")

        # Get domain if not provided
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        email_address = format_email_address(domain, target)
        await log_operation_start(ctx, "Updating identity", email_address)

        service = get_service_factory().identity_service()
        result = await service.update_identity(
            domain, mailbox, target, name, may_send, may_receive
        )

        await log_operation_success(ctx, "Updated identity", email_address)
        return {"identity": result, "email_address": email_address, "success": True}

    @mcp.tool(
        tags={"identity", "update", "configuration"},
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
        """Update settings for one or more identities.

        Args:
            updates: List of identity update specifications. Each dict should contain:
                - target: Local part of identity address (required)
                - mailbox: Username of mailbox that owns this identity (required)
                - domain: Domain name (optional, uses MIGADU_DOMAIN if not provided)
                - name: Update display name (optional)
                - may_send: Allow/deny sending from identity (optional)
                - may_receive: Allow/deny receiving to identity (optional)

        Returns:
            JSON object with updated identity configuration(s)

        Examples:
            Single: [{"target": "support", "mailbox": "john", "may_send": false}]
            Bulk: [
                {"target": "support", "mailbox": "john", "name": "Support Team Updated"},
                {"target": "sales", "mailbox": "jane", "may_receive": false}
            ]
        """
        count = len(list(ensure_iterable(updates)))
        await log_bulk_operation_start(ctx, "Updating", count, "identity")

        result = await process_update_identity(updates, ctx)
        await log_bulk_operation_result(ctx, "Identity update", result, "identity")
        return result

    @bulk_processor
    async def process_delete_identity(
        item: Dict[str, Any], ctx: Context
    ) -> Dict[str, Any]:
        """Process a single identity deletion"""
        # Validate required fields
        validate_required_fields(item, ["target", "mailbox"], "delete_identity")

        # Extract fields with defaults
        target = item["target"]
        mailbox = item["mailbox"]
        domain = get_field_with_default(item, "domain")

        # Get domain if not provided
        if domain is None:
            from migadu_mcp.config import get_config

            config = get_config()
            domain = config.get_default_domain()
            if not domain:
                raise ValueError("No domain provided and MIGADU_DOMAIN not configured")

        email_address = format_email_address(domain, target)
        await ctx.warning(f"🗑️ DESTRUCTIVE: Deleting identity {email_address}")

        service = get_service_factory().identity_service()
        await service.delete_identity(domain, mailbox, target)

        await log_operation_success(ctx, "Deleted identity", email_address)
        return {"deleted": email_address, "success": True}

    @mcp.tool(
        tags={"identity", "delete", "destructive"},
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
        """Delete one or more identities.

        Args:
            targets: List of deletion specifications. Each dict should contain:
                - target: Local part of identity address (required)
                - mailbox: Username of mailbox that owns this identity (required)
                - domain: Domain name (optional, uses MIGADU_DOMAIN if not provided)

        Returns:
            JSON object with deletion results

        Examples:
            Single: [{"target": "support", "mailbox": "john"}]
            Bulk: [
                {"target": "support", "mailbox": "john"},
                {"target": "sales", "mailbox": "jane", "domain": "other.com"}
            ]
        """
        count = len(list(ensure_iterable(targets)))
        await log_bulk_operation_start(ctx, "Deleting", count, "identity")
        await ctx.warning("🗑️ DESTRUCTIVE: This operation cannot be undone!")

        result = await process_delete_identity(targets, ctx)
        await log_bulk_operation_result(ctx, "Identity deletion", result, "identity")
        return result
