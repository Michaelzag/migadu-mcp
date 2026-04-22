"""Migadu MCP server — domains, mailboxes, aliases, identities, forwardings, rewrites."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("migadu-mcp")
except PackageNotFoundError:
    __version__ = "0.0.0+dev"

from migadu_mcp.main import mcp

__all__ = ["mcp", "__version__"]
