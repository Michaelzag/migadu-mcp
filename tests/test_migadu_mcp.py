#!/usr/bin/env python3
"""
FastMCP testing infrastructure for Migadu MCP Server
"""

import pytest
from fastmcp import Client


@pytest.fixture
def mcp_server():
    """Fixture providing initialized FastMCP server for testing"""
    from fastmcp import FastMCP
    from migadu_mcp.tools.mailbox_tools import register_mailbox_tools
    from migadu_mcp.tools.identity_tools import register_identity_tools
    from migadu_mcp.tools.alias_tools import register_alias_tools
    from migadu_mcp.tools.rewrite_tools import register_rewrite_tools
    from migadu_mcp.tools.resource_tools import register_resources

    # Create a fresh server instance for testing to avoid duplicate warnings
    test_mcp = FastMCP("Test Migadu Server")
    register_mailbox_tools(test_mcp)
    register_identity_tools(test_mcp)
    register_alias_tools(test_mcp)
    register_rewrite_tools(test_mcp)
    register_resources(test_mcp)

    # Add test prompts
    @test_mcp.prompt
    def mailbox_creation_wizard(domain: str, user_requirements: str) -> str:
        return f"Test prompt for {domain}: {user_requirements}"

    @test_mcp.prompt
    def bulk_operation_planner(domain: str, operation_type: str, targets: str) -> str:
        return f"Test bulk operation for {domain}: {operation_type} on {targets}"

    return test_mcp


class TestMigaduMCPTools:
    """Test suite for Migadu MCP tools using FastMCP's built-in client"""

    async def test_list_tools(self, mcp_server):
        """Test that all expected tools are registered"""
        async with Client(mcp_server) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]

            # Expected tools based on all the tool files
            expected_tools = [
                # Mailbox tools
                "list_mailboxes",
                "list_my_mailboxes",
                "get_mailbox",
                "get_my_mailbox",
                "create_mailbox",
                "create_my_mailbox",
                "update_mailbox",
                "delete_mailbox",
                "bulk_delete_mailboxes",
                "reset_mailbox_password",
                "set_autoresponder",
                "list_forwardings",
                "create_forwarding",
                "get_forwarding",
                "update_forwarding",
                "delete_forwarding",
                "list_my_aliases",
                # Alias tools
                "list_aliases",
                "create_alias",
                "get_alias",
                "update_alias",
                "delete_alias",
                # Identity tools
                "list_identities",
                "create_identity",
                "get_identity",
                "update_identity",
                "delete_identity",
                # Rewrite tools
                "list_rewrites",
                "create_rewrite",
                "get_rewrite",
                "update_rewrite",
                "delete_rewrite",
            ]

            print(f"Found {len(tool_names)} tools: {sorted(tool_names)}")
            print(f"Expected {len(expected_tools)} tools: {sorted(expected_tools)}")

            # Check that all expected tools are present
            missing_tools = [tool for tool in expected_tools if tool not in tool_names]
            extra_tools = [tool for tool in tool_names if tool not in expected_tools]

            if missing_tools:
                print(f"Missing tools: {missing_tools}")
            if extra_tools:
                print(f"Extra tools: {extra_tools}")

            # All expected tools should be present
            for tool in expected_tools:
                assert tool in tool_names, f"Missing tool: {tool}"

    async def test_list_resources(self, mcp_server):
        """Test that all expected resources are registered"""
        async with Client(mcp_server) as client:
            resources = await client.list_resources()
            # Resources should be empty since we have resource templates
            assert isinstance(resources, list)

    async def test_list_resource_templates(self, mcp_server):
        """Test that resource templates are registered"""
        async with Client(mcp_server) as client:
            templates = await client.list_resource_templates()
            template_uris = [template.uriTemplate for template in templates]

            # Expected resource templates based on resource_tools.py
            expected_templates = [
                "mailboxes://{domain}",
                "mailbox://{domain}/{local_part}",
                "identities://{domain}/{mailbox}",
                "forwardings://{domain}/{mailbox}",
                "aliases://{domain}",
                "rewrites://{domain}",
            ]

            print(
                f"Found {len(template_uris)} resource templates: {sorted(template_uris)}"
            )
            print(
                f"Expected {len(expected_templates)} templates: {sorted(expected_templates)}"
            )

            # Check that all expected templates are present
            for template in expected_templates:
                assert template in template_uris, (
                    f"Missing resource template: {template}"
                )

    async def test_list_prompts(self, mcp_server):
        """Test that prompts are registered"""
        async with Client(mcp_server) as client:
            prompts = await client.list_prompts()
            prompt_names = [prompt.name for prompt in prompts]

            # Check for expected prompts
            assert "mailbox_creation_wizard" in prompt_names
            assert "bulk_operation_planner" in prompt_names


class TestMigaduMCPIntegration:
    """Integration tests that require valid Migadu credentials"""

    @pytest.mark.integration
    async def test_list_my_mailboxes_integration(self, mcp_server):
        """Integration test for listing mailboxes (requires valid env vars)"""
        async with Client(mcp_server) as client:
            try:
                result = await client.call_tool("list_my_mailboxes", {})
                # Should return a valid result structure
                assert len(result) > 0
                # Just check we got some kind of response
                assert result[0] is not None
            except Exception as e:
                # If no valid credentials, should get a configuration error
                assert "migadu_email" in str(e).lower() or "api_key" in str(e).lower()

    @pytest.mark.integration
    async def test_read_mailboxes_resource(self, mcp_server):
        """Integration test for reading mailboxes resource"""
        async with Client(mcp_server) as client:
            try:
                # This would need a real domain configured
                result = await client.read_resource("mailboxes://example.com")
                assert isinstance(result, list)
            except Exception as e:
                # Expected if no valid configuration
                assert "migadu_email" in str(e).lower() or "api_key" in str(e).lower()


# Integration tests are configured via pyproject.toml pytest markers
