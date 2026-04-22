"""Service layer for the Migadu API."""

from migadu_mcp.services.alias_service import AliasService
from migadu_mcp.services.domain_service import DomainService
from migadu_mcp.services.forwarding_service import ForwardingService
from migadu_mcp.services.identity_service import IdentityService
from migadu_mcp.services.mailbox_service import MailboxService
from migadu_mcp.services.rewrite_service import RewriteService
from migadu_mcp.services.service_factory import ServiceFactory, get_service_factory

__all__ = [
    "AliasService",
    "DomainService",
    "ForwardingService",
    "IdentityService",
    "MailboxService",
    "RewriteService",
    "ServiceFactory",
    "get_service_factory",
]
