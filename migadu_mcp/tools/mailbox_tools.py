#!/usr/bin/env python3
"""
MCP tools for mailbox operations
"""

from typing import Dict, Any, Optional, List
from fastmcp import FastMCP, Context
from migadu_mcp.config import get_config
from migadu_mcp.services.service_factory import get_service_factory


def register_mailbox_tools(mcp: FastMCP):
    """Register mailbox tools with FastMCP instance"""

    @mcp.tool(
        tags={"mailbox", "read", "audit"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def list_mailboxes(domain: str, ctx: Context) -> Dict[str, Any]:
        """Retrieve all email mailboxes configured for a domain. Mailboxes are full email accounts with storage,
        password authentication, and IMAP/POP3 access capabilities. Each mailbox shows configuration details
        including permissions (send/receive/IMAP/POP3), spam settings, autoresponder status, and security options.
        Use this to audit domain email accounts, review permissions, and manage organizational email infrastructure.

        Args:
            domain: The domain name to list mailboxes for (e.g., 'mydomain.org')

        Returns:
            JSON object containing array of all mailboxes with full configuration details
        """
        await ctx.info(f"📋 Listing all mailboxes for domain: {domain}")
        try:
            factory = get_service_factory()
            service = factory.mailbox_service()
            result = await service.list_mailboxes(domain)
            count = len(result.get("mailboxes", []))
            await ctx.info(f"✅ Found {count} mailboxes for {domain}")
            return result
        except Exception as e:
            await ctx.error(f"❌ Failed to list mailboxes for {domain}: {str(e)}")
            raise

    @mcp.tool(
        tags={"mailbox", "read", "convenience"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def list_my_mailboxes(ctx: Context) -> Dict[str, Any]:
        """Retrieve all email mailboxes for your default configured domain. Mailboxes are full email accounts
        with storage, password authentication, and IMAP/POP3 access. This convenience function uses your
        MIGADU_DOMAIN environment variable to automatically target the correct domain. Returns detailed
        configuration for each mailbox including permissions, spam settings, and security options.

        Returns:
            JSON object containing array of all mailboxes for the default domain
        """
        config = get_config()
        domain = config.get_default_domain()
        await ctx.info(f"📋 Listing mailboxes for default domain: {domain}")
        try:
            factory = get_service_factory()
            service = factory.mailbox_service()
            result = await service.list_mailboxes(domain)
            count = len(result.get("mailboxes", []))
            await ctx.info(f"✅ Found {count} mailboxes for default domain {domain}")
            return result
        except Exception as e:
            await ctx.error(
                f"❌ Failed to list mailboxes for default domain {domain}: {str(e)}"
            )
            raise

    @mcp.tool(
        tags={"mailbox", "read", "details"},
        annotations={
            "readOnlyHint": True,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def get_mailbox(ctx: Context, domain: str, local_part: str) -> Dict[str, Any]:
        """Retrieve detailed information about a specific mailbox. Shows complete configuration including
        permissions (send/receive/IMAP/POP3/ManageSieve), spam filtering settings, autoresponder configuration,
        footer settings, allowlists/denylists, and account status. Use this to inspect individual mailbox
        settings before making changes or troubleshooting email issues.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            local_part: The username part of the email address (e.g., 'demo' for demo@mydomain.org)

        Returns:
            JSON object with complete mailbox configuration and status information
        """
        email_address = f"{local_part}@{domain}"
        await ctx.info(f"📋 Retrieving details for mailbox: {email_address}")

        try:
            factory = get_service_factory()
            service = factory.mailbox_service()
            result = await service.get_mailbox(domain, local_part)
            await ctx.info(f"✅ Retrieved configuration for {email_address}")
            return result
        except Exception as e:
            await ctx.error(f"❌ Failed to retrieve mailbox {email_address}: {str(e)}")
            raise

    @mcp.tool(
        tags={"mailbox", "create", "account"},
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,  # Creates new resource, not destructive
            "idempotentHint": False,  # Creating same mailbox twice will fail
            "openWorldHint": True,
        },
    )
    async def create_mailbox(
        ctx: Context,
        domain: str,
        local_part: str,
        name: str,
        password: Optional[str] = None,
        password_recovery_email: Optional[str] = None,
        is_internal: bool = False,
        forwarding_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new email mailbox with full storage and authentication capabilities. Mailboxes are complete
        email accounts that can receive, store, and send messages with IMAP/POP3 access. You can set an immediate
        password or send an invitation email for the user to set their own password. Use is_internal=True to
        restrict the mailbox to only receive messages from Migadu servers (useful for system accounts).
        Optionally configure automatic forwarding to an external address during creation.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            local_part: Username part of the email address (e.g., 'demo' for demo@mydomain.org)
            name: Display name for the mailbox user (e.g., 'Demo User')
            password: Set immediate password, or leave None to use invitation method
            password_recovery_email: Required if password is None - where to send setup invitation
            is_internal: If True, only accepts messages from Migadu servers (no external email)
            forwarding_to: Optional external email address to automatically forward messages to

        Returns:
            JSON object with newly created mailbox configuration and settings
        """
        email_address = f"{local_part}@{domain}"
        await ctx.info(f"📬 Creating mailbox: {email_address} ({name})")

        try:
            factory = get_service_factory()
            service = factory.mailbox_service()
            result = await service.create_mailbox(
                domain,
                local_part,
                name,
                password,
                password_recovery_email,
                is_internal,
                forwarding_to,
            )

            await ctx.info(f"✅ Successfully created mailbox: {email_address}")
            if forwarding_to:
                await ctx.info(f"🔄 Configured forwarding to: {forwarding_to}")
            if is_internal:
                await ctx.info("🔒 Configured as internal-only mailbox")

            return result
        except Exception as e:
            await ctx.error(f"❌ Failed to create mailbox {email_address}: {str(e)}")
            raise

    @mcp.tool(
        tags={"mailbox", "create", "convenience"},
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": True,
        },
    )
    async def create_my_mailbox(
        ctx: Context,
        local_part: str,
        name: str,
        password: Optional[str] = None,
        password_recovery_email: Optional[str] = None,
        is_internal: bool = False,
        forwarding_to: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new email mailbox on your default configured domain. This convenience function automatically
        uses your MIGADU_DOMAIN environment variable. Creates a complete email account with storage and
        authentication. Choose between setting an immediate password or sending an invitation email. Use
        is_internal=True for system accounts that should only receive internal messages.

        Args:
            local_part: Username part of the email address (e.g., 'demo' for demo@yourdomain.org)
            name: Display name for the mailbox user (e.g., 'Demo User')
            password: Set immediate password, or leave None to use invitation method
            password_recovery_email: Required if password is None - where to send setup invitation
            is_internal: If True, only accepts messages from Migadu servers
            forwarding_to: Optional external email address to automatically forward messages to

        Returns:
            JSON object with newly created mailbox configuration
        """
        config = get_config()
        domain = config.get_default_domain()
        email_address = f"{local_part}@{domain}"
        await ctx.info(
            f"📬 Creating mailbox on default domain: {email_address} ({name})"
        )

        try:
            factory = get_service_factory()
            service = factory.mailbox_service()
            result = await service.create_mailbox(
                domain,
                local_part,
                name,
                password,
                password_recovery_email,
                is_internal,
                forwarding_to,
            )

            await ctx.info(f"✅ Successfully created mailbox: {email_address}")
            if forwarding_to:
                await ctx.info(f"🔄 Configured forwarding to: {forwarding_to}")
            if is_internal:
                await ctx.info("🔒 Configured as internal-only mailbox")

            return result
        except Exception as e:
            await ctx.error(f"❌ Failed to create mailbox {email_address}: {str(e)}")
            raise

    @mcp.tool
    async def get_my_mailbox(local_part: str) -> Dict[str, Any]:
        """Retrieve detailed information about a specific mailbox on your default configured domain.
        This convenience function automatically uses your MIGADU_DOMAIN environment variable. Shows complete
        mailbox configuration including permissions, spam settings, autoresponder status, and security options.

        Args:
            local_part: Username part of the email address (e.g., 'demo' for demo@yourdomain.org)

        Returns:
            JSON object with complete mailbox configuration and status information
        """
        config = get_config()
        domain = config.get_default_domain()
        factory = get_service_factory()
        service = factory.mailbox_service()
        return await service.get_mailbox(domain, local_part)

    @mcp.tool
    async def list_my_aliases() -> Dict[str, Any]:
        """Retrieve all email aliases configured for your default domain. Aliases are email addresses that
        automatically forward incoming messages to one or more destination addresses without storing the
        messages themselves. This convenience function uses your MIGADU_DOMAIN environment variable.
        Use this to audit email forwarding rules and manage domain-wide email routing.

        Returns:
            JSON object containing array of all aliases with their destinations and configuration
        """
        config = get_config()
        domain = config.get_default_domain()
        factory = get_service_factory()
        service = factory.alias_service()
        return await service.list_aliases(domain)

    @mcp.tool(
        tags={"mailbox", "update", "configuration"},
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,  # Modifies settings but doesn't delete
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def update_mailbox(
        ctx: Context,
        domain: str,
        local_part: str,
        name: Optional[str] = None,
        may_send: Optional[bool] = None,
        may_receive: Optional[bool] = None,
        may_access_imap: Optional[bool] = None,
        may_access_pop3: Optional[bool] = None,
        spam_action: Optional[str] = None,
        spam_aggressiveness: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Modify configuration settings for an existing mailbox. Update display name, permissions
        (send/receive/IMAP/POP3 access), and spam filtering behavior. Use this to adjust mailbox capabilities
        without recreating the account. Common use cases include disabling send permissions for receive-only
        accounts, restricting protocol access, or adjusting spam filtering sensitivity.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            local_part: Username part of the email address (e.g., 'demo' for demo@mydomain.org)
            name: Update display name for the mailbox user
            may_send: Allow/deny sending emails from this mailbox
            may_receive: Allow/deny receiving emails to this mailbox
            may_access_imap: Allow/deny IMAP protocol access
            may_access_pop3: Allow/deny POP3 protocol access
            spam_action: How to handle spam ("folder", "reject", or other predefined values)
            spam_aggressiveness: Spam filtering sensitivity ("default", "aggressive", etc.)

        Returns:
            JSON object with updated mailbox configuration
        """
        email_address = f"{local_part}@{domain}"
        await ctx.info(f"⚙️ Updating configuration for mailbox: {email_address}")

        try:
            factory = get_service_factory()
            service = factory.mailbox_service()
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
            await ctx.info(f"✅ Successfully updated configuration for {email_address}")
            return result
        except Exception as e:
            await ctx.error(f"❌ Failed to update mailbox {email_address}: {str(e)}")
            raise

    @mcp.tool(
        tags={"mailbox", "delete", "destructive"},
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,  # Permanently deletes data
            "idempotentHint": True,  # Can be safely retried
            "openWorldHint": True,
        },
    )
    async def delete_mailbox(
        ctx: Context, domain: str, local_part: str
    ) -> Dict[str, Any]:
        """Permanently delete a mailbox and all its stored messages. This action is irreversible and will
        remove the email account, all stored emails, settings, and associated data. The email address
        becomes available for reuse after deletion. Use with caution as this cannot be undone.

        Note: Due to a Migadu API bug, successful deletions may return HTTP 500 errors. The operation
        actually succeeds despite the error response.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            local_part: Username part of the email address (e.g., 'demo' for demo@mydomain.org)

        Returns:
            JSON object confirming deletion (may show 500 error despite success)
        """
        email_address = f"{local_part}@{domain}"
        await ctx.warning(
            f"🗑️ DESTRUCTIVE: Deleting mailbox {email_address} - this cannot be undone!"
        )

        try:
            factory = get_service_factory()
            service = factory.mailbox_service()
            result = await service.delete_mailbox(domain, local_part)
            await ctx.info(f"✅ Successfully deleted mailbox: {email_address}")
            return result
        except Exception as e:
            await ctx.error(f"❌ Failed to delete mailbox {email_address}: {str(e)}")
            # Check if it's the known Migadu API bug
            if "500" in str(e) or "Internal Server Error" in str(e):
                await ctx.info(
                    f"ℹ️ Note: Migadu API often returns 500 errors for successful deletions. Please verify if {email_address} was actually deleted."
                )
            raise

    @mcp.tool(
        tags={"mailbox", "delete", "bulk", "destructive"},
        annotations={
            "readOnlyHint": False,
            "destructiveHint": True,  # Deletes resources
            "idempotentHint": True,  # Can be safely retried
            "openWorldHint": True,
        },
    )
    async def bulk_delete_mailboxes(
        ctx: Context, domain: str, local_parts: List[str]
    ) -> Dict[str, Any]:
        """Delete multiple mailboxes in one operation with intelligent error handling. This function
        automatically handles the Migadu API bug where successful deletions return HTTP 500 errors.
        Provides detailed results showing which mailboxes were deleted, which were already gone, and
        which actually failed. Use this for cleanup operations or managing large numbers of test accounts.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            local_parts: List of usernames to delete (e.g., ['demo1', 'demo2', 'test'])

        Returns:
            JSON object with arrays: deleted, already_gone, failed, and total_requested count
        """
        total = len(local_parts)
        await ctx.info(f"🗑️ Starting bulk deletion of {total} mailboxes from {domain}")

        try:
            factory = get_service_factory()
            service = factory.mailbox_service()

            # Add progress reporting during the operation
            await ctx.report_progress(0, total)
            result = await service.bulk_delete_mailboxes(domain, local_parts)
            await ctx.report_progress(total, total)

            deleted_count = len(result.get("deleted", []))
            failed_count = len(result.get("failed", []))
            already_gone_count = len(result.get("already_gone", []))

            await ctx.info(
                f"✅ Bulk deletion completed: {deleted_count} deleted, {already_gone_count} already gone, {failed_count} failed"
            )

            if failed_count > 0:
                await ctx.warning(
                    f"⚠️ {failed_count} mailboxes failed to delete - check the 'failed' array in response"
                )

            return result
        except Exception as e:
            await ctx.error(f"❌ Bulk deletion failed for {domain}: {str(e)}")
            raise

    @mcp.tool(
        tags={"mailbox", "password", "security"},
        annotations={
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": True,
        },
    )
    async def reset_mailbox_password(
        ctx: Context, domain: str, local_part: str, new_password: str
    ) -> Dict[str, Any]:
        """Change the authentication password for an existing mailbox. The new password will be required
        for IMAP, POP3, SMTP authentication, and webmail access. Use this for password recovery, security
        updates, or when users forget their credentials. The change takes effect immediately.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            local_part: Username part of the email address (e.g., 'demo' for demo@mydomain.org)
            new_password: The new password for authentication

        Returns:
            JSON object confirming password update
        """
        email_address = f"{local_part}@{domain}"
        await ctx.info(f"🔐 Resetting password for mailbox: {email_address}")

        try:
            factory = get_service_factory()
            service = factory.mailbox_service()
            result = await service.reset_mailbox_password(
                domain, local_part, new_password
            )
            await ctx.info(f"✅ Successfully reset password for {email_address}")
            return result
        except Exception as e:
            await ctx.error(
                f"❌ Failed to reset password for {email_address}: {str(e)}"
            )
            raise

    @mcp.tool
    async def set_autoresponder(
        domain: str,
        local_part: str,
        active: bool,
        subject: Optional[str] = None,
        body: Optional[str] = None,
        expires_on: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Configure automatic email responses for a mailbox. When active, the mailbox will automatically
        send a reply to incoming messages using the specified subject and body text. Commonly used for
        out-of-office messages, vacation notices, or informational responses. You can set an expiration
        date to automatically disable the autoresponder after a specific date.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            local_part: Username part of the email address (e.g., 'demo' for demo@mydomain.org)
            active: Whether the autoresponder is enabled or disabled
            subject: Subject line for automatic replies (can include {{subject}} placeholder)
            body: Message content for automatic replies
            expires_on: Date when autoresponder should automatically disable (YYYY-MM-DD format)

        Returns:
            JSON object confirming autoresponder configuration
        """
        factory = get_service_factory()
        service = factory.mailbox_service()
        return await service.set_autoresponder(
            domain, local_part, active, subject, body, expires_on
        )

    @mcp.tool
    async def list_forwardings(domain: str, mailbox: str) -> Dict[str, Any]:
        """Retrieve all external forwarding rules configured for a mailbox. Forwardings automatically
        send copies of incoming messages to external email addresses with confirmation and verification
        processes. Each forwarding shows the destination address, confirmation status, active state,
        and expiration settings. Use this to audit external forwarding rules and manage message routing.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            mailbox: Username part of the mailbox (e.g., 'demo' for demo@mydomain.org)

        Returns:
            JSON object containing array of all forwarding rules with status and configuration
        """
        factory = get_service_factory()
        service = factory.mailbox_service()
        return await service.list_forwardings(domain, mailbox)

    @mcp.tool
    async def create_forwarding(
        domain: str, mailbox: str, address: str
    ) -> Dict[str, Any]:
        """Create a new external forwarding rule for a mailbox. This sends copies of incoming messages
        to the specified external email address. Migadu will send a confirmation email to the destination
        address that must be confirmed before forwarding becomes active. Use this to route messages to
        external systems or backup email accounts.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            mailbox: Username part of the mailbox (e.g., 'demo' for demo@mydomain.org)
            address: External email address to forward messages to (e.g., 'user@external.com')

        Returns:
            JSON object with forwarding details including confirmation status
        """
        factory = get_service_factory()
        service = factory.mailbox_service()
        return await service.create_forwarding(domain, mailbox, address)

    @mcp.tool
    async def get_forwarding(domain: str, mailbox: str, address: str) -> Dict[str, Any]:
        """Retrieve detailed information about a specific external forwarding rule. Shows confirmation
        status, active state, expiration settings, and any blocking information. Use this to check the
        status of forwarding rules and troubleshoot delivery issues.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            mailbox: Username part of the mailbox (e.g., 'demo' for demo@mydomain.org)
            address: External email address of the forwarding rule

        Returns:
            JSON object with detailed forwarding status and configuration
        """
        factory = get_service_factory()
        service = factory.mailbox_service()
        return await service.get_forwarding(domain, mailbox, address)

    @mcp.tool
    async def update_forwarding(
        domain: str,
        mailbox: str,
        address: str,
        is_active: Optional[bool] = None,
        expires_on: Optional[str] = None,
        remove_upon_expiry: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Modify settings for an existing external forwarding rule. Enable/disable forwarding, set
        expiration dates, or configure automatic removal after expiration. Use expires_on with future
        dates only - past dates will return an error. This is useful for temporary forwarding
        arrangements or scheduled forwarding changes.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            mailbox: Username part of the mailbox (e.g., 'demo' for demo@mydomain.org)
            address: External email address of the forwarding rule
            is_active: Enable or disable the forwarding rule
            expires_on: Date when forwarding should stop (YYYY-MM-DD format, future dates only)
            remove_upon_expiry: Whether to delete the rule when it expires

        Returns:
            JSON object with updated forwarding configuration
        """
        factory = get_service_factory()
        service = factory.mailbox_service()
        return await service.update_forwarding(
            domain, mailbox, address, is_active, expires_on, remove_upon_expiry
        )

    @mcp.tool
    async def delete_forwarding(
        domain: str, mailbox: str, address: str
    ) -> Dict[str, Any]:
        """Permanently remove an external forwarding rule from a mailbox. Messages will no longer be
        forwarded to the specified external address. This action is immediate and cannot be undone.
        Use this to clean up old forwarding rules or stop unwanted message routing.

        Args:
            domain: The domain name (e.g., 'mydomain.org')
            mailbox: Username part of the mailbox (e.g., 'demo' for demo@mydomain.org)
            address: External email address of the forwarding rule to delete

        Returns:
            JSON object confirming forwarding rule deletion
        """
        factory = get_service_factory()
        service = factory.mailbox_service()
        return await service.delete_forwarding(domain, mailbox, address)
