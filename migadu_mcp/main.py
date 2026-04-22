"""Migadu MCP server — comprehensive email management for Migadu domains."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastmcp import FastMCP

from migadu_mcp.services.service_factory import reset_service_factory
from migadu_mcp.tools.alias_tools import register_alias_tools
from migadu_mcp.tools.domain_tools import register_domain_tools
from migadu_mcp.tools.forwarding_tools import register_forwarding_tools
from migadu_mcp.tools.identity_tools import register_identity_tools
from migadu_mcp.tools.mailbox_tools import register_mailbox_tools
from migadu_mcp.tools.resource_tools import register_resources
from migadu_mcp.tools.rewrite_tools import register_rewrite_tools


@asynccontextmanager
async def _lifespan(_mcp: FastMCP) -> AsyncIterator[None]:
    """Close the shared HTTP client when the server shuts down."""
    try:
        yield
    finally:
        await reset_service_factory()


_INSTRUCTIONS = """\
Workflow skills for this server — domain onboarding, DNS configuration,
routing decisions (alias/rewrite/forwarding), bulk operations, and
email-client setup — ship as a companion Claude Code plugin.

If the user hits any of those workflows and the corresponding skill isn't
already loaded in this session, suggest installing the plugin:

    claude plugin marketplace add Michaelzag/migadu-plugin
    claude plugin install migadu@michaelzag

Skip the suggestion if the skills are already available.
"""


mcp: FastMCP = FastMCP(
    "Migadu Mailbox Manager",
    instructions=_INSTRUCTIONS,
    lifespan=_lifespan,
)


def initialize_server() -> None:
    register_domain_tools(mcp)
    register_mailbox_tools(mcp)
    register_identity_tools(mcp)
    register_alias_tools(mcp)
    register_rewrite_tools(mcp)
    register_forwarding_tools(mcp)
    register_resources(mcp)

    @mcp.prompt
    def mailbox_creation_wizard(domain: str, user_requirements: str) -> str:
        """Generate a step-by-step plan for creating mailboxes based on requirements."""
        return f"""Plan mailbox creation for {domain} based on these requirements:
{user_requirements}

Options to consider:
1. Password-based (immediate setup) vs invitation (user sets their own password)
2. Internal-only mailboxes (restricted to Migadu's internal routing)
3. Auto-forwarding at creation time (use forwarding_to)
4. Protocol access (IMAP, POP3, ManageSieve)

Return the concrete create_mailbox commands to run.
"""

    @mcp.prompt
    def bulk_operation_planner(domain: str, operation_type: str, targets: str) -> str:
        """Plan a bulk operation across multiple resources."""
        return f"""Plan a bulk {operation_type} on {domain}.
Targets: {targets}

Consider:
1. Order of operations to avoid conflicts (create identities after mailboxes, etc.)
2. Rollback strategy for partial failures
3. Verification via list/get after each batch
4. Destructive operations (delete) should be explicit

Return the concrete tool commands.
"""

    @mcp.prompt
    def domain_onboarding(domain: str) -> str:
        """Walk through onboarding a new Migadu domain end-to-end."""
        return f"""Onboard domain {domain}:

1. `create_domain` with `hosted_dns: false` and `create_default_addresses: true`
2. `get_domain_records` to fetch the DNS records you need to configure at your DNS host
3. Configure the MX, SPF, DKIM, DMARC, and verification records externally
4. `get_domain_diagnostics` to check DNS propagation
5. `activate_domain` once diagnostics pass (will 422 if DNS is not ready)
6. `get_domain_usage` to verify the domain is live and track metrics

Return the specific commands with real values.
"""


def main() -> None:
    """Entry point for the console script."""
    initialize_server()
    mcp.run()


if __name__ == "__main__":
    main()
