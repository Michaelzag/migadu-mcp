"""Boot smoke test for the Migadu MCP server.

Asserts only that the server starts and registers a non-zero number of tools and
resources. Behavior coverage lives in tests/services/, tests/test_decorators.py,
tests/test_schemas.py, tests/test_http_client.py, and tests/test_summarize.py.
"""

from __future__ import annotations

import pytest
from fastmcp import Client, FastMCP

from migadu_mcp.tools.alias_tools import register_alias_tools
from migadu_mcp.tools.domain_tools import register_domain_tools
from migadu_mcp.tools.forwarding_tools import register_forwarding_tools
from migadu_mcp.tools.identity_tools import register_identity_tools
from migadu_mcp.tools.mailbox_tools import register_mailbox_tools
from migadu_mcp.tools.resource_tools import register_resources
from migadu_mcp.tools.rewrite_tools import register_rewrite_tools


@pytest.fixture
def mcp_server() -> FastMCP:
    server = FastMCP("test-migadu")
    register_domain_tools(server)
    register_mailbox_tools(server)
    register_identity_tools(server)
    register_alias_tools(server)
    register_rewrite_tools(server)
    register_forwarding_tools(server)
    register_resources(server)
    return server


@pytest.mark.asyncio
async def test_server_boots_and_registers_tools(mcp_server: FastMCP) -> None:
    async with Client(mcp_server) as client:
        tools = await client.list_tools()
        templates = await client.list_resource_templates()
        assert len(tools) >= 20, f"expected at least 20 tools, got {len(tools)}"
        assert len(templates) >= 5
