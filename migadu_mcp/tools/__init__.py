#!/usr/bin/env python3
"""
MCP tools for Migadu API
"""

# Import all tool modules
from migadu_mcp.tools import mailbox_tools
from migadu_mcp.tools import identity_tools
from migadu_mcp.tools import alias_tools
from migadu_mcp.tools import rewrite_tools
from migadu_mcp.tools import resource_tools

__all__ = [
    "mailbox_tools",
    "identity_tools",
    "alias_tools",
    "rewrite_tools",
    "resource_tools",
]
