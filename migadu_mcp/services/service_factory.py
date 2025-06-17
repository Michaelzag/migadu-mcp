#!/usr/bin/env python3
"""
Service factory for dependency injection
"""

from typing import Optional
from migadu_mcp.client.migadu_client import MigaduClient
from migadu_mcp.config import get_config
from migadu_mcp.services.mailbox_service import MailboxService
from migadu_mcp.services.identity_service import IdentityService
from migadu_mcp.services.alias_service import AliasService
from migadu_mcp.services.rewrite_service import RewriteService


class ServiceFactory:
    """Factory for creating service instances with dependency injection"""

    def __init__(self):
        self._client: Optional[MigaduClient] = None

    def _get_client(self) -> MigaduClient:
        """Get or create Migadu client"""
        if self._client is None:
            config = get_config()
            # Config validation ensures these are not None
            assert config.email is not None, "Email must be configured"
            assert config.api_key is not None, "API key must be configured"
            self._client = MigaduClient(config.email, config.api_key)
        return self._client

    def mailbox_service(self) -> MailboxService:
        """Create mailbox service instance"""
        return MailboxService(self._get_client())

    def identity_service(self) -> IdentityService:
        """Create identity service instance"""
        return IdentityService(self._get_client())

    def alias_service(self) -> AliasService:
        """Create alias service instance"""
        return AliasService(self._get_client())

    def rewrite_service(self) -> RewriteService:
        """Create rewrite service instance"""
        return RewriteService(self._get_client())


# Global factory instance
_factory: Optional[ServiceFactory] = None


def get_service_factory() -> ServiceFactory:
    """Get global service factory instance"""
    global _factory
    if _factory is None:
        _factory = ServiceFactory()
    return _factory
