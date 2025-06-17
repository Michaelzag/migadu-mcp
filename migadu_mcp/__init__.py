"""
Migadu MCP Server

MCP server for comprehensive Migadu email management - mailboxes, aliases, identities, forwardings, and rewrites.
"""

__version__ = "3.1.5"
__author__ = "Michael Broel"
__email__ = "Michael@Michaelzag.com"

from .main import mcp

__all__ = ["mcp"]
