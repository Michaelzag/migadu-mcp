"""Domain service for the Migadu API."""

from __future__ import annotations

from typing import Any

from migadu_mcp.client.migadu_client import MigaduClient


class DomainService:
    """CRUD and operational endpoints for domains."""

    def __init__(self, client: MigaduClient) -> None:
        self.client = client

    async def list_domains(self) -> dict[str, Any]:
        return await self.client.get("/domains")

    async def get_domain(self, name: str) -> dict[str, Any]:
        return await self.client.get(f"/domains/{name}")

    async def create_domain(
        self,
        name: str,
        hosted_dns: bool = False,
        create_default_addresses: bool = True,
    ) -> dict[str, Any]:
        data = {
            "name": name,
            "hosted_dns": hosted_dns,
            "create_default_addresses": create_default_addresses,
        }
        return await self.client.post("/domains", json=data)

    async def update_domain(
        self,
        name: str,
        description: str | None = None,
        tags: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {}
        if description is not None:
            data["description"] = description
        if tags is not None:
            data["tags"] = tags
        return await self.client.patch(f"/domains/{name}", json=data)

    async def get_domain_records(self, name: str) -> dict[str, Any]:
        """Returns DNS records (MX, SPF, DKIM, DMARC, verification) needed for setup."""
        return await self.client.get(f"/domains/{name}/records")

    async def get_domain_diagnostics(self, name: str) -> dict[str, Any]:
        """Returns DNS validation results after records are configured externally."""
        return await self.client.get(f"/domains/{name}/diagnostics")

    async def activate_domain(self, name: str) -> dict[str, Any]:
        """Activate a domain once DNS records are correctly configured.

        Raises MigaduAPIError(422, ...) if DNS validation fails.
        """
        return await self.client.get(f"/domains/{name}/activate")

    async def get_domain_usage(self, name: str) -> dict[str, Any]:
        """Returns message and storage usage metrics."""
        return await self.client.get(f"/domains/{name}/usage")
