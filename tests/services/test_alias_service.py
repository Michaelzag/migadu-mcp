"""Tests for AliasService."""

from __future__ import annotations

import json

import pytest
import respx

from migadu_mcp.client.migadu_client import MigaduClient
from migadu_mcp.services.alias_service import AliasService


@pytest.fixture
def service(client: MigaduClient) -> AliasService:
    return AliasService(client)


@pytest.mark.asyncio
async def test_list_aliases(service: AliasService, mock_api: respx.Router) -> None:
    # Real API returns "address_aliases", not "aliases" — verified against live API.
    mock_api.get("/domains/test.example/aliases").respond(
        200, json={"address_aliases": []}
    )
    result = await service.list_aliases("test.example")
    assert result == {"address_aliases": []}


@pytest.mark.asyncio
async def test_get_alias(service: AliasService, mock_api: respx.Router) -> None:
    mock_api.get("/domains/test.example/aliases/info").respond(
        200, json={"address": "info@test.example"}
    )
    result = await service.get_alias("test.example", "info")
    assert result["address"] == "info@test.example"


@pytest.mark.asyncio
async def test_create_alias_joins_destinations_as_csv(
    service: AliasService, mock_api: respx.Router
) -> None:
    route = mock_api.post("/domains/test.example/aliases").respond(200, json={})
    await service.create_alias(
        "test.example", "info", ["a@x.com", "b@x.com"], is_internal=True
    )
    body = json.loads(route.calls[0].request.content)
    assert body == {
        "local_part": "info",
        "destinations": "a@x.com,b@x.com",
        "is_internal": True,
    }


@pytest.mark.asyncio
async def test_update_alias(service: AliasService, mock_api: respx.Router) -> None:
    route = mock_api.put("/domains/test.example/aliases/info").respond(200, json={})
    await service.update_alias("test.example", "info", ["c@x.com"])
    body = json.loads(route.calls[0].request.content)
    assert body == {"destinations": "c@x.com"}


@pytest.mark.asyncio
async def test_delete_alias_500_succeeds(
    service: AliasService, mock_api: respx.Router
) -> None:
    mock_api.delete("/domains/test.example/aliases/info").respond(500, text="bug")
    await service.delete_alias("test.example", "info")
