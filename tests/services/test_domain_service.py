"""Tests for DomainService."""

from __future__ import annotations

import json

import pytest
import respx

from migadu_mcp.client.migadu_client import MigaduAPIError, MigaduClient
from migadu_mcp.services.domain_service import DomainService


@pytest.fixture
def service(client: MigaduClient) -> DomainService:
    return DomainService(client)


@pytest.mark.asyncio
async def test_list_domains(service: DomainService, mock_api: respx.Router) -> None:
    mock_api.get("/domains").respond(200, json={"domains": [{"name": "a.example"}]})
    result = await service.list_domains()
    assert result == {"domains": [{"name": "a.example"}]}


@pytest.mark.asyncio
async def test_get_domain(service: DomainService, mock_api: respx.Router) -> None:
    mock_api.get("/domains/a.example").respond(200, json={"name": "a.example"})
    result = await service.get_domain("a.example")
    assert result["name"] == "a.example"


@pytest.mark.asyncio
async def test_create_domain(service: DomainService, mock_api: respx.Router) -> None:
    route = mock_api.post("/domains").respond(200, json={"name": "new.example"})
    await service.create_domain(
        "new.example", hosted_dns=False, create_default_addresses=True
    )
    body = json.loads(route.calls[0].request.content)
    assert body == {
        "name": "new.example",
        "hosted_dns": False,
        "create_default_addresses": True,
    }


@pytest.mark.asyncio
async def test_update_domain_uses_patch(
    service: DomainService, mock_api: respx.Router
) -> None:
    route = mock_api.patch("/domains/a.example").respond(
        200, json={"name": "a.example"}
    )
    await service.update_domain("a.example", description="new desc")
    body = json.loads(route.calls[0].request.content)
    assert body == {"description": "new desc"}


@pytest.mark.asyncio
async def test_update_domain_skips_none_fields(
    service: DomainService, mock_api: respx.Router
) -> None:
    route = mock_api.patch("/domains/a.example").respond(200, json={})
    await service.update_domain("a.example", description=None, tags="prod")
    body = json.loads(route.calls[0].request.content)
    assert body == {"tags": "prod"}


@pytest.mark.asyncio
async def test_get_domain_records(
    service: DomainService, mock_api: respx.Router
) -> None:
    mock_api.get("/domains/a.example/records").respond(200, json={"records": []})
    result = await service.get_domain_records("a.example")
    assert "records" in result


@pytest.mark.asyncio
async def test_get_domain_diagnostics(
    service: DomainService, mock_api: respx.Router
) -> None:
    mock_api.get("/domains/a.example/diagnostics").respond(200, json={"ok": True})
    result = await service.get_domain_diagnostics("a.example")
    assert result["ok"] is True


@pytest.mark.asyncio
async def test_activate_domain(service: DomainService, mock_api: respx.Router) -> None:
    mock_api.get("/domains/a.example/activate").respond(200, json={"activated": True})
    result = await service.activate_domain("a.example")
    assert result["activated"] is True


@pytest.mark.asyncio
async def test_activate_domain_422_when_dns_not_ready(
    service: DomainService, mock_api: respx.Router
) -> None:
    mock_api.get("/domains/a.example/activate").respond(422, text="DNS not configured")
    with pytest.raises(MigaduAPIError) as exc:
        await service.activate_domain("a.example")
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_get_domain_usage(service: DomainService, mock_api: respx.Router) -> None:
    mock_api.get("/domains/a.example/usage").respond(
        200, json={"incoming": 100, "outgoing": 50, "storage": 2.5}
    )
    result = await service.get_domain_usage("a.example")
    assert result["storage"] == 2.5
