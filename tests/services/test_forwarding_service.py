"""Tests for ForwardingService."""

from __future__ import annotations

import json

import pytest
import respx

from migadu_mcp.client.migadu_client import MigaduClient
from migadu_mcp.services.forwarding_service import ForwardingService


@pytest.fixture
def service(client: MigaduClient) -> ForwardingService:
    return ForwardingService(client)


@pytest.mark.asyncio
async def test_list_forwardings(
    service: ForwardingService, mock_api: respx.Router
) -> None:
    mock_api.get("/domains/test.example/mailboxes/alice/forwardings").respond(
        200, json={"forwardings": []}
    )
    result = await service.list_forwardings("test.example", "alice")
    assert result == {"forwardings": []}


@pytest.mark.asyncio
async def test_get_forwarding_encodes_address(
    service: ForwardingService, mock_api: respx.Router
) -> None:
    # @ must be URL-encoded
    route = mock_api.get(
        "/domains/test.example/mailboxes/alice/forwardings/bob%40elsewhere.com"
    ).respond(200, json={"address": "bob@elsewhere.com"})
    await service.get_forwarding("test.example", "alice", "bob@elsewhere.com")
    assert route.called


@pytest.mark.asyncio
async def test_create_forwarding(
    service: ForwardingService, mock_api: respx.Router
) -> None:
    route = mock_api.post("/domains/test.example/mailboxes/alice/forwardings").respond(
        200, json={"address": "bob@elsewhere.com"}
    )
    await service.create_forwarding("test.example", "alice", "bob@elsewhere.com")
    body = json.loads(route.calls[0].request.content)
    assert body == {"address": "bob@elsewhere.com"}


@pytest.mark.asyncio
async def test_create_forwarding_with_expiry(
    service: ForwardingService, mock_api: respx.Router
) -> None:
    route = mock_api.post("/domains/test.example/mailboxes/alice/forwardings").respond(
        200, json={}
    )
    await service.create_forwarding(
        "test.example",
        "alice",
        "bob@elsewhere.com",
        expires_on="2099-01-01",
        remove_upon_expiry=True,
    )
    body = json.loads(route.calls[0].request.content)
    assert body["expires_on"] == "2099-01-01"
    assert body["remove_upon_expiry"] is True


@pytest.mark.asyncio
async def test_update_forwarding(
    service: ForwardingService, mock_api: respx.Router
) -> None:
    route = mock_api.put(
        "/domains/test.example/mailboxes/alice/forwardings/bob%40elsewhere.com"
    ).respond(200, json={})
    await service.update_forwarding(
        "test.example", "alice", "bob@elsewhere.com", is_active=False
    )
    body = json.loads(route.calls[0].request.content)
    assert body == {"is_active": False}


@pytest.mark.asyncio
async def test_delete_forwarding_500_succeeds(
    service: ForwardingService, mock_api: respx.Router
) -> None:
    """Migadu DELETE bug: 500 means success."""
    mock_api.delete(
        "/domains/test.example/mailboxes/alice/forwardings/bob%40elsewhere.com"
    ).respond(500, text="bug")
    await service.delete_forwarding("test.example", "alice", "bob@elsewhere.com")
