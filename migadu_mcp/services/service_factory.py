"""Service factory — one HTTP client, one instance of each service, per server process."""

from __future__ import annotations

from migadu_mcp.client.migadu_client import MigaduClient
from migadu_mcp.config import get_config
from migadu_mcp.services.alias_service import AliasService
from migadu_mcp.services.domain_service import DomainService
from migadu_mcp.services.forwarding_service import ForwardingService
from migadu_mcp.services.identity_service import IdentityService
from migadu_mcp.services.mailbox_service import MailboxService
from migadu_mcp.services.rewrite_service import RewriteService


class ServiceFactory:
    """Lazy factory. Creates one MigaduClient and shares it across services.

    Call `aclose()` on server shutdown to close the HTTP client cleanly.
    """

    def __init__(self) -> None:
        self._client: MigaduClient | None = None

    def _get_client(self) -> MigaduClient:
        if self._client is None:
            config = get_config()
            if config.email is None or config.api_key is None:
                raise ValueError("MIGADU_EMAIL and MIGADU_API_KEY must be set")
            self._client = MigaduClient(config.email, config.api_key)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    def mailbox_service(self) -> MailboxService:
        return MailboxService(self._get_client())

    def identity_service(self) -> IdentityService:
        return IdentityService(self._get_client())

    def alias_service(self) -> AliasService:
        return AliasService(self._get_client())

    def rewrite_service(self) -> RewriteService:
        return RewriteService(self._get_client())

    def domain_service(self) -> DomainService:
        return DomainService(self._get_client())

    def forwarding_service(self) -> ForwardingService:
        return ForwardingService(self._get_client())


_factory: ServiceFactory | None = None


def get_service_factory() -> ServiceFactory:
    global _factory
    if _factory is None:
        _factory = ServiceFactory()
    return _factory


async def reset_service_factory() -> None:
    """Close and drop the singleton. For tests and server shutdown."""
    global _factory
    if _factory is not None:
        await _factory.aclose()
        _factory = None
