#!/usr/bin/env python3
"""
Migadu MCP Server - Comprehensive email management for Migadu domains
"""

from fastmcp import FastMCP
from migadu_mcp.tools.mailbox_tools import register_mailbox_tools
from migadu_mcp.tools.identity_tools import register_identity_tools
from migadu_mcp.tools.alias_tools import register_alias_tools
from migadu_mcp.tools.rewrite_tools import register_rewrite_tools
from migadu_mcp.tools.resource_tools import register_resources


# Initialize FastMCP server
mcp: FastMCP = FastMCP("Migadu Mailbox Manager")


def initialize_server():
    """Initialize the MCP server with all tools and resources"""
    # Register all tools
    register_mailbox_tools(mcp)
    register_identity_tools(mcp)
    register_alias_tools(mcp)
    register_rewrite_tools(mcp)
    register_resources(mcp)

    # Add prompts
    @mcp.prompt
    def mailbox_creation_wizard(domain: str, user_requirements: str) -> str:
        """Generate a step-by-step plan for creating mailboxes based on requirements"""
        return f"""
Please help me create mailboxes for domain {domain} based on these requirements:
{user_requirements}

Consider the following options:
1. Basic mailbox with password
2. Mailbox with invitation email for user to set password
3. Internal-only mailbox (no external email reception)
4. Mailbox with automatic forwarding
5. Mailbox with specific permissions (IMAP, POP3, etc.)

Provide a detailed plan with the specific create_mailbox commands needed.
"""

    @mcp.prompt
    def bulk_operation_planner(domain: str, operation_type: str, targets: str) -> str:
        """Plan bulk operations for multiple mailboxes or aliases"""
        return f"""
Help me plan a bulk {operation_type} operation for domain {domain}.
Targets: {targets}

Provide step-by-step commands and consider:
1. Order of operations to avoid conflicts
2. Error handling and rollback procedures
3. Verification steps after completion
4. Best practices for the specific operation type

Generate the specific tool commands needed.
"""


def main():
    """Entry point for the console script"""
    initialize_server()
    mcp.run()


if __name__ == "__main__":
    main()
