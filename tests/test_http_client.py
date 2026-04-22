"""Tests for MigaduClient — HTTP wiring, DELETE quirk, client reuse."""

from __future__ import annotations

import pytest
import respx

from migadu_mcp.client.migadu_client import MigaduAPIError, MigaduClient


@pytest.mark.asyncio
async def test_get_request_sends_auth_header(
    client: MigaduClient, mock_api: respx.Router
) -> None:
    route = mock_api.get("/domains").respond(200, json={"domains": []})
    await client.get("/domains")
    assert route.called
    sent = route.calls[0].request
    assert sent.headers["Authorization"].startswith("Basic ")


@pytest.mark.asyncio
async def test_4xx_raises(client: MigaduClient, mock_api: respx.Router) -> None:
    mock_api.get("/domains/missing.example").respond(404, text="not found")
    with pytest.raises(MigaduAPIError) as exc:
        await client.get("/domains/missing.example")
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_real_500_on_get_raises(
    client: MigaduClient, mock_api: respx.Router
) -> None:
    mock_api.get("/domains").respond(500, text="internal error")
    with pytest.raises(MigaduAPIError) as exc:
        await client.get("/domains")
    assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_delete_200_returns_none(
    client: MigaduClient, mock_api: respx.Router
) -> None:
    mock_api.delete("/domains/test.example/mailboxes/x").respond(200, json={})
    result = await client.delete("/domains/test.example/mailboxes/x")
    assert result is None


@pytest.mark.asyncio
async def test_delete_500_treated_as_success(
    client: MigaduClient, mock_api: respx.Router
) -> None:
    """The Migadu API returns 500 on successful DELETE — must not raise."""
    mock_api.delete("/domains/test.example/mailboxes/x").respond(500, text="bug")
    result = await client.delete("/domains/test.example/mailboxes/x")
    assert result is None


@pytest.mark.asyncio
async def test_delete_404_idempotent(
    client: MigaduClient, mock_api: respx.Router
) -> None:
    """Deleting a non-existent resource is idempotent — no raise."""
    mock_api.delete("/domains/test.example/mailboxes/x").respond(404, text="no such")
    result = await client.delete("/domains/test.example/mailboxes/x")
    assert result is None


@pytest.mark.asyncio
async def test_delete_other_errors_raise(
    client: MigaduClient, mock_api: respx.Router
) -> None:
    mock_api.delete("/domains/test.example/mailboxes/x").respond(403, text="forbidden")
    with pytest.raises(MigaduAPIError) as exc:
        await client.delete("/domains/test.example/mailboxes/x")
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_httpx_client_is_reused(
    client: MigaduClient, mock_api: respx.Router
) -> None:
    """Multiple requests share the same AsyncClient instance."""
    mock_api.get("/domains").respond(200, json={"domains": []})
    await client.get("/domains")
    first_client = client._get_client()  # type: ignore[attr-defined]
    await client.get("/domains")
    second_client = client._get_client()  # type: ignore[attr-defined]
    assert first_client is second_client


@pytest.mark.asyncio
async def test_aclose_is_idempotent(client: MigaduClient) -> None:
    await client.aclose()
    await client.aclose()  # second call must not raise


@pytest.mark.asyncio
async def test_reopens_after_close(
    client: MigaduClient, mock_api: respx.Router
) -> None:
    mock_api.get("/domains").respond(200, json={"domains": []})
    await client.get("/domains")
    await client.aclose()
    await client.get("/domains")  # lazy recreate on next request


@pytest.mark.asyncio
async def test_patch_verb(client: MigaduClient, mock_api: respx.Router) -> None:
    route = mock_api.patch("/domains/test.example").respond(
        200, json={"name": "test.example"}
    )
    await client.patch("/domains/test.example", json={"description": "x"})
    assert route.called
