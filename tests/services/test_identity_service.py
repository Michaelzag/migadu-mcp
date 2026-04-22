"""Tests for IdentityService."""

from __future__ import annotations

import json

import pytest
import respx

from migadu_mcp.client.migadu_client import MigaduClient
from migadu_mcp.services.identity_service import IdentityService


@pytest.fixture
def service(client: MigaduClient) -> IdentityService:
    return IdentityService(client)


@pytest.mark.asyncio
async def test_list_identities(
    service: IdentityService, mock_api: respx.Router
) -> None:
    mock_api.get("/domains/test.example/mailboxes/alice/identities").respond(
        200, json={"identities": []}
    )
    result = await service.list_identities("test.example", "alice")
    assert result == {"identities": []}


@pytest.mark.asyncio
async def test_get_identity(service: IdentityService, mock_api: respx.Router) -> None:
    mock_api.get("/domains/test.example/mailboxes/alice/identities/support").respond(
        200, json={"address": "support@test.example"}
    )
    result = await service.get_identity("test.example", "alice", "support")
    assert result["address"] == "support@test.example"


@pytest.mark.asyncio
async def test_create_identity(
    service: IdentityService, mock_api: respx.Router
) -> None:
    route = mock_api.post("/domains/test.example/mailboxes/alice/identities").respond(
        200, json={}
    )
    await service.create_identity(
        "test.example", "alice", "support", "Support Team", "pw"
    )
    body = json.loads(route.calls[0].request.content)
    assert body == {"local_part": "support", "name": "Support Team", "password": "pw"}


@pytest.mark.asyncio
async def test_update_identity_partial(
    service: IdentityService, mock_api: respx.Router
) -> None:
    route = mock_api.put(
        "/domains/test.example/mailboxes/alice/identities/support"
    ).respond(200, json={})
    await service.update_identity(
        "test.example", "alice", "support", may_send=False, footer_active=True
    )
    body = json.loads(route.calls[0].request.content)
    assert body == {"may_send": False, "footer_active": True}


@pytest.mark.asyncio
async def test_delete_identity_500_succeeds(
    service: IdentityService, mock_api: respx.Router
) -> None:
    mock_api.delete("/domains/test.example/mailboxes/alice/identities/support").respond(
        500, text="bug"
    )
    await service.delete_identity("test.example", "alice", "support")
