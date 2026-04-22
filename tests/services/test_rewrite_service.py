"""Tests for RewriteService."""

from __future__ import annotations

import json

import pytest
import respx

from migadu_mcp.client.migadu_client import MigaduClient
from migadu_mcp.services.rewrite_service import RewriteService


@pytest.fixture
def service(client: MigaduClient) -> RewriteService:
    return RewriteService(client)


@pytest.mark.asyncio
async def test_list_rewrites(service: RewriteService, mock_api: respx.Router) -> None:
    mock_api.get("/domains/test.example/rewrites").respond(200, json={"rewrites": []})
    result = await service.list_rewrites("test.example")
    assert result == {"rewrites": []}


@pytest.mark.asyncio
async def test_get_rewrite(service: RewriteService, mock_api: respx.Router) -> None:
    mock_api.get("/domains/test.example/rewrites/demo-rule").respond(
        200, json={"name": "demo-rule"}
    )
    result = await service.get_rewrite("test.example", "demo-rule")
    assert result["name"] == "demo-rule"


@pytest.mark.asyncio
async def test_create_rewrite(service: RewriteService, mock_api: respx.Router) -> None:
    route = mock_api.post("/domains/test.example/rewrites").respond(200, json={})
    await service.create_rewrite(
        "test.example", "demo", "demo-*", ["info@x.com"], order_num=10
    )
    body = json.loads(route.calls[0].request.content)
    assert body == {
        "name": "demo",
        "local_part_rule": "demo-*",
        "destinations": "info@x.com",
        "order_num": 10,
    }


@pytest.mark.asyncio
async def test_update_rewrite_with_rename(
    service: RewriteService, mock_api: respx.Router
) -> None:
    route = mock_api.put("/domains/test.example/rewrites/old-name").respond(
        200, json={}
    )
    await service.update_rewrite(
        "test.example", "old-name", new_name="new-name", order_num=20
    )
    body = json.loads(route.calls[0].request.content)
    assert body == {"name": "new-name", "order_num": 20}


@pytest.mark.asyncio
async def test_delete_rewrite_500_succeeds(
    service: RewriteService, mock_api: respx.Router
) -> None:
    mock_api.delete("/domains/test.example/rewrites/demo").respond(500, text="bug")
    await service.delete_rewrite("test.example", "demo")
