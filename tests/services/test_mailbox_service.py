"""Tests for MailboxService."""

from __future__ import annotations

import json

import pytest
import respx

from migadu_mcp.client.migadu_client import MigaduAPIError, MigaduClient
from migadu_mcp.services.mailbox_service import MailboxService


@pytest.fixture
def service(client: MigaduClient) -> MailboxService:
    return MailboxService(client)


@pytest.mark.asyncio
async def test_list_mailboxes(service: MailboxService, mock_api: respx.Router) -> None:
    mock_api.get("/domains/test.example/mailboxes").respond(
        200, json={"mailboxes": [{"address": "a@test.example"}]}
    )
    result = await service.list_mailboxes("test.example")
    assert len(result["mailboxes"]) == 1


@pytest.mark.asyncio
async def test_get_mailbox(service: MailboxService, mock_api: respx.Router) -> None:
    mock_api.get("/domains/test.example/mailboxes/alice").respond(
        200, json={"address": "alice@test.example"}
    )
    result = await service.get_mailbox("test.example", "alice")
    assert result["address"] == "alice@test.example"


@pytest.mark.asyncio
async def test_create_mailbox_with_password(
    service: MailboxService, mock_api: respx.Router
) -> None:
    route = mock_api.post("/domains/test.example/mailboxes").respond(200, json={})
    await service.create_mailbox("test.example", "alice", "Alice", password="fake-placeholder-pw")
    body = json.loads(route.calls[0].request.content)
    assert body == {
        "local_part": "alice",
        "name": "Alice",
        "is_internal": False,
        "password": "fake-placeholder-pw",
    }


@pytest.mark.asyncio
async def test_create_mailbox_with_invitation(
    service: MailboxService, mock_api: respx.Router
) -> None:
    route = mock_api.post("/domains/test.example/mailboxes").respond(200, json={})
    await service.create_mailbox(
        "test.example",
        "alice",
        "Alice",
        password_recovery_email="recovery@elsewhere.com",
    )
    body = json.loads(route.calls[0].request.content)
    assert body["password_method"] == "invitation"
    assert body["password_recovery_email"] == "recovery@elsewhere.com"
    assert "password" not in body


@pytest.mark.asyncio
async def test_update_mailbox_partial(
    service: MailboxService, mock_api: respx.Router
) -> None:
    route = mock_api.put("/domains/test.example/mailboxes/alice").respond(200, json={})
    await service.update_mailbox("test.example", "alice", may_send=False)
    body = json.loads(route.calls[0].request.content)
    assert body == {"may_send": False}


@pytest.mark.asyncio
async def test_delete_mailbox_500_bug_succeeds(
    service: MailboxService, mock_api: respx.Router
) -> None:
    """The original bug: successful deletes return 500. Must not raise."""
    mock_api.delete("/domains/test.example/mailboxes/alice").respond(500, text="bug")
    await service.delete_mailbox("test.example", "alice")


@pytest.mark.asyncio
async def test_delete_mailbox_200_succeeds(
    service: MailboxService, mock_api: respx.Router
) -> None:
    mock_api.delete("/domains/test.example/mailboxes/alice").respond(200, json={})
    await service.delete_mailbox("test.example", "alice")


@pytest.mark.asyncio
async def test_delete_mailbox_404_idempotent(
    service: MailboxService, mock_api: respx.Router
) -> None:
    """Deleting a mailbox that's already gone is a no-op, not an error."""
    mock_api.delete("/domains/test.example/mailboxes/alice").respond(404, text="gone")
    await service.delete_mailbox("test.example", "alice")


@pytest.mark.asyncio
async def test_delete_mailbox_403_raises(
    service: MailboxService, mock_api: respx.Router
) -> None:
    mock_api.delete("/domains/test.example/mailboxes/alice").respond(403, text="nope")
    with pytest.raises(MigaduAPIError) as exc:
        await service.delete_mailbox("test.example", "alice")
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_reset_password(service: MailboxService, mock_api: respx.Router) -> None:
    route = mock_api.put("/domains/test.example/mailboxes/alice").respond(200, json={})
    await service.reset_mailbox_password("test.example", "alice", "fake-reset-pw")
    body = json.loads(route.calls[0].request.content)
    assert body == {"password": "fake-reset-pw"}


@pytest.mark.asyncio
async def test_set_autoresponder(
    service: MailboxService, mock_api: respx.Router
) -> None:
    route = mock_api.put("/domains/test.example/mailboxes/alice").respond(200, json={})
    await service.set_autoresponder(
        "test.example",
        "alice",
        active=True,
        subject="Away",
        body="Back soon",
        expires_on="2099-01-01",
    )
    body = json.loads(route.calls[0].request.content)
    assert body == {
        "autorespond_active": True,
        "autorespond_subject": "Away",
        "autorespond_body": "Back soon",
        "autorespond_expires_on": "2099-01-01",
    }
