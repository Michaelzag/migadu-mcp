"""
Migadu MCP Server

MCP server for comprehensive Migadu email management - mailboxes, aliases, identities, forwardings, and rewrites.
"""

try:
    from importlib.metadata import version
    __version__ = version("migadu-mcp")
except Exception:
    # Fallback for development or when package not installed
    __version__ = "0.0.0+dev"

__author__ = "Michael Broel"
__email__ = "Michael@Michaelzag.com"

from .main import mcp

__all__ = ["mcp", "__version__"]
