#!/usr/bin/env python3
"""
Service layer for Migadu API operations
"""

from migadu_mcp.services.mailbox_service import MailboxService
from migadu_mcp.services.identity_service import IdentityService
from migadu_mcp.services.alias_service import AliasService
from migadu_mcp.services.rewrite_service import RewriteService
from migadu_mcp.services.service_factory import ServiceFactory, get_service_factory

__all__ = [
    "MailboxService",
    "IdentityService",
    "AliasService",
    "RewriteService",
    "ServiceFactory",
    "get_service_factory",
]
