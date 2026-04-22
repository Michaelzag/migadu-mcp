"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
import respx

from migadu_mcp.client.migadu_client import MigaduClient


@pytest.fixture(autouse=True)
def _configure_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Provide Migadu credentials to the config singleton for every test.

    Uses dummy values; respx intercepts outbound HTTP so nothing leaves the process.
    """
    monkeypatch.setenv("MIGADU_EMAIL", "admin@test.example")
    monkeypatch.setenv("MIGADU_API_KEY", "test-key")
    monkeypatch.setenv("MIGADU_DOMAIN", "test.example")
    # Force the config singleton to re-read env on each test.
    import migadu_mcp.config as config_module

    monkeypatch.setattr(config_module, "_config", None)


@pytest.fixture
async def client() -> AsyncIterator[MigaduClient]:
    """A MigaduClient bound to a respx-mocked transport."""
    c = MigaduClient("admin@test.example", "test-key")
    try:
        yield c
    finally:
        await c.aclose()


@pytest.fixture
def mock_api() -> AsyncIterator[respx.Router]:
    """respx router that intercepts all calls to the Migadu API base URL."""
    with respx.mock(base_url=MigaduClient.BASE_URL, assert_all_called=False) as router:
        yield router
